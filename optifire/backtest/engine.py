"""
OptiFIRE Backtesting Engine

Simulates trading strategies on historical data to evaluate performance.
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from dataclasses import dataclass
import httpx
import os

from optifire.core.logger import logger


@dataclass
class BacktestConfig:
    """Backtesting configuration."""
    start_date: str  # YYYY-MM-DD
    end_date: str  # YYYY-MM-DD
    initial_capital: float = 10000.0
    commission: float = 0.0  # Per share
    slippage_bps: float = 5.0  # Basis points (0.05%)

    # Risk parameters
    max_position_size: float = 0.10  # 10% of portfolio per position
    max_total_exposure: float = 0.30  # 30% total exposure
    stop_loss_pct: float = 0.03  # 3% stop loss
    take_profit_pct: float = 0.07  # 7% take profit

    # Strategy symbols
    symbols: List[str] = None  # Default watchlist

    def __post_init__(self):
        if self.symbols is None:
            self.symbols = ["SPY", "QQQ", "AAPL", "NVDA", "TSLA", "MSFT", "GOOGL", "META", "AMZN"]


@dataclass
class Trade:
    """Represents a single trade."""
    timestamp: datetime
    symbol: str
    action: str  # BUY, SELL, SHORT, COVER
    price: float
    shares: int
    commission: float
    slippage: float
    pnl: float = 0.0
    reason: str = ""


@dataclass
class Position:
    """Represents an open position."""
    symbol: str
    entry_time: datetime
    entry_price: float
    shares: int
    side: str  # LONG or SHORT
    stop_loss: float
    take_profit: float
    reason: str = ""


class BacktestEngine:
    """
    Event-driven backtesting engine.

    Features:
    - Historical data loading from Alpaca
    - Position tracking with stop loss / take profit
    - Commission and slippage modeling
    - Performance metrics calculation
    """

    def __init__(self, config: BacktestConfig):
        self.config = config
        self.capital = config.initial_capital
        self.initial_capital = config.initial_capital

        # State
        self.positions: Dict[str, Position] = {}
        self.trades: List[Trade] = []
        self.equity_curve: List[Tuple[datetime, float]] = []
        self.cash_history: List[Tuple[datetime, float]] = []

        # Historical data cache
        self.price_data: Dict[str, pd.DataFrame] = {}

        # Alpaca credentials
        self.api_key = os.getenv("ALPACA_API_KEY")
        self.api_secret = os.getenv("ALPACA_API_SECRET")
        self.headers = {
            "APCA-API-KEY-ID": self.api_key or "",
            "APCA-API-SECRET-KEY": self.api_secret or "",
        }

    async def load_historical_data(self, symbol: str) -> pd.DataFrame:
        """
        Load historical OHLCV data from Alpaca.

        Returns:
            DataFrame with columns: timestamp, open, high, low, close, volume
        """
        if symbol in self.price_data:
            return self.price_data[symbol]

        logger.info(f"Loading historical data for {symbol}...")

        # Alpaca data API
        url = f"https://data.alpaca.markets/v2/stocks/{symbol}/bars"
        params = {
            "start": self.config.start_date,
            "end": self.config.end_date,
            "timeframe": "1Day",  # Daily bars
            "adjustment": "all",  # Adjust for splits/dividends
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()

            if "bars" not in data or not data["bars"]:
                logger.warning(f"No data for {symbol}")
                return pd.DataFrame()

            # Convert to DataFrame
            bars = data["bars"]
            df = pd.DataFrame(bars)
            df["timestamp"] = pd.to_datetime(df["t"])
            df = df.rename(columns={"o": "open", "h": "high", "l": "low", "c": "close", "v": "volume"})
            df = df[["timestamp", "open", "high", "low", "close", "volume"]]
            df = df.sort_values("timestamp")

            self.price_data[symbol] = df
            logger.info(f"Loaded {len(df)} bars for {symbol}")
            return df

        except Exception as e:
            logger.error(f"Failed to load data for {symbol}: {e}")
            return pd.DataFrame()

    def calculate_slippage(self, price: float, action: str) -> float:
        """Calculate slippage based on action."""
        slippage_amt = price * (self.config.slippage_bps / 10000.0)
        if action in ["BUY", "COVER"]:
            return slippage_amt  # Pay more when buying
        else:
            return -slippage_amt  # Get less when selling

    def calculate_commission(self, shares: int) -> float:
        """Calculate commission."""
        return shares * self.config.commission

    def can_open_position(self, symbol: str, price: float, shares: int) -> bool:
        """Check if we can open a new position."""
        cost = price * shares

        # Check cash
        if cost > self.capital:
            return False

        # Check position size limit
        # Create price dict for valuation
        current_prices = {s: price for s in self.positions.keys()}
        current_prices[symbol] = price
        total_value = self.get_total_value(current_prices)
        if cost > total_value * self.config.max_position_size:
            return False

        # Check total exposure
        current_exposure = sum(
            pos.shares * price  # Approximate with current price
            for pos in self.positions.values()
        )
        if (current_exposure + cost) > total_value * self.config.max_total_exposure:
            return False

        return True

    def open_position(self, timestamp: datetime, symbol: str, price: float,
                     shares: int, side: str, reason: str = "") -> Optional[Trade]:
        """Open a new position."""
        if not self.can_open_position(symbol, price, shares):
            logger.debug(f"Cannot open position for {symbol} - risk limits exceeded")
            return None

        # Calculate costs
        slippage = self.calculate_slippage(price, "BUY" if side == "LONG" else "SHORT")
        commission = self.calculate_commission(shares)
        total_cost = (price + slippage) * shares + commission

        # Deduct from capital
        self.capital -= total_cost

        # Create position
        stop_loss = price * (1 - self.config.stop_loss_pct) if side == "LONG" else price * (1 + self.config.stop_loss_pct)
        take_profit = price * (1 + self.config.take_profit_pct) if side == "LONG" else price * (1 - self.config.take_profit_pct)

        position = Position(
            symbol=symbol,
            entry_time=timestamp,
            entry_price=price,
            shares=shares,
            side=side,
            stop_loss=stop_loss,
            take_profit=take_profit,
            reason=reason,
        )

        self.positions[symbol] = position

        # Record trade
        trade = Trade(
            timestamp=timestamp,
            symbol=symbol,
            action="BUY" if side == "LONG" else "SHORT",
            price=price,
            shares=shares,
            commission=commission,
            slippage=slippage * shares,
            reason=reason,
        )
        self.trades.append(trade)

        logger.debug(f"Opened {side} position: {symbol} x{shares} @ ${price:.2f}")
        return trade

    def close_position(self, timestamp: datetime, symbol: str, price: float, reason: str = "") -> Optional[Trade]:
        """Close an existing position."""
        if symbol not in self.positions:
            return None

        position = self.positions[symbol]

        # Calculate P&L
        if position.side == "LONG":
            pnl = (price - position.entry_price) * position.shares
        else:  # SHORT
            pnl = (position.entry_price - price) * position.shares

        # Calculate costs
        action = "SELL" if position.side == "LONG" else "COVER"
        slippage = self.calculate_slippage(price, action)
        commission = self.calculate_commission(position.shares)

        # Add proceeds to capital
        proceeds = (price + slippage) * position.shares - commission
        self.capital += proceeds

        # Record trade
        trade = Trade(
            timestamp=timestamp,
            symbol=symbol,
            action=action,
            price=price,
            shares=position.shares,
            commission=commission,
            slippage=slippage * position.shares,
            pnl=pnl - commission - abs(slippage * position.shares),
            reason=reason,
        )
        self.trades.append(trade)

        # Remove position
        del self.positions[symbol]

        logger.debug(f"Closed position: {symbol} @ ${price:.2f}, P&L: ${trade.pnl:.2f}, Reason: {reason}")
        return trade

    def check_stop_loss_take_profit(self, timestamp: datetime, symbol: str,
                                    low: float, high: float) -> Optional[Trade]:
        """Check if stop loss or take profit was hit."""
        if symbol not in self.positions:
            return None

        position = self.positions[symbol]

        if position.side == "LONG":
            # Check stop loss
            if low <= position.stop_loss:
                return self.close_position(timestamp, symbol, position.stop_loss, "Stop Loss")
            # Check take profit
            if high >= position.take_profit:
                return self.close_position(timestamp, symbol, position.take_profit, "Take Profit")
        else:  # SHORT
            # Check stop loss (price goes up)
            if high >= position.stop_loss:
                return self.close_position(timestamp, symbol, position.stop_loss, "Stop Loss")
            # Check take profit (price goes down)
            if low <= position.take_profit:
                return self.close_position(timestamp, symbol, position.take_profit, "Take Profit")

        return None

    def get_total_value(self, current_prices: Dict[str, float] = None) -> float:
        """Get total portfolio value."""
        if current_prices is None:
            current_prices = {}

        position_value = sum(
            pos.shares * current_prices.get(symbol, pos.entry_price)
            for symbol, pos in self.positions.items()
        )

        return self.capital + position_value

    def record_equity(self, timestamp: datetime, current_prices: Dict[str, float]):
        """Record equity curve point."""
        total_value = self.get_total_value(current_prices)
        self.equity_curve.append((timestamp, total_value))
        self.cash_history.append((timestamp, self.capital))

    async def run(self, signal_generator) -> Dict:
        """
        Run backtest with a signal generator.

        Args:
            signal_generator: Async function that takes (timestamp, price_data) and returns signals
                            Signal format: {"symbol": str, "action": "BUY"|"SELL", "confidence": float, "reason": str}

        Returns:
            Dictionary with backtest results and metrics
        """
        logger.info(f"Starting backtest from {self.config.start_date} to {self.config.end_date}")
        logger.info(f"Initial capital: ${self.config.initial_capital:,.2f}")

        # Load data for all symbols
        logger.info(f"Loading data for {len(self.config.symbols)} symbols...")
        for symbol in self.config.symbols:
            await self.load_historical_data(symbol)

        # Get date range
        start = pd.to_datetime(self.config.start_date)
        end = pd.to_datetime(self.config.end_date)

        # Simulate day by day
        current_date = start
        days_processed = 0

        while current_date <= end:
            # Get prices for all symbols on this day
            day_prices = {}
            day_data = {}

            for symbol in self.config.symbols:
                if symbol not in self.price_data or self.price_data[symbol].empty:
                    continue

                df = self.price_data[symbol]
                day_df = df[df["timestamp"].dt.date == current_date.date()]

                if not day_df.empty:
                    row = day_df.iloc[0]
                    day_prices[symbol] = row["close"]
                    day_data[symbol] = row.to_dict()

            if day_prices:
                # Check stop loss / take profit for existing positions
                for symbol in list(self.positions.keys()):
                    if symbol in day_data:
                        self.check_stop_loss_take_profit(
                            current_date,
                            symbol,
                            day_data[symbol]["low"],
                            day_data[symbol]["high"],
                        )

                # Generate signals
                signals = await signal_generator(current_date, day_data)

                # Execute signals
                for signal in signals:
                    symbol = signal.get("symbol")
                    action = signal.get("action")
                    confidence = signal.get("confidence", 0.5)
                    reason = signal.get("reason", "Signal")

                    if symbol not in day_prices:
                        continue

                    price = day_prices[symbol]

                    # Size position based on confidence
                    target_value = self.get_total_value(day_prices) * self.config.max_position_size
                    shares = int(target_value * confidence / price)

                    if action == "BUY" and shares > 0:
                        if symbol not in self.positions:
                            self.open_position(current_date, symbol, price, shares, "LONG", reason)
                    elif action == "SELL" and symbol in self.positions:
                        self.close_position(current_date, symbol, price, reason)

                # Record equity
                self.record_equity(current_date, day_prices)
                days_processed += 1

            current_date += timedelta(days=1)

        # Close all remaining positions
        logger.info("Closing remaining positions...")
        final_prices = {symbol: df.iloc[-1]["close"]
                       for symbol, df in self.price_data.items()
                       if not df.empty}

        for symbol in list(self.positions.keys()):
            if symbol in final_prices:
                self.close_position(end, symbol, final_prices[symbol], "Backtest End")

        logger.info(f"Backtest complete. Processed {days_processed} days, {len(self.trades)} trades")

        # Calculate metrics
        return self.calculate_metrics()

    def calculate_metrics(self) -> Dict:
        """Calculate performance metrics."""
        if not self.equity_curve:
            return {"error": "No equity data"}

        # Convert equity curve to DataFrame
        df = pd.DataFrame(self.equity_curve, columns=["timestamp", "equity"])
        df["returns"] = df["equity"].pct_change()

        # Basic metrics
        final_equity = df["equity"].iloc[-1]
        total_return = (final_equity - self.initial_capital) / self.initial_capital

        # Trade statistics
        winning_trades = [t for t in self.trades if t.pnl > 0]
        losing_trades = [t for t in self.trades if t.pnl < 0]
        win_rate = len(winning_trades) / len(self.trades) if self.trades else 0

        avg_win = np.mean([t.pnl for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t.pnl for t in losing_trades]) if losing_trades else 0

        # Drawdown
        df["cummax"] = df["equity"].cummax()
        df["drawdown"] = (df["equity"] - df["cummax"]) / df["cummax"]
        max_drawdown = df["drawdown"].min()

        # Sharpe ratio (annualized, assuming daily returns)
        if len(df) > 1 and df["returns"].std() > 0:
            sharpe = (df["returns"].mean() / df["returns"].std()) * np.sqrt(252)
        else:
            sharpe = 0

        # Sortino ratio (downside deviation)
        downside_returns = df["returns"][df["returns"] < 0]
        if len(downside_returns) > 0 and downside_returns.std() > 0:
            sortino = (df["returns"].mean() / downside_returns.std()) * np.sqrt(252)
        else:
            sortino = 0

        metrics = {
            "initial_capital": self.initial_capital,
            "final_equity": final_equity,
            "total_return": total_return,
            "total_return_pct": total_return * 100,
            "total_pnl": final_equity - self.initial_capital,

            "total_trades": len(self.trades),
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "win_rate": win_rate,
            "win_rate_pct": win_rate * 100,

            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "avg_trade": np.mean([t.pnl for t in self.trades]) if self.trades else 0,
            "profit_factor": abs(sum(t.pnl for t in winning_trades) / sum(t.pnl for t in losing_trades)) if losing_trades else 0,

            "max_drawdown": max_drawdown,
            "max_drawdown_pct": max_drawdown * 100,

            "sharpe_ratio": sharpe,
            "sortino_ratio": sortino,

            "equity_curve": df[["timestamp", "equity"]].to_dict("records"),
            "trades": [
                {
                    "timestamp": t.timestamp.isoformat(),
                    "symbol": t.symbol,
                    "action": t.action,
                    "price": t.price,
                    "shares": t.shares,
                    "pnl": t.pnl,
                    "reason": t.reason,
                }
                for t in self.trades
            ],
        }

        return metrics

"""
Example trading strategies for backtesting.
"""
from datetime import datetime
from typing import Dict, List
import pandas as pd
import numpy as np


class SimpleStrategy:
    """
    Simple momentum + mean reversion strategy.

    Rules:
    - BUY when price crosses above 20-day MA and RSI < 70
    - SELL when price crosses below 20-day MA or RSI > 80
    """

    def __init__(self):
        self.price_history: Dict[str, List[float]] = {}
        self.ma_period = 20
        self.rsi_period = 14

    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Calculate RSI indicator."""
        if len(prices) < period + 1:
            return 50.0

        deltas = np.diff(prices[-period-1:])
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)

        avg_gain = np.mean(gains)
        avg_loss = np.mean(losses)

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    async def generate_signals(self, timestamp: datetime, price_data: Dict[str, Dict]) -> List[Dict]:
        """
        Generate trading signals.

        Args:
            timestamp: Current timestamp
            price_data: Dict of {symbol: {open, high, low, close, volume}}

        Returns:
            List of signal dicts
        """
        signals = []

        for symbol, data in price_data.items():
            close = data["close"]

            # Update price history
            if symbol not in self.price_history:
                self.price_history[symbol] = []
            self.price_history[symbol].append(close)

            # Need enough history
            if len(self.price_history[symbol]) < self.ma_period:
                continue

            prices = self.price_history[symbol]

            # Calculate indicators
            ma20 = np.mean(prices[-self.ma_period:])
            rsi = self.calculate_rsi(prices, self.rsi_period)

            # Previous price for crossover detection
            prev_price = prices[-2] if len(prices) > 1 else close
            prev_ma = np.mean(prices[-self.ma_period-1:-1]) if len(prices) > self.ma_period else ma20

            # BUY signal: price crosses above MA and RSI not overbought
            if prev_price < prev_ma and close > ma20 and rsi < 70:
                signals.append({
                    "symbol": symbol,
                    "action": "BUY",
                    "confidence": min(0.8, (70 - rsi) / 70),  # Higher confidence when RSI lower
                    "reason": f"MA Crossover (RSI: {rsi:.1f})",
                })

            # SELL signal: price crosses below MA or RSI overbought
            elif (prev_price > prev_ma and close < ma20) or rsi > 80:
                signals.append({
                    "symbol": symbol,
                    "action": "SELL",
                    "confidence": 0.9,
                    "reason": f"MA Crossunder / Overbought (RSI: {rsi:.1f})",
                })

        return signals


class TrendFollowingStrategy:
    """
    Trend following strategy using dual moving averages.

    Rules:
    - BUY when fast MA crosses above slow MA
    - SELL when fast MA crosses below slow MA
    """

    def __init__(self, fast_period: int = 10, slow_period: int = 50):
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.price_history: Dict[str, List[float]] = {}

    async def generate_signals(self, timestamp: datetime, price_data: Dict[str, Dict]) -> List[Dict]:
        """Generate trend following signals."""
        signals = []

        for symbol, data in price_data.items():
            close = data["close"]

            # Update history
            if symbol not in self.price_history:
                self.price_history[symbol] = []
            self.price_history[symbol].append(close)

            prices = self.price_history[symbol]

            # Need enough history
            if len(prices) < self.slow_period:
                continue

            # Calculate MAs
            fast_ma = np.mean(prices[-self.fast_period:])
            slow_ma = np.mean(prices[-self.slow_period:])

            # Previous MAs
            prev_fast = np.mean(prices[-self.fast_period-1:-1])
            prev_slow = np.mean(prices[-self.slow_period-1:-1])

            # Golden cross: fast crosses above slow
            if prev_fast < prev_slow and fast_ma > slow_ma:
                signals.append({
                    "symbol": symbol,
                    "action": "BUY",
                    "confidence": 0.7,
                    "reason": f"Golden Cross ({self.fast_period}/{self.slow_period} MA)",
                })

            # Death cross: fast crosses below slow
            elif prev_fast > prev_slow and fast_ma < slow_ma:
                signals.append({
                    "symbol": symbol,
                    "action": "SELL",
                    "confidence": 0.9,
                    "reason": f"Death Cross ({self.fast_period}/{self.slow_period} MA)",
                })

        return signals


class MomentumStrategy:
    """
    Momentum strategy - buy winners, sell losers.

    Rules:
    - BUY when 5-day return > 2% and 20-day return > 5%
    - SELL when 5-day return < -2%
    """

    def __init__(self):
        self.price_history: Dict[str, List[float]] = {}

    async def generate_signals(self, timestamp: datetime, price_data: Dict[str, Dict]) -> List[Dict]:
        """Generate momentum signals."""
        signals = []

        for symbol, data in price_data.items():
            close = data["close"]

            # Update history
            if symbol not in self.price_history:
                self.price_history[symbol] = []
            self.price_history[symbol].append(close)

            prices = self.price_history[symbol]

            # Need 20 days of history
            if len(prices) < 20:
                continue

            # Calculate returns
            ret_5d = (prices[-1] - prices[-5]) / prices[-5]
            ret_20d = (prices[-1] - prices[-20]) / prices[-20]

            # BUY: strong momentum
            if ret_5d > 0.02 and ret_20d > 0.05:
                confidence = min(0.9, ret_20d * 5)  # Higher confidence for stronger momentum
                signals.append({
                    "symbol": symbol,
                    "action": "BUY",
                    "confidence": confidence,
                    "reason": f"Strong Momentum ({ret_20d*100:.1f}% 20d)",
                })

            # SELL: momentum reversal
            elif ret_5d < -0.02:
                signals.append({
                    "symbol": symbol,
                    "action": "SELL",
                    "confidence": 0.8,
                    "reason": f"Momentum Reversal ({ret_5d*100:.1f}% 5d)",
                })

        return signals


class MeanReversionStrategy:
    """
    Mean reversion strategy using Bollinger Bands.

    Rules:
    - BUY when price touches lower Bollinger Band
    - SELL when price touches upper Bollinger Band
    """

    def __init__(self, period: int = 20, std_dev: float = 2.0):
        self.period = period
        self.std_dev = std_dev
        self.price_history: Dict[str, List[float]] = {}

    async def generate_signals(self, timestamp: datetime, price_data: Dict[str, Dict]) -> List[Dict]:
        """Generate mean reversion signals."""
        signals = []

        for symbol, data in price_data.items():
            close = data["close"]

            # Update history
            if symbol not in self.price_history:
                self.price_history[symbol] = []
            self.price_history[symbol].append(close)

            prices = self.price_history[symbol]

            if len(prices) < self.period:
                continue

            # Calculate Bollinger Bands
            ma = np.mean(prices[-self.period:])
            std = np.std(prices[-self.period:])
            upper_band = ma + (self.std_dev * std)
            lower_band = ma - (self.std_dev * std)

            # BUY: price at lower band (oversold)
            if close <= lower_band:
                # Distance from lower band as confidence
                distance = (lower_band - close) / lower_band
                confidence = min(0.9, 0.5 + distance * 10)

                signals.append({
                    "symbol": symbol,
                    "action": "BUY",
                    "confidence": confidence,
                    "reason": f"Oversold (BB Lower)",
                })

            # SELL: price at upper band (overbought)
            elif close >= upper_band:
                signals.append({
                    "symbol": symbol,
                    "action": "SELL",
                    "confidence": 0.8,
                    "reason": f"Overbought (BB Upper)",
                })

        return signals


class BuyAndHoldStrategy:
    """
    Simple buy and hold strategy for benchmarking.

    Rules:
    - BUY on first day
    - HOLD forever
    """

    def __init__(self):
        self.positions_opened = set()

    async def generate_signals(self, timestamp: datetime, price_data: Dict[str, Dict]) -> List[Dict]:
        """Generate buy and hold signals."""
        signals = []

        for symbol in price_data.keys():
            # Only buy once
            if symbol not in self.positions_opened:
                signals.append({
                    "symbol": symbol,
                    "action": "BUY",
                    "confidence": 1.0,
                    "reason": "Buy and Hold",
                })
                self.positions_opened.add(symbol)

        return signals

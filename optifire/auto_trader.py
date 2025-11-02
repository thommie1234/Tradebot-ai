"""
OptiFIRE Auto-Trading Engine
Automatically executes trades based on signals from plugins.
"""
import asyncio
from datetime import datetime, time
from typing import Dict, List, Optional
import pytz

from optifire.core.logger import logger
from optifire.core.bus import EventBus
from optifire.exec.executor import OrderExecutor
from optifire.exec.broker_alpaca import AlpacaBroker
from optifire.ai.openai_client import OpenAIClient
from optifire.services.earnings_calendar import EarningsCalendar
from optifire.services.news_scanner import NewsScanner

# Import plugins for signal generation
from optifire.plugins.alpha_vix_regime.impl import AlphaVixRegime
from optifire.plugins.alpha_cross_asset_corr.impl import AlphaCrossAssetCorr
from optifire.plugins.alpha_vrp.impl import AlphaVrp
from optifire.plugins.risk_var_budget.impl import RiskVarBudget
from optifire.plugins.risk_drawdown_derisk.impl import RiskDrawdownDerisk
from optifire.plugins.risk_vol_target.impl import RiskVolTarget
from optifire.plugins.fe_garch.impl import FeGarch
from optifire.plugins.fe_entropy.impl import FeEntropy


class Signal:
    """Trading signal."""
    def __init__(
        self,
        symbol: str,
        action: str,  # "BUY" or "SELL"
        confidence: float,  # 0.0 - 1.0
        reason: str,
        size_pct: float = 0.05,  # % of portfolio
        take_profit: Optional[float] = None,  # % gain to take profit
        stop_loss: Optional[float] = None,  # % loss to stop
    ):
        self.symbol = symbol
        self.action = action
        self.confidence = confidence
        self.reason = reason
        self.size_pct = size_pct
        self.take_profit = take_profit
        self.stop_loss = stop_loss
        self.timestamp = datetime.now(pytz.UTC)


class AutoTrader:
    """
    Automated trading engine.

    Features:
    - Pre-earnings trades
    - News-based trades
    - Automatic position management
    - Take profit / stop loss
    """

    def __init__(self, broker=None, db=None):
        self.broker = broker or AlpacaBroker(paper=True)
        self.executor = OrderExecutor(self.broker, db) if db else None
        self.openai = OpenAIClient()
        self.bus = EventBus()
        self.earnings_calendar = EarningsCalendar()
        self.news_scanner = NewsScanner()

        # Initialize plugins
        self.vix_regime_plugin = AlphaVixRegime()
        self.cross_asset_plugin = AlphaCrossAssetCorr()
        self.vrp_plugin = AlphaVrp()
        self.var_budget_plugin = RiskVarBudget()
        self.drawdown_plugin = RiskDrawdownDerisk()
        self.vol_target_plugin = RiskVolTarget()
        self.garch_plugin = FeGarch()
        self.entropy_plugin = FeEntropy()

        self.active = True
        self.signals: List[Signal] = []
        self.positions: Dict[str, Dict] = {}

        # Plugin state cache
        self.vix_regime = "NORMAL"
        self.exposure_multiplier = 1.0  # From VIX regime
        self.drawdown_multiplier = 1.0  # From drawdown de-risking
        self.vol_target_multiplier = 1.0  # From vol targeting

        # Config
        self.max_positions = 5
        self.default_take_profit = 0.07  # 7% gain
        self.default_stop_loss = 0.03    # 3% loss
        self.max_position_size = 0.10    # 10% of portfolio per position

    async def start(self):
        """Start the auto-trading engine."""
        logger.info("🤖 AutoTrader starting...")

        # Schedule tasks
        tasks = [
            self.plugin_monitor_loop(),      # NEW: Monitor plugin states
            self.earnings_scanner_loop(),
            self.news_scanner_loop(),
            self.position_manager_loop(),
            self.signal_executor_loop(),
        ]

        await asyncio.gather(*tasks)

    async def plugin_monitor_loop(self):
        """Monitor plugin states and update risk multipliers."""
        logger.info("🔌 Plugin monitor started")

        while self.active:
            try:
                # Update VIX regime (affects all position sizing)
                await self.update_vix_regime()

                # Update drawdown de-risking
                await self.update_drawdown_multiplier()

                # Update vol targeting
                await self.update_vol_target_multiplier()

                # Run every 5 minutes
                await asyncio.sleep(300)

            except Exception as e:
                logger.error(f"Plugin monitor error: {e}", exc_info=True)
                await asyncio.sleep(60)

    async def update_vix_regime(self):
        """Update VIX regime and exposure multiplier."""
        try:
            # Get VIX data (simplified - should use real API)
            # For now, use mock data
            vix_level = 20.0  # TODO: Fetch real VIX from market data API

            # Detect regime
            if vix_level < 15:
                self.vix_regime = "LOW"
                self.exposure_multiplier = 1.2  # Increase exposure in calm markets
            elif vix_level < 25:
                self.vix_regime = "NORMAL"
                self.exposure_multiplier = 1.0
            elif vix_level < 35:
                self.vix_regime = "ELEVATED"
                self.exposure_multiplier = 0.7  # Reduce exposure
            else:
                self.vix_regime = "CRISIS"
                self.exposure_multiplier = 0.3  # Drastically reduce

            logger.debug(f"VIX regime: {self.vix_regime}, exposure mult: {self.exposure_multiplier:.2f}")

        except Exception as e:
            logger.error(f"Error updating VIX regime: {e}")

    async def update_drawdown_multiplier(self):
        """Update drawdown multiplier based on current portfolio DD."""
        try:
            # Get portfolio metrics
            account = await self.broker.get_account()
            equity = float(account.get("equity", 1000))

            # Calculate high-water mark and drawdown
            # (simplified - should track actual HWM over time)
            high_water_mark = 1000.0  # TODO: Track actual HWM
            drawdown = (high_water_mark - equity) / high_water_mark

            # Apply de-risking based on drawdown
            if drawdown >= 0.08:
                self.drawdown_multiplier = 0.0  # STOP trading at 8% DD
                logger.warning(f"⛔ Trading STOPPED - drawdown {drawdown:.1%} >= 8%")
            elif drawdown >= 0.05:
                self.drawdown_multiplier = 0.5  # Half size at 5% DD
                logger.warning(f"⚠️  Drawdown de-risking: {drawdown:.1%} - reducing size to 50%")
            else:
                self.drawdown_multiplier = 1.0

        except Exception as e:
            logger.error(f"Error updating drawdown multiplier: {e}")

    async def update_vol_target_multiplier(self):
        """Update volatility targeting multiplier."""
        try:
            # Calculate portfolio volatility (simplified)
            # Should use GARCH plugin for better estimate
            target_vol = 0.15  # 15% annualized
            current_vol = 0.12  # TODO: Calculate from returns

            # Adjust leverage to target volatility
            self.vol_target_multiplier = target_vol / max(current_vol, 0.01)
            self.vol_target_multiplier = min(self.vol_target_multiplier, 1.5)  # Cap at 1.5x

            logger.debug(f"Vol targeting mult: {self.vol_target_multiplier:.2f}")

        except Exception as e:
            logger.error(f"Error updating vol target multiplier: {e}")

    async def earnings_scanner_loop(self):
        """Scan earnings calendar and generate pre-earnings trades."""
        logger.info("📅 Earnings scanner started")

        while self.active:
            try:
                if self.is_market_hours():
                    # Check earnings calendar
                    upcoming = await self.get_upcoming_earnings()

                    for symbol, days_until in upcoming.items():
                        if 1 <= days_until <= 2:  # 1-2 days before earnings
                            # Generate pre-earnings signal
                            signal = await self.analyze_pre_earnings(symbol)
                            if signal:
                                self.signals.append(signal)
                                logger.info(f"📊 Pre-earnings signal: {symbol} in {days_until} days")

                # Run every 4 hours
                await asyncio.sleep(4 * 3600)

            except Exception as e:
                logger.error(f"Earnings scanner error: {e}", exc_info=True)
                await asyncio.sleep(300)

    async def news_scanner_loop(self):
        """Scan news every hour for trading opportunities."""
        logger.info("📰 News scanner started")

        while self.active:
            try:
                if self.is_market_hours():
                    # Scan news for watchlist
                    watchlist = ["NVDA", "TSLA", "AAPL", "MSFT", "GOOGL", "META", "AMZN"]

                    for symbol in watchlist:
                        signal = await self.scan_news_for_symbol(symbol)
                        if signal:
                            self.signals.append(signal)
                            logger.info(f"📰 News signal: {symbol} - {signal.reason}")

                    # Also check cross-asset correlation signals
                    cross_asset_signal = await self.check_cross_asset_signals()
                    if cross_asset_signal:
                        self.signals.append(cross_asset_signal)
                        logger.info(f"📊 Cross-asset signal: {cross_asset_signal.symbol} - {cross_asset_signal.reason}")

                # Run every hour
                await asyncio.sleep(3600)

            except Exception as e:
                logger.error(f"News scanner error: {e}", exc_info=True)
                await asyncio.sleep(300)

    async def check_cross_asset_signals(self) -> Optional[Signal]:
        """Check for cross-asset correlation breakdown signals."""
        try:
            # Example: SPY-TLT correlation breakdown
            # Simplified - should use real price data and correlation calc

            # If SPY-TLT correlation breaks down (goes from -0.7 to 0.0)
            # This often signals market stress → trade safe havens

            # Mock data for now
            spy_tlt_corr = -0.3  # TODO: Calculate real correlation

            # Normal correlation is around -0.7 (inverse relationship)
            # If it breaks above -0.4, it's unusual → potential signal

            if spy_tlt_corr > -0.4:
                # Correlation breakdown → potential flight to safety
                return Signal(
                    symbol="TLT",  # Treasury bonds
                    action="BUY",
                    confidence=0.65,
                    reason=f"📊 SPY-TLT correlation breakdown ({spy_tlt_corr:.2f}), flight to safety expected",
                    size_pct=0.06,
                    take_profit=0.04,  # Bonds move slower
                    stop_loss=0.02,
                )

            return None

        except Exception as e:
            logger.error(f"Error checking cross-asset signals: {e}")
            return None

    async def position_manager_loop(self):
        """Manage open positions - take profit and stop loss."""
        logger.info("💼 Position manager started")

        while self.active:
            try:
                if self.is_market_hours():
                    # Get current positions
                    positions = await self.broker.get_positions()

                    for pos in positions:
                        symbol = pos.get("symbol")
                        current_price = float(pos.get("current_price", 0))
                        avg_entry = float(pos.get("avg_entry_price", 0))
                        qty = float(pos.get("qty", 0))

                        if avg_entry == 0:
                            continue

                        # Calculate P&L %
                        pnl_pct = (current_price - avg_entry) / avg_entry

                        # Check take profit
                        if pnl_pct >= self.default_take_profit:
                            logger.info(f"💰 Take profit triggered: {symbol} at +{pnl_pct*100:.1f}%")
                            await self.close_position(symbol, qty, "TAKE_PROFIT")

                        # Check stop loss
                        elif pnl_pct <= -self.default_stop_loss:
                            logger.warning(f"🛑 Stop loss triggered: {symbol} at {pnl_pct*100:.1f}%")
                            await self.close_position(symbol, qty, "STOP_LOSS")

                # Check every 30 seconds
                await asyncio.sleep(30)

            except Exception as e:
                logger.error(f"Position manager error: {e}", exc_info=True)
                await asyncio.sleep(60)

    async def signal_executor_loop(self):
        """Execute signals from the queue."""
        logger.info("⚡ Signal executor started")

        while self.active:
            try:
                if self.signals and self.is_market_hours():
                    # Get highest confidence signal
                    signal = max(self.signals, key=lambda s: s.confidence)
                    self.signals.remove(signal)

                    # Check if we have room for new position
                    positions = await self.broker.get_positions()
                    if len(positions) >= self.max_positions:
                        logger.info(f"⚠️  Max positions reached ({self.max_positions}), skipping signal")
                        continue

                    # Execute signal
                    await self.execute_signal(signal)

                await asyncio.sleep(10)

            except Exception as e:
                logger.error(f"Signal executor error: {e}", exc_info=True)
                await asyncio.sleep(30)

    async def execute_signal(self, signal: Signal):
        """Execute a trading signal with plugin-based risk adjustments."""
        try:
            if not self.executor:
                logger.warning("Executor not initialized - cannot execute signal")
                return

            # Check if drawdown has stopped trading
            if self.drawdown_multiplier == 0.0:
                logger.warning(f"⛔ Signal BLOCKED - drawdown de-risking active")
                return

            # Get account info
            account = await self.broker.get_account()
            buying_power = float(account.get("buying_power", 0))

            # Calculate position size with ALL plugin multipliers
            base_size_pct = signal.size_pct

            # Apply VIX regime multiplier
            adjusted_size = base_size_pct * self.exposure_multiplier

            # Apply drawdown multiplier
            adjusted_size *= self.drawdown_multiplier

            # Apply vol targeting multiplier
            adjusted_size *= self.vol_target_multiplier

            # Calculate position value
            position_value = buying_power * adjusted_size

            # Get current price
            quote = await self.broker.get_quote(signal.symbol)
            current_price = float(quote.get("ap", 0))  # Ask price

            if current_price == 0:
                logger.warning(f"Could not get price for {signal.symbol}")
                return

            # Calculate qty
            qty = int(position_value / current_price)

            if qty == 0:
                logger.warning(f"Position too small for {signal.symbol}: ${position_value:.2f}")
                return

            # Place order
            logger.info(f"🚀 Executing signal: {signal.action} {qty} {signal.symbol} @ ${current_price:.2f}")
            logger.info(f"   Reason: {signal.reason}")
            logger.info(f"   Confidence: {signal.confidence:.0%}")
            logger.info(f"   📊 Plugin adjustments:")
            logger.info(f"      Base size: {base_size_pct:.1%}")
            logger.info(f"      VIX regime ({self.vix_regime}): {self.exposure_multiplier:.2f}x")
            logger.info(f"      Drawdown: {self.drawdown_multiplier:.2f}x")
            logger.info(f"      Vol target: {self.vol_target_multiplier:.2f}x")
            logger.info(f"      Final size: {adjusted_size:.1%} (${position_value:.2f})")

            from optifire.exec.executor import OrderRequest

            order = OrderRequest(
                symbol=signal.symbol,
                qty=qty,
                side=signal.action.lower(),
                type="market",
                time_in_force="day",
            )

            order_id = await self.executor.submit_order(order)

            # Store position info for TP/SL
            self.positions[signal.symbol] = {
                "entry_price": current_price,
                "qty": qty,
                "take_profit_pct": signal.take_profit or self.default_take_profit,
                "stop_loss_pct": signal.stop_loss or self.default_stop_loss,
            }

            logger.info(f"✅ Order placed: {order_id}")

        except Exception as e:
            logger.error(f"Error executing signal: {e}", exc_info=True)

    async def close_position(self, symbol: str, qty: float, reason: str):
        """Close a position."""
        try:
            if not self.executor:
                logger.warning("Executor not initialized - cannot close position")
                return

            from optifire.exec.executor import OrderRequest

            order = OrderRequest(
                symbol=symbol,
                qty=int(qty),
                side="sell",
                type="market",
                time_in_force="day",
            )

            order_id = await self.executor.submit_order(order)
            logger.info(f"✅ Position closed: {symbol} - {reason} - Order: {order_id}")

            # Remove from tracking
            if symbol in self.positions:
                del self.positions[symbol]

        except Exception as e:
            logger.error(f"Error closing position {symbol}: {e}", exc_info=True)

    async def get_upcoming_earnings(self) -> Dict[str, int]:
        """Get upcoming earnings (days until earnings)."""
        return await self.earnings_calendar.get_upcoming_earnings(days_ahead=7)

    async def analyze_pre_earnings(self, symbol: str) -> Optional[Signal]:
        """Analyze if we should trade before earnings."""
        try:
            # Get recent news sentiment
            prompt = f"""Analyze {symbol} for pre-earnings trade opportunity.

Should we BUY, SELL, or SKIP this pre-earnings play?
Consider:
- Recent news sentiment
- Historical earnings reaction
- Current momentum

Respond in JSON format:
{{
    "action": "BUY|SELL|SKIP",
    "confidence": 0.0-1.0,
    "reason": "Brief explanation"
}}
"""

            result = await self.openai.analyze_text(prompt)

            # Parse result (simplified - should use proper JSON parsing)
            if "SKIP" in result:
                return None

            action = "BUY" if "BUY" in result else "SELL"

            return Signal(
                symbol=symbol,
                action=action,
                confidence=0.6,  # Conservative for earnings
                reason=f"Pre-earnings play: {result[:100]}",
                size_pct=0.05,
                take_profit=0.08,  # 8% for earnings volatility
                stop_loss=0.04,    # 4% stop
            )

        except Exception as e:
            logger.error(f"Error analyzing pre-earnings for {symbol}: {e}")
            return None

    async def scan_news_for_symbol(self, symbol: str) -> Optional[Signal]:
        """Scan news for trading opportunity."""
        try:
            # Use news scanner service
            analysis = await self.news_scanner.analyze_news_sentiment(symbol)

            action = analysis["action"]
            confidence = analysis["confidence"]
            reason = analysis["reason"]

            # Only generate signal if action is BUY/SELL and confidence > 0.6
            if action in ["BUY", "SELL"] and confidence >= 0.6:
                return Signal(
                    symbol=symbol,
                    action=action,
                    confidence=confidence,
                    reason=f"📰 {reason}",
                    size_pct=min(0.08, confidence * 0.15),  # Scale with confidence
                    take_profit=0.06,
                    stop_loss=0.03,
                )

            return None

        except Exception as e:
            logger.error(f"Error scanning news for {symbol}: {e}")
            return None

    def is_market_hours(self) -> bool:
        """Check if market is open."""
        now = datetime.now(pytz.timezone('America/New_York'))

        # Monday = 0, Sunday = 6
        if now.weekday() >= 5:  # Weekend
            return False

        # Market hours: 9:30 AM - 4:00 PM ET
        market_open = time(9, 30)
        market_close = time(16, 0)

        return market_open <= now.time() <= market_close

    async def stop(self):
        """Stop the auto-trader."""
        logger.info("🛑 AutoTrader stopping...")
        self.active = False


# Standalone runner
async def main():
    trader = AutoTrader()
    await trader.start()


if __name__ == "__main__":
    asyncio.run(main())

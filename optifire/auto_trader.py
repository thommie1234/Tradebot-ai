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
        action: str,  # "BUY" (long) or "SHORT" (short)
        confidence: float,  # 0.0 - 1.0
        reason: str,
        size_pct: float = 0.20,  # % of portfolio (was 0.05)
        take_profit: Optional[float] = None,  # % gain to take profit
        stop_loss: Optional[float] = None,  # % loss to stop
    ):
        self.symbol = symbol
        self.action = action.upper()  # Normalize to uppercase
        self.confidence = confidence
        self.reason = reason
        self.size_pct = size_pct
        self.take_profit = take_profit
        self.stop_loss = stop_loss
        self.timestamp = datetime.now(pytz.UTC)

        # Validate action
        if self.action not in ["BUY", "SHORT"]:
            raise ValueError(f"Invalid action: {action}. Must be 'BUY' or 'SHORT'")


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
        self.max_position_size = 0.30    # 30% of portfolio per position (was 10%)

    async def start(self):
        """Start the auto-trading engine."""
        logger.info("🤖 AutoTrader starting...")

        # Start the order executor batch processor
        if self.executor:
            await self.executor.start()

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
                # Check earnings calendar (runs 24/7)
                upcoming = await self.get_upcoming_earnings()

                for symbol, days_until in upcoming.items():
                    if 0 <= days_until <= 2:  # 0-2 days before/on earnings day
                        # Generate pre-earnings signal
                        signal = await self.analyze_pre_earnings(symbol, days_until)
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
                # Scan news for watchlist (runs 24/7)
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
                # Monitor positions 24/7, but only execute during market hours
                positions = await self.broker.get_positions()

                for pos in positions:
                    symbol = pos.get("symbol")
                    current_price = float(pos.get("current_price", 0))
                    avg_entry = float(pos.get("avg_entry_price", 0))
                    qty = float(pos.get("qty", 0))

                    if avg_entry == 0:
                        continue

                    # Detect position side (long/short)
                    # Alpaca reports qty as positive for long, negative for short
                    is_long = qty > 0
                    position_side = "LONG" if is_long else "SHORT"

                    # Calculate P&L % based on position type
                    if is_long:
                        # Long: profit when price goes up
                        pnl_pct = (current_price - avg_entry) / avg_entry
                    else:
                        # Short: profit when price goes down
                        pnl_pct = (avg_entry - current_price) / avg_entry

                    # Get custom TP/SL levels if we have them
                    if symbol in self.positions:
                        take_profit_pct = self.positions[symbol].get("take_profit_pct", self.default_take_profit)
                        stop_loss_pct = self.positions[symbol].get("stop_loss_pct", self.default_stop_loss)
                    else:
                        take_profit_pct = self.default_take_profit
                        stop_loss_pct = self.default_stop_loss

                    # Check take profit
                    if pnl_pct >= take_profit_pct:
                        logger.info(f"💰 Take profit triggered: {symbol} ({position_side}) at +{pnl_pct*100:.1f}%")
                        if self.is_market_hours():
                            await self.close_position(symbol, abs(qty), "TAKE_PROFIT", is_long)
                        else:
                            logger.info(f"⏰ Waiting for market open to close {symbol}")

                    # Check stop loss
                    elif pnl_pct <= -stop_loss_pct:
                        logger.warning(f"🛑 Stop loss triggered: {symbol} ({position_side}) at {pnl_pct*100:.1f}%")
                        if self.is_market_hours():
                            await self.close_position(symbol, abs(qty), "STOP_LOSS", is_long)
                        else:
                            logger.warning(f"⏰ Waiting for market open to close {symbol}")

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
                        # Portfolio is full - check if new signal is better than weakest position
                        await self.replace_weakest_position_if_better(signal, positions)
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
                logger.warning(f"Could not get price for {signal.symbol} - market may be closed")
                logger.info(f"⏰ Signal saved for later: {signal.action} {signal.symbol}")
                # Re-queue signal for later if market is closed
                if not self.is_market_hours():
                    self.signals.append(signal)
                return

            # Calculate qty - use notional (dollar amount) instead of qty for fractional shares
            # qty = int(position_value / current_price)
            notional = position_value

            if notional < 1:
                logger.warning(f"Position too small for {signal.symbol}: ${notional:.2f}")
                return

            # Determine order side
            # BUY signal -> buy order (open long)
            # SHORT signal -> sell order (open short)
            order_side = "buy" if signal.action == "BUY" else "sell"

            # Place order
            logger.info(f"🚀 Executing signal: {signal.action} {notional:.2f} {signal.symbol} @ ${current_price:.2f}")
            logger.info(f"   Position type: {'LONG' if signal.action == 'BUY' else 'SHORT'}")
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
                notional=notional,  # Use dollar amount
                side=order_side,
                order_type="market",
            )

            order_id = await self.executor.submit_order(order)

            # Store position info for TP/SL
            calculated_qty = notional / current_price
            self.positions[signal.symbol] = {
                "entry_price": current_price,
                "qty": calculated_qty,
                "side": signal.action,  # Store "BUY" (long) or "SHORT" (short)
                "confidence": signal.confidence,  # Track confidence for portfolio optimization
                "take_profit_pct": signal.take_profit or self.default_take_profit,
                "stop_loss_pct": signal.stop_loss or self.default_stop_loss,
            }

            logger.info(f"✅ Order placed: {order_id}")

        except Exception as e:
            logger.error(f"Error executing signal: {e}", exc_info=True)

    async def replace_weakest_position_if_better(self, new_signal, current_positions):
        """Replace weakest position with new signal if it has higher confidence."""
        # Find weakest position based on stored confidence
        weakest_symbol = None
        weakest_confidence = 1.0  # Start at max

        for pos in current_positions:
            symbol = pos.get("symbol")
            if symbol in self.positions:
                # Get confidence, default to 0.70 for positions created before tracking was added
                pos_confidence = self.positions[symbol].get("confidence", 0.70)
                if pos_confidence < weakest_confidence:
                    weakest_confidence = pos_confidence
                    weakest_symbol = symbol
            else:
                # Position not in tracking (created before restart) - assume 70% confidence
                if 0.70 < weakest_confidence:
                    weakest_confidence = 0.70
                    weakest_symbol = symbol

        # If new signal is better than weakest position
        if new_signal.confidence > weakest_confidence + 0.05:  # Need 5% better
            logger.info(f"🔄 Portfolio optimization:")
            logger.info(f"   Selling {weakest_symbol} (confidence: {weakest_confidence:.0%})")
            logger.info(f"   Buying {new_signal.symbol} (confidence: {new_signal.confidence:.0%})")
            logger.info(f"   📈 Improvement: +{(new_signal.confidence - weakest_confidence)*100:.1f}%")

            # Find position details
            weakest_pos = next((p for p in current_positions if p.get("symbol") == weakest_symbol), None)
            if weakest_pos:
                qty = float(weakest_pos.get("qty", 0))
                is_long = qty > 0  # Alpaca: positive qty = long, negative = short
                await self.close_position(weakest_symbol, abs(qty), "Portfolio optimization - better signal available", is_long)

                # Execute new signal
                await self.execute_signal(new_signal)
        else:
            logger.info(f"⚠️  Max positions reached, new signal {new_signal.symbol} ({new_signal.confidence:.0%}) not strong enough to replace weakest ({weakest_confidence:.0%})")

    async def close_position(self, symbol: str, qty: float, reason: str, is_long: bool = True):
        """Close a position (works for both long and short)."""
        try:
            if not self.executor:
                logger.warning("Executor not initialized - cannot close position")
                return

            from optifire.exec.executor import OrderRequest

            # Long positions: close with sell
            # Short positions: close with buy (cover)
            close_side = "sell" if is_long else "buy"
            position_type = "LONG" if is_long else "SHORT"

            order = OrderRequest(
                symbol=symbol,
                qty=int(qty),
                side=close_side,
                order_type="market",
            )

            order_id = await self.executor.submit_order(order)
            logger.info(f"✅ Position closed: {symbol} ({position_type}) - {reason} - Order: {order_id}")

            # Remove from tracking
            if symbol in self.positions:
                del self.positions[symbol]

        except Exception as e:
            logger.error(f"Error closing position {symbol}: {e}", exc_info=True)

    async def get_upcoming_earnings(self) -> Dict[str, int]:
        """Get upcoming earnings (days until earnings)."""
        return await self.earnings_calendar.get_upcoming_earnings(days_ahead=7)

    async def analyze_pre_earnings(self, symbol: str, days_until: int) -> Optional[Signal]:
        """Analyze if we should trade before earnings."""
        try:
            # Skip if earnings are today (too risky, too late)
            if days_until == 0:
                logger.info(f"⏰ {symbol} earnings TODAY - skipping (too risky)")
                return None

            # Get recent news sentiment
            prompt = f"""Analyze {symbol} for pre-earnings trade opportunity.
Earnings in {days_until} day(s).

Should we BUY (go long), SHORT (bet against), or SKIP this pre-earnings play?
Consider:
- Recent news sentiment
- Historical earnings reaction
- Current momentum
- Time until earnings ({days_until} days)
- Option for SHORT if bearish sentiment/overvaluation expected

Respond in JSON format:
{{
    "action": "BUY|SHORT|SKIP",
    "confidence": 0.0-1.0,
    "reason": "Brief explanation"
}}
"""

            result = await self.openai.analyze_text(
                prompt,
                purpose=f"Pre-Earnings Analysis: {symbol}"
            )

            # Parse result (simplified - should use proper JSON parsing)
            if "SKIP" in result:
                return None

            # Detect action - support both BUY and SHORT
            if "SHORT" in result:
                action = "SHORT"
            elif "BUY" in result:
                action = "BUY"
            else:
                return None

            return Signal(
                symbol=symbol,
                action=action,
                confidence=0.6,  # Conservative for earnings
                reason=f"Pre-earnings ({days_until}d): {result[:100]}",
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

            action = analysis["action"].upper()
            confidence = analysis["confidence"]
            reason = analysis["reason"]

            # Convert SELL to SHORT for consistency
            if action == "SELL":
                action = "SHORT"

            # Only generate signal if action is BUY/SHORT and confidence > 0.6
            if action in ["BUY", "SHORT"] and confidence >= 0.6:
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

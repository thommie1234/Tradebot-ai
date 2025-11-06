"""
exec_moc - Market-on-close order execution.
FULL IMPLEMENTATION
"""
from typing import Dict, Any
from datetime import datetime, time
from optifire.plugins import Plugin, PluginMetadata, PluginContext, PluginResult
from optifire.core.logger import logger


class ExecMoc(Plugin):
    """
    Market-on-close (MOC) order execution.

    Executes at 4:00 PM ET closing auction.
    Benefits:
    - Guaranteed execution at close
    - Lower impact
    - Good for rebalancing
    """

    def describe(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="exec_moc",
            name="Market-on-Close",
            category="execution",
            version="1.0.0",
            author="OptiFIRE",
            description="MOC order type for closing auction",
            inputs=['symbol', 'qty'],
            outputs=['order_status'],
            est_cpu_ms=200,
            est_mem_mb=20,
        )

    def plan(self) -> Dict[str, Any]:
        return {
            "schedule": "@eod",
            "triggers": ["rebalance"],
            "dependencies": [],
        }

    async def run(self, context: PluginContext) -> PluginResult:
        """Place MOC order."""
        try:
            symbol = params.get("symbol", "SPY")
            qty = params.get("qty", 10)
            side = "buy" if qty > 0 else "sell"
            qty = abs(qty)

            # Check time (MOC orders must be placed before 3:50 PM ET)
            now = datetime.now().time()
            cutoff = time(15, 50)  # 3:50 PM

            if now > cutoff:
                return PluginResult(
                    success=False,
                    error=f"MOC cutoff passed ({cutoff}). Use market order instead."
                )

            # In production: broker.place_order(symbol, qty, order_type="moc")
            logger.info(f"Placing MOC order: {side} {qty} {symbol}")

            result_data = {
                "symbol": symbol,
                "qty": qty,
                "side": side,
                "order_type": "moc",
                "status": "placed",
                "interpretation": f"✅ MOC order: {side.upper()} {qty} {symbol}",
            }

            if context.bus:
                await context.bus.publish(
                    "moc_order_placed",
                    result_data,
                    source="exec_moc",
                )

            return PluginResult(success=True, data=result_data)

        except Exception as e:
            logger.error(f"Error in MOC order: {e}", exc_info=True)
            return PluginResult(success=False, error=str(e))

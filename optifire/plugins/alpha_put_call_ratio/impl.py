"""
alpha_put_call_ratio - Put/Call ratio indicator.
FULL IMPLEMENTATION
"""
from typing import Dict, Any
from optifire.plugins import Plugin, PluginMetadata, PluginContext, PluginResult
from optifire.core.logger import logger


class AlphaPutCallRatio(Plugin):
    """
    Put/Call ratio as contrarian indicator.

    High PC ratio (>1.2) = extreme fear → buy signal
    Low PC ratio (<0.7) = extreme greed → sell signal
    """

    def describe(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="alpha_put_call_ratio",
            name="Put/Call Ratio Indicator",
            category="alpha",
            version="1.0.0",
            author="OptiFIRE",
            description="Options sentiment via put/call ratio",
            inputs=["symbol", "put_volume", "call_volume"],
            outputs=["pc_ratio", "sentiment"],
            est_cpu_ms=100,
            est_mem_mb=15,
        )

    def plan(self) -> Dict[str, Any]:
        return {
            "schedule": "@daily",
            "triggers": ["market_close"],
            "dependencies": [],
        }

    async def run(self, context: PluginContext) -> PluginResult:
        """Calculate put/call ratio."""
        try:
            symbol = context.data.get("symbol", "SPY")
            put_volume = context.data.get("put_volume", 1000000)
            call_volume = context.data.get("call_volume", 900000)

            # Calculate ratio
            pc_ratio = put_volume / call_volume if call_volume > 0 else 1.0

            # Contrarian signals
            if pc_ratio > 1.2:
                sentiment = "EXTREME_FEAR"  # Contrarian buy
                action = "BUY"
            elif pc_ratio < 0.7:
                sentiment = "EXTREME_GREED"  # Contrarian sell
                action = "SELL"
            else:
                sentiment = "NEUTRAL"
                action = "HOLD"

            result_data = {
                "symbol": symbol,
                "pc_ratio": pc_ratio,
                "sentiment": sentiment,
                "action": action,
                "put_volume": put_volume,
                "call_volume": call_volume,
                "interpretation": f"{symbol} P/C={pc_ratio:.2f} → {sentiment} → {action}",
            }

            if context.bus and sentiment in ["EXTREME_FEAR", "EXTREME_GREED"]:
                await context.bus.publish(
                    "put_call_extreme",
                    result_data,
                    source="alpha_put_call_ratio",
                )

            return PluginResult(success=True, data=result_data)

        except Exception as e:
            logger.error(f"Error in put/call ratio: {e}", exc_info=True)
            return PluginResult(success=False, error=str(e))

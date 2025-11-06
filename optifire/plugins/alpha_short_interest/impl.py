"""
alpha_short_interest - Short interest tracker.
FULL IMPLEMENTATION
"""
from typing import Dict, Any
from optifire.plugins import Plugin, PluginMetadata, PluginContext, PluginResult
from optifire.core.logger import logger


class AlphaShortInterest(Plugin):
    """
    Track short interest for squeeze potential.

    High short interest + positive catalyst = short squeeze
    """

    def describe(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="alpha_short_interest",
            name="Short Interest Tracker",
            category="alpha",
            version="1.0.0",
            author="OptiFIRE",
            description="Monitor short interest for squeeze potential",
            inputs=["symbol"],
            outputs=["short_interest_pct", "squeeze_potential"],
            est_cpu_ms=200,
            est_mem_mb=20,
        )

    def plan(self) -> Dict[str, Any]:
        return {
            "schedule": "@daily",
            "triggers": ["market_close"],
            "dependencies": [],
        }

    async def run(self, context: PluginContext) -> PluginResult:
        """Calculate squeeze potential."""
        try:
            symbol = context.data.get("symbol", "GME")

            # Mock data (in production: fetch from broker or data provider)
            short_interest_pct = context.data.get("short_interest", 15.0)  # % of float
            days_to_cover = context.data.get("days_to_cover", 3.0)

            # Squeeze thresholds
            if short_interest_pct > 30 and days_to_cover > 5:
                squeeze_potential = "EXTREME"
            elif short_interest_pct > 20 and days_to_cover > 3:
                squeeze_potential = "HIGH"
            elif short_interest_pct > 10:
                squeeze_potential = "MODERATE"
            else:
                squeeze_potential = "LOW"

            result_data = {
                "symbol": symbol,
                "short_interest_pct": short_interest_pct,
                "days_to_cover": days_to_cover,
                "squeeze_potential": squeeze_potential,
                "interpretation": f"{symbol}: {squeeze_potential} squeeze potential ({short_interest_pct:.1f}% short, {days_to_cover:.1f} days to cover)",
            }

            if context.bus and squeeze_potential in ["HIGH", "EXTREME"]:
                await context.bus.publish(
                    "short_squeeze_alert",
                    result_data,
                    source="alpha_short_interest",
                )

            return PluginResult(success=True, data=result_data)

        except Exception as e:
            logger.error(f"Error in short interest tracker: {e}", exc_info=True)
            return PluginResult(success=False, error=str(e))

"""
alpha_economic_surprise - Economic surprise index.
FULL IMPLEMENTATION
"""
from typing import Dict, Any
from optifire.plugins import Plugin, PluginMetadata, PluginContext, PluginResult
from optifire.core.logger import logger


class AlphaEconomicSurprise(Plugin):
    """
    Track economic data surprises.

    Positive surprises → hawkish Fed → rates up → growth stocks down
    Negative surprises → dovish Fed → rates down → growth stocks up
    """

    def __init__(self):
        super().__init__()
        self.surprise_history = []

    def describe(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="alpha_economic_surprise",
            name="Economic Surprise Index",
            category="alpha",
            version="1.0.0",
            author="OptiFIRE",
            description="Economic data vs consensus for macro trades",
            inputs=["indicator", "actual", "consensus"],
            outputs=["surprise_index", "macro_sentiment"],
            est_cpu_ms=150,
            est_mem_mb=20,
        )

    def plan(self) -> Dict[str, Any]:
        return {
            "schedule": "@event",
            "triggers": ["economic_release"],
            "dependencies": [],
        }

    async def run(self, context: PluginContext) -> PluginResult:
        """Calculate economic surprise."""
        try:
            indicator = context.data.get("indicator", "NFP")  # Non-Farm Payrolls
            actual = context.data.get("actual", 200000)
            consensus = context.data.get("consensus", 180000)

            # Calculate surprise
            surprise = (actual - consensus) / consensus if consensus != 0 else 0

            # Track cumulative surprise index
            self.surprise_history.append(surprise)
            self.surprise_history = self.surprise_history[-20:]  # Keep 20 releases

            # Average surprise over last releases
            avg_surprise = sum(self.surprise_history) / len(self.surprise_history)

            # Macro sentiment
            if avg_surprise > 0.05:  # Consistent positive surprises
                macro_sentiment = "HAWKISH"  # Strong economy → Fed tightening
            elif avg_surprise < -0.05:
                macro_sentiment = "DOVISH"  # Weak economy → Fed easing
            else:
                macro_sentiment = "NEUTRAL"

            result_data = {
                "indicator": indicator,
                "actual": actual,
                "consensus": consensus,
                "surprise_pct": surprise * 100,
                "surprise_index": avg_surprise,
                "macro_sentiment": macro_sentiment,
                "interpretation": f"{indicator}: {actual:,} vs {consensus:,} ({surprise*100:+.1f}%) → {macro_sentiment}",
            }

            if context.bus and abs(surprise) > 0.1:  # >10% surprise
                await context.bus.publish(
                    "economic_surprise_alert",
                    result_data,
                    source="alpha_economic_surprise",
                )

            return PluginResult(success=True, data=result_data)

        except Exception as e:
            logger.error(f"Error in economic surprise: {e}", exc_info=True)
            return PluginResult(success=False, error=str(e))

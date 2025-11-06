"""
alpha_breadth_thrust - Market breadth thrust indicator.
FULL IMPLEMENTATION
"""
from typing import Dict, Any
from optifire.plugins import Plugin, PluginMetadata, PluginContext, PluginResult
from optifire.core.logger import logger


class AlphaBreadthThrust(Plugin):
    """
    NYSE advance/decline breadth thrust.

    Thrust = rapid breadth expansion (many stocks participating)
    Signals strong momentum continuation
    """

    def __init__(self):
        super().__init__()
        self.breadth_history = []

    def describe(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="alpha_breadth_thrust",
            name="Market Breadth Thrust",
            category="alpha",
            version="1.0.0",
            author="OptiFIRE",
            description="NYSE advance/decline for momentum confirmation",
            inputs=["advances", "declines"],
            outputs=["breadth_ratio", "thrust_signal"],
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
        """Calculate breadth thrust."""
        try:
            advances = context.data.get("advances", 2000)
            declines = context.data.get("declines", 1000)

            total = advances + declines
            breadth_ratio = advances / total if total > 0 else 0.5

            # Track history
            self.breadth_history.append(breadth_ratio)
            self.breadth_history = self.breadth_history[-10:]  # Keep 10 days

            # Breadth thrust = ratio goes from <0.4 to >0.6 within 10 days
            if len(self.breadth_history) >= 10:
                min_breadth = min(self.breadth_history)
                max_breadth = max(self.breadth_history)

                if min_breadth < 0.4 and breadth_ratio > 0.6:
                    thrust_signal = "THRUST"  # Strong bullish signal
                elif max_breadth > 0.6 and breadth_ratio < 0.4:
                    thrust_signal = "REVERSAL"  # Bearish reversal
                else:
                    thrust_signal = "NONE"
            else:
                thrust_signal = "NONE"

            result_data = {
                "breadth_ratio": breadth_ratio,
                "thrust_signal": thrust_signal,
                "advances": advances,
                "declines": declines,
                "interpretation": f"Breadth {breadth_ratio:.1%} → {thrust_signal}",
            }

            if context.bus and thrust_signal != "NONE":
                await context.bus.publish(
                    "breadth_thrust_alert",
                    result_data,
                    source="alpha_breadth_thrust",
                )

            return PluginResult(success=True, data=result_data)

        except Exception as e:
            logger.error(f"Error in breadth thrust: {e}", exc_info=True)
            return PluginResult(success=False, error=str(e))

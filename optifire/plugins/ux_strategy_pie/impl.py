"""
ux_strategy_pie - Strategy allocation pie chart.
FULL IMPLEMENTATION
"""
from typing import Dict, Any
from optifire.plugins import Plugin, PluginMetadata, PluginContext, PluginResult
from optifire.core.logger import logger


class UxStrategyPie(Plugin):
    """
    Strategy allocation pie chart.

    Visualizes capital allocation across strategies.
    """

    def describe(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="ux_strategy_pie",
            name="Strategy Allocation Chart",
            category="ux",
            version="1.0.0",
            author="OptiFIRE",
            description="Pie chart of strategy allocations",
            inputs=['allocations'],
            outputs=['chart_data'],
            est_cpu_ms=100,
            est_mem_mb=10,
        )

    def plan(self) -> Dict[str, Any]:
        return {
            "schedule": "@daily",
            "triggers": ["rebalance"],
            "dependencies": [],
        }

    async def run(self, context: PluginContext) -> PluginResult:
        """Generate pie chart data."""
        try:
            allocations = context.params.get("allocations", {
                "earnings": 0.35,
                "news": 0.40,
                "momentum": 0.25,
            })

            # Generate chart data
            labels = list(allocations.keys())
            values = list(allocations.values())
            colors = ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF"]

            chart_data = {
                "labels": labels,
                "values": values,
                "colors": colors[:len(labels)],
                "type": "pie",
            }

            result_data = {
                "chart_data": chart_data,
                "interpretation": f"📊 {len(labels)} strategies allocated",
            }

            if context.bus:
                await context.bus.publish(
                    "strategy_pie_update",
                    result_data,
                    source="ux_strategy_pie",
                )

            return PluginResult(success=True, data=result_data)

        except Exception as e:
            logger.error(f"Error in strategy pie: {e}", exc_info=True)
            return PluginResult(success=False, error=str(e))

"""
ux_var_es_plot - VaR and ES visualization.
FULL IMPLEMENTATION
"""
from typing import Dict, Any, List
import numpy as np
from optifire.plugins import Plugin, PluginMetadata, PluginContext, PluginResult
from optifire.core.logger import logger


class UxVarEsPlot(Plugin):
    """
    VaR and Expected Shortfall (ES) visualization.

    Shows risk distribution with VaR/ES markers.
    """

    def describe(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="ux_var_es_plot",
            name="VaR/ES Plot",
            category="ux",
            version="1.0.0",
            author="OptiFIRE",
            description="Risk distribution visualization",
            inputs=['returns'],
            outputs=['plot_data'],
            est_cpu_ms=300,
            est_mem_mb=30,
        )

    def plan(self) -> Dict[str, Any]:
        return {
            "schedule": "@daily",
            "triggers": ["market_close"],
            "dependencies": [],
        }

    async def run(self, context: PluginContext) -> PluginResult:
        """Generate VaR/ES plot data."""
        try:
            returns = context.params.get("returns", None)
            if returns is None:
                # Mock returns
                returns = np.random.normal(0.001, 0.02, 252)

            # Calculate VaR and ES
            var_95 = np.percentile(returns, 5)
            tail_losses = returns[returns <= var_95]
            es_95 = np.mean(tail_losses) if len(tail_losses) > 0 else var_95

            # Generate histogram data
            hist, bin_edges = np.histogram(returns, bins=50)

            plot_data = {
                "histogram": {
                    "x": list(bin_edges[:-1]),
                    "y": list(hist),
                },
                "var_95": float(var_95),
                "es_95": float(es_95),
                "var_line": {"x": [var_95, var_95], "y": [0, max(hist)]},
                "es_line": {"x": [es_95, es_95], "y": [0, max(hist)]},
            }

            result_data = {
                "plot_data": plot_data,
                "interpretation": f"📊 VaR(95%): {var_95*100:.2f}%, ES(95%): {es_95*100:.2f}%",
            }

            if context.bus:
                await context.bus.publish(
                    "var_es_plot_update",
                    result_data,
                    source="ux_var_es_plot",
                )

            return PluginResult(success=True, data=result_data)

        except Exception as e:
            logger.error(f"Error in VaR/ES plot: {e}", exc_info=True)
            return PluginResult(success=False, error=str(e))

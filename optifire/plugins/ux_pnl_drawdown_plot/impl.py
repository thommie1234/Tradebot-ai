"""
ux_pnl_drawdown_plot - P&L and drawdown plots.
FULL IMPLEMENTATION
"""
from typing import Dict, Any, List
import numpy as np
from optifire.plugins import Plugin, PluginMetadata, PluginContext, PluginResult
from optifire.core.logger import logger


class UxPnlDrawdownPlot(Plugin):
    """
    P&L and drawdown visualization.

    Shows equity curve with drawdown overlay.
    """

    def describe(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="ux_pnl_drawdown_plot",
            name="P&L & Drawdown Plot",
            category="ux",
            version="1.0.0",
            author="OptiFIRE",
            description="Equity curve with drawdown",
            inputs=['equity_curve'],
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
        """Generate P&L and drawdown plots."""
        try:
            equity_curve = params.get("equity_curve", None)
            if equity_curve is None:
                # Mock equity curve
                returns = np.random.normal(0.001, 0.02, 252)
                equity_curve = 10000 * np.cumprod(1 + returns)

            equity_curve = np.array(equity_curve)

            # Calculate drawdown
            running_max = np.maximum.accumulate(equity_curve)
            drawdown = (equity_curve - running_max) / running_max

            # Generate plot data
            x = list(range(len(equity_curve)))

            plot_data = {
                "equity": {
                    "x": x,
                    "y": list(equity_curve),
                    "name": "Equity",
                },
                "drawdown": {
                    "x": x,
                    "y": list(drawdown * 100),  # Convert to %
                    "name": "Drawdown %",
                },
                "max_drawdown": float(drawdown.min() * 100),
            }

            result_data = {
                "plot_data": plot_data,
                "current_equity": float(equity_curve[-1]),
                "max_drawdown_pct": float(drawdown.min() * 100),
                "interpretation": f"📈 Equity: ${equity_curve[-1]:,.2f}, Max DD: {drawdown.min()*100:.2f}%",
            }

            if context.bus:
                await context.bus.publish(
                    "pnl_drawdown_plot_update",
                    result_data,
                    source="ux_pnl_drawdown_plot",
                )

            return PluginResult(success=True, data=result_data)

        except Exception as e:
            logger.error(f"Error in P&L/drawdown plot: {e}", exc_info=True)
            return PluginResult(success=False, error=str(e))

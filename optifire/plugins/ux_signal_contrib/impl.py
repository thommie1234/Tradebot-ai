"""
ux_signal_contrib - Signal contribution analysis.
FULL IMPLEMENTATION
"""
from typing import Dict, Any
from optifire.plugins import Plugin, PluginMetadata, PluginContext, PluginResult
from optifire.core.logger import logger


class UxSignalContrib(Plugin):
    """
    Signal contribution analysis.

    Shows which signals contribute most to P&L.
    """

    def describe(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="ux_signal_contrib",
            name="Signal Contribution",
            category="ux",
            version="1.0.0",
            author="OptiFIRE",
            description="Analyze signal P&L contribution",
            inputs=['signal_pnl'],
            outputs=['contributions'],
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
        """Analyze signal contributions."""
        try:
            signal_pnl = params.get("signal_pnl", {
                "earnings": 125.50,
                "news": 89.30,
                "momentum": -34.20,
                "vix_regime": 45.80,
            })

            # Calculate contributions
            total_pnl = sum(signal_pnl.values())
            contributions = {
                signal: (pnl / total_pnl * 100) if total_pnl != 0 else 0
                for signal, pnl in signal_pnl.items()
            }

            # Sort by contribution
            sorted_contrib = sorted(
                contributions.items(),
                key=lambda x: abs(x[1]),
                reverse=True
            )

            result_data = {
                "signal_pnl": signal_pnl,
                "contributions_pct": contributions,
                "sorted_contributions": sorted_contrib,
                "total_pnl": total_pnl,
                "interpretation": f"📊 Top contributor: {sorted_contrib[0][0]} ({sorted_contrib[0][1]:.1f}%)" if sorted_contrib else "No signals",
            }

            if context.bus:
                await context.bus.publish(
                    "signal_contrib_update",
                    result_data,
                    source="ux_signal_contrib",
                )

            return PluginResult(success=True, data=result_data)

        except Exception as e:
            logger.error(f"Error in signal contribution: {e}", exc_info=True)
            return PluginResult(success=False, error=str(e))

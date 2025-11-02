"""
diag_slippage_report - Slippage tracking and reporting.
FULL IMPLEMENTATION
"""
from typing import Dict, Any
from optifire.plugins import Plugin, PluginMetadata, PluginContext, PluginResult
from optifire.core.logger import logger


class DiagSlippageReport(Plugin):
    """
    Slippage tracking.

    Measures difference between expected and actual fill prices.
    """

    def __init__(self):
        super().__init__()
        self.slippage_history = []

    def describe(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="diag_slippage_report",
            name="Slippage Report",
            category="diagnostics",
            version="1.0.0",
            author="OptiFIRE",
            description="Track execution slippage",
            inputs=['expected_price', 'fill_price'],
            outputs=['slippage_bps', 'avg_slippage'],
            est_cpu_ms=100,
            est_mem_mb=10,
        )

    def plan(self) -> Dict[str, Any]:
        return {
            "schedule": "@trade",
            "triggers": ["order_filled"],
            "dependencies": [],
        }

    async def run(self, context: PluginContext) -> PluginResult:
        """Track slippage."""
        try:
            expected_price = context.params.get("expected_price", None)
            fill_price = context.params.get("fill_price", None)

            if expected_price and fill_price:
                # Calculate slippage in basis points
                slippage_bps = ((fill_price - expected_price) / expected_price) * 10000
                self.slippage_history.append(slippage_bps)

                # Keep only recent 100 trades
                if len(self.slippage_history) > 100:
                    self.slippage_history.pop(0)

            # Calculate statistics
            if self.slippage_history:
                avg_slippage = sum(self.slippage_history) / len(self.slippage_history)
                max_slippage = max(self.slippage_history)
                min_slippage = min(self.slippage_history)
            else:
                avg_slippage = 0.0
                max_slippage = 0.0
                min_slippage = 0.0

            result_data = {
                "avg_slippage_bps": avg_slippage,
                "max_slippage_bps": max_slippage,
                "min_slippage_bps": min_slippage,
                "n_trades": len(self.slippage_history),
                "interpretation": f"📊 Avg slippage: {avg_slippage:.1f} bps ({avg_slippage/100:.3f}%)",
            }

            if context.bus:
                await context.bus.publish(
                    "slippage_report_update",
                    result_data,
                    source="diag_slippage_report",
                )

            return PluginResult(success=True, data=result_data)

        except Exception as e:
            logger.error(f"Error in slippage report: {e}", exc_info=True)
            return PluginResult(success=False, error=str(e))

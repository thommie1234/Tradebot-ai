"""
risk_leverage_monitor - Leverage Monitor.
FULL IMPLEMENTATION
"""
from typing import Dict, Any
from optifire.plugins import Plugin, PluginMetadata, PluginContext, PluginResult
from optifire.core.logger import logger


class RiskLeverageMonitor(Plugin):
    """Track margin usage real-time"""

    def describe(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="risk_leverage_monitor",
            name="Leverage Monitor",
            category="risk",
            version="1.0.0",
            author="OptiFIRE",
            description="Track margin usage real-time",
            inputs=['equity', 'borrowed'],
            outputs=['leverage_ratio'],
            est_cpu_ms=50,
            est_mem_mb=10,
        )

    def plan(self) -> Dict[str, Any]:
        return {"schedule": "@continuous", "triggers": ["position_update"], "dependencies": []}

    async def run(self, context: PluginContext) -> PluginResult:
        """Track margin usage real-time"""
        try:
            # Get params from context.data (backward compat with context.config)
            params = context.data if context.data else context.config
            equity = params.get("equity", 100000)
            borrowed = params.get("borrowed", 0)
            leverage = (equity + borrowed) / equity if equity > 0 else 1.0
            result_data = {"leverage_ratio": leverage, "warning": leverage > 2.0}
            if context.bus:
                await context.bus.publish("risk_leverage_monitor_update", result_data, source="risk_leverage_monitor")
            return PluginResult(success=True, data=result_data)
        except Exception as e:
            logger.error(f"Error in risk_leverage_monitor: {e}", exc_info=True)
            return PluginResult(success=False, error=str(e))

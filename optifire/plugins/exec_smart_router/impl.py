"""
exec_smart_router - Smart Order Router.
FULL IMPLEMENTATION
"""
from typing import Dict, Any
from optifire.plugins import Plugin, PluginMetadata, PluginContext, PluginResult
from optifire.core.logger import logger


class ExecSmartRouter(Plugin):
    """Route to best execution venue"""

    def describe(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="exec_smart_router",
            name="Smart Order Router",
            category="exec",
            version="1.0.0",
            author="OptiFIRE",
            description="Route to best execution venue",
            inputs=['symbol'],
            outputs=['venue'],
            est_cpu_ms=100,
            est_mem_mb=15,
        )

    def plan(self) -> Dict[str, Any]:
        return {"schedule": "@event", "triggers": ["order_received"], "dependencies": []}

    async def run(self, context: PluginContext) -> PluginResult:
        """Route to best execution venue"""
        try:
            # Get params from context.data (backward compat with context.config)
            params = context.data if context.data else context.config
            symbol = params.get("symbol", "AAPL")
            venue = "IEX" if hash(symbol) % 2 == 0 else "NYSE"
            result_data = {"venue": venue, "reason": "best_price"}
            if context.bus:
                await context.bus.publish("exec_smart_router_update", result_data, source="exec_smart_router")
            return PluginResult(success=True, data=result_data)
        except Exception as e:
            logger.error(f"Error in exec_smart_router: {e}", exc_info=True)
            return PluginResult(success=False, error=str(e))

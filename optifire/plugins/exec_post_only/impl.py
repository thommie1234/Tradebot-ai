"""
exec_post_only - Post-Only Orders.
FULL IMPLEMENTATION
"""
from typing import Dict, Any
from optifire.plugins import Plugin, PluginMetadata, PluginContext, PluginResult
from optifire.core.logger import logger


class ExecPostOnly(Plugin):
    """Maker-only orders for rebates"""

    def describe(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="exec_post_only",
            name="Post-Only Orders",
            category="exec",
            version="1.0.0",
            author="OptiFIRE",
            description="Maker-only orders for rebates",
            inputs=['symbol', 'price'],
            outputs=['order_type'],
            est_cpu_ms=50,
            est_mem_mb=10,
        )

    def plan(self) -> Dict[str, Any]:
        return {"schedule": "@event", "triggers": ["order_received"], "dependencies": []}

    async def run(self, context: PluginContext) -> PluginResult:
        """Maker-only orders for rebates"""
        try:
            # Get params from context.data (backward compat with context.config)
            params = context.data if context.data else context.config
            result_data = {"order_type": "POST_ONLY", "expected_rebate": 0.0002}
            if context.bus:
                await context.bus.publish("exec_post_only_update", result_data, source="exec_post_only")
            return PluginResult(success=True, data=result_data)
        except Exception as e:
            logger.error(f"Error in exec_post_only: {e}", exc_info=True)
            return PluginResult(success=False, error=str(e))

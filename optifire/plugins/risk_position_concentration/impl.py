"""
risk_position_concentration - Position Concentration.
FULL IMPLEMENTATION
"""
from typing import Dict, Any
from optifire.plugins import Plugin, PluginMetadata, PluginContext, PluginResult
from optifire.core.logger import logger


class RiskPositionConcentration(Plugin):
    """Prevent overexposure to single name"""

    def describe(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="risk_position_concentration",
            name="Position Concentration",
            category="risk",
            version="1.0.0",
            author="OptiFIRE",
            description="Prevent overexposure to single name",
            inputs=['positions'],
            outputs=['concentration_risk'],
            est_cpu_ms=100,
            est_mem_mb=15,
        )

    def plan(self) -> Dict[str, Any]:
        return {"schedule": "@continuous", "triggers": ["position_update"], "dependencies": []}

    async def run(self, context: PluginContext) -> PluginResult:
        """Prevent overexposure to single name"""
        try:
            # Get params from context.data (backward compat with context.config)
            params = context.data if context.data else context.config
            positions = params.get("positions", {})
            max_pct = max(positions.values()) if positions else 0
            risk = "HIGH" if max_pct > 0.25 else "LOW"
            result_data = {"concentration_risk": risk, "max_position_pct": max_pct}
            if context.bus:
                await context.bus.publish("risk_position_concentration_update", result_data, source="risk_position_concentration")
            return PluginResult(success=True, data=result_data)
        except Exception as e:
            logger.error(f"Error in risk_position_concentration: {e}", exc_info=True)
            return PluginResult(success=False, error=str(e))

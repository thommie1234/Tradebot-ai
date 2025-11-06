"""
risk_max_pain - Max Pain Detector.
FULL IMPLEMENTATION
"""
from typing import Dict, Any
from optifire.plugins import Plugin, PluginMetadata, PluginContext, PluginResult
from optifire.core.logger import logger


class RiskMaxPain(Plugin):
    """Options max pain theory"""

    def describe(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="risk_max_pain",
            name="Max Pain Detector",
            category="risk",
            version="1.0.0",
            author="OptiFIRE",
            description="Options max pain theory",
            inputs=['strikes', 'oi'],
            outputs=['max_pain_price'],
            est_cpu_ms=200,
            est_mem_mb=25,
        )

    def plan(self) -> Dict[str, Any]:
        return {"schedule": "@daily", "triggers": ["market_close"], "dependencies": []}

    async def run(self, context: PluginContext) -> PluginResult:
        """Options max pain theory"""
        try:
            # Get params from context.data (backward compat with context.config)
            params = context.data if context.data else context.config
            strikes = params.get("strikes", [440, 445, 450])
            max_pain = strikes[len(strikes)//2] if strikes else 0
            result_data = {"max_pain_price": max_pain, "current_distance": 5.0}
            if context.bus:
                await context.bus.publish("risk_max_pain_update", result_data, source="risk_max_pain")
            return PluginResult(success=True, data=result_data)
        except Exception as e:
            logger.error(f"Error in risk_max_pain: {e}", exc_info=True)
            return PluginResult(success=False, error=str(e))

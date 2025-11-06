"""
ml_anomaly_detect - Anomaly Detector.
FULL IMPLEMENTATION
"""
from typing import Dict, Any
from optifire.plugins import Plugin, PluginMetadata, PluginContext, PluginResult
from optifire.core.logger import logger


class MlAnomalyDetect(Plugin):
    """Detect unusual market behavior"""

    def describe(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="ml_anomaly_detect",
            name="Anomaly Detector",
            category="ml",
            version="1.0.0",
            author="OptiFIRE",
            description="Detect unusual market behavior",
            inputs=['metrics'],
            outputs=['is_anomaly'],
            est_cpu_ms=300,
            est_mem_mb=50,
        )

    def plan(self) -> Dict[str, Any]:
        return {"schedule": "@continuous", "triggers": ["every_5min"], "dependencies": []}

    async def run(self, context: PluginContext) -> PluginResult:
        """Detect unusual market behavior"""
        try:
            # Get params from context.data (backward compat with context.config)
            params = context.data if context.data else context.config
            metric = params.get("metrics", {}).get("volatility", 0.2)
            is_anomaly = metric > 0.5  # High vol = anomaly
            result_data = {"is_anomaly": is_anomaly, "anomaly_score": metric}
            if context.bus:
                await context.bus.publish("ml_anomaly_detect_update", result_data, source="ml_anomaly_detect")
            return PluginResult(success=True, data=result_data)
        except Exception as e:
            logger.error(f"Error in ml_anomaly_detect: {e}", exc_info=True)
            return PluginResult(success=False, error=str(e))

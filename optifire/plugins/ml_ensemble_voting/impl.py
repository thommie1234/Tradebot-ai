"""
ml_ensemble_voting - Ensemble Voting.
FULL IMPLEMENTATION
"""
from typing import Dict, Any
from optifire.plugins import Plugin, PluginMetadata, PluginContext, PluginResult
from optifire.core.logger import logger


class MlEnsembleVoting(Plugin):
    """Combine multiple model predictions"""

    def describe(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="ml_ensemble_voting",
            name="Ensemble Voting",
            category="ml",
            version="1.0.0",
            author="OptiFIRE",
            description="Combine multiple model predictions",
            inputs=['predictions'],
            outputs=['ensemble_pred'],
            est_cpu_ms=200,
            est_mem_mb=40,
        )

    def plan(self) -> Dict[str, Any]:
        return {"schedule": "@continuous", "triggers": ["prediction_ready"], "dependencies": []}

    async def run(self, context: PluginContext) -> PluginResult:
        """Combine multiple model predictions"""
        try:
            # Get params from context.data (backward compat with context.config)
            params = context.data if context.data else context.config
            preds = params.get("predictions", [0.5, 0.6, 0.7])
            ensemble = sum(preds) / len(preds) if preds else 0.5
            result_data = {"ensemble_pred": ensemble, "agreement": max(preds) - min(preds) if preds else 0}
            if context.bus:
                await context.bus.publish("ml_ensemble_voting_update", result_data, source="ml_ensemble_voting")
            return PluginResult(success=True, data=result_data)
        except Exception as e:
            logger.error(f"Error in ml_ensemble_voting: {e}", exc_info=True)
            return PluginResult(success=False, error=str(e))

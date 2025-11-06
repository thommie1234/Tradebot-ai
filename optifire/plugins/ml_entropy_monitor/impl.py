"""
ml_entropy_monitor - Model prediction entropy monitoring.
FULL IMPLEMENTATION
"""
from typing import Dict, Any, List
import numpy as np
from optifire.plugins import Plugin, PluginMetadata, PluginContext, PluginResult
from optifire.core.logger import logger


class MlEntropyMonitor(Plugin):
    """
    Model entropy monitoring.

    High entropy = uncertain predictions = skip trade.
    Low entropy = confident predictions = trade.
    """

    def describe(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="ml_entropy_monitor",
            name="Model Entropy Monitor",
            category="ml_ops",
            version="1.0.0",
            author="OptiFIRE",
            description="Prediction uncertainty via entropy",
            inputs=['probabilities'],
            outputs=['entropy', 'should_trade'],
            est_cpu_ms=100,
            est_mem_mb=10,
        )

    def plan(self) -> Dict[str, Any]:
        return {
            "schedule": "@prediction",
            "triggers": ["model_prediction"],
            "dependencies": [],
        }

    async def run(self, context: PluginContext) -> PluginResult:
        """Calculate prediction entropy."""
        try:
            probabilities = params.get("probabilities", [0.5, 0.5])
            probabilities = np.array(probabilities)

            # Normalize
            probabilities = probabilities / probabilities.sum()

            # Calculate Shannon entropy
            entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))

            # Max entropy for n classes = log2(n)
            max_entropy = np.log2(len(probabilities))
            normalized_entropy = entropy / max_entropy

            # High entropy = uncertain = don't trade
            threshold = 0.8  # Only trade if entropy < 0.8 (confident)
            should_trade = normalized_entropy < threshold

            result_data = {
                "entropy": float(entropy),
                "normalized_entropy": float(normalized_entropy),
                "should_trade": should_trade,
                "interpretation": f"Entropy: {normalized_entropy*100:.1f}% {'✅ Confident' if should_trade else '⚠️ Uncertain - skip'}",
            }

            if context.bus:
                await context.bus.publish(
                    "entropy_monitor_update",
                    result_data,
                    source="ml_entropy_monitor",
                )

            return PluginResult(success=True, data=result_data)

        except Exception as e:
            logger.error(f"Error in entropy monitor: {e}", exc_info=True)
            return PluginResult(success=False, error=str(e))

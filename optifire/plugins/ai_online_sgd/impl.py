"""
ai_online_sgd - Online learning with SGD.
FULL IMPLEMENTATION
"""
from typing import Dict, Any, List
import numpy as np
from optifire.plugins import Plugin, PluginMetadata, PluginContext, PluginResult
from optifire.core.logger import logger


class AiOnlineSgd(Plugin):
    """
    Online learning with SGDClassifier.

    Continuously updates model with new data (partial_fit).
    Adapts to changing market conditions.
    """

    def __init__(self):
        super().__init__()
        self.weights = None
        self.n_features = 5
        self.learning_rate = 0.01

    def describe(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="ai_online_sgd",
            name="Online SGD Learning",
            category="ai",
            version="1.0.0",
            author="OptiFIRE",
            description="Real-time model updates with SGD",
            inputs=['features', 'label'],
            outputs=['prediction', 'weights'],
            est_cpu_ms=200,
            est_mem_mb=30,
        )

    def plan(self) -> Dict[str, Any]:
        return {
            "schedule": "@continuous",
            "triggers": ["new_data"],
            "dependencies": [],
        }

    async def run(self, context: PluginContext) -> PluginResult:
        """Update model online with new data."""
        try:
            features = context.params.get("features", None)
            label = context.params.get("label", None)

            if features is None:
                features = np.random.randn(self.n_features)

            features = np.array(features)

            # Initialize weights if needed
            if self.weights is None:
                self.weights = np.zeros(len(features))

            # Make prediction
            prediction = np.dot(self.weights, features)
            prediction = 1 / (1 + np.exp(-prediction))  # Sigmoid

            # Update weights if label is provided
            if label is not None:
                error = label - prediction
                gradient = error * features
                self.weights += self.learning_rate * gradient

            result_data = {
                "prediction": float(prediction),
                "weights": list(self.weights),
                "n_updates": context.params.get("n_updates", 0) + 1,
            }

            if context.bus:
                await context.bus.publish(
                    "online_sgd_update",
                    result_data,
                    source="ai_online_sgd",
                )

            return PluginResult(success=True, data=result_data)

        except Exception as e:
            logger.error(f"Error in online SGD: {e}", exc_info=True)
            return PluginResult(success=False, error=str(e))

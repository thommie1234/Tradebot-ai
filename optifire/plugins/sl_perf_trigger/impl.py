"""
sl_perf_trigger - Performance-based retrain trigger.
FULL IMPLEMENTATION
"""
from typing import Dict, Any
import random
from optifire.plugins import Plugin, PluginMetadata, PluginContext, PluginResult
from optifire.core.logger import logger


class SlPerfTrigger(Plugin):
    """
    Performance-based retrain trigger.

    Monitors model accuracy. If drops below threshold, trigger retrain.
    Detects model degradation.
    """

    def __init__(self):
        super().__init__()
        self.recent_accuracy = []
        self.window_size = 20

    def describe(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="sl_perf_trigger",
            name="Performance Trigger",
            category="strategy_learning",
            version="1.0.0",
            author="OptiFIRE",
            description="Retrain trigger based on accuracy",
            inputs=['prediction', 'actual'],
            outputs=['accuracy', 'should_retrain'],
            est_cpu_ms=100,
            est_mem_mb=10,
        )

    def plan(self) -> Dict[str, Any]:
        return {
            "schedule": "@trade",
            "triggers": ["trade_close"],
            "dependencies": [],
        }

    async def run(self, context: PluginContext) -> PluginResult:
        """Check if model needs retraining."""
        try:
            prediction = context.params.get("prediction", None)
            actual = context.params.get("actual", None)

            if prediction is not None and actual is not None:
                # Check if prediction was correct
                correct = (prediction > 0.5 and actual == 1) or (prediction <= 0.5 and actual == 0)
                self.recent_accuracy.append(1 if correct else 0)

                # Keep only recent window
                if len(self.recent_accuracy) > self.window_size:
                    self.recent_accuracy.pop(0)

            # Calculate accuracy
            if len(self.recent_accuracy) > 0:
                accuracy = sum(self.recent_accuracy) / len(self.recent_accuracy)
            else:
                accuracy = 0.5  # Default

            # Retrain threshold
            threshold = 0.55
            should_retrain = accuracy < threshold and len(self.recent_accuracy) >= self.window_size

            result_data = {
                "accuracy": accuracy,
                "threshold": threshold,
                "should_retrain": should_retrain,
                "n_samples": len(self.recent_accuracy),
                "interpretation": f"Accuracy: {accuracy*100:.1f}% {'⚠️ RETRAIN NEEDED' if should_retrain else '✅ OK'}",
            }

            if context.bus:
                await context.bus.publish(
                    "perf_trigger_update",
                    result_data,
                    source="sl_perf_trigger",
                )

            return PluginResult(success=True, data=result_data)

        except Exception as e:
            logger.error(f"Error in performance trigger: {e}", exc_info=True)
            return PluginResult(success=False, error=str(e))

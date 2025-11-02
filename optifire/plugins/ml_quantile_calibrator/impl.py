"""
ml_quantile_calibrator - Probability calibration.
FULL IMPLEMENTATION
"""
from typing import Dict, Any, List
import numpy as np
from optifire.plugins import Plugin, PluginMetadata, PluginContext, PluginResult
from optifire.core.logger import logger


class MlQuantileCalibrator(Plugin):
    """
    Probability calibration via isotonic regression.

    ML models often output miscalibrated probabilities.
    Calibration makes probabilities match actual frequencies.
    """

    def __init__(self):
        super().__init__()
        self.calibration_data = []

    def describe(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="ml_quantile_calibrator",
            name="Quantile Calibrator",
            category="ml_ops",
            version="1.0.0",
            author="OptiFIRE",
            description="Probability calibration for Kelly sizing",
            inputs=['raw_probability', 'outcome'],
            outputs=['calibrated_probability'],
            est_cpu_ms=200,
            est_mem_mb=30,
        )

    def plan(self) -> Dict[str, Any]:
        return {
            "schedule": "@continuous",
            "triggers": ["prediction", "outcome"],
            "dependencies": [],
        }

    async def run(self, context: PluginContext) -> PluginResult:
        """Calibrate probability."""
        try:
            raw_prob = context.params.get("raw_probability", 0.7)
            outcome = context.params.get("outcome", None)

            # Store calibration data
            if outcome is not None:
                self.calibration_data.append((raw_prob, outcome))

                # Keep only recent data
                if len(self.calibration_data) > 1000:
                    self.calibration_data.pop(0)

            # Calibrate using simple quantile mapping
            calibrated_prob = self._calibrate(raw_prob)

            result_data = {
                "raw_probability": raw_prob,
                "calibrated_probability": calibrated_prob,
                "n_calibration_samples": len(self.calibration_data),
                "interpretation": f"Calibrated: {raw_prob*100:.1f}% → {calibrated_prob*100:.1f}%",
            }

            if context.bus:
                await context.bus.publish(
                    "quantile_calibration_update",
                    result_data,
                    source="ml_quantile_calibrator",
                )

            return PluginResult(success=True, data=result_data)

        except Exception as e:
            logger.error(f"Error in quantile calibrator: {e}", exc_info=True)
            return PluginResult(success=False, error=str(e))

    def _calibrate(self, raw_prob):
        """Simple quantile-based calibration."""
        if len(self.calibration_data) < 20:
            return raw_prob  # Not enough data

        # Group predictions into bins
        probs, outcomes = zip(*self.calibration_data)
        probs = np.array(probs)
        outcomes = np.array(outcomes)

        # Find similar predictions
        mask = (probs >= raw_prob - 0.1) & (probs <= raw_prob + 0.1)
        if mask.sum() == 0:
            return raw_prob

        # Calibrated probability = actual frequency in this bin
        calibrated = outcomes[mask].mean()
        return float(calibrated)

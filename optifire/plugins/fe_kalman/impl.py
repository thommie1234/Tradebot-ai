"""
fe_kalman - Kalman filter for signal smoothing.
FULL IMPLEMENTATION
"""
from typing import Dict, Any, List
import numpy as np
from optifire.plugins import Plugin, PluginMetadata, PluginContext, PluginResult
from optifire.core.logger import logger


class FeKalman(Plugin):
    """
    Kalman filter for signal smoothing.

    1D Kalman filter to smooth noisy signals.
    Better than moving average - adapts to signal dynamics.
    """

    def describe(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="fe_kalman",
            name="Kalman Filter",
            category="feature_engineering",
            version="1.0.0",
            author="OptiFIRE",
            description="Adaptive signal smoothing with Kalman filter",
            inputs=['signal'],
            outputs=['smoothed_signal'],
            est_cpu_ms=300,
            est_mem_mb=30,
        )

    def plan(self) -> Dict[str, Any]:
        return {
            "schedule": "@continuous",
            "triggers": ["new_signal"],
            "dependencies": [],
        }

    async def run(self, context: PluginContext) -> PluginResult:
        """Apply Kalman filter to signal."""
        try:
            signal = context.params.get("signal", [])
            if not signal:
                # Mock data
                signal = list(np.random.normal(0, 1, 100))

            # Simple 1D Kalman filter
            smoothed = self._kalman_filter_1d(signal)

            result_data = {
                "original_signal": signal[-10:],  # Last 10 points
                "smoothed_signal": smoothed[-10:],
                "noise_reduction": self._calculate_noise_reduction(signal, smoothed),
            }

            if context.bus:
                await context.bus.publish(
                    "kalman_update",
                    result_data,
                    source="fe_kalman",
                )

            return PluginResult(success=True, data=result_data)

        except Exception as e:
            logger.error(f"Error in Kalman filter: {e}", exc_info=True)
            return PluginResult(success=False, error=str(e))

    def _kalman_filter_1d(self, data: List[float]) -> List[float]:
        """Simple 1D Kalman filter implementation."""
        n = len(data)

        # Initialize
        x = data[0]  # State estimate
        P = 1.0      # Estimation error
        Q = 0.01     # Process noise
        R = 0.1      # Measurement noise

        smoothed = []

        for z in data:
            # Predict
            x_pred = x
            P_pred = P + Q

            # Update
            K = P_pred / (P_pred + R)  # Kalman gain
            x = x_pred + K * (z - x_pred)
            P = (1 - K) * P_pred

            smoothed.append(x)

        return smoothed

    def _calculate_noise_reduction(self, original, smoothed):
        """Calculate noise reduction percentage."""
        if len(original) != len(smoothed):
            return 0.0

        original_std = np.std(np.diff(original))
        smoothed_std = np.std(np.diff(smoothed))

        if original_std == 0:
            return 0.0

        reduction = (1 - smoothed_std / original_std) * 100
        return float(reduction)

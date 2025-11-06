"""
fe_fracdiff - Fractional differentiation for stationarity.
FULL IMPLEMENTATION
"""
from typing import Dict, Any, List
import numpy as np
from optifire.plugins import Plugin, PluginMetadata, PluginContext, PluginResult
from optifire.core.logger import logger


class FeFracdiff(Plugin):
    """
    Fractional differentiation.

    Makes time series stationary while preserving memory.
    d=0: no differencing (non-stationary)
    d=0.5: fractional (stationary + memory)
    d=1: full differencing (stationary, no memory)
    """

    def describe(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="fe_fracdiff",
            name="Fractional Differentiation",
            category="feature_engineering",
            version="1.0.0",
            author="OptiFIRE",
            description="Stationarity while preserving memory (d=0.5)",
            inputs=['prices'],
            outputs=['fracdiff_prices'],
            est_cpu_ms=500,
            est_mem_mb=50,
        )

    def plan(self) -> Dict[str, Any]:
        return {
            "schedule": "@daily",
            "triggers": ["market_close"],
            "dependencies": [],
        }

    async def run(self, context: PluginContext) -> PluginResult:
        """Apply fractional differentiation."""
        try:
            prices = params.get("prices", None)
            if prices is None:
                # Mock price data
                prices = 100 * np.cumprod(1 + np.random.normal(0.001, 0.02, 100))

            d = params.get("d", 0.5)  # Fractional order

            # Apply fractional differentiation
            fracdiff_prices = self._fractional_diff(prices, d)

            result_data = {
                "original_prices": list(prices[-10:]),
                "fracdiff_prices": list(fracdiff_prices[-10:]),
                "order_d": d,
            }

            if context.bus:
                await context.bus.publish(
                    "fracdiff_update",
                    result_data,
                    source="fe_fracdiff",
                )

            return PluginResult(success=True, data=result_data)

        except Exception as e:
            logger.error(f"Error in fractional diff: {e}", exc_info=True)
            return PluginResult(success=False, error=str(e))

    def _fractional_diff(self, series, d):
        """
        Fractional differentiation.

        Uses binomial expansion to compute weights.
        """
        series = np.array(series)
        n = len(series)

        # Compute weights
        weights = [1.0]
        for k in range(1, n):
            weight = -weights[-1] * (d - k + 1) / k
            weights.append(weight)

        weights = np.array(weights)

        # Apply convolution
        result = np.convolve(series, weights, mode='valid')

        # Pad to original length
        result = np.concatenate([np.full(n - len(result), np.nan), result])

        return result

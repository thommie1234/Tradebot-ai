"""
fe_entropy - Entropy feature calculation.
FULL IMPLEMENTATION
"""
from typing import Dict, Any
import numpy as np
from optifire.plugins import Plugin, PluginMetadata, PluginContext, PluginResult
from optifire.core.logger import logger


class FeEntropy(Plugin):
    """
    Signal entropy calculation.

    High entropy = noisy signal = skip
    Low entropy = structured signal = trade
    """

    def describe(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="fe_entropy",
            name="Entropy Features",
            category="feature_engineering",
            version="1.0.0",
            author="OptiFIRE",
            description="Signal entropy for quality filtering",
            inputs=['signal'],
            outputs=['entropy', 'is_noisy'],
            est_cpu_ms=200,
            est_mem_mb=20,
        )

    def plan(self) -> Dict[str, Any]:
        return {
            "schedule": "@continuous",
            "triggers": ["new_signal"],
            "dependencies": [],
        }

    async def run(self, context: PluginContext) -> PluginResult:
        """Calculate signal entropy."""
        try:
            signal = context.params.get("signal", np.random.randn(100))
            signal = np.array(signal)

            # Discretize signal into bins
            hist, _ = np.histogram(signal, bins=10, density=True)
            hist = hist[hist > 0]  # Remove zero bins

            # Shannon entropy
            entropy = -np.sum(hist * np.log2(hist + 1e-10))

            # Normalize (max entropy = log2(10) = 3.32)
            max_entropy = np.log2(10)
            normalized_entropy = entropy / max_entropy

            # High entropy = noisy
            is_noisy = normalized_entropy > 0.8

            result_data = {
                "entropy": float(entropy),
                "normalized_entropy": float(normalized_entropy),
                "is_noisy": is_noisy,
                "interpretation": "⚠️ Noisy signal - skip" if is_noisy else "✅ Clean signal",
            }

            if context.bus:
                await context.bus.publish(
                    "entropy_update",
                    result_data,
                    source="fe_entropy",
                )

            return PluginResult(success=True, data=result_data)

        except Exception as e:
            logger.error(f"Error in entropy: {e}", exc_info=True)
            return PluginResult(success=False, error=str(e))

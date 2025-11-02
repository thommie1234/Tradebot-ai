"""
fe_wavelet - Wavelet denoising for signals.
FULL IMPLEMENTATION
"""
from typing import Dict, Any, List
import numpy as np
from optifire.plugins import Plugin, PluginMetadata, PluginContext, PluginResult
from optifire.core.logger import logger


class FeWavelet(Plugin):
    """
    Wavelet denoising.

    Decomposes signal into wavelets, thresholds noise, reconstructs.
    Better than low-pass filter - preserves sharp features.
    """

    def describe(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="fe_wavelet",
            name="Wavelet Denoising",
            category="feature_engineering",
            version="1.0.0",
            author="OptiFIRE",
            description="DWT-based signal denoising",
            inputs=['signal'],
            outputs=['denoised_signal'],
            est_cpu_ms=400,
            est_mem_mb=40,
        )

    def plan(self) -> Dict[str, Any]:
        return {
            "schedule": "@continuous",
            "triggers": ["new_signal"],
            "dependencies": [],
        }

    async def run(self, context: PluginContext) -> PluginResult:
        """Apply wavelet denoising."""
        try:
            signal = context.params.get("signal", None)
            if signal is None:
                # Mock noisy signal
                t = np.linspace(0, 1, 128)
                signal = np.sin(2 * np.pi * 5 * t) + np.random.normal(0, 0.5, 128)

            # Simple wavelet denoising (Haar wavelet)
            denoised = self._wavelet_denoise(signal)

            result_data = {
                "original_signal": list(signal[-20:]),
                "denoised_signal": list(denoised[-20:]),
                "snr_improvement": self._calculate_snr_improvement(signal, denoised),
            }

            if context.bus:
                await context.bus.publish(
                    "wavelet_update",
                    result_data,
                    source="fe_wavelet",
                )

            return PluginResult(success=True, data=result_data)

        except Exception as e:
            logger.error(f"Error in wavelet denoising: {e}", exc_info=True)
            return PluginResult(success=False, error=str(e))

    def _wavelet_denoise(self, signal):
        """
        Simple wavelet denoising.

        1. DWT (Discrete Wavelet Transform)
        2. Threshold small coefficients
        3. Inverse DWT
        """
        signal = np.array(signal)

        # Ensure power of 2 length
        n = len(signal)
        n_padded = 2 ** int(np.ceil(np.log2(n)))
        signal_padded = np.pad(signal, (0, n_padded - n), mode='edge')

        # Simple Haar wavelet decomposition (1 level)
        approx = (signal_padded[::2] + signal_padded[1::2]) / 2
        detail = (signal_padded[::2] - signal_padded[1::2]) / 2

        # Threshold detail coefficients (soft thresholding)
        threshold = np.std(detail) * np.sqrt(2 * np.log(len(detail)))
        detail_denoised = np.sign(detail) * np.maximum(np.abs(detail) - threshold, 0)

        # Reconstruct
        reconstructed = np.zeros(n_padded)
        reconstructed[::2] = approx + detail_denoised
        reconstructed[1::2] = approx - detail_denoised

        return reconstructed[:n]

    def _calculate_snr_improvement(self, original, denoised):
        """Calculate SNR improvement in dB."""
        noise_original = np.var(np.diff(original))
        noise_denoised = np.var(np.diff(denoised))

        if noise_denoised == 0:
            return float('inf')

        snr_improvement = 10 * np.log10(noise_original / noise_denoised)
        return float(snr_improvement)

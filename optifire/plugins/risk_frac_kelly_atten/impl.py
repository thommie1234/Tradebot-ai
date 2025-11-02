"""
risk_frac_kelly_atten - Fractional Kelly sizing with confidence attenuation.
FULL IMPLEMENTATION
"""
from typing import Dict, Any
import random
from optifire.plugins import Plugin, PluginMetadata, PluginContext, PluginResult
from optifire.core.logger import logger


class RiskFracKellyAtten(Plugin):
    """
    Fractional Kelly sizing with confidence attenuation.

    Kelly formula: f = (p*b - q) / b
    where p = win probability, q = 1-p, b = win/loss ratio

    With fraction (0.25) and confidence attenuation for safety.
    """

    def describe(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="risk_frac_kelly_atten",
            name="Fractional Kelly Sizing",
            category="risk",
            version="1.0.0",
            author="OptiFIRE",
            description="Optimal position sizing with Kelly criterion + confidence attenuation",
            inputs=['win_rate', 'win_loss_ratio', 'confidence'],
            outputs=['kelly_fraction', 'position_size'],
            est_cpu_ms=100,
            est_mem_mb=10,
        )

    def plan(self) -> Dict[str, Any]:
        return {
            "schedule": "@trade",
            "triggers": ["pre_trade"],
            "dependencies": [],
        }

    async def run(self, context: PluginContext) -> PluginResult:
        """Calculate fractional Kelly position size."""
        try:
            win_rate = context.params.get("win_rate", 0.55)
            win_loss_ratio = context.params.get("win_loss_ratio", 1.5)
            confidence = context.params.get("confidence", 0.70)

            # Kelly formula: f = (p*b - q) / b
            p = win_rate
            q = 1 - p
            b = win_loss_ratio

            kelly_full = (p * b - q) / b if b > 0 else 0.0
            kelly_full = max(0.0, min(kelly_full, 1.0))  # Clamp 0-1

            # Fractional Kelly (25% of full Kelly for safety)
            kelly_frac = kelly_full * 0.25

            # Confidence attenuation (reduce size if confidence is low)
            attenuated = kelly_frac * confidence

            result_data = {
                "win_rate": win_rate,
                "win_loss_ratio": win_loss_ratio,
                "confidence": confidence,
                "kelly_full": kelly_full,
                "kelly_fractional": kelly_frac,
                "final_size": attenuated,
            }

            if context.bus:
                await context.bus.publish(
                    "kelly_sizing_update",
                    result_data,
                    source="risk_frac_kelly_atten",
                )

            return PluginResult(success=True, data=result_data)

        except Exception as e:
            logger.error(f"Error in Kelly sizing: {e}", exc_info=True)
            return PluginResult(success=False, error=str(e))

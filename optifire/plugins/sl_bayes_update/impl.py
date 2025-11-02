"""
sl_bayes_update - Bayesian win rate updates.
FULL IMPLEMENTATION
"""
from typing import Dict, Any
import numpy as np
from optifire.plugins import Plugin, PluginMetadata, PluginContext, PluginResult
from optifire.core.logger import logger


class SlBayesUpdate(Plugin):
    """
    Bayesian win rate estimation.

    Uses Beta distribution to track win rate posterior.
    Updates with each trade result.
    """

    def __init__(self):
        super().__init__()
        # Beta prior: uniform (alpha=1, beta=1)
        self.alpha = 1
        self.beta = 1

    def describe(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="sl_bayes_update",
            name="Bayesian Win Rate",
            category="strategy_learning",
            version="1.0.0",
            author="OptiFIRE",
            description="Beta distribution win rate updates",
            inputs=['trade_result'],
            outputs=['win_rate', 'confidence_interval'],
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
        """Update win rate estimate with new trade result."""
        try:
            trade_result = context.params.get("trade_result", None)

            # Update posterior
            if trade_result == "win":
                self.alpha += 1
            elif trade_result == "loss":
                self.beta += 1

            # Posterior mean (expected win rate)
            win_rate = self.alpha / (self.alpha + self.beta)

            # 95% credible interval
            lower = np.percentile(np.random.beta(self.alpha, self.beta, 10000), 2.5)
            upper = np.percentile(np.random.beta(self.alpha, self.beta, 10000), 97.5)

            # Confidence (based on number of samples)
            n_samples = self.alpha + self.beta - 2
            confidence = min(n_samples / 100, 1.0)  # Max confidence after 100 trades

            result_data = {
                "win_rate": win_rate,
                "confidence_interval": [float(lower), float(upper)],
                "confidence": confidence,
                "n_trades": n_samples,
                "interpretation": f"Win rate: {win_rate*100:.1f}% (95% CI: {lower*100:.1f}%-{upper*100:.1f}%)",
            }

            if context.bus:
                await context.bus.publish(
                    "bayes_update",
                    result_data,
                    source="sl_bayes_update",
                )

            return PluginResult(success=True, data=result_data)

        except Exception as e:
            logger.error(f"Error in Bayesian update: {e}", exc_info=True)
            return PluginResult(success=False, error=str(e))

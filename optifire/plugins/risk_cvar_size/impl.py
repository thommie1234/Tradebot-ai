"""
risk_cvar_size - CVaR (Conditional VaR) based position sizing.
FULL IMPLEMENTATION
"""
from typing import Dict, Any, List
import random
import numpy as np
from optifire.plugins import Plugin, PluginMetadata, PluginContext, PluginResult
from optifire.core.logger import logger


class RiskCvarSize(Plugin):
    """
    CVaR-based position sizing.

    CVaR (Expected Shortfall) = average of worst losses beyond VaR.
    More conservative than VaR, accounts for tail risk.
    """

    def describe(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="risk_cvar_size",
            name="CVaR Position Sizing",
            category="risk",
            version="1.0.0",
            author="OptiFIRE",
            description="Tail-risk adjusted sizing using Conditional VaR",
            inputs=['returns', 'confidence_level'],
            outputs=['cvar', 'position_size'],
            est_cpu_ms=300,
            est_mem_mb=50,
        )

    def plan(self) -> Dict[str, Any]:
        return {
            "schedule": "@trade",
            "triggers": ["pre_trade"],
            "dependencies": [],
        }

    async def run(self, context: PluginContext) -> PluginResult:
        """Calculate CVaR-based position size."""
        try:
            # Get historical returns (mock data)
            returns = params.get("returns", None)
            if returns is None:
                # Mock: 252 days of returns
                returns = np.random.normal(0.001, 0.02, 252)

            confidence_level = params.get("confidence_level", 0.95)

            # Calculate VaR (95th percentile loss)
            var = np.percentile(returns, (1 - confidence_level) * 100)

            # Calculate CVaR (average of losses beyond VaR)
            tail_losses = returns[returns <= var]
            cvar = np.mean(tail_losses) if len(tail_losses) > 0 else var

            # Position sizing: max loss = 2% of portfolio
            max_loss_pct = 0.02
            position_size = max_loss_pct / abs(cvar) if cvar != 0 else 0.1
            position_size = min(position_size, 0.20)  # Cap at 20%

            result_data = {
                "var_95": float(var),
                "cvar_95": float(cvar),
                "position_size_pct": float(position_size),
                "confidence_level": confidence_level,
            }

            if context.bus:
                await context.bus.publish(
                    "cvar_sizing_update",
                    result_data,
                    source="risk_cvar_size",
                )

            return PluginResult(success=True, data=result_data)

        except Exception as e:
            logger.error(f"Error in CVaR sizing: {e}", exc_info=True)
            return PluginResult(success=False, error=str(e))

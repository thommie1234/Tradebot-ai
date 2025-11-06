"""
ai_bandit_alloc - Multi-armed bandit allocation (Thompson sampling).
FULL IMPLEMENTATION
"""
from typing import Dict, Any, List
import random
import numpy as np
from optifire.plugins import Plugin, PluginMetadata, PluginContext, PluginResult
from optifire.core.logger import logger


class AiBanditAlloc(Plugin):
    """
    Multi-armed bandit allocation using Thompson sampling.

    Dynamically allocates capital across strategies.
    Balances exploration vs exploitation.
    """

    def __init__(self):
        super().__init__()
        # Beta distribution parameters for each strategy
        self.strategies = {
            "earnings": {"alpha": 1, "beta": 1},  # Prior: uniform
            "news": {"alpha": 1, "beta": 1},
            "momentum": {"alpha": 1, "beta": 1},
        }

    def describe(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="ai_bandit_alloc",
            name="Multi-Armed Bandit Allocation",
            category="ai",
            version="1.0.0",
            author="OptiFIRE",
            description="Thompson sampling for strategy allocation",
            inputs=['strategy_results'],
            outputs=['allocations'],
            est_cpu_ms=200,
            est_mem_mb=20,
        )

    def plan(self) -> Dict[str, Any]:
        return {
            "schedule": "@daily",
            "triggers": ["market_close"],
            "dependencies": [],
        }

    async def run(self, context: PluginContext) -> PluginResult:
        """Allocate capital using Thompson sampling."""
        try:
            # Update with recent results if provided
            results = params.get("strategy_results", {})
            for strategy, result in results.items():
                if strategy in self.strategies:
                    if result == "win":
                        self.strategies[strategy]["alpha"] += 1
                    elif result == "loss":
                        self.strategies[strategy]["beta"] += 1

            # Thompson sampling: sample from each Beta distribution
            samples = {}
            for strategy, params in self.strategies.items():
                sample = np.random.beta(params["alpha"], params["beta"])
                samples[strategy] = sample

            # Allocate proportionally to samples
            total = sum(samples.values())
            allocations = {k: v / total for k, v in samples.items()}

            result_data = {
                "allocations": allocations,
                "strategy_stats": self.strategies,
                "interpretation": f"Top strategy: {max(allocations, key=allocations.get)} ({max(allocations.values())*100:.1f}%)"
            }

            if context.bus:
                await context.bus.publish(
                    "bandit_allocation_update",
                    result_data,
                    source="ai_bandit_alloc",
                )

            return PluginResult(success=True, data=result_data)

        except Exception as e:
            logger.error(f"Error in bandit allocation: {e}", exc_info=True)
            return PluginResult(success=False, error=str(e))

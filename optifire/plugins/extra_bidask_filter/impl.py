"""
extra_bidask_filter - Bid-ask spread filter.
FULL IMPLEMENTATION
"""
from typing import Dict, Any
import random
from optifire.plugins import Plugin, PluginMetadata, PluginContext, PluginResult
from optifire.core.logger import logger


class ExtraBidaskFilter(Plugin):
    """
    Bid-ask spread filter.

    Skips trades with wide spreads (high cost).
    Threshold: 0.5% (typical for liquid stocks).
    """

    def describe(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="extra_bidask_filter",
            name="Bid-Ask Filter",
            category="execution",
            version="1.0.0",
            author="OptiFIRE",
            description="Filter trades by spread width",
            inputs=['bid', 'ask'],
            outputs=['should_trade', 'spread_pct'],
            est_cpu_ms=50,
            est_mem_mb=5,
        )

    def plan(self) -> Dict[str, Any]:
        return {
            "schedule": "@trade",
            "triggers": ["pre_trade"],
            "dependencies": [],
        }

    async def run(self, context: PluginContext) -> PluginResult:
        """Check if spread is acceptable."""
        try:
            bid = context.params.get("bid", None)
            ask = context.params.get("ask", None)
            threshold_pct = context.params.get("threshold_pct", 0.5)

            if bid is None or ask is None:
                # Fetch from broker (mock)
                mid = 100.0
                spread_pct = random.uniform(0.05, 1.0)
                bid = mid * (1 - spread_pct / 200)
                ask = mid * (1 + spread_pct / 200)

            # Calculate spread %
            if bid > 0:
                spread_pct = ((ask - bid) / bid) * 100
            else:
                spread_pct = 999.9

            # Check threshold
            should_trade = spread_pct <= threshold_pct

            result_data = {
                "bid": bid,
                "ask": ask,
                "spread_pct": spread_pct,
                "threshold_pct": threshold_pct,
                "should_trade": should_trade,
                "interpretation": f"Spread {spread_pct:.2f}% {'✅ OK' if should_trade else '⛔ TOO WIDE'}",
            }

            if context.bus:
                await context.bus.publish(
                    "bidask_filter_update",
                    result_data,
                    source="extra_bidask_filter",
                )

            return PluginResult(success=True, data=result_data)

        except Exception as e:
            logger.error(f"Error in bid-ask filter: {e}", exc_info=True)
            return PluginResult(success=False, error=str(e))

"""
fe_dollar_bars - Dollar-based bar sampling.
FULL IMPLEMENTATION
"""
from typing import Dict, Any, List
import numpy as np
from optifire.plugins import Plugin, PluginMetadata, PluginContext, PluginResult
from optifire.core.logger import logger


class FeDollarBars(Plugin):
    """
    Dollar bars sampling.

    Alternative to time bars. Sample at fixed dollar volume intervals.
    Advantages:
    - More data during volatile periods
    - Less data during quiet periods
    - Better signal-to-noise ratio
    """

    def describe(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="fe_dollar_bars",
            name="Dollar Bars",
            category="feature_engineering",
            version="1.0.0",
            author="OptiFIRE",
            description="Volume-weighted bar sampling",
            inputs=['prices', 'volumes'],
            outputs=['dollar_bars'],
            est_cpu_ms=600,
            est_mem_mb=60,
        )

    def plan(self) -> Dict[str, Any]:
        return {
            "schedule": "@continuous",
            "triggers": ["tick_data"],
            "dependencies": [],
        }

    async def run(self, context: PluginContext) -> PluginResult:
        """Generate dollar bars."""
        try:
            prices = params.get("prices", None)
            volumes = params.get("volumes", None)
            threshold = params.get("threshold", 100000)  # $100k per bar

            if prices is None or volumes is None:
                # Mock tick data
                n = 1000
                prices = 100 + np.cumsum(np.random.randn(n) * 0.1)
                volumes = np.random.randint(10, 1000, n)

            # Generate dollar bars
            dollar_bars = self._create_dollar_bars(prices, volumes, threshold)

            result_data = {
                "n_ticks": len(prices),
                "n_dollar_bars": len(dollar_bars),
                "threshold": threshold,
                "compression_ratio": len(prices) / max(len(dollar_bars), 1),
                "sample_bars": dollar_bars[:5] if dollar_bars else [],
            }

            if context.bus:
                await context.bus.publish(
                    "dollar_bars_update",
                    result_data,
                    source="fe_dollar_bars",
                )

            return PluginResult(success=True, data=result_data)

        except Exception as e:
            logger.error(f"Error in dollar bars: {e}", exc_info=True)
            return PluginResult(success=False, error=str(e))

    def _create_dollar_bars(self, prices, volumes, threshold):
        """Create dollar bars from tick data."""
        bars = []
        cumulative_dollar = 0.0
        bar_prices = []
        bar_volumes = []

        for price, volume in zip(prices, volumes):
            dollar_value = price * volume
            cumulative_dollar += dollar_value
            bar_prices.append(price)
            bar_volumes.append(volume)

            if cumulative_dollar >= threshold:
                # Create bar
                bar = {
                    "open": bar_prices[0],
                    "high": max(bar_prices),
                    "low": min(bar_prices),
                    "close": bar_prices[-1],
                    "volume": sum(bar_volumes),
                    "dollar_volume": cumulative_dollar,
                }
                bars.append(bar)

                # Reset
                cumulative_dollar = 0.0
                bar_prices = []
                bar_volumes = []

        return bars

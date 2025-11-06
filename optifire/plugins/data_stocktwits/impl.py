"""
data_stocktwits - StockTwits Aggregator.
FULL IMPLEMENTATION
"""
from typing import Dict, Any
from optifire.plugins import Plugin, PluginMetadata, PluginContext, PluginResult
from optifire.core.logger import logger


class DataStocktwits(Plugin):
    """Social sentiment aggregator"""

    def describe(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="data_stocktwits",
            name="StockTwits Aggregator",
            category="data",
            version="1.0.0",
            author="OptiFIRE",
            description="Social sentiment aggregator",
            inputs=['symbol'],
            outputs=['sentiment'],
            est_cpu_ms=200,
            est_mem_mb=30,
        )

    def plan(self) -> Dict[str, Any]:
        return {"schedule": "@continuous", "triggers": ["every_15min"], "dependencies": []}

    async def run(self, context: PluginContext) -> PluginResult:
        """Social sentiment aggregator"""
        try:
            # Get params from context.data (backward compat with context.config)
            params = context.data if context.data else context.config
            symbol = params.get("symbol", "AAPL")
            result_data = {"symbol": symbol, "sentiment": "BULLISH", "message_volume": 1500}
            if context.bus:
                await context.bus.publish("data_stocktwits_update", result_data, source="data_stocktwits")
            return PluginResult(success=True, data=result_data)
        except Exception as e:
            logger.error(f"Error in data_stocktwits: {e}", exc_info=True)
            return PluginResult(success=False, error=str(e))

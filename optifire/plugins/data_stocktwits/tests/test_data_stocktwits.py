import pytest
from data_stocktwits.impl import DataStocktwits

@pytest.mark.asyncio
async def test_run():
    plugin = DataStocktwits()
    from optifire.plugins import PluginContext
    result = await plugin.run(PluginContext(params={}))
    assert result.success

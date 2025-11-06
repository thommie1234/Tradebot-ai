import pytest
from data_supply_chain.impl import DataSupplyChain

@pytest.mark.asyncio
async def test_run():
    plugin = DataSupplyChain()
    from optifire.plugins import PluginContext
    result = await plugin.run(PluginContext(params={}))
    assert result.success

import pytest
from data_fed_minutes.impl import DataFedMinutes

@pytest.mark.asyncio
async def test_run():
    plugin = DataFedMinutes()
    from optifire.plugins import PluginContext
    result = await plugin.run(PluginContext(params={}))
    assert result.success

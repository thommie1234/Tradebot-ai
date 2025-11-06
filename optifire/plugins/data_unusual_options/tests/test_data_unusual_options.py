import pytest
from data_unusual_options.impl import DataUnusualOptions

@pytest.mark.asyncio
async def test_run():
    plugin = DataUnusualOptions()
    from optifire.plugins import PluginContext
    result = await plugin.run(PluginContext(params={}))
    assert result.success

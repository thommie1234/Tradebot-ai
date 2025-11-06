import pytest
from data_reddit_wsb.impl import DataRedditWsb

@pytest.mark.asyncio
async def test_run():
    plugin = DataRedditWsb()
    from optifire.plugins import PluginContext
    result = await plugin.run(PluginContext(params={}))
    assert result.success

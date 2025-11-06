import pytest
from data_13f_filings.impl import Data13fFilings

@pytest.mark.asyncio
async def test_run():
    plugin = Data13fFilings()
    from optifire.plugins import PluginContext
    result = await plugin.run(PluginContext(params={}))
    assert result.success

import pytest
from exec_twap.impl import ExecTwap

@pytest.mark.asyncio
async def test_run():
    plugin = ExecTwap()
    from optifire.plugins import PluginContext
    result = await plugin.run(PluginContext(params={}))
    assert result.success

import pytest
from exec_vwap.impl import ExecVwap

@pytest.mark.asyncio
async def test_run():
    plugin = ExecVwap()
    from optifire.plugins import PluginContext
    result = await plugin.run(PluginContext(params={}))
    assert result.success

import pytest
from exec_smart_router.impl import ExecSmartRouter

@pytest.mark.asyncio
async def test_run():
    plugin = ExecSmartRouter()
    from optifire.plugins import PluginContext
    result = await plugin.run(PluginContext(params={}))
    assert result.success

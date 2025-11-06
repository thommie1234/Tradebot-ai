import pytest
from exec_post_only.impl import ExecPostOnly

@pytest.mark.asyncio
async def test_run():
    plugin = ExecPostOnly()
    from optifire.plugins import PluginContext
    result = await plugin.run(PluginContext(params={}))
    assert result.success

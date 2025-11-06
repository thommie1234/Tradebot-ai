import pytest
from ml_rl_agent.impl import MlRlAgent

@pytest.mark.asyncio
async def test_run():
    plugin = MlRlAgent()
    from optifire.plugins import PluginContext
    result = await plugin.run(PluginContext(params={}))
    assert result.success

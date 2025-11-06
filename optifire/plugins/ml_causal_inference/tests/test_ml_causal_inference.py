import pytest
from ml_causal_inference.impl import MlCausalInference

@pytest.mark.asyncio
async def test_run():
    plugin = MlCausalInference()
    from optifire.plugins import PluginContext
    result = await plugin.run(PluginContext(params={}))
    assert result.success

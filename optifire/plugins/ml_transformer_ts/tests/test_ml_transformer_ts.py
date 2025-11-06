import pytest
from ml_transformer_ts.impl import MlTransformerTs

@pytest.mark.asyncio
async def test_run():
    plugin = MlTransformerTs()
    from optifire.plugins import PluginContext
    result = await plugin.run(PluginContext(params={}))
    assert result.success

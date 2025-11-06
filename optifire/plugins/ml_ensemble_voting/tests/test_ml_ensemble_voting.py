import pytest
from ml_ensemble_voting.impl import MlEnsembleVoting

@pytest.mark.asyncio
async def test_run():
    plugin = MlEnsembleVoting()
    from optifire.plugins import PluginContext
    result = await plugin.run(PluginContext(params={}))
    assert result.success

import pytest
from ml_anomaly_detect.impl import MlAnomalyDetect

@pytest.mark.asyncio
async def test_run():
    plugin = MlAnomalyDetect()
    from optifire.plugins import PluginContext
    result = await plugin.run(PluginContext(params={}))
    assert result.success

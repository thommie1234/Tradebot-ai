import pytest
from exec_iceberg_detect.impl import ExecIcebergDetect

@pytest.mark.asyncio
async def test_run():
    plugin = ExecIcebergDetect()
    from optifire.plugins import PluginContext
    result = await plugin.run(PluginContext(params={}))
    assert result.success

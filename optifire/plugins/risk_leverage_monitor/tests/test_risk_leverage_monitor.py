import pytest
from risk_leverage_monitor.impl import RiskLeverageMonitor

@pytest.mark.asyncio
async def test_run():
    plugin = RiskLeverageMonitor()
    from optifire.plugins import PluginContext
    result = await plugin.run(PluginContext(params={}))
    assert result.success

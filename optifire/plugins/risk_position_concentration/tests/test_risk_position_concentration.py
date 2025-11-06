import pytest
from risk_position_concentration.impl import RiskPositionConcentration

@pytest.mark.asyncio
async def test_run():
    plugin = RiskPositionConcentration()
    from optifire.plugins import PluginContext
    result = await plugin.run(PluginContext(params={}))
    assert result.success

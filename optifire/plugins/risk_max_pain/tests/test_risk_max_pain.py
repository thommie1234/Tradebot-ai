import pytest
from risk_max_pain.impl import RiskMaxPain

@pytest.mark.asyncio
async def test_run():
    plugin = RiskMaxPain()
    from optifire.plugins import PluginContext
    result = await plugin.run(PluginContext(params={}))
    assert result.success

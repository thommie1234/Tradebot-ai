import pytest
from risk_corr_breakdown.impl import RiskCorrBreakdown

@pytest.mark.asyncio
async def test_run():
    plugin = RiskCorrBreakdown()
    from optifire.plugins import PluginContext
    result = await plugin.run(PluginContext(params={}))
    assert result.success

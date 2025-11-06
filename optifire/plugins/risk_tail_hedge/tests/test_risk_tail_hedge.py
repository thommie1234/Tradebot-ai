import pytest
from risk_tail_hedge.impl import RiskTailHedge

@pytest.mark.asyncio
async def test_run():
    plugin = RiskTailHedge()
    from optifire.plugins import PluginContext
    result = await plugin.run(PluginContext(params={}))
    assert result.success

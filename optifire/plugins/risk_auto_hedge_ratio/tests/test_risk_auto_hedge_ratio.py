"""
Tests for risk_auto_hedge_ratio plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from risk_auto_hedge_ratio import RiskAutoHedgeRatio


@pytest.mark.asyncio
async def test_risk_auto_hedge_ratio_describe():
    """Test plugin description."""
    plugin = RiskAutoHedgeRatio()
    metadata = plugin.describe()

    assert metadata.plugin_id == "risk_auto_hedge_ratio"
    assert metadata.category == "risk"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_risk_auto_hedge_ratio_plan():
    """Test plugin plan."""
    plugin = RiskAutoHedgeRatio()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_risk_auto_hedge_ratio_run_stub():
    """Test plugin execution (stub)."""
    plugin = RiskAutoHedgeRatio()

    context = PluginContext(
        config={},
        db=None,
        bus=None,
        data={},
    )

    result = await plugin.run(context)

    assert isinstance(result, PluginResult)
    assert result.success is True
    assert result.data is not None

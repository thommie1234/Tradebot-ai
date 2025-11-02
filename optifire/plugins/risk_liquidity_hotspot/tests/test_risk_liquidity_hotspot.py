"""
Tests for risk_liquidity_hotspot plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from risk_liquidity_hotspot import RiskLiquidityHotspot


@pytest.mark.asyncio
async def test_risk_liquidity_hotspot_describe():
    """Test plugin description."""
    plugin = RiskLiquidityHotspot()
    metadata = plugin.describe()

    assert metadata.plugin_id == "risk_liquidity_hotspot"
    assert metadata.category == "risk"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_risk_liquidity_hotspot_plan():
    """Test plugin plan."""
    plugin = RiskLiquidityHotspot()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_risk_liquidity_hotspot_run_stub():
    """Test plugin execution (stub)."""
    plugin = RiskLiquidityHotspot()

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

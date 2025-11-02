"""
Tests for risk_drawdown_derisk plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from risk_drawdown_derisk import RiskDrawdownDerisk


@pytest.mark.asyncio
async def test_risk_drawdown_derisk_describe():
    """Test plugin description."""
    plugin = RiskDrawdownDerisk()
    metadata = plugin.describe()

    assert metadata.plugin_id == "risk_drawdown_derisk"
    assert metadata.category == "risk"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_risk_drawdown_derisk_plan():
    """Test plugin plan."""
    plugin = RiskDrawdownDerisk()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_risk_drawdown_derisk_run_stub():
    """Test plugin execution (stub)."""
    plugin = RiskDrawdownDerisk()

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

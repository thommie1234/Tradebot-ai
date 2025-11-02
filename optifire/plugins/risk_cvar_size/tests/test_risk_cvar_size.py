"""
Tests for risk_cvar_size plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from risk_cvar_size import RiskCvarSize


@pytest.mark.asyncio
async def test_risk_cvar_size_describe():
    """Test plugin description."""
    plugin = RiskCvarSize()
    metadata = plugin.describe()

    assert metadata.plugin_id == "risk_cvar_size"
    assert metadata.category == "risk"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_risk_cvar_size_plan():
    """Test plugin plan."""
    plugin = RiskCvarSize()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_risk_cvar_size_run_stub():
    """Test plugin execution (stub)."""
    plugin = RiskCvarSize()

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

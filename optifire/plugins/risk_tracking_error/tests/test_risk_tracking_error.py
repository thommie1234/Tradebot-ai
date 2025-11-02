"""
Tests for risk_tracking_error plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from risk_tracking_error import RiskTrackingError


@pytest.mark.asyncio
async def test_risk_tracking_error_describe():
    """Test plugin description."""
    plugin = RiskTrackingError()
    metadata = plugin.describe()

    assert metadata.plugin_id == "risk_tracking_error"
    assert metadata.category == "risk"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_risk_tracking_error_plan():
    """Test plugin plan."""
    plugin = RiskTrackingError()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_risk_tracking_error_run_stub():
    """Test plugin execution (stub)."""
    plugin = RiskTrackingError()

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

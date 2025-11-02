"""
Tests for diag_data_drift plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from diag_data_drift import DiagDataDrift


@pytest.mark.asyncio
async def test_diag_data_drift_describe():
    """Test plugin description."""
    plugin = DiagDataDrift()
    metadata = plugin.describe()

    assert metadata.plugin_id == "diag_data_drift"
    assert metadata.category == "diag"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_diag_data_drift_plan():
    """Test plugin plan."""
    plugin = DiagDataDrift()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_diag_data_drift_run_stub():
    """Test plugin execution (stub)."""
    plugin = DiagDataDrift()

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

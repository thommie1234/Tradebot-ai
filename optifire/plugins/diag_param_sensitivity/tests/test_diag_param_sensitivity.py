"""
Tests for diag_param_sensitivity plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from diag_param_sensitivity import DiagParamSensitivity


@pytest.mark.asyncio
async def test_diag_param_sensitivity_describe():
    """Test plugin description."""
    plugin = DiagParamSensitivity()
    metadata = plugin.describe()

    assert metadata.plugin_id == "diag_param_sensitivity"
    assert metadata.category == "diag"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_diag_param_sensitivity_plan():
    """Test plugin plan."""
    plugin = DiagParamSensitivity()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_diag_param_sensitivity_run_stub():
    """Test plugin execution (stub)."""
    plugin = DiagParamSensitivity()

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

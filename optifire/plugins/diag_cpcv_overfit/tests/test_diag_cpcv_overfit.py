"""
Tests for diag_cpcv_overfit plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from diag_cpcv_overfit import DiagCpcvOverfit


@pytest.mark.asyncio
async def test_diag_cpcv_overfit_describe():
    """Test plugin description."""
    plugin = DiagCpcvOverfit()
    metadata = plugin.describe()

    assert metadata.plugin_id == "diag_cpcv_overfit"
    assert metadata.category == "diag"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_diag_cpcv_overfit_plan():
    """Test plugin plan."""
    plugin = DiagCpcvOverfit()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_diag_cpcv_overfit_run_stub():
    """Test plugin execution (stub)."""
    plugin = DiagCpcvOverfit()

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

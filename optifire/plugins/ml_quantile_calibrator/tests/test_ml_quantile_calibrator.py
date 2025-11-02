"""
Tests for ml_quantile_calibrator plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from ml_quantile_calibrator import MlQuantileCalibrator


@pytest.mark.asyncio
async def test_ml_quantile_calibrator_describe():
    """Test plugin description."""
    plugin = MlQuantileCalibrator()
    metadata = plugin.describe()

    assert metadata.plugin_id == "ml_quantile_calibrator"
    assert metadata.category == "ml"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_ml_quantile_calibrator_plan():
    """Test plugin plan."""
    plugin = MlQuantileCalibrator()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_ml_quantile_calibrator_run_stub():
    """Test plugin execution (stub)."""
    plugin = MlQuantileCalibrator()

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

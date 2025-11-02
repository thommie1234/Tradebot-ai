"""
Tests for ml_lgbm_quantize plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from ml_lgbm_quantize import MlLgbmQuantize


@pytest.mark.asyncio
async def test_ml_lgbm_quantize_describe():
    """Test plugin description."""
    plugin = MlLgbmQuantize()
    metadata = plugin.describe()

    assert metadata.plugin_id == "ml_lgbm_quantize"
    assert metadata.category == "ml"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_ml_lgbm_quantize_plan():
    """Test plugin plan."""
    plugin = MlLgbmQuantize()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_ml_lgbm_quantize_run_stub():
    """Test plugin execution (stub)."""
    plugin = MlLgbmQuantize()

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

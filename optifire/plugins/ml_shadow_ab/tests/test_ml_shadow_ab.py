"""
Tests for ml_shadow_ab plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from ml_shadow_ab import MlShadowAb


@pytest.mark.asyncio
async def test_ml_shadow_ab_describe():
    """Test plugin description."""
    plugin = MlShadowAb()
    metadata = plugin.describe()

    assert metadata.plugin_id == "ml_shadow_ab"
    assert metadata.category == "ml"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_ml_shadow_ab_plan():
    """Test plugin plan."""
    plugin = MlShadowAb()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_ml_shadow_ab_run_stub():
    """Test plugin execution (stub)."""
    plugin = MlShadowAb()

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

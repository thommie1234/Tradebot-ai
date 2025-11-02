"""
Tests for fe_kalman plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from fe_kalman import FeKalman


@pytest.mark.asyncio
async def test_fe_kalman_describe():
    """Test plugin description."""
    plugin = FeKalman()
    metadata = plugin.describe()

    assert metadata.plugin_id == "fe_kalman"
    assert metadata.category == "fe"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_fe_kalman_plan():
    """Test plugin plan."""
    plugin = FeKalman()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_fe_kalman_run_stub():
    """Test plugin execution (stub)."""
    plugin = FeKalman()

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

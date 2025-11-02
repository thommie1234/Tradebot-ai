"""
Tests for alpha_position_agnostic plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from alpha_position_agnostic import AlphaPositionAgnostic


@pytest.mark.asyncio
async def test_alpha_position_agnostic_describe():
    """Test plugin description."""
    plugin = AlphaPositionAgnostic()
    metadata = plugin.describe()

    assert metadata.plugin_id == "alpha_position_agnostic"
    assert metadata.category == "alpha"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_alpha_position_agnostic_plan():
    """Test plugin plan."""
    plugin = AlphaPositionAgnostic()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_alpha_position_agnostic_run_stub():
    """Test plugin execution (stub)."""
    plugin = AlphaPositionAgnostic()

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

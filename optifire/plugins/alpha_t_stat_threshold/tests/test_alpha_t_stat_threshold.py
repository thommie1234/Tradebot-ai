"""
Tests for alpha_t_stat_threshold plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from alpha_t_stat_threshold import AlphaTStatThreshold


@pytest.mark.asyncio
async def test_alpha_t_stat_threshold_describe():
    """Test plugin description."""
    plugin = AlphaTStatThreshold()
    metadata = plugin.describe()

    assert metadata.plugin_id == "alpha_t_stat_threshold"
    assert metadata.category == "alpha"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_alpha_t_stat_threshold_plan():
    """Test plugin plan."""
    plugin = AlphaTStatThreshold()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_alpha_t_stat_threshold_run_stub():
    """Test plugin execution (stub)."""
    plugin = AlphaTStatThreshold()

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

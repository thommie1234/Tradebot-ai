"""
Tests for extra_bidask_filter plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from extra_bidask_filter import ExtraBidaskFilter


@pytest.mark.asyncio
async def test_extra_bidask_filter_describe():
    """Test plugin description."""
    plugin = ExtraBidaskFilter()
    metadata = plugin.describe()

    assert metadata.plugin_id == "extra_bidask_filter"
    assert metadata.category == "exec"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_extra_bidask_filter_plan():
    """Test plugin plan."""
    plugin = ExtraBidaskFilter()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_extra_bidask_filter_run_stub():
    """Test plugin execution (stub)."""
    plugin = ExtraBidaskFilter()

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

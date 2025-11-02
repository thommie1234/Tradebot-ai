"""
Tests for sl_perf_trigger plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from sl_perf_trigger import SlPerfTrigger


@pytest.mark.asyncio
async def test_sl_perf_trigger_describe():
    """Test plugin description."""
    plugin = SlPerfTrigger()
    metadata = plugin.describe()

    assert metadata.plugin_id == "sl_perf_trigger"
    assert metadata.category == "ml"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_sl_perf_trigger_plan():
    """Test plugin plan."""
    plugin = SlPerfTrigger()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_sl_perf_trigger_run_stub():
    """Test plugin execution (stub)."""
    plugin = SlPerfTrigger()

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

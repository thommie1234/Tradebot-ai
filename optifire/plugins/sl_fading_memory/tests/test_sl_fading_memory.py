"""
Tests for sl_fading_memory plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from sl_fading_memory import SlFadingMemory


@pytest.mark.asyncio
async def test_sl_fading_memory_describe():
    """Test plugin description."""
    plugin = SlFadingMemory()
    metadata = plugin.describe()

    assert metadata.plugin_id == "sl_fading_memory"
    assert metadata.category == "ml"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_sl_fading_memory_plan():
    """Test plugin plan."""
    plugin = SlFadingMemory()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_sl_fading_memory_run_stub():
    """Test plugin execution (stub)."""
    plugin = SlFadingMemory()

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

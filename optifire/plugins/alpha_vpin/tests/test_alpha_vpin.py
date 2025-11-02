"""
Tests for alpha_vpin plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from alpha_vpin import AlphaVpin


@pytest.mark.asyncio
async def test_alpha_vpin_describe():
    """Test plugin description."""
    plugin = AlphaVpin()
    metadata = plugin.describe()

    assert metadata.plugin_id == "alpha_vpin"
    assert metadata.category == "alpha"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_alpha_vpin_plan():
    """Test plugin plan."""
    plugin = AlphaVpin()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_alpha_vpin_run_stub():
    """Test plugin execution (stub)."""
    plugin = AlphaVpin()

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

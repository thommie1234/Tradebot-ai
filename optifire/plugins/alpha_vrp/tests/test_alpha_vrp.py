"""
Tests for alpha_vrp plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from alpha_vrp import AlphaVrp


@pytest.mark.asyncio
async def test_alpha_vrp_describe():
    """Test plugin description."""
    plugin = AlphaVrp()
    metadata = plugin.describe()

    assert metadata.plugin_id == "alpha_vrp"
    assert metadata.category == "alpha"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_alpha_vrp_plan():
    """Test plugin plan."""
    plugin = AlphaVrp()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_alpha_vrp_run_stub():
    """Test plugin execution (stub)."""
    plugin = AlphaVrp()

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

"""
Tests for alpha_micro_imbalance plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from alpha_micro_imbalance import AlphaMicroImbalance


@pytest.mark.asyncio
async def test_alpha_micro_imbalance_describe():
    """Test plugin description."""
    plugin = AlphaMicroImbalance()
    metadata = plugin.describe()

    assert metadata.plugin_id == "alpha_micro_imbalance"
    assert metadata.category == "alpha"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_alpha_micro_imbalance_plan():
    """Test plugin plan."""
    plugin = AlphaMicroImbalance()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_alpha_micro_imbalance_run_stub():
    """Test plugin execution (stub)."""
    plugin = AlphaMicroImbalance()

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

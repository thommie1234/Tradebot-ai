"""
Tests for ux_strategy_pie plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from ux_strategy_pie import UxStrategyPie


@pytest.mark.asyncio
async def test_ux_strategy_pie_describe():
    """Test plugin description."""
    plugin = UxStrategyPie()
    metadata = plugin.describe()

    assert metadata.plugin_id == "ux_strategy_pie"
    assert metadata.category == "ux"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_ux_strategy_pie_plan():
    """Test plugin plan."""
    plugin = UxStrategyPie()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_ux_strategy_pie_run_stub():
    """Test plugin execution (stub)."""
    plugin = UxStrategyPie()

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

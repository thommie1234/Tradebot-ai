"""
Tests for sl_optuna_pruner plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from sl_optuna_pruner import SlOptunaPruner


@pytest.mark.asyncio
async def test_sl_optuna_pruner_describe():
    """Test plugin description."""
    plugin = SlOptunaPruner()
    metadata = plugin.describe()

    assert metadata.plugin_id == "sl_optuna_pruner"
    assert metadata.category == "ml"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_sl_optuna_pruner_plan():
    """Test plugin plan."""
    plugin = SlOptunaPruner()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_sl_optuna_pruner_run_stub():
    """Test plugin execution (stub)."""
    plugin = SlOptunaPruner()

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

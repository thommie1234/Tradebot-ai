"""
Tests for sl_bayes_update plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from sl_bayes_update import SlBayesUpdate


@pytest.mark.asyncio
async def test_sl_bayes_update_describe():
    """Test plugin description."""
    plugin = SlBayesUpdate()
    metadata = plugin.describe()

    assert metadata.plugin_id == "sl_bayes_update"
    assert metadata.category == "ml"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_sl_bayes_update_plan():
    """Test plugin plan."""
    plugin = SlBayesUpdate()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_sl_bayes_update_run_stub():
    """Test plugin execution (stub)."""
    plugin = SlBayesUpdate()

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

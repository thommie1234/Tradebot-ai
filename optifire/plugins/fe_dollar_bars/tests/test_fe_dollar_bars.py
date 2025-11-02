"""
Tests for fe_dollar_bars plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from fe_dollar_bars import FeDollarBars


@pytest.mark.asyncio
async def test_fe_dollar_bars_describe():
    """Test plugin description."""
    plugin = FeDollarBars()
    metadata = plugin.describe()

    assert metadata.plugin_id == "fe_dollar_bars"
    assert metadata.category == "fe"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_fe_dollar_bars_plan():
    """Test plugin plan."""
    plugin = FeDollarBars()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_fe_dollar_bars_run_stub():
    """Test plugin execution (stub)."""
    plugin = FeDollarBars()

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

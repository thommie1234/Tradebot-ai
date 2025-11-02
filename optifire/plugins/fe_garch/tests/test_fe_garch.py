"""
Tests for fe_garch plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from fe_garch import FeGarch


@pytest.mark.asyncio
async def test_fe_garch_describe():
    """Test plugin description."""
    plugin = FeGarch()
    metadata = plugin.describe()

    assert metadata.plugin_id == "fe_garch"
    assert metadata.category == "fe"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_fe_garch_plan():
    """Test plugin plan."""
    plugin = FeGarch()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_fe_garch_run_stub():
    """Test plugin execution (stub)."""
    plugin = FeGarch()

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

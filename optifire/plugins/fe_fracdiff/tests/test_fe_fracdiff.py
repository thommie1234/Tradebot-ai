"""
Tests for fe_fracdiff plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from fe_fracdiff import FeFracdiff


@pytest.mark.asyncio
async def test_fe_fracdiff_describe():
    """Test plugin description."""
    plugin = FeFracdiff()
    metadata = plugin.describe()

    assert metadata.plugin_id == "fe_fracdiff"
    assert metadata.category == "fe"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_fe_fracdiff_plan():
    """Test plugin plan."""
    plugin = FeFracdiff()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_fe_fracdiff_run_stub():
    """Test plugin execution (stub)."""
    plugin = FeFracdiff()

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

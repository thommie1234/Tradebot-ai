"""
Tests for ux_signal_contrib plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from ux_signal_contrib import UxSignalContrib


@pytest.mark.asyncio
async def test_ux_signal_contrib_describe():
    """Test plugin description."""
    plugin = UxSignalContrib()
    metadata = plugin.describe()

    assert metadata.plugin_id == "ux_signal_contrib"
    assert metadata.category == "ux"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_ux_signal_contrib_plan():
    """Test plugin plan."""
    plugin = UxSignalContrib()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_ux_signal_contrib_run_stub():
    """Test plugin execution (stub)."""
    plugin = UxSignalContrib()

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

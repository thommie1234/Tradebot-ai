"""
Tests for ux_ws_pnl_sse plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from ux_ws_pnl_sse import UxWsPnlSse


@pytest.mark.asyncio
async def test_ux_ws_pnl_sse_describe():
    """Test plugin description."""
    plugin = UxWsPnlSse()
    metadata = plugin.describe()

    assert metadata.plugin_id == "ux_ws_pnl_sse"
    assert metadata.category == "ux"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_ux_ws_pnl_sse_plan():
    """Test plugin plan."""
    plugin = UxWsPnlSse()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_ux_ws_pnl_sse_run_stub():
    """Test plugin execution (stub)."""
    plugin = UxWsPnlSse()

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

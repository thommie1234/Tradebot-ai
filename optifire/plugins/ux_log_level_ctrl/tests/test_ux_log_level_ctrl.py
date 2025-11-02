"""
Tests for ux_log_level_ctrl plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from ux_log_level_ctrl import UxLogLevelCtrl


@pytest.mark.asyncio
async def test_ux_log_level_ctrl_describe():
    """Test plugin description."""
    plugin = UxLogLevelCtrl()
    metadata = plugin.describe()

    assert metadata.plugin_id == "ux_log_level_ctrl"
    assert metadata.category == "ux"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_ux_log_level_ctrl_plan():
    """Test plugin plan."""
    plugin = UxLogLevelCtrl()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_ux_log_level_ctrl_run_stub():
    """Test plugin execution (stub)."""
    plugin = UxLogLevelCtrl()

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

"""
Tests for diag_oos_decay_plot plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from diag_oos_decay_plot import DiagOosDecayPlot


@pytest.mark.asyncio
async def test_diag_oos_decay_plot_describe():
    """Test plugin description."""
    plugin = DiagOosDecayPlot()
    metadata = plugin.describe()

    assert metadata.plugin_id == "diag_oos_decay_plot"
    assert metadata.category == "diag"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_diag_oos_decay_plot_plan():
    """Test plugin plan."""
    plugin = DiagOosDecayPlot()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_diag_oos_decay_plot_run_stub():
    """Test plugin execution (stub)."""
    plugin = DiagOosDecayPlot()

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

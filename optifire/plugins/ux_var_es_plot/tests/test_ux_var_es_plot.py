"""
Tests for ux_var_es_plot plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from ux_var_es_plot import UxVarEsPlot


@pytest.mark.asyncio
async def test_ux_var_es_plot_describe():
    """Test plugin description."""
    plugin = UxVarEsPlot()
    metadata = plugin.describe()

    assert metadata.plugin_id == "ux_var_es_plot"
    assert metadata.category == "ux"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_ux_var_es_plot_plan():
    """Test plugin plan."""
    plugin = UxVarEsPlot()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_ux_var_es_plot_run_stub():
    """Test plugin execution (stub)."""
    plugin = UxVarEsPlot()

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

"""
Tests for diag_sharpe_ci plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from diag_sharpe_ci import DiagSharpeCi


@pytest.mark.asyncio
async def test_diag_sharpe_ci_describe():
    """Test plugin description."""
    plugin = DiagSharpeCi()
    metadata = plugin.describe()

    assert metadata.plugin_id == "diag_sharpe_ci"
    assert metadata.category == "diag"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_diag_sharpe_ci_plan():
    """Test plugin plan."""
    plugin = DiagSharpeCi()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_diag_sharpe_ci_run_stub():
    """Test plugin execution (stub)."""
    plugin = DiagSharpeCi()

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

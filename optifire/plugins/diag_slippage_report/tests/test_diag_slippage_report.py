"""
Tests for diag_slippage_report plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from diag_slippage_report import DiagSlippageReport


@pytest.mark.asyncio
async def test_diag_slippage_report_describe():
    """Test plugin description."""
    plugin = DiagSlippageReport()
    metadata = plugin.describe()

    assert metadata.plugin_id == "diag_slippage_report"
    assert metadata.category == "diag"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_diag_slippage_report_plan():
    """Test plugin plan."""
    plugin = DiagSlippageReport()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_diag_slippage_report_run_stub():
    """Test plugin execution (stub)."""
    plugin = DiagSlippageReport()

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

"""
Tests for alpha_etf_flow_div plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from alpha_etf_flow_div import AlphaEtfFlowDiv


@pytest.mark.asyncio
async def test_alpha_etf_flow_div_describe():
    """Test plugin description."""
    plugin = AlphaEtfFlowDiv()
    metadata = plugin.describe()

    assert metadata.plugin_id == "alpha_etf_flow_div"
    assert metadata.category == "alpha"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_alpha_etf_flow_div_plan():
    """Test plugin plan."""
    plugin = AlphaEtfFlowDiv()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_alpha_etf_flow_div_run_stub():
    """Test plugin execution (stub)."""
    plugin = AlphaEtfFlowDiv()

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

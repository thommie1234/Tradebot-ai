"""
Tests for risk_frac_kelly_atten plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from risk_frac_kelly_atten import RiskFracKellyAtten


@pytest.mark.asyncio
async def test_risk_frac_kelly_atten_describe():
    """Test plugin description."""
    plugin = RiskFracKellyAtten()
    metadata = plugin.describe()

    assert metadata.plugin_id == "risk_frac_kelly_atten"
    assert metadata.category == "risk"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_risk_frac_kelly_atten_plan():
    """Test plugin plan."""
    plugin = RiskFracKellyAtten()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_risk_frac_kelly_atten_run_stub():
    """Test plugin execution (stub)."""
    plugin = RiskFracKellyAtten()

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

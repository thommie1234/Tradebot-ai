"""
Tests for alpha_risk_reversal plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from alpha_risk_reversal import AlphaRiskReversal


@pytest.mark.asyncio
async def test_alpha_risk_reversal_describe():
    """Test plugin description."""
    plugin = AlphaRiskReversal()
    metadata = plugin.describe()

    assert metadata.plugin_id == "alpha_risk_reversal"
    assert metadata.category == "alpha"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_alpha_risk_reversal_plan():
    """Test plugin plan."""
    plugin = AlphaRiskReversal()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_alpha_risk_reversal_run_stub():
    """Test plugin execution (stub)."""
    plugin = AlphaRiskReversal()

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

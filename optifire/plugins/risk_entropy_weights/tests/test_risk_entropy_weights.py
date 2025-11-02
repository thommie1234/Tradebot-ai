"""
Tests for risk_entropy_weights plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from risk_entropy_weights import RiskEntropyWeights


@pytest.mark.asyncio
async def test_risk_entropy_weights_describe():
    """Test plugin description."""
    plugin = RiskEntropyWeights()
    metadata = plugin.describe()

    assert metadata.plugin_id == "risk_entropy_weights"
    assert metadata.category == "risk"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_risk_entropy_weights_plan():
    """Test plugin plan."""
    plugin = RiskEntropyWeights()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_risk_entropy_weights_run_stub():
    """Test plugin execution (stub)."""
    plugin = RiskEntropyWeights()

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

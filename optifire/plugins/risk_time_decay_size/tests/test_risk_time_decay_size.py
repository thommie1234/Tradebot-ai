"""
Tests for risk_time_decay_size plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from risk_time_decay_size import RiskTimeDecaySize


@pytest.mark.asyncio
async def test_risk_time_decay_size_describe():
    """Test plugin description."""
    plugin = RiskTimeDecaySize()
    metadata = plugin.describe()

    assert metadata.plugin_id == "risk_time_decay_size"
    assert metadata.category == "risk"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_risk_time_decay_size_plan():
    """Test plugin plan."""
    plugin = RiskTimeDecaySize()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_risk_time_decay_size_run_stub():
    """Test plugin execution (stub)."""
    plugin = RiskTimeDecaySize()

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

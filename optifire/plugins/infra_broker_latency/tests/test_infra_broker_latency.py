"""
Tests for infra_broker_latency plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from infra_broker_latency import InfraBrokerLatency


@pytest.mark.asyncio
async def test_infra_broker_latency_describe():
    """Test plugin description."""
    plugin = InfraBrokerLatency()
    metadata = plugin.describe()

    assert metadata.plugin_id == "infra_broker_latency"
    assert metadata.category == "infra"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_infra_broker_latency_plan():
    """Test plugin plan."""
    plugin = InfraBrokerLatency()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_infra_broker_latency_run_stub():
    """Test plugin execution (stub)."""
    plugin = InfraBrokerLatency()

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

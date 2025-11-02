"""
Tests for infra_heartbeat plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from infra_heartbeat import InfraHeartbeat


@pytest.mark.asyncio
async def test_infra_heartbeat_describe():
    """Test plugin description."""
    plugin = InfraHeartbeat()
    metadata = plugin.describe()

    assert metadata.plugin_id == "infra_heartbeat"
    assert metadata.category == "infra"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_infra_heartbeat_plan():
    """Test plugin plan."""
    plugin = InfraHeartbeat()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_infra_heartbeat_run_stub():
    """Test plugin execution (stub)."""
    plugin = InfraHeartbeat()

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

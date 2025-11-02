"""
Tests for infra_checkpoint_restart plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from infra_checkpoint_restart import InfraCheckpointRestart


@pytest.mark.asyncio
async def test_infra_checkpoint_restart_describe():
    """Test plugin description."""
    plugin = InfraCheckpointRestart()
    metadata = plugin.describe()

    assert metadata.plugin_id == "infra_checkpoint_restart"
    assert metadata.category == "infra"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_infra_checkpoint_restart_plan():
    """Test plugin plan."""
    plugin = InfraCheckpointRestart()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_infra_checkpoint_restart_run_stub():
    """Test plugin execution (stub)."""
    plugin = InfraCheckpointRestart()

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

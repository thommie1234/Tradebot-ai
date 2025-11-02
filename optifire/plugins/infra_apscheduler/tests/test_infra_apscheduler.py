"""
Tests for infra_apscheduler plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from infra_apscheduler import InfraApscheduler


@pytest.mark.asyncio
async def test_infra_apscheduler_describe():
    """Test plugin description."""
    plugin = InfraApscheduler()
    metadata = plugin.describe()

    assert metadata.plugin_id == "infra_apscheduler"
    assert metadata.category == "infra"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_infra_apscheduler_plan():
    """Test plugin plan."""
    plugin = InfraApscheduler()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_infra_apscheduler_run_stub():
    """Test plugin execution (stub)."""
    plugin = InfraApscheduler()

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

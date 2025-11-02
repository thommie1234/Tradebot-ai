"""
Tests for infra_dockerize plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from infra_dockerize import InfraDockerize


@pytest.mark.asyncio
async def test_infra_dockerize_describe():
    """Test plugin description."""
    plugin = InfraDockerize()
    metadata = plugin.describe()

    assert metadata.plugin_id == "infra_dockerize"
    assert metadata.category == "infra"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_infra_dockerize_plan():
    """Test plugin plan."""
    plugin = InfraDockerize()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_infra_dockerize_run_stub():
    """Test plugin execution (stub)."""
    plugin = InfraDockerize()

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

"""
Tests for infra_api_cache plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from infra_api_cache import InfraApiCache


@pytest.mark.asyncio
async def test_infra_api_cache_describe():
    """Test plugin description."""
    plugin = InfraApiCache()
    metadata = plugin.describe()

    assert metadata.plugin_id == "infra_api_cache"
    assert metadata.category == "infra"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_infra_api_cache_plan():
    """Test plugin plan."""
    plugin = InfraApiCache()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_infra_api_cache_run_stub():
    """Test plugin execution (stub)."""
    plugin = InfraApiCache()

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

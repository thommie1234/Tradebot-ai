"""
Tests for infra_config_hot_reload plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from infra_config_hot_reload import InfraConfigHotReload


@pytest.mark.asyncio
async def test_infra_config_hot_reload_describe():
    """Test plugin description."""
    plugin = InfraConfigHotReload()
    metadata = plugin.describe()

    assert metadata.plugin_id == "infra_config_hot_reload"
    assert metadata.category == "infra"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_infra_config_hot_reload_plan():
    """Test plugin plan."""
    plugin = InfraConfigHotReload()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_infra_config_hot_reload_run_stub():
    """Test plugin execution (stub)."""
    plugin = InfraConfigHotReload()

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

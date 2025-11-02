"""
Tests for infra_psutil_health plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from infra_psutil_health import InfraPsutilHealth


@pytest.mark.asyncio
async def test_infra_psutil_health_describe():
    """Test plugin description."""
    plugin = InfraPsutilHealth()
    metadata = plugin.describe()

    assert metadata.plugin_id == "infra_psutil_health"
    assert metadata.category == "infra"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_infra_psutil_health_plan():
    """Test plugin plan."""
    plugin = InfraPsutilHealth()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_infra_psutil_health_run_stub():
    """Test plugin execution (stub)."""
    plugin = InfraPsutilHealth()

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

"""
Tests for infra_pandera_validation plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from infra_pandera_validation import InfraPanderaValidation


@pytest.mark.asyncio
async def test_infra_pandera_validation_describe():
    """Test plugin description."""
    plugin = InfraPanderaValidation()
    metadata = plugin.describe()

    assert metadata.plugin_id == "infra_pandera_validation"
    assert metadata.category == "infra"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_infra_pandera_validation_plan():
    """Test plugin plan."""
    plugin = InfraPanderaValidation()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_infra_pandera_validation_run_stub():
    """Test plugin execution (stub)."""
    plugin = InfraPanderaValidation()

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

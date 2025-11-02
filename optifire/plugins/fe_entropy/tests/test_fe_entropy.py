"""
Tests for fe_entropy plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from fe_entropy import FeEntropy


@pytest.mark.asyncio
async def test_fe_entropy_describe():
    """Test plugin description."""
    plugin = FeEntropy()
    metadata = plugin.describe()

    assert metadata.plugin_id == "fe_entropy"
    assert metadata.category == "fe"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_fe_entropy_plan():
    """Test plugin plan."""
    plugin = FeEntropy()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_fe_entropy_run_stub():
    """Test plugin execution (stub)."""
    plugin = FeEntropy()

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

"""
Tests for ml_entropy_monitor plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from ml_entropy_monitor import MlEntropyMonitor


@pytest.mark.asyncio
async def test_ml_entropy_monitor_describe():
    """Test plugin description."""
    plugin = MlEntropyMonitor()
    metadata = plugin.describe()

    assert metadata.plugin_id == "ml_entropy_monitor"
    assert metadata.category == "ml"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_ml_entropy_monitor_plan():
    """Test plugin plan."""
    plugin = MlEntropyMonitor()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_ml_entropy_monitor_run_stub():
    """Test plugin execution (stub)."""
    plugin = MlEntropyMonitor()

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

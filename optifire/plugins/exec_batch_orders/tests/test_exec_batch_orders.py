"""
Tests for exec_batch_orders plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from exec_batch_orders import ExecBatchOrders


@pytest.mark.asyncio
async def test_exec_batch_orders_describe():
    """Test plugin description."""
    plugin = ExecBatchOrders()
    metadata = plugin.describe()

    assert metadata.plugin_id == "exec_batch_orders"
    assert metadata.category == "exec"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_exec_batch_orders_plan():
    """Test plugin plan."""
    plugin = ExecBatchOrders()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_exec_batch_orders_run_stub():
    """Test plugin execution (stub)."""
    plugin = ExecBatchOrders()

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

"""
Tests for exec_moc plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from exec_moc import ExecMoc


@pytest.mark.asyncio
async def test_exec_moc_describe():
    """Test plugin description."""
    plugin = ExecMoc()
    metadata = plugin.describe()

    assert metadata.plugin_id == "exec_moc"
    assert metadata.category == "exec"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_exec_moc_plan():
    """Test plugin plan."""
    plugin = ExecMoc()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_exec_moc_run_stub():
    """Test plugin execution (stub)."""
    plugin = ExecMoc()

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

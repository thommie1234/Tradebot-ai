"""
Tests for infra_sqlite_txlog plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from infra_sqlite_txlog import InfraSqliteTxlog


@pytest.mark.asyncio
async def test_infra_sqlite_txlog_describe():
    """Test plugin description."""
    plugin = InfraSqliteTxlog()
    metadata = plugin.describe()

    assert metadata.plugin_id == "infra_sqlite_txlog"
    assert metadata.category == "infra"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_infra_sqlite_txlog_plan():
    """Test plugin plan."""
    plugin = InfraSqliteTxlog()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_infra_sqlite_txlog_run_stub():
    """Test plugin execution (stub)."""
    plugin = InfraSqliteTxlog()

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

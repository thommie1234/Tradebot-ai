"""
Tests for fe_duckdb_store plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from fe_duckdb_store import FeDuckdbStore


@pytest.mark.asyncio
async def test_fe_duckdb_store_describe():
    """Test plugin description."""
    plugin = FeDuckdbStore()
    metadata = plugin.describe()

    assert metadata.plugin_id == "fe_duckdb_store"
    assert metadata.category == "fe"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_fe_duckdb_store_plan():
    """Test plugin plan."""
    plugin = FeDuckdbStore()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_fe_duckdb_store_run_stub():
    """Test plugin execution (stub)."""
    plugin = FeDuckdbStore()

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

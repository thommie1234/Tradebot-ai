"""
Tests for alpha_analyst_revisions plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from alpha_analyst_revisions import AlphaAnalystRevisions


@pytest.mark.asyncio
async def test_alpha_analyst_revisions_describe():
    """Test plugin description."""
    plugin = AlphaAnalystRevisions()
    metadata = plugin.describe()

    assert metadata.plugin_id == "alpha_analyst_revisions"
    assert metadata.category == "alpha"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_alpha_analyst_revisions_plan():
    """Test plugin plan."""
    plugin = AlphaAnalystRevisions()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_alpha_analyst_revisions_run_stub():
    """Test plugin execution (stub)."""
    plugin = AlphaAnalystRevisions()

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

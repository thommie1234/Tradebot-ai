"""
Tests for alpha_coint_pairs plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from alpha_coint_pairs import AlphaCointPairs


@pytest.mark.asyncio
async def test_alpha_coint_pairs_describe():
    """Test plugin description."""
    plugin = AlphaCointPairs()
    metadata = plugin.describe()

    assert metadata.plugin_id == "alpha_coint_pairs"
    assert metadata.category == "alpha"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_alpha_coint_pairs_plan():
    """Test plugin plan."""
    plugin = AlphaCointPairs()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_alpha_coint_pairs_run_stub():
    """Test plugin execution (stub)."""
    plugin = AlphaCointPairs()

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

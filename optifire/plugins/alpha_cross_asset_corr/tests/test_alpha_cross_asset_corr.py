"""
Tests for alpha_cross_asset_corr plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from alpha_cross_asset_corr import AlphaCrossAssetCorr


@pytest.mark.asyncio
async def test_alpha_cross_asset_corr_describe():
    """Test plugin description."""
    plugin = AlphaCrossAssetCorr()
    metadata = plugin.describe()

    assert metadata.plugin_id == "alpha_cross_asset_corr"
    assert metadata.category == "alpha"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_alpha_cross_asset_corr_plan():
    """Test plugin plan."""
    plugin = AlphaCrossAssetCorr()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_alpha_cross_asset_corr_run_stub():
    """Test plugin execution (stub)."""
    plugin = AlphaCrossAssetCorr()

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

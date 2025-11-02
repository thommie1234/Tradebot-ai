"""
Tests for alpha_vix_regime plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from alpha_vix_regime import AlphaVixRegime


@pytest.mark.asyncio
async def test_alpha_vix_regime_describe():
    """Test plugin description."""
    plugin = AlphaVixRegime()
    metadata = plugin.describe()

    assert metadata.plugin_id == "alpha_vix_regime"
    assert metadata.category == "alpha"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_alpha_vix_regime_plan():
    """Test plugin plan."""
    plugin = AlphaVixRegime()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_alpha_vix_regime_run_stub():
    """Test plugin execution (stub)."""
    plugin = AlphaVixRegime()

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

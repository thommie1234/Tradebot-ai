"""
Tests for alpha_google_trends plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from alpha_google_trends import AlphaGoogleTrends


@pytest.mark.asyncio
async def test_alpha_google_trends_describe():
    """Test plugin description."""
    plugin = AlphaGoogleTrends()
    metadata = plugin.describe()

    assert metadata.plugin_id == "alpha_google_trends"
    assert metadata.category == "alpha"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_alpha_google_trends_plan():
    """Test plugin plan."""
    plugin = AlphaGoogleTrends()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_alpha_google_trends_run_stub():
    """Test plugin execution (stub)."""
    plugin = AlphaGoogleTrends()

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

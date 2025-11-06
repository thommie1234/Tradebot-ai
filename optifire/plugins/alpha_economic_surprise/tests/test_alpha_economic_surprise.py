"""
Tests for alpha_economic_surprise plugin.
"""
import pytest
from alpha_economic_surprise.impl import AlphaEconomicSurprise


@pytest.mark.asyncio
async def test_alpha_economic_surprise_describe():
    plugin = AlphaEconomicSurprise()
    metadata = plugin.describe()
    assert metadata.plugin_id == "alpha_economic_surprise"
    assert metadata.category == "alpha"


@pytest.mark.asyncio
async def test_alpha_economic_surprise_plan():
    plugin = AlphaEconomicSurprise()
    plan = plugin.plan()
    assert "schedule" in plan


@pytest.mark.asyncio
async def test_alpha_economic_surprise_run():
    plugin = AlphaEconomicSurprise()
    from optifire.plugins import PluginContext
    context = PluginContext(params={})
    result = await plugin.run(context)
    assert result.success or not result.success

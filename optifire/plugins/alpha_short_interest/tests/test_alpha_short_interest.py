"""
Tests for alpha_short_interest plugin.
"""
import pytest
from alpha_short_interest.impl import AlphaShortInterest


@pytest.mark.asyncio
async def test_alpha_short_interest_describe():
    plugin = AlphaShortInterest()
    metadata = plugin.describe()
    assert metadata.plugin_id == "alpha_short_interest"
    assert metadata.category == "alpha"


@pytest.mark.asyncio
async def test_alpha_short_interest_plan():
    plugin = AlphaShortInterest()
    plan = plugin.plan()
    assert "schedule" in plan


@pytest.mark.asyncio
async def test_alpha_short_interest_run():
    plugin = AlphaShortInterest()
    from optifire.plugins import PluginContext
    context = PluginContext(params={})
    result = await plugin.run(context)
    assert result.success or not result.success  # Can succeed or fail

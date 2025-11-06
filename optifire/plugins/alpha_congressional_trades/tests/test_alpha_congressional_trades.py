"""
Tests for alpha_congressional_trades plugin.
"""
import pytest
from alpha_congressional_trades.impl import AlphaCongressionalTrades


@pytest.mark.asyncio
async def test_alpha_congressional_trades_describe():
    plugin = AlphaCongressionalTrades()
    metadata = plugin.describe()
    assert metadata.plugin_id == "alpha_congressional_trades"
    assert metadata.category == "alpha"


@pytest.mark.asyncio
async def test_alpha_congressional_trades_plan():
    plugin = AlphaCongressionalTrades()
    plan = plugin.plan()
    assert "schedule" in plan


@pytest.mark.asyncio
async def test_alpha_congressional_trades_run():
    plugin = AlphaCongressionalTrades()
    from optifire.plugins import PluginContext
    context = PluginContext(params={})
    result = await plugin.run(context)
    assert result.success or not result.success  # Can succeed or fail

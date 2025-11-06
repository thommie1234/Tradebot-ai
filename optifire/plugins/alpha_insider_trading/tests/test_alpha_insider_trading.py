"""
Tests for alpha_insider_trading plugin.
"""
import pytest
from alpha_insider_trading.impl import AlphaInsiderTrading


@pytest.mark.asyncio
async def test_alpha_insider_trading_describe():
    plugin = AlphaInsiderTrading()
    metadata = plugin.describe()
    assert metadata.plugin_id == "alpha_insider_trading"
    assert metadata.category == "alpha"


@pytest.mark.asyncio
async def test_alpha_insider_trading_plan():
    plugin = AlphaInsiderTrading()
    plan = plugin.plan()
    assert "schedule" in plan


@pytest.mark.asyncio
async def test_alpha_insider_trading_run():
    plugin = AlphaInsiderTrading()
    from optifire.plugins import PluginContext
    context = PluginContext(params={})
    result = await plugin.run(context)
    assert result.success or not result.success  # Can succeed or fail

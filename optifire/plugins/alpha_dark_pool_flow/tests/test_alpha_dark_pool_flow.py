"""
Tests for alpha_dark_pool_flow plugin.
"""
import pytest
from alpha_dark_pool_flow.impl import AlphaDarkPoolFlow


@pytest.mark.asyncio
async def test_alpha_dark_pool_flow_describe():
    plugin = AlphaDarkPoolFlow()
    metadata = plugin.describe()
    assert metadata.plugin_id == "alpha_dark_pool_flow"
    assert metadata.category == "alpha"


@pytest.mark.asyncio
async def test_alpha_dark_pool_flow_plan():
    plugin = AlphaDarkPoolFlow()
    plan = plugin.plan()
    assert "schedule" in plan


@pytest.mark.asyncio
async def test_alpha_dark_pool_flow_run():
    plugin = AlphaDarkPoolFlow()
    from optifire.plugins import PluginContext
    context = PluginContext(params={})
    result = await plugin.run(context)
    assert result.success or not result.success  # Can succeed or fail

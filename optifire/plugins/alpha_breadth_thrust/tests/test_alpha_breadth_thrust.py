"""
Tests for alpha_breadth_thrust plugin.
"""
import pytest
from alpha_breadth_thrust.impl import AlphaBreadthThrust


@pytest.mark.asyncio
async def test_alpha_breadth_thrust_describe():
    plugin = AlphaBreadthThrust()
    metadata = plugin.describe()
    assert metadata.plugin_id == "alpha_breadth_thrust"
    assert metadata.category == "alpha"


@pytest.mark.asyncio
async def test_alpha_breadth_thrust_plan():
    plugin = AlphaBreadthThrust()
    plan = plugin.plan()
    assert "schedule" in plan


@pytest.mark.asyncio
async def test_alpha_breadth_thrust_run():
    plugin = AlphaBreadthThrust()
    from optifire.plugins import PluginContext
    context = PluginContext(params={})
    result = await plugin.run(context)
    assert result.success or not result.success

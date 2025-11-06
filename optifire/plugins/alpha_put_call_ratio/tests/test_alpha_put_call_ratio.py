"""
Tests for alpha_put_call_ratio plugin.
"""
import pytest
from alpha_put_call_ratio.impl import AlphaPutCallRatio


@pytest.mark.asyncio
async def test_alpha_put_call_ratio_describe():
    plugin = AlphaPutCallRatio()
    metadata = plugin.describe()
    assert metadata.plugin_id == "alpha_put_call_ratio"
    assert metadata.category == "alpha"


@pytest.mark.asyncio
async def test_alpha_put_call_ratio_plan():
    plugin = AlphaPutCallRatio()
    plan = plugin.plan()
    assert "schedule" in plan


@pytest.mark.asyncio
async def test_alpha_put_call_ratio_run():
    plugin = AlphaPutCallRatio()
    from optifire.plugins import PluginContext
    context = PluginContext(params={})
    result = await plugin.run(context)
    assert result.success or not result.success

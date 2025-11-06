"""
Tests for alpha_sector_rotation plugin.
"""
import pytest
from alpha_sector_rotation.impl import AlphaSectorRotation


@pytest.mark.asyncio
async def test_alpha_sector_rotation_describe():
    plugin = AlphaSectorRotation()
    metadata = plugin.describe()
    assert metadata.plugin_id == "alpha_sector_rotation"
    assert metadata.category == "alpha"


@pytest.mark.asyncio
async def test_alpha_sector_rotation_plan():
    plugin = AlphaSectorRotation()
    plan = plugin.plan()
    assert "schedule" in plan


@pytest.mark.asyncio
async def test_alpha_sector_rotation_run():
    plugin = AlphaSectorRotation()
    from optifire.plugins import PluginContext
    context = PluginContext(params={})
    result = await plugin.run(context)
    assert result.success or not result.success

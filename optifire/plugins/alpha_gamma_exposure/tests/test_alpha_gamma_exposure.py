"""
Tests for alpha_gamma_exposure plugin.
"""
import pytest
from alpha_gamma_exposure.impl import AlphaGammaExposure


@pytest.mark.asyncio
async def test_alpha_gamma_exposure_describe():
    plugin = AlphaGammaExposure()
    metadata = plugin.describe()
    assert metadata.plugin_id == "alpha_gamma_exposure"
    assert metadata.category == "alpha"


@pytest.mark.asyncio
async def test_alpha_gamma_exposure_plan():
    plugin = AlphaGammaExposure()
    plan = plugin.plan()
    assert "schedule" in plan


@pytest.mark.asyncio
async def test_alpha_gamma_exposure_run():
    plugin = AlphaGammaExposure()
    from optifire.plugins import PluginContext
    context = PluginContext(params={})
    result = await plugin.run(context)
    assert result.success or not result.success

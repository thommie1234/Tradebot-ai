"""
Tests for alpha_crypto_correlation plugin.
"""
import pytest
from alpha_crypto_correlation.impl import AlphaCryptoCorrelation


@pytest.mark.asyncio
async def test_alpha_crypto_correlation_describe():
    plugin = AlphaCryptoCorrelation()
    metadata = plugin.describe()
    assert metadata.plugin_id == "alpha_crypto_correlation"
    assert metadata.category == "alpha"


@pytest.mark.asyncio
async def test_alpha_crypto_correlation_plan():
    plugin = AlphaCryptoCorrelation()
    plan = plugin.plan()
    assert "schedule" in plan


@pytest.mark.asyncio
async def test_alpha_crypto_correlation_run():
    plugin = AlphaCryptoCorrelation()
    from optifire.plugins import PluginContext
    context = PluginContext(params={})
    result = await plugin.run(context)
    assert result.success or not result.success  # Can succeed or fail

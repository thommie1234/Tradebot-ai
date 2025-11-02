"""
Tests for alpha_whisper_spread plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from alpha_whisper_spread import AlphaWhisperSpread


@pytest.mark.asyncio
async def test_alpha_whisper_spread_describe():
    """Test plugin description."""
    plugin = AlphaWhisperSpread()
    metadata = plugin.describe()

    assert metadata.plugin_id == "alpha_whisper_spread"
    assert metadata.category == "alpha"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_alpha_whisper_spread_plan():
    """Test plugin plan."""
    plugin = AlphaWhisperSpread()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_alpha_whisper_spread_run_stub():
    """Test plugin execution (stub)."""
    plugin = AlphaWhisperSpread()

    context = PluginContext(
        config={},
        db=None,
        bus=None,
        data={},
    )

    result = await plugin.run(context)

    assert isinstance(result, PluginResult)
    assert result.success is True
    assert result.data is not None

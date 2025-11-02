"""
Tests for fe_wavelet plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from fe_wavelet import FeWavelet


@pytest.mark.asyncio
async def test_fe_wavelet_describe():
    """Test plugin description."""
    plugin = FeWavelet()
    metadata = plugin.describe()

    assert metadata.plugin_id == "fe_wavelet"
    assert metadata.category == "fe"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_fe_wavelet_plan():
    """Test plugin plan."""
    plugin = FeWavelet()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_fe_wavelet_run_stub():
    """Test plugin execution (stub)."""
    plugin = FeWavelet()

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

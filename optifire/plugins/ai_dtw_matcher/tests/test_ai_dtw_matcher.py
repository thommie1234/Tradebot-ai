"""
Tests for ai_dtw_matcher plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from ai_dtw_matcher import AiDtwMatcher


@pytest.mark.asyncio
async def test_ai_dtw_matcher_describe():
    """Test plugin description."""
    plugin = AiDtwMatcher()
    metadata = plugin.describe()

    assert metadata.plugin_id == "ai_dtw_matcher"
    assert metadata.category == "ai"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_ai_dtw_matcher_plan():
    """Test plugin plan."""
    plugin = AiDtwMatcher()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_ai_dtw_matcher_run_stub():
    """Test plugin execution (stub)."""
    plugin = AiDtwMatcher()

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

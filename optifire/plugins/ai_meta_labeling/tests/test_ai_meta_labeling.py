"""
Tests for ai_meta_labeling plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from ai_meta_labeling import AiMetaLabeling


@pytest.mark.asyncio
async def test_ai_meta_labeling_describe():
    """Test plugin description."""
    plugin = AiMetaLabeling()
    metadata = plugin.describe()

    assert metadata.plugin_id == "ai_meta_labeling"
    assert metadata.category == "ai"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_ai_meta_labeling_plan():
    """Test plugin plan."""
    plugin = AiMetaLabeling()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_ai_meta_labeling_run_stub():
    """Test plugin execution (stub)."""
    plugin = AiMetaLabeling()

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

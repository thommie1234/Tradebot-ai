"""
Tests for ai_topic_clustering plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from ai_topic_clustering import AiTopicClustering


@pytest.mark.asyncio
async def test_ai_topic_clustering_describe():
    """Test plugin description."""
    plugin = AiTopicClustering()
    metadata = plugin.describe()

    assert metadata.plugin_id == "ai_topic_clustering"
    assert metadata.category == "ai"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_ai_topic_clustering_plan():
    """Test plugin plan."""
    plugin = AiTopicClustering()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_ai_topic_clustering_run_stub():
    """Test plugin execution (stub)."""
    plugin = AiTopicClustering()

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

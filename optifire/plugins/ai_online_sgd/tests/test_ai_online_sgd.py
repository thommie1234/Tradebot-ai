"""
Tests for ai_online_sgd plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from ai_online_sgd import AiOnlineSgd


@pytest.mark.asyncio
async def test_ai_online_sgd_describe():
    """Test plugin description."""
    plugin = AiOnlineSgd()
    metadata = plugin.describe()

    assert metadata.plugin_id == "ai_online_sgd"
    assert metadata.category == "ai"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_ai_online_sgd_plan():
    """Test plugin plan."""
    plugin = AiOnlineSgd()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_ai_online_sgd_run_stub():
    """Test plugin execution (stub)."""
    plugin = AiOnlineSgd()

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

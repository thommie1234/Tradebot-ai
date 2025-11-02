"""
Tests for ai_shap_drift plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from ai_shap_drift import AiShapDrift


@pytest.mark.asyncio
async def test_ai_shap_drift_describe():
    """Test plugin description."""
    plugin = AiShapDrift()
    metadata = plugin.describe()

    assert metadata.plugin_id == "ai_shap_drift"
    assert metadata.category == "ai"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_ai_shap_drift_plan():
    """Test plugin plan."""
    plugin = AiShapDrift()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_ai_shap_drift_run_stub():
    """Test plugin execution (stub)."""
    plugin = AiShapDrift()

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

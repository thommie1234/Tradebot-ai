"""
Tests for ml_onnx_runtime plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from ml_onnx_runtime import MlOnnxRuntime


@pytest.mark.asyncio
async def test_ml_onnx_runtime_describe():
    """Test plugin description."""
    plugin = MlOnnxRuntime()
    metadata = plugin.describe()

    assert metadata.plugin_id == "ml_onnx_runtime"
    assert metadata.category == "infra"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_ml_onnx_runtime_plan():
    """Test plugin plan."""
    plugin = MlOnnxRuntime()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_ml_onnx_runtime_run_stub():
    """Test plugin execution (stub)."""
    plugin = MlOnnxRuntime()

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

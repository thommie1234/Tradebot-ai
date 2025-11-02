"""
Tests for fe_mini_pca plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from fe_mini_pca import FeMiniPca


@pytest.mark.asyncio
async def test_fe_mini_pca_describe():
    """Test plugin description."""
    plugin = FeMiniPca()
    metadata = plugin.describe()

    assert metadata.plugin_id == "fe_mini_pca"
    assert metadata.category == "fe"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_fe_mini_pca_plan():
    """Test plugin plan."""
    plugin = FeMiniPca()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_fe_mini_pca_run_stub():
    """Test plugin execution (stub)."""
    plugin = FeMiniPca()

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

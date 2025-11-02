"""
Tests for fe_price_news_div plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from fe_price_news_div import FePriceNewsDiv


@pytest.mark.asyncio
async def test_fe_price_news_div_describe():
    """Test plugin description."""
    plugin = FePriceNewsDiv()
    metadata = plugin.describe()

    assert metadata.plugin_id == "fe_price_news_div"
    assert metadata.category == "fe"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_fe_price_news_div_plan():
    """Test plugin plan."""
    plugin = FePriceNewsDiv()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_fe_price_news_div_run_stub():
    """Test plugin execution (stub)."""
    plugin = FePriceNewsDiv()

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

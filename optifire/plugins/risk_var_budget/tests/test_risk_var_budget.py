"""
Tests for risk_var_budget plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from risk_var_budget import RiskVarBudget


@pytest.mark.asyncio
async def test_risk_var_budget_describe():
    """Test plugin description."""
    plugin = RiskVarBudget()
    metadata = plugin.describe()

    assert metadata.plugin_id == "risk_var_budget"
    assert metadata.category == "risk"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_risk_var_budget_plan():
    """Test plugin plan."""
    plugin = RiskVarBudget()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_risk_var_budget_run_stub():
    """Test plugin execution (stub)."""
    plugin = RiskVarBudget()

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

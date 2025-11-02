"""
Tests for ux_discord_cmds plugin.
"""
import pytest
from optifire.plugins import PluginContext, PluginResult
from ux_discord_cmds import UxDiscordCmds


@pytest.mark.asyncio
async def test_ux_discord_cmds_describe():
    """Test plugin description."""
    plugin = UxDiscordCmds()
    metadata = plugin.describe()

    assert metadata.plugin_id == "ux_discord_cmds"
    assert metadata.category == "ux"
    assert metadata.est_cpu_ms > 0
    assert metadata.est_mem_mb > 0


@pytest.mark.asyncio
async def test_ux_discord_cmds_plan():
    """Test plugin plan."""
    plugin = UxDiscordCmds()
    plan = plugin.plan()

    assert "schedule" in plan
    assert "triggers" in plan


@pytest.mark.asyncio
async def test_ux_discord_cmds_run_stub():
    """Test plugin execution (stub)."""
    plugin = UxDiscordCmds()

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

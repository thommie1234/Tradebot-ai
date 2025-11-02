"""Tests for core modules."""
import pytest
import asyncio
from pathlib import Path
import tempfile

from optifire.core.config import Config
from optifire.core.flags import FeatureFlags
from optifire.core.bus import EventBus, Event


@pytest.mark.asyncio
async def test_config_basic():
    """Test basic configuration loading."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("test_key: test_value\n")
        f.flush()

        config = Config(Path(f.name))
        assert config.get("test_key") == "test_value"


@pytest.mark.asyncio
async def test_event_bus():
    """Test event bus pub/sub."""
    bus = EventBus()
    await bus.start()

    received_events = []

    async def handler(event: Event):
        received_events.append(event)

    await bus.subscribe("test_event", handler)
    await bus.publish("test_event", {"data": "test"}, source="test")

    # Give time for async processing
    await asyncio.sleep(0.1)

    assert len(received_events) == 1
    assert received_events[0].type == "test_event"
    assert received_events[0].data == {"data": "test"}

    await bus.stop()


def test_config_default_values():
    """Test configuration default values."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("{}\n")
        f.flush()

        config = Config(Path(f.name))
        # Should fall back to defaults
        assert config.get("system.max_workers") == 3
        assert config.get("risk.max_exposure_total") == 0.30

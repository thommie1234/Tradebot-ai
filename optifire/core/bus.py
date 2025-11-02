"""
Event bus for pub/sub communication between components.
"""
import asyncio
from typing import Any, Callable, Dict, List
from dataclasses import dataclass
from datetime import datetime
import json

from .logger import logger


@dataclass
class Event:
    """Event data structure."""

    type: str
    data: Any
    source: str
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.type,
            "data": self.data,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), default=str)


class EventBus:
    """
    Async event bus for decoupled communication.
    Thread-safe, supports wildcard subscriptions.
    """

    def __init__(self):
        """Initialize event bus."""
        self._subscribers: Dict[str, List[Callable]] = {}
        self._lock = asyncio.Lock()
        self._queue: asyncio.Queue = asyncio.Queue()
        self._running = False

    async def start(self) -> None:
        """Start event bus processing."""
        self._running = True
        asyncio.create_task(self._process_events())
        logger.info("Event bus started")

    async def stop(self) -> None:
        """Stop event bus processing."""
        self._running = False
        logger.info("Event bus stopped")

    async def _process_events(self) -> None:
        """Process events from queue."""
        while self._running:
            try:
                event = await asyncio.wait_for(self._queue.get(), timeout=1.0)
                await self._dispatch_event(event)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing event: {e}")

    async def _dispatch_event(self, event: Event) -> None:
        """Dispatch event to subscribers."""
        async with self._lock:
            # Exact match
            if event.type in self._subscribers:
                for handler in self._subscribers[event.type]:
                    try:
                        if asyncio.iscoroutinefunction(handler):
                            await handler(event)
                        else:
                            handler(event)
                    except Exception as e:
                        logger.error(
                            f"Error in event handler for {event.type}: {e}",
                            exc_info=True,
                        )

            # Wildcard match (*)
            if "*" in self._subscribers:
                for handler in self._subscribers["*"]:
                    try:
                        if asyncio.iscoroutinefunction(handler):
                            await handler(event)
                        else:
                            handler(event)
                    except Exception as e:
                        logger.error(
                            f"Error in wildcard event handler: {e}",
                            exc_info=True,
                        )

    async def publish(
        self,
        event_type: str,
        data: Any,
        source: str = "system",
    ) -> None:
        """
        Publish an event.

        Args:
            event_type: Event type identifier
            data: Event data
            source: Event source identifier
        """
        event = Event(type=event_type, data=data, source=source)
        await self._queue.put(event)
        logger.debug(f"Published event: {event_type} from {source}")

    async def subscribe(
        self,
        event_type: str,
        handler: Callable[[Event], Any],
    ) -> None:
        """
        Subscribe to events.

        Args:
            event_type: Event type to subscribe to (use "*" for all)
            handler: Callback function (sync or async)
        """
        async with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []

            self._subscribers[event_type].append(handler)
            logger.debug(
                f"Subscribed to {event_type}: {handler.__name__} "
                f"({len(self._subscribers[event_type])} total)"
            )

    async def unsubscribe(
        self,
        event_type: str,
        handler: Callable[[Event], Any],
    ) -> None:
        """
        Unsubscribe from events.

        Args:
            event_type: Event type
            handler: Handler to remove
        """
        async with self._lock:
            if event_type in self._subscribers:
                if handler in self._subscribers[event_type]:
                    self._subscribers[event_type].remove(handler)
                    logger.debug(f"Unsubscribed from {event_type}: {handler.__name__}")

    def get_subscriber_count(self, event_type: str) -> int:
        """Get number of subscribers for an event type."""
        return len(self._subscribers.get(event_type, []))

    def get_all_event_types(self) -> List[str]:
        """Get all subscribed event types."""
        return list(self._subscribers.keys())

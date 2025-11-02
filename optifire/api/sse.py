"""Server-Sent Events for real-time updates."""
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
import asyncio
import json
from datetime import datetime

router = APIRouter()


async def event_generator(request: Request):
    """Generate SSE events from EventBus."""
    g = request.app.state.g
    broker = g.broker
    bus = g.bus

    # Create a queue to receive events
    event_queue = asyncio.Queue()

    # Subscribe to all events
    async def event_handler(event):
        """Handle events from bus."""
        await event_queue.put(event)

    await bus.subscribe("*", event_handler)

    try:
        # Send initial connection event
        yield f"data: {json.dumps({'type': 'connected', 'timestamp': datetime.utcnow().isoformat()})}\n\n"

        # Main event loop
        while True:
            # Send periodic portfolio updates
            try:
                # Try to get portfolio data
                account = await broker.get_account()
                portfolio_data = {
                    "type": "portfolio_update",
                    "equity": float(account.get("equity", 0)),
                    "unrealized_pnl": float(account.get("unrealized_pl", 0)),
                    "realized_pnl": float(account.get("realized_pl", 0)),
                    "timestamp": datetime.utcnow().isoformat(),
                }
                yield f"data: {json.dumps(portfolio_data)}\n\n"
            except Exception as e:
                # If Alpaca fails, send mock data
                pass

            # Check for events from the bus (non-blocking)
            try:
                event = await asyncio.wait_for(event_queue.get(), timeout=2.0)
                event_data = {
                    "type": event.type,
                    "data": event.data,
                    "source": event.source,
                    "timestamp": event.timestamp.isoformat(),
                }
                yield f"data: {json.dumps(event_data)}\n\n"
            except asyncio.TimeoutError:
                # No events, continue
                pass

            await asyncio.sleep(0.1)

    finally:
        # Cleanup: unsubscribe from bus
        await bus.unsubscribe("*", event_handler)


@router.get("/stream")
async def stream_events(request: Request):
    """Stream real-time events via SSE."""
    return StreamingResponse(
        event_generator(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )

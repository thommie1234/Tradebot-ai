"""
Order executor with batching and slippage handling.
"""
import asyncio
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, time as dt_time

from optifire.core.logger import logger
from optifire.core.errors import ExecutionError
from optifire.core.db import Database
from .broker_alpaca import AlpacaBroker
from .slippage import SlippageModel


@dataclass
class OrderRequest:
    """Order request."""

    symbol: str
    qty: float
    side: str
    order_type: str = "market"
    limit_price: Optional[float] = None
    metadata: Optional[Dict] = None


class OrderExecutor:
    """
    Order executor with batching and risk integration.
    """

    def __init__(
        self,
        broker: AlpacaBroker,
        db: Database,
        batch_window_seconds: float = 1.0,
        rth_only: bool = True,
    ):
        """
        Initialize executor.

        Args:
            broker: Broker client
            db: Database instance
            batch_window_seconds: Batch window for order aggregation
            rth_only: Only trade during regular trading hours
        """
        self.broker = broker
        self.db = db
        self.batch_window_seconds = batch_window_seconds
        self.rth_only = rth_only
        self.slippage_model = SlippageModel()

        self._order_queue: List[OrderRequest] = []
        self._queue_lock = asyncio.Lock()
        self._batch_task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """Start executor."""
        if not self._batch_task:
            self._batch_task = asyncio.create_task(self._batch_processor())
        logger.info("Order executor started")

    async def stop(self) -> None:
        """Stop executor."""
        if self._batch_task:
            self._batch_task.cancel()
            try:
                await self._batch_task
            except asyncio.CancelledError:
                pass
            self._batch_task = None
        logger.info("Order executor stopped")

    async def submit_order(self, request: OrderRequest) -> str:
        """
        Submit order to batch queue.

        Args:
            request: Order request

        Returns:
            Order ID (placeholder until batched)
        """
        # Check RTH
        if self.rth_only and not self._is_rth():
            raise ExecutionError("Outside regular trading hours")

        async with self._queue_lock:
            self._order_queue.append(request)
            logger.debug(
                f"Order queued: {request.symbol} {request.side} {request.qty} "
                f"(queue size: {len(self._order_queue)})"
            )

        return f"queued_{len(self._order_queue)}"

    async def _batch_processor(self) -> None:
        """Process order batches."""
        while True:
            try:
                await asyncio.sleep(self.batch_window_seconds)

                async with self._queue_lock:
                    if not self._order_queue:
                        continue

                    # Take current batch
                    batch = self._order_queue.copy()
                    self._order_queue.clear()

                logger.info(f"Processing batch of {len(batch)} orders")

                # Aggregate same-symbol orders
                aggregated = self._aggregate_orders(batch)

                # Execute orders
                for agg_request in aggregated:
                    try:
                        await self._execute_single(agg_request)
                    except Exception as e:
                        logger.error(
                            f"Error executing {agg_request.symbol}: {e}",
                            exc_info=True,
                        )

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in batch processor: {e}", exc_info=True)

    def _aggregate_orders(self, batch: List[OrderRequest]) -> List[OrderRequest]:
        """Aggregate orders for same symbol."""
        aggregated: Dict[str, OrderRequest] = {}

        for req in batch:
            key = f"{req.symbol}_{req.side}_{req.order_type}"

            if key in aggregated:
                # Aggregate quantity
                aggregated[key].qty += req.qty
            else:
                aggregated[key] = req

        return list(aggregated.values())

    async def _execute_single(self, request: OrderRequest) -> None:
        """Execute a single aggregated order."""
        if request.qty == 0:
            logger.debug(f"Skipping zero-quantity order for {request.symbol}")
            return

        # Submit to broker
        order = await self.broker.submit_order(
            symbol=request.symbol,
            qty=abs(request.qty),
            side=request.side,
            order_type=request.order_type,
            limit_price=request.limit_price,
        )

        # Log to database
        await self.db.insert_order({
            "order_id": order["id"],
            "symbol": request.symbol,
            "side": request.side,
            "qty": request.qty,
            "order_type": request.order_type,
            "status": order.get("status", "pending"),
            "submitted_at": order.get("submitted_at"),
            "metadata": str(request.metadata) if request.metadata else None,
        })

        logger.info(
            f"Executed: {request.symbol} {request.side} {request.qty} "
            f"({request.order_type}) - Order ID: {order['id']}"
        )

    def _is_rth(self) -> bool:
        """Check if currently in regular trading hours."""
        now = datetime.now()

        # Check if weekday
        if now.weekday() >= 5:  # Saturday or Sunday
            return False

        # Check market hours (9:30 AM - 4:00 PM ET)
        # Simplified: just check time (not accounting for holidays)
        market_open = dt_time(9, 30)
        market_close = dt_time(16, 0)
        current_time = now.time()

        return market_open <= current_time <= market_close

    async def cancel_order(self, order_id: str) -> None:
        """Cancel an order."""
        await self.broker.cancel_order(order_id)
        await self.db.update_order(
            order_id,
            {"status": "canceled", "canceled_at": datetime.utcnow().isoformat()},
        )

    async def get_order_status(self, order_id: str) -> Dict:
        """Get order status from database."""
        order = await self.db.fetch_one(
            "SELECT * FROM orders WHERE order_id = ?",
            (order_id,),
        )
        return order if order else {}

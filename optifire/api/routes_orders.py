"""Order management routes."""
from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from typing import Optional

from optifire.api.routes_auth import verify_token

try:
    from optifire.exec.market_hours import get_market_status
except:
    # Fallback if market_hours not available
    def get_market_status():
        return {"is_open": True, "status": "unknown", "message": "Market status unknown"}

router = APIRouter()


class OrderRequest(BaseModel):
    symbol: str
    qty: Optional[float] = None
    notional: Optional[float] = None
    side: str = "buy"
    order_type: str = "market"
    time_in_force: str = "day"
    limit_price: Optional[float] = None
    stop_price: Optional[float] = None


@router.post("/submit")
async def submit_order(order: OrderRequest, request: Request, user=Depends(verify_token)):
    """Submit a manual order. Requires authentication."""
    g = request.app.state.g
    broker = g.broker

    try:
        # Validate inputs
        if not order.qty and not order.notional:
            raise HTTPException(status_code=400, detail="Must specify qty or notional")

        if order.qty and order.qty <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be positive")

        # Check market hours for market orders
        market_status = get_market_status()
        if order.order_type == "market" and not market_status["is_open"]:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot place market order: {market_status['message']}. Use limit order instead."
            )

        # Check buying power before submitting order
        account = await broker.get_account()
        buying_power = float(account.get("buying_power", 0))

        # Calculate estimated order cost
        if order.notional:
            estimated_cost = order.notional
        else:
            # Get current price to estimate cost
            try:
                latest_trade = await broker.get_latest_trade(order.symbol.upper())
                current_price = float(latest_trade.get("p", 0))
                estimated_cost = order.qty * current_price
            except Exception:
                # If we can't get price, allow order through (Alpaca will validate)
                estimated_cost = 0

        # Validate buying power (only for buy orders)
        if order.side.lower() == "buy" and estimated_cost > 0:
            if estimated_cost > buying_power:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient buying power. Order cost: ${estimated_cost:.2f}, Available: ${buying_power:.2f}"
                )

        # Submit order via Alpaca
        result = await broker.submit_order(
            symbol=order.symbol.upper(),
            qty=order.qty,
            notional=order.notional,
            side=order.side.lower(),
            order_type=order.order_type.lower(),
            time_in_force=order.time_in_force.lower(),
            limit_price=order.limit_price,
            stop_price=order.stop_price,
        )

        # Log order in database
        await g.db.insert_order({
            "order_id": result["id"],
            "symbol": result["symbol"],
            "side": result["side"],
            "qty": float(result.get("qty", 0)),
            "order_type": result["type"],
            "limit_price": result.get("limit_price"),
            "stop_price": result.get("stop_price"),
            "status": result["status"],
            "submitted_at": result.get("submitted_at"),
        })

        # Publish event
        await g.bus.publish(
            "order_submitted",
            {
                "order_id": result["id"],
                "symbol": result["symbol"],
                "side": result["side"],
                "qty": float(result.get("qty", 0)),
            },
            source="api",
        )

        return {
            "order_id": result["id"],
            "symbol": result["symbol"],
            "qty": result.get("qty"),
            "side": result["side"],
            "status": result["status"],
            "submitted_at": result.get("submitted_at"),
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{order_id}")
async def get_order(order_id: str, request: Request):
    """Get order status."""
    g = request.app.state.g
    broker = g.broker

    try:
        order = await broker.get_order(order_id)
        return {
            "order_id": order["id"],
            "symbol": order["symbol"],
            "side": order["side"],
            "qty": order.get("qty"),
            "status": order["status"],
            "filled_qty": order.get("filled_qty"),
            "filled_avg_price": order.get("filled_avg_price"),
            "submitted_at": order.get("submitted_at"),
            "filled_at": order.get("filled_at"),
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{order_id}")
async def cancel_order(order_id: str, request: Request, user=Depends(verify_token)):
    """Cancel an order. Requires authentication."""
    g = request.app.state.g
    broker = g.broker

    try:
        await broker.cancel_order(order_id)

        # Update database
        await g.db.update_order(order_id, {"status": "canceled"})

        # Publish event
        await g.bus.publish(
            "order_canceled",
            {"order_id": order_id},
            source="api",
        )

        return {
            "order_id": order_id,
            "status": "canceled",
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/")
async def list_orders(limit: int = 100, request: Request = None):
    """List recent orders."""
    g = request.app.state.g
    db = g.db

    try:
        orders = await db.fetch_all(
            "SELECT * FROM orders ORDER BY submitted_at DESC LIMIT ?",
            (limit,),
        )
        return {"orders": orders}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

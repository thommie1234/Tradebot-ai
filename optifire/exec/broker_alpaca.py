"""
Alpaca broker integration.
"""
import os
from typing import Dict, List, Optional
import httpx
from datetime import datetime

from optifire.core.logger import logger
from optifire.core.errors import ExecutionError


class AlpacaBroker:
    """
    Alpaca API client for paper/live trading.
    """

    def __init__(self, paper: bool = True):
        """
        Initialize Alpaca broker.

        Args:
            paper: Use paper trading endpoint
        """
        self.api_key = os.getenv("ALPACA_API_KEY")
        self.api_secret = os.getenv("ALPACA_API_SECRET")

        if not self.api_key or not self.api_secret:
            logger.warning("Alpaca credentials not found in environment")

        self.base_url = (
            "https://paper-api.alpaca.markets"
            if paper
            else "https://api.alpaca.markets"
        )

        self.headers = {
            "APCA-API-KEY-ID": self.api_key or "",
            "APCA-API-SECRET-KEY": self.api_secret or "",
        }

    async def get_account(self) -> Dict:
        """Get account information."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/v2/account",
                headers=self.headers,
                timeout=10.0,
            )
            response.raise_for_status()
            return response.json()

    async def get_positions(self) -> List[Dict]:
        """Get all positions."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/v2/positions",
                headers=self.headers,
                timeout=10.0,
            )
            response.raise_for_status()
            return response.json()

    async def get_position(self, symbol: str) -> Optional[Dict]:
        """Get position for a symbol."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/v2/positions/{symbol}",
                    headers=self.headers,
                    timeout=10.0,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise

    async def submit_order(
        self,
        symbol: str,
        qty: Optional[float] = None,
        notional: Optional[float] = None,
        side: str = "buy",
        order_type: str = "market",
        time_in_force: str = "day",
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None,
    ) -> Dict:
        """
        Submit an order.

        Args:
            symbol: Symbol to trade
            qty: Quantity (shares)
            notional: Dollar amount
            side: buy or sell
            order_type: market, limit, stop, stop_limit
            time_in_force: day, gtc, ioc, fok
            limit_price: Limit price for limit orders
            stop_price: Stop price for stop orders

        Returns:
            Order response
        """
        payload = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "time_in_force": time_in_force,
        }

        if qty is not None:
            payload["qty"] = qty
        elif notional is not None:
            payload["notional"] = notional
        else:
            raise ExecutionError("Must specify qty or notional")

        if limit_price is not None:
            payload["limit_price"] = limit_price

        if stop_price is not None:
            payload["stop_price"] = stop_price

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/v2/orders",
                headers=self.headers,
                json=payload,
                timeout=10.0,
            )

            # Better error handling
            if response.status_code != 200:
                error_detail = response.text
                try:
                    error_json = response.json()
                    error_msg = error_json.get('message', error_detail)
                except:
                    error_msg = error_detail

                logger.error(f"Order failed: {error_msg}")
                raise ExecutionError(f"Alpaca order failed: {error_msg}")

            order = response.json()

        logger.info(f"Order submitted: {symbol} {side} {qty or notional} - {order['id']}")
        return order

    async def cancel_order(self, order_id: str) -> None:
        """Cancel an order."""
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.base_url}/v2/orders/{order_id}",
                headers=self.headers,
                timeout=10.0,
            )
            response.raise_for_status()

        logger.info(f"Order canceled: {order_id}")

    async def get_order(self, order_id: str) -> Dict:
        """Get order status."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/v2/orders/{order_id}",
                headers=self.headers,
                timeout=10.0,
            )
            response.raise_for_status()
            return response.json()

    async def get_bars(
        self,
        symbol: str,
        timeframe: str = "1Day",
        start: Optional[str] = None,
        end: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict]:
        """Get historical bars."""
        params = {
            "timeframe": timeframe,
            "limit": limit,
        }
        if start:
            params["start"] = start
        if end:
            params["end"] = end

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/v2/stocks/{symbol}/bars",
                headers=self.headers,
                params=params,
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("bars", [])

    async def get_latest_trade(self, symbol: str) -> Dict:
        """Get latest trade."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/v2/stocks/{symbol}/trades/latest",
                headers=self.headers,
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("trade", {})

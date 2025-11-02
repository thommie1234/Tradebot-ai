"""
Order routing logic with smart order types.
"""
from typing import Dict, Optional
from enum import Enum

from optifire.core.logger import logger


class OrderType(Enum):
    """Order types."""

    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    MOC = "moc"  # Market on Close
    MOO = "moo"  # Market on Open


class OrderRouter:
    """
    Smart order router for optimal execution.
    """

    def __init__(self):
        """Initialize order router."""
        pass

    def route_order(
        self,
        symbol: str,
        qty: float,
        side: str,
        urgency: str = "normal",
        current_price: Optional[float] = None,
        volatility: Optional[float] = None,
    ) -> Dict:
        """
        Determine optimal order type and parameters.

        Args:
            symbol: Symbol to trade
            qty: Quantity
            side: buy or sell
            urgency: low, normal, high
            current_price: Current market price
            volatility: Current volatility

        Returns:
            Order parameters dictionary
        """
        # Default to market order
        order_type = OrderType.MARKET.value
        limit_price = None

        # Low urgency: use limit orders
        if urgency == "low":
            order_type = OrderType.LIMIT.value
            if current_price:
                # Set limit price slightly better than market
                if side == "buy":
                    limit_price = current_price * 0.999  # 0.1% below
                else:
                    limit_price = current_price * 1.001  # 0.1% above

        # High volatility: use limit orders
        elif volatility and volatility > 0.30:
            order_type = OrderType.LIMIT.value
            if current_price:
                if side == "buy":
                    limit_price = current_price * 1.002  # 0.2% above for fill
                else:
                    limit_price = current_price * 0.998  # 0.2% below for fill

        logger.debug(
            f"Routed order: {symbol} {side} {qty} as {order_type} "
            f"(urgency={urgency}, limit_price={limit_price})"
        )

        return {
            "order_type": order_type,
            "limit_price": limit_price,
        }

    def add_protective_stops(
        self,
        entry_price: float,
        side: str,
        atr: Optional[float] = None,
        stop_loss_multiplier: float = 2.0,
        take_profit_multiplier: float = 3.0,
    ) -> Dict:
        """
        Calculate protective stop and take profit levels.

        Args:
            entry_price: Entry price
            side: buy or sell
            atr: Average True Range
            stop_loss_multiplier: ATR multiplier for stop loss
            take_profit_multiplier: ATR multiplier for take profit

        Returns:
            Dictionary with stop_price and take_profit_price
        """
        if not atr:
            # Default to 2% stop, 3% target
            atr = entry_price * 0.01

        if side == "buy":
            stop_price = entry_price - (atr * stop_loss_multiplier)
            take_profit_price = entry_price + (atr * take_profit_multiplier)
        else:
            stop_price = entry_price + (atr * stop_loss_multiplier)
            take_profit_price = entry_price - (atr * take_profit_multiplier)

        return {
            "stop_price": stop_price,
            "take_profit_price": take_profit_price,
        }

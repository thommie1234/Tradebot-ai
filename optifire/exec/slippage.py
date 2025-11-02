"""
Slippage model for execution cost estimation.
"""
from typing import Optional
import numpy as np

from optifire.core.logger import logger


class SlippageModel:
    """
    Slippage and transaction cost estimator.
    """

    def __init__(
        self,
        base_slippage_bps: float = 2.0,
        volume_impact_factor: float = 0.1,
        volatility_impact_factor: float = 0.5,
    ):
        """
        Initialize slippage model.

        Args:
            base_slippage_bps: Base slippage in basis points
            volume_impact_factor: Impact from volume ratio
            volatility_impact_factor: Impact from volatility
        """
        self.base_slippage_bps = base_slippage_bps
        self.volume_impact_factor = volume_impact_factor
        self.volatility_impact_factor = volatility_impact_factor

    def estimate_slippage(
        self,
        qty: float,
        avg_daily_volume: Optional[float] = None,
        volatility: Optional[float] = None,
        is_market_order: bool = True,
    ) -> float:
        """
        Estimate slippage for an order.

        Args:
            qty: Order quantity
            avg_daily_volume: Average daily volume
            volatility: Current volatility (annualized)
            is_market_order: True if market order

        Returns:
            Estimated slippage in basis points
        """
        slippage_bps = self.base_slippage_bps

        # Limit orders have less slippage
        if not is_market_order:
            slippage_bps *= 0.5

        # Volume impact
        if avg_daily_volume and avg_daily_volume > 0:
            volume_ratio = abs(qty) / avg_daily_volume
            volume_impact = self.volume_impact_factor * volume_ratio * 10000  # to bps
            slippage_bps += volume_impact

        # Volatility impact
        if volatility:
            vol_impact = self.volatility_impact_factor * volatility * 100  # to bps
            slippage_bps += vol_impact

        return slippage_bps

    def estimate_execution_price(
        self,
        current_price: float,
        qty: float,
        side: str,
        avg_daily_volume: Optional[float] = None,
        volatility: Optional[float] = None,
        is_market_order: bool = True,
    ) -> float:
        """
        Estimate execution price including slippage.

        Args:
            current_price: Current market price
            qty: Order quantity
            side: 'buy' or 'sell'
            avg_daily_volume: Average daily volume
            volatility: Current volatility
            is_market_order: True if market order

        Returns:
            Estimated execution price
        """
        slippage_bps = self.estimate_slippage(
            qty, avg_daily_volume, volatility, is_market_order
        )

        # Convert bps to decimal
        slippage_pct = slippage_bps / 10000

        # Apply slippage
        if side == "buy":
            # Pay more when buying
            execution_price = current_price * (1 + slippage_pct)
        else:
            # Receive less when selling
            execution_price = current_price * (1 - slippage_pct)

        return execution_price

    def estimate_cost(
        self,
        current_price: float,
        qty: float,
        side: str,
        avg_daily_volume: Optional[float] = None,
        volatility: Optional[float] = None,
    ) -> float:
        """
        Estimate total cost including slippage.

        Args:
            current_price: Current market price
            qty: Order quantity
            side: 'buy' or 'sell'
            avg_daily_volume: Average daily volume
            volatility: Current volatility

        Returns:
            Estimated total cost
        """
        execution_price = self.estimate_execution_price(
            current_price, qty, side, avg_daily_volume, volatility
        )

        total_cost = execution_price * abs(qty)
        return total_cost

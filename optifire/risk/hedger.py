"""
Portfolio hedging with beta-based SPY hedge.
"""
from typing import Dict, Optional, Tuple
import numpy as np

from optifire.core.logger import logger


class BetaHedger:
    """
    Beta-based portfolio hedger using SPY.
    """

    def __init__(
        self,
        beta_threshold: float = 0.6,
        hedge_ratio_target: float = 1.0,
    ):
        """
        Initialize beta hedger.

        Args:
            beta_threshold: Beta above which to hedge
            hedge_ratio_target: Target hedge ratio (1.0 = fully hedged)
        """
        self.beta_threshold = beta_threshold
        self.hedge_ratio_target = hedge_ratio_target

    def calculate_portfolio_beta(
        self,
        positions: Dict[str, float],
        betas: Dict[str, float],
        portfolio_value: float,
    ) -> float:
        """
        Calculate weighted portfolio beta.

        Args:
            positions: Dict of symbol -> position value
            betas: Dict of symbol -> beta
            portfolio_value: Total portfolio value

        Returns:
            Portfolio beta
        """
        if not positions or portfolio_value == 0:
            return 0.0

        weighted_beta = 0.0
        for symbol, position_value in positions.items():
            beta = betas.get(symbol, 1.0)
            weight = position_value / portfolio_value
            weighted_beta += weight * beta

        return weighted_beta

    def calculate_hedge(
        self,
        portfolio_value: float,
        portfolio_beta: float,
        spy_price: float,
    ) -> Tuple[int, str]:
        """
        Calculate SPY hedge quantity.

        Args:
            portfolio_value: Total portfolio value
            portfolio_beta: Portfolio beta
            spy_price: Current SPY price

        Returns:
            Tuple of (hedge_quantity, reason)
        """
        # Check if hedging is needed
        if portfolio_beta < self.beta_threshold:
            logger.debug(
                f"No hedge needed: beta {portfolio_beta:.2f} < "
                f"threshold {self.beta_threshold:.2f}"
            )
            return 0, "beta_below_threshold"

        # Calculate hedge quantity
        # Hedge qty = (Portfolio Value * Beta * Hedge Ratio) / SPY Price
        hedge_value = portfolio_value * portfolio_beta * self.hedge_ratio_target
        hedge_qty = -int(hedge_value / spy_price)  # Negative = short

        logger.info(
            f"Hedge calculated: {hedge_qty} SPY @ ${spy_price:.2f} "
            f"(beta={portfolio_beta:.2f})"
        )

        return hedge_qty, "beta_hedge"

    def adjust_existing_hedge(
        self,
        current_hedge_qty: int,
        target_hedge_qty: int,
        rebalance_threshold: float = 0.20,
    ) -> Tuple[int, bool]:
        """
        Determine if hedge needs rebalancing.

        Args:
            current_hedge_qty: Current SPY hedge quantity
            target_hedge_qty: Target SPY hedge quantity
            rebalance_threshold: Rebalance if drift > this percent

        Returns:
            Tuple of (adjustment_qty, should_rebalance)
        """
        if target_hedge_qty == 0:
            # Close hedge
            return -current_hedge_qty, True

        if current_hedge_qty == 0:
            # Open new hedge
            return target_hedge_qty, True

        # Check drift
        drift = abs(current_hedge_qty - target_hedge_qty) / abs(target_hedge_qty)

        if drift > rebalance_threshold:
            adjustment = target_hedge_qty - current_hedge_qty
            logger.info(
                f"Hedge rebalance needed: drift {drift:.2%}, adjust by {adjustment}"
            )
            return adjustment, True

        return 0, False

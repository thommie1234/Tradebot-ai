"""
Kelly Criterion position sizing with dynamic adjustment.
"""
from typing import Optional
import numpy as np

from optifire.core.logger import logger


class KellySizer:
    """
    Kelly Criterion position sizer with bounds and dynamic adjustment.
    """

    def __init__(
        self,
        min_multiplier: float = 0.25,
        max_multiplier: float = 1.5,
        default_multiplier: float = 0.5,
    ):
        """
        Initialize Kelly sizer.

        Args:
            min_multiplier: Minimum Kelly fraction
            max_multiplier: Maximum Kelly fraction
            default_multiplier: Default Kelly fraction
        """
        self.min_multiplier = min_multiplier
        self.max_multiplier = max_multiplier
        self.default_multiplier = default_multiplier

    def calculate(
        self,
        win_rate: float,
        avg_win: float,
        avg_loss: float,
        confidence: float = 1.0,
    ) -> float:
        """
        Calculate Kelly fraction.

        Args:
            win_rate: Probability of winning (0-1)
            avg_win: Average win amount
            avg_loss: Average loss amount (positive)
            confidence: Confidence in signal (0-1)

        Returns:
            Kelly fraction (bounded)
        """
        if win_rate <= 0 or win_rate >= 1:
            logger.warning(f"Invalid win_rate: {win_rate}, using default")
            return self.default_multiplier

        if avg_win <= 0 or avg_loss <= 0:
            logger.warning("Invalid avg_win or avg_loss, using default")
            return self.default_multiplier

        # Kelly formula: f = (p * b - q) / b
        # where p = win_rate, q = 1 - p, b = avg_win / avg_loss
        b = avg_win / avg_loss
        q = 1 - win_rate
        kelly_fraction = (win_rate * b - q) / b

        # Adjust for confidence
        kelly_fraction *= confidence

        # Bound the fraction
        kelly_fraction = np.clip(
            kelly_fraction,
            self.min_multiplier,
            self.max_multiplier,
        )

        return kelly_fraction

    def adjust_for_volatility(
        self,
        kelly_fraction: float,
        current_vol: float,
        target_vol: float,
    ) -> float:
        """
        Adjust Kelly fraction for volatility regime.

        Args:
            kelly_fraction: Base Kelly fraction
            current_vol: Current volatility
            target_vol: Target volatility

        Returns:
            Adjusted Kelly fraction
        """
        if current_vol <= 0 or target_vol <= 0:
            return kelly_fraction

        vol_ratio = target_vol / current_vol
        adjusted = kelly_fraction * vol_ratio

        return np.clip(adjusted, self.min_multiplier, self.max_multiplier)

    def adjust_for_drawdown(
        self,
        kelly_fraction: float,
        current_dd: float,
        max_dd_threshold: float = 0.05,
    ) -> float:
        """
        Reduce sizing during drawdown.

        Args:
            kelly_fraction: Base Kelly fraction
            current_dd: Current drawdown (0-1)
            max_dd_threshold: Threshold to start reducing

        Returns:
            Adjusted Kelly fraction
        """
        if current_dd <= 0:
            return kelly_fraction

        if current_dd >= max_dd_threshold:
            # Reduce exponentially
            reduction = np.exp(-5 * (current_dd - max_dd_threshold))
            adjusted = kelly_fraction * reduction
            return max(adjusted, self.min_multiplier)

        return kelly_fraction

"""
Value at Risk (VaR) and Conditional Value at Risk (CVaR) calculations.
"""
from typing import List, Optional, Tuple
import numpy as np
from scipy import stats

from optifire.core.logger import logger


class VaRCalculator:
    """
    Value at Risk and CVaR calculator.
    Supports historical, parametric, and Monte Carlo methods.
    """

    def __init__(self, confidence_level: float = 0.95):
        """
        Initialize VaR calculator.

        Args:
            confidence_level: Confidence level (e.g., 0.95 for 95%)
        """
        self.confidence_level = confidence_level

    def historical_var(
        self,
        returns: List[float],
        portfolio_value: float,
    ) -> float:
        """
        Calculate historical VaR.

        Args:
            returns: Historical returns
            portfolio_value: Current portfolio value

        Returns:
            VaR value (positive = loss)
        """
        if not returns or len(returns) < 10:
            logger.warning("Insufficient returns for VaR calculation")
            return 0.0

        returns_array = np.array(returns)
        percentile = (1 - self.confidence_level) * 100
        var_return = np.percentile(returns_array, percentile)

        # VaR is positive for losses
        var = -var_return * portfolio_value
        return max(var, 0.0)

    def parametric_var(
        self,
        mean_return: float,
        std_return: float,
        portfolio_value: float,
    ) -> float:
        """
        Calculate parametric VaR (assumes normal distribution).

        Args:
            mean_return: Mean return
            std_return: Standard deviation of returns
            portfolio_value: Current portfolio value

        Returns:
            VaR value (positive = loss)
        """
        if std_return <= 0:
            return 0.0

        z_score = stats.norm.ppf(1 - self.confidence_level)
        var_return = mean_return + z_score * std_return

        var = -var_return * portfolio_value
        return max(var, 0.0)

    def cvar(
        self,
        returns: List[float],
        portfolio_value: float,
    ) -> float:
        """
        Calculate Conditional VaR (Expected Shortfall).

        Args:
            returns: Historical returns
            portfolio_value: Current portfolio value

        Returns:
            CVaR value (positive = loss)
        """
        if not returns or len(returns) < 10:
            logger.warning("Insufficient returns for CVaR calculation")
            return 0.0

        returns_array = np.array(returns)
        percentile = (1 - self.confidence_level) * 100
        var_return = np.percentile(returns_array, percentile)

        # CVaR is the average of returns worse than VaR
        tail_returns = returns_array[returns_array <= var_return]

        if len(tail_returns) == 0:
            return 0.0

        cvar_return = np.mean(tail_returns)
        cvar = -cvar_return * portfolio_value

        return max(cvar, 0.0)

    def portfolio_var(
        self,
        positions: List[Tuple[float, float, float]],
        correlation_matrix: Optional[np.ndarray] = None,
    ) -> Tuple[float, float]:
        """
        Calculate portfolio VaR considering correlations.

        Args:
            positions: List of (value, mean_return, std_return) tuples
            correlation_matrix: Correlation matrix (optional)

        Returns:
            Tuple of (VaR, CVaR)
        """
        if not positions:
            return 0.0, 0.0

        n = len(positions)
        values = np.array([p[0] for p in positions])
        means = np.array([p[1] for p in positions])
        stds = np.array([p[2] for p in positions])

        # Portfolio mean and std
        portfolio_mean = np.sum(values * means)

        if correlation_matrix is None:
            # Assume independent
            portfolio_var_calc = np.sum((values * stds) ** 2)
        else:
            # Consider correlations
            cov_matrix = np.outer(stds, stds) * correlation_matrix
            portfolio_var_calc = values @ cov_matrix @ values

        portfolio_std = np.sqrt(portfolio_var_calc)
        portfolio_value = np.sum(values)

        # Calculate VaR
        var = self.parametric_var(
            portfolio_mean / portfolio_value,
            portfolio_std / portfolio_value,
            portfolio_value,
        )

        # Estimate CVaR (assuming normal distribution)
        z_score = stats.norm.ppf(1 - self.confidence_level)
        pdf_at_z = stats.norm.pdf(z_score)
        cvar_multiplier = pdf_at_z / (1 - self.confidence_level)
        cvar = var + (cvar_multiplier * portfolio_std)

        return var, cvar

    def check_var_breach(
        self,
        var: float,
        max_var: float,
    ) -> bool:
        """
        Check if VaR exceeds threshold.

        Args:
            var: Calculated VaR
            max_var: Maximum allowed VaR

        Returns:
            True if breached
        """
        return var > max_var

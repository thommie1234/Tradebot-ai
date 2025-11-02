"""
Position and exposure limits enforcement.
"""
from typing import Dict, List, Optional
from dataclasses import dataclass

from optifire.core.logger import logger
from optifire.core.errors import RiskError


@dataclass
class PositionLimits:
    """Position limits configuration."""

    max_exposure_total: float = 0.30  # 30% of portfolio
    max_exposure_symbol: float = 0.10  # 10% per symbol
    max_sector_exposure: float = 0.25  # 25% per sector
    max_leverage: float = 1.0  # No leverage by default
    max_concentration_top5: float = 0.40  # Top 5 positions ≤ 40%


class LimitsEnforcer:
    """
    Enforce position and exposure limits.
    Fail-closed: reject on any breach.
    """

    def __init__(self, limits: Optional[PositionLimits] = None):
        """
        Initialize limits enforcer.

        Args:
            limits: Position limits configuration
        """
        self.limits = limits or PositionLimits()

    def check_new_position(
        self,
        symbol: str,
        proposed_value: float,
        portfolio_value: float,
        current_positions: Dict[str, float],
        sector: Optional[str] = None,
        sector_map: Optional[Dict[str, str]] = None,
    ) -> bool:
        """
        Check if new position violates limits.

        Args:
            symbol: Symbol to trade
            proposed_value: Proposed position value
            portfolio_value: Total portfolio value
            current_positions: Dict of symbol -> position value
            sector: Symbol's sector
            sector_map: Dict of symbol -> sector

        Returns:
            True if allowed, False if rejected

        Raises:
            RiskError: If limit is breached
        """
        # Check symbol exposure
        current_symbol_value = current_positions.get(symbol, 0.0)
        new_symbol_value = current_symbol_value + proposed_value
        symbol_exposure = abs(new_symbol_value) / portfolio_value

        if symbol_exposure > self.limits.max_exposure_symbol:
            raise RiskError(
                f"Symbol exposure limit breach: {symbol} would be "
                f"{symbol_exposure:.2%} > {self.limits.max_exposure_symbol:.2%}"
            )

        # Check total exposure
        total_exposure = sum(abs(v) for v in current_positions.values())
        total_exposure += abs(proposed_value)
        total_exposure_pct = total_exposure / portfolio_value

        if total_exposure_pct > self.limits.max_exposure_total:
            raise RiskError(
                f"Total exposure limit breach: would be "
                f"{total_exposure_pct:.2%} > {self.limits.max_exposure_total:.2%}"
            )

        # Check sector exposure
        if sector and sector_map:
            sector_exposure = self._calculate_sector_exposure(
                sector,
                current_positions,
                sector_map,
                portfolio_value,
            )
            sector_exposure += abs(proposed_value) / portfolio_value

            if sector_exposure > self.limits.max_sector_exposure:
                raise RiskError(
                    f"Sector exposure limit breach: {sector} would be "
                    f"{sector_exposure:.2%} > {self.limits.max_sector_exposure:.2%}"
                )

        # Check concentration
        new_positions = current_positions.copy()
        new_positions[symbol] = new_positions.get(symbol, 0.0) + proposed_value

        concentration = self._calculate_concentration(new_positions, portfolio_value)

        if concentration > self.limits.max_concentration_top5:
            raise RiskError(
                f"Concentration limit breach: top 5 would be "
                f"{concentration:.2%} > {self.limits.max_concentration_top5:.2%}"
            )

        logger.debug(f"Position check passed for {symbol}")
        return True

    def check_leverage(
        self,
        total_position_value: float,
        portfolio_value: float,
    ) -> bool:
        """
        Check leverage limits.

        Args:
            total_position_value: Sum of absolute position values
            portfolio_value: Portfolio value

        Returns:
            True if within limits

        Raises:
            RiskError: If leverage exceeded
        """
        leverage = total_position_value / portfolio_value

        if leverage > self.limits.max_leverage:
            raise RiskError(
                f"Leverage limit breach: {leverage:.2f}x > "
                f"{self.limits.max_leverage:.2f}x"
            )

        return True

    def _calculate_sector_exposure(
        self,
        sector: str,
        positions: Dict[str, float],
        sector_map: Dict[str, str],
        portfolio_value: float,
    ) -> float:
        """Calculate exposure to a sector."""
        sector_value = sum(
            abs(value)
            for symbol, value in positions.items()
            if sector_map.get(symbol) == sector
        )
        return sector_value / portfolio_value

    def _calculate_concentration(
        self,
        positions: Dict[str, float],
        portfolio_value: float,
    ) -> float:
        """Calculate concentration of top 5 positions."""
        if not positions:
            return 0.0

        sorted_positions = sorted(
            positions.values(),
            key=lambda x: abs(x),
            reverse=True,
        )

        top5_value = sum(abs(v) for v in sorted_positions[:5])
        return top5_value / portfolio_value

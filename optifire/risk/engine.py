"""
Central risk engine coordinating all risk checks.
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

from optifire.core.logger import logger
from optifire.core.errors import RiskError
from .kelly import KellySizer
from .var_cvar import VaRCalculator
from .limits import LimitsEnforcer, PositionLimits
from .hedger import BetaHedger


@dataclass
class RiskContext:
    """Risk context for decision making."""

    portfolio_value: float
    buying_power: float
    settled_cash: float
    positions: Dict[str, float]
    returns_history: List[float]
    current_drawdown: float
    losing_days_streak: int
    betas: Optional[Dict[str, float]] = None
    sector_map: Optional[Dict[str, str]] = None


@dataclass
class RiskDecision:
    """Risk decision output."""

    approved: bool
    reason: str
    max_position_size: Optional[float] = None
    kelly_fraction: Optional[float] = None
    var: Optional[float] = None
    cvar: Optional[float] = None


class RiskEngine:
    """
    Central risk engine with fail-closed approach.
    Coordinates Kelly sizing, VaR, limits, and hedging.
    """

    def __init__(self, config: Dict):
        """
        Initialize risk engine.

        Args:
            config: Risk configuration
        """
        self.config = config

        # Initialize components
        self.kelly_sizer = KellySizer(
            min_multiplier=config.get("kelly_min", 0.25),
            max_multiplier=config.get("kelly_max", 1.5),
        )

        self.var_calculator = VaRCalculator(
            confidence_level=config.get("var_confidence", 0.95),
        )

        limits = PositionLimits(
            max_exposure_total=config.get("max_exposure_total", 0.30),
            max_exposure_symbol=config.get("max_exposure_symbol", 0.10),
        )
        self.limits_enforcer = LimitsEnforcer(limits)

        self.beta_hedger = BetaHedger(
            beta_threshold=config.get("beta_hedge_threshold", 0.6),
        )

        # Risk thresholds
        self.max_drawdown = config.get("max_drawdown", 0.08)
        self.max_losing_streak = config.get("max_losing_streak", 3)
        self.max_var_pct = config.get("max_var_pct", 0.05)
        self.cooldown_hours = config.get("cooldown_hours", 24)

        # State
        self._in_cooldown = False
        self._cooldown_until: Optional[datetime] = None

    def evaluate_trade(
        self,
        symbol: str,
        proposed_value: float,
        signal_confidence: float,
        context: RiskContext,
        sector: Optional[str] = None,
    ) -> RiskDecision:
        """
        Evaluate if a trade should be allowed.

        Args:
            symbol: Symbol to trade
            proposed_value: Proposed position value
            signal_confidence: Signal confidence (0-1)
            context: Risk context
            sector: Symbol's sector

        Returns:
            RiskDecision with approval and reasoning
        """
        # FAIL-CLOSED: Check cooldown
        if self._in_cooldown:
            if datetime.utcnow() < self._cooldown_until:
                return RiskDecision(
                    approved=False,
                    reason=f"In cooldown until {self._cooldown_until.isoformat()}",
                )
            else:
                self._in_cooldown = False
                self._cooldown_until = None

        # FAIL-CLOSED: Check drawdown
        if context.current_drawdown >= self.max_drawdown:
            self._enter_cooldown()
            return RiskDecision(
                approved=False,
                reason=f"Drawdown {context.current_drawdown:.2%} >= "
                f"{self.max_drawdown:.2%}, entering cooldown",
            )

        # FAIL-CLOSED: Check losing streak
        if context.losing_days_streak >= self.max_losing_streak:
            self._enter_cooldown()
            return RiskDecision(
                approved=False,
                reason=f"Losing streak {context.losing_days_streak} days, "
                f"entering cooldown",
            )

        # FAIL-CLOSED: Check buying power
        if proposed_value > 0 and proposed_value > context.buying_power:
            return RiskDecision(
                approved=False,
                reason=f"Insufficient buying power: need ${proposed_value:.2f}, "
                f"have ${context.buying_power:.2f}",
            )

        # Calculate VaR and CVaR
        var = self.var_calculator.historical_var(
            context.returns_history,
            context.portfolio_value,
        )
        cvar = self.var_calculator.cvar(
            context.returns_history,
            context.portfolio_value,
        )

        # FAIL-CLOSED: Check VaR limit
        max_var = context.portfolio_value * self.max_var_pct
        if var > max_var:
            return RiskDecision(
                approved=False,
                reason=f"VaR ${var:.2f} > max ${max_var:.2f}",
                var=var,
                cvar=cvar,
            )

        # FAIL-CLOSED: Check position limits
        try:
            self.limits_enforcer.check_new_position(
                symbol=symbol,
                proposed_value=proposed_value,
                portfolio_value=context.portfolio_value,
                current_positions=context.positions,
                sector=sector,
                sector_map=context.sector_map,
            )
        except RiskError as e:
            return RiskDecision(
                approved=False,
                reason=str(e),
                var=var,
                cvar=cvar,
            )

        # Calculate Kelly-based position size
        # Placeholder: using default confidence-adjusted sizing
        kelly_fraction = self.kelly_sizer.calculate(
            win_rate=0.52,  # Would come from backtest/stats
            avg_win=0.015,
            avg_loss=0.010,
            confidence=signal_confidence,
        )

        # Adjust for drawdown
        kelly_fraction = self.kelly_sizer.adjust_for_drawdown(
            kelly_fraction,
            context.current_drawdown,
        )

        # Calculate max position size
        max_position_size = context.portfolio_value * kelly_fraction

        # Ensure proposed value doesn't exceed Kelly size
        if abs(proposed_value) > max_position_size:
            logger.warning(
                f"Proposed value ${proposed_value:.2f} > Kelly size "
                f"${max_position_size:.2f}, capping"
            )
            proposed_value = max_position_size if proposed_value > 0 else -max_position_size

        logger.info(
            f"Trade approved: {symbol} ${proposed_value:.2f} "
            f"(Kelly: {kelly_fraction:.2%}, VaR: ${var:.2f})"
        )

        return RiskDecision(
            approved=True,
            reason="All risk checks passed",
            max_position_size=max_position_size,
            kelly_fraction=kelly_fraction,
            var=var,
            cvar=cvar,
        )

    def should_hedge(
        self,
        context: RiskContext,
        spy_price: float,
    ) -> Tuple[int, str]:
        """
        Determine if portfolio should be hedged.

        Args:
            context: Risk context
            spy_price: Current SPY price

        Returns:
            Tuple of (hedge_quantity, reason)
        """
        if not context.betas:
            return 0, "no_beta_data"

        portfolio_beta = self.beta_hedger.calculate_portfolio_beta(
            context.positions,
            context.betas,
            context.portfolio_value,
        )

        return self.beta_hedger.calculate_hedge(
            context.portfolio_value,
            portfolio_beta,
            spy_price,
        )

    def _enter_cooldown(self) -> None:
        """Enter risk cooldown period."""
        self._in_cooldown = True
        self._cooldown_until = datetime.utcnow() + timedelta(hours=self.cooldown_hours)
        logger.warning(f"Entering risk cooldown until {self._cooldown_until.isoformat()}")

    def get_risk_metrics(self, context: RiskContext) -> Dict:
        """
        Get current risk metrics.

        Args:
            context: Risk context

        Returns:
            Dictionary of risk metrics
        """
        var = self.var_calculator.historical_var(
            context.returns_history,
            context.portfolio_value,
        )
        cvar = self.var_calculator.cvar(
            context.returns_history,
            context.portfolio_value,
        )

        total_exposure = sum(abs(v) for v in context.positions.values())
        exposure_pct = total_exposure / context.portfolio_value if context.portfolio_value > 0 else 0

        portfolio_beta = 0.0
        if context.betas:
            portfolio_beta = self.beta_hedger.calculate_portfolio_beta(
                context.positions,
                context.betas,
                context.portfolio_value,
            )

        return {
            "var_95": var,
            "cvar_95": cvar,
            "exposure_pct": exposure_pct,
            "portfolio_beta": portfolio_beta,
            "drawdown": context.current_drawdown,
            "losing_streak": context.losing_days_streak,
            "in_cooldown": self._in_cooldown,
            "cooldown_until": self._cooldown_until.isoformat() if self._cooldown_until else None,
        }

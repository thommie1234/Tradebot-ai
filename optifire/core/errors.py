"""
Custom exception classes for OptiFIRE.
"""


class OptiFIREError(Exception):
    """Base exception for all OptiFIRE errors."""
    pass


class ConfigError(OptiFIREError):
    """Configuration-related errors."""
    pass


class RiskError(OptiFIREError):
    """Risk management errors - fail-closed."""
    pass


class ExecutionError(OptiFIREError):
    """Order execution errors."""
    pass


class DataError(OptiFIREError):
    """Data feed or processing errors."""
    pass


class PluginError(OptiFIREError):
    """Plugin loading or execution errors."""
    pass


class ResourceBudgetExceeded(OptiFIREError):
    """Plugin exceeded CPU or memory budget."""
    pass


class AuthenticationError(OptiFIREError):
    """Authentication or authorization errors."""
    pass


class ValidationError(OptiFIREError):
    """Data validation errors."""
    pass

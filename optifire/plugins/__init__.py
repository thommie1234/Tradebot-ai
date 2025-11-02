"""
Plugin architecture for OptiFIRE.
All 75 plugin modules with unified interface.
"""
from typing import Dict, Any, Optional, Protocol
from dataclasses import dataclass
from abc import ABC, abstractmethod
import time
import psutil

from optifire.core.logger import logger
from optifire.core.errors import PluginError, ResourceBudgetExceeded


@dataclass
class PluginMetadata:
    """Plugin metadata."""

    plugin_id: str
    name: str
    category: str  # alpha, fe, risk, ml, ai, exec, ux, diag, infra
    version: str
    author: str
    description: str
    inputs: list[str]
    outputs: list[str]
    est_cpu_ms: int
    est_mem_mb: int


@dataclass
class PluginContext:
    """Runtime context passed to plugins."""

    config: Dict[str, Any]
    db: Any  # Database instance
    bus: Any  # Event bus instance
    data: Dict[str, Any]  # Shared data


@dataclass
class PluginResult:
    """Plugin execution result."""

    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    cpu_ms: int = 0
    mem_mb: int = 0


class Plugin(ABC):
    """
    Base plugin interface.
    All plugins must implement this interface.
    """

    def __init__(self):
        """Initialize plugin."""
        self.metadata = self.describe()

    @abstractmethod
    def describe(self) -> PluginMetadata:
        """
        Describe plugin capabilities and requirements.

        Returns:
            Plugin metadata
        """
        pass

    @abstractmethod
    def plan(self) -> Dict[str, Any]:
        """
        Define execution plan.

        Returns:
            Dictionary with 'schedule', 'triggers', etc.
        """
        pass

    @abstractmethod
    async def run(self, context: PluginContext) -> PluginResult:
        """
        Execute plugin logic.

        Args:
            context: Runtime context

        Returns:
            Plugin result
        """
        pass

    async def execute_with_budget(
        self,
        context: PluginContext,
        cpu_budget_ms: int,
        mem_budget_mb: int,
    ) -> PluginResult:
        """
        Execute with resource budget enforcement.

        Args:
            context: Runtime context
            cpu_budget_ms: CPU time budget in milliseconds
            mem_budget_mb: Memory budget in MB

        Returns:
            Plugin result

        Raises:
            ResourceBudgetExceeded: If budget exceeded
        """
        process = psutil.Process()
        mem_before = process.memory_info().rss / 1024 / 1024  # MB
        start_time = time.perf_counter()

        try:
            result = await self.run(context)

            # Measure actual usage
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            mem_after = process.memory_info().rss / 1024 / 1024
            mem_used = mem_after - mem_before

            # Check budgets
            if elapsed_ms > cpu_budget_ms:
                logger.warning(
                    f"{self.metadata.plugin_id} exceeded CPU budget: "
                    f"{elapsed_ms}ms > {cpu_budget_ms}ms"
                )

            if mem_used > mem_budget_mb:
                logger.warning(
                    f"{self.metadata.plugin_id} exceeded memory budget: "
                    f"{mem_used:.1f}MB > {mem_budget_mb}MB"
                )

            result.cpu_ms = elapsed_ms
            result.mem_mb = int(mem_used)

            return result

        except Exception as e:
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            logger.error(f"{self.metadata.plugin_id} failed: {e}", exc_info=True)

            return PluginResult(
                success=False,
                error=str(e),
                cpu_ms=elapsed_ms,
                mem_mb=0,
            )


class PluginRegistry:
    """Registry for all plugins."""

    def __init__(self):
        """Initialize registry."""
        self._plugins: Dict[str, Plugin] = {}

    def register(self, plugin: Plugin) -> None:
        """Register a plugin."""
        plugin_id = plugin.metadata.plugin_id
        self._plugins[plugin_id] = plugin
        logger.info(f"Registered plugin: {plugin_id}")

    def get(self, plugin_id: str) -> Optional[Plugin]:
        """Get a plugin by ID."""
        return self._plugins.get(plugin_id)

    def list_all(self) -> list[str]:
        """List all registered plugin IDs."""
        return list(self._plugins.keys())

    def list_by_category(self, category: str) -> list[str]:
        """List plugins by category."""
        return [
            pid
            for pid, plugin in self._plugins.items()
            if plugin.metadata.category == category
        ]


# Global registry instance
registry = PluginRegistry()

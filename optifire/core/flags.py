"""
Feature flags registry with hot-reload support.
"""
import asyncio
from pathlib import Path
from typing import Any, Dict, Optional
import yaml

from .errors import ConfigError
from .logger import logger


class FeatureFlags:
    """
    Feature flags manager for plugin control.
    Supports hot-reload and runtime toggles.
    """

    def __init__(self, flags_path: Path):
        """
        Initialize feature flags manager.

        Args:
            flags_path: Path to features.yaml
        """
        self.flags_path = flags_path
        self._flags: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
        self._version = 0
        self.load()

    def load(self) -> None:
        """Load feature flags from YAML file."""
        try:
            with open(self.flags_path, "r") as f:
                data = yaml.safe_load(f) or {}
                self._flags = data.get("plugins", {})
            self._version += 1
            enabled_count = sum(1 for f in self._flags.values() if f.get("enabled", False))
            logger.info(
                f"Loaded {len(self._flags)} feature flags "
                f"({enabled_count} enabled) v{self._version}"
            )
        except FileNotFoundError:
            logger.warning(f"Feature flags file not found: {self.flags_path}")
            self._flags = {}
        except yaml.YAMLError as e:
            raise ConfigError(f"Invalid YAML in feature flags: {e}")

    async def reload(self) -> None:
        """Reload feature flags (hot-reload)."""
        async with self._lock:
            old_version = self._version
            self.load()
            if self._version > old_version:
                logger.info(f"Hot-reloaded feature flags to v{self._version}")

    async def toggle(self, plugin_id: str, enabled: bool) -> None:
        """
        Toggle a feature flag.

        Args:
            plugin_id: Plugin identifier
            enabled: Enable or disable
        """
        async with self._lock:
            if plugin_id not in self._flags:
                raise ConfigError(f"Unknown plugin: {plugin_id}")

            self._flags[plugin_id]["enabled"] = enabled
            self._version += 1
            logger.info(
                f"Toggled {plugin_id}: {'ENABLED' if enabled else 'DISABLED'} "
                f"(v{self._version})"
            )

    async def bulk_update(self, updates: Dict[str, Dict[str, Any]]) -> None:
        """
        Bulk update feature flags.

        Args:
            updates: Dictionary of plugin_id -> updates
        """
        async with self._lock:
            for plugin_id, update_data in updates.items():
                if plugin_id in self._flags:
                    self._flags[plugin_id].update(update_data)

            self._version += 1
            logger.info(f"Bulk updated {len(updates)} flags (v{self._version})")

    def is_enabled(self, plugin_id: str) -> bool:
        """
        Check if a plugin is enabled.

        Args:
            plugin_id: Plugin identifier

        Returns:
            True if enabled, False otherwise
        """
        return self._flags.get(plugin_id, {}).get("enabled", False)

    def get_config(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """
        Get plugin configuration.

        Args:
            plugin_id: Plugin identifier

        Returns:
            Plugin configuration dictionary or None
        """
        return self._flags.get(plugin_id)

    def get_enabled_plugins(self) -> list[str]:
        """Get list of enabled plugin IDs."""
        return [
            plugin_id
            for plugin_id, config in self._flags.items()
            if config.get("enabled", False)
        ]

    def get_all_plugins(self) -> list[str]:
        """Get list of all plugin IDs."""
        return list(self._flags.keys())

    def get_budget(self, plugin_id: str) -> Dict[str, int]:
        """
        Get resource budget for a plugin.

        Args:
            plugin_id: Plugin identifier

        Returns:
            Budget dictionary with cpu_ms and mem_mb
        """
        config = self.get_config(plugin_id)
        if not config:
            return {"cpu_ms": 1000, "mem_mb": 50}  # Defaults

        budget = config.get("budget", {})
        return {
            "cpu_ms": budget.get("cpu_ms", 1000),
            "mem_mb": budget.get("mem_mb", 50),
        }

    def get_schedule(self, plugin_id: str) -> Optional[str]:
        """
        Get schedule for a plugin.

        Args:
            plugin_id: Plugin identifier

        Returns:
            Schedule string (cron, @idle, @open, @close) or None
        """
        config = self.get_config(plugin_id)
        return config.get("schedule") if config else None

    def get_all_flags(self) -> Dict[str, Dict[str, Any]]:
        """Get all feature flags."""
        return self._flags.copy()

    def get_version(self) -> int:
        """Get current flags version."""
        return self._version

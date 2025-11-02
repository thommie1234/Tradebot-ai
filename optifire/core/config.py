"""
Configuration management with hot-reload support.
"""
import asyncio
from pathlib import Path
from typing import Any, Dict, Optional
import yaml
from datetime import datetime

from .errors import ConfigError
from .logger import logger


class Config:
    """
    Configuration manager with hot-reload capability.
    Thread-safe using asyncio locks.
    """

    def __init__(self, config_path: Path):
        """
        Initialize configuration manager.

        Args:
            config_path: Path to config.yaml
        """
        self.config_path = config_path
        self._config: Dict[str, Any] = {}
        self._lock = asyncio.Lock()
        self._version = 0
        self._history: list[Dict[str, Any]] = []
        self.load()

    def load(self) -> None:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, "r") as f:
                self._config = yaml.safe_load(f) or {}
            self._version += 1
            logger.info(f"Loaded config v{self._version} from {self.config_path}")
        except FileNotFoundError:
            logger.warning(f"Config file not found: {self.config_path}")
            self._config = self._get_defaults()
        except yaml.YAMLError as e:
            raise ConfigError(f"Invalid YAML in config: {e}")

    async def reload(self) -> None:
        """Reload configuration (hot-reload)."""
        async with self._lock:
            # Save current config to history
            self._history.append({
                "version": self._version,
                "timestamp": datetime.utcnow().isoformat(),
                "config": self._config.copy(),
            })
            # Keep last 10 versions
            if len(self._history) > 10:
                self._history.pop(0)

            self.load()
            logger.info(f"Hot-reloaded config to v{self._version}")

    async def update_runtime(self, updates: Dict[str, Any]) -> None:
        """
        Update runtime configuration.

        Args:
            updates: Dictionary of config updates
        """
        async with self._lock:
            # Save to history
            self._history.append({
                "version": self._version,
                "timestamp": datetime.utcnow().isoformat(),
                "config": self._config.copy(),
            })
            if len(self._history) > 10:
                self._history.pop(0)

            # Apply updates
            self._deep_update(self._config, updates)
            self._version += 1
            logger.info(f"Updated runtime config to v{self._version}")

    async def rollback(self, version: Optional[int] = None) -> None:
        """
        Rollback to a previous configuration version.

        Args:
            version: Target version (defaults to previous)
        """
        async with self._lock:
            if not self._history:
                raise ConfigError("No history available for rollback")

            if version is None:
                # Rollback to previous
                previous = self._history.pop()
            else:
                # Find specific version
                previous = next(
                    (h for h in reversed(self._history) if h["version"] == version),
                    None,
                )
                if not previous:
                    raise ConfigError(f"Version {version} not found in history")
                # Remove newer versions
                self._history = [h for h in self._history if h["version"] <= version]

            self._config = previous["config"]
            self._version = previous["version"]
            logger.info(f"Rolled back config to v{self._version}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation key.

        Args:
            key: Configuration key (e.g., "risk.max_exposure")
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value

    def get_all(self) -> Dict[str, Any]:
        """Get entire configuration dictionary."""
        return self._config.copy()

    def get_version(self) -> int:
        """Get current configuration version."""
        return self._version

    def get_history(self) -> list[Dict[str, Any]]:
        """Get configuration history."""
        return self._history.copy()

    @staticmethod
    def _deep_update(base: Dict, updates: Dict) -> None:
        """Deep update dictionary in-place."""
        for key, value in updates.items():
            if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                Config._deep_update(base[key], value)
            else:
                base[key] = value

    @staticmethod
    def _get_defaults() -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "system": {
                "max_workers": 3,
                "max_ram_mb": 900,
                "max_cpu_percent": 90,
            },
            "risk": {
                "max_exposure_total": 0.30,
                "max_exposure_symbol": 0.10,
                "max_drawdown": 0.08,
                "kelly_min": 0.25,
                "kelly_max": 1.5,
                "beta_hedge_threshold": 0.6,
            },
            "execution": {
                "batch_window_seconds": 1,
                "rth_only": True,
                "max_slippage_bps": 10,
            },
            "api": {
                "host": "0.0.0.0",
                "port": 8000,
                "jwt_expiry_hours": 24,
            },
            "openai": {
                "max_concurrent": 1,
                "timeout_seconds": 15,
                "cache_dir": "data/openai_cache",
            },
        }

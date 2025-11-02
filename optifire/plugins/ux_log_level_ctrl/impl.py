"""
ux_log_level_ctrl - Dynamic log level control.
FULL IMPLEMENTATION
"""
from typing import Dict, Any
import logging
from optifire.plugins import Plugin, PluginMetadata, PluginContext, PluginResult
from optifire.core.logger import logger


class UxLogLevelCtrl(Plugin):
    """
    Dynamic log level control.

    Change logging verbosity without restart.
    """

    def describe(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="ux_log_level_ctrl",
            name="Log Level Control",
            category="ux",
            version="1.0.0",
            author="OptiFIRE",
            description="Dynamic log level adjustment",
            inputs=['level'],
            outputs=['current_level'],
            est_cpu_ms=50,
            est_mem_mb=5,
        )

    def plan(self) -> Dict[str, Any]:
        return {
            "schedule": "@manual",
            "triggers": ["log_level_change"],
            "dependencies": [],
        }

    async def run(self, context: PluginContext) -> PluginResult:
        """Change log level."""
        try:
            level = context.params.get("level", None)

            if level:
                # Convert string to log level
                level_map = {
                    "debug": logging.DEBUG,
                    "info": logging.INFO,
                    "warning": logging.WARNING,
                    "error": logging.ERROR,
                    "critical": logging.CRITICAL,
                }

                level_int = level_map.get(level.lower(), logging.INFO)
                logger.setLevel(level_int)

                result_data = {
                    "level": level.upper(),
                    "interpretation": f"✅ Log level set to {level.upper()}",
                }
            else:
                # Get current level
                current_level_int = logger.level
                level_names = {
                    logging.DEBUG: "DEBUG",
                    logging.INFO: "INFO",
                    logging.WARNING: "WARNING",
                    logging.ERROR: "ERROR",
                    logging.CRITICAL: "CRITICAL",
                }
                current_level = level_names.get(current_level_int, "UNKNOWN")

                result_data = {
                    "level": current_level,
                    "interpretation": f"Current log level: {current_level}",
                }

            return PluginResult(success=True, data=result_data)

        except Exception as e:
            logger.error(f"Error in log level control: {e}", exc_info=True)
            return PluginResult(success=False, error=str(e))

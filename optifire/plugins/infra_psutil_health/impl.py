"""
infra_psutil_health - System health monitoring.
FULL IMPLEMENTATION
"""
from typing import Dict, Any
import psutil
from optifire.plugins import Plugin, PluginMetadata, PluginContext, PluginResult
from optifire.core.logger import logger


class InfraPsutilHealth(Plugin):
    """
    System health monitoring.

    Monitors:
    - CPU usage
    - Memory usage
    - Thread count
    - Disk space
    """

    def describe(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="infra_psutil_health",
            name="System Health Monitor",
            category="infrastructure",
            version="1.0.0",
            author="OptiFIRE",
            description="CPU, RAM, disk monitoring via psutil",
            inputs=[],
            outputs=['cpu_pct', 'memory_pct', 'status'],
            est_cpu_ms=100,
            est_mem_mb=10,
        )

    def plan(self) -> Dict[str, Any]:
        return {
            "schedule": "@continuous",
            "triggers": ["every_minute"],
            "dependencies": [],
        }

    async def run(self, context: PluginContext) -> PluginResult:
        """Check system health."""
        try:
            # CPU usage
            cpu_pct = psutil.cpu_percent(interval=0.1)

            # Memory usage
            memory = psutil.virtual_memory()
            memory_pct = memory.percent

            # Thread count
            process = psutil.Process()
            thread_count = process.num_threads()

            # Disk usage
            disk = psutil.disk_usage('/')
            disk_pct = disk.percent

            # Health status
            status = "healthy"
            warnings = []

            if cpu_pct > 80:
                warnings.append("High CPU")
                status = "warning"
            if memory_pct > 85:
                warnings.append("High memory")
                status = "warning"
            if disk_pct > 90:
                warnings.append("Low disk space")
                status = "critical"

            result_data = {
                "cpu_pct": cpu_pct,
                "memory_pct": memory_pct,
                "thread_count": thread_count,
                "disk_pct": disk_pct,
                "status": status,
                "warnings": warnings,
                "interpretation": f"{'✅' if status == 'healthy' else '⚠️'} {status.upper()}: CPU {cpu_pct:.1f}%, RAM {memory_pct:.1f}%",
            }

            if context.bus:
                await context.bus.publish(
                    "system_health_update",
                    result_data,
                    source="infra_psutil_health",
                )

            return PluginResult(success=True, data=result_data)

        except Exception as e:
            logger.error(f"Error in health monitor: {e}", exc_info=True)
            return PluginResult(success=False, error=str(e))

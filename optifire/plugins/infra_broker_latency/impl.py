"""
infra_broker_latency - Broker API latency monitoring.
FULL IMPLEMENTATION
"""
from typing import Dict, Any
import time
from optifire.plugins import Plugin, PluginMetadata, PluginContext, PluginResult
from optifire.core.logger import logger


class InfraBrokerLatency(Plugin):
    """
    Broker API latency monitoring.

    Tracks round-trip time for API calls.
    Detects performance degradation.
    """

    def __init__(self):
        super().__init__()
        self.latency_history = []
        self.window_size = 100

    def describe(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="infra_broker_latency",
            name="Broker Latency Monitor",
            category="infrastructure",
            version="1.0.0",
            author="OptiFIRE",
            description="Track API round-trip time",
            inputs=['latency_ms'],
            outputs=['avg_latency', 'p95_latency'],
            est_cpu_ms=50,
            est_mem_mb=5,
        )

    def plan(self) -> Dict[str, Any]:
        return {
            "schedule": "@continuous",
            "triggers": ["api_call"],
            "dependencies": [],
        }

    async def run(self, context: PluginContext) -> PluginResult:
        """Track broker latency."""
        try:
            latency_ms = params.get("latency_ms", None)

            if latency_ms is not None:
                self.latency_history.append(latency_ms)

                # Keep only recent window
                if len(self.latency_history) > self.window_size:
                    self.latency_history.pop(0)

            # Calculate metrics
            if self.latency_history:
                avg_latency = sum(self.latency_history) / len(self.latency_history)
                sorted_latency = sorted(self.latency_history)
                p95_idx = int(len(sorted_latency) * 0.95)
                p95_latency = sorted_latency[p95_idx] if p95_idx < len(sorted_latency) else avg_latency
            else:
                avg_latency = 0.0
                p95_latency = 0.0

            # Status
            status = "healthy"
            if avg_latency > 1000:  # 1 second
                status = "slow"
            elif avg_latency > 500:  # 500ms
                status = "warning"

            result_data = {
                "avg_latency_ms": avg_latency,
                "p95_latency_ms": p95_latency,
                "n_samples": len(self.latency_history),
                "status": status,
                "interpretation": f"{'✅' if status == 'healthy' else '⚠️'} Avg: {avg_latency:.0f}ms, P95: {p95_latency:.0f}ms",
            }

            if context.bus:
                await context.bus.publish(
                    "broker_latency_update",
                    result_data,
                    source="infra_broker_latency",
                )

            return PluginResult(success=True, data=result_data)

        except Exception as e:
            logger.error(f"Error in latency monitor: {e}", exc_info=True)
            return PluginResult(success=False, error=str(e))

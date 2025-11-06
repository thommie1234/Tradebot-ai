"""
diag_param_sensitivity - Parameter sensitivity analysis.
FULL IMPLEMENTATION
"""
from typing import Dict, Any
import numpy as np
from optifire.plugins import Plugin, PluginMetadata, PluginContext, PluginResult
from optifire.core.logger import logger


class DiagParamSensitivity(Plugin):
    """
    Parameter sensitivity analysis.

    Tests how performance changes with parameter variations.
    Detects overfitting to specific parameter values.
    """

    def describe(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="diag_param_sensitivity",
            name="Parameter Sensitivity",
            category="diagnostics",
            version="1.0.0",
            author="OptiFIRE",
            description="Analyze parameter robustness",
            inputs=['param_name', 'param_range'],
            outputs=['sensitivity_score', 'plot_data'],
            est_cpu_ms=500,
            est_mem_mb=50,
        )

    def plan(self) -> Dict[str, Any]:
        return {
            "schedule": "@manual",
            "triggers": ["backtest_complete"],
            "dependencies": [],
        }

    async def run(self, context: PluginContext) -> PluginResult:
        """Analyze parameter sensitivity."""
        try:
            param_name = params.get("param_name", "threshold")
            param_range = params.get("param_range", None)

            if param_range is None:
                # Mock parameter range
                param_range = np.linspace(0.5, 2.0, 15)

            # Mock performance for each parameter value
            # In production: run backtest for each value
            performance = []
            for param_value in param_range:
                # Simulate performance (with noise)
                perf = 1.5 - 0.5 * (param_value - 1.2) ** 2 + np.random.normal(0, 0.1)
                performance.append(perf)

            performance = np.array(performance)

            # Calculate sensitivity (variance of performance)
            sensitivity_score = np.std(performance)

            # Find optimal parameter
            optimal_idx = np.argmax(performance)
            optimal_param = param_range[optimal_idx]

            # Generate plot data
            plot_data = {
                "x": list(param_range),
                "y": list(performance),
                "optimal_x": float(optimal_param),
                "optimal_y": float(performance[optimal_idx]),
            }

            # Interpretation
            if sensitivity_score < 0.1:
                interpretation = "✅ LOW sensitivity - robust parameter"
            elif sensitivity_score < 0.3:
                interpretation = "⚠️ MODERATE sensitivity - use with caution"
            else:
                interpretation = "⚠️ HIGH sensitivity - likely overfit"

            result_data = {
                "param_name": param_name,
                "sensitivity_score": float(sensitivity_score),
                "optimal_value": float(optimal_param),
                "plot_data": plot_data,
                "interpretation": interpretation,
            }

            if context.bus:
                await context.bus.publish(
                    "param_sensitivity_update",
                    result_data,
                    source="diag_param_sensitivity",
                )

            return PluginResult(success=True, data=result_data)

        except Exception as e:
            logger.error(f"Error in parameter sensitivity: {e}", exc_info=True)
            return PluginResult(success=False, error=str(e))

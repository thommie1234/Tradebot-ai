"""
System health monitoring.
"""
import psutil
from typing import Dict
from datetime import datetime

from optifire.core.logger import logger


class HealthMonitor:
    """System health monitoring."""
    
    def __init__(self):
        """Initialize health monitor."""
        self.process = psutil.Process()
        self.start_time = datetime.utcnow()
    
    def get_metrics(self) -> Dict:
        """Get current health metrics."""
        try:
            cpu_percent = self.process.cpu_percent(interval=0.1)
            memory_info = self.process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            
            # System-wide
            system_cpu = psutil.cpu_percent(interval=0.1)
            system_memory = psutil.virtual_memory()
            
            uptime = (datetime.utcnow() - self.start_time).total_seconds()
            
            return {
                "process": {
                    "cpu_percent": round(cpu_percent, 2),
                    "memory_mb": round(memory_mb, 2),
                    "num_threads": self.process.num_threads(),
                    "num_fds": self.process.num_fds() if hasattr(self.process, 'num_fds') else 0,
                },
                "system": {
                    "cpu_percent": round(system_cpu, 2),
                    "memory_percent": round(system_memory.percent, 2),
                    "memory_available_mb": round(system_memory.available / 1024 / 1024, 2),
                },
                "uptime_seconds": int(uptime),
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error getting health metrics: {e}")
            return {}
    
    def check_thresholds(self, max_cpu: float = 90, max_memory_mb: float = 900) -> Dict:
        """Check if metrics exceed thresholds."""
        metrics = self.get_metrics()
        
        warnings = []
        
        if metrics["process"]["memory_mb"] > max_memory_mb:
            warnings.append(f"Memory usage {metrics['process']['memory_mb']} MB > {max_memory_mb} MB")
        
        if metrics["process"]["cpu_percent"] > max_cpu:
            warnings.append(f"CPU usage {metrics['process']['cpu_percent']}% > {max_cpu}%")
        
        return {
            "healthy": len(warnings) == 0,
            "warnings": warnings,
            "metrics": metrics,
        }

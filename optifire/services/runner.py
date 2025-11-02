"""
Main service runner - single process, asyncio-based.
"""
import asyncio
import signal
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from optifire.core.config import Config
from optifire.core.flags import FeatureFlags
from optifire.core.db import Database
from optifire.core.bus import EventBus
from optifire.core.scheduler import Scheduler
from optifire.core.logger import logger
from optifire.api.server import create_app
import uvicorn


class OptiFIRERunner:
    """
    Main runner for OptiFIRE system.
    Single process, asyncio-based with thread pool.
    """

    def __init__(self):
        """Initialize runner."""
        self.base_path = Path(__file__).parent.parent.parent
        self.config_path = self.base_path / "configs" / "config.yaml"
        self.flags_path = self.base_path / "configs" / "features.yaml"
        self.db_path = self.base_path / "data" / "optifire.db"

        # Core components
        self.config = Config(self.config_path)
        self.flags = FeatureFlags(self.flags_path)
        self.db = Database(self.db_path)
        self.bus = EventBus()
        self.scheduler = Scheduler()

        # Thread pool for blocking operations
        self.executor = ThreadPoolExecutor(max_workers=3)

        # FastAPI app
        self.app = create_app()

        # Shutdown flag
        self._shutdown = False

    async def start(self) -> None:
        """Start all services."""
        logger.info("Starting OptiFIRE...")

        # Initialize database
        await self.db.initialize()

        # Start event bus
        await self.bus.start()

        # Start scheduler
        await self.scheduler.start()

        # Load and register enabled plugins
        await self._load_plugins()

        logger.info("OptiFIRE started successfully")

    async def stop(self) -> None:
        """Stop all services."""
        logger.info("Stopping OptiFIRE...")

        self._shutdown = True

        # Stop scheduler
        await self.scheduler.stop()

        # Stop event bus
        await self.bus.stop()

        # Shutdown thread pool
        self.executor.shutdown(wait=True)

        logger.info("OptiFIRE stopped")

    async def _load_plugins(self) -> None:
        """Load and schedule enabled plugins."""
        enabled = self.flags.get_enabled_plugins()
        logger.info(f"Loading {len(enabled)} enabled plugins")

        for plugin_id in enabled:
            try:
                # Dynamic import would happen here
                # For now, just log
                schedule = self.flags.get_schedule(plugin_id)
                budget = self.flags.get_budget(plugin_id)

                logger.info(
                    f"Loaded plugin: {plugin_id} "
                    f"(schedule={schedule}, budget={budget})"
                )

                # Would schedule plugin execution here
                # self.scheduler.schedule_plugin(plugin_id, schedule, plugin.run)

            except Exception as e:
                logger.error(f"Failed to load plugin {plugin_id}: {e}")

    def run_api(self, host: str = "0.0.0.0", port: int = 8000) -> None:
        """
        Run FastAPI server.

        Args:
            host: Host to bind to
            port: Port to bind to
        """
        # Setup signal handlers
        for sig in (signal.SIGTERM, signal.SIGINT):
            signal.signal(sig, self._handle_signal)

        # Run startup
        asyncio.run(self.start())

        # Run uvicorn
        logger.info(f"Starting API server on {host}:{port}")
        uvicorn.run(
            self.app,
            host=host,
            port=port,
            log_level="info",
        )

    def _handle_signal(self, signum, frame) -> None:
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, shutting down...")
        asyncio.create_task(self.stop())


def main():
    """Main entry point."""
    runner = OptiFIRERunner()
    runner.run_api()


if __name__ == "__main__":
    main()

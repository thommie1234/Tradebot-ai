"""
OptiFIRE - Optimized Feature Integration & Risk Engine
Main entry point and global state management.
"""
import asyncio
import os
from pathlib import Path
import uvicorn

from optifire.core.logger import logger
from optifire.core.config import Config
from optifire.core.flags import FeatureFlags
from optifire.core.db import Database
from optifire.core.bus import EventBus
from optifire.exec.broker_alpaca import AlpacaBroker
from optifire.ai.openai_client import OpenAIClient
from optifire.api.server import create_app

# Load environment variables manually
def load_env_file(filepath="secrets.env"):
    """Load environment variables from file."""
    if not os.path.exists(filepath):
        logger.warning(f"{filepath} not found")
        return

    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()
    logger.info(f"Loaded environment from {filepath}")

load_env_file("secrets.env")

# Global instances
class GlobalState:
    """Global application state."""

    def __init__(self):
        self.config: Config = None
        self.flags: FeatureFlags = None
        self.db: Database = None
        self.bus: EventBus = None
        self.broker: AlpacaBroker = None
        self.openai: OpenAIClient = None
        self.app = None

    async def initialize(self):
        """Initialize all global instances."""
        logger.info("=" * 60)
        logger.info("OptiFIRE - Optimized Feature Integration & Risk Engine")
        logger.info("=" * 60)

        # Create data directory
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)

        # Initialize configuration
        config_path = Path("config.yaml")
        if not config_path.exists():
            logger.warning("config.yaml not found, using defaults")
            config_path.write_text("""
system:
  max_workers: 3
  max_ram_mb: 900
  max_cpu_percent: 90

risk:
  max_exposure_total: 0.30
  max_exposure_symbol: 0.10
  max_drawdown: 0.08

execution:
  batch_window_seconds: 1
  rth_only: true
  max_slippage_bps: 10

api:
  host: 0.0.0.0
  port: 8000
  jwt_expiry_hours: 24
""")

        self.config = Config(config_path)

        # Initialize feature flags
        flags_path = Path("features.yaml")
        if not flags_path.exists():
            logger.warning("features.yaml not found, creating default")
            flags_path.write_text("""
plugins:
  exec_batch:
    enabled: true
    budget:
      cpu_ms: 500
      mem_mb: 30
""")

        self.flags = FeatureFlags(flags_path)

        # Initialize database
        db_path = data_dir / "optifire.db"
        self.db = Database(db_path)
        await self.db.initialize()

        # Initialize event bus
        self.bus = EventBus()
        await self.bus.start()

        # Initialize Alpaca broker
        paper = os.getenv("ALPACA_PAPER", "true").lower() == "true"
        self.broker = AlpacaBroker(paper=paper)

        # Test broker connection
        try:
            account = await self.broker.get_account()
            logger.info(f"✓ Alpaca connected: ${float(account['equity']):,.2f} equity")
        except Exception as e:
            logger.warning(f"Alpaca connection failed (will use mock data): {e}")

        # Initialize OpenAI client
        self.openai = OpenAIClient()
        if os.getenv("OPENAI_API_KEY"):
            logger.info("✓ OpenAI client initialized")
        else:
            logger.warning("OpenAI API key not found (AI features disabled)")

        # Create FastAPI app
        self.app = create_app()

        # Attach global state to app
        self.app.state.g = self

        logger.info("✓ All systems initialized")
        logger.info("=" * 60)

    async def shutdown(self):
        """Shutdown all services."""
        logger.info("Shutting down...")
        if self.bus:
            await self.bus.stop()
        logger.info("Shutdown complete")


# Global state instance
g = GlobalState()


async def startup():
    """Application startup."""
    await g.initialize()


async def shutdown():
    """Application shutdown."""
    await g.shutdown()


def main():
    """Main entry point."""
    # Initialize asyncio event loop and global state
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(startup())

    # Get configuration
    host = g.config.get("api.host", "0.0.0.0")
    port = g.config.get("api.port", 8000)

    # Run server
    logger.info(f"Starting server on {host}:{port}")

    try:
        uvicorn.run(
            g.app,
            host=host,
            port=port,
            log_level="info",
            access_log=False,
        )
    finally:
        loop.run_until_complete(shutdown())
        loop.close()


if __name__ == "__main__":
    main()

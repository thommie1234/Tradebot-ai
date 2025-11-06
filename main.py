"""
OptiFIRE - Optimized Feature Integration & Risk Engine
Main entry point and global state management.
"""
import asyncio
import os
from pathlib import Path
from contextlib import asynccontextmanager
import uvicorn

from optifire.core.logger import logger
from optifire.core.config import Config
from optifire.core.flags import FeatureFlags
from optifire.core.db import Database
from optifire.core.bus import EventBus
from optifire.exec.broker_alpaca import AlpacaBroker
from optifire.ai.openai_client import OpenAIClient
from optifire.auto_trader import AutoTrader

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
        self.auto_trader: AutoTrader = None
        self.auto_trader_task = None
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

        logger.info("✓ All systems initialized")
        logger.info("=" * 60)

    async def start_auto_trader(self):
        """Start the auto-trader (called by FastAPI lifespan)."""
        auto_trading_enabled = os.getenv("AUTO_TRADING_ENABLED", "true").lower() == "true"
        if auto_trading_enabled:
            self.auto_trader = AutoTrader(broker=self.broker, db=self.db)
            # Start auto-trader in background task
            self.auto_trader_task = asyncio.create_task(self.auto_trader.start())
            logger.info("✓ Auto-trader started (earnings scanner, news scanner, position manager)")
        else:
            logger.info("⚠ Auto-trading disabled (set AUTO_TRADING_ENABLED=true to enable)")

    async def shutdown(self):
        """Shutdown all services."""
        logger.info("Shutting down...")

        # Stop auto-trader
        if self.auto_trader:
            await self.auto_trader.stop()
            if self.auto_trader_task:
                self.auto_trader_task.cancel()
                try:
                    await self.auto_trader_task
                except asyncio.CancelledError:
                    pass

        # Stop event bus
        if self.bus:
            await self.bus.stop()

        logger.info("Shutdown complete")


# Global state instance
g = GlobalState()


@asynccontextmanager
async def lifespan(app):
    """FastAPI lifespan context manager."""
    # Startup
    await g.initialize()
    await g.start_auto_trader()
    yield
    # Shutdown
    await g.shutdown()


def create_app_with_lifespan():
    """Create FastAPI app with lifespan."""
    from fastapi import FastAPI, Request
    from fastapi.staticfiles import StaticFiles
    from fastapi.templating import Jinja2Templates
    from fastapi.responses import HTMLResponse
    from fastapi.middleware.cors import CORSMiddleware
    from pathlib import Path

    from optifire.api.routes_config import router as config_router
    from optifire.api.routes_metrics import router as metrics_router
    from optifire.api.routes_orders import router as orders_router
    from optifire.api.routes_plugins import router as plugins_router
    from optifire.api.routes_chat import router as chat_router
    from optifire.api.sse import router as sse_router

    app = FastAPI(
        title="OptiFIRE",
        description="Optimized Feature Integration & Risk Engine",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Attach global state
    app.state.g = g

    # Mount static files
    static_path = Path(__file__).parent / "optifire" / "api" / "static"
    static_path.mkdir(exist_ok=True)
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

    # Templates
    templates_path = Path(__file__).parent / "optifire" / "api" / "templates"
    templates_path.mkdir(exist_ok=True)
    app.state.templates = Jinja2Templates(directory=str(templates_path))

    # Include routers
    app.include_router(config_router, prefix="/config", tags=["config"])
    app.include_router(metrics_router, prefix="/metrics", tags=["metrics"])
    app.include_router(orders_router, prefix="/orders", tags=["orders"])
    app.include_router(plugins_router, prefix="/plugins", tags=["plugins"])
    app.include_router(chat_router, prefix="/chat", tags=["chat"])
    app.include_router(sse_router, prefix="/events", tags=["sse"])

    # Main dashboard route
    @app.get("/", response_class=HTMLResponse)
    async def dashboard(request: Request):
        """Main dashboard."""
        return app.state.templates.TemplateResponse(
            "dashboard.html",
            {"request": request},
        )

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        try:
            import psutil
            process = psutil.Process()
            return {
                "status": "healthy",
                "cpu_percent": process.cpu_percent(),
                "memory_mb": process.memory_info().rss / 1024 / 1024,
                "num_threads": process.num_threads(),
            }
        except ImportError:
            return {
                "status": "healthy",
                "message": "OptiFIRE running (psutil not available)"
            }

    return app


def main():
    """Main entry point."""
    # Create app with lifespan
    app = create_app_with_lifespan()

    # Get configuration (use defaults if not initialized yet)
    host = "0.0.0.0"
    port = 8000

    # Run server
    logger.info(f"Starting server on {host}:{port}")

    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        access_log=False,
    )


if __name__ == "__main__":
    main()

"""
FastAPI server with HTMX + Tailwind UI.
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path

from optifire.core.logger import logger
# from .routes_auth import router as auth_router  # Disabled - requires pyotp
from .routes_config import router as config_router
from .routes_metrics import router as metrics_router
from .routes_orders import router as orders_router
from .routes_plugins import router as plugins_router
from .routes_ai import router as ai_router
from .sse import router as sse_router


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="OptiFIRE",
        description="Optimized Feature Integration & Risk Engine",
        version="1.0.0",
    )

    # Mount static files
    static_path = Path(__file__).parent / "static"
    static_path.mkdir(exist_ok=True)
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

    # Templates
    templates_path = Path(__file__).parent / "templates"
    templates_path.mkdir(exist_ok=True)
    app.state.templates = Jinja2Templates(directory=str(templates_path))

    # Include routers
    # app.include_router(auth_router, prefix="/auth", tags=["auth"])  # Disabled
    app.include_router(config_router, prefix="/config", tags=["config"])
    app.include_router(metrics_router, prefix="/metrics", tags=["metrics"])
    app.include_router(orders_router, prefix="/orders", tags=["orders"])
    app.include_router(plugins_router, prefix="/plugins", tags=["plugins"])
    app.include_router(ai_router, prefix="/api/ai", tags=["ai"])
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

    logger.info("FastAPI app created")
    return app

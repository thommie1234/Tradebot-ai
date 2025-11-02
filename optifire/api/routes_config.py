"""Configuration management routes."""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, Any

router = APIRouter()


class RuntimeUpdate(BaseModel):
    updates: Dict[str, Any]


@router.get("/runtime")
async def get_runtime_config(request: Request):
    """Get current runtime configuration."""
    g = request.app.state.g
    config = g.config

    return {
        "version": config.get_version(),
        "config": config.get_all(),
    }


@router.put("/runtime")
async def update_runtime_config(update: RuntimeUpdate, request: Request):
    """Update runtime configuration."""
    g = request.app.state.g
    config = g.config

    try:
        await config.update_runtime(update.updates)

        # Publish event
        await g.bus.publish(
            "config_updated",
            {"version": config.get_version(), "updates": update.updates},
            source="api",
        )

        return {
            "status": "updated",
            "version": config.get_version(),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/flags")
async def get_feature_flags(request: Request):
    """Get all feature flags."""
    g = request.app.state.g
    flags = g.flags

    return {
        "version": flags.get_version(),
        "plugins": flags.get_all_flags(),
    }


@router.post("/flags/{plugin_id}/toggle")
async def toggle_flag(plugin_id: str, enabled: bool, request: Request):
    """Toggle a feature flag."""
    g = request.app.state.g
    flags = g.flags

    try:
        await flags.toggle(plugin_id, enabled)

        # Publish event
        await g.bus.publish(
            "flag_toggled",
            {"plugin_id": plugin_id, "enabled": enabled},
            source="api",
        )

        return {
            "plugin_id": plugin_id,
            "enabled": enabled,
            "version": flags.get_version(),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/history")
async def get_config_history(request: Request):
    """Get configuration history."""
    g = request.app.state.g
    config = g.config

    return {
        "current_version": config.get_version(),
        "history": config.get_history(),
    }


@router.post("/rollback/{version}")
async def rollback_config(version: int, request: Request):
    """Rollback to a previous version."""
    g = request.app.state.g
    config = g.config

    try:
        await config.rollback(version)

        # Publish event
        await g.bus.publish(
            "config_rollback",
            {"version": version},
            source="api",
        )

        return {
            "status": "rolled_back",
            "version": config.get_version(),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

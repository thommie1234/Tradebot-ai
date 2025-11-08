"""Plugin management routes."""
from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

from optifire.api.routes_auth import verify_token

router = APIRouter()


class PluginExecuteRequest(BaseModel):
    plugin_id: str
    context_data: Optional[Dict[str, Any]] = None


@router.get("/")
async def list_plugins(category: Optional[str] = None, request: Request = None):
    """List all registered plugins."""
    try:
        from optifire.plugins import registry

        if category:
            plugins = registry.list_by_category(category)
        else:
            plugins = registry.list_all()

        # Get details for each plugin
        plugin_details = []
        for plugin_id in plugins:
            plugin = registry.get(plugin_id)
            if plugin:
                metadata = plugin.metadata
                plugin_details.append({
                    "plugin_id": metadata.plugin_id,
                    "name": metadata.name,
                    "category": metadata.category,
                    "version": metadata.version,
                    "description": metadata.description,
                    "inputs": metadata.inputs,
                    "outputs": metadata.outputs,
                    "est_cpu_ms": metadata.est_cpu_ms,
                    "est_mem_mb": metadata.est_mem_mb,
                })

        return {
            "total": len(plugin_details),
            "category": category or "all",
            "plugins": plugin_details,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{plugin_id}")
async def get_plugin(plugin_id: str):
    """Get detailed information about a specific plugin."""
    try:
        from optifire.plugins import registry

        plugin = registry.get(plugin_id)
        if not plugin:
            raise HTTPException(status_code=404, detail=f"Plugin {plugin_id} not found")

        metadata = plugin.metadata
        plan = plugin.plan()

        return {
            "plugin_id": metadata.plugin_id,
            "name": metadata.name,
            "category": metadata.category,
            "version": metadata.version,
            "author": metadata.author,
            "description": metadata.description,
            "inputs": metadata.inputs,
            "outputs": metadata.outputs,
            "est_cpu_ms": metadata.est_cpu_ms,
            "est_mem_mb": metadata.est_mem_mb,
            "plan": plan,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{plugin_id}/execute")
async def execute_plugin(plugin_id: str, exec_req: PluginExecuteRequest, request: Request, user=Depends(verify_token)):
    """Execute a plugin manually. Requires authentication."""
    try:
        from optifire.plugins import registry, PluginContext

        g = request.app.state.g

        plugin = registry.get(plugin_id)
        if not plugin:
            raise HTTPException(status_code=404, detail=f"Plugin {plugin_id} not found")

        # Build context
        context = PluginContext(
            config=g.config.get_all() if g.config else {},
            db=g.db,
            bus=g.bus,
            data=exec_req.context_data or {},
        )

        # Execute with budget
        result = await plugin.execute_with_budget(
            context=context,
            cpu_budget_ms=plugin.metadata.est_cpu_ms * 2,  # 2x estimated
            mem_budget_mb=plugin.metadata.est_mem_mb * 2,
        )

        return {
            "plugin_id": plugin_id,
            "success": result.success,
            "data": result.data,
            "error": result.error,
            "cpu_ms": result.cpu_ms,
            "mem_mb": result.mem_mb,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories/list")
async def list_categories():
    """List all plugin categories."""
    return {
        "categories": [
            {"id": "alpha", "name": "Alpha Generation", "description": "Signal generation & trading ideas"},
            {"id": "feature_eng", "name": "Feature Engineering", "description": "Data transformation & features"},
            {"id": "risk", "name": "Risk Management", "description": "Position sizing & risk control"},
            {"id": "ai", "name": "AI Intelligence", "description": "Machine learning & AI features"},
            {"id": "ml", "name": "Model Management", "description": "Model deployment & monitoring"},
            {"id": "self_learning", "name": "Self-Learning", "description": "Adaptive & online learning"},
            {"id": "infrastructure", "name": "Infrastructure", "description": "System reliability & operations"},
            {"id": "execution", "name": "Execution", "description": "Order execution & routing"},
            {"id": "ux", "name": "UX/Visualization", "description": "User interface & dashboards"},
            {"id": "diagnostics", "name": "Diagnostics", "description": "Testing & analysis tools"},
        ]
    }


@router.get("/stats/summary")
async def get_plugin_stats(request: Request):
    """Get plugin execution statistics."""
    g = request.app.state.g
    db = g.db

    try:
        # Get execution stats from database
        stats = await db.fetch_all(
            """
            SELECT 
                plugin_id,
                COUNT(*) as execution_count,
                AVG(CAST(json_extract(metadata, '$.cpu_ms') AS INTEGER)) as avg_cpu_ms,
                AVG(CAST(json_extract(metadata, '$.mem_mb') AS INTEGER)) as avg_mem_mb,
                SUM(CASE WHEN json_extract(metadata, '$.success') = 'true' THEN 1 ELSE 0 END) as success_count
            FROM signals
            WHERE plugin_id IS NOT NULL
            GROUP BY plugin_id
            ORDER BY execution_count DESC
            LIMIT 50
            """
        )

        return {
            "stats": stats,
            "total_plugins": len(stats),
        }

    except Exception as e:
        # If stats table doesn't exist or error, return empty
        return {
            "stats": [],
            "total_plugins": 0,
            "error": str(e),
        }

"""Metrics and dashboard data routes."""
from fastapi import APIRouter, HTTPException, Request

router = APIRouter()


@router.get("/portfolio")
async def get_portfolio_metrics(request: Request):
    """Get portfolio metrics."""
    g = request.app.state.g
    broker = g.broker

    try:
        account = await broker.get_account()

        equity = float(account.get("equity", 0))
        cash = float(account.get("cash", 0))
        positions_value = equity - cash
        buying_power = float(account.get("buying_power", 0))

        return {
            "equity": equity,
            "cash": cash,
            "positions_value": positions_value,
            "buying_power": buying_power,
            "unrealized_pnl": float(account.get("unrealized_pl", 0)),
            "realized_pnl": float(account.get("realized_pl", 0)),
            "exposure_pct": positions_value / equity if equity > 0 else 0.0,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get portfolio: {str(e)}")


@router.get("/positions")
async def get_positions(request: Request):
    """Get current positions."""
    g = request.app.state.g
    broker = g.broker

    try:
        positions = await broker.get_positions()

        formatted = []
        for pos in positions:
            formatted.append({
                "symbol": pos["symbol"],
                "qty": float(pos["qty"]),
                "side": pos["side"],
                "avg_entry_price": float(pos["avg_entry_price"]),
                "current_price": float(pos["current_price"]),
                "market_value": float(pos["market_value"]),
                "unrealized_pnl": float(pos["unrealized_pl"]),
                "unrealized_pnl_pct": float(pos["unrealized_plpc"]) * 100,
                "cost_basis": float(pos["cost_basis"]),
            })

        return {"positions": formatted}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get positions: {str(e)}")


@router.get("/risk")
async def get_risk_metrics(request: Request):
    """Get risk metrics."""
    g = request.app.state.g
    broker = g.broker
    db = g.db

    try:
        # Get account
        account = await broker.get_account()
        equity = float(account.get("equity", 100000))

        # Get positions
        positions = await broker.get_positions()

        # Calculate total exposure
        total_exposure = sum(abs(float(p["market_value"])) for p in positions)
        exposure_pct = total_exposure / equity if equity > 0 else 0.0

        # Get historical PnL from database for VaR calculation
        # For now, use simple approximations
        # In production, you'd calculate these from historical returns

        # Simple VaR estimate (95% confidence)
        # Assuming 2% daily volatility
        daily_vol = 0.02
        var_95 = equity * daily_vol * 1.65  # 95% confidence
        cvar_95 = equity * daily_vol * 2.5  # Expected shortfall

        # Beta approximation (would need SPY correlation)
        beta = 1.0

        # Current drawdown
        drawdown = 0.0  # Would calculate from equity high water mark

        # Sharpe ratio (would calculate from returns history)
        sharpe = 0.0

        return {
            "exposure_pct": exposure_pct,
            "var_95": var_95,
            "cvar_95": cvar_95,
            "beta": beta,
            "drawdown": drawdown,
            "sharpe": sharpe,
            "num_positions": len(positions),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get risk metrics: {str(e)}")


@router.get("/performance")
async def get_performance(request: Request):
    """Get performance metrics."""
    g = request.app.state.g
    broker = g.broker
    db = g.db

    try:
        account = await broker.get_account()

        # Get performance from database
        perf_metrics = await db.fetch_all(
            "SELECT * FROM performance ORDER BY timestamp DESC LIMIT 100"
        )

        # Calculate from account if no history
        total_return_pct = 0.0
        sharpe_ratio = 0.0
        max_drawdown = 0.0
        win_rate = 0.5

        # Get trades for win rate
        trades = await db.fetch_all(
            "SELECT pnl FROM trades WHERE pnl IS NOT NULL"
        )

        if trades:
            winning_trades = sum(1 for t in trades if t["pnl"] > 0)
            win_rate = winning_trades / len(trades) if len(trades) > 0 else 0.5

        return {
            "total_return_pct": total_return_pct,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_drawdown,
            "win_rate": win_rate,
            "total_trades": len(trades),
            "unrealized_pnl": float(account.get("unrealized_pl", 0)),
            "realized_pnl": float(account.get("realized_pl", 0)),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance: {str(e)}")


@router.get("/plugins")
async def get_plugin_status(request: Request):
    """Get plugin execution status."""
    g = request.app.state.g
    db = g.db
    flags = g.flags

    try:
        # Get recent plugin executions
        recent_logs = await db.fetch_all(
            """
            SELECT plugin_id, status, cpu_ms, mem_mb, started_at, completed_at
            FROM plugin_log
            ORDER BY started_at DESC
            LIMIT 100
            """
        )

        # Get all plugins from flags
        all_plugins = flags.get_all_flags()

        plugins = []
        for plugin_id, config in all_plugins.items():
            # Find most recent execution
            last_run = next(
                (log for log in recent_logs if log["plugin_id"] == plugin_id),
                None
            )

            plugins.append({
                "plugin_id": plugin_id,
                "enabled": config.get("enabled", False),
                "last_status": last_run["status"] if last_run else "never_run",
                "last_run": last_run["completed_at"] if last_run else None,
                "cpu_ms": last_run["cpu_ms"] if last_run else None,
                "mem_mb": last_run["mem_mb"] if last_run else None,
            })

        return {"plugins": plugins}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get plugin status: {str(e)}")

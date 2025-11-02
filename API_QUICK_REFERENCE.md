# OptiFIRE API Quick Reference

## Endpoints Summary

### Authentication
```
POST   /auth/login                           # Login, returns JWT
Helper: verify_token()                       # Token verification
```

### Configuration
```
GET    /config/runtime                       # Get config (STUB)
PUT    /config/runtime                       # Update config (STUB)
GET    /config/flags                         # Get feature flags (STUB)
POST   /config/flags/{plugin_id}/toggle      # Toggle flag (STUB)
GET    /config/history                       # Config history (STUB)
POST   /config/rollback/{version}            # Rollback (STUB)
```

### Metrics
```
GET    /metrics/portfolio                    # Portfolio metrics (STUB)
GET    /metrics/positions                    # Positions (STUB)
GET    /metrics/risk                         # Risk metrics (STUB)
GET    /metrics/performance                  # Performance (STUB)
GET    /metrics/plugins                      # Plugin status (STUB)
```

### Orders
```
POST   /orders/submit                        # Submit order (STUB)
GET    /orders/                              # List orders (STUB)
GET    /orders/{order_id}                    # Get order (STUB)
DELETE /orders/{order_id}                    # Cancel order (STUB)
```

### Events
```
GET    /events/stream                        # SSE stream (STUB)
```

### System
```
GET    /health                               # Health check (FULL)
GET    /                                     # Dashboard (needs template)
```

---

## Plugin Statistics

| Metric | Count |
|--------|-------|
| Total Plugins | 75 |
| Fully Implemented | 44 (59%) |
| Functional Stubs | 31 (41%) |

### By Category

- **Alpha Signals**: 4/13 complete
- **Feature Engineering**: 3/10 complete
- **Risk Management**: 7/10 complete (70%)
- **AI/ML**: 8/17 complete
- **Execution**: 3/3 complete (100%)
- **Infrastructure**: 9/10 complete (90%)
- **Diagnostics**: 4/5 complete
- **UX/UI**: 6/7 complete

---

## Critical Incomplete APIs

### 1. Configuration Management
- Routes defined, database integration missing
- Version tracking not implemented
- Rollback logic missing

### 2. Feature Flags
- Routes defined, toggle persistence missing
- Registry integration incomplete

### 3. Metrics
- All endpoints return hardcoded/zero data
- No real-time calculations
- No portfolio tracking

### 4. Orders
- No broker integration (Alpaca)
- No order execution
- No order history

### 5. SSE Events
- Event Bus not integrated
- No real-time streaming
- Mock data only

### 6. Dashboard
- HTML template missing
- No HTMX interactions

---

## Best Implemented Plugins

### Infrastructure (90% complete)
- `infra_psutil_health` - CPU/RAM monitoring
- `infra_heartbeat` - System heartbeat
- `infra_checkpoint_restart` - Checkpoint/restart
- `infra_config_hot_reload` - Hot reload
- `infra_apscheduler` - Scheduler
- `infra_api_cache` - Response caching
- `infra_sqlite_txlog` - Transaction logging
- `infra_dockerize` - Docker utilities
- `infra_broker_latency` - Latency tracking

### Execution (100% complete)
- `exec_batch_orders` - Batch execution
- `exec_moc` - Market-on-close
- `extra_bidask_filter` - Spread filtering

### Risk Management (70% complete)
- `risk_var_budget` - VaR budgeting
- `risk_drawdown_derisk` - **CRITICAL** - De-risking at 5%/8%
- `risk_frac_kelly_atten` - Kelly sizing
- `risk_vol_target` - Volatility targeting
- `risk_cvar_size` - CVaR sizing
- `risk_auto_hedge_ratio` - Auto hedging
- `risk_entropy_weights` - Entropy weighting

### Full Implementations (44 total)
See API_AND_PLUGIN_OVERVIEW.md for complete list

---

## Plugins Needing External APIs

### Google Trends
- `alpha_google_trends`
- `ai_topic_clustering`

### Market Data
- `alpha_analyst_revisions` (earnings)
- `alpha_whisper_spread` (earnings)
- `alpha_risk_reversal` (options)
- `alpha_etf_flow_div` (ETF flows)
- `alpha_micro_imbalance` (L2 order book)
- `alpha_vpin` (tick data)

### News/Sentiment
- `fe_price_news_div`
- `ai_news_vectors`
- `ai_shap_drift`

### ML Models
- `ml_lgbm_quantize`
- `ml_onnx_runtime`

### Other
- `ux_discord_cmds` (Discord API)

---

## Configuration Files

### system config (config.yaml)
- System limits (workers, RAM, CPU)
- Risk parameters (exposure, drawdown, VaR)
- Execution settings (Alpaca, paper trading)
- API settings (host, port, JWT)
- Data paths (SQLite, DuckDB, parquet)
- ML paths (model storage)

### Feature Flags (features.yaml)
- 75 plugins, all OFF by default
- Per-plugin schedule and budget
- Example: `risk_drawdown_derisk` is ON (safety)
- Example: `infra_psutil_health` is ON (monitoring)

---

## Next Steps to Complete APIs

1. **Database Integration** - SQLite/DuckDB for config, flags, history
2. **Portfolio Engine** - Real-time PnL, risk metrics
3. **Broker Integration** - Alpaca API for orders
4. **Event Bus** - Pub/sub for real-time updates
5. **Dashboard HTML** - HTMX + Tailwind UI
6. **External APIs** - Google Trends, earnings, options, news feeds

---

## Testing Health Check

```bash
curl http://localhost:8000/health
```

Should return:
```json
{
  "status": "healthy",
  "cpu_percent": 45.2,
  "memory_mb": 256.5,
  "num_threads": 8
}
```

---

## Key Files

- `/root/optifire/optifire/api/server.py` - FastAPI app
- `/root/optifire/optifire/api/routes_*.py` - API routes
- `/root/optifire/configs/config.yaml` - System config
- `/root/optifire/configs/features.yaml` - Plugin flags
- `/root/optifire/IMPLEMENTATION_STATUS.md` - Plugin status
- `/root/optifire/API_AND_PLUGIN_OVERVIEW.md` - Full details


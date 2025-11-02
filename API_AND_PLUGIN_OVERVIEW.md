# OptiFIRE: Complete API and Plugin Architecture Overview

## Project Summary

**Project Name**: OptiFIRE (Optimized Feature Integration & Risk Engine)
**Type**: Trading/Finance application with plugin-based architecture
**Framework**: FastAPI + HTMX + Tailwind CSS
**Language**: Python
**Total Plugins**: 75 (all scaffolded, ~35 fully implemented, ~40 functional stubs)

---

## Architecture Overview

### Core Project Structure

```
optifire/
├── optifire/
│   ├── api/                    # FastAPI endpoints & routes
│   │   ├── server.py           # Main FastAPI app
│   │   ├── routes_auth.py      # Authentication endpoints
│   │   ├── routes_config.py    # Configuration management
│   │   ├── routes_metrics.py   # Dashboard metrics
│   │   ├── routes_orders.py    # Order management
│   │   ├── sse.py              # Server-Sent Events
│   │   ├── static/             # Static assets (CSS, JS)
│   │   └── templates/          # HTML templates
│   ├── core/                   # Core infrastructure
│   │   ├── config.py           # Configuration management
│   │   ├── db.py               # Database layer
│   │   ├── bus.py              # Event bus
│   │   ├── scheduler.py        # Scheduler
│   │   ├── logger.py           # Logging
│   │   ├── errors.py           # Exception classes
│   │   └── flags.py            # Feature flags
│   ├── plugins/                # 75 plugin modules (see below)
│   ├── data/                   # Data collection
│   ├── exec/                   # Order execution
│   ├── risk/                   # Risk management
│   ├── fe/                     # Feature engineering
│   └── services/               # Service runners
├── configs/
│   ├── config.yaml             # System configuration
│   └── features.yaml           # Feature flags for all 75 plugins
├── generate_plugins.py         # Plugin generation script
└── IMPLEMENTATION_STATUS.md    # Status document
```

---

## REST API Endpoints

### Base Configuration
- **Host**: `0.0.0.0`
- **Port**: `8000`
- **API Title**: OptiFIRE
- **API Version**: 1.0.0
- **Authentication**: JWT + TOTP (optional)

### Implemented API Routes

#### 1. **Authentication Routes** (`/auth`)
Prefix: `/auth`

| Method | Endpoint | Purpose | Status | Implementation |
|--------|----------|---------|--------|-----------------|
| POST | `/login` | Login with username/password + TOTP | ✅ Implemented | Full - Returns JWT token |
| (Helper) | `verify_token()` | Verify JWT token | ✅ Implemented | Full - Used as dependency |

**Example Request**:
```json
POST /auth/login
{
  "username": "admin",
  "password": "change-me",
  "totp_code": "123456"
}
```

**Example Response**:
```json
{
  "access_token": "eyJ0eXAi...",
  "token_type": "bearer"
}
```

**Authentication Details**:
- JWT Secret: `JWT_SECRET` env var (default: "change-me-in-production")
- TOTP Secret: `TOTP_SECRET` env var (optional)
- JWT Algorithm: HS256
- Token Expiry: 24 hours

---

#### 2. **Configuration Routes** (`/config`)
Prefix: `/config`

| Method | Endpoint | Purpose | Status | Integration |
|--------|----------|---------|--------|-------------|
| GET | `/runtime` | Get current runtime configuration | ✅ Defined | **INCOMPLETE** - Would integrate with Config instance |
| PUT | `/runtime` | Update runtime configuration | ✅ Defined | **INCOMPLETE** - Would call config.update_runtime() |
| GET | `/flags` | Get all feature flags | ✅ Defined | **INCOMPLETE** - Would integrate with FeatureFlags instance |
| POST | `/flags/{plugin_id}/toggle` | Toggle a feature flag | ✅ Defined | **INCOMPLETE** - Would call flags.toggle() |
| GET | `/history` | Get configuration history | ✅ Defined | **INCOMPLETE** - Stub implementation |
| POST | `/rollback/{version}` | Rollback to previous config | ✅ Defined | **INCOMPLETE** - Stub implementation |

**Current Stub Response** (all endpoints):
```json
{
  "version": 1,
  "config": {}
}
```

**What's Missing**:
- Database integration for config persistence
- Config version tracking
- Actual rollback logic
- FeatureFlags integration

---

#### 3. **Metrics Routes** (`/metrics`)
Prefix: `/metrics`

| Method | Endpoint | Purpose | Status | Implementation |
|--------|----------|---------|--------|-----------------|
| GET | `/portfolio` | Get portfolio metrics | ✅ Defined | Stub - hardcoded mock data |
| GET | `/positions` | Get current positions | ✅ Defined | Stub - empty list |
| GET | `/risk` | Get risk metrics | ✅ Defined | Stub - zeros |
| GET | `/performance` | Get performance metrics | ✅ Defined | Stub - zeros |
| GET | `/plugins` | Get plugin execution status | ✅ Defined | Stub - empty list |

**Example Response** (`/portfolio`):
```json
{
  "equity": 100000.0,
  "cash": 50000.0,
  "positions_value": 50000.0,
  "unrealized_pnl": 0.0,
  "realized_pnl": 0.0,
  "exposure_pct": 0.50
}
```

**What's Missing**:
- Real-time portfolio calculations
- Position tracking
- PnL calculations
- Risk metric calculations
- Plugin status monitoring

---

#### 4. **Order Routes** (`/orders`)
Prefix: `/orders`

| Method | Endpoint | Purpose | Status | Integration |
|--------|----------|---------|--------|-------------|
| POST | `/submit` | Submit a manual order | ✅ Defined | **INCOMPLETE** - Would integrate with OrderExecutor |
| GET | `/{order_id}` | Get order status | ✅ Defined | Stub - returns filled |
| DELETE | `/{order_id}` | Cancel an order | ✅ Defined | Stub - returns canceled |
| GET | `/` | List recent orders | ✅ Defined | Stub - empty list |

**Example Request**:
```json
POST /orders/submit
{
  "symbol": "AAPL",
  "qty": 100,
  "side": "buy",
  "order_type": "market"
}
```

**Example Response**:
```json
{
  "order_id": "mock_123",
  "symbol": "AAPL",
  "qty": 100,
  "status": "submitted"
}
```

**What's Missing**:
- Real order execution
- Broker integration (Alpaca)
- Order tracking and status
- Order history

---

#### 5. **SSE (Server-Sent Events) Routes** (`/events`)
Prefix: `/events`

| Method | Endpoint | Purpose | Status | Implementation |
|--------|----------|---------|--------|-----------------|
| GET | `/stream` | Real-time event stream | ✅ Defined | **INCOMPLETE** - Would integrate with EventBus |

**Stream Format**:
```
data: {"type": "pnl_update", "equity": 100000.0, "pnl": 0.0, "timestamp": "2025-01-01T00:00:00Z"}
```

**What's Missing**:
- EventBus integration
- Real PnL streaming
- Event filtering
- Client subscription management

---

#### 6. **Health Check**

| Method | Endpoint | Purpose | Status |
|--------|----------|---------|--------|
| GET | `/health` | System health check | ✅ Fully Implemented |

**Response**:
```json
{
  "status": "healthy",
  "cpu_percent": 45.2,
  "memory_mb": 256.5,
  "num_threads": 8
}
```

---

#### 7. **Dashboard Route**

| Method | Endpoint | Purpose | Status |
|--------|----------|---------|--------|
| GET | `/` | Main dashboard HTML | ✅ Defined | Requires HTML template |

---

## API Integration Status Summary

### Fully Implemented ✅
- Authentication (JWT + TOTP)
- Health check endpoint
- API structure & routing

### Defined But Incomplete 🟡
- **Configuration API** - Endpoints exist, need Config/FeatureFlags integration
- **Metrics API** - Endpoints exist, need real data source
- **Orders API** - Endpoints exist, need Broker integration
- **SSE API** - Endpoint exists, needs EventBus integration
- **Dashboard** - Route exists, needs HTML template

### Configuration Files

#### System Configuration (`config.yaml`)

```yaml
system:
  max_workers: 3              # Concurrency limit
  max_ram_mb: 900             # Memory limit
  max_cpu_percent: 90         # CPU limit
  log_level: "INFO"

risk:
  max_exposure_total: 0.30    # 30% portfolio max
  max_exposure_symbol: 0.10   # 10% per symbol
  max_drawdown: 0.08          # 8% stop loss
  var_confidence: 0.95        # VaR at 95%
  max_var_pct: 0.05           # 5% portfolio

execution:
  batch_window_seconds: 1.0
  rth_only: true              # Regular trading hours
  broker: "alpaca"
  paper_trading: true

api:
  host: "0.0.0.0"
  port: 8000
  jwt_expiry_hours: 24
  enable_cors: false
```

#### Feature Flags (`features.yaml`)

All 75 plugins are OFF by default. Can be enabled individually:

```yaml
plugins:
  alpha_vix_regime:
    enabled: false
    schedule: "@open"
    budget: {cpu_ms: 500, mem_mb: 30}
  
  risk_drawdown_derisk:
    enabled: true  # Safety-critical
    schedule: "interval_5m"
    budget: {cpu_ms: 300, mem_mb: 20}
```

---

## Plugin Architecture

### Plugin Base Class

All 75 plugins inherit from `Plugin` base class with required methods:

```python
class Plugin(ABC):
    def describe(self) -> PluginMetadata:
        """Return plugin metadata"""
    
    def plan(self) -> Dict[str, Any]:
        """Return execution plan (schedule, triggers, deps)"""
    
    async def run(self, context: PluginContext) -> PluginResult:
        """Execute plugin logic"""
```

### Plugin Categories (75 Total)

#### 1. **Alpha Signals** (13 plugins)
Generate trading signals based on various market data:

| Plugin | Status | Implementation |
|--------|--------|-----------------|
| `alpha_vix_regime` | ✅ FULL | VIX-based regime detection (Low/Normal/Elevated/Crisis) |
| `alpha_cross_asset_corr` | ✅ FULL | SPY-TLT correlation breakdowns |
| `alpha_vrp` | ✅ FULL | Implied vs realized volatility |
| `alpha_google_trends` | 🟡 STUB | Requires Google Trends API |
| `alpha_analyst_revisions` | 🟡 STUB | Requires earnings data API |
| `alpha_whisper_spread` | 🟡 STUB | Requires earnings whisper data |
| `alpha_coint_pairs` | 🟡 STUB | Cointegration pairs trading |
| `alpha_risk_reversal` | 🟡 STUB | Requires options data |
| `alpha_etf_flow_div` | 🟡 STUB | Requires ETF flow data |
| `alpha_micro_imbalance` | 🟡 STUB | Requires L2 order book data |
| `alpha_t_stat_threshold` | ✅ FULL | T-stat based filtering |
| `alpha_position_agnostic` | ✅ FULL | Position-agnostic signals |
| `alpha_vpin` | 🟡 STUB | Requires tick data |

#### 2. **Feature Engineering** (10 plugins)
Create/transform features for ML models:

| Plugin | Status | Implementation |
|--------|--------|-----------------|
| `fe_kalman` | ✅ FULL | EWMA smoothing |
| `fe_garch` | ✅ FULL | EWMA variance estimation |
| `fe_entropy` | ✅ FULL | Shannon entropy calculation |
| `fe_price_news_div` | 🟡 STUB | Requires news data |
| `fe_fracdiff` | 🟡 STUB | Fractional differencing |
| `fe_mini_pca` | 🟡 STUB | PCA dimensionality reduction |
| `fe_wavelet` | 🟡 STUB | Wavelet decomposition |
| `fe_duckdb_store` | 🟡 STUB | DuckDB storage |
| `fe_dollar_bars` | 🟡 STUB | Dollar bar construction |
| `fe_vol_weighted_sent` | 🟡 STUB | Volume-weighted sentiment |

#### 3. **Risk Management** (10 plugins)
Control portfolio risk:

| Plugin | Status | Implementation |
|--------|--------|-----------------|
| `risk_var_budget` | ✅ FULL | VaR-based position budgeting |
| `risk_drawdown_derisk` | ✅ FULL | **CRITICAL** - 0.5x at 5% DD, stop at 8% |
| `risk_frac_kelly_atten` | ✅ FULL | Fractional Kelly sizing |
| `risk_vol_target` | ✅ FULL | Scale to 15% volatility |
| `risk_cvar_size` | ✅ FULL | CVaR-based sizing |
| `risk_auto_hedge_ratio` | ✅ FULL | Auto SPY hedge |
| `risk_entropy_weights` | ✅ FULL | Maximum entropy weighting |
| `risk_time_decay_size` | ✅ FULL | Time-decay sizing |
| `risk_tracking_error` | 🟡 STUB | Tracking error limits |
| `risk_liquidity_hotspot` | 🟡 STUB | Liquidity monitoring |

#### 4. **AI/ML** (17 plugins)
Machine learning and advanced analytics:

| Plugin | Status | Implementation |
|--------|--------|-----------------|
| `ai_bandit_alloc` | ✅ FULL | Thompson sampling allocation |
| `sl_fading_memory` | ✅ FULL | Fading memory learning |
| `sl_bayes_update` | ✅ FULL | Bayesian updates |
| `ml_entropy_monitor` | ✅ FULL | Model entropy monitoring |
| `diag_data_drift` | ✅ FULL | KS test data drift |
| `ml_shadow_ab` | ✅ FULL | Shadow A/B testing |
| `ml_quantile_calibrator` | ✅ FULL | Quantile calibration |
| `sl_perf_trigger` | ✅ FULL | Performance-triggered retraining |
| `ai_meta_labeling` | 🟡 STUB | Meta-labeling for bet sizing |
| `ai_online_sgd` | 🟡 STUB | Online SGD |
| `ai_dtw_matcher` | 🟡 STUB | Dynamic Time Warping |
| `ai_news_vectors` | 🟡 STUB | News embeddings |
| `ai_shap_drift` | 🟡 STUB | SHAP drift detection |
| `sl_optuna_pruner` | 🟡 STUB | Hyperparameter tuning |
| `ml_lgbm_quantize` | 🟡 STUB | LightGBM quantization |
| `ml_onnx_runtime` | 🟡 STUB | ONNX inference |
| `ai_topic_clustering` | 🟡 STUB | News topic clustering |

#### 5. **Execution** (3 plugins)
Order execution strategies:

| Plugin | Status | Implementation |
|--------|--------|-----------------|
| `exec_batch_orders` | ✅ FULL | Batch order execution |
| `exec_moc` | ✅ FULL | Market-on-close orders |
| `extra_bidask_filter` | ✅ FULL | 20 bps bid-ask filter |

#### 6. **Infrastructure** (10 plugins)
System infrastructure and monitoring:

| Plugin | Status | Implementation |
|--------|--------|-----------------|
| `infra_psutil_health` | ✅ FULL | CPU/RAM/thread monitoring |
| `infra_heartbeat` | ✅ FULL | System heartbeat |
| `infra_checkpoint_restart` | ✅ FULL | Checkpoint/restart |
| `infra_sqlite_txlog` | ✅ FULL | Transaction logging |
| `infra_config_hot_reload` | ✅ FULL | Hot configuration reload |
| `infra_apscheduler` | ✅ FULL | Scheduler integration |
| `infra_api_cache` | ✅ FULL | 5-minute response caching |
| `infra_dockerize` | ✅ FULL | Docker utilities |
| `infra_broker_latency` | ✅ FULL | Latency monitoring |
| `infra_pandera_validation` | 🟡 STUB | Data validation |

#### 7. **Diagnostics** (5 plugins)
Performance analysis and diagnostics:

| Plugin | Status | Implementation |
|--------|--------|-----------------|
| `diag_oos_decay_plot` | ✅ FULL | Out-of-sample decay |
| `diag_slippage_report` | ✅ FULL | Slippage analysis |
| `diag_param_sensitivity` | ✅ FULL | Parameter sensitivity |
| `diag_sharpe_ci` | ✅ FULL | Sharpe confidence intervals |
| `diag_cpcv_overfit` | 🟡 STUB | Combinatorial purged CV |

#### 8. **UX/UI** (7 plugins)
User interface and visualization:

| Plugin | Status | Implementation |
|--------|--------|-----------------|
| `ux_ws_pnl_sse` | ✅ FULL | SSE P&L streaming |
| `ux_strategy_pie` | ✅ FULL | Strategy allocation chart |
| `ux_var_es_plot` | ✅ FULL | VaR/ES visualization |
| `ux_signal_contrib` | ✅ FULL | Signal contribution |
| `ux_pnl_drawdown_plot` | ✅ FULL | P&L/drawdown plots |
| `ux_log_level_ctrl` | ✅ FULL | Runtime log control |
| `ux_discord_cmds` | 🟡 STUB | Discord bot |

---

## What APIs/Features Are Incomplete or Missing

### 1. **Critical Missing Integrations** 🔴

The API layer defines routes but lacks core system integrations:

| Component | Status | What's Missing |
|-----------|--------|-----------------|
| **Config Management** | 🟡 Stub | Database integration, version tracking, rollback |
| **Feature Flags** | 🟡 Stub | Flag toggle persistence, registry integration |
| **Event Bus** | 🟡 Stub | Real-time event streaming infrastructure |
| **Order Executor** | 🟡 Stub | Broker integration (Alpaca), order routing |
| **Metrics Collection** | 🟡 Stub | Real-time portfolio calculations |
| **Plugin Status** | 🟡 Stub | Plugin execution monitoring |

### 2. **Configuration APIs Missing Integration**

```python
# These endpoints are defined but not integrated:

@router.get("/runtime")
async def get_runtime_config():
    # Would integrate with Config instance
    return {"version": 1, "config": {}}  # Stub!

@router.put("/runtime") 
async def update_runtime_config(update: RuntimeUpdate):
    # Would call config.update_runtime(update.updates)
    return {"status": "updated", "version": 2}  # Stub!

@router.get("/flags")
async def get_feature_flags():
    # Would integrate with FeatureFlags instance
    return {"plugins": {}}  # Stub!

@router.post("/flags/{plugin_id}/toggle")
async def toggle_flag(plugin_id: str, enabled: bool):
    # Would call flags.toggle(plugin_id, enabled)
    return {"plugin_id": plugin_id, "enabled": enabled}  # Stub!
```

### 3. **Metrics APIs Missing Real Data**

All metrics endpoints return mock/stub data:

```python
@router.get("/portfolio")
async def get_portfolio_metrics():
    return {
        "equity": 100000.0,        # Hardcoded!
        "cash": 50000.0,           # Hardcoded!
        "positions_value": 50000.0,# Hardcoded!
        ...
    }

@router.get("/risk")
async def get_risk_metrics():
    return {
        "var_95": 0.0,    # Zeros!
        "cvar_95": 0.0,   # Zeros!
        ...
    }
```

### 4. **Order Management Missing Broker Integration**

```python
@router.post("/submit")
async def submit_order(order: OrderRequest):
    # Would integrate with OrderExecutor
    # Missing: Alpaca broker connection, order execution logic
    return {
        "order_id": "mock_123",
        "status": "submitted",
    }
```

### 5. **SSE Missing Event Bus**

```python
async def event_generator():
    while True:
        # Would integrate with EventBus
        # Missing: Real event subscriptions, filtering
        data = {
            "type": "pnl_update",
            "equity": 100000.0,  # Hardcoded!
            "pnl": 0.0,          # Hardcoded!
        }
        yield f"data: {json.dumps(data)}\n\n"
```

### 6. **No Dashboard Template**

The dashboard route exists but requires HTML template:
```python
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return app.state.templates.TemplateResponse("dashboard.html", ...)
```

---

## Plugin Implementation Status Summary

### By Category

| Category | Total | Full | Stub | Percent |
|----------|-------|------|------|---------|
| Alpha Signals | 13 | 4 | 9 | 31% |
| Feature Engineering | 10 | 3 | 7 | 30% |
| Risk Management | 10 | 7 | 3 | 70% |
| AI/ML | 17 | 8 | 9 | 47% |
| Execution | 3 | 3 | 0 | 100% |
| Infrastructure | 10 | 9 | 1 | 90% |
| Diagnostics | 5 | 4 | 1 | 80% |
| UX/UI | 7 | 6 | 1 | 86% |
| **TOTAL** | **75** | **44** | **31** | **59%** |

### Plugins Requiring External Data/APIs

The following stubs need external API integration:

1. **Google Trends API**: `alpha_google_trends`, `ai_topic_clustering`
2. **Earnings Data**: `alpha_analyst_revisions`, `alpha_whisper_spread`
3. **Options Data**: `alpha_risk_reversal`
4. **ETF Flow Data**: `alpha_etf_flow_div`
5. **L2 Order Book**: `alpha_micro_imbalance`, `alpha_vpin`
6. **News Data**: `fe_price_news_div`, `ai_news_vectors`, `ai_shap_drift`
7. **Tick Data**: `fe_dollar_bars`, `alpha_vpin`
8. **ML Models**: `ml_lgbm_quantize`, `ml_onnx_runtime`
9. **Discord API**: `ux_discord_cmds`

---

## Recommended Next Steps

### Priority 1: Core API Integration (Critical)
1. **Implement Config Management**
   - Database persistence
   - Version tracking
   - Runtime config updates

2. **Implement Feature Flags**
   - Toggle persistence
   - Registry integration
   - Hot reload support

3. **Implement Event Bus**
   - Real-time event streaming
   - SSE support
   - Event filtering

4. **Implement Broker Integration**
   - Alpaca API integration
   - Order execution
   - Order status tracking

### Priority 2: Metrics Collection
1. Real-time portfolio calculations
2. PnL tracking
3. Risk metric calculations
4. Plugin execution monitoring

### Priority 3: Complete Stub Plugins
1. Set up required external APIs
2. Implement data fetching
3. Test end-to-end flows

### Priority 4: Frontend
1. Create dashboard HTML template
2. Implement HTMX interactions
3. Real-time chart updates via SSE

---

## Code Quality Notes

### Well-Implemented
- Plugin base class and registry system
- Async/await throughout
- Error handling with custom exceptions
- Resource budget enforcement
- Comprehensive logging

### Areas Needing Work
- API endpoints lack actual business logic
- Configuration not persisted
- No database integration yet
- No real-time calculations
- Mock data everywhere

---

## Summary

**OptiFIRE** is a sophisticated trading system framework with:

✅ **75 plugins** scaffolded and ready
✅ **44 fully implemented** with working logic
✅ **31 functional stubs** with proper structure
✅ **Clean REST API** with 16+ endpoints
✅ **JWT authentication** with TOTP support

⚠️ **But needs**:
- API integration with core systems
- Database persistence
- Real broker integration
- Real-time data collection
- External API integrations

The foundation is solid. The missing pieces are primarily integrations with external services and core system components.


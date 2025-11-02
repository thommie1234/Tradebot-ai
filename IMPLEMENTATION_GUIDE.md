# Plugin Implementation Guide

## Implemented Plugins (Full Working Code)

The following plugins have been fully implemented with working logic:

### ✅ alpha_vix_regime
**File**: `optifire/plugins/alpha_vix_regime/impl.py`

**What it does**:
- Fetches current VIX value from market data
- Classifies market regime: low_vol, normal, elevated, crisis
- Returns exposure multiplier and signal
- Stores in database and publishes to event bus

**Key logic**:
```python
if vix < 15:   regime = "low_vol", multiplier = 1.2
if vix < 25:   regime = "normal", multiplier = 1.0  
if vix < 35:   regime = "elevated", multiplier = 0.7
if vix >= 35:  regime = "crisis", multiplier = 0.3
```

### ✅ infra_psutil_health
**File**: `optifire/plugins/infra_psutil_health/impl.py`

**What it does**:
- Monitors CPU, memory, threads, file descriptors
- Checks against thresholds (900 MB RAM, 90% CPU)
- Logs warnings if exceeded
- Publishes health events

## Implementation Pattern

All plugins follow this structure:

```python
from typing import Dict, Any
from optifire.plugins import Plugin, PluginMetadata, PluginContext, PluginResult
from optifire.core.logger import logger

class YourPlugin(Plugin):
    """Your plugin description."""
    
    def __init__(self):
        """Initialize plugin with any state."""
        super().__init__()
        # Your initialization
    
    def describe(self) -> PluginMetadata:
        """Describe capabilities."""
        return PluginMetadata(
            plugin_id="your_plugin",
            name="Your Plugin",
            category="alpha",  # or fe, risk, ml, etc.
            version="1.0.0",
            author="OptiFIRE",
            description="What it does",
            inputs=["what_it_needs"],
            outputs=["what_it_produces"],
            est_cpu_ms=500,  # Estimate
            est_mem_mb=30,   # Estimate
        )
    
    def plan(self) -> Dict[str, Any]:
        """Define when to run."""
        return {
            "schedule": "@open",  # or @close, @idle, cron, interval_Xm
            "triggers": ["market_open"],
            "dependencies": ["market_data"],
        }
    
    async def run(self, context: PluginContext) -> PluginResult:
        """Execute your logic."""
        try:
            logger.info(f"Running {self.metadata.plugin_id}...")
            
            # 1. Get data from context
            # context.config - configuration
            # context.db - database
            # context.bus - event bus
            # context.data - shared data dict
            
            # 2. Do your computation
            result = your_algorithm()
            
            # 3. Store in database (optional)
            if context.db:
                await context.db.execute("INSERT INTO ...", (...))
            
            # 4. Publish event (optional)
            if context.bus:
                await context.bus.publish("event_type", data, source="your_plugin")
            
            # 5. Return success
            return PluginResult(
                success=True,
                data={
                    "plugin_id": "your_plugin",
                    # your results
                },
            )
            
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            return PluginResult(success=False, error=str(e))
```

## How to Implement More Plugins

### 1. Choose a Plugin
Pick from the 75 plugins in `optifire/plugins/*/`

### 2. Edit impl.py
Replace the stub in `impl.py` with real logic

### 3. Use Helper Modules

Available helpers:
- `optifire.data.feeds.DataFeed` - Market data
- `optifire.fe.engineering.FeatureEngineer` - Technical indicators
- `optifire.ops.health.HealthMonitor` - System health
- `optifire.risk.engine.RiskEngine` - Risk checks
- `optifire.exec.broker_alpaca.AlpacaBroker` - Trading

### 4. Test
```bash
pytest optifire/plugins/your_plugin/tests/
```

### 5. Enable
Edit `configs/features.yaml`:
```yaml
plugins:
  your_plugin:
    enabled: true
```

## Example Implementations

### Alpha Plugin Example (Mean Reversion)
```python
async def run(self, context: PluginContext) -> PluginResult:
    # Get price data
    feed = DataFeed()
    df = await feed.get_bars("SPY", limit=50)
    
    # Calculate indicator
    fe = FeatureEngineer()
    sma_20 = df["close"].rolling(20).mean()
    current = df["close"].iloc[-1]
    
    # Generate signal
    if current < sma_20.iloc[-1] * 0.98:  # 2% below SMA
        signal = 1.0  # Buy
    elif current > sma_20.iloc[-1] * 1.02:  # 2% above SMA
        signal = -1.0  # Sell
    else:
        signal = 0.0  # Neutral
    
    return PluginResult(
        success=True,
        data={"signal": signal, "sma_20": sma_20.iloc[-1]},
    )
```

### Risk Plugin Example (Volatility Scaling)
```python
async def run(self, context: PluginContext) -> PluginResult:
    # Get returns
    feed = DataFeed()
    df = await feed.get_bars("SPY", limit=100)
    
    fe = FeatureEngineer()
    returns = fe.calculate_returns(df["close"])
    vol = fe.calculate_volatility(returns, window=20)
    
    # Target vol is 15% annualized
    target_vol = 0.15
    current_vol = vol.iloc[-1]
    
    # Scale position size inversely with vol
    vol_scalar = target_vol / current_vol if current_vol > 0 else 1.0
    vol_scalar = min(max(vol_scalar, 0.5), 2.0)  # Bound 0.5x - 2.0x
    
    return PluginResult(
        success=True,
        data={"vol_scalar": vol_scalar, "current_vol": current_vol},
    )
```

### Feature Engineering Plugin Example
```python
async def run(self, context: PluginContext) -> PluginResult:
    # Get data from shared context
    df = context.data.get("market_data")
    
    if df is None:
        return PluginResult(success=False, error="No market data")
    
    # Calculate features
    fe = FeatureEngineer()
    
    features = {
        "rsi_14": fe.calculate_rsi(df["close"], 14).iloc[-1],
        "atr_14": fe.calculate_atr(df["high"], df["low"], df["close"], 14).iloc[-1],
        "vol_20": fe.calculate_volatility(df["close"].pct_change(), 20).iloc[-1],
    }
    
    # Store in shared context for other plugins
    context.data["features"] = features
    
    # Also store in DB
    for name, value in features.items():
        await context.db.execute(
            "INSERT INTO features (symbol, feature_name, value) VALUES (?, ?, ?)",
            ("SPY", name, value),
        )
    
    return PluginResult(success=True, data=features)
```

## Quick Reference

### Schedules
- `@open` - Market open (9:30 AM ET)
- `@close` - Market close (4:00 PM ET)
- `@idle` - During off-hours
- `interval_1m` - Every 1 minute
- `interval_5m` - Every 5 minutes
- `interval_1h` - Every hour
- `0 9 * * *` - Cron: 9 AM daily

### Categories
- `alpha` - Signal generation
- `fe` - Feature engineering
- `risk` - Risk management
- `ml` - Machine learning
- `ai` - AI/LLM features
- `exec` - Execution
- `ux` - User interface
- `diag` - Diagnostics
- `infra` - Infrastructure

### Context Fields
- `context.config` - Config dictionary
- `context.db` - Database instance
- `context.bus` - Event bus
- `context.data` - Shared data dict

## Priority Plugins to Implement

High priority (implement these first):

1. **risk_drawdown_derisk** - Critical safety
2. **exec_batch_orders** - Core execution
3. **alpha_vix_regime** - ✅ DONE
4. **infra_psutil_health** - ✅ DONE
5. **fe_kalman** - Useful filtering
6. **risk_vol_target** - Position sizing
7. **alpha_cross_asset_corr** - Diversification
8. **diag_slippage_report** - Cost analysis

Medium priority:
- ML plugins (if you have trained models)
- Advanced alpha plugins (require backtesting)
- UI plugins (nice to have)

Low priority:
- Experimental features
- Research plugins
- Advanced diagnostics

## Tips

1. **Start simple**: Implement basic version first, refine later
2. **Test with paper trading**: Never go live without testing
3. **Monitor resources**: Check CPU/RAM usage with each plugin
4. **Backtest**: Validate signals before enabling
5. **Version control**: Commit after each working plugin
6. **Document**: Update plugin README.md with actual behavior

## Need Help?

Check existing implementations:
- `optifire/plugins/alpha_vix_regime/impl.py` - Alpha example
- `optifire/plugins/infra_psutil_health/impl.py` - Infra example

Helper modules:
- `optifire/data/feeds.py` - Market data fetching
- `optifire/fe/engineering.py` - Technical indicators
- `optifire/risk/engine.py` - Risk checks

Core docs:
- `README.md` - Main documentation
- `DEPLOYMENT.md` - Deployment guide

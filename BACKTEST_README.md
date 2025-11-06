# OptiFIRE Backtesting Framework

Volledig backtesting framework om je trading strategieën te testen op historische data voordat je live gaat.

## ✨ Features

- **Historische data loading** van Alpaca (dagelijkse bars)
- **Event-driven simulatie** met realistische fills
- **Stop loss & take profit** automatisch gemanaged
- **Commission & slippage modeling** voor realistische resultaten
- **Performance metrics**: Sharpe ratio, max drawdown, win rate, profit factor
- **Visualisaties**: Equity curve, drawdown plot, trade analysis, monthly returns

## 🚀 Quick Start

### Basis gebruik

```bash
# Run backtest met default settings (laatste 6 maanden, simple strategy)
python3 run_backtest.py

# Trend following strategie (heel 2024)
python3 run_backtest.py --strategy trend --start 2024-01-01

# Custom capital en symbols
python3 run_backtest.py --strategy momentum --capital 50000 --symbols "SPY,QQQ,NVDA"
```

### Beschikbare strategieën

1. **simple** - Momentum + Mean Reversion met MA crossover en RSI
2. **trend** - Dual moving average trend following
3. **momentum** - Buy winners, sell losers
4. **mean_reversion** - Bollinger Bands oversold/overbought
5. **buy_hold** - Buy and hold voor benchmarking

## 📊 Output

Na een backtest krijg je:

```
backtest_results/
├── backtest_equity.png     # Equity curve + drawdown plot
├── backtest_trades.png     # Trade analysis (P&L, cumulative, distribution)
├── backtest_monthly.png    # Monthly returns bar chart
├── metrics.json            # Alle performance metrics
└── trades.csv              # Gedetailleerde trade log
```

## 📈 Performance Metrics

De backtest berekent automatisch:

**Returns:**
- Total return (%)
- Total P&L ($)

**Trade Statistics:**
- Win rate (%)
- Average win/loss
- Profit factor (wins/losses ratio)

**Risk Metrics:**
- Max drawdown (%)
- Sharpe ratio (risk-adjusted return)
- Sortino ratio (downside risk)

## ⚙️ Configuratie

### Risk Parameters (in BacktestConfig)

```python
max_position_size = 0.10     # 10% per positie
max_total_exposure = 0.30    # 30% totaal belegd
stop_loss_pct = 0.03         # 3% stop loss
take_profit_pct = 0.07       # 7% take profit
commission = 0.0             # $0 per aandeel (paper trading)
slippage_bps = 5.0           # 0.05% slippage
```

## 🎯 Interpretatie Resultaten

### Sharpe Ratio
- **< 0**: Strategie slechter dan risicovrij
- **0-1**: Matig
- **1-2**: Goed
- **> 2**: Uitstekend

### Max Drawdown
- **< -5%**: Excellent
- **-5% tot -10%**: Goed
- **-10% tot -20%**: Acceptabel
- **> -20%**: Risicovol

### Win Rate
- **> 60%**: Uitstekend
- **50-60%**: Goed
- **40-50%**: Acceptabel (met goede profit factor)
- **< 40%**: Risicovol (tenzij avg_win >> avg_loss)

## 🔧 Eigen Strategie Maken

Maak een nieuwe strategie in `optifire/backtest/strategies.py`:

```python
class MyStrategy:
    def __init__(self):
        self.price_history = {}

    async def generate_signals(self, timestamp, price_data):
        """
        Args:
            timestamp: Current datetime
            price_data: Dict of {symbol: {open, high, low, close, volume}}

        Returns:
            List of signals: [
                {
                    "symbol": "AAPL",
                    "action": "BUY" or "SELL",
                    "confidence": 0.0-1.0,
                    "reason": "Why this trade"
                }
            ]
        """
        signals = []

        for symbol, data in price_data.items():
            # Jouw logica hier
            if should_buy(data):
                signals.append({
                    "symbol": symbol,
                    "action": "BUY",
                    "confidence": 0.8,
                    "reason": "My signal",
                })

        return signals
```

Dan voeg toe aan `run_backtest.py`:

```python
STRATEGIES = {
    ...
    "my_strategy": MyStrategy,
}
```

## 📝 Voorbeelden

### Test je huidige live strategie

```bash
# Backtest de laatste 3 maanden met je watchlist
python3 run_backtest.py --start 2024-08-01 --symbols "NVDA,TSLA,AAPL,MSFT,GOOGL,META,AMZN"
```

### Vergelijk strategieën

```bash
# Trend following
python3 run_backtest.py --strategy trend --start 2024-01-01 --output results_trend

# Momentum
python3 run_backtest.py --strategy momentum --start 2024-01-01 --output results_momentum

# Buy & Hold benchmark
python3 run_backtest.py --strategy buy_hold --start 2024-01-01 --output results_benchmark
```

### Optimize parameters

Pas `BacktestConfig` aan in `run_backtest.py` om verschillende settings te testen:

```python
config = BacktestConfig(
    start_date=start_date,
    end_date=end_date,
    initial_capital=args.capital,
    symbols=symbols,
    stop_loss_pct=0.05,      # Test met 5% stop loss
    take_profit_pct=0.10,    # Test met 10% take profit
)
```

## ⚠️ Belangrijke Notes

1. **Paper trading eerst**: Backtest resultaten zijn GEEN garantie voor toekomstige performance
2. **Overfitting**: Test niet teveel parameter combinaties (curve fitting)
3. **Survivorship bias**: Alpaca data bevat geen delisted stocks
4. **Slippage & fees**: Real trading heeft meer kosten
5. **Forward testing**: Doe altijd paper trading voordat je live gaat

## 🛠 Technische Details

**Data source:** Alpaca Markets API (gratis met account)
**Timeframe:** Daily bars
**Execution:** Market orders met slippage modeling
**Position sizing:** Confidence-based (higher confidence = larger position)

## 💡 Tips

1. **Start klein**: Test eerst korte periodes (1-3 maanden)
2. **Multiple symbols**: Diversificatie verbetert risk-adjusted returns
3. **Compare to benchmark**: Is je strategie beter dan buy & hold?
4. **Check drawdowns**: Max drawdown moet acceptabel zijn voor jou
5. **Win rate ≠ profit**: Lage win rate kan ok zijn met goede profit factor

## 📚 Volgende Stappen

1. ✅ Run backtest op je strategieën
2. ✅ Analyseer de resultaten (metrics + charts)
3. ✅ Optimize parameters indien nodig
4. ✅ Paper trade 2-4 weken om te valideren
5. ✅ Start live trading met klein kapitaal

Veel succes! 🚀

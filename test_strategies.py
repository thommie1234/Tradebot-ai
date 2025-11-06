#!/usr/bin/env python3
"""
Test Multiple Trading Strategies
"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Config
INITIAL_CAPITAL = 10000
SYMBOLS = ["SPY", "QQQ", "AAPL", "NVDA", "TSLA", "MSFT", "GOOGL", "META", "AMZN"]
START_DATE = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")
END_DATE = datetime.now().strftime("%Y-%m-%d")

# Best params from optimizer
POSITION_SIZE = 0.05
MAX_POSITIONS = 2
STOP_LOSS = 0.015
TAKE_PROFIT = 0.10

print("="*70)
print("STRATEGY COMPARISON - Testing Different Approaches")
print("="*70)
print(f"Period: {START_DATE} to {END_DATE}")
print(f"Capital: ${INITIAL_CAPITAL:,.2f}")
print("="*70 + "\n")

# Download data
print("📊 Downloading data...")
data = {}
for symbol in SYMBOLS:
    try:
        df = yf.download(symbol, start=START_DATE, end=END_DATE, progress=False)
        if not df.empty:
            # Calculate indicators
            df['SMA_20'] = df['Close'].rolling(20).mean()
            df['SMA_50'] = df['Close'].rolling(50).mean()
            df['RSI'] = calculate_rsi(df['Close'], 14)
            df['MACD'], df['Signal'] = calculate_macd(df['Close'])
            df['BB_upper'], df['BB_lower'] = calculate_bollinger(df['Close'], 20)
            data[symbol] = df
    except:
        pass

print(f"✓ Loaded {len(data)} symbols\n")

def calculate_rsi(prices, period=14):
    """Calculate RSI"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(prices, fast=12, slow=26, signal=9):
    """Calculate MACD"""
    ema_fast = prices.ewm(span=fast).mean()
    ema_slow = prices.ewm(span=slow).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal).mean()
    return macd, signal_line

def calculate_bollinger(prices, period=20, std_dev=2):
    """Calculate Bollinger Bands"""
    sma = prices.rolling(period).mean()
    std = prices.rolling(period).std()
    upper = sma + (std * std_dev)
    lower = sma - (std * std_dev)
    return upper, lower

def run_strategy(signal_func, name):
    """Run backtest with custom signal function"""
    capital = INITIAL_CAPITAL
    positions = {}
    trades = []
    equity_curve = [INITIAL_CAPITAL]
    dates = pd.date_range(START_DATE, END_DATE, freq='D')

    for date in dates:
        if date.weekday() >= 5:
            continue

        # Calculate equity
        current_equity = capital
        for symbol, pos in list(positions.items()):
            if symbol in data and date in data[symbol].index:
                current_price = float(data[symbol].loc[date, 'Close'])
                pos['current_value'] = pos['shares'] * current_price
                current_equity += pos['current_value']

                pnl_pct = (current_price - pos['entry_price']) / pos['entry_price']

                # Stop loss / Take profit
                if pnl_pct <= -STOP_LOSS:
                    capital += pos['shares'] * current_price
                    trades.append({'pnl': pos['shares'] * (current_price - pos['entry_price'])})
                    del positions[symbol]
                elif pnl_pct >= TAKE_PROFIT:
                    capital += pos['shares'] * current_price
                    trades.append({'pnl': pos['shares'] * (current_price - pos['entry_price'])})
                    del positions[symbol]

        # Generate signals
        if len(positions) < MAX_POSITIONS:
            for symbol in SYMBOLS:
                if symbol in positions or symbol not in data:
                    continue
                if date not in data[symbol].index:
                    continue

                df = data[symbol]
                if signal_func(df, date):  # Custom signal
                    current_price = float(df.loc[date, 'Close'])
                    position_value = current_equity * POSITION_SIZE
                    shares = int(position_value / current_price)

                    if shares > 0 and capital >= shares * current_price:
                        capital -= shares * current_price
                        positions[symbol] = {
                            'entry_price': current_price,
                            'shares': shares,
                            'entry_date': date
                        }
                        if len(positions) >= MAX_POSITIONS:
                            break

        equity_curve.append(current_equity)

    # Close positions
    final_equity = capital
    for symbol, pos in positions.items():
        if symbol in data:
            final_price = float(data[symbol].iloc[-1]['Close'])
            final_equity += pos['shares'] * final_price

    # Metrics
    total_return = ((final_equity - INITIAL_CAPITAL) / INITIAL_CAPITAL) * 100
    winning = [t for t in trades if t['pnl'] > 0]
    losing = [t for t in trades if t['pnl'] < 0]
    win_rate = (len(winning) / len(trades) * 100) if trades else 0

    equity_series = pd.Series(equity_curve)
    rolling_max = equity_series.expanding().max()
    drawdowns = (equity_series - rolling_max) / rolling_max
    max_dd = drawdowns.min() * 100

    returns = equity_series.pct_change().dropna()
    sharpe = (returns.mean() / returns.std() * np.sqrt(252)) if len(returns) > 0 and returns.std() > 0 else 0

    return {
        'name': name,
        'return': total_return,
        'max_dd': max_dd,
        'win_rate': win_rate,
        'trades': len(trades),
        'sharpe': sharpe,
        'final': final_equity,
        'score': total_return - abs(max_dd) + (sharpe * 10)
    }

# Strategy 1: Momentum (20-day breakout)
def momentum_signal(df, date):
    recent = df.loc[:date].tail(20)
    if len(recent) < 20:
        return False
    current = float(df.loc[date, 'Close'])
    high_20 = float(recent['High'].max())
    return current >= high_20 * 0.98

# Strategy 2: RSI Oversold
def rsi_signal(df, date):
    if date not in df.index or pd.isna(df.loc[date, 'RSI']):
        return False
    rsi = float(df.loc[date, 'RSI'])
    return rsi < 30  # Oversold

# Strategy 3: MACD Crossover
def macd_signal(df, date):
    if date not in df.index:
        return False
    if pd.isna(df.loc[date, 'MACD']) or pd.isna(df.loc[date, 'Signal']):
        return False

    idx = df.index.get_loc(date)
    if idx == 0:
        return False

    prev_date = df.index[idx - 1]
    macd_now = float(df.loc[date, 'MACD'])
    signal_now = float(df.loc[date, 'Signal'])
    macd_prev = float(df.loc[prev_date, 'MACD'])
    signal_prev = float(df.loc[prev_date, 'Signal'])

    # Bullish crossover
    return macd_prev < signal_prev and macd_now > signal_now

# Strategy 4: Mean Reversion (Bollinger)
def mean_reversion_signal(df, date):
    if date not in df.index:
        return False
    if pd.isna(df.loc[date, 'BB_lower']):
        return False
    current = float(df.loc[date, 'Close'])
    bb_lower = float(df.loc[date, 'BB_lower'])
    return current < bb_lower  # Price below lower band

# Strategy 5: Trend Following (SMA crossover)
def trend_signal(df, date):
    if date not in df.index:
        return False
    if pd.isna(df.loc[date, 'SMA_20']) or pd.isna(df.loc[date, 'SMA_50']):
        return False

    idx = df.index.get_loc(date)
    if idx == 0:
        return False

    prev_date = df.index[idx - 1]
    sma20_now = float(df.loc[date, 'SMA_20'])
    sma50_now = float(df.loc[date, 'SMA_50'])
    sma20_prev = float(df.loc[prev_date, 'SMA_20'])
    sma50_prev = float(df.loc[prev_date, 'SMA_50'])

    # Golden cross
    return sma20_prev < sma50_prev and sma20_now > sma50_now

# Strategy 6: Ensemble (combine signals)
def ensemble_signal(df, date):
    signals = 0
    if momentum_signal(df, date):
        signals += 1
    if rsi_signal(df, date):
        signals += 1
    if macd_signal(df, date):
        signals += 1
    return signals >= 2  # At least 2 agree

# Test all strategies
print("🚀 Testing strategies...\n")
strategies = [
    (momentum_signal, "Momentum (20D Breakout)"),
    (rsi_signal, "RSI Oversold (<30)"),
    (macd_signal, "MACD Crossover"),
    (mean_reversion_signal, "Mean Reversion (Bollinger)"),
    (trend_signal, "Trend (SMA Crossover)"),
    (ensemble_signal, "Ensemble (2+ signals)")
]

results = []
for signal_func, name in strategies:
    result = run_strategy(signal_func, name)
    results.append(result)
    print(f"✓ {name}")

# Sort by score
results_df = pd.DataFrame(results)
results_df = results_df.sort_values('score', ascending=False)

print("\n" + "="*70)
print("STRATEGY RANKINGS")
print("="*70 + "\n")

for i, row in results_df.iterrows():
    rank = results_df.index.get_loc(i) + 1
    emoji = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"#{rank}"
    print(f"{emoji} {row['name']}")
    print(f"   Return:      {row['return']:+.2f}%")
    print(f"   Max DD:      {row['max_dd']:.2f}%")
    print(f"   Win Rate:    {row['win_rate']:.1f}%")
    print(f"   Sharpe:      {row['sharpe']:.2f}")
    print(f"   Trades:      {int(row['trades'])}")
    print(f"   Score:       {row['score']:.2f}")
    print(f"   Final:       ${row['final']:,.2f}")
    print()

best = results_df.iloc[0]
print("="*70)
print("🏆 BEST STRATEGY")
print("="*70)
print(f"\n{best['name']}")
print(f"  Total Return:    {best['return']:+.2f}%")
print(f"  Max Drawdown:    {best['max_dd']:.2f}%")
print(f"  Win Rate:        {best['win_rate']:.1f}%")
print(f"  Sharpe Ratio:    {best['sharpe']:.2f}")
print(f"  Total Trades:    {int(best['trades'])}")
print(f"  Final Equity:    ${best['final']:,.2f}")
print(f"\n{'='*70}\n")

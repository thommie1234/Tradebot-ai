#!/usr/bin/env python3
"""
Strategy Optimizer - Tests multiple parameter combinations
"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from itertools import product
import warnings
warnings.filterwarnings('ignore')

# Config
INITIAL_CAPITAL = 10000
SYMBOLS = ["SPY", "QQQ", "AAPL", "NVDA", "TSLA", "MSFT", "GOOGL", "META", "AMZN"]
START_DATE = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")
END_DATE = datetime.now().strftime("%Y-%m-%d")

# Parameter grid to test
# Focus: More positions (diversification) with smaller sizes (risk control)
POSITION_SIZES = [0.02, 0.03, 0.04]  # 2%, 3%, 4% (smaller but more positions)
STOP_LOSSES = [0.015, 0.02, 0.025]  # 1.5%, 2%, 2.5%
TAKE_PROFITS = [0.08, 0.10, 0.12]  # 8%, 10%, 12%
MAX_POSITIONS_LIST = [5, 7, 10]  # More positions for diversification
TRAILING_STOPS = [True, False]

print("="*70)
print("STRATEGY OPTIMIZER - Finding Best Parameters")
print("="*70)
print(f"Period: {START_DATE} to {END_DATE}")
print(f"Initial Capital: ${INITIAL_CAPITAL:,.2f}")
print(f"\nTesting {len(POSITION_SIZES)} position sizes x {len(STOP_LOSSES)} stop losses")
print(f"x {len(TAKE_PROFITS)} take profits x {len(MAX_POSITIONS_LIST)} max positions")
print(f"x {len(TRAILING_STOPS)} trailing stop options")
total_tests = len(POSITION_SIZES) * len(STOP_LOSSES) * len(TAKE_PROFITS) * len(MAX_POSITIONS_LIST) * len(TRAILING_STOPS)
print(f"\nTotal combinations to test: {total_tests}")
print("="*70 + "\n")

# Download data once
print("📊 Downloading data from Yahoo Finance...")
data = {}
for symbol in SYMBOLS:
    try:
        df = yf.download(symbol, start=START_DATE, end=END_DATE, progress=False)
        if not df.empty:
            data[symbol] = df
    except:
        pass

print(f"✓ Loaded data for {len(data)} symbols\n")

def run_backtest(position_size, stop_loss, take_profit, max_positions, trailing_stop):
    """Run backtest with given parameters"""
    capital = INITIAL_CAPITAL
    positions = {}
    trades = []
    equity_curve = [INITIAL_CAPITAL]
    dates = pd.date_range(START_DATE, END_DATE, freq='D')

    for date in dates:
        if date.weekday() >= 5:
            continue

        # Calculate current equity
        current_equity = capital
        for symbol, pos in list(positions.items()):
            if symbol in data and date in data[symbol].index:
                current_price = float(data[symbol].loc[date, 'Close'])
                pos['current_value'] = pos['shares'] * current_price
                current_equity += pos['current_value']

                # Update highest price for trailing stop
                if 'highest_price' not in pos:
                    pos['highest_price'] = pos['entry_price']
                pos['highest_price'] = max(pos['highest_price'], current_price)

                pnl_pct = (current_price - pos['entry_price']) / pos['entry_price']

                # Trailing stop
                if trailing_stop and pos['highest_price'] > pos['entry_price']:
                    trailing_stop_price = pos['highest_price'] * (1 - stop_loss)
                    if current_price < trailing_stop_price:
                        capital += pos['shares'] * current_price
                        trades.append({
                            'pnl': pos['shares'] * (current_price - pos['entry_price'])
                        })
                        del positions[symbol]
                        continue

                # Stop loss
                if pnl_pct <= -stop_loss:
                    capital += pos['shares'] * current_price
                    trades.append({
                        'pnl': pos['shares'] * (current_price - pos['entry_price'])
                    })
                    del positions[symbol]

                # Take profit
                elif pnl_pct >= take_profit:
                    capital += pos['shares'] * current_price
                    trades.append({
                        'pnl': pos['shares'] * (current_price - pos['entry_price'])
                    })
                    del positions[symbol]

        # Generate signals
        if len(positions) < max_positions:
            for symbol in SYMBOLS:
                if symbol in positions or symbol not in data:
                    continue

                if date not in data[symbol].index:
                    continue

                df = data[symbol]
                recent = df.loc[:date].tail(20)

                if len(recent) < 20:
                    continue

                current_price = float(df.loc[date, 'Close'])
                twenty_day_high = float(recent['High'].max())

                # Buy signal: breaking 20-day high
                if current_price >= twenty_day_high * 0.98:
                    position_value = current_equity * position_size
                    shares = int(position_value / current_price)

                    if shares > 0 and capital >= shares * current_price:
                        capital -= shares * current_price
                        positions[symbol] = {
                            'entry_price': current_price,
                            'shares': shares,
                            'entry_date': date
                        }

                        if len(positions) >= max_positions:
                            break

        equity_curve.append(current_equity)

    # Close all positions
    final_equity = capital
    for symbol, pos in positions.items():
        if symbol in data:
            last_date = data[symbol].index[-1]
            final_price = float(data[symbol].loc[last_date, 'Close'])
            final_equity += pos['shares'] * final_price
            trades.append({
                'pnl': pos['shares'] * (final_price - pos['entry_price'])
            })

    # Calculate metrics
    total_return = ((final_equity - INITIAL_CAPITAL) / INITIAL_CAPITAL) * 100

    winning_trades = [t for t in trades if t.get('pnl', 0) > 0]
    losing_trades = [t for t in trades if t.get('pnl', 0) < 0]
    total_trades = len(trades)

    win_rate = (len(winning_trades) / total_trades * 100) if total_trades > 0 else 0

    # Max drawdown
    equity_series = pd.Series(equity_curve)
    rolling_max = equity_series.expanding().max()
    drawdowns = (equity_series - rolling_max) / rolling_max
    max_drawdown = drawdowns.min() * 100

    # Sharpe ratio (simplified)
    returns = equity_series.pct_change().dropna()
    sharpe = (returns.mean() / returns.std() * np.sqrt(252)) if len(returns) > 0 and returns.std() > 0 else 0

    return {
        'position_size': position_size,
        'stop_loss': stop_loss,
        'take_profit': take_profit,
        'max_positions': max_positions,
        'trailing_stop': trailing_stop,
        'total_return': total_return,
        'max_drawdown': max_drawdown,
        'win_rate': win_rate,
        'total_trades': total_trades,
        'sharpe': sharpe,
        'final_equity': final_equity,
        # Score: combine return, drawdown, sharpe
        'score': total_return - abs(max_drawdown) + (sharpe * 10)
    }

# Run all combinations
print("🚀 Testing all parameter combinations...\n")
results = []

test_num = 0
for pos_size, stop, tp, max_pos, trailing in product(
    POSITION_SIZES, STOP_LOSSES, TAKE_PROFITS, MAX_POSITIONS_LIST, TRAILING_STOPS
):
    test_num += 1
    result = run_backtest(pos_size, stop, tp, max_pos, trailing)
    results.append(result)

    if test_num % 20 == 0:
        print(f"Progress: {test_num}/{total_tests} tests completed...")

print(f"\n✓ Completed all {total_tests} tests!\n")

# Sort by score
results_df = pd.DataFrame(results)
results_df = results_df.sort_values('score', ascending=False)

# Show top 10
print("="*70)
print("TOP 10 BEST PARAMETER COMBINATIONS")
print("="*70)
print()

for i, row in results_df.head(10).iterrows():
    print(f"#{results_df.index.get_loc(i) + 1}:")
    print(f"  Position Size:   {row['position_size']*100:.1f}%")
    print(f"  Max Positions:   {row['max_positions']}")
    print(f"  Stop Loss:       {row['stop_loss']*100:.1f}%")
    print(f"  Take Profit:     {row['take_profit']*100:.1f}%")
    print(f"  Trailing Stop:   {row['trailing_stop']}")
    print(f"  📈 Return:       {row['total_return']:+.2f}%")
    print(f"  📉 Max DD:       {row['max_drawdown']:.2f}%")
    print(f"  ✅ Win Rate:     {row['win_rate']:.1f}%")
    print(f"  📊 Sharpe:       {row['sharpe']:.2f}")
    print(f"  🎯 Score:        {row['score']:.2f}")
    print(f"  💰 Final:        ${row['final_equity']:,.2f}")
    print()

# Best overall
best = results_df.iloc[0]
print("="*70)
print("🏆 WINNING STRATEGY")
print("="*70)
print(f"\nOptimal Parameters:")
print(f"  Position Size:   {best['position_size']*100:.1f}%")
print(f"  Max Positions:   {int(best['max_positions'])}")
print(f"  Stop Loss:       {best['stop_loss']*100:.1f}%")
print(f"  Take Profit:     {best['take_profit']*100:.1f}%")
print(f"  Trailing Stop:   {best['trailing_stop']}")
print(f"\nPerformance:")
print(f"  Total Return:    {best['total_return']:+.2f}%")
print(f"  Max Drawdown:    {best['max_drawdown']:.2f}%")
print(f"  Win Rate:        {best['win_rate']:.1f}%")
print(f"  Sharpe Ratio:    {best['sharpe']:.2f}")
print(f"  Total Trades:    {int(best['total_trades'])}")
print(f"  Final Equity:    ${best['final_equity']:,.2f}")

# Check if it meets our criteria
print(f"\n{'='*70}")
print("VERDICT:")
print("="*70)
if best['total_return'] > 5 and best['max_drawdown'] > -15 and best['sharpe'] > 0.5:
    print("✅ EXCELLENT - Ready for live trading!")
elif best['total_return'] > 3 and best['max_drawdown'] > -20:
    print("✓ GOOD - Consider paper trading first")
elif best['total_return'] > 0:
    print("⚠ ACCEPTABLE - Needs more optimization")
else:
    print("❌ POOR - Strategy needs major rework")

print("\n" + "="*70 + "\n")

# Save results
results_df.to_csv('optimization_results.csv', index=False)
print("📁 Full results saved to optimization_results.csv")

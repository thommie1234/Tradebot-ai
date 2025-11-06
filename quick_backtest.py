#!/usr/bin/env python3
"""
Quick backtest using Yahoo Finance (free data)
"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Config - OPTIMIZED for better risk-adjusted returns
INITIAL_CAPITAL = 10000
SYMBOLS = ["SPY", "QQQ", "AAPL", "NVDA", "TSLA", "MSFT", "GOOGL", "META", "AMZN"]
START_DATE = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")
END_DATE = datetime.now().strftime("%Y-%m-%d")
POSITION_SIZE = 0.05  # 5% per position (was 10% - reduced for safety)
MAX_POSITIONS = 3  # Max 3 positions = 15% total exposure (was unlimited)
STOP_LOSS = 0.02  # 2% tight stop (was 3%)
TAKE_PROFIT = 0.10  # 10% higher target (was 7%)
TRAILING_STOP = True  # Use trailing stop to lock in profits

print("="*60)
print("QUICK BACKTEST - Momentum Strategy")
print("="*60)
print(f"Period: {START_DATE} to {END_DATE}")
print(f"Initial Capital: ${INITIAL_CAPITAL:,.2f}")
print(f"Symbols: {', '.join(SYMBOLS)}")
print(f"Position Size: {POSITION_SIZE*100}%")
print(f"Max Positions: {MAX_POSITIONS}")
print(f"Stop Loss: {STOP_LOSS*100}%")
print(f"Take Profit: {TAKE_PROFIT*100}%")
print(f"Trailing Stop: {TRAILING_STOP}")
print("="*60 + "\n")

# Download data
print("📊 Downloading data from Yahoo Finance...")
data = {}
for symbol in SYMBOLS:
    try:
        df = yf.download(symbol, start=START_DATE, end=END_DATE, progress=False)
        if not df.empty:
            data[symbol] = df
            print(f"✓ {symbol}: {len(df)} days")
        else:
            print(f"✗ {symbol}: No data")
    except Exception as e:
        print(f"✗ {symbol}: {e}")

if not data:
    print("\n❌ No data available - cannot run backtest")
    exit(1)

print(f"\n✓ Loaded data for {len(data)} symbols\n")

# Simple momentum strategy
print("🚀 Running momentum strategy backtest...\n")

capital = INITIAL_CAPITAL
positions = {}  # {symbol: {entry_price, shares, entry_date, highest_price}}
trades = []
equity_curve = [INITIAL_CAPITAL]
dates = pd.date_range(START_DATE, END_DATE, freq='D')

for date in dates:
    # Skip weekends
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

            # Check stop loss / take profit
            pnl_pct = (current_price - pos['entry_price']) / pos['entry_price']

            # Trailing stop: if price is up, use trailing stop from highest
            if TRAILING_STOP and pos['highest_price'] > pos['entry_price']:
                trailing_stop_price = pos['highest_price'] * (1 - STOP_LOSS)
                if current_price < trailing_stop_price:
                    # Trailing stop hit
                    capital += pos['shares'] * current_price
                    trades.append({
                        'date': date,
                        'symbol': symbol,
                        'action': 'SELL',
                        'reason': 'TRAILING_STOP',
                        'pnl': pos['shares'] * (current_price - pos['entry_price'])
                    })
                    print(f"📉 {date.strftime('%Y-%m-%d')}: TRAILING STOP - {symbol} at ${current_price:.2f} ({pnl_pct*100:.1f}%)")
                    del positions[symbol]
                    continue

            if pnl_pct <= -STOP_LOSS:
                # Stop loss hit
                capital += pos['shares'] * current_price
                trades.append({
                    'date': date,
                    'symbol': symbol,
                    'action': 'SELL',
                    'reason': 'STOP_LOSS',
                    'pnl': pos['shares'] * (current_price - pos['entry_price'])
                })
                print(f"🛑 {date.strftime('%Y-%m-%d')}: STOP LOSS - {symbol} at ${current_price:.2f} ({pnl_pct*100:.1f}%)")
                del positions[symbol]

            elif pnl_pct >= TAKE_PROFIT:
                # Take profit hit
                capital += pos['shares'] * current_price
                trades.append({
                    'date': date,
                    'symbol': symbol,
                    'action': 'SELL',
                    'reason': 'TAKE_PROFIT',
                    'pnl': pos['shares'] * (current_price - pos['entry_price'])
                })
                print(f"💰 {date.strftime('%Y-%m-%d')}: TAKE PROFIT - {symbol} at ${current_price:.2f} (+{pnl_pct*100:.1f}%)")
                del positions[symbol]

    # Generate signals (simple momentum: 20-day high)
    if len(positions) < MAX_POSITIONS:  # Respect position limit
        for symbol in SYMBOLS:
            if symbol in positions or symbol not in data:
                continue

            if date not in data[symbol].index:
                continue

            df = data[symbol]
            # Get last 20 days
            recent = df.loc[:date].tail(20)

            if len(recent) < 20:
                continue

            current_price = float(df.loc[date, 'Close'])
            twenty_day_high = float(recent['High'].max())

            # Buy signal: breaking 20-day high
            if current_price >= twenty_day_high * 0.98:  # Within 2% of high
                position_value = current_equity * POSITION_SIZE
                shares = int(position_value / current_price)

                if shares > 0 and capital >= shares * current_price:
                    capital -= shares * current_price
                    positions[symbol] = {
                        'entry_price': current_price,
                        'shares': shares,
                        'entry_date': date
                    }
                    trades.append({
                        'date': date,
                        'symbol': symbol,
                        'action': 'BUY',
                        'reason': '20D_BREAKOUT',
                        'pnl': 0
                    })
                    print(f"🚀 {date.strftime('%Y-%m-%d')}: BUY {symbol} @ ${current_price:.2f} ({shares} shares)")

    equity_curve.append(current_equity)

# Close all positions at end
final_equity = capital
for symbol, pos in positions.items():
    if symbol in data:
        # Use last available date
        last_date = data[symbol].index[-1]
        final_price = float(data[symbol].loc[last_date, 'Close'])
        final_equity += pos['shares'] * final_price
        trades.append({
            'date': END_DATE,
            'symbol': symbol,
            'action': 'SELL',
            'reason': 'END_OF_BACKTEST',
            'pnl': pos['shares'] * (final_price - pos['entry_price'])
        })

# Calculate metrics
total_return = ((final_equity - INITIAL_CAPITAL) / INITIAL_CAPITAL) * 100
total_pnl = final_equity - INITIAL_CAPITAL

winning_trades = [t for t in trades if t.get('pnl', 0) > 0]
losing_trades = [t for t in trades if t.get('pnl', 0) < 0]
total_trades = len([t for t in trades if 'pnl' in t and t['action'] == 'SELL'])

win_rate = (len(winning_trades) / total_trades * 100) if total_trades > 0 else 0

# Max drawdown
equity_series = pd.Series(equity_curve)
rolling_max = equity_series.expanding().max()
drawdowns = (equity_series - rolling_max) / rolling_max
max_drawdown = drawdowns.min() * 100

print("\n" + "="*60)
print("BACKTEST RESULTS")
print("="*60)
print(f"\n💰 Final Equity:       ${final_equity:,.2f}")
print(f"📈 Total Return:       {total_return:+.2f}%")
print(f"💵 Total P&L:          ${total_pnl:+,.2f}")
print(f"\n📊 Trading Stats:")
print(f"   Total Trades:       {total_trades}")
print(f"   Winning Trades:     {len(winning_trades)}")
print(f"   Losing Trades:      {len(losing_trades)}")
print(f"   Win Rate:           {win_rate:.1f}%")
print(f"   Max Drawdown:       {max_drawdown:.2f}%")

if winning_trades:
    avg_win = sum(t['pnl'] for t in winning_trades) / len(winning_trades)
    print(f"   Avg Win:            ${avg_win:,.2f}")
if losing_trades:
    avg_loss = sum(t['pnl'] for t in losing_trades) / len(losing_trades)
    print(f"   Avg Loss:           ${avg_loss:,.2f}")

print("\n" + "="*60)
print("VERDICT")
print("="*60)

if total_return > 20 and win_rate > 50 and max_drawdown > -15:
    print("✅ EXCELLENT - Strong performance!")
elif total_return > 10 and win_rate > 40:
    print("✓ GOOD - Decent results")
elif total_return > 0:
    print("⚠ MEDIOCRE - Slightly profitable")
else:
    print("❌ POOR - Strategy loses money")

print("\n" + "="*60 + "\n")

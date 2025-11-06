#!/usr/bin/env python3
"""
IPO Trading Strategy Backtest

Tests IPO first-day trading strategy on real historical IPO data.
"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Known recent IPOs with their IPO dates
# Format: (symbol, ipo_date, company_name)
RECENT_IPOS = [
    # 2024 IPOs
    ("RDDT", "2024-03-21", "Reddit"),
    ("ASML", "2024-01-15", "ASML (secondary)"),
    ("ARM", "2023-09-14", "ARM Holdings"),
    ("BIRK", "2023-10-19", "Birkenstock"),
    ("KVUE", "2023-05-04", "Kenvue"),
    ("VFS", "2023-06-28", "VinFast"),
    ("FYBR", "2023-10-05", "Frontier Communications"),

    # Earlier high-profile IPOs for testing
    ("COIN", "2021-04-14", "Coinbase"),
    ("RBLX", "2021-03-10", "Roblox"),
    ("ABNB", "2020-12-10", "Airbnb"),
    ("SNOW", "2020-09-16", "Snowflake"),
    ("PLTR", "2020-09-30", "Palantir"),
    ("U", "2019-05-10", "Unity"),
    ("UBER", "2019-05-10", "Uber"),
    ("LYFT", "2019-03-29", "Lyft"),
    ("PINS", "2019-04-18", "Pinterest"),
    ("ZM", "2019-04-18", "Zoom"),
]

# Strategy parameters
INITIAL_CAPITAL = 10000
POSITION_SIZE = 0.08  # 8% per IPO (higher risk = smaller size)
STOP_LOSS = 0.05  # 5% stop (IPOs volatile)
TAKE_PROFIT = 0.20  # 20% target (IPOs can pop hard)
HOLDING_DAYS = 5  # Max hold period (exit after 5 days regardless)

print("="*70)
print("IPO FIRST-DAY TRADING BACKTEST")
print("="*70)
print(f"Initial Capital: ${INITIAL_CAPITAL:,.2f}")
print(f"Position Size:   {POSITION_SIZE*100}%")
print(f"Stop Loss:       {STOP_LOSS*100}%")
print(f"Take Profit:     {TAKE_PROFIT*100}%")
print(f"Max Hold:        {HOLDING_DAYS} days")
print(f"Testing {len(RECENT_IPOS)} IPOs")
print("="*70 + "\n")

# Strategy: Buy on IPO day, sell on:
# 1. +20% (take profit)
# 2. -5% (stop loss)
# 3. Day 5 (max hold)

capital = INITIAL_CAPITAL
positions = []
trades = []

print("🚀 Simulating IPO trades...\n")

for symbol, ipo_date_str, company in RECENT_IPOS:
    try:
        # Download data starting from IPO date
        ipo_date = datetime.strptime(ipo_date_str, "%Y-%m-%d")
        end_date = ipo_date + timedelta(days=30)  # Get 30 days post-IPO

        df = yf.download(symbol, start=ipo_date_str, end=end_date.strftime("%Y-%m-%d"), progress=False)

        if df.empty or len(df) < 2:
            print(f"⚠️  {symbol} ({company}): No data available")
            continue

        # Get IPO day price (first available close)
        ipo_day = df.index[0]
        entry_price = float(df.iloc[0]['Close'])

        # Calculate position
        position_value = capital * POSITION_SIZE
        shares = int(position_value / entry_price)

        if shares == 0 or capital < shares * entry_price:
            print(f"⚠️  {symbol} ({company}): Insufficient capital")
            continue

        # Deduct from capital
        capital -= shares * entry_price

        # Track position
        entry_date = ipo_day
        exit_price = None
        exit_date = None
        exit_reason = None

        # Simulate holding
        for i in range(1, min(len(df), HOLDING_DAYS + 1)):
            current_date = df.index[i]
            current_price = float(df.iloc[i]['Close'])

            pnl_pct = (current_price - entry_price) / entry_price

            # Check exit conditions
            if pnl_pct >= TAKE_PROFIT:
                # Take profit
                exit_price = current_price
                exit_date = current_date
                exit_reason = "TAKE_PROFIT"
                break
            elif pnl_pct <= -STOP_LOSS:
                # Stop loss
                exit_price = current_price
                exit_date = current_date
                exit_reason = "STOP_LOSS"
                break
            elif i == HOLDING_DAYS:
                # Max hold reached
                exit_price = current_price
                exit_date = current_date
                exit_reason = "MAX_HOLD"
                break

        # If still holding (ran out of data), close at last price
        if exit_price is None:
            exit_price = float(df.iloc[-1]['Close'])
            exit_date = df.index[-1]
            exit_reason = "END_OF_DATA"

        # Calculate P&L
        pnl = shares * (exit_price - entry_price)
        pnl_pct = (exit_price - entry_price) / entry_price

        # Return capital
        capital += shares * exit_price

        # Record trade
        trades.append({
            'symbol': symbol,
            'company': company,
            'entry_date': entry_date,
            'exit_date': exit_date,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'shares': shares,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'reason': exit_reason,
            'hold_days': (exit_date - entry_date).days
        })

        # Log trade
        emoji = "💰" if pnl > 0 else "🛑"
        print(f"{emoji} {symbol} ({company})")
        print(f"   Entry: {entry_date.strftime('%Y-%m-%d')} @ ${entry_price:.2f}")
        print(f"   Exit:  {exit_date.strftime('%Y-%m-%d')} @ ${exit_price:.2f} ({exit_reason})")
        print(f"   P&L:   {pnl_pct*100:+.1f}% (${pnl:+,.2f})")
        print(f"   Held:  {(exit_date - entry_date).days} days")
        print()

    except Exception as e:
        print(f"❌ {symbol} ({company}): Error - {e}\n")

# Calculate final metrics
final_equity = capital
total_return = ((final_equity - INITIAL_CAPITAL) / INITIAL_CAPITAL) * 100

winning_trades = [t for t in trades if t['pnl'] > 0]
losing_trades = [t for t in trades if t['pnl'] < 0]

win_rate = (len(winning_trades) / len(trades) * 100) if trades else 0

avg_win = sum(t['pnl'] for t in winning_trades) / len(winning_trades) if winning_trades else 0
avg_loss = sum(t['pnl'] for t in losing_trades) / len(losing_trades) if losing_trades else 0

avg_win_pct = sum(t['pnl_pct'] for t in winning_trades) / len(winning_trades) * 100 if winning_trades else 0
avg_loss_pct = sum(t['pnl_pct'] for t in losing_trades) / len(losing_trades) * 100 if losing_trades else 0

# Best and worst trades
if trades:
    best_trade = max(trades, key=lambda t: t['pnl_pct'])
    worst_trade = min(trades, key=lambda t: t['pnl_pct'])

print("="*70)
print("BACKTEST RESULTS")
print("="*70)
print(f"\n💰 Final Equity:       ${final_equity:,.2f}")
print(f"📈 Total Return:       {total_return:+.2f}%")
print(f"💵 Total P&L:          ${final_equity - INITIAL_CAPITAL:+,.2f}")

print(f"\n📊 Trading Stats:")
print(f"   Total IPOs Traded:  {len(trades)}")
print(f"   Winning Trades:     {len(winning_trades)} ({win_rate:.1f}%)")
print(f"   Losing Trades:      {len(losing_trades)}")

if winning_trades:
    print(f"   Avg Win:            ${avg_win:,.2f} ({avg_win_pct:+.1f}%)")
if losing_trades:
    print(f"   Avg Loss:           ${avg_loss:,.2f} ({avg_loss_pct:.1f}%)")

if trades:
    avg_hold = sum(t['hold_days'] for t in trades) / len(trades)
    print(f"   Avg Hold Period:    {avg_hold:.1f} days")

    print(f"\n🏆 Best Trade:")
    print(f"   {best_trade['symbol']} ({best_trade['company']})")
    print(f"   {best_trade['pnl_pct']*100:+.1f}% (${best_trade['pnl']:+,.2f})")

    print(f"\n📉 Worst Trade:")
    print(f"   {worst_trade['symbol']} ({worst_trade['company']})")
    print(f"   {worst_trade['pnl_pct']*100:+.1f}% (${worst_trade['pnl']:+,.2f})")

print("\n" + "="*70)
print("VERDICT")
print("="*70)

if total_return > 20 and win_rate > 50:
    print("✅ EXCELLENT - IPO strategy is highly profitable!")
    print("   Consider dedicating 10-15% of portfolio to IPO plays")
elif total_return > 10:
    print("✓ GOOD - IPO strategy shows promise")
    print("   Use with caution, allocate 5-10% of portfolio")
elif total_return > 0:
    print("⚠ MEDIOCRE - IPO strategy barely profitable")
    print("   Very risky, only allocate 2-5% of portfolio")
else:
    print("❌ POOR - IPO strategy loses money")
    print("   Do NOT trade IPOs with this approach")

print(f"\n💡 Key Insights:")
if win_rate < 50:
    print("   • Low win rate suggests need for better entry timing")
if avg_win_pct > abs(avg_loss_pct) * 2:
    print("   • Good risk/reward ratio - winners are much bigger than losers")
if avg_hold < 2:
    print("   • Very short holds - mostly first-day pops")
elif avg_hold > 4:
    print("   • Longer holds - IPOs trending after initial pop")

print("\n" + "="*70 + "\n")

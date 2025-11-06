#!/usr/bin/env python3
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from optifire.backtest.engine import BacktestEngine, BacktestConfig
from optifire.backtest.visualizer import BacktestVisualizer
from optifire.backtest.strategies import MomentumStrategy

# Load environment
import os
env_file = Path(__file__).parent / "secrets.env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()

async def main():
    print("\n" + "="*70)
    print("🔧 OPTIMIZED MOMENTUM STRATEGY")
    print("="*70)
    
    # Test 1: Wider stop loss (5% instead of 3%)
    print("\n📊 Test 1: Wider Stop Loss (5% instead of 3%)")
    config1 = BacktestConfig(
        start_date="2023-01-01",
        end_date="2024-11-05",
        initial_capital=10000,
        symbols=["SPY", "QQQ", "AAPL", "NVDA", "TSLA", "MSFT"],
        stop_loss_pct=0.05,  # 5% instead of 3%
        take_profit_pct=0.07,
        max_position_size=0.10,
        max_total_exposure=0.30,
    )
    
    engine1 = BacktestEngine(config1)
    strategy1 = MomentumStrategy()
    metrics1 = await engine1.run(strategy1.generate_signals)
    
    print(f"\n  Return:      {metrics1['total_return_pct']:.2f}%")
    print(f"  Sharpe:      {metrics1['sharpe_ratio']:.2f}")
    print(f"  Max DD:      {metrics1['max_drawdown_pct']:.2f}%")
    print(f"  Trades:      {metrics1['total_trades']}")
    print(f"  Win Rate:    {metrics1['win_rate_pct']:.1f}%")
    
    # Test 2: Higher take profit (10% instead of 7%)
    print("\n📊 Test 2: Higher Take Profit (10% instead of 7%)")
    config2 = BacktestConfig(
        start_date="2023-01-01",
        end_date="2024-11-05",
        initial_capital=10000,
        symbols=["SPY", "QQQ", "AAPL", "NVDA", "TSLA", "MSFT"],
        stop_loss_pct=0.03,
        take_profit_pct=0.10,  # 10% instead of 7%
        max_position_size=0.10,
        max_total_exposure=0.30,
    )
    
    engine2 = BacktestEngine(config2)
    strategy2 = MomentumStrategy()
    metrics2 = await engine2.run(strategy2.generate_signals)
    
    print(f"\n  Return:      {metrics2['total_return_pct']:.2f}%")
    print(f"  Sharpe:      {metrics2['sharpe_ratio']:.2f}")
    print(f"  Max DD:      {metrics2['max_drawdown_pct']:.2f}%")
    print(f"  Trades:      {metrics2['total_trades']}")
    print(f"  Win Rate:    {metrics2['win_rate_pct']:.1f}%")
    
    # Test 3: Focus on best symbols (NVDA, TSLA only)
    print("\n📊 Test 3: Focus on Best Symbols (NVDA, TSLA)")
    config3 = BacktestConfig(
        start_date="2023-01-01",
        end_date="2024-11-05",
        initial_capital=10000,
        symbols=["NVDA", "TSLA"],  # Best performers
        stop_loss_pct=0.03,
        take_profit_pct=0.07,
        max_position_size=0.10,
        max_total_exposure=0.30,
    )
    
    engine3 = BacktestEngine(config3)
    strategy3 = MomentumStrategy()
    metrics3 = await engine3.run(strategy3.generate_signals)
    
    print(f"\n  Return:      {metrics3['total_return_pct']:.2f}%")
    print(f"  Sharpe:      {metrics3['sharpe_ratio']:.2f}")
    print(f"  Max DD:      {metrics3['max_drawdown_pct']:.2f}%")
    print(f"  Trades:      {metrics3['total_trades']}")
    print(f"  Win Rate:    {metrics3['win_rate_pct']:.1f}%")
    
    # Test 4: Higher exposure (50% instead of 30%)
    print("\n📊 Test 4: Higher Exposure (50% instead of 30%)")
    config4 = BacktestConfig(
        start_date="2023-01-01",
        end_date="2024-11-05",
        initial_capital=10000,
        symbols=["SPY", "QQQ", "AAPL", "NVDA", "TSLA", "MSFT"],
        stop_loss_pct=0.03,
        take_profit_pct=0.07,
        max_position_size=0.10,
        max_total_exposure=0.50,  # 50% instead of 30%
    )
    
    engine4 = BacktestEngine(config4)
    strategy4 = MomentumStrategy()
    metrics4 = await engine4.run(strategy4.generate_signals)
    
    print(f"\n  Return:      {metrics4['total_return_pct']:.2f}%")
    print(f"  Sharpe:      {metrics4['sharpe_ratio']:.2f}")
    print(f"  Max DD:      {metrics4['max_drawdown_pct']:.2f}%")
    print(f"  Trades:      {metrics4['total_trades']}")
    print(f"  Win Rate:    {metrics4['win_rate_pct']:.1f}%")
    
    # Test 5: Combined best settings
    print("\n📊 Test 5: OPTIMIZED - Best Settings Combined")
    config5 = BacktestConfig(
        start_date="2023-01-01",
        end_date="2024-11-05",
        initial_capital=10000,
        symbols=["NVDA", "TSLA", "AAPL"],  # Best + good performer
        stop_loss_pct=0.05,  # Wider
        take_profit_pct=0.10,  # Higher
        max_position_size=0.15,  # Larger positions
        max_total_exposure=0.45,  # More exposure
    )
    
    engine5 = BacktestEngine(config5)
    strategy5 = MomentumStrategy()
    metrics5 = await engine5.run(strategy5.generate_signals)
    
    print(f"\n  Return:      {metrics5['total_return_pct']:.2f}%")
    print(f"  Sharpe:      {metrics5['sharpe_ratio']:.2f}")
    print(f"  Max DD:      {metrics5['max_drawdown_pct']:.2f}%")
    print(f"  Trades:      {metrics5['total_trades']}")
    print(f"  Win Rate:    {metrics5['win_rate_pct']:.1f}%")
    
    # Save best one
    BacktestVisualizer.create_all_plots(metrics5, "backtest_optimized")
    
    # Summary
    print("\n" + "="*70)
    print("📊 COMPARISON SUMMARY")
    print("="*70)
    print(f"\n  Original:        {8.06:.2f}% return, Sharpe {1.68:.2f}")
    print(f"  1. Wider SL:     {metrics1['total_return_pct']:>6.2f}% return, Sharpe {metrics1['sharpe_ratio']:>4.2f}")
    print(f"  2. Higher TP:    {metrics2['total_return_pct']:>6.2f}% return, Sharpe {metrics2['sharpe_ratio']:>4.2f}")
    print(f"  3. Best Symbols: {metrics3['total_return_pct']:>6.2f}% return, Sharpe {metrics3['sharpe_ratio']:>4.2f}")
    print(f"  4. More Exposure:{metrics4['total_return_pct']:>6.2f}% return, Sharpe {metrics4['sharpe_ratio']:>4.2f}")
    print(f"  5. OPTIMIZED:    {metrics5['total_return_pct']:>6.2f}% return, Sharpe {metrics5['sharpe_ratio']:>4.2f}")
    
    # Verdict
    best_return = max(
        metrics1['total_return_pct'],
        metrics2['total_return_pct'],
        metrics3['total_return_pct'],
        metrics4['total_return_pct'],
        metrics5['total_return_pct'],
    )
    
    print("\n" + "="*70)
    if best_return > 8.06:
        improvement = best_return - 8.06
        print(f"✅ OPTIMIZATION SUCCESS! +{improvement:.2f}% improvement")
    else:
        print("⚠️  Original settings were already optimal")
    print("="*70 + "\n")

if __name__ == "__main__":
    asyncio.run(main())

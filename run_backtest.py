#!/usr/bin/env python3
"""
OptiFIRE Backtesting Script

Run backtests on your trading strategies to evaluate performance before going live.

Usage:
    python run_backtest.py [--strategy STRATEGY] [--start START] [--end END] [--capital CAPITAL]

Examples:
    # Run simple strategy backtest (last 6 months, $10k)
    python run_backtest.py

    # Run trend following strategy (last year, $50k)
    python run_backtest.py --strategy trend --start 2024-01-01 --capital 50000

    # Run momentum strategy
    python run_backtest.py --strategy momentum --start 2023-01-01 --end 2024-12-31
"""
import asyncio
import argparse
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add parent dir to path
sys.path.insert(0, str(Path(__file__).parent))

from optifire.backtest.engine import BacktestEngine, BacktestConfig
from optifire.backtest.visualizer import BacktestVisualizer
from optifire.backtest.strategies import (
    SimpleStrategy,
    TrendFollowingStrategy,
    MomentumStrategy,
    MeanReversionStrategy,
    BuyAndHoldStrategy,
)


# Strategy mapping
STRATEGIES = {
    "simple": SimpleStrategy,
    "trend": TrendFollowingStrategy,
    "momentum": MomentumStrategy,
    "mean_reversion": MeanReversionStrategy,
    "buy_hold": BuyAndHoldStrategy,
}


def load_env():
    """Load environment variables from secrets.env"""
    env_file = Path(__file__).parent / "secrets.env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()


async def main():
    parser = argparse.ArgumentParser(description="Run OptiFIRE backtests")

    parser.add_argument(
        "--strategy",
        choices=list(STRATEGIES.keys()),
        default="simple",
        help="Trading strategy to backtest (default: simple)",
    )

    parser.add_argument(
        "--start",
        type=str,
        help="Start date (YYYY-MM-DD). Default: 6 months ago",
    )

    parser.add_argument(
        "--end",
        type=str,
        help="End date (YYYY-MM-DD). Default: today",
    )

    parser.add_argument(
        "--capital",
        type=float,
        default=10000.0,
        help="Initial capital (default: 10000)",
    )

    parser.add_argument(
        "--symbols",
        type=str,
        help="Comma-separated list of symbols (default: SPY,QQQ,AAPL,NVDA,TSLA,MSFT,GOOGL,META,AMZN)",
    )

    parser.add_argument(
        "--output",
        type=str,
        default="backtest_results",
        help="Output directory for results (default: backtest_results)",
    )

    args = parser.parse_args()

    # Load environment
    load_env()

    # Validate API keys
    if not os.getenv("ALPACA_API_KEY"):
        print("❌ Error: ALPACA_API_KEY not found in environment")
        print("   Make sure secrets.env contains your Alpaca credentials")
        sys.exit(1)

    # Default date range: 6 months
    end_date = args.end or datetime.now().strftime("%Y-%m-%d")
    if args.start:
        start_date = args.start
    else:
        start_dt = datetime.now() - timedelta(days=180)
        start_date = start_dt.strftime("%Y-%m-%d")

    # Parse symbols
    if args.symbols:
        symbols = [s.strip().upper() for s in args.symbols.split(",")]
    else:
        symbols = ["SPY", "QQQ", "AAPL", "NVDA", "TSLA", "MSFT", "GOOGL", "META", "AMZN"]

    # Create config
    config = BacktestConfig(
        start_date=start_date,
        end_date=end_date,
        initial_capital=args.capital,
        symbols=symbols,
    )

    print("\n" + "="*60)
    print("OptiFIRE BACKTESTING")
    print("="*60)
    print(f"\nStrategy:        {args.strategy}")
    print(f"Date Range:      {start_date} to {end_date}")
    print(f"Initial Capital: ${args.capital:,.2f}")
    print(f"Symbols:         {', '.join(symbols)}")
    print(f"\nRisk Parameters:")
    print(f"  Max Position:    {config.max_position_size*100:.0f}%")
    print(f"  Max Exposure:    {config.max_total_exposure*100:.0f}%")
    print(f"  Stop Loss:       {config.stop_loss_pct*100:.0f}%")
    print(f"  Take Profit:     {config.take_profit_pct*100:.0f}%")
    print("\n" + "="*60 + "\n")

    # Create backtest engine
    engine = BacktestEngine(config)

    # Create strategy
    strategy_class = STRATEGIES[args.strategy]
    strategy = strategy_class()

    # Run backtest
    print("🚀 Starting backtest...\n")

    try:
        metrics = await engine.run(strategy.generate_signals)

        if "error" in metrics:
            print(f"❌ Backtest failed: {metrics['error']}")
            sys.exit(1)

        # Create output directory
        output_dir = Path(args.output)
        output_dir.mkdir(exist_ok=True)

        # Generate visualizations
        print("\n📊 Generating visualizations...")
        BacktestVisualizer.create_all_plots(metrics, str(output_dir))

        # Save metrics to JSON
        import json
        metrics_file = output_dir / "metrics.json"
        with open(metrics_file, "w") as f:
            # Convert equity curve to serializable format
            serializable_metrics = {
                k: v for k, v in metrics.items()
                if k not in ["equity_curve", "trades"]
            }
            json.dump(serializable_metrics, f, indent=2)
        print(f"✓ Metrics saved to {metrics_file}")

        # Save trade log
        trades_file = output_dir / "trades.csv"
        import pandas as pd
        df_trades = pd.DataFrame(metrics["trades"])
        df_trades.to_csv(trades_file, index=False)
        print(f"✓ Trade log saved to {trades_file}")

        print(f"\n✅ Backtest complete! Results saved to {output_dir}/")

        # Final verdict
        print("\n" + "="*60)
        print("VERDICT")
        print("="*60)

        if metrics["total_return_pct"] > 20 and metrics["sharpe_ratio"] > 1.0 and metrics["max_drawdown_pct"] > -15:
            print("✅ EXCELLENT - Strategy shows strong performance")
        elif metrics["total_return_pct"] > 10 and metrics["sharpe_ratio"] > 0.5:
            print("✓ GOOD - Strategy has potential, consider optimization")
        elif metrics["total_return_pct"] > 0:
            print("⚠ MEDIOCRE - Strategy is slightly profitable, needs improvement")
        else:
            print("❌ POOR - Strategy loses money, do NOT trade live")

        print("\n💡 Next steps:")
        if metrics["total_return_pct"] > 10:
            print("  1. Try different parameters (position size, stop loss, etc.)")
            print("  2. Run paper trading for 2-4 weeks to validate")
            print("  3. Start with small capital if going live")
        else:
            print("  1. Try a different strategy")
            print("  2. Adjust risk parameters")
            print("  3. Consider different symbols or timeframes")

        print("\n" + "="*60 + "\n")

    except KeyboardInterrupt:
        print("\n\n⚠ Backtest interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Backtest failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

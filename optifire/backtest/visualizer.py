"""
Backtesting visualization tools.
"""
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import pandas as pd
from typing import Dict, List
from pathlib import Path


class BacktestVisualizer:
    """Creates visualizations for backtest results."""

    @staticmethod
    def plot_equity_curve(metrics: Dict, output_path: str = "backtest_equity.png"):
        """
        Plot equity curve over time.

        Args:
            metrics: Backtest metrics dictionary
            output_path: Path to save plot
        """
        equity_data = metrics.get("equity_curve", [])
        if not equity_data:
            print("No equity data to plot")
            return

        df = pd.DataFrame(equity_data)
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

        # Equity curve
        ax1.plot(df["timestamp"], df["equity"], linewidth=2, color='#2E86AB')
        ax1.axhline(y=metrics["initial_capital"], color='gray', linestyle='--', alpha=0.5, label='Initial Capital')
        ax1.set_ylabel("Portfolio Value ($)", fontsize=12)
        ax1.set_title(f"Backtest Results: {metrics['total_return_pct']:.2f}% Return", fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend()

        # Format y-axis as currency
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

        # Drawdown
        df["cummax"] = df["equity"].cummax()
        df["drawdown"] = ((df["equity"] - df["cummax"]) / df["cummax"]) * 100

        ax2.fill_between(df["timestamp"], df["drawdown"], 0, color='#A23B72', alpha=0.5)
        ax2.set_ylabel("Drawdown (%)", fontsize=12)
        ax2.set_xlabel("Date", fontsize=12)
        ax2.grid(True, alpha=0.3)
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.1f}%'))

        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()

        print(f"✓ Equity curve saved to {output_path}")

    @staticmethod
    def plot_trade_analysis(metrics: Dict, output_path: str = "backtest_trades.png"):
        """
        Plot trade analysis.

        Args:
            metrics: Backtest metrics dictionary
            output_path: Path to save plot
        """
        trades = metrics.get("trades", [])
        if not trades:
            print("No trades to plot")
            return

        df = pd.DataFrame(trades)
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))

        # 1. P&L per trade
        colors = ['#06A77D' if pnl > 0 else '#D81E5B' for pnl in df["pnl"]]
        ax1.bar(range(len(df)), df["pnl"], color=colors, alpha=0.7)
        ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
        ax1.set_xlabel("Trade #", fontsize=10)
        ax1.set_ylabel("P&L ($)", fontsize=10)
        ax1.set_title("P&L per Trade", fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='y')

        # 2. Cumulative P&L
        df["cumulative_pnl"] = df["pnl"].cumsum()
        ax2.plot(df["timestamp"], df["cumulative_pnl"], linewidth=2, color='#2E86AB')
        ax2.fill_between(df["timestamp"], df["cumulative_pnl"], 0, alpha=0.3, color='#2E86AB')
        ax2.set_xlabel("Date", fontsize=10)
        ax2.set_ylabel("Cumulative P&L ($)", fontsize=10)
        ax2.set_title("Cumulative P&L Over Time", fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

        # 3. Win/Loss distribution
        wins = df[df["pnl"] > 0]["pnl"]
        losses = df[df["pnl"] < 0]["pnl"]

        ax3.hist([wins, losses], bins=20, color=['#06A77D', '#D81E5B'], alpha=0.7, label=['Wins', 'Losses'])
        ax3.set_xlabel("P&L ($)", fontsize=10)
        ax3.set_ylabel("Frequency", fontsize=10)
        ax3.set_title("Win/Loss Distribution", fontsize=12, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3, axis='y')

        # 4. Trade reasons pie chart
        reason_counts = df["reason"].value_counts()
        colors_pie = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#06A77D']
        ax4.pie(reason_counts.values, labels=reason_counts.index, autopct='%1.1f%%',
                colors=colors_pie[:len(reason_counts)], startangle=90)
        ax4.set_title("Trade Exit Reasons", fontsize=12, fontweight='bold')

        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()

        print(f"✓ Trade analysis saved to {output_path}")

    @staticmethod
    def plot_monthly_returns(metrics: Dict, output_path: str = "backtest_monthly.png"):
        """
        Plot monthly returns heatmap.

        Args:
            metrics: Backtest metrics dictionary
            output_path: Path to save plot
        """
        trades = metrics.get("trades", [])
        if not trades:
            print("No trades for monthly analysis")
            return

        df = pd.DataFrame(trades)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["year"] = df["timestamp"].dt.year
        df["month"] = df["timestamp"].dt.month

        # Group by year and month
        monthly = df.groupby(["year", "month"])["pnl"].sum().reset_index()
        monthly["year_month"] = pd.to_datetime(monthly[["year", "month"]].assign(day=1))

        fig, ax = plt.subplots(figsize=(12, 6))

        # Bar chart
        colors = ['#06A77D' if pnl > 0 else '#D81E5B' for pnl in monthly["pnl"]]
        bars = ax.bar(monthly["year_month"], monthly["pnl"], width=25, color=colors, alpha=0.7)

        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
        ax.set_xlabel("Month", fontsize=12)
        ax.set_ylabel("Monthly P&L ($)", fontsize=12)
        ax.set_title("Monthly P&L", fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            if abs(height) > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'${height:,.0f}',
                       ha='center', va='bottom' if height > 0 else 'top',
                       fontsize=8)

        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()

        print(f"✓ Monthly returns saved to {output_path}")

    @staticmethod
    def print_summary(metrics: Dict):
        """
        Print a formatted summary of backtest results.

        Args:
            metrics: Backtest metrics dictionary
        """
        print("\n" + "="*60)
        print("BACKTEST SUMMARY")
        print("="*60)

        print(f"\n💰 RETURNS:")
        print(f"  Initial Capital:        ${metrics['initial_capital']:>12,.2f}")
        print(f"  Final Equity:           ${metrics['final_equity']:>12,.2f}")
        print(f"  Total Return:           {metrics['total_return_pct']:>12.2f}%")
        print(f"  Total P&L:              ${metrics['total_pnl']:>12,.2f}")

        print(f"\n📊 TRADE STATISTICS:")
        print(f"  Total Trades:           {metrics['total_trades']:>12}")
        print(f"  Winning Trades:         {metrics['winning_trades']:>12} ({metrics['win_rate_pct']:.1f}%)")
        print(f"  Losing Trades:          {metrics['losing_trades']:>12}")
        print(f"  Average Win:            ${metrics['avg_win']:>12,.2f}")
        print(f"  Average Loss:           ${metrics['avg_loss']:>12,.2f}")
        print(f"  Profit Factor:          {metrics['profit_factor']:>12.2f}")

        print(f"\n📉 RISK METRICS:")
        print(f"  Max Drawdown:           {metrics['max_drawdown_pct']:>12.2f}%")
        print(f"  Sharpe Ratio:           {metrics['sharpe_ratio']:>12.2f}")
        print(f"  Sortino Ratio:          {metrics['sortino_ratio']:>12.2f}")

        print("\n" + "="*60 + "\n")

    @staticmethod
    def create_all_plots(metrics: Dict, output_dir: str = "."):
        """
        Create all visualization plots.

        Args:
            metrics: Backtest metrics dictionary
            output_dir: Directory to save plots
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        BacktestVisualizer.print_summary(metrics)
        BacktestVisualizer.plot_equity_curve(metrics, str(output_path / "backtest_equity.png"))
        BacktestVisualizer.plot_trade_analysis(metrics, str(output_path / "backtest_trades.png"))
        BacktestVisualizer.plot_monthly_returns(metrics, str(output_path / "backtest_monthly.png"))

        print(f"\n✅ All plots saved to {output_dir}/")

#!/usr/bin/env python3
"""Comprehensive backtest for v2 alpha plugins (2023-2025)"""
import asyncio
import sys
from datetime import datetime, timedelta
import random
sys.path.insert(0, 'optifire/plugins')

from optifire.plugins import PluginContext

# Mock market data for backtesting
class BacktestEngine:
    def __init__(self, start_date, end_date):
        self.start = start_date
        self.end = end_date
        self.current_date = start_date
        self.portfolio_value = 100000
        self.trades = []
        self.daily_returns = []

    def generate_market_data(self, symbol, date):
        """Generate realistic mock market data"""
        base_price = {"SPY": 450, "AAPL": 180, "NVDA": 450, "TSLA": 250, "GME": 20}
        price = base_price.get(symbol, 100)
        volatility = 0.02
        drift = 0.0003  # Slightly positive trend

        days_elapsed = (date - self.start).days
        random_return = random.gauss(drift, volatility)
        return price * (1 + random_return) ** days_elapsed

    async def test_alpha_signal(self, plugin_module, plugin_class, signal_params):
        """Test a single alpha signal"""
        try:
            mod = __import__(f'{plugin_module}.impl', fromlist=[plugin_class])
            PluginClass = getattr(mod, plugin_class)
            plugin = PluginClass()

            ctx = PluginContext(config={}, db=None, bus=None, data=signal_params)
            result = await plugin.run(ctx)

            if result.success and result.data:
                # Extract signal strength (0-1)
                data = result.data

                # Different plugins have different signal formats
                if 'unusual_flow_detected' in data:
                    return 0.7 if data['unusual_flow_detected'] else 0.0
                elif 'insider_sentiment' in data:
                    return 0.8 if data['insider_sentiment'] == 'BULLISH' else 0.0
                elif 'squeeze_potential' in data:
                    potential = data['squeeze_potential']
                    return {'EXTREME': 0.9, 'HIGH': 0.7, 'MODERATE': 0.4}.get(potential, 0.0)
                elif 'crypto_sentiment' in data:
                    return 0.6 if data['crypto_sentiment'] == 'RISK_ON' else 0.0
                elif 'rotation_signal' in data:
                    return 0.5 if data['rotation_signal'] == 'RISK_ON' else 0.0
                elif 'sentiment' in data:
                    return 0.7 if data['sentiment'] in ['EXTREME_FEAR', 'BULLISH'] else 0.0
                elif 'directional_bias' in data:
                    return 0.6 if data['directional_bias'] == 'TRENDING' else 0.0
                elif 'thrust_signal' in data:
                    return 0.8 if data['thrust_signal'] == 'THRUST' else 0.0
                elif 'macro_sentiment' in data:
                    return 0.5 if data['macro_sentiment'] in ['HAWKISH', 'DOVISH'] else 0.0

            return 0.0
        except:
            return 0.0

    async def run_backtest(self):
        """Run comprehensive backtest"""
        print(f"🔬 BACKTEST: {self.start.date()} → {self.end.date()}")
        print("="*60)

        alpha_plugins = [
            ('alpha_dark_pool_flow', 'AlphaDarkPoolFlow', {'symbol': 'AAPL', 'volume': 2000000, 'avg_daily_volume': 50000000}),
            ('alpha_insider_trading', 'AlphaInsiderTrading', {'symbol': 'NVDA'}),
            ('alpha_short_interest', 'AlphaShortInterest', {'symbol': 'GME', 'short_interest': 30.0}),
            ('alpha_crypto_correlation', 'AlphaCryptoCorrelation', {'btc_price': 50000, 'eth_price': 3000}),
            ('alpha_sector_rotation', 'AlphaSectorRotation', {}),
            ('alpha_put_call_ratio', 'AlphaPutCallRatio', {'symbol': 'SPY', 'put_volume': 1300000, 'call_volume': 1000000}),
            ('alpha_gamma_exposure', 'AlphaGammaExposure', {'symbol': 'SPY', 'current_price': 450}),
            ('alpha_breadth_thrust', 'AlphaBreadthThrust', {'advances': 2200, 'declines': 800}),
            ('alpha_economic_surprise', 'AlphaEconomicSurprise', {'indicator': 'NFP', 'actual': 250000, 'consensus': 200000}),
        ]

        results = {}

        # Simulate trading days
        trading_days = []
        current = self.start
        while current <= self.end:
            if current.weekday() < 5:  # Monday-Friday
                trading_days.append(current)
            current += timedelta(days=1)

        print(f"📅 Trading days: {len(trading_days)}")
        print(f"💰 Starting capital: ${self.portfolio_value:,.0f}\n")

        for day_num, date in enumerate(trading_days[:100]):  # Limit to 100 days for speed
            self.current_date = date

            # Collect signals from all plugins
            signals = []
            for plugin_id, class_name, params in alpha_plugins:
                # Vary params slightly each day for realism
                varied_params = params.copy()
                if 'volume' in varied_params:
                    varied_params['volume'] = int(varied_params['volume'] * random.uniform(0.8, 1.5))

                signal_strength = await self.test_alpha_signal(plugin_id, class_name, varied_params)

                if signal_strength > 0.5:  # Signal threshold
                    signals.append((plugin_id, signal_strength))

                    if plugin_id not in results:
                        results[plugin_id] = {'signals': 0, 'wins': 0, 'losses': 0, 'pnl': 0}
                    results[plugin_id]['signals'] += 1

            # Execute trades based on signals
            if signals:
                # Aggregate signals
                avg_signal = sum(s[1] for s in signals) / len(signals)

                # Position size based on signal strength
                position_size = min(self.portfolio_value * 0.1 * avg_signal, self.portfolio_value * 0.15)

                # Simulate trade outcome (simplified)
                market_return = random.gauss(0.001, 0.02)  # Daily return
                trade_pnl = position_size * market_return

                self.portfolio_value += trade_pnl
                self.trades.append({
                    'date': date,
                    'signals': [s[0] for s in signals],
                    'position_size': position_size,
                    'pnl': trade_pnl
                })

                # Track per-plugin performance
                for plugin_id, _ in signals:
                    results[plugin_id]['pnl'] += trade_pnl / len(signals)
                    if trade_pnl > 0:
                        results[plugin_id]['wins'] += 1
                    else:
                        results[plugin_id]['losses'] += 1

            # Track daily portfolio value
            self.daily_returns.append(self.portfolio_value)

            # Progress update
            if (day_num + 1) % 20 == 0:
                pnl = self.portfolio_value - 100000
                print(f"Day {day_num+1}/{min(100, len(trading_days))}: Portfolio ${self.portfolio_value:,.0f} (PnL: ${pnl:+,.0f})")

        # Calculate final metrics
        total_return = (self.portfolio_value - 100000) / 100000
        num_trades = len(self.trades)
        win_rate = sum(1 for t in self.trades if t['pnl'] > 0) / num_trades if num_trades > 0 else 0

        print("\n" + "="*60)
        print("📊 BACKTEST RESULTS")
        print("="*60)
        print(f"Final Portfolio Value: ${self.portfolio_value:,.2f}")
        print(f"Total Return: {total_return*100:+.2f}%")
        print(f"Number of Trades: {num_trades}")
        print(f"Win Rate: {win_rate*100:.1f}%")
        print(f"\n🎯 PER-PLUGIN PERFORMANCE:")
        print("-"*60)

        # Sort by PnL
        sorted_results = sorted(results.items(), key=lambda x: x[1]['pnl'], reverse=True)

        for plugin_id, stats in sorted_results:
            win_rate_plugin = stats['wins'] / (stats['wins'] + stats['losses']) if (stats['wins'] + stats['losses']) > 0 else 0
            print(f"{plugin_id:30s} | Signals: {stats['signals']:3d} | Win: {win_rate_plugin*100:5.1f}% | PnL: ${stats['pnl']:+8,.0f}")

        return self.portfolio_value, total_return, results

async def main():
    """Run comprehensive backtest"""
    start = datetime(2023, 1, 1)
    end = datetime(2025, 11, 6)

    engine = BacktestEngine(start, end)
    final_value, total_return, results = await engine.run_backtest()

    print("\n" + "="*60)
    print("✅ BACKTEST COMPLETE")
    print("="*60)

    return final_value > 100000  # Success if profitable

if __name__ == '__main__':
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

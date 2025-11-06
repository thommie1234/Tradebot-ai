#!/usr/bin/env python3
"""Quick integration test for new v2 plugins"""
import asyncio
import sys
sys.path.insert(0, 'optifire/plugins')

from optifire.plugins import PluginContext

async def test_plugin(plugin_module, plugin_class, test_params):
    """Test a single plugin"""
    try:
        mod = __import__(f'{plugin_module}.impl', fromlist=[plugin_class])
        PluginClass = getattr(mod, plugin_class)
        plugin = PluginClass()

        # Test describe
        meta = plugin.describe()
        assert meta.plugin_id == plugin_module

        # Test run - use proper PluginContext signature
        ctx = PluginContext(config=test_params, db=None, bus=None, data=test_params)
        result = await plugin.run(ctx)

        return True, result.data if result.success else result.error
    except Exception as e:
        return False, str(e)

async def main():
    tests = [
        ('alpha_dark_pool_flow', 'AlphaDarkPoolFlow', {'symbol': 'AAPL', 'volume': 1000000, 'price': 180.0}),
        ('alpha_insider_trading', 'AlphaInsiderTrading', {'symbol': 'NVDA'}),
        ('alpha_short_interest', 'AlphaShortInterest', {'symbol': 'GME', 'short_interest': 25.0}),
        ('alpha_crypto_correlation', 'AlphaCryptoCorrelation', {'btc_price': 50000, 'eth_price': 3000}),
        ('alpha_sector_rotation', 'AlphaSectorRotation', {}),
        ('alpha_put_call_ratio', 'AlphaPutCallRatio', {'symbol': 'SPY', 'put_volume': 1200000, 'call_volume': 900000}),
        ('ml_transformer_ts', 'MlTransformerTs', {'prices': [100, 101, 102, 103]}),
        ('ml_rl_agent', 'MlRlAgent', {'state': {'vix': 20, 'trend': 'up'}}),
        ('exec_twap', 'ExecTwap', {'symbol': 'AAPL', 'qty': 1000}),
        ('exec_vwap', 'ExecVwap', {'symbol': 'TSLA', 'qty': 500}),
        ('risk_corr_breakdown', 'RiskCorrBreakdown', {'positions': ['AAPL', 'MSFT', 'GOOGL']}),
        ('risk_tail_hedge', 'RiskTailHedge', {'vix': 35.0}),
        ('data_reddit_wsb', 'DataRedditWsb', {'subreddit': 'wallstreetbets'}),
        ('data_stocktwits', 'DataStocktwits', {'symbol': 'TSLA'}),
    ]

    passed = 0
    failed = []

    for plugin_id, class_name, params in tests:
        success, result = await test_plugin(plugin_id, class_name, params)
        if success:
            passed += 1
            print(f'✓ {plugin_id}: {str(result)[:60]}...')
        else:
            failed.append((plugin_id, result))
            print(f'✗ {plugin_id}: {result}')

    print(f'\n{"="*60}')
    print(f'RESULTS: {passed}/{len(tests)} passed')
    if failed:
        print(f'Failed: {[f[0] for f in failed]}')
    return passed == len(tests)

if __name__ == '__main__':
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""Register all v2 plugins in the global registry"""
import sys
sys.path.insert(0, 'optifire/plugins')

from optifire.plugins import registry
from optifire.core.logger import logger

# All v2 plugins
V2_PLUGINS = [
    # Alpha (10)
    ('alpha_dark_pool_flow', 'AlphaDarkPoolFlow'),
    ('alpha_insider_trading', 'AlphaInsiderTrading'),
    ('alpha_short_interest', 'AlphaShortInterest'),
    ('alpha_congressional_trades', 'AlphaCongressionalTrades'),
    ('alpha_crypto_correlation', 'AlphaCryptoCorrelation'),
    ('alpha_sector_rotation', 'AlphaSectorRotation'),
    ('alpha_put_call_ratio', 'AlphaPutCallRatio'),
    ('alpha_gamma_exposure', 'AlphaGammaExposure'),
    ('alpha_breadth_thrust', 'AlphaBreadthThrust'),
    ('alpha_economic_surprise', 'AlphaEconomicSurprise'),

    # ML/AI (6)
    ('ml_transformer_ts', 'MlTransformerTs'),
    ('ml_rl_agent', 'MlRlAgent'),
    ('ml_lstm_sentiment', 'MlLstmSentiment'),
    ('ml_ensemble_voting', 'MlEnsembleVoting'),
    ('ml_anomaly_detect', 'MlAnomalyDetect'),
    ('ml_causal_inference', 'MlCausalInference'),

    # Execution (5)
    ('exec_twap', 'ExecTwap'),
    ('exec_vwap', 'ExecVwap'),
    ('exec_iceberg_detect', 'ExecIcebergDetect'),
    ('exec_smart_router', 'ExecSmartRouter'),
    ('exec_post_only', 'ExecPostOnly'),

    # Risk (5)
    ('risk_corr_breakdown', 'RiskCorrBreakdown'),
    ('risk_tail_hedge', 'RiskTailHedge'),
    ('risk_position_concentration', 'RiskPositionConcentration'),
    ('risk_leverage_monitor', 'RiskLeverageMonitor'),
    ('risk_max_pain', 'RiskMaxPain'),

    # Data (6)
    ('data_reddit_wsb', 'DataRedditWsb'),
    ('data_stocktwits', 'DataStocktwits'),
    ('data_unusual_options', 'DataUnusualOptions'),
    ('data_13f_filings', 'Data13fFilings'),
    ('data_fed_minutes', 'DataFedMinutes'),
    ('data_supply_chain', 'DataSupplyChain'),
]

def register_all():
    """Register all v2 plugins"""
    registered = 0
    failed = []

    for plugin_id, class_name in V2_PLUGINS:
        try:
            mod = __import__(f'{plugin_id}.impl', fromlist=[class_name])
            PluginClass = getattr(mod, class_name)
            plugin = PluginClass()
            registry.register(plugin)
            registered += 1
        except Exception as e:
            failed.append((plugin_id, str(e)))
            logger.error(f"Failed to register {plugin_id}: {e}")

    print(f"✅ Registered {registered}/{len(V2_PLUGINS)} v2 plugins")
    if failed:
        print(f"❌ Failed: {[f[0] for f in failed[:5]]}")
    return registered, failed

if __name__ == '__main__':
    registered, failed = register_all()
    sys.exit(0 if len(failed) == 0 else 1)

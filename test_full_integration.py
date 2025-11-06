#!/usr/bin/env python3
"""Test complete system integration with all v2 plugins"""
import asyncio
import sys
from pathlib import Path

async def test_system_integration():
    """Test that all components work together"""
    print("🔧 SYSTEM INTEGRATION TEST")
    print("="*60)

    # 1. Test imports
    print("\n1️⃣ Testing core imports...")
    try:
        from optifire.core.config import Config
        from optifire.core.db import Database
        from optifire.core.bus import EventBus
        from optifire.exec.broker_alpaca import AlpacaBroker
        from optifire.plugins import PluginContext, PluginRegistry
        print("   ✓ Core imports successful")
    except Exception as e:
        print(f"   ✗ Import failed: {e}")
        return False

    # 2. Test plugin registry
    print("\n2️⃣ Testing plugin registry...")
    try:
        from optifire.plugins import registry

        # Import and register new plugins
        new_plugins = [
            ('alpha_dark_pool_flow', 'AlphaDarkPoolFlow'),
            ('alpha_insider_trading', 'AlphaInsiderTrading'),
            ('alpha_sector_rotation', 'AlphaSectorRotation'),
            ('ml_transformer_ts', 'MlTransformerTs'),
            ('exec_twap', 'ExecTwap'),
            ('risk_corr_breakdown', 'RiskCorrBreakdown'),
            ('data_reddit_wsb', 'DataRedditWsb'),
        ]

        registered = 0
        for plugin_id, class_name in new_plugins:
            try:
                sys.path.insert(0, 'optifire/plugins')
                mod = __import__(f'{plugin_id}.impl', fromlist=[class_name])
                PluginClass = getattr(mod, class_name)
                plugin = PluginClass()
                registry.register(plugin)
                registered += 1
            except Exception as e:
                print(f"   ✗ Failed to register {plugin_id}: {e}")

        print(f"   ✓ Registered {registered}/{len(new_plugins)} new plugins")
        print(f"   ✓ Total plugins in registry: {len(registry.list_all())}")
    except Exception as e:
        print(f"   ✗ Registry test failed: {e}")
        return False

    # 3. Test database initialization
    print("\n3️⃣ Testing database...")
    try:
        db = Database(Path("data/test_integration.db"))
        await db.initialize()
        print("   ✓ Database initialized")

        # Test inserting a signal (using correct schema)
        await db.execute(
            "INSERT INTO signals (plugin_id, symbol, signal_type, value, confidence) VALUES (?, ?, ?, ?, ?)",
            ("alpha_dark_pool_flow", "AAPL", "BUY", 1.0, 0.8)
        )
        print("   ✓ Database write test passed")
    except Exception as e:
        print(f"   ✗ Database test failed: {e}")
        return False

    # 4. Test event bus
    print("\n4️⃣ Testing event bus...")
    try:
        bus = EventBus()
        await bus.start()

        received = []
        async def handler(event):
            received.append((event.type, event.data))

        await bus.subscribe("test_topic", handler)
        await bus.publish("test_topic", {"value": 42}, source="test")
        await asyncio.sleep(0.2)

        if received and len(received) > 0 and received[0][1]["value"] == 42:
            print("   ✓ Event bus working")
        else:
            print("   ✗ Event bus not receiving events")
            return False

        await bus.stop()
    except Exception as e:
        print(f"   ✗ Event bus test failed: {e}")
        return False

    # 5. Test plugin execution with real context
    print("\n5️⃣ Testing plugin execution...")
    try:
        plugin = registry.get('alpha_dark_pool_flow')
        if plugin:
            ctx = PluginContext(
                config={},
                db=db,
                bus=None,
                data={'symbol': 'AAPL', 'volume': 5000000, 'avg_daily_volume': 50000000}
            )
            result = await plugin.run(ctx)

            if result.success:
                print(f"   ✓ Plugin executed: {result.data.get('interpretation', 'N/A')[:60]}")
            else:
                print(f"   ✗ Plugin failed: {result.error}")
                return False
        else:
            print("   ✗ Plugin not found in registry")
            return False
    except Exception as e:
        print(f"   ✗ Plugin execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 6. Test FastAPI can start
    print("\n6️⃣ Testing FastAPI initialization...")
    try:
        from main import create_app_with_lifespan
        app = create_app_with_lifespan()
        print(f"   ✓ FastAPI app created with {len(app.routes)} routes")
    except Exception as e:
        print(f"   ✗ FastAPI init failed: {e}")
        return False

    print("\n" + "="*60)
    print("✅ ALL INTEGRATION TESTS PASSED")
    print("="*60)
    return True

async def main():
    success = await test_system_integration()
    return success

if __name__ == '__main__':
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

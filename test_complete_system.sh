#!/bin/bash
# Complete System Test Suite voor OptiFIRE

echo "═══════════════════════════════════════════════════════════════════════════════"
echo "🧪 OPTIFIIRE COMPLETE SYSTEM TEST"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""

PASSED=0
FAILED=0

test_result() {
    if [ $1 -eq 0 ]; then
        echo "✅ PASSED: $2"
        ((PASSED++))
    else
        echo "❌ FAILED: $2"
        ((FAILED++))
    fi
}

# TEST 1: Check Python version
echo "TEST 1: Python Version"
python3 --version > /dev/null 2>&1
test_result $? "Python 3 installed"
echo ""

# TEST 2: Check required Python packages
echo "TEST 2: Python Dependencies"
python3 -c "import asyncio, fastapi, uvicorn, alpaca_trade_api, openai" 2>/dev/null
test_result $? "Required Python packages installed"
echo ""

# TEST 3: Check environment file
echo "TEST 3: Environment Configuration"
if [ -f "/root/optifire/secrets.env" ]; then
    grep -q "ALPACA_API_KEY" /root/optifire/secrets.env
    test_result $? "secrets.env exists with ALPACA_API_KEY"
else
    test_result 1 "secrets.env exists"
fi
echo ""

# TEST 4: Check all 75 plugins exist
echo "TEST 4: Plugin Files"
PLUGIN_COUNT=$(find /root/optifire/optifire/plugins -name "impl.py" -type f | wc -l)
if [ $PLUGIN_COUNT -ge 75 ]; then
    test_result 0 "All 75+ plugin files exist ($PLUGIN_COUNT found)"
else
    test_result 1 "All 75 plugin files exist (only $PLUGIN_COUNT found)"
fi
echo ""

# TEST 5: Test plugin imports
echo "TEST 5: Plugin Imports"
python3 << 'PYEOF'
import sys
try:
    from optifire.plugins.alpha_vix_regime.impl import AlphaVixRegime
    from optifire.plugins.risk_drawdown_derisk.impl import RiskDrawdownDerisk
    from optifire.plugins.fe_kalman.impl import FeKalman
    from optifire.plugins.ai_bandit_alloc.impl import AiBanditAlloc
    print("✅ Core plugins import successfully")
    sys.exit(0)
except Exception as e:
    print(f"❌ Plugin import failed: {e}")
    sys.exit(1)
PYEOF
test_result $? "Core plugins can be imported"
echo ""

# TEST 6: Systemd service file
echo "TEST 6: Systemd Service"
if [ -f "/etc/systemd/system/optifire.service" ]; then
    test_result 0 "Systemd service file exists"
else
    test_result 1 "Systemd service file exists"
fi

systemctl is-enabled optifire.service > /dev/null 2>&1
test_result $? "Systemd service is enabled"
echo ""

# TEST 7: Cronjob configuration
echo "TEST 7: Cronjob"
crontab -l 2>/dev/null | grep -q "restart_daily.sh"
test_result $? "Cronjob configured for daily restart"
echo ""

# TEST 8: Management scripts
echo "TEST 8: Management Scripts"
if [ -x "/root/optifire/manage.sh" ]; then
    test_result 0 "manage.sh exists and is executable"
else
    test_result 1 "manage.sh exists and is executable"
fi

if [ -x "/root/optifire/restart_daily.sh" ]; then
    test_result 0 "restart_daily.sh exists and is executable"
else
    test_result 1 "restart_daily.sh exists and is executable"
fi
echo ""

# TEST 9: Database initialization
echo "TEST 9: Database"
python3 << 'PYEOF'
import sys
from pathlib import Path
try:
    from optifire.core.db import Database
    db_path = Path("/tmp/test_optifire.db")
    db = Database(db_path)
    db_path.unlink(missing_ok=True)
    print("✅ Database can be initialized")
    sys.exit(0)
except Exception as e:
    print(f"❌ Database initialization failed: {e}")
    sys.exit(1)
PYEOF
test_result $? "Database initialization works"
echo ""

# TEST 10: Auto-trader initialization
echo "TEST 10: Auto-Trader"
timeout 5 python3 << 'PYEOF' 2>/dev/null
import asyncio
import sys
from optifire.auto_trader import AutoTrader

async def test():
    try:
        trader = AutoTrader()
        print("✅ Auto-trader can be instantiated")
        return 0
    except Exception as e:
        print(f"❌ Auto-trader failed: {e}")
        return 1

sys.exit(asyncio.run(test()))
PYEOF
test_result $? "Auto-trader can be instantiated"
echo ""

# TEST 11: Config file
echo "TEST 11: Configuration"
if [ -f "/root/optifire/config.yaml" ]; then
    test_result 0 "config.yaml exists"
else
    test_result 1 "config.yaml exists"
fi
echo ""

# TEST 12: Documentation
echo "TEST 12: Documentation"
DOC_COUNT=0
[ -f "/root/optifire/DEPLOYMENT_GUIDE.md" ] && ((DOC_COUNT++))
[ -f "/root/optifire/PLUGIN_IMPLEMENTATION_COMPLETE.md" ] && ((DOC_COUNT++))
[ -f "/root/optifire/AUTO_TRADING_GUIDE.md" ] && ((DOC_COUNT++))
[ -f "/root/optifire/PLUGIN_INTEGRATION.md" ] && ((DOC_COUNT++))

if [ $DOC_COUNT -ge 4 ]; then
    test_result 0 "All documentation files exist ($DOC_COUNT/4)"
else
    test_result 1 "All documentation files exist ($DOC_COUNT/4)"
fi
echo ""

# TEST 13: FastAPI startup (quick test)
echo "TEST 13: FastAPI Server"
timeout 3 python3 -c "from optifire.main import create_app; app = create_app(); print('FastAPI app created')" 2>/dev/null
test_result $? "FastAPI app can be created"
echo ""

# TEST 14: Alpaca connection
echo "TEST 14: Alpaca Broker Connection"
python3 << 'PYEOF'
import sys
try:
    from optifire.exec.broker_alpaca import AlpacaBroker
    broker = AlpacaBroker(paper=True)
    print("✅ Alpaca broker connected")
    sys.exit(0)
except Exception as e:
    print(f"❌ Alpaca connection failed: {e}")
    sys.exit(1)
PYEOF
test_result $? "Alpaca broker connection works"
echo ""

# TEST 15: OpenAI client
echo "TEST 15: OpenAI Client"
python3 << 'PYEOF'
import sys
try:
    from optifire.ai.openai_client import OpenAIClient
    client = OpenAIClient()
    print("✅ OpenAI client initialized")
    sys.exit(0)
except Exception as e:
    print(f"❌ OpenAI client failed: {e}")
    sys.exit(1)
PYEOF
test_result $? "OpenAI client initialization works"
echo ""

# SUMMARY
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "📊 TEST SUMMARY"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""
echo "✅ PASSED: $PASSED tests"
echo "❌ FAILED: $FAILED tests"
echo "📊 TOTAL:  $((PASSED + FAILED)) tests"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "🎉🎉🎉 ALL TESTS PASSED! SYSTEM IS READY! 🎉🎉🎉"
    echo ""
    exit 0
else
    echo "⚠️  SOME TESTS FAILED - CHECK ERRORS ABOVE"
    echo ""
    exit 1
fi

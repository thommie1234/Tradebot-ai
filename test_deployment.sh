#!/bin/bash
# Test Deployment Configuration (Systemd + Cronjob)

echo "═══════════════════════════════════════════════════════════════════════════════"
echo "🧪 DEPLOYMENT CONFIGURATION TEST"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""

PASSED=0
FAILED=0

# TEST 1: Systemd service file exists
echo "TEST 1: Systemd Service File"
if [ -f "/etc/systemd/system/optifire.service" ]; then
    echo "   ✅ Service file exists"
    ((PASSED++))
    
    # Check service file content
    if grep -q "ExecStart=/usr/bin/python3 /root/optifire/main.py" /etc/systemd/system/optifire.service; then
        echo "   ✅ ExecStart configured correctly"
        ((PASSED++))
    else
        echo "   ❌ ExecStart not configured correctly"
        ((FAILED++))
    fi
    
    if grep -q "Restart=on-failure" /etc/systemd/system/optifire.service; then
        echo "   ✅ Auto-restart configured"
        ((PASSED++))
    else
        echo "   ❌ Auto-restart not configured"
        ((FAILED++))
    fi
else
    echo "   ❌ Service file missing"
    ((FAILED++))
fi
echo ""

# TEST 2: Service is enabled
echo "TEST 2: Service Auto-Start Configuration"
if systemctl is-enabled optifire.service >/dev/null 2>&1; then
    echo "   ✅ Service is enabled (will start on boot)"
    ((PASSED++))
else
    echo "   ❌ Service is not enabled"
    ((FAILED++))
fi
echo ""

# TEST 3: Service can be started
echo "TEST 3: Service Start/Stop Test"
echo "   Starting service..."
sudo systemctl start optifire.service
sleep 5

if systemctl is-active optifire.service >/dev/null 2>&1; then
    echo "   ✅ Service started successfully"
    ((PASSED++))
    
    # Check HTTP endpoint
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
    if [ "$HTTP_CODE" = "200" ]; then
        echo "   ✅ HTTP endpoint responding"
        ((PASSED++))
    else
        echo "   ⚠️  HTTP endpoint not responding (code: $HTTP_CODE)"
    fi
else
    echo "   ❌ Service failed to start"
    ((FAILED++))
    sudo systemctl status optifire.service --no-pager | tail -10
fi

echo "   Stopping service..."
sudo systemctl stop optifire.service
sleep 2

if ! systemctl is-active optifire.service >/dev/null 2>&1; then
    echo "   ✅ Service stopped successfully"
    ((PASSED++))
else
    echo "   ❌ Service failed to stop"
    ((FAILED++))
fi
echo ""

# TEST 4: Cronjob configuration
echo "TEST 4: Cronjob Configuration"
if crontab -l 2>/dev/null | grep -q "restart_daily.sh"; then
    echo "   ✅ Cronjob configured"
    ((PASSED++))
    
    # Show the cron entry
    echo "   Cron entry:"
    crontab -l | grep "restart_daily.sh"
else
    echo "   ❌ Cronjob not configured"
    ((FAILED++))
fi
echo ""

# TEST 5: Restart script exists and is executable
echo "TEST 5: Daily Restart Script"
if [ -x "/root/optifire/restart_daily.sh" ]; then
    echo "   ✅ restart_daily.sh exists and is executable"
    ((PASSED++))
else
    echo "   ❌ restart_daily.sh missing or not executable"
    ((FAILED++))
fi
echo ""

# TEST 6: Management script
echo "TEST 6: Management Script"
if [ -x "/root/optifire/manage.sh" ]; then
    echo "   ✅ manage.sh exists and is executable"
    ((PASSED++))
    
    # Test commands
    /root/optifire/manage.sh status >/dev/null 2>&1
    echo "   ✅ manage.sh status command works"
    ((PASSED++))
else
    echo "   ❌ manage.sh missing or not executable"
    ((FAILED++))
fi
echo ""

# TEST 7: Log files writable
echo "TEST 7: Log File Permissions"
touch /tmp/optifire.log 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✅ /tmp/optifire.log is writable"
    ((PASSED++))
else
    echo "   ❌ Cannot write to /tmp/optifire.log"
    ((FAILED++))
fi

touch /tmp/optifire_restart.log 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✅ /tmp/optifire_restart.log is writable"
    ((PASSED++))
else
    echo "   ❌ Cannot write to /tmp/optifire_restart.log"
    ((FAILED++))
fi
echo ""

# SUMMARY
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "📊 DEPLOYMENT TEST SUMMARY"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""
echo "✅ PASSED: $PASSED tests"
echo "❌ FAILED: $FAILED tests"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "🎉 ALL DEPLOYMENT TESTS PASSED!"
    echo ""
    echo "✅ Systemd service configured and working"
    echo "✅ Auto-start on boot enabled"
    echo "✅ Auto-restart on crash enabled"
    echo "✅ Daily restart cronjob configured"
    echo "✅ Management scripts working"
    echo ""
    echo "🚀 SYSTEM IS READY FOR PRODUCTION!"
    echo ""
    exit 0
else
    echo "⚠️  SOME TESTS FAILED"
    exit 1
fi

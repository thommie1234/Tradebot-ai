#!/bin/bash
# OptiFIRE Auto-Restart Monitor
# Checks server health and restarts if crashed

LOG_FILE="/tmp/optifire_monitor.log"
SERVER_LOG="/tmp/optifire.log"
HEALTH_URL="http://localhost:8000/health"
CHECK_INTERVAL=30  # seconds

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

start_server() {
    log "Starting OptiFIRE server..."
    cd /root/optifire
    nohup python3 main.py > "$SERVER_LOG" 2>&1 &
    SERVER_PID=$!
    log "Server started with PID: $SERVER_PID"
    sleep 5
}

check_health() {
    curl -s -f "$HEALTH_URL" > /dev/null 2>&1
    return $?
}

log "OptiFIRE Monitor started"

# Initial start
if ! check_health; then
    log "Server not running, starting initial instance..."
    start_server
fi

# Monitor loop
while true; do
    sleep "$CHECK_INTERVAL"

    if check_health; then
        log "✓ Server healthy"
    else
        log "✗ Server health check failed, restarting..."

        # Kill any stuck processes
        pkill -9 python3
        sleep 2

        # Restart server
        start_server

        # Verify it started
        sleep 5
        if check_health; then
            log "✓ Server successfully restarted"
        else
            log "✗ Server failed to restart, will retry in $CHECK_INTERVAL seconds"
        fi
    fi
done

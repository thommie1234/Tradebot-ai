#!/bin/bash
# Daily restart script for OptiFIRE
# Runs at 00:00 every day

echo "$(date): Daily restart initiated" >> /tmp/optifire_restart.log

# Stop the service gracefully
systemctl stop optifire.service

# Wait for it to stop
sleep 5

# Start the service
systemctl start optifire.service

# Check status
if systemctl is-active --quiet optifire.service; then
    echo "$(date): Service restarted successfully" >> /tmp/optifire_restart.log
else
    echo "$(date): ERROR - Service failed to start!" >> /tmp/optifire_restart.log
    # Send notification (you can add email/Discord webhook here)
fi

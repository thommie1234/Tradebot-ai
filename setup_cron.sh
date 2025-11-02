#!/bin/bash
# Setup cron job for daily database backups

CRON_JOB="0 2 * * * /root/optifire/backup.sh"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "backup.sh"; then
    echo "Cron job already exists"
    crontab -l
else
    # Add cron job (daily at 2 AM)
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "✓ Cron job added: Daily backup at 2:00 AM"
    echo ""
    echo "Current crontab:"
    crontab -l
fi

echo ""
echo "To manually run backup: /root/optifire/backup.sh"
echo "To view backup logs: tail -f /tmp/optifire_backup.log"

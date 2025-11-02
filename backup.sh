#!/bin/bash
# OptiFIRE Database Backup Script
# Backs up SQLite database with proper WAL checkpoint

DB_PATH="/root/optifire/data/optifire.db"
BACKUP_DIR="/root/optifire/backups"
MAX_BACKUPS=30  # Keep last 30 backups (1 month if daily)
LOG_FILE="/tmp/optifire_backup.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Generate backup filename with timestamp
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
BACKUP_FILE="$BACKUP_DIR/optifire_${TIMESTAMP}.db"

log "Starting database backup..."

# Check if database exists
if [ ! -f "$DB_PATH" ]; then
    log "ERROR: Database not found at $DB_PATH"
    exit 1
fi

# Perform SQLite backup with WAL checkpoint
# This ensures all WAL data is flushed to the main database
sqlite3 "$DB_PATH" "PRAGMA wal_checkpoint(FULL);" 2>&1 | tee -a "$LOG_FILE"

# Copy database file
cp "$DB_PATH" "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    # Get file size
    SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    log "✓ Backup successful: $BACKUP_FILE ($SIZE)"

    # Clean up old backups (keep only MAX_BACKUPS most recent)
    BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/optifire_*.db 2>/dev/null | wc -l)
    if [ "$BACKUP_COUNT" -gt "$MAX_BACKUPS" ]; then
        log "Cleaning up old backups (keeping $MAX_BACKUPS most recent)..."
        ls -1t "$BACKUP_DIR"/optifire_*.db | tail -n +$((MAX_BACKUPS + 1)) | xargs rm -f
        log "✓ Cleanup complete"
    fi

    # Show backup list
    log "Current backups:"
    ls -lh "$BACKUP_DIR"/optifire_*.db | tail -5 | tee -a "$LOG_FILE"
else
    log "✗ Backup failed"
    exit 1
fi

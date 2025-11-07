#!/bin/bash
# Export OptiFIRE for migration to laptop

set -e

echo "=========================================="
echo "OptiFIRE Migration Export"
echo "=========================================="

# Create export directory
EXPORT_DIR="/tmp/optifire_export"
rm -rf "$EXPORT_DIR"
mkdir -p "$EXPORT_DIR"

echo "✓ Created export directory: $EXPORT_DIR"

# Copy source code
echo "Copying source code..."
cp -r /root/optifire/optifire "$EXPORT_DIR/"
cp /root/optifire/main.py "$EXPORT_DIR/"
cp /root/optifire/requirements.txt "$EXPORT_DIR/"
cp /root/optifire/config.yaml "$EXPORT_DIR/" 2>/dev/null || echo "⚠ config.yaml not found (will be auto-generated)"
cp /root/optifire/features.yaml "$EXPORT_DIR/" 2>/dev/null || echo "⚠ features.yaml not found (will be auto-generated)"

# Copy secrets (IMPORTANT!)
if [ -f /root/optifire/secrets.env ]; then
    cp /root/optifire/secrets.env "$EXPORT_DIR/"
    echo "✓ Copied secrets.env (API keys)"
else
    echo "⚠ WARNING: secrets.env not found! You'll need to recreate API keys manually."
fi

# Copy database
echo "Copying database..."
if [ -f /root/optifire/data/optifire.db ]; then
    mkdir -p "$EXPORT_DIR/data"
    cp /root/optifire/data/optifire.db "$EXPORT_DIR/data/"
    DB_SIZE=$(du -h /root/optifire/data/optifire.db | cut -f1)
    echo "✓ Copied database (size: $DB_SIZE)"
else
    echo "⚠ Database not found (fresh install will create new one)"
fi

# Copy backups (optional)
if [ -d /root/optifire/data/backups ]; then
    echo "Copying database backups..."
    cp -r /root/optifire/data/backups "$EXPORT_DIR/data/" 2>/dev/null || true
    BACKUP_COUNT=$(ls /root/optifire/data/backups/*.db 2>/dev/null | wc -l)
    echo "✓ Copied $BACKUP_COUNT backup files"
fi

# Copy scripts
echo "Copying utility scripts..."
cp /root/optifire/backup.sh "$EXPORT_DIR/" 2>/dev/null || true
cp /root/optifire/install_dependencies.sh "$EXPORT_DIR/" 2>/dev/null || true

# Create archive
echo "Creating archive..."
cd /tmp
tar -czf optifire_migration.tar.gz optifire_export/
ARCHIVE_SIZE=$(du -h optifire_migration.tar.gz | cut -f1)
mv optifire_migration.tar.gz /root/optifire/

echo ""
echo "=========================================="
echo "✓ Export complete!"
echo "=========================================="
echo ""
echo "Archive created: /root/optifire/optifire_migration.tar.gz"
echo "Size: $ARCHIVE_SIZE"
echo ""
echo "Download to your laptop:"
echo "  scp root@$(hostname -I | awk '{print $1}'):/root/optifire/optifire_migration.tar.gz ~/Downloads/"
echo ""
echo "Or if you have the IP:"
echo "  scp root@YOUR_SERVER_IP:/root/optifire/optifire_migration.tar.gz ~/Downloads/"
echo ""
echo "Next steps:"
echo "  1. Download the archive to your laptop"
echo "  2. Follow instructions in MIGRATION_GUIDE.md"
echo "  3. Run install_on_laptop.sh on your laptop"
echo ""
echo "⚠ IMPORTANT: Keep secrets.env safe (contains API keys)!"
echo "=========================================="

# Cleanup
rm -rf "$EXPORT_DIR"

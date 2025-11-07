#!/bin/bash
# Setup auto-start service for OptiFIRE on laptop

set -e

echo "=========================================="
echo "OptiFIRE Auto-Start Setup"
echo "=========================================="

# Get absolute path to optifire directory
OPTIFIRE_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "OptiFIRE directory: $OPTIFIRE_DIR"

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
else
    echo "⚠ Unsupported OS: $OSTYPE"
    echo "For Windows, use Task Scheduler (see MIGRATION_GUIDE.md)"
    exit 1
fi

echo "Detected OS: $OS"
echo ""

if [[ "$OS" == "linux" ]]; then
    echo "Setting up systemd user service..."

    # Create systemd user directory
    mkdir -p ~/.config/systemd/user

    # Create service file
    cat > ~/.config/systemd/user/optifire.service <<EOF
[Unit]
Description=OptiFIRE Algorithmic Trading Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=$OPTIFIRE_DIR
ExecStart=$OPTIFIRE_DIR/venv/bin/python $OPTIFIRE_DIR/main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Environment
Environment="PATH=$OPTIFIRE_DIR/venv/bin:/usr/local/bin:/usr/bin:/bin"

[Install]
WantedBy=default.target
EOF

    echo "✓ Service file created: ~/.config/systemd/user/optifire.service"

    # Reload systemd
    systemctl --user daemon-reload
    echo "✓ Systemd reloaded"

    # Enable service
    systemctl --user enable optifire.service
    echo "✓ Service enabled (will start on boot)"

    # Start service
    systemctl --user start optifire.service
    echo "✓ Service started"

    # Enable lingering (keeps user services running after logout)
    loginctl enable-linger $USER
    echo "✓ User lingering enabled"

    echo ""
    echo "=========================================="
    echo "✓ Auto-start configured!"
    echo "=========================================="
    echo ""
    echo "Service commands:"
    echo "  Status:  systemctl --user status optifire"
    echo "  Stop:    systemctl --user stop optifire"
    echo "  Restart: systemctl --user restart optifire"
    echo "  Logs:    journalctl --user -u optifire -f"
    echo ""
    echo "Check status now:"
    sleep 2
    systemctl --user status optifire --no-pager

elif [[ "$OS" == "macos" ]]; then
    echo "Setting up LaunchAgent..."

    # Create LaunchAgents directory
    mkdir -p ~/Library/LaunchAgents

    # Create plist file
    PLIST_FILE=~/Library/LaunchAgents/com.optifire.tradebot.plist
    cat > "$PLIST_FILE" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.optifire.tradebot</string>

    <key>ProgramArguments</key>
    <array>
        <string>$OPTIFIRE_DIR/venv/bin/python</string>
        <string>$OPTIFIRE_DIR/main.py</string>
    </array>

    <key>WorkingDirectory</key>
    <string>$OPTIFIRE_DIR</string>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>

    <key>StandardOutPath</key>
    <string>$OPTIFIRE_DIR/logs/optifire.log</string>

    <key>StandardErrorPath</key>
    <string>$OPTIFIRE_DIR/logs/optifire_error.log</string>

    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>$OPTIFIRE_DIR/venv/bin:/usr/local/bin:/usr/bin:/bin</string>
    </dict>
</dict>
</plist>
EOF

    echo "✓ LaunchAgent created: $PLIST_FILE"

    # Load the agent
    launchctl unload "$PLIST_FILE" 2>/dev/null || true
    launchctl load "$PLIST_FILE"
    echo "✓ LaunchAgent loaded"

    # Start the service
    launchctl start com.optifire.tradebot
    echo "✓ Service started"

    echo ""
    echo "=========================================="
    echo "✓ Auto-start configured!"
    echo "=========================================="
    echo ""
    echo "Service commands:"
    echo "  Stop:    launchctl stop com.optifire.tradebot"
    echo "  Start:   launchctl start com.optifire.tradebot"
    echo "  Restart: launchctl stop com.optifire.tradebot && launchctl start com.optifire.tradebot"
    echo "  Status:  launchctl list | grep optifire"
    echo "  Logs:    tail -f $OPTIFIRE_DIR/logs/optifire.log"
    echo ""
    echo "⚠ IMPORTANT: Prevent sleep in System Preferences → Energy Saver"
fi

echo ""
echo "Dashboard will be available at: http://localhost:8000"
echo ""

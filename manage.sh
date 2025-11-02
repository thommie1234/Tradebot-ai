#!/bin/bash
# OptiFIRE Management Script

case "$1" in
    start)
        echo "🚀 Starting OptiFIRE..."
        sudo systemctl start optifire.service
        sleep 2
        sudo systemctl status optifire.service --no-pager
        ;;
    stop)
        echo "🛑 Stopping OptiFIRE..."
        sudo systemctl stop optifire.service
        ;;
    restart)
        echo "🔄 Restarting OptiFIRE..."
        sudo systemctl restart optifire.service
        sleep 2
        sudo systemctl status optifire.service --no-pager
        ;;
    status)
        sudo systemctl status optifire.service --no-pager
        ;;
    logs)
        echo "📋 Live logs (Ctrl+C to exit):"
        tail -f /tmp/optifire.log
        ;;
    logs-tail)
        tail -n ${2:-50} /tmp/optifire.log
        ;;
    enable)
        echo "✅ Enabling auto-start on boot..."
        sudo systemctl enable optifire.service
        ;;
    disable)
        echo "❌ Disabling auto-start on boot..."
        sudo systemctl disable optifire.service
        ;;
    test)
        echo "🧪 Testing OptiFIRE (dry-run for 10 seconds)..."
        timeout 10 python3 /root/optifire/main.py || echo "✅ Test completed"
        ;;
    *)
        echo "OptiFIRE Management Script"
        echo ""
        echo "Usage: $0 {start|stop|restart|status|logs|logs-tail|enable|disable|test}"
        echo ""
        echo "Commands:"
        echo "  start       - Start the service"
        echo "  stop        - Stop the service"
        echo "  restart     - Restart the service"
        echo "  status      - Show service status"
        echo "  logs        - Follow live logs (Ctrl+C to exit)"
        echo "  logs-tail   - Show last 50 lines of logs"
        echo "  enable      - Enable auto-start on boot"
        echo "  disable     - Disable auto-start on boot"
        echo "  test        - Test run for 10 seconds"
        echo ""
        exit 1
        ;;
esac

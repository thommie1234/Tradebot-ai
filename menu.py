#!/usr/bin/env python3
"""
OptiFIRE Control Menu
Easy management interface for OptiFIRE trading system
"""
import os
import sys
import subprocess
import time
import json
from pathlib import Path

# Colors
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BOLD = '\033[1m'
END = '\033[0m'

def clear_screen():
    os.system('clear' if os.name != 'nt' else 'cls')

def print_header():
    print(f"{BLUE}{BOLD}")
    print("=" * 60)
    print("   OptiFIRE - Trading System Control Panel")
    print("=" * 60)
    print(END)

def check_server_status():
    """Check if server is running."""
    result = subprocess.run(['pgrep', '-f', 'python3.*main.py'],
                          capture_output=True, text=True)
    return result.returncode == 0

def start_server():
    """Start the OptiFIRE server."""
    print(f"{YELLOW}Starting OptiFIRE server...{END}")

    if check_server_status():
        print(f"{RED}Server is already running!{END}")
        return

    subprocess.Popen(['nohup', 'python3', '-u', 'main.py'],
                    stdout=open('/tmp/optifire.log', 'w'),
                    stderr=subprocess.STDOUT)

    time.sleep(3)

    if check_server_status():
        print(f"{GREEN}✓ Server started successfully!{END}")
        print(f"Dashboard: http://185.181.8.39:8000")
    else:
        print(f"{RED}✗ Server failed to start. Check logs.{END}")

def stop_server():
    """Stop the OptiFIRE server."""
    print(f"{YELLOW}Stopping OptiFIRE server...{END}")

    if not check_server_status():
        print(f"{RED}Server is not running!{END}")
        return

    subprocess.run(['pkill', '-f', 'python3.*main.py'])
    time.sleep(1)

    if not check_server_status():
        print(f"{GREEN}✓ Server stopped successfully!{END}")
    else:
        print(f"{RED}✗ Failed to stop server{END}")

def restart_server():
    """Restart the OptiFIRE server."""
    stop_server()
    time.sleep(1)
    start_server()

def show_status():
    """Show server status and info."""
    print(f"{BOLD}Server Status:{END}")

    if check_server_status():
        print(f"  Status: {GREEN}RUNNING{END}")

        # Get PID
        result = subprocess.run(['pgrep', '-f', 'python3.*main.py'],
                              capture_output=True, text=True)
        print(f"  PID: {result.stdout.strip()}")

        # Try to get portfolio
        try:
            import urllib.request
            response = urllib.request.urlopen('http://localhost:8000/health', timeout=2)
            data = json.loads(response.read())
            print(f"  Health: {GREEN}OK{END}")

            response = urllib.request.urlopen('http://localhost:8000/metrics/portfolio', timeout=2)
            portfolio = json.loads(response.read())
            print(f"\n{BOLD}Portfolio:{END}")
            print(f"  Equity: ${portfolio['equity']:,.2f}")
            print(f"  Cash: ${portfolio['cash']:,.2f}")
            print(f"  P&L: ${portfolio['unrealized_pnl']:,.2f}")
        except Exception as e:
            print(f"  Health: {RED}Cannot connect{END}")
    else:
        print(f"  Status: {RED}STOPPED{END}")

    print(f"\n{BOLD}Dashboard:{END} http://185.181.8.39:8000")

def view_logs():
    """View server logs."""
    print(f"{BOLD}Recent Logs (last 30 lines):{END}\n")

    if Path('/tmp/optifire.log').exists():
        subprocess.run(['tail', '-30', '/tmp/optifire.log'])
    else:
        print(f"{RED}No logs found{END}")

    print(f"\n{YELLOW}Press Enter to continue...{END}")
    input()

def submit_test_order():
    """Submit a test order."""
    print(f"{BOLD}Submit Test Order{END}\n")

    if not check_server_status():
        print(f"{RED}Server is not running!{END}")
        return

    symbol = input(f"Symbol (e.g., AAPL): ").upper() or "AAPL"
    qty = input(f"Quantity (default: 1): ") or "1"
    side = input(f"Side (buy/sell, default: buy): ").lower() or "buy"

    print(f"\n{YELLOW}Submitting order...{END}")

    try:
        import urllib.request
        import json

        data = json.dumps({
            "symbol": symbol,
            "qty": float(qty),
            "side": side,
            "order_type": "market"
        }).encode('utf-8')

        req = urllib.request.Request(
            'http://localhost:8000/orders/submit',
            data=data,
            headers={'Content-Type': 'application/json'}
        )

        response = urllib.request.urlopen(req, timeout=5)
        result = json.loads(response.read())

        print(f"\n{GREEN}✓ Order submitted successfully!{END}")
        print(f"  Order ID: {result['order_id']}")
        print(f"  Symbol: {result['symbol']}")
        print(f"  Qty: {result['qty']}")
        print(f"  Status: {result['status']}")

    except Exception as e:
        print(f"{RED}✗ Order failed: {e}{END}")

    print(f"\n{YELLOW}Press Enter to continue...{END}")
    input()

def view_portfolio():
    """View portfolio details."""
    print(f"{BOLD}Portfolio Summary{END}\n")

    if not check_server_status():
        print(f"{RED}Server is not running!{END}")
        return

    try:
        import urllib.request

        # Portfolio
        response = urllib.request.urlopen('http://localhost:8000/metrics/portfolio', timeout=2)
        portfolio = json.loads(response.read())

        print(f"{BOLD}Account:{END}")
        print(f"  Equity:        ${portfolio['equity']:>12,.2f}")
        print(f"  Cash:          ${portfolio['cash']:>12,.2f}")
        print(f"  Buying Power:  ${portfolio['buying_power']:>12,.2f}")

        pnl_color = GREEN if portfolio['unrealized_pnl'] >= 0 else RED
        print(f"  Unrealized P&L: {pnl_color}${portfolio['unrealized_pnl']:>11,.2f}{END}")
        print(f"  Exposure:      {portfolio['exposure_pct']*100:>12.1f}%")

        # Positions
        response = urllib.request.urlopen('http://localhost:8000/metrics/positions', timeout=2)
        positions_data = json.loads(response.read())
        positions = positions_data['positions']

        if positions:
            print(f"\n{BOLD}Positions:{END}")
            print(f"  {'Symbol':<8} {'Qty':>8} {'Entry':>10} {'Current':>10} {'P&L':>12}")
            print("  " + "-" * 58)
            for pos in positions:
                pnl_color = GREEN if pos['unrealized_pnl'] >= 0 else RED
                print(f"  {pos['symbol']:<8} {pos['qty']:>8.2f} ${pos['avg_entry_price']:>9.2f} "
                      f"${pos['current_price']:>9.2f} {pnl_color}${pos['unrealized_pnl']:>11.2f}{END}")
        else:
            print(f"\n  No open positions")

        # Risk
        response = urllib.request.urlopen('http://localhost:8000/metrics/risk', timeout=2)
        risk = json.loads(response.read())

        print(f"\n{BOLD}Risk Metrics:{END}")
        print(f"  VaR (95%):     ${risk['var_95']:>12,.0f}")
        print(f"  CVaR (95%):    ${risk['cvar_95']:>12,.0f}")
        print(f"  Beta:          {risk['beta']:>13.2f}")
        print(f"  Sharpe:        {risk['sharpe']:>13.2f}")

    except Exception as e:
        print(f"{RED}✗ Cannot fetch portfolio: {e}{END}")

    print(f"\n{YELLOW}Press Enter to continue...{END}")
    input()

def view_orders():
    """View recent orders."""
    print(f"{BOLD}Recent Orders{END}\n")

    if not check_server_status():
        print(f"{RED}Server is not running!{END}")
        return

    try:
        import urllib.request

        response = urllib.request.urlopen('http://localhost:8000/orders/?limit=10', timeout=2)
        data = json.loads(response.read())
        orders = data['orders']

        if orders:
            print(f"  {'Order ID':<38} {'Symbol':<8} {'Side':<6} {'Qty':>6} {'Status':<10}")
            print("  " + "-" * 78)
            for order in orders:
                status_color = GREEN if order['status'] == 'filled' else YELLOW
                print(f"  {order['order_id']:<38} {order['symbol']:<8} {order['side']:<6} "
                      f"{order['qty']:>6.0f} {status_color}{order['status']:<10}{END}")
        else:
            print("  No orders found")

    except Exception as e:
        print(f"{RED}✗ Cannot fetch orders: {e}{END}")

    print(f"\n{YELLOW}Press Enter to continue...{END}")
    input()

def open_dashboard():
    """Open dashboard in browser."""
    print(f"{YELLOW}Opening dashboard...{END}")
    print(f"URL: http://185.181.8.39:8000")
    print(f"\n{YELLOW}Press Enter to continue...{END}")
    input()

def show_menu():
    """Display the main menu."""
    clear_screen()
    print_header()

    # Show status indicator
    if check_server_status():
        print(f"Status: {GREEN}● RUNNING{END}\n")
    else:
        print(f"Status: {RED}● STOPPED{END}\n")

    print(f"{BOLD}Server Control:{END}")
    print(f"  {BOLD}1{END} - Start Server")
    print(f"  {BOLD}2{END} - Stop Server")
    print(f"  {BOLD}3{END} - Restart Server")
    print(f"  {BOLD}4{END} - Server Status")
    print(f"  {BOLD}5{END} - View Logs")

    print(f"\n{BOLD}Trading:{END}")
    print(f"  {BOLD}6{END} - View Portfolio")
    print(f"  {BOLD}7{END} - View Orders")
    print(f"  {BOLD}8{END} - Submit Test Order")

    print(f"\n{BOLD}Other:{END}")
    print(f"  {BOLD}9{END} - Open Dashboard")
    print(f"  {BOLD}0{END} - Exit")

    print("\n" + "=" * 60)
    choice = input(f"{BOLD}Select option: {END}")

    return choice

def main():
    """Main menu loop."""
    os.chdir('/root/optifire')

    while True:
        choice = show_menu()

        if choice == '1':
            clear_screen()
            print_header()
            start_server()
            print(f"\n{YELLOW}Press Enter to continue...{END}")
            input()

        elif choice == '2':
            clear_screen()
            print_header()
            stop_server()
            print(f"\n{YELLOW}Press Enter to continue...{END}")
            input()

        elif choice == '3':
            clear_screen()
            print_header()
            restart_server()
            print(f"\n{YELLOW}Press Enter to continue...{END}")
            input()

        elif choice == '4':
            clear_screen()
            print_header()
            show_status()
            print(f"\n{YELLOW}Press Enter to continue...{END}")
            input()

        elif choice == '5':
            clear_screen()
            print_header()
            view_logs()

        elif choice == '6':
            clear_screen()
            print_header()
            view_portfolio()

        elif choice == '7':
            clear_screen()
            print_header()
            view_orders()

        elif choice == '8':
            clear_screen()
            print_header()
            submit_test_order()

        elif choice == '9':
            clear_screen()
            print_header()
            open_dashboard()

        elif choice == '0':
            clear_screen()
            print(f"{GREEN}Goodbye!{END}")
            sys.exit(0)

        else:
            print(f"{RED}Invalid option!{END}")
            time.sleep(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        clear_screen()
        print(f"\n{GREEN}Goodbye!{END}")
        sys.exit(0)

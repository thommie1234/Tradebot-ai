#!/usr/bin/env python3
"""
Simple demo server for OptiFIRE (no external dependencies)
"""
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Load secrets
def load_secrets():
    secrets = {}
    if os.path.exists('secrets.env'):
        with open('secrets.env') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    secrets[key.strip()] = value.strip()
    return secrets

secrets = load_secrets()

class OptiFIREHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path

        if path == '/':
            # Dashboard HTML
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('optifire/api/templates/dashboard.html', 'rb') as f:
                self.wfile.write(f.read())

        elif path == '/health':
            self.json_response({'status': 'healthy', 'message': 'OptiFIRE Demo Server'})

        elif path == '/metrics/portfolio':
            self.json_response({
                'equity': 100000.0,
                'cash': 50000.0,
                'positions_value': 50000.0,
                'buying_power': 200000.0,
                'unrealized_pnl': 1250.50,
                'realized_pnl': 500.00,
                'exposure_pct': 0.50
            })

        elif path == '/metrics/positions':
            self.json_response({
                'positions': [
                    {
                        'symbol': 'AAPL',
                        'qty': 10,
                        'side': 'long',
                        'avg_entry_price': 175.50,
                        'current_price': 180.25,
                        'market_value': 1802.50,
                        'unrealized_pnl': 47.50,
                        'unrealized_pnl_pct': 2.71,
                        'cost_basis': 1755.00
                    },
                    {
                        'symbol': 'TSLA',
                        'qty': 5,
                        'side': 'long',
                        'avg_entry_price': 250.00,
                        'current_price': 255.00,
                        'market_value': 1275.00,
                        'unrealized_pnl': 25.00,
                        'unrealized_pnl_pct': 2.00,
                        'cost_basis': 1250.00
                    }
                ]
            })

        elif path == '/metrics/risk':
            self.json_response({
                'exposure_pct': 0.50,
                'var_95': 2000.0,
                'cvar_95': 2500.0,
                'beta': 1.1,
                'drawdown': 0.02,
                'sharpe': 1.5,
                'num_positions': 2
            })

        elif path == '/metrics/performance':
            self.json_response({
                'total_return_pct': 5.5,
                'sharpe_ratio': 1.5,
                'max_drawdown': 8.2,
                'win_rate': 0.65,
                'total_trades': 42,
                'unrealized_pnl': 1250.50,
                'realized_pnl': 500.00
            })

        elif path == '/orders/':
            self.json_response({
                'orders': [
                    {
                        'order_id': 'demo_001',
                        'symbol': 'AAPL',
                        'side': 'buy',
                        'qty': 10,
                        'status': 'filled'
                    }
                ]
            })

        elif path == '/events/stream':
            # SSE stream
            self.send_response(200)
            self.send_header('Content-type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Connection', 'keep-alive')
            self.end_headers()

            # Send initial event
            event = json.dumps({
                'type': 'connected',
                'timestamp': '2025-11-01T16:00:00Z'
            })
            self.wfile.write(f'data: {event}\n\n'.encode())
            self.wfile.flush()

        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

    def do_POST(self):
        path = urlparse(self.path).path
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')

        if path == '/orders/submit':
            try:
                data = json.loads(body) if body else {}
                self.json_response({
                    'order_id': 'demo_' + str(hash(str(data)) % 10000),
                    'symbol': data.get('symbol', 'UNKNOWN'),
                    'qty': data.get('qty', 0),
                    'side': data.get('side', 'buy'),
                    'status': 'submitted',
                    'submitted_at': '2025-11-01T16:00:00Z'
                })
            except:
                self.json_response({'error': 'Invalid request'}, 400)
        else:
            self.send_response(404)
            self.end_headers()

    def json_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        print(f"[OptiFIRE] {format % args}")

def run(port=8000):
    server = HTTPServer(('0.0.0.0', port), OptiFIREHandler)
    print("=" * 60)
    print("OptiFIRE Demo Server")
    print("=" * 60)
    print(f"Server running on http://0.0.0.0:{port}")
    print(f"Dashboard: http://185.181.8.39:{port}")
    print("")
    print("Note: Install dependencies for full functionality:")
    print("  pip install -r requirements.txt")
    print("=" * 60)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()

if __name__ == '__main__':
    os.chdir('/root/optifire')
    run(8000)

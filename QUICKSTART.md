# OptiFIRE Quick Start Guide

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

Create a `secrets.env` file (already exists with your keys):

```env
ALPACA_API_KEY=your_key_here
ALPACA_API_SECRET=your_secret_here
ALPACA_PAPER=true

JWT_SECRET=your_jwt_secret
ADMIN_USER=admin
ADMIN_PASS=your_password

OPENAI_API_KEY=your_openai_key_here
```

### 3. Run the Server

```bash
# Method 1: Using the run script
./run.sh

# Method 2: Direct Python
python main.py
```

### 4. Access the Dashboard

Open your browser to: **http://localhost:8000**

---

## 📡 API Endpoints

### Portfolio & Metrics
- `GET /metrics/portfolio` - Current portfolio metrics
- `GET /metrics/positions` - All open positions  
- `GET /metrics/risk` - Risk metrics (VaR, CVaR, etc.)
- `GET /metrics/performance` - Performance stats
- `GET /metrics/plugins` - Plugin execution status

### Orders
- `POST /orders/submit` - Submit a new order
- `GET /orders/{order_id}` - Get order status
- `DELETE /orders/{order_id}` - Cancel an order
- `GET /orders/` - List recent orders

### Configuration
- `GET /config/runtime` - Get current configuration
- `PUT /config/runtime` - Update runtime config
- `GET /config/flags` - Get feature flags
- `POST /config/flags/{plugin_id}/toggle` - Toggle plugin
- `GET /config/history` - Configuration history
- `POST /config/rollback/{version}` - Rollback config

### Real-time Events
- `GET /events/stream` - Server-Sent Events (SSE) stream

### Health
- `GET /health` - Health check

---

## 🧪 Testing with curl

### Get Portfolio
```bash
curl http://localhost:8000/metrics/portfolio
```

### Submit an Order
```bash
curl -X POST http://localhost:8000/orders/submit \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "qty": 1,
    "side": "buy",
    "order_type": "market"
  }'
```

### Get Positions
```bash
curl http://localhost:8000/metrics/positions
```

### Stream Events
```bash
curl -N http://localhost:8000/events/stream
```

---

## 🔧 System Architecture

```
OptiFIRE/
├── main.py                 # Entry point & global state
├── optifire/
│   ├── core/              # Core infrastructure
│   │   ├── config.py      # Configuration management
│   │   ├── flags.py       # Feature flags
│   │   ├── db.py          # SQLite database
│   │   ├── bus.py         # Event bus
│   │   └── logger.py      # Logging
│   ├── api/               # FastAPI routes
│   │   ├── server.py      # FastAPI app
│   │   ├── routes_*.py    # API endpoints
│   │   ├── sse.py         # Server-Sent Events
│   │   └── templates/     # HTML dashboard
│   ├── exec/              # Execution layer
│   │   ├── broker_alpaca.py  # Alpaca integration
│   │   └── executor.py       # Order execution
│   ├── ai/                # AI/ML features
│   │   └── openai_client.py  # OpenAI integration
│   ├── risk/              # Risk management
│   └── plugins/           # Trading plugins (75 total)
└── data/                  # SQLite database & logs
```

---

## ✅ What's Implemented

### ✓ Fully Working APIs
1. **Orders API** - Full Alpaca integration
   - Submit market/limit/stop orders
   - Real-time order status
   - Order cancellation
   - Database persistence

2. **Metrics API** - Live portfolio data
   - Real-time equity & P&L from Alpaca
   - Position tracking
   - Risk calculations (VaR, CVaR, exposure)
   - Performance metrics

3. **Configuration API** - Runtime management
   - Hot-reload configuration
   - Feature flag toggles
   - Version history & rollback

4. **SSE Streaming** - Real-time updates
   - Portfolio updates every 2 seconds
   - Order events (submitted, filled, canceled)
   - Event bus integration

5. **Dashboard** - Modern web UI
   - Real-time portfolio metrics
   - Position table
   - Order submission form
   - Live event log
   - Built with HTMX + Tailwind CSS

### ✓ Core Infrastructure
- **Database**: SQLite with WAL mode
- **Event Bus**: Pub/sub for real-time events
- **Config Management**: YAML with hot-reload
- **Feature Flags**: Plugin enable/disable
- **Alpaca Broker**: Full integration (paper & live)
- **OpenAI Client**: Sentiment analysis & AI signals

---

## 🎯 Next Steps

### For Production Use:
1. Change secrets in `secrets.env`
2. Set `ALPACA_PAPER=false` for live trading
3. Configure risk limits in `config.yaml`
4. Enable desired plugins in `features.yaml`
5. Set up monitoring & alerting

### For Development:
1. Review plugin implementations in `optifire/plugins/`
2. Add custom alpha signals
3. Implement additional risk controls
4. Add external data feeds (Google Trends, news, etc.)
5. Enhance AI/ML features with OpenAI

---

## 🐛 Troubleshooting

### Alpaca Connection Failed
- Check your API keys in `secrets.env`
- Verify paper/live mode setting
- Check Alpaca API status

### Database Errors
- Delete `data/optifire.db` to reset
- Check file permissions

### Port Already in Use
- Change port in `config.yaml`: `api.port: 8001`
- Or kill existing process: `lsof -ti:8000 | xargs kill`

---

## 📚 Documentation

For detailed plugin documentation, see:
- `API_AND_PLUGIN_OVERVIEW.md` - Complete technical reference
- `API_QUICK_REFERENCE.md` - Quick API lookup
- `ANALYSIS_INDEX.md` - Project navigation guide

---

## 🎉 You're All Set!

Your OptiFIRE system is now **100% functional** with:
- ✅ Live Alpaca trading integration
- ✅ Real-time portfolio metrics
- ✅ Order execution & tracking
- ✅ Event streaming (SSE)
- ✅ Modern web dashboard
- ✅ OpenAI AI/ML capabilities
- ✅ 75 trading plugins ready to enable

**Start the server and access the dashboard at http://localhost:8000**

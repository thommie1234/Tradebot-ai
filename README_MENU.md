# OptiFIRE Control Menu

## 🚀 Quick Start

Start het menu met:

```bash
optifire
```

Of vanuit de optifire directory:

```bash
python3 menu.py
```

## 📋 Menu Opties

### Server Control
- **1** - Start Server - Start de OptiFIRE trading server
- **2** - Stop Server - Stop de server
- **3** - Restart Server - Herstart de server
- **4** - Server Status - Toon status & portfolio summary
- **5** - View Logs - Bekijk de laatste 30 regels logs

### Trading
- **6** - View Portfolio - Volledige portfolio met posities & risk metrics
- **7** - View Orders - Recent orders met status
- **8** - Submit Test Order - Plaats een test order interactief

### Other
- **9** - Open Dashboard - Dashboard URL
- **0** - Exit - Sluit het menu af

## 🎯 Handige Shortcuts

### Server beheren
```bash
# Start menu
optifire

# Direct server status (zonder menu)
curl http://localhost:8000/health
```

### Portfolio bekijken
```bash
# Via menu: optie 6
# Of direct:
curl http://localhost:8000/metrics/portfolio | python3 -m json.tool
```

### Order plaatsen
```bash
# Via menu: optie 8 (interactief)
# Of direct via API:
curl -X POST http://localhost:8000/orders/submit \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL","qty":1,"side":"buy","order_type":"market"}'
```

## 🌐 URLs

- **Dashboard**: http://185.181.8.39:8000
- **Health Check**: http://185.181.8.39:8000/health
- **API Docs**: http://185.181.8.39:8000/docs (FastAPI auto-generated)

## 📊 Menu Screenshots

```
============================================================
   OptiFIRE - Trading System Control Panel
============================================================

Status: ● RUNNING

Server Control:
  1 - Start Server
  2 - Stop Server
  3 - Restart Server
  4 - Server Status
  5 - View Logs

Trading:
  6 - View Portfolio
  7 - View Orders
  8 - Submit Test Order

Other:
  9 - Open Dashboard
  0 - Exit

============================================================
Select option: 
```

## 🔧 Troubleshooting

**Server won't start?**
- Check logs met optie 5
- Controleer of port 8000 vrij is: `lsof -i :8000`

**Can't connect to Alpaca?**
- Controleer je API keys in `secrets.env`
- Test met: `cat secrets.env | grep ALPACA`

**Menu werkt niet?**
- Start direct: `python3 menu.py`

## 📚 Meer Info

Zie ook:
- `QUICKSTART.md` - Volledige getting started guide
- `IMPLEMENTATION_SUMMARY.md` - Wat er allemaal geïmplementeerd is
- `API_AND_PLUGIN_OVERVIEW.md` - Technische documentatie

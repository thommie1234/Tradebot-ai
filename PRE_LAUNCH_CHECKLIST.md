# 🚀 Pre-Launch Checklist - Maandag Markt Open

## 🎯 Maandag Morning Quick Start

**VOOR de markt opent (voor 9:30 AM ET):**
```bash
# 1. Start server met monitoring
pkill -9 python3  # Stop oude processen
cd /root/optifire
nohup /root/optifire/monitor.sh > /tmp/monitor.log 2>&1 &

# 2. Check server status (wacht 10 seconden)
sleep 10
curl http://localhost:8000/health

# 3. Check Alpaca balance
curl http://localhost:8000/metrics/portfolio

# 4. Setup daily backup (eenmalig)
/root/optifire/setup_cron.sh

# 5. Open dashboard
# Browser: http://185.181.8.39:8000
```

**Tijdens markt (9:30 AM - 4:00 PM ET):**
- Monitor logs: `tail -f /tmp/optifire.log`
- Monitor health: `tail -f /tmp/optifire_monitor.log`
- Dashboard: http://185.181.8.39:8000

## ✅ Status Check

### Veiligheid
- [x] **ALPACA_PAPER=true** - Paper trading actief (NIET live geld!)
- [x] **$1,000 paper balance** - Test account
- [x] **Risk limits** geconfigureerd (30% max exposure, 10% per symbol)
- [x] **Market hours check** - Voorkomt market orders buiten uren
- [x] **Order size validation** - Check buying power BEFORE submitting
- [ ] **Position limits** - Maximaal aantal posities (nice to have)

### Systeem
- [x] **Server draait** - http://185.181.8.39:8000
- [x] **Database** - SQLite opgeslagen in data/optifire.db
- [x] **Alpaca connected** - API keys werken
- [x] **OpenAI connected** - AI features beschikbaar
- [x] **Event bus** - Real-time updates
- [x] **Logging** - /tmp/optifire.log

### APIs Werkend
- [x] **Orders API** - Submit/cancel/status
- [x] **Portfolio API** - Real-time data
- [x] **Metrics API** - Risk & performance
- [x] **SSE Streaming** - Live updates
- [x] **Dashboard** - 5 tabs met navigatie

## ⚠️ TODO voor Maandag

### Kritisch (MOET)
1. [x] **Order size validation** - ✅ DONE: Checkt buying power voor elke order
2. [x] **Auto-restart script** - ✅ DONE: monitor.sh + systemd service
3. [x] **Backup strategie** - ✅ DONE: backup.sh met cron job (daily 2 AM)

### Nice to Have
4. [ ] **Email alerts** - Bij grote verliezen
5. [ ] **Daily report** - Einde dag samenvatting
6. [ ] **Position monitoring** - Auto-close bij verlies

## ✅ Fixes Geïmplementeerd

### 1. Order Size Validation ✅
**Status**: DONE
**Locatie**: `optifire/api/routes_orders.py:49-72`
- Checkt buying power VOOR order submission
- Haalt huidige prijs op voor qty-based orders
- Blokkeert orders die buying power overschrijden
- Geeft duidelijke error: "Insufficient buying power. Order cost: $X, Available: $Y"

### 2. Auto-Restart ✅
**Status**: DONE
**Bestanden**:
- `monitor.sh` - Health check elke 30 seconden, auto-restart bij crash
- `optifire.service` - Systemd service voor boot-time start
**Gebruik**:
```bash
# Manual monitoring (in background)
nohup /root/optifire/monitor.sh &

# Or install as systemd service
sudo cp optifire.service /etc/systemd/system/
sudo systemctl enable optifire
sudo systemctl start optifire
```

### 3. Database Backup ✅
**Status**: DONE
**Bestanden**:
- `backup.sh` - WAL checkpoint + backup, houdt laatste 30 backups
- `setup_cron.sh` - Instellen daily backup (2 AM)
**Gebruik**:
```bash
# Setup daily automatic backup
/root/optifire/setup_cron.sh

# Manual backup
/root/optifire/backup.sh

# Restore from backup
cp /root/optifire/backups/optifire_YYYYMMDD_HHMMSS.db /root/optifire/data/optifire.db
```

## 📞 Emergency Commands

```bash
# Stop alle trading
pkill -9 python3

# Check logs
tail -f /tmp/optifire.log

# Restart server
nohup python3 main.py > /tmp/optifire.log 2>&1 &

# Check positions
curl http://localhost:8000/metrics/positions

# Cancel ALL orders (manual)
# Via Alpaca dashboard: https://app.alpaca.markets/paper/dashboard/overview
```

## 🛡️ Safety Reminders

1. **Dit is PAPER TRADING** - Geen echt geld
2. **$1,000 limiet** - Maximaal verlies = $1,000 (fake money)
3. **Test eerst grondig** - Maandag eerst monitoren zonder auto-trading
4. **Manual review** - Check elke order voordat je submit

## ✅ Maandag Morning Checklist

1. [ ] Server status checken (curl http://localhost:8000/health)
2. [ ] Alpaca balance checken
3. [ ] Test order plaatsen ($1 test)
4. [ ] Monitor logs (tail -f /tmp/optifire.log)
5. [ ] Dashboard bekijken (http://185.181.8.39:8000)
6. [ ] Risk metrics checken


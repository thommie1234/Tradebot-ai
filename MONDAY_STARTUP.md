# 🚀 Maandag Markt Open - Startup Guide

## Overzicht van Nieuwe Features

### ✅ 1. Order Size Validation
**Wat doet het?**
- Checkt automatisch of je genoeg buying power hebt VOOR het plaatsen van een order
- Voorkomt dat je meer uitgeeft dan beschikbaar
- Geeft duidelijke foutmelding met beschikbaar bedrag

**Voorbeeld foutmelding:**
```
Insufficient buying power. Order cost: $450.00, Available: $250.00
```

**Geen actie nodig** - werkt automatisch!

---

### ✅ 2. Auto-Restart Monitor
**Wat doet het?**
- Checkt elke 30 seconden of de server nog draait
- Start server automatisch opnieuw als hij crasht
- Logt alle events naar `/tmp/optifire_monitor.log`

**Hoe te gebruiken:**
```bash
# Start monitoring
nohup /root/optifire/monitor.sh > /tmp/monitor.log 2>&1 &

# Check monitor logs
tail -f /tmp/optifire_monitor.log

# Stop monitoring
pkill -f monitor.sh
```

**Output:**
```
[2025-11-01 16:30:00] OptiFIRE Monitor started
[2025-11-01 16:30:05] Server started with PID: 12345
[2025-11-01 16:30:35] ✓ Server healthy
[2025-11-01 16:31:05] ✓ Server healthy
```

---

### ✅ 3. Database Backup
**Wat doet het?**
- Maakt automatisch backups van je database
- Houdt laatste 30 backups (1 maand)
- Kan handmatig of automatisch (cron)

**Setup (eenmalig):**
```bash
# Installeer daily backup om 2:00 AM
/root/optifire/setup_cron.sh
```

**Handmatig backup:**
```bash
# Maak nu een backup
/root/optifire/backup.sh

# Check backups
ls -lh /root/optifire/backups/
```

**Restore van backup:**
```bash
# Stop server eerst!
pkill -9 python3

# Restore
cp /root/optifire/backups/optifire_20251101_140000.db /root/optifire/data/optifire.db

# Start server opnieuw
nohup /root/optifire/monitor.sh > /tmp/monitor.log 2>&1 &
```

---

## 🎯 Maandag Morning Checklist

**Stap 1: Start Server (voor 9:30 AM ET)**
```bash
cd /root/optifire
pkill -9 python3  # Stop oude processen
nohup /root/optifire/monitor.sh > /tmp/monitor.log 2>&1 &
sleep 10
```

**Stap 2: Verify Server**
```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy",...}

curl http://localhost:8000/metrics/portfolio
# Expected: {"equity":1000.0,"cash":1000.0,...}
```

**Stap 3: Setup Backup (eenmalig)**
```bash
/root/optifire/setup_cron.sh
```

**Stap 4: Open Dashboard**
```
Browser: http://185.181.8.39:8000
```

**Stap 5: Test Order (klein bedrag!)**
```bash
# Via dashboard Orders tab:
Symbol: AAPL
Quantity: 1
Side: buy
Order Type: limit
Limit Price: 150.00  # Of huidige prijs - $5

# Expected: Order accepted (markt moet open zijn!)
# If market closed: "Cannot place market order: Market is closed"
```

---

## 📊 Monitoring Commands

```bash
# Server logs
tail -f /tmp/optifire.log

# Monitor logs
tail -f /tmp/optifire_monitor.log

# Backup logs
tail -f /tmp/optifire_backup.log

# Check portfolio
curl http://localhost:8000/metrics/portfolio | python3 -m json.tool

# Check positions
curl http://localhost:8000/metrics/positions | python3 -m json.tool

# List recent orders
curl http://localhost:8000/orders/ | python3 -m json.tool
```

---

## 🛡️ Safety Features Active

✅ **Paper Trading Only** - $1,000 fake money (ALPACA_PAPER=true)
✅ **Market Hours Check** - Geen market orders buiten trading hours
✅ **Buying Power Validation** - Kan niet meer uitgeven dan beschikbaar
✅ **Risk Limits** - Max 30% total exposure, 10% per symbol
✅ **Auto-Restart** - Server komt automatisch terug na crash
✅ **Daily Backups** - Database backup elke nacht om 2 AM

---

## 🚨 Als Iets Fout Gaat

**Server reageert niet:**
```bash
# Check processen
ps aux | grep python3

# Hard restart
pkill -9 python3
nohup /root/optifire/monitor.sh > /tmp/monitor.log 2>&1 &
```

**Orders werken niet:**
```bash
# Check of markt open is
curl http://localhost:8000/metrics/portfolio

# Als markt gesloten: gebruik limit orders ipv market orders
```

**Database corrupt:**
```bash
# Restore laatste backup
ls -lh /root/optifire/backups/  # Kies laatste backup
pkill -9 python3
cp /root/optifire/backups/optifire_YYYYMMDD_HHMMSS.db /root/optifire/data/optifire.db
nohup /root/optifire/monitor.sh > /tmp/monitor.log 2>&1 &
```

**All Hope Lost:**
```bash
# Nuclear option: stop alles
pkill -9 python3

# Check Alpaca dashboard manually
# https://app.alpaca.markets/paper/dashboard/overview

# Cancel all orders via Alpaca dashboard
```

---

## 📞 Contact Info

**Alpaca Dashboard:** https://app.alpaca.markets/paper/dashboard/overview
**Server Dashboard:** http://185.181.8.39:8000
**Server Logs:** `/tmp/optifire.log`
**Monitor Logs:** `/tmp/optifire_monitor.log`
**Backup Logs:** `/tmp/optifire_backup.log`

---

## ✅ Ready for Monday!

Alle kritische features zijn geïmplementeerd:
- ✅ Order size validation
- ✅ Auto-restart monitoring
- ✅ Database backups

**Next Steps:**
1. Maandag morning: volg de checklist hierboven
2. Start met monitoring (geen auto-trading!)
3. Test handmatig een paar orders
4. Check risk metrics regelmatig
5. Einde dag: review logs en performance

**Veel succes! 🚀**

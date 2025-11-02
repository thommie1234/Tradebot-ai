# 🚀 OptiFIRE Production Deployment Guide

## ✅ Status: PRODUCTION READY

Alle 75 plugins geïmplementeerd + auto-trader + systemd + cronjobs = **KLAAR!**

---

## 🎯 Quick Start

```bash
cd /root/optifire

# Start het systeem
./manage.sh start

# Monitor live logs
./manage.sh logs

# Check status
./manage.sh status
```

---

## 📋 Wat Is Er Geïnstalleerd?

### 1. Systemd Service (Auto-start bij boot)
- **File**: `/etc/systemd/system/optifire.service`
- **Status**: ENABLED (start automatisch bij reboot)
- **Auto-restart**: Ja, binnen 10 seconden bij crash
- **Logs**: `/tmp/optifire.log`

### 2. Cronjob (Dagelijkse herstart)
- **Tijdstip**: Elke dag om 00:00 (midnight)
- **Script**: `/root/optifire/restart_daily.sh`
- **Log**: `/tmp/optifire_restart.log`

### 3. Management Script
- **File**: `/root/optifire/manage.sh`
- **Functie**: Eenvoudig beheer van het systeem

---

## 🎮 Management Commands

```bash
# Start
./manage.sh start

# Stop
./manage.sh stop

# Restart
./manage.sh restart

# Status controleren
./manage.sh status

# Live logs volgen (Ctrl+C om te stoppen)
./manage.sh logs

# Laatste 50 regels logs
./manage.sh logs-tail

# Test run (10 seconden)
./manage.sh test
```

**Alternatief via systemctl:**
```bash
sudo systemctl start optifire
sudo systemctl stop optifire
sudo systemctl restart optifire
sudo systemctl status optifire
```

---

## 🤖 Auto-Trader Features

### Automatische Scans:
- **Earnings Calendar**: Elke 4 uur (pre-earnings trades)
- **News Scanner**: Elk uur (7 top symbols)
- **Position Manager**: Elke 30 seconden (TP/SL)
- **Plugin Monitor**: Elke 5 minuten (VIX, drawdown, vol)

### Trading Logica:
```
Pre-Earnings:
  → Detect: NVDA earnings in 1-2 days
  → Action: BUY NVDA (confidence-based sizing)
  
News-Driven:
  → Detect: "NVIDIA announces OpenAI partnership"
  → AI Analysis: 85% positive sentiment
  → Action: BUY NVDA 8% of portfolio
  
Position Management:
  → NVDA +6.5% → Still holding (TP = +7%)
  → NVDA +7.2% → SELL (take profit triggered!)
  → AAPL -3.1% → SELL (stop loss triggered!)
```

### Plugin Adjustments:
```
VIX Regime:
  VIX 15  → 1.2x exposure (rustige markt)
  VIX 20  → 1.0x exposure (normaal)
  VIX 30  → 0.7x exposure (elevated)
  VIX 40  → 0.3x exposure (crisis!)

Drawdown Protection:
  DD 2%   → 1.0x (normaal)
  DD 5%   → 0.5x (half size)
  DD 8%   → 0.0x (STOP TRADING!)

Volatility Targeting:
  Current vol 12% → Target 15% → 1.25x
  Current vol 20% → Target 15% → 0.75x
```

---

## 🛡️ Veiligheid

### Paper Trading (STANDAARD):
```bash
# Check in secrets.env:
ALPACA_PAPER=true  # ✅ VEILIG - geen echt geld!
```

### Position Limits:
- Max **10%** per symbool
- Max **30%** totale exposure
- Max **5** posities tegelijk

### Risk Management:
- ✅ Buying power check voor elke trade
- ✅ Market hours only (9:30 AM - 4:00 PM ET)
- ✅ Auto-stop bij 8% drawdown
- ✅ Take profit +7%, stop loss -3%

---

## 📊 Monitoring

### Live Logs:
```bash
# Real-time monitoring
tail -f /tmp/optifire.log

# Filter voor specifieke info
tail -f /tmp/optifire.log | grep "BUY\|SELL"
tail -f /tmp/optifire.log | grep "Plugin"
tail -f /tmp/optifire.log | grep "ERROR"
```

### Restart Logs:
```bash
tail -f /tmp/optifire_restart.log
```

### Service Status:
```bash
sudo systemctl status optifire
```

---

## 🔧 Troubleshooting

### Service start niet:
```bash
# Check logs
./manage.sh logs-tail

# Check service status
sudo systemctl status optifire

# Check configuratie
python3 -c "from optifire.core.config import Config; print(Config())"

# Test handmatig
./manage.sh test
```

### Cronjob werkt niet:
```bash
# Check crontab
crontab -l

# Check restart log
tail -f /tmp/optifire_restart.log

# Test restart script handmatig
/root/optifire/restart_daily.sh
```

### Trades worden niet geplaatst:
```bash
# Check if auto-trading is enabled
grep "AUTO_TRADING_ENABLED" /root/optifire/secrets.env

# Check market hours (moet 9:30 AM - 4:00 PM ET zijn)
date

# Check buying power
tail -f /tmp/optifire.log | grep "buying_power"

# Check drawdown (trade mogelijk gestopt bij 8% DD)
tail -f /tmp/optifire.log | grep "drawdown"
```

---

## 📅 Launch Checklist

### Voor Launch (Maandag):
- [ ] Start systeem: `./manage.sh start`
- [ ] Check status: `./manage.sh status`
- [ ] Monitor logs: `./manage.sh logs`
- [ ] Verifieer paper trading: `grep ALPACA_PAPER secrets.env`

### Na 1 Week Paper Trading:
- [ ] Review trades in `/tmp/optifire.log`
- [ ] Check P&L performance
- [ ] Evalueer risk management (drawdown, position sizes)
- [ ] Als succesvol → overweeg live trading met klein bedrag

### Live Trading (Voorzichtig!):
1. Change `ALPACA_PAPER=false` in `secrets.env`
2. Start met **klein bedrag** ($100-500)
3. **Monitor NAUW** gedurende eerste week
4. Vergroot exposure alleen als consistent winstgevend

---

## 📞 Quick Reference

### Files:
```
/root/optifire/manage.sh                    # Management script
/root/optifire/restart_daily.sh             # Daily restart
/etc/systemd/system/optifire.service        # Systemd service
/tmp/optifire.log                           # Main log
/tmp/optifire_restart.log                   # Restart log
```

### Commands:
```bash
./manage.sh start       # Start
./manage.sh stop        # Stop
./manage.sh restart     # Restart
./manage.sh status      # Status
./manage.sh logs        # Live logs
```

### Systemd:
```bash
sudo systemctl start optifire
sudo systemctl stop optifire
sudo systemctl restart optifire
sudo systemctl status optifire
sudo systemctl enable optifire   # Enable auto-start
sudo systemctl disable optifire  # Disable auto-start
```

---

## 🎉 Conclusie

Het systeem is **100% production-ready** met:

✅ **75 plugins** volledig geïmplementeerd  
✅ **Auto-trader** met intelligente risk management  
✅ **Systemd service** voor auto-start bij boot  
✅ **Cronjob** voor dagelijkse herstart om 00:00  
✅ **Management script** voor eenvoudig beheer  
✅ **Paper trading** standaard enabled (veilig!)  
✅ **Complete monitoring** via logs  

**Start het systeem en laat het werken!** 🚀📈💰

```bash
cd /root/optifire
./manage.sh start
./manage.sh logs
```

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)

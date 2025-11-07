# 🚀 OptiFIRE Laptop Migratie - Quick Start

## ⚡ Migreer in 3 Stappen

### 1️⃣ Op de Server (SSH)
```bash
cd /root/optifire && bash export_for_migration.sh
```

### 2️⃣ Op je Laptop (Terminal)

**Linux/macOS:**
```bash
# Download (vervang YOUR_SERVER_IP)
scp root@YOUR_SERVER_IP:/root/optifire/optifire_migration.tar.gz ~/Downloads/

# Installeer
cd ~ && tar -xzf ~/Downloads/optifire_migration.tar.gz && cd optifire_export && bash install_on_laptop.sh

# Auto-start (optioneel)
bash setup_laptop_service.sh
```

**Windows (WSL2):**
```bash
# Download (vervang YOUR_SERVER_IP)
cd /mnt/c/Users/JOUW_NAAM/Downloads
scp root@YOUR_SERVER_IP:/root/optifire/optifire_migration.tar.gz .

# Installeer
cd ~ && tar -xzf /mnt/c/Users/JOUW_NAAM/Downloads/optifire_migration.tar.gz && cd optifire_export && bash install_on_laptop.sh
```

### 3️⃣ Open Dashboard
```
http://localhost:8000
```

**Login:**
- Username: `admin`
- Password: (zie `secrets.env` voor `ADMIN_PASS`)

---

## ✅ Checklist

- [ ] Export van server gelukt
- [ ] Archive gedownload naar laptop
- [ ] Python 3.11+ geïnstalleerd
- [ ] `install_on_laptop.sh` succesvol uitgevoerd
- [ ] Dashboard opent op http://localhost:8000
- [ ] Alpaca broker is verbonden (check dashboard)
- [ ] Auto-trading staat aan (zie logs)
- [ ] Laptop sleep uitgeschakeld
- [ ] Auto-start geconfigureerd (optioneel)

---

## 🔧 Handige Commando's

**Start bot:**
```bash
cd ~/optifire && bash start.sh
```

**Stop bot:**
```bash
pkill -f "python main.py"
```

**Restart bot:**
```bash
cd ~/optifire && bash restart.sh
```

**Logs bekijken:**
```bash
# Live logs
tail -f ~/optifire/logs/optifire.log

# Of systemd (Linux)
journalctl --user -u optifire -f
```

**Status checken (Linux):**
```bash
systemctl --user status optifire
```

---

## 💰 Kostenbesparing

**Vóór:** ~€5-20/maand (server)
**Na:** ~€3/maand (laptop stroom)

**Besparing: €50-200/jaar** 🎉

---

## ⚠️ Troubleshooting

**Bot start niet:**
```bash
cd ~/optifire
source venv/bin/activate
python main.py
# Kijk naar error messages
```

**Alpaca verbinding mislukt:**
```bash
# Check API keys
cat ~/optifire/secrets.env | grep ALPACA
```

**Port 8000 bezet:**
```bash
# Wijzig poort
nano ~/optifire/config.yaml
# Wijzig port naar 8001
```

---

## 📚 Meer Info

Zie **MIGRATION_GUIDE.md** voor:
- Gedetailleerde stappen
- Windows Task Scheduler setup
- Sleep preventie configuratie
- Veiligheid & backups
- Troubleshooting

---

## 🆘 Support

Bij problemen:
1. Check logs: `tail -f ~/optifire/logs/optifire.log`
2. Test broker: `cd ~/optifire && python -c "from optifire.exec.broker_alpaca import AlpacaBroker; import asyncio; asyncio.run(AlpacaBroker(paper=True).get_account())"`
3. Zie MIGRATION_GUIDE.md

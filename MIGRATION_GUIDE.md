# OptiFIRE Migratie naar Laptop

## Overzicht
Deze guide helpt je om OptiFIRE van de server naar je laptop te migreren voor kostenbesparingen.

## ⚡ Snelle Migratie (Copy-Paste)

### Optie A: Complete Migratie in 3 Commando's

**Op de SERVER (SSH):**
```bash
cd /root/optifire && bash export_for_migration.sh
```

**Op je LAPTOP (Terminal):**
```bash
# Download van server (vervang YOUR_SERVER_IP met je server IP)
scp root@YOUR_SERVER_IP:/root/optifire/optifire_migration.tar.gz ~/Downloads/

# Installeer
cd ~ && tar -xzf ~/Downloads/optifire_migration.tar.gz && cd optifire_export && bash install_on_laptop.sh

# Setup auto-start (optioneel)
bash setup_laptop_service.sh
```

**Open Dashboard:**
```
http://localhost:8000
```

✅ **Klaar! Je bot draait nu lokaal op je laptop.**

---

### Voor Windows (WSL2) Gebruikers:

**Installeer WSL2 (eenmalig):**
```powershell
# In PowerShell als Administrator:
wsl --install
# Herstart computer
```

**Migratie (in WSL2 terminal):**
```bash
# Download (vervang YOUR_SERVER_IP)
cd /mnt/c/Users/JOUW_NAAM/Downloads
scp root@YOUR_SERVER_IP:/root/optifire/optifire_migration.tar.gz .

# Installeer
cd ~ && tar -xzf /mnt/c/Users/JOUW_NAAM/Downloads/optifire_migration.tar.gz && cd optifire_export && bash install_on_laptop.sh

# Setup auto-start via Task Scheduler (zie Stap 3 hieronder)
```

---

### Optie B: Stapsgewijze Migratie

Gebruik onderstaande gedetailleerde stappen als je meer controle wilt.

---

## Vereisten Laptop
- **OS**: Ubuntu 22.04+ / Windows 10+ (met WSL2) / macOS 12+
- **Python**: 3.11 of hoger
- **RAM**: Minimaal 4GB vrij
- **Disk**: Minimaal 2GB vrij
- **Internet**: Stabiele verbinding (voor market data)

## Stap 1: Export van Server

Op de **server**, voer uit:
```bash
cd /root/optifire
bash export_for_migration.sh
```

Dit maakt een bestand `optifire_migration.tar.gz` met:
- ✓ Alle code bestanden
- ✓ Database (optifire.db) met historische data
- ✓ Configuratie (config.yaml, features.yaml)
- ✓ Dependencies (requirements.txt)
- ✓ API keys (secrets.env) - **veilig bewaren!**

**Download dit bestand naar je laptop:**
```bash
# Van je laptop:
scp root@YOUR_SERVER_IP:/root/optifire/optifire_migration.tar.gz ~/Downloads/
```

## Stap 2: Installatie op Laptop

### Voor Ubuntu/Linux:
```bash
# Pak het archief uit
cd ~/
tar -xzf ~/Downloads/optifire_migration.tar.gz
cd optifire

# Installeer dependencies
bash install_on_laptop.sh
```

### Voor Windows (WSL2):
```bash
# Open WSL2 terminal
wsl

# Pak het archief uit
cd ~/
tar -xzf /mnt/c/Users/JOUW_NAAM/Downloads/optifire_migration.tar.gz
cd optifire

# Installeer dependencies
bash install_on_laptop.sh
```

### Voor macOS:
```bash
# Pak het archief uit
cd ~/
tar -xzf ~/Downloads/optifire_migration.tar.gz
cd optifire

# Installeer Homebrew (als nog niet geïnstalleerd)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Installeer Python 3.11
brew install python@3.11

# Installeer dependencies
bash install_on_laptop.sh
```

## Stap 3: Auto-Start Configuratie

### Ubuntu/Linux (Systemd):
```bash
# Setup systemd service voor auto-start
bash setup_laptop_service.sh

# Check status
systemctl --user status optifire
```

### Windows (Task Scheduler):
```powershell
# Open Task Scheduler
# Import: optifire_windows_task.xml
# Of handmatig aanmaken:
# - Trigger: At startup
# - Action: wsl bash -c "cd ~/optifire && source venv/bin/activate && python main.py"
```

### macOS (LaunchAgent):
```bash
# Setup LaunchAgent voor auto-start
bash setup_laptop_service.sh
```

## Stap 4: Verificatie

```bash
# Test de installatie
cd ~/optifire
source venv/bin/activate
python main.py
```

Open browser: http://localhost:8000

Je zou moeten zien:
- ✓ Dashboard met portfolio waarde
- ✓ Auto-trader status (earnings scanner, news scanner)
- ✓ Historische trades (van database)

## Stap 5: Laptop Instellingen voor 24/7 Trading

### Ubuntu/Linux:
```bash
# Voorkom slaapstand
gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-ac-timeout 0
gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-battery-timeout 0

# Of via GUI: Settings → Power → Never sleep
```

### Windows:
```
Settings → System → Power & Sleep
- Screen: Never
- Sleep: Never
```

### macOS:
```bash
# Voorkom slaapstand (met charger)
sudo pmset -c sleep 0
sudo pmset -c displaysleep 10  # Screen mag wel dimmen

# Of via GUI: System Preferences → Energy Saver → Never sleep
```

## Monitoring & Onderhoud

### Logs bekijken:
```bash
# Live logs
tail -f ~/optifire/logs/optifire.log

# Of via journalctl (Linux)
journalctl --user -u optifire -f
```

### Heropstarten:
```bash
# Systemd (Linux)
systemctl --user restart optifire

# Handmatig
cd ~/optifire
bash restart.sh
```

### Backups:
```bash
# Database backup (automatisch dagelijks)
ls -lh ~/optifire/data/backups/

# Handmatige backup
cd ~/optifire
bash backup.sh
```

## Kostenbesparing

**Voor:**
- Server: ~$5-20/maand (afhankelijk van provider)

**Na:**
- Laptop: €0/maand (alleen stroom: ~€3/maand bij 24/7)

**Totale besparing: ~€50-200/jaar** 🎉

## Troubleshooting

### Auto-trader start niet:
```bash
# Check logs
journalctl --user -u optifire | grep -i error

# Check secrets.env
cat ~/optifire/secrets.env | grep ALPACA_API_KEY
```

### Database fouten:
```bash
# Restore van backup
cd ~/optifire/data
cp backups/optifire_backup_LATEST.db optifire.db
```

### Port 8000 al in gebruik:
```bash
# Wijzig poort in config.yaml
vim ~/optifire/config.yaml
# Wijzig port: 8001
```

## Veiligheid

⚠️ **Belangrijke beveiligingstips:**
1. **secrets.env**: Deel dit bestand NOOIT online
2. **Firewall**: Firewall actief houden
3. **Updates**: Houd laptop OS up-to-date
4. **VPN**: Overweeg VPN voor extra veiligheid
5. **Backups**: Dagelijkse backups (automatisch)

## Support

Bij problemen:
1. Check logs: `tail -f ~/optifire/logs/optifire.log`
2. Test broker: `cd ~/optifire && python -c "from optifire.exec.broker_alpaca import AlpacaBroker; import asyncio; asyncio.run(AlpacaBroker(paper=True).get_account())"`
3. Herstart: `systemctl --user restart optifire`

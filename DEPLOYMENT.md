# OptiFIRE Deployment Guide

## VPS Setup (2 CPU / 1 GB RAM / 20 GB Disk)

### 1. Prepare VPS (Ubuntu 22.04)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt install python3.11 python3.11-venv python3.11-dev -y

# Install build tools
sudo apt install build-essential git curl -y

# Create user
sudo useradd -m -s /bin/bash optifire
sudo usermod -aG sudo optifire
sudo su - optifire
```

### 2. Deploy OptiFIRE

```bash
# Clone repository
cd ~
git clone <your-repo> optifire
cd optifire

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create data directories
mkdir -p data logs
```

### 3. Configure

```bash
# Set up secrets
cp configs/secrets.env.template configs/secrets.env
nano configs/secrets.env
# Fill in your API keys

# Review config
nano configs/config.yaml
# Ensure paper_trading: true for testing

# Review feature flags
nano configs/features.yaml
# Keep defaults (only 8 plugins enabled)
```

### 4. Test Run

```bash
# Activate venv
source venv/bin/activate

# Start server
python -m optifire.services.runner

# In another terminal, test health
curl http://localhost:8000/health
```

Expected output:
```json
{"status": "healthy", "cpu_percent": 10-20, "memory_mb": 300-500}
```

### 5. Production Setup with systemd

Create service file:
```bash
sudo nano /etc/systemd/system/optifire.service
```

Content:
```ini
[Unit]
Description=OptiFIRE Trading System
After=network.target

[Service]
Type=simple
User=optifire
WorkingDirectory=/home/optifire/optifire
Environment="PATH=/home/optifire/optifire/venv/bin"
EnvironmentFile=/home/optifire/optifire/configs/secrets.env
ExecStart=/home/optifire/optifire/venv/bin/python -m optifire.services.runner
Restart=on-failure
RestartSec=10
StandardOutput=append:/home/optifire/optifire/logs/optifire.log
StandardError=append:/home/optifire/optifire/logs/optifire_error.log

# Resource limits
MemoryMax=950M
CPUQuota=180%

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable optifire
sudo systemctl start optifire
sudo systemctl status optifire
```

### 6. Nginx Reverse Proxy (Optional)

```bash
sudo apt install nginx -y
sudo nano /etc/nginx/sites-available/optifire
```

Content:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Enable:
```bash
sudo ln -s /etc/nginx/sites-available/optifire /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 7. SSL with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

### 8. Monitoring

```bash
# View logs
journalctl -u optifire -f

# Check resource usage
systemctl status optifire

# Monitor memory
watch -n 5 'ps aux | grep optifire'

# Check disk
df -h
du -sh ~/optifire/data
```

### 9. Backup Script

```bash
nano ~/backup_optifire.sh
```

Content:
```bash
#!/bin/bash
BACKUP_DIR=~/optifire_backups
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
cd ~/optifire

# Backup data and config
tar -czf $BACKUP_DIR/optifire_$DATE.tar.gz \
    data/ \
    configs/config.yaml \
    configs/features.yaml \
    logs/

# Keep only last 7 backups
ls -t $BACKUP_DIR/optifire_*.tar.gz | tail -n +8 | xargs rm -f

echo "Backup completed: optifire_$DATE.tar.gz"
```

Make executable and add to cron:
```bash
chmod +x ~/backup_optifire.sh
crontab -e
# Add: 0 2 * * * /home/optifire/backup_optifire.sh
```

### 10. Monitoring Alerts

```bash
nano ~/check_optifire.sh
```

Content:
```bash
#!/bin/bash
WEBHOOK_URL="YOUR_DISCORD_WEBHOOK_URL"

# Check if service is running
if ! systemctl is-active --quiet optifire; then
    curl -X POST -H 'Content-Type: application/json' \
        -d '{"content":"⚠️ OptiFIRE service is DOWN!"}' \
        $WEBHOOK_URL
fi

# Check memory usage
MEM=$(ps aux | grep 'optifire.services.runner' | grep -v grep | awk '{print $6}')
if [ "$MEM" -gt 900000 ]; then
    curl -X POST -H 'Content-Type: application/json' \
        -d "{\"content\":\"⚠️ OptiFIRE memory usage HIGH: ${MEM}KB\"}" \
        $WEBHOOK_URL
fi
```

Make executable and add to cron:
```bash
chmod +x ~/check_optifire.sh
crontab -e
# Add: */5 * * * * /home/optifire/check_optifire.sh
```

## Performance Tuning

### Reduce Memory Usage

1. Disable unused plugins in `configs/features.yaml`
2. Reduce cache sizes in `configs/config.yaml`
3. Use ONNX quantized models instead of full LightGBM
4. Clear old data: `rm data/parquet/old_*.parquet`

### Reduce CPU Usage

1. Increase plugin schedules (less frequent runs)
2. Disable real-time features (use @close instead of interval_1m)
3. Reduce concurrent OpenAI calls to 1
4. Use DuckDB for heavy analytics (offline)

## Troubleshooting

### Service Won't Start

```bash
# Check logs
journalctl -u optifire -n 50

# Check permissions
ls -la /home/optifire/optifire/

# Test manually
cd ~/optifire
source venv/bin/activate
python -m optifire.services.runner
```

### High Memory

```bash
# Identify culprit
sudo systemctl stop optifire
# Enable plugins one by one
# Test: curl http://localhost:8000/metrics/portfolio
```

### Database Locked

```bash
# Stop service
sudo systemctl stop optifire

# Check for stale locks
rm data/optifire.db-shm data/optifire.db-wal

# Restart
sudo systemctl start optifire
```

## Security Hardening

1. **Firewall**:
```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

2. **SSH Keys Only**:
```bash
sudo nano /etc/ssh/sshd_config
# Set: PasswordAuthentication no
sudo systemctl restart sshd
```

3. **Fail2Ban**:
```bash
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
```

4. **Keep Updated**:
```bash
sudo apt update && sudo apt upgrade -y
```

## Going Live Checklist

- [ ] Paper trading works for 2+ weeks
- [ ] Sharpe ratio > 1.0 in paper mode
- [ ] Max drawdown < 10% in paper mode
- [ ] No memory spikes > 900 MB
- [ ] All secrets configured
- [ ] TOTP 2FA enabled
- [ ] SSL configured
- [ ] Monitoring alerts tested
- [ ] Backups working
- [ ] Kill switch tested
- [ ] Start with 10% of intended capital

**Remember: Start small, scale gradually!**

# 🌍 OptiFIRE Remote Access - Stap voor Stap

## ✅ Configuratie Voltooid!

Je tradebot is nu geconfigureerd voor remote access via je lokale netwerk.

### 📊 Je Netwerk Configuratie

```
Lokaal IP Adres:    192.168.1.55
Publiek IP Adres:   89.99.148.189
Dashboard URL:      http://192.168.1.55:8000
Port:               8000
```

---

## 🔥 STAP 1: Firewall Configureren

De bot draait op poort 8000. Je moet deze poort openen voor je lokale netwerk.

**Optie A: UFW Firewall (Ubuntu/Debian)**

```bash
# Open poort 8000 voor lokaal netwerk
sudo ufw allow from 192.168.1.0/24 to any port 8000

# Check firewall status
sudo ufw status

# Als firewall uit staat (inactive), hoef je niets te doen!
```

**Optie B: Firewalld (Fedora/RHEL)**

```bash
# Open poort 8000
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

**Optie C: Geen Firewall Actief**

Als `sudo ufw status` zegt "Status: inactive", dan hoef je niets te doen! De poort is al toegankelijk.

---

## 📱 STAP 2: Vanaf Je Telefoon/Tablet Verbinden

### A. Zorg dat je op hetzelfde WiFi netwerk zit

Je telefoon/tablet moet verbonden zijn met **hetzelfde WiFi netwerk** als je laptop!

### B. Open Browser op Je Telefoon

Open Safari (iPhone) of Chrome (Android) en ga naar:

```
http://192.168.1.55:8000
```

### C. Login met Je Credentials

```
Username: admin
Password: BTryuXxNV2BKEFsOjNO9Gw
TOTP Code: (leeg laten, tenzij je 2FA hebt geactiveerd)
```

---

## 💻 STAP 3: Vanaf Andere Laptop Verbinden

### Zelfde WiFi Netwerk:

```
http://192.168.1.55:8000
```

### Andere Locatie (Buitenshuis):

Je hebt 3 opties:

**Optie 1: VPN naar Je Thuisnetwerk**

Als je een VPN naar thuis hebt (zoals Tailscale, WireGuard, of je router's VPN):
1. Verbind met je thuis VPN
2. Ga naar `http://192.168.1.55:8000`

**Optie 2: Port Forwarding (NIET AANBEVOLEN voor security)**

Op je router:
1. Forward poort 8000 → 192.168.1.55:8000
2. Ga naar `http://89.99.148.189:8000`

⚠️ **WAARSCHUWING**: Dit maakt je bot toegankelijk voor iedereen op internet!
- Gebruik alleen als je weet wat je doet
- Activeer IP whitelist in secrets.env:
  ```
  ENABLE_IP_WHITELIST=true
  IP_WHITELIST=127.0.0.1,JE_REMOTE_IP
  ```

**Optie 3: SSH Tunnel (VEILIGSTE OPTIE)**

Op je remote laptop:
```bash
# Verbind via SSH tunnel
ssh -L 8000:localhost:8000 thomas@89.99.148.189

# Dan open in browser:
http://localhost:8000
```

Dit vereist dat SSH (poort 22) toegankelijk is vanaf buiten.

---

## 🧪 STAP 4: Test Je Verbinding

### Test 1: Health Check

```bash
# Vanaf je telefoon/andere device in hetzelfde netwerk:
curl http://192.168.1.55:8000/health

# Verwachte output:
{
  "status": "healthy",
  "cpu_percent": 0.0,
  "memory_mb": 140.07,
  "num_threads": 14
}
```

### Test 2: Login Test

```bash
curl -X POST http://192.168.1.55:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "BTryuXxNV2BKEFsOjNO9Gw",
    "totp_code": ""
  }'

# Verwachte output:
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

### Test 3: Portfolio Ophalen

```bash
# Gebruik de token uit vorige stap
TOKEN="eyJhbGc..."

curl http://192.168.1.55:8000/metrics/portfolio \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🔒 Security Instellingen

### Huidige Configuratie:

```bash
✅ Rate Limiting:        100 requests/minuut per IP
✅ CORS Origins:         localhost + 192.168.1.55
✅ IP Whitelist:         UITGESCHAKELD (iedereen in lokaal netwerk)
✅ Authentication:       VERPLICHT voor orders/config
✅ JWT Expiry:           24 uur
```

### IP Whitelist Activeren (Optioneel)

Als je alleen specifieke devices wilt toestaan:

1. **Vind IP van je telefoon/tablet:**
   - iPhone: Settings → WiFi → (i) → IP Address
   - Android: Settings → WiFi → Advanced → IP Address

2. **Update secrets.env:**
   ```bash
   nano ~/Tradebot-ai/secrets.env

   # Wijzig:
   ENABLE_IP_WHITELIST=true
   IP_WHITELIST=127.0.0.1,::1,192.168.1.55,192.168.1.XXX
   #                                        ^^^^^^^^^^^^^^
   #                                        Je telefoon IP
   ```

3. **Herstart bot:**
   ```bash
   pkill -f "python.*main.py"
   cd ~/Tradebot-ai
   source venv/bin/activate
   python3 main.py > optifire.log 2>&1 &
   ```

---

## 🆘 Troubleshooting

### Kan Niet Verbinden van Telefoon

**Check 1: Zelfde WiFi?**
```
Laptop en telefoon moeten op HETZELFDE WiFi netwerk zitten!
```

**Check 2: Firewall?**
```bash
# Check of firewall poort blokkeert
sudo ufw status

# Als actief, voeg regel toe:
sudo ufw allow from 192.168.1.0/24 to any port 8000
```

**Check 3: Bot Draait?**
```bash
# Check of bot actief is
curl http://localhost:8000/health

# Check logs
tail -f ~/Tradebot-ai/optifire.log
```

**Check 4: Juiste IP?**
```bash
# Controleer of IP nog steeds 192.168.1.55 is
hostname -I
```

### Connection Refused Error

```bash
# Check of bot luistert op alle interfaces
ss -tlnp | grep :8000

# Verwacht: 0.0.0.0:8000 (niet 127.0.0.1:8000!)
```

Als het 127.0.0.1:8000 toont, dan moet je main.py aanpassen om op 0.0.0.0 te luisteren (al geconfigureerd).

### "Not authenticated" Error

Je moet eerst inloggen en een token krijgen:

```bash
# 1. Login
curl -X POST http://192.168.1.55:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"BTryuXxNV2BKEFsOjNO9Gw","totp_code":""}'

# 2. Kopieer de access_token uit de response

# 3. Gebruik in volgende requests:
curl http://192.168.1.55:8000/orders/submit \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL","qty":1,"side":"buy"}'
```

### Rate Limit Exceeded

Je hebt 100 requests/minuut gedaan. Wacht 1 minuut of verhoog het limiet:

```python
# In main.py, regel 219:
app.add_middleware(RateLimitMiddleware, requests_per_minute=200)  # Verhoog naar 200
```

---

## 📱 Mobile App Integratie

Voor een betere mobiele ervaring kun je een app bouwen die met de API praat:

**React Native / Flutter App:**
```javascript
// Login
const login = async () => {
  const response = await fetch('http://192.168.1.55:8000/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username: 'admin',
      password: 'BTryuXxNV2BKEFsOjNO9Gw',
      totp_code: ''
    })
  });
  const data = await response.json();
  return data.access_token;
};

// Get Portfolio
const getPortfolio = async (token) => {
  const response = await fetch('http://192.168.1.55:8000/metrics/portfolio', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return await response.json();
};
```

**iOS Shortcuts:**

Je kunt een iOS Shortcut maken om snel orders te plaatsen of je portfolio te checken!

---

## 🎯 Quick Commands

```bash
# Bot starten
cd ~/Tradebot-ai && source venv/bin/activate && python3 main.py > optifire.log 2>&1 &

# Bot stoppen
pkill -f "python.*main.py"

# Bot herstarten
pkill -f "python.*main.py" && sleep 2 && cd ~/Tradebot-ai && source venv/bin/activate && python3 main.py > optifire.log 2>&1 &

# Logs bekijken
tail -f ~/Tradebot-ai/optifire.log

# Health check
curl http://192.168.1.55:8000/health

# Login
curl -X POST http://192.168.1.55:8000/auth/login -H "Content-Type: application/json" -d '{"username":"admin","password":"BTryuXxNV2BKEFsOjNO9Gw","totp_code":""}'
```

---

## ✅ Checklist voor Eerste Keer Remote Access

- [ ] Bot draait: `curl http://localhost:8000/health`
- [ ] Firewall geconfigureerd (indien actief)
- [ ] Telefoon op zelfde WiFi als laptop
- [ ] Dashboard open op: `http://192.168.1.55:8000`
- [ ] Ingelogd met admin credentials
- [ ] Portfolio zichtbaar
- [ ] Test order geplaatst (kleine hoeveelheid!)

---

**Veel succes met remote trading! 📈**

Voor vragen, check de logs: `tail -f ~/Tradebot-ai/optifire.log`

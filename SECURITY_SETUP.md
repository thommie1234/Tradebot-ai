# 🔒 OptiFIRE Security Setup

## Security Verbeteringen Geïmplementeerd

### ✅ Wat is er Beveiligd?

1. **File Permissions**
   - `secrets.env` is nu alleen leesbaar voor jouw account (600)
   - Niemand anders kan je API keys zien

2. **Sterke Authenticatie**
   - JWT Secret: 64 karakters (cryptografisch veilig)
   - Admin Wachtwoord: Automatisch gegenereerd, 22 karakters
   - Token verloopt na 24 uur

3. **Endpoint Beveiliging**
   - ✅ Orders plaatsen: BEVEILIGD met authenticatie
   - ✅ Orders annuleren: BEVEILIGD met authenticatie
   - ✅ Config wijzigen: BEVEILIGD met authenticatie
   - ✅ Plugins uitvoeren: BEVEILIGD met authenticatie
   - ✅ Flags toggle: BEVEILIGD met authenticatie

4. **CORS Beperking**
   - Alleen toegestane origins kunnen requests maken
   - Standaard: localhost:8000, localhost:3000
   - Configureerbaar via `ALLOWED_ORIGINS` in secrets.env

5. **Rate Limiting**
   - Maximum 100 requests per minuut per IP adres
   - Voorkomt brute force en API misbruik

6. **IP Whitelist (Optioneel)**
   - Kan geactiveerd worden voor extra beveiliging
   - Alleen specifieke IP adressen krijgen toegang

---

## 🔑 Inloggen

### Je Credentials

```
Username: admin
Password: BTryuXxNV2BKEFsOjNO9Gw
```

**⚠️ BELANGRIJK:** Bewaar dit wachtwoord veilig! Het staat in `/home/thomas/Tradebot-ai/secrets.env`

### Login via API

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "BTryuXxNV2BKEFsOjNO9Gw",
    "totp_code": ""
  }'
```

Response:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

### Authenticated Request Maken

```bash
# Bewaar je token
TOKEN="eyJhbGc..."

# Gebruik token voor requests
curl -X GET http://localhost:8000/metrics/portfolio \
  -H "Authorization: Bearer $TOKEN"

# Order plaatsen (nu beveiligd!)
curl -X POST http://localhost:8000/orders/submit \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "qty": 1,
    "side": "buy",
    "order_type": "market"
  }'
```

---

## 🌍 Van Buiten Inloggen (Remote Access)

### Optie 1: SSH Tunnel (Meest Veilig)

```bash
# Op je remote machine (bijv. telefoon/andere laptop):
ssh -L 8000:localhost:8000 thomas@JE_LAPTOP_IP

# Dan open in browser:
http://localhost:8000
```

**Voordelen:**
- ✅ Versleuteld via SSH
- ✅ Geen extra configuratie nodig
- ✅ Werkt overal

### Optie 2: Direct Access (Vereist IP Whitelist)

1. **Activeer IP Whitelist:**

Bewerk `secrets.env`:
```bash
# Security
ALLOWED_ORIGINS=http://localhost:8000,http://JE_LAPTOP_IP:8000
ENABLE_IP_WHITELIST=true
IP_WHITELIST=127.0.0.1,::1,JE_REMOTE_IP
```

2. **Vind je Remote IP:**
```bash
# Op je remote machine:
curl ifconfig.me
```

3. **Herstart OptiFIRE:**
```bash
pkill -f "python.*main.py"
cd ~/Tradebot-ai
source venv/bin/activate
python3 main.py > optifire.log 2>&1 &
```

4. **Open in browser:**
```
http://JE_LAPTOP_IP:8000
```

### Optie 3: Cloudflare Tunnel (Meest Flexibel)

Voor toegang vanaf overal zonder IP whitelist:

```bash
# Installeer Cloudflare Tunnel
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# Login
cloudflared tunnel login

# Maak tunnel
cloudflared tunnel create optifire

# Start tunnel
cloudflared tunnel --url http://localhost:8000
```

Je krijgt een URL zoals: `https://xxx-xxx.trycloudflare.com`

---

## 🔐 Extra Beveiliging (Optioneel)

### 2FA Activeren (TOTP)

1. **Genereer TOTP Secret:**
```bash
python3 -c "import pyotp; print('TOTP_SECRET=' + pyotp.random_base32())"
```

2. **Voeg toe aan secrets.env:**
```
TOTP_SECRET=JBSWY3DPEHPK3PXP
```

3. **Scan QR code in authenticator app:**
```bash
python3 -c "
import pyotp
import qrcode
secret = 'JBSWY3DPEHPK3PXP'
uri = pyotp.totp.TOTP(secret).provisioning_uri(
    name='admin@optifire',
    issuer_name='OptiFIRE'
)
qrcode.make(uri).save('totp_qr.png')
print('QR code saved to totp_qr.png')
"
```

4. **Login met TOTP:**
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "BTryuXxNV2BKEFsOjNO9Gw",
    "totp_code": "123456"
  }'
```

### HTTPS Setup (Voor Productie)

Als je de bot op een server wilt draaien met HTTPS:

```bash
# Installeer certbot
sudo apt install certbot

# Verkrijg SSL certificaat
sudo certbot certonly --standalone -d jouw-domein.com

# Update config om HTTPS te gebruiken
# In main.py wijzig uvicorn.run() naar:
uvicorn.run(
    app,
    host="0.0.0.0",
    port=443,
    ssl_keyfile="/etc/letsencrypt/live/jouw-domein.com/privkey.pem",
    ssl_certfile="/etc/letsencrypt/live/jouw-domein.com/fullchain.pem",
)
```

---

## 📊 Security Checklist

Voor je van buiten inlogt, check:

- [ ] Secrets.env permissions zijn 600 (`ls -la secrets.env`)
- [ ] Sterk wachtwoord is ingesteld
- [ ] CORS origins zijn correct geconfigureerd
- [ ] Rate limiting is actief (100 req/min)
- [ ] IP whitelist ingesteld (indien gewenst)
- [ ] TOTP/2FA geactiveerd (optioneel maar aanbevolen)
- [ ] HTTPS actief (voor productie)
- [ ] Firewall regels correct ingesteld
- [ ] Alpaca keys zijn voor PAPER trading (niet live!)

---

## 🆘 Troubleshooting

### "Not authenticated" Error

- Check of je token geldig is
- Token verloopt na 24 uur - log opnieuw in
- Gebruik correct header: `Authorization: Bearer TOKEN`

### "Rate limit exceeded"

- Wacht 1 minuut
- Te veel requests van hetzelfde IP
- Rate limit verhogen in main.py (requests_per_minute parameter)

### "Access denied: IP not whitelisted"

- Controleer IP_WHITELIST in secrets.env
- Voeg je huidige IP toe
- Of schakel IP whitelist uit: `ENABLE_IP_WHITELIST=false`

### Kan niet inloggen

- Check of wachtwoord correct is in secrets.env
- Check of bot draait: `ps aux | grep python.*main.py`
- Check logs: `tail -f optifire.log`

---

## 🔒 Security Best Practices

1. **Wijzig wachtwoord regelmatig** (elke 3 maanden)
2. **Gebruik HTTPS** in productie
3. **Activeer 2FA** voor extra beveiliging
4. **Monitor logs** voor verdachte activiteit
5. **Beperk IP whitelist** tot bekende IPs
6. **Gebruik SSH tunnel** voor remote access
7. **Backup secrets.env** veilig
8. **Test alleen met PAPER trading** account

---

**Vragen?** Check de logs: `tail -f optifire.log`

**Versie:** Security Update 1.0 - November 2024

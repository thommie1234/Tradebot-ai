# Short Selling Guide

## 🎯 Overzicht

De OptiFIRE trading bot ondersteunt nu **volledig geautomatiseerd short selling** naast long posities. De bot kan automatisch besluiten om short te gaan op basis van:

- 📰 **Negatief nieuws** (bijv. rechtszaken, negatieve earnings, regulatory issues)
- 📉 **Pre-earnings bearish sentiment** (verwachte earnings teleurstelling)
- 📊 **Cross-asset signalen** (market stress indicators)

## 🔧 Hoe het werkt

### Signal Types

De bot ondersteunt twee signaal types:

1. **BUY** - Opent long positie (koopt aandelen)
2. **SHORT** - Opent short positie (verkoopt aandelen die je niet bezit)

```python
# Long signal
long_signal = Signal(
    symbol="NVDA",
    action="BUY",
    confidence=0.80,
    reason="Partnership with OpenAI announced"
)

# Short signal
short_signal = Signal(
    symbol="TSLA",
    action="SHORT",
    confidence=0.75,
    reason="Regulatory investigation announced"
)
```

### P&L Berekening

De bot berekent winst/verlies correct voor beide posities:

**LONG posities:**
- Prijs stijgt → winst ✅
- Prijs daalt → verlies ❌
- Formule: `(huidige_prijs - entry_prijs) / entry_prijs`

**SHORT posities:**
- Prijs daalt → winst ✅
- Prijs stijgt → verlies ❌
- Formule: `(entry_prijs - huidige_prijs) / entry_prijs`

### Automatische Exit

De bot sluit posities automatisch bij:

- **Take Profit**: +7% winst (standaard)
- **Stop Loss**: -3% verlies (standaard)

Dit werkt correct voor **zowel long als short** posities.

### Order Logica

**Opening posities:**
- BUY signal → `buy` order → opent LONG
- SHORT signal → `sell` order → opent SHORT

**Closing posities:**
- LONG sluiten → `sell` order
- SHORT sluiten → `buy` order (cover)

## 📊 Voorbeelden

### Voorbeeld 1: Short op slecht nieuws

```
📰 NEWS SCANNER detecteert:
"TSLA faces SEC investigation into Autopilot claims"

AI Analysis:
- Action: SHORT
- Confidence: 0.78
- Reason: Major regulatory risk

Bot Action:
→ Opens SHORT position: 50 shares TSLA @ $250
→ Take profit: $232.50 (7% down)
→ Stop loss: $257.50 (3% up)

Scenario A - Prijs daalt naar $230:
✅ Take profit triggered: +8.0% profit ($1,000)

Scenario B - Prijs stijgt naar $260:
❌ Stop loss triggered: -4.0% loss ($500)
```

### Voorbeeld 2: Pre-earnings short

```
📅 EARNINGS CALENDAR:
Netflix earnings in 2 days

AI Analysis:
- Action: SHORT
- Confidence: 0.65
- Reason: Weak subscriber growth signals, competitors gaining

Bot Action:
→ Opens SHORT position @ $450
→ Waits for earnings...
→ Earnings miss → price drops to $410
→ Take profit at +8.9% ($1,800 profit)
```

## 🎛️ Configuratie

### Position Sizing

Shorts gebruiken **dezelfde risico management** als longs:

```python
# Base size
base_size = 10% van portfolio (standaard, scaled with confidence)

# Risk adjustments
final_size = base_size × VIX_multiplier × drawdown_multiplier × vol_multiplier

# Voor shorts in hoge VIX (>25):
# → Size wordt automatisch kleiner (0.7x)
```

### Stop Loss / Take Profit

Standaard voor **alle posities** (long + short):

```python
take_profit = 7%   # 7% winst
stop_loss = 3%     # 3% verlies
```

Dit betekent voor shorts:
- Exit bij 7% **prijsdaling** (winst)
- Exit bij 3% **prijsstijging** (verlies)

## 🤖 AI Signal Generation

### News Scanner

De nieuws scanner kijkt naar **negatieve catalysts**:

- ❌ Rechtszaken / SEC investigations
- ❌ Product recalls
- ❌ Earnings misses
- ❌ Management scandals
- ❌ Regulatory crackdowns
- ❌ Major customer losses

Voorbeeld prompt:
```
"NVDA faces DOJ antitrust investigation"
→ AI: ACTION: SHORT, CONFIDENCE: 0.82
→ Bot: Opens short position
```

### Earnings Scanner

Pre-earnings analyse kan SHORT signals genereren:

```
Earnings in 2 days for AAPL

AI considers:
- Recent iPhone sales weak
- China revenue concerns
- Analyst downgrades

→ Decision: SHORT with 0.70 confidence
```

## ⚠️ Risico's en Limieten

### Inherent Risico Short Selling

**Onbeperkt verlies risico:**
- Long: max verlies = 100% (prijs naar $0)
- Short: max verlies = ∞ (prijs kan oneindig stijgen)

**Bot protecties:**
1. ✅ **Stop losses** (3% standaard)
2. ✅ **Position size limits** (max 15% per positie)
3. ✅ **Max positions** (15 totaal, zowel long als short)
4. ✅ **VIX regime detection** (kleiner in volatiele markten)
5. ✅ **Drawdown de-risking** (stopt bij 8% portfolio drawdown)

### Margin Requirements

Alpaca vereist **150-300% margin** voor shorts:
- Long $1000 → kost $1000
- Short $1000 → vereist $1500-3000 margin

Bot houdt rekening met `buying_power` checks.

### Borrow Availability

**Niet alle aandelen zijn shortable:**
- Hard-to-borrow stocks hebben hoge fees
- Low float stocks kunnen unavailable zijn
- Bot krijgt error als short niet mogelijk is

## 🔍 Monitoring

### Log Output

De bot logt duidelijk welk type positie:

```
🚀 Executing signal: SHORT 5000.00 TSLA @ $250.00
   Position type: SHORT
   Reason: 📰 SEC investigation announced
   Confidence: 78%
```

### Dashboard

De dashboard toont:
- Position type: LONG / SHORT
- P&L berekend voor juiste side
- Entry price en current price

## 📝 Samenvatting

✅ **Volledig geautomatiseerd** short selling
✅ **AI-driven** signal generation (nieuws + earnings)
✅ **Correcte P&L** berekening voor shorts
✅ **Automatische exits** (TP/SL werkt voor beide)
✅ **Risk management** (position sizing, stop losses)
✅ **Market hours** enforcement (alleen tijdens beurs open)

**De bot kan nu zowel long als short gaan volledig automatisch!** 🎉

## 🚀 Voorbeelden van Automatische Short Signalen

### Real-world scenario's waar de bot SHORT zou gaan:

1. **"Tesla recalls 2 million vehicles over Autopilot safety"**
   → SHORT TSLA (confidence: 0.85)

2. **"Meta faces $5B fine from EU regulators"**
   → SHORT META (confidence: 0.72)

3. **"Netflix subscriber count misses by 2 million"**
   → SHORT NFLX (confidence: 0.78)

4. **"AMD reports weak datacenter demand guidance"**
   → SHORT AMD (confidence: 0.70)

5. **Pre-earnings: "NVDA faces China export restrictions ahead of earnings"**
   → SHORT NVDA (confidence: 0.65)

De bot evalueert **elk uur** nieuws voor 7 symbolen en genereert automatisch SHORT signalen waar nodig! 📉

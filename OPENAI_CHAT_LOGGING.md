# OpenAI Chat Logging - Overzicht

## 🎯 Wat is toegevoegd

Je kunt nu **alle OpenAI conversaties** bekijken die de bot heeft gehad! Elke keer dat de bot OpenAI gebruikt (voor nieuws analyse, earnings analyse, etc.) wordt:

1. ✅ De **volledige prompt** opgeslagen
2. ✅ De **volledige response** opgeslagen
3. ✅ **Metadata** bijgehouden (tokens, kosten, timestamp, purpose)
4. ✅ Gelogd naar **database** (SQLite)
5. ✅ Gelogd naar **bestand** (voor makkelijk lezen)

## 📊 Hoe kun je de chats inzien?

### 1. Via Log Bestanden (Meest leesbaar)

**Locatie:** `/root/optifire/data/openai_logs/conversations_YYYY-MM-DD.log`

```bash
# Bekijk vandaag's gesprekken
cat /root/optifire/data/openai_logs/conversations_2025-11-04.log

# Live monitoring (zie nieuwe chats zodra ze gebeuren)
tail -f /root/optifire/data/openai_logs/conversations_*.log

# Zoek specifiek symbool
grep -A 20 "NVDA" /root/optifire/data/openai_logs/conversations_*.log
```

**Format:**
```
================================================================================
TIMESTAMP: 2025-11-04T15:31:42.290076
MODEL: gpt-4o-mini
PURPOSE: News Analysis: TSLA
TEMPERATURE: 0.3
MAX_TOKENS: 300
TOKENS_USED: 156
COST: $0.0023

--- PROMPT ---
SYSTEM: You are a financial analyst expert at interpreting market news and sentiment.

USER: Analyze these news headlines for TSLA and determine if there's a strong
trading opportunity.

Recent headlines:
- Tesla announces record deliveries, beats analyst estimates
- Elon Musk settles SEC lawsuit over Twitter acquisition

Instructions:
1. Look for major catalysts...
[volledige prompt]

--- RESPONSE ---
ACTION: BUY
CONFIDENCE: 0.75
REASON: Strong positive catalyst with record deliveries beating estimates,
indicating robust demand despite macro headwinds.
KEY_HEADLINE: Tesla announces record deliveries, beats analyst estimates
================================================================================
```

### 2. Via API Endpoints

De bot heeft nu een **REST API** om conversaties op te vragen:

```bash
# Alle conversaties (laatste 50)
curl http://localhost:8000/api/ai/conversations

# Met paginering
curl http://localhost:8000/api/ai/conversations?limit=100&offset=0

# Filter op purpose (bijv. alleen nieuws analyse)
curl "http://localhost:8000/api/ai/conversations?purpose=News%20Analysis"

# Filter op symbool
curl "http://localhost:8000/api/ai/conversations?purpose=TSLA"

# Specifieke conversatie
curl http://localhost:8000/api/ai/conversations/1

# Statistieken (totaal tokens, kosten, etc.)
curl http://localhost:8000/api/ai/conversations/stats

# Zoeken in prompts/responses
curl "http://localhost:8000/api/ai/conversations/search?query=NVDA"
```

**Voorbeeld response:**
```json
{
  "id": 1,
  "timestamp": "2025-11-04T15:31:42.290076",
  "model": "gpt-4o-mini",
  "purpose": "News Analysis: TSLA",
  "prompt": "SYSTEM: You are a financial analyst...\n\nUSER: Analyze these headlines...",
  "response": "ACTION: BUY\nCONFIDENCE: 0.75\nREASON: Strong positive catalyst...",
  "tokens_used": 156,
  "cost_usd": 0.0023,
  "temperature": 0.3,
  "max_tokens": 300
}
```

### 3. Via Database (SQLite)

```bash
# Open database
sqlite3 /root/optifire/data/optifire.db

# Bekijk alle conversaties
SELECT * FROM openai_conversations ORDER BY timestamp DESC LIMIT 10;

# Alleen voor een specifiek symbool
SELECT timestamp, purpose, tokens_used, cost_usd
FROM openai_conversations
WHERE purpose LIKE '%NVDA%'
ORDER BY timestamp DESC;

# Totale kosten vandaag
SELECT SUM(cost_usd) FROM openai_conversations
WHERE date(timestamp) = date('now');

# Per purpose samenvatting
SELECT purpose, COUNT(*) as count, SUM(tokens_used) as total_tokens, SUM(cost_usd) as total_cost
FROM openai_conversations
GROUP BY purpose
ORDER BY count DESC;
```

**Database schema:**
```sql
CREATE TABLE openai_conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    model TEXT NOT NULL,
    purpose TEXT,                    -- Bijvoorbeeld "News Analysis: TSLA"
    prompt TEXT NOT NULL,            -- Volledige prompt
    response TEXT NOT NULL,          -- Volledige AI response
    tokens_used INTEGER,
    cost_usd REAL,
    temperature REAL,
    max_tokens INTEGER
)
```

## 📈 Statistieken Endpoint

De `/api/ai/conversations/stats` endpoint geeft een mooi overzicht:

```bash
curl http://localhost:8000/api/ai/conversations/stats | jq
```

```json
{
  "total_conversations": 156,
  "total_tokens": 45230,
  "total_cost_usd": 0.3421,
  "last_24h": {
    "conversations": 23,
    "tokens": 6789,
    "cost_usd": 0.0512
  },
  "by_purpose": [
    {
      "purpose": "News Analysis: NVDA",
      "count": 45,
      "tokens": 12500,
      "cost_usd": 0.0945
    },
    {
      "purpose": "Pre-Earnings Analysis: TSLA",
      "count": 12,
      "tokens": 3200,
      "cost_usd": 0.0242
    }
  ]
}
```

## 🔍 Praktische Gebruik Cases

### Use Case 1: Waarom heeft de bot TSLA gekocht?

```bash
# Zoek alle TSLA analyses
grep -B 5 -A 30 "TSLA" /root/optifire/data/openai_logs/conversations_*.log

# Of via API
curl "http://localhost:8000/api/ai/conversations?purpose=TSLA" | jq
```

Je ziet dan:
- De exacte headlines die de AI zag
- Het complete reasoning process
- Confidence level en waarom

### Use Case 2: Hoeveel kost OpenAI per dag?

```bash
# Via API
curl http://localhost:8000/api/ai/conversations/stats | jq '.last_24h.cost_usd'

# Via database
sqlite3 /root/optifire/data/optifire.db \
  "SELECT SUM(cost_usd) FROM openai_conversations WHERE date(timestamp) = date('now')"
```

### Use Case 3: Live monitoring tijdens trading

```bash
# Open terminal en watch live
tail -f /root/optifire/data/openai_logs/conversations_*.log
```

Elke keer dat de bot OpenAI aanroept zie je:
- Welk nieuws item wordt geanalyseerd
- Wat de AI ervan vindt
- Of het een BUY/SHORT signal wordt

### Use Case 4: Welke symbolen zijn het meest geanalyseerd?

```bash
sqlite3 /root/optifire/data/optifire.db <<EOF
SELECT
  SUBSTR(purpose, INSTR(purpose, ':')+2) as symbol,
  COUNT(*) as analyses,
  SUM(tokens_used) as total_tokens
FROM openai_conversations
WHERE purpose LIKE 'News Analysis:%'
GROUP BY symbol
ORDER BY analyses DESC
LIMIT 10;
EOF
```

## 💰 Kosten Tracking

**gpt-4o-mini pricing:**
- Input: $0.150 per 1M tokens
- Output: $0.600 per 1M tokens

**Typische kosten:**
- Nieuws analyse: ~150 tokens = $0.0023 per analyse
- Pre-earnings analyse: ~200 tokens = $0.0030 per analyse
- Bij 100 analyses/dag = ~$0.25/dag = ~$7.50/maand

## 🎛️ Purpose Tags

De bot gebruikt deze purpose tags:

1. **"News Analysis: {SYMBOL}"** - Nieuws scanner
2. **"Pre-Earnings Analysis: {SYMBOL}"** - Earnings scanner
3. **"Test: {DESCRIPTION}"** - Test conversaties

Filter erop met:
```bash
curl "http://localhost:8000/api/ai/conversations?purpose=News%20Analysis"
```

## 🔧 Dashboard Integratie (Toekomst)

Je kunt een mooie dashboard pagina maken op:
```
http://localhost:8000/ai-conversations
```

Dit zou kunnen tonen:
- Recent chats (live updates)
- Token/cost charts
- Filter op symbool/purpose
- Search functionaliteit

## ⚙️ Configuratie

Logging is **altijd aan** en kan niet uitgeschakeld worden (voor transparantie).

Database locatie is configureerbaar:
```python
from optifire.ai.openai_client import OpenAIClient

client = OpenAIClient(db_path="/custom/path/optifire.db")
```

## 📝 Voorbeeld Sessie

```bash
# 1. Start de bot
sudo systemctl start optifire

# 2. Monitor OpenAI chats live
tail -f /root/optifire/data/openai_logs/conversations_*.log

# 3. In another terminal, check stats
watch -n 10 'curl -s http://localhost:8000/api/ai/conversations/stats | jq'

# 4. Zie in real-time:
#    - Welk nieuws wordt geanalyseerd
#    - Wat AI ervan vindt
#    - Of het een trade signal wordt
#    - Hoeveel het kost
```

## 🎯 Samenvatting

**Alles wordt gelogd:**
- ✅ Volledige prompts
- ✅ Volledige responses
- ✅ Tokens en kosten
- ✅ Timestamps en metadata

**Toegankelijk via:**
- 📄 Log bestanden (meest leesbaar)
- 🔌 REST API (programmatisch)
- 💾 SQLite database (queries)

**Transparantie:**
- Je ziet exact wat de AI ziet
- Je ziet exact hoe de AI redeneert
- Je kunt alle beslissingen traceren

Dit maakt debugging en optimalisatie veel makkelijker! 🚀

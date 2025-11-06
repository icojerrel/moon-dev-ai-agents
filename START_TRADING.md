# 🚀 START TRADING NU!

Volg deze stappen om **vandaag** te beginnen met AI-powered paper trading op MT5.

---

## ✅ PRE-FLIGHT CHECKLIST (5 minuten)

### 1️⃣ MetaTrader 5 Gereed

- [ ] MT5 geïnstalleerd ([download hier](https://www.metatrader5.com/en/download))
- [ ] MT5 **draait** (terminal is open)
- [ ] Demo account aangemaakt
- [ ] Ingelogd in MT5 (groene verbinding rechtsonder)
- [ ] Market Watch zichtbaar (Ctrl+M)

**Demo Account Aanmaken:**
1. File → Open an Account
2. Kies **MetaQuotes-Demo**
3. Selecteer "Open a demo account"
4. Vul in: Deposit $10,000, Leverage 1:100
5. **Schrijf credentials op!**

---

### 2️⃣ Code Gereed

```bash
# Op je Windows PC:
cd C:\path\to\moon-dev-ai-agents

# Pull laatste wijzigingen
git pull origin claude/check-rbi-agent-sync-011CUr2WPY92uVwAtpiBnjwB

# Of clone fresh:
git clone https://github.com/jouw-username/moon-dev-ai-agents.git
cd moon-dev-ai-agents
git checkout claude/check-rbi-agent-sync-011CUr2WPY92uVwAtpiBnjwB
```

---

### 3️⃣ Installeer Dependencies

**Optie A: Automated (Aanbevolen)**
```bash
install_mt5_windows.bat
```

**Optie B: Handmatig**
```bash
# Activeer conda environment (als je die hebt)
conda activate tflow

# Installeer MT5 library
pip install MetaTrader5

# Installeer overige dependencies
pip install -r requirements.txt
```

---

### 4️⃣ Configureer Credentials

**Maak `.env` bestand** (kopieer van `.env_example`):

```bash
# MT5 Account Credentials
MT5_LOGIN=12345678                      # Jouw demo account nummer
MT5_PASSWORD=DemoPass123                # Jouw demo password
MT5_SERVER=MetaQuotes-Demo              # Jouw broker server

# AI Model Key (kies er één)
GROK_API_KEY=xai-your_key_here         # ✅ Aanbevolen (goedkoop, snel)
# Of:
GROQ_API_KEY=your_groq_key             # ✅ Ook goed (gratis tier)
# Of:
OPENAI_KEY=sk-your_key                 # ✅ GPT-4 (duurder)
# Of:
ANTHROPIC_KEY=your_claude_key          # ✅ Claude (slim)

# Andere API keys (optioneel)
BIRDEYE_API_KEY=your_key               # Voor crypto data
SOLANA_PRIVATE_KEY=your_key            # Voor Solana trading
```

**⚠️ BELANGRIJK:** Verander `MT5_LOGIN`, `MT5_PASSWORD`, `MT5_SERVER` naar **jouw** demo account!

---

### 5️⃣ Check Configuratie

Open `src/config.py` en verifieer:

```python
# MT5 Settings
MT5_ENABLED = True  # ✅ Moet True zijn!

# Trading symbols (verander naar wat jij wil traden)
MT5_SYMBOLS = [
    'EURUSD',  # ✅ Deze werken meestal altijd
    'GBPUSD',
    'USDJPY',
    'XAUUSD',  # Gold
]

# Veilige test settings
MT5_LOT_SIZE = 0.01              # Micro lot (klein!)
MT5_MAX_POSITIONS = 3            # Max 3 trades
MT5_RISK_PERCENT = 0.5           # Risk 0.5% per trade
MT5_STOP_LOSS_POINTS = 500       # 50 pip SL
MT5_TAKE_PROFIT_POINTS = 1000    # 100 pip TP

# Trading interval
SLEEP_BETWEEN_RUNS_MINUTES = 15  # Check elke 15 min
```

---

## 🚀 OPSTARTEN

### Optie 1: MT5 Agent Alleen (Aanbevolen voor eerste keer)

```bash
start_mt5_trading.bat
```

Of handmatig:
```bash
python src/agents/mt5_trading_agent.py
```

**Verwachte Output:**
```
🌙 Moon Dev's MT5 AI Trading Agent Initialized
✅ Connected to MT5 account: 12345678
📊 Server: MetaQuotes-Demo
💰 Balance: $10000.00
💵 Equity: $10000.00

============================================================
📊 TRADING STATISTICS
============================================================
💰 Balance: $10000.00
💵 Equity: $10000.00
📈 Profit: $0.00
📊 Margin Level: 0.00%
🎯 Open Positions: 0
📝 Trades Today: 0
============================================================

📊 Analyzing EURUSD...
✅ AI Model initialized: xai

BUY SIGNAL: EURUSD
   Price: 1.08245
   Lot Size: 0.01
   Stop Loss: 1.07745
   Take Profit: 1.09245
   AI Reasoning: Price broke above MA20 with strong momentum...

✅ BUY EURUSD: 0.01 lots @ 1.08245
📈 Position opened: #123456

😴 Sleeping for 15 minutes...
```

---

### Optie 2: Volledig Systeem (MT5 + Andere Agents)

**Activeer MT5 in `src/main.py`:**
```python
ACTIVE_AGENTS = {
    'risk': False,
    'trading': False,
    'strategy': False,
    'copybot': False,
    'sentiment': False,
    'mt5': True,  # ✅ Zet op True
}
```

**Start:**
```bash
start_mt5_with_orchestrator.bat
```

Of handmatig:
```bash
python src/main.py
```

---

## 📊 MONITORING

### Waar Zie Je Je Trades?

**1. MetaTrader 5 Terminal:**
- View → Terminal (Ctrl+T)
- Tabblad "Trade" = open posities
- Tabblad "History" = gesloten trades

**2. Console Output:**
- Realtime trading beslissingen
- AI reasoning
- Win/loss updates

**3. Trade Logs (CSV):**
```
src/data/mt5_trading_agent/trades_20250206.csv
```

Kolommen: timestamp, symbol, action, price, lot_size, sl, tp, reasoning

**4. Account Info:**
- In MT5: Tools → Account History
- Of via console output elke trading cycle

---

## 🎯 EERSTE DAG VERWACHTINGEN

### ✅ Normaal Gedrag

```
📊 Analyzing EURUSD...
⏸️ EURUSD: No trade signal
   Reasoning: Price ranging between MA20 and MA50, awaiting clearer signal...

📊 Analyzing GBPUSD...
🟢 BUY SIGNAL: GBPUSD
   AI Reasoning: Bullish breakout above resistance...
✅ BUY GBPUSD: 0.01 lots @ 1.27345
```

**Gemiddeld:**
- 1-5 trades per dag (afhankelijk van volatiliteit)
- Niet elk symbool geeft signaal
- AI wacht vaak op duidelijke patronen
- De meeste tijd: "NOTHING" (en dat is goed!)

### ⚠️ Waarschuwingen

**Als je dit ziet:**
```
❌ Failed to connect to MT5
```
→ MT5 terminal is niet aan! Start MT5 eerst.

```
❌ Symbol XXXUSD not found
```
→ Symbool niet beschikbaar bij jouw broker. Check Market Watch (Ctrl+M)

```
❌ Not enough money
```
→ Te groot lot size. Verlaag `MT5_LOT_SIZE` naar 0.01

```
⚠️ Maximum positions reached (3)
```
→ Normaal! Bot wacht tot er ruimte is.

---

## 📈 PERFORMANCE TRACKING

### Dagelijkse Check (5 min)

1. **Open MT5 Terminal**
   - Check balance en equity
   - Bekijk open posities
   - Review trade history

2. **Check Logs**
   ```bash
   # Open laatste trade log
   notepad src\data\mt5_trading_agent\trades_20250206.csv
   ```

3. **Console Output**
   - Lees AI reasoning
   - Check voor errors
   - Verifieer trading interval

### Week Review

**Bereken Performance:**
```python
# In Python console:
import pandas as pd
df = pd.read_csv('src/data/mt5_trading_agent/trades_20250206.csv')

# Aantal trades
print(f"Total trades: {len(df)}")

# Per symbool
print(df['symbol'].value_counts())

# BUY vs SELL
print(df['action'].value_counts())
```

**Check in MT5:**
- Right-click History → Custom Period → Last Week
- Bekijk profit/loss grafiek
- Analyseer welke symbolen goed/slecht presteren

---

## ⚙️ OPTIMALISATIE TIPS

### Week 1: Observeren
- Laat draaien met default settings
- Noteer welke symbolen het meeste traden
- Check AI reasoning - is het logisch?
- **Verander nog niks!**

### Week 2: Aanpassen

**Als te weinig trades:**
```python
MT5_SYMBOLS = [
    'EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD',  # Meer symbolen
    'USDCAD', 'NZDUSD', 'EURGBP', 'EURJPY',
]
SLEEP_BETWEEN_RUNS_MINUTES = 5  # Check vaker
```

**Als te veel trades:**
```python
MT5_SYMBOLS = ['EURUSD', 'GBPUSD']  # Minder symbolen
SLEEP_BETWEEN_RUNS_MINUTES = 30     # Check minder vaak
```

**Als te veel losses:**
```python
MT5_STOP_LOSS_POINTS = 300    # Kortere SL (30 pips)
MT5_TAKE_PROFIT_POINTS = 900  # Grotere TP (90 pips) = 1:3 R:R
```

**Als te conservatief:**
```python
MT5_LOT_SIZE = 0.02           # Grotere posities
MT5_MAX_POSITIONS = 5         # Meer concurrent trades
```

---

## 🆘 TROUBLESHOOTING

### Bot Stopt Met Error

**Check:**
1. Is MT5 nog aan?
2. Is internet verbinding OK?
3. Is demo account nog actief? (verloopt na 30 dagen)

**Herstart:**
```bash
# Stop bot (Ctrl+C)
# Check MT5 verbinding
# Herstart bot
start_mt5_trading.bat
```

### Geen Trades Na Uren

**Normaal als:**
- Markten zijn gesloten (weekend, feestdagen)
- Geen duidelijke signalen (ranging market)
- Alle symbolen al open posities hebben

**Check:**
1. Market Watch - zien prijzen veranderen?
2. Console - zegt AI "NOTHING" met goede reden?
3. Timeframe - probeer H1 of M15 voor meer signalen

### AI Geeft Rare Signalen

**Check AI Model:**
```python
# In mt5_trading_agent.py:
AI_MODEL_TYPE = 'xai'      # Probeer verschillende
AI_MODEL_NAME = None

# Alternatieven:
# AI_MODEL_TYPE = 'groq'   # Llama 3.3
# AI_MODEL_TYPE = 'claude' # Claude Sonnet
```

---

## 🎓 LEREN VAN JE BOT

### Goede Gewoonte: Log Bijhouden

**Elke dag noteer:**
```
Datum: 2025-02-06
Trades: 3
Wins: 2
Losses: 1
Beste trade: EURUSD +50 pips
Slechtste trade: GBPUSD -30 pips
AI Model: xAI Grok
Notities: AI goed in trend detection, minder goed bij ranging
```

**Wekelijkse Review:**
- Welk symbool het meest winstgevend?
- Welke timeframe werkt best?
- Welk AI model geeft beste reasoning?
- Wat is gemiddelde win rate?

---

## 🚀 VOLGENDE STAPPEN

### Na 1 Week Demo:
- [ ] Analyseer performance
- [ ] Optimaliseer settings
- [ ] Test andere symbolen
- [ ] Probeer verschillende AI models

### Na 1 Maand Demo:
- [ ] Bereken totale profit/loss
- [ ] Check consistency
- [ ] Documenteer beste settings
- [ ] Besluit: live gaan of meer testen?

### Naar Live Trading (Optioneel):
⚠️ **ALLEEN als:**
- [ ] Winstgevend op demo >3 maanden
- [ ] Je begrijpt elke trade
- [ ] Je kunt losses accepteren
- [ ] Je start met **minimale** positie sizes

**Live Setup:**
```python
# Krijg live account bij broker
# Update .env met live credentials
MT5_SERVER=BrokerName-Live  # Let op: LIVE!
MT5_LOT_SIZE = 0.01         # Start klein!
MT5_MAX_POSITIONS = 1       # Zeer voorzichtig
```

---

## 📞 HULP NODIG?

**Checklist voor hulp vragen:**
1. Wat zie je in console output?
2. Wat staat in laatste trade log?
3. Is MT5 aan en verbonden?
4. Welke error message precies?

**Resources:**
- 📖 Volledige guide: `src/agents/MT5_SETUP_GUIDE.md`
- 🚀 Quick start: `src/agents/MT5_QUICKSTART.md`
- 💻 Code: `src/agents/mt5_trading_agent.py`
- 🌙 Moon Dev YouTube: [@moondevonyt](https://youtube.com/@moondevonyt)

---

## 🎉 JE BENT KLAAR!

**Run dit commando en start met traden:**

```bash
start_mt5_trading.bat
```

**Of test eerst de verbinding:**

```bash
python src/agents/mt5_utils.py
```

---

## ⚠️ DISCLAIMER

Dit is **experimentele software** voor educatieve doeleinden:

- ✅ Demo trading wordt aangemoedigd
- ⚠️ Live trading op eigen risico
- ❌ Geen garantie van winst
- 📉 Substantieel risico van verlies

**Altijd:**
- Test grondig op demo
- Start met minimale position sizes
- Risk nooit geld dat je niet kunt missen
- Begrijp de risico's van algoritmisch traden

---

Built with 🌙 by Moon Dev

**HAPPY TRADING! 🚀📈💰**

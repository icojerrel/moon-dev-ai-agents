# 🌙 MT5 Trading Agent - Stap voor Stap Installatie

**Complete installatiegids voor $150K SMC Trading Agent**

---

## 📋 Overzicht Stappen

1. ✅ MT5 Platform Installeren
2. ✅ Demo Account Aanmaken
3. ✅ Python Dependencies Installeren
4. ✅ Ollama + Qwen3-Coder Installeren
5. ✅ MT5 Python Connectie Testen
6. ✅ Paper Trading Draaien
7. ✅ Eerste Trade Cycle Verifiëren

**Geschatte tijd**: 30-45 minuten

---

## 📝 Voordat Je Begint

### Wat Je Nodig Hebt:
- ✅ Computer met Windows/Mac/Linux
- ✅ ~10GB vrije schijfruimte (voor Ollama model)
- ✅ Stabiele internetverbinding
- ✅ Python 3.8+ (check: `python --version`)
- ✅ Conda environment "tflow" (zoals in je project)

### Check Je Python Versie
```bash
python --version
# Of
python3 --version

# Moet 3.8 of hoger zijn
```

---

## STAP 1: MT5 Platform Installeren

### Windows

1. **Download MT5**
   - Ga naar: https://www.metatrader5.com/en/download
   - Klik op "Download MetaTrader 5"
   - Of download via je broker (bijvoorbeeld: XM, IC Markets, FTMO)

2. **Installeer MT5**
   ```
   - Dubbelklik op mt5setup.exe
   - Volg de installatie wizard
   - Kies installatiemap (standaard is OK)
   - Wacht tot installatie klaar is
   ```

3. **Start MT5**
   - Open MetaTrader 5 vanaf desktop icoon
   - Je ziet het welkomstscherm

### Mac

1. **Download MT5 voor Mac**
   - Ga naar: https://www.metatrader5.com/en/download
   - Klik op "Download for Mac"

2. **Installeer**
   ```
   - Open het .dmg bestand
   - Sleep MT5 naar Applications
   - Open MT5 vanuit Applications
   ```

### Linux

1. **Download Windows versie**
   - Je moet MT5 via Wine draaien op Linux
   - Of gebruik Windows in een VM

2. **Alternatief: Wine Setup**
   ```bash
   # Installeer Wine
   sudo apt-get install wine64

   # Download MT5 Windows versie
   wget https://download.mql5.com/cdn/web/metaquotes.software.corp/mt5/mt5setup.exe

   # Installeer via Wine
   wine mt5setup.exe
   ```

**✅ Verificatie**: MT5 is geïnstalleerd en start op

---

## STAP 2: Demo Account Aanmaken

### In MT5:

1. **Open Account Dialog**
   ```
   Menu: File → Open an Account
   Of: Ctrl + Shift + O
   ```

2. **Kies Broker**
   - Zoek "MetaQuotes" of gebruik je eigen broker
   - Voor testen: "MetaQuotes-Demo" is prima
   - Klik "Next"

3. **Kies Account Type**
   - Selecteer: "Open a demo account"
   - Klik "Next"

4. **Vul Gegevens In**
   ```
   Name:          Jouw naam
   Email:         Je email
   Phone:         Je telefoonnummer
   Account Type:  Standard (of Hedge)
   Deposit:       150000 USD  ← BELANGRIJK!
   Leverage:      1:100 of 1:200
   ```

5. **Krijg Login Gegevens**
   ```
   MT5 toont je:
   - Login nummer (bijvoorbeeld: 12345678)
   - Password
   - Server naam

   ⚠️ SCHRIJF DEZE OP! Je hebt ze later nodig
   ```

6. **Test Inloggen**
   - MT5 logt automatisch in
   - Rechtsonderin zie je: verbindingsindicator (moet groen zijn met snelheid)
   - In "Terminal" (Ctrl+T) zie je: Account Balance $150,000.00

**✅ Verificatie**: Demo account is actief met $150,000 balance

---

## STAP 3: Python Dependencies Installeren

### Activeer Je Conda Environment

```bash
# Ga naar je project folder
cd /home/user/moon-dev-ai-agents

# Activeer tflow environment
conda activate tflow

# Verify
conda info --envs
# Je moet een * zien bij tflow
```

### Installeer Dependencies

```bash
# Installeer alle requirements
pip install -r requirements.txt

# Dit installeert onder andere:
# - MetaTrader5>=5.0.45 (MT5 Python API)
# - pandas, numpy
# - termcolor (voor mooie output)
# - En alle andere dependencies
```

### Verificatie

```bash
# Test of MetaTrader5 package is geïnstalleerd
python -c "import MetaTrader5 as mt5; print(f'MT5 version: {mt5.__version__}')"

# Verwachte output:
# MT5 version: 5.0.45 (of hoger)
```

**✅ Verificatie**: Dependencies zijn geïnstalleerd

---

## STAP 4: Ollama + Qwen3-Coder Installeren

### 4.1 Installeer Ollama

#### Windows
```bash
# Download installer van:
https://ollama.com/download/windows

# Dubbelklik op OllamaSetup.exe
# Volg installatie wizard
```

#### Mac
```bash
# Download van:
https://ollama.com/download/mac

# Of via Homebrew:
brew install ollama
```

#### Linux
```bash
# Installeer via curl
curl -fsSL https://ollama.com/install.sh | sh

# Verificatie
which ollama
# Output: /usr/local/bin/ollama
```

### 4.2 Start Ollama Service

**Open een NIEUWE terminal** (laat deze terminal open!)

```bash
# Start Ollama server
ollama serve

# Je ziet:
# Ollama is running on http://localhost:11434
```

⚠️ **BELANGRIJK**: Laat deze terminal open! Ollama moet blijven draaien.

### 4.3 Download Qwen3-Coder Model

**Open een TWEEDE terminal**

```bash
# Activeer environment
conda activate tflow

# Download het 30B model (dit duurt 15-30 minuten)
ollama pull qwen3-coder:30b

# Je ziet een progress bar:
# pulling manifest
# pulling 4f9b5... 100% ████████████ 17GB/17GB
# pulling 8a8... 100% ████████████ 1.5GB/1.5GB
# ...
# success
```

**Download grootte**: ~17GB (zorg dat je genoeg ruimte hebt!)

### 4.4 Verificatie

```bash
# Check of model beschikbaar is
ollama list

# Je moet zien:
# NAME                    ID              SIZE    MODIFIED
# qwen3-coder:30b         abc123def       17GB    2 minutes ago

# Test het model
ollama run qwen3-coder:30b "Write a hello world in Python"

# Je moet een response krijgen met code
```

**✅ Verificatie**: Ollama draait en qwen3-coder:30b is beschikbaar

---

## STAP 5: MT5 Python Connectie Testen

### 5.1 Zorg dat MT5 draait
- Open MT5 applicatie
- Zorg dat je ingelogd bent op je demo account
- Je ziet je balance $150,000

### 5.2 Maak Test Script

```bash
# In je project directory
nano test_mt5_connection.py
```

Plak deze code:

```python
#!/usr/bin/env python3
import MetaTrader5 as mt5
from termcolor import cprint

cprint("\n🔧 Testing MT5 Connection...\n", "cyan")

# Initialize MT5
if not mt5.initialize():
    cprint("❌ MT5 initialize() failed", "red")
    cprint(f"Error: {mt5.last_error()}", "yellow")
    quit()

cprint("✅ MT5 initialized successfully!", "green")

# Get account info
account_info = mt5.account_info()
if account_info is None:
    cprint("❌ Failed to get account info", "red")
    mt5.shutdown()
    quit()

# Show account details
cprint("\n💼 Account Information:", "cyan")
cprint(f"  Login: {account_info.login}", "white")
cprint(f"  Server: {account_info.server}", "white")
cprint(f"  Balance: ${account_info.balance:,.2f}", "green")
cprint(f"  Equity: ${account_info.equity:,.2f}", "white")
cprint(f"  Leverage: 1:{account_info.leverage}", "white")

# Test getting symbols
symbols = mt5.symbols_get()
cprint(f"\n📊 Available Symbols: {len(symbols)}", "cyan")

# Try to get EURUSD price
symbol = "EURUSD"
tick = mt5.symbol_info_tick(symbol)

if tick:
    cprint(f"\n💹 {symbol} Current Price:", "cyan")
    cprint(f"  Bid: {tick.bid:.5f}", "white")
    cprint(f"  Ask: {tick.ask:.5f}", "white")
    cprint(f"  Spread: {(tick.ask - tick.bid):.5f}", "yellow")
else:
    cprint(f"\n⚠️  Could not get {symbol} price", "yellow")

# Shutdown
mt5.shutdown()
cprint("\n✅ All tests passed! MT5 connection works!\n", "green")
```

### 5.3 Run Test

```bash
# Run het test script
python test_mt5_connection.py
```

### Verwachte Output:

```
🔧 Testing MT5 Connection...

✅ MT5 initialized successfully!

💼 Account Information:
  Login: 12345678
  Server: MetaQuotes-Demo
  Balance: $150,000.00
  Equity: $150,000.00
  Leverage: 1:100

📊 Available Symbols: 127

💹 EURUSD Current Price:
  Bid: 1.08450
  Ask: 1.08453
  Spread: 0.00003

✅ All tests passed! MT5 connection works!
```

### ⚠️ Troubleshooting

**Error: "MT5 initialize() failed"**
- ✅ Check: Is MT5 applicatie open?
- ✅ Check: Ben je ingelogd op demo account?
- ✅ Check: Draait MT5 op dezelfde computer?

**Error: "No module named 'MetaTrader5'"**
```bash
# Installeer opnieuw
pip install MetaTrader5>=5.0.45
```

**Error: Permission denied**
- Windows: Run Python als Administrator
- Mac/Linux: Check MT5 via Wine of gebruik Windows VM

**✅ Verificatie**: Python kan succesvol met MT5 communiceren

---

## STAP 6: Paper Trading Agent Starten

### 6.1 Laatste Checks

```bash
# Terminal 1: Ollama draait?
# Je moet zien: "Ollama is running on http://localhost:11434"

# Terminal 2: MT5 draait en je bent ingelogd?
# Open MT5 en check balance $150,000

# Terminal 3: Conda environment actief?
conda activate tflow
cd /home/user/moon-dev-ai-agents
```

### 6.2 Start de Agent

```bash
# Start agent met jouw $150k configuratie
python src/agents/mt5_agent_smc.py --balance 150000 --interval 15 --max-positions 1
```

### 6.3 Verwachte Output

```
======================================================================
  🌙 Moon Dev's MT5 SMC Trading Agent
  Smart Money Concepts + Qwen3-Coder:30b
======================================================================

📝 PAPER TRADING MODE - No real trades will be executed!
💰 Virtual balance: $150,000.00

🤖 Initializing AI model...
✅ AI Model loaded: qwen3-coder:30b

💼 Account Size: $150,000.00
📊 Risk Parameters:
  Risk per trade: 1.0%
  Max positions: 5
  Max daily loss: 4.0%
  Take profit target: 3.0R
  Min confidence: 75%

⚙️  Overriding max positions: 1

🚀 Starting SMC trading loop...
  Interval: 15 minutes
  Symbols: EURUSD, GBPUSD, USDJPY
  Max Positions: 1
  Risk per Trade: 1.0%
  Strategy: Smart Money Concepts

  Press Ctrl+C to stop

██████████████████████████████████████████████████████████████████████
  SMC CYCLE 1 - 2025-01-15 14:30:00
██████████████████████████████████████████████████████████████████████

💰 Account Status:
  Balance: $150,000.00
  Equity: $150,000.00
  P/L: $0.00

🔍 SMC Analysis for EURUSD...
```

**De agent is nu actief!** 🎉

### 6.4 Wat Gebeurt Er Nu?

De agent zal:
1. ✅ Elke 15 minuten 3 symbols analyseren (EURUSD, GBPUSD, USDJPY)
2. ✅ SMC indicators detecteren (IFVGs, Breaker Blocks, etc.)
3. ✅ Qwen3-Coder vragen om analyse
4. ✅ Als confidence > 75% en 2+ confluences: trade openen
5. ✅ Posities managen (TP bij $4,500, SL bij -$1,500)

---

## STAP 7: Eerste Trade Cycle Verifiëren

### 7.1 Wat Te Verwachten

**Cycle 1-4 (eerste uur)**:
- Agent analyseert alle 3 symbols
- Mogelijk nog geen trades (wacht op goede setup)
- Je ziet SMC analyses verschijnen

**Als een Trade Gevonden Wordt**:
```
🔍 SMC Analysis for EURUSD...

📊 SMC MARKET ANALYSIS - EURUSD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MARKET STRUCTURE: BULLISH
  - Trend: Higher Highs + Higher Lows
  - Confidence: 85%

ACTIVE IFVGs (Imbalance Fair Value Gaps):
  🟢 BULLISH IFVG: 1.08234 - 1.08456 (22.2 pips)

BREAKER BLOCKS:
  🔵 BULLISH BREAKER: 1.08123 (former resistance, now support)

ORDER BLOCKS:
  ⬛ BULLISH OB: 1.07989 - 1.08045 (last up candle before pullback)

LIQUIDITY ZONES:
  💧 BUY-SIDE LIQ: Below 1.07850 (stop hunt area)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🤔 AI analyzing with SMC context...
✅ Analysis complete in 8.2s

📊 EURUSD SMC Decision:
  Decision: BUY
  Confidence: 82%
  SMC Confluences: Bullish IFVG + Bullish structure + Breaker block

💼 Position Sizing:
  Account Balance: $150,000.00
  Risk per Trade: 1.0%
  Risk Amount: $1,500.00
  Stop Loss Distance: 30.0 pips
  Calculated Lot Size: 5.00
  Lot Range: 0.2 - 5.0

======================================================================
🎯 SMC TRADE SIGNAL
======================================================================
  Symbol: EURUSD
  Decision: BUY
  Confidence: 82%
  SMC Confluences: Bullish IFVG + Bullish structure + Breaker block
  Reasoning: Price bounced from bullish IFVG zone with market
             structure confirmation and breaker block support

  Market Structure: BULLISH
  Active IFVGs: 1
  Breaker Blocks: 1
  Order Blocks: 1

  Entry Price: 1.08450
  Stop Loss: 1.08150
  Take Profit: 1.09350
  Lot Size: 5.0
======================================================================

📝 Paper trade opened:
   Symbol: EURUSD
   Type: BUY
   Volume: 5.0 lots
   Entry: 1.08450
   SL: 1.08150 (-30 pips = -$1,500)
   TP: 1.09350 (+90 pips = +$4,500)

✅ SMC Trade executed! Ticket: 1

😴 Sleeping for 15 minutes...
```

### 7.2 Monitor Je Trade

**Volgende Cycle (15 minuten later)**:
```
██████████████████████████████████████████████████████████████████████
  SMC CYCLE 2 - 2025-01-15 14:45:00
██████████████████████████████████████████████████████████████████████

💰 Account Status:
  Balance: $150,000.00
  Equity: $150,350.00
  P/L: $350.00

📊 Managing 1 position(s)...

  Position 1:
    Symbol: EURUSD
    Type: BUY
    Entry: 1.08450
    P/L: $350.00
    Target: $4,500.00 | Stop: $-1,500.00

🔍 SMC Analysis for EURUSD...
⏸️  Max positions reached (1)

🔍 SMC Analysis for GBPUSD...
⏸️  Max positions reached (1)

🔍 SMC Analysis for USDJPY...
⏸️  Max positions reached (1)

😴 Sleeping for 15 minutes...
```

### 7.3 Check Trade History

```bash
# In een nieuwe terminal
cd /home/user/moon-dev-ai-agents

# Bekijk trade history file
cat src/data/mt5_paper/paper_trades.json | python -m json.tool
```

Output:
```json
{
  "initial_balance": 150000.0,
  "current_balance": 150000.0,
  "trade_history": [
    {
      "ticket": 1,
      "symbol": "EURUSD",
      "type": "BUY",
      "volume": 5.0,
      "open_time": "2025-01-15 14:30:15",
      "open_price": 1.08450,
      "sl": 1.08150,
      "tp": 1.09350,
      "status": "OPEN",
      "profit": 350.0,
      "comment": "SMC 82%"
    }
  ]
}
```

**✅ Verificatie**: Agent draait en kan trades openen/managen

---

## 🎯 Je Bent Klaar!

### Checklist:
- ✅ MT5 geïnstalleerd en demo account actief
- ✅ Python dependencies geïnstalleerd
- ✅ Ollama + qwen3-coder:30b draait
- ✅ MT5 Python connectie werkt
- ✅ Agent draait in paper trading mode
- ✅ Eerste analyses zijn succesvol

### Wat Nu?

#### Korte Termijn (Vandaag/Morgen):
```bash
# Laat de agent draaien voor een paar uur
# Monitor de output
# Check of trades worden geopend/gesloten
```

#### Deze Week:
```bash
# Laat agent continu draaien (of in ieder geval tijdens market hours)
# Analyseer resultaten einde van de week:
python -c "
import json
with open('src/data/mt5_paper/paper_trades.json') as f:
    data = json.load(f)
print(f'Balance: ${data[\"current_balance\"]:,.2f}')
print(f'Trades: {len(data[\"trade_history\"])}')
"
```

#### Na 2-4 Weken Paper Trading:
- Evalueer win rate (target: >50%)
- Evalueer profit factor (target: >1.5)
- Als succesvol: overweeg live trading met kleinere posities

---

## 🔧 Handige Commands

### Stop de Agent
```bash
# Druk op Ctrl+C in de terminal waar agent draait
# Agent sluit netjes af en toont finale stats
```

### Herstart de Agent
```bash
# Zelfde command als eerst
python src/agents/mt5_agent_smc.py --balance 150000 --interval 15 --max-positions 1
```

### Check Trade History
```bash
# Quick stats
python -c "
import json
import pandas as pd

with open('src/data/mt5_paper/paper_trades.json') as f:
    data = json.load(f)

trades = pd.DataFrame(data['trade_history'])
closed = trades[trades['status'] == 'CLOSED']

if len(closed) > 0:
    print(f'Closed Trades: {len(closed)}')
    print(f'Win Rate: {(closed[\"profit\"] > 0).sum() / len(closed) * 100:.1f}%')
    print(f'Total P/L: ${closed[\"profit\"].sum():,.2f}')
else:
    print('No closed trades yet')
"
```

### Check Ollama Status
```bash
# Is Ollama running?
curl http://localhost:11434/api/tags

# Should return JSON with models list
```

### View Logs in Real-Time
```bash
# Als agent draait in terminal 1
# Open terminal 2:
tail -f src/data/mt5_agent/agent.log  # Als je logging hebt ingeschakeld
```

---

## ❓ Troubleshooting

### "Ollama not available"
```bash
# Check of Ollama draait
curl http://localhost:11434/api/tags

# Zo niet, start het:
ollama serve
```

### "MT5 initialize() failed"
```bash
# 1. Check: Is MT5 applicatie open?
# 2. Check: Ben je ingelogd?
# 3. Windows: Run terminal als Administrator
# 4. Herstart MT5
```

### "No module named X"
```bash
# Herinstalleer dependencies
conda activate tflow
pip install -r requirements.txt
```

### Agent crasht tijdens analyse
```bash
# Check qwen3-coder model
ollama list

# Re-download als nodig
ollama pull qwen3-coder:30b
```

### Geen trades worden geopend
- ✅ Normaal! Agent is zeer selectief (75% confidence)
- ✅ Wacht op goede SMC setups
- ✅ Kan uren duren voor eerste trade
- ✅ Check tijdens London/NY session (meeste volatiliteit)

---

## 📚 Volgende Stappen

1. **Lees de documentatie**:
   - `QUICK_START_150K.md` - Snelle referentie
   - `MT5_150K_ACCOUNT_SETUP.md` - Technische details
   - `MT5_SMC_COMPARISON.md` - Strategie uitleg

2. **Monitor en Leer**:
   - Bekijk waarom agent trades neemt
   - Check SMC confluences in analyse output
   - Leer van de reasoning die AI geeft

3. **Optimaliseer**:
   - Test verschillende intervals (5, 15, 30, 60 min)
   - Pas min_confidence aan in code indien nodig
   - Voeg meer symbols toe (zie config)

4. **Na Succesvolle Paper Trading**:
   - Evalueer 2-4 weken resultaten
   - Start live met 50% position size
   - Scale geleidelijk op naar volle size

---

## 🌙 Support

**Vragen?**
- Check de andere MD files in project
- Kijk naar agent code: `src/agents/mt5_agent_smc.py`
- Test scripts: alle files met `test_` prefix

**Succes met je trading journey! 🚀**

---

*Laatste update: 2025-01-15*
*Voor project: moon-dev-ai-agents*

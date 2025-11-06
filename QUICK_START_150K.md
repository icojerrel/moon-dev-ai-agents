# 🚀 Quick Start - $150K Account

## Voor jouw $150,000 account met maximaal 1 positie tegelijk

---

## ⚡ Direct Starten

### Paper Trading (Aanbevolen om mee te beginnen)

```bash
python src/agents/mt5_agent_smc.py --balance 150000 --interval 15 --max-positions 1
```

### Live Trading (Alleen na grondig testen!)

```bash
python src/agents/mt5_agent_smc.py --live --balance 150000 --interval 15 --max-positions 1
```

---

## 📊 Jouw Configuratie

```
Account Balance:     $150,000
Max Positions:       1 (jouw voorkeur)
Risk per Trade:      1% = $1,500
Monitoring:          Elke 15 minuten
Strategy:            Smart Money Concepts (SMC)
Min Confidence:      75%
Take Profit:         3R = $4,500
Stop Loss:           1R = $1,500
```

---

## 💼 Position Sizing Voorbeelden

### EURUSD met 30 pip Stop Loss
```
Risk:               $1,500 (1%)
Stop Loss:          30 pips
Lot Size:           5.00 lots (max)
Position Value:     $500,000
Max Loss:           $1,500
Target Profit:      $4,500 (3R)
```

### GBPUSD met 50 pip Stop Loss
```
Risk:               $1,500 (1%)
Stop Loss:          50 pips
Lot Size:           3.00 lots
Position Value:     $300,000
Max Loss:           $1,500
Target Profit:      $4,500 (3R)
```

---

## 📈 Verwachte Prestaties (1 positie tegelijk)

### Met 60% winratio (SMC strategie)

**Per Dag**:
- Trades: 1-2 trades per dag
- Winstkans: 60%
- Gemiddelde winst: $4,500
- Gemiddeld verlies: $1,500

**Per Week** (5 trading dagen):
```
Trades:        7 (1.4 per dag)
Wins:          4.2 @ $4,500 = $18,900
Losses:        2.8 @ -$1,500 = -$4,200
Net Profit:    $14,700
Weekly Return: 9.8%
```

**Per Maand** (20 trading dagen):
```
Trades:        28 (1.4 per dag)
Wins:          16.8 @ $4,500 = $75,600
Losses:        11.2 @ -$1,500 = -$16,800
Net Profit:    $58,800
Monthly Return: 39.2%
```

### Met 50% winratio (conservatiever)

**Per Maand**:
```
Trades:        28
Wins:          14 @ $4,500 = $63,000
Losses:        14 @ -$1,500 = -$21,000
Net Profit:    $42,000
Monthly Return: 28%
```

---

## 🎯 Voordelen van 1 Positie Tegelijk

✅ **Maximale focus** op één trade
✅ **Lager risico** - max $1,500 exposure
✅ **Betere emotionele controle**
✅ **Eenvoudigere monitoring**
✅ **Geen correlatie risico** tussen posities

---

## ⚙️ Command Line Opties

```bash
python src/agents/mt5_agent_smc.py [OPTIONS]

Opties:
  --balance AMOUNT         Account balans (default: 10000)
  --interval MINUTES       Minuten tussen analyses (default: 15)
  --max-positions NUM      Max concurrent posities (default: 1 voor jouw setup)
  --live                   Live trading (default: paper trading)

Voorbeelden:

# Zeer frequent monitoren (elke 5 minuten)
python src/agents/mt5_agent_smc.py --balance 150000 --interval 5 --max-positions 1

# Standaard (elke 15 minuten)
python src/agents/mt5_agent_smc.py --balance 150000 --interval 15 --max-positions 1

# Minder frequent (elk uur)
python src/agents/mt5_agent_smc.py --balance 150000 --interval 60 --max-positions 1

# Live trading
python src/agents/mt5_agent_smc.py --live --balance 150000 --interval 15 --max-positions 1
```

---

## 📊 Wat Gebeurt Er?

### Elke 15 minuten:

1. **Account Check**
   - Balance: $150,000
   - Open posities: 0 of 1
   - Beschikbaar voor nieuwe trade: Ja/Nee

2. **Market Analyse** (EURUSD, GBPUSD, USDJPY)
   - SMC indicators detecteren
   - AI analyseert met qwen3-coder:30b
   - Confidence score berekenen

3. **Trade Beslissing**
   - Alleen als confidence > 75%
   - Alleen als 2+ SMC confluences
   - Alleen als WITH market structure
   - Alleen als geen open positie

4. **Positie Management**
   - Check open positie P/L
   - Take profit bij $4,500 (3R)
   - Stop loss bij -$1,500 (1R)

---

## 🎬 Voorbeeld Output

```bash
$ python src/agents/mt5_agent_smc.py --balance 150000 --interval 15 --max-positions 1

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
  SMC CYCLE 1 - 2025-01-15 10:00:00
██████████████████████████████████████████████████████████████████████

💰 Account Status:
  Balance: $150,000.00
  Equity: $150,000.00
  P/L: $0.00

🔍 SMC Analysis for EURUSD...

📊 SMC MARKET ANALYSIS - EURUSD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MARKET STRUCTURE: BULLISH
  - Trend: Higher Highs + Higher Lows
  - Confidence: 85%

ACTIVE IFVGs: 1
  🟢 BULLISH IFVG: 1.08234 - 1.08456

BREAKER BLOCKS: 1
  🔵 BULLISH BREAKER: 1.08123

🤔 AI analyzing with SMC context...
✅ Analysis complete in 7.8s

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
  Entry Price: 1.08450
  Stop Loss: 1.08150
  Take Profit: 1.09350
  Lot Size: 5.0
======================================================================

✅ SMC Trade executed! Ticket: 1

😴 Sleeping for 15 minutes...

[15 minutes later...]

██████████████████████████████████████████████████████████████████████
  SMC CYCLE 2 - 2025-01-15 10:15:00
██████████████████████████████████████████████████████████████████████

💰 Account Status:
  Balance: $150,000.00
  Equity: $150,250.00
  P/L: $250.00

📊 Managing 1 position(s)...

  Position 1:
    Symbol: EURUSD
    Type: BUY
    Entry: 1.08450
    P/L: $250.00
    Target: $4,500.00 | Stop: $-1,500.00

🔍 SMC Analysis for EURUSD...
⏸️  Max positions reached (1)

🔍 SMC Analysis for GBPUSD...
⏸️  Max positions reached (1)

🔍 SMC Analysis for USDJPY...
⏸️  Max positions reached (1)

😴 Sleeping for 15 minutes...
```

---

## 💡 Tips voor $150K Account

### 1. Start met Paper Trading
```bash
# Draai minimaal 2 weken in paper mode
python src/agents/mt5_agent_smc.py --balance 150000 --interval 15 --max-positions 1
```

### 2. Monitor Dagelijks
- Check trade history in `src/data/mt5_paper/paper_trades.json`
- Analyseer win rate
- Kijk naar gemiddelde win/loss ratio

### 3. Evalueer na 1 Maand
```python
import json
import pandas as pd

with open('src/data/mt5_paper/paper_trades.json') as f:
    data = json.load(f)

print(f"Starting: ${data['initial_balance']:,.2f}")
print(f"Current:  ${data['current_balance']:,.2f}")
print(f"Profit:   ${data['current_balance'] - data['initial_balance']:,.2f}")

trades = pd.DataFrame(data['trade_history'])
closed = trades[trades['status'] == 'CLOSED']

print(f"\nTrades: {len(closed)}")
print(f"Win Rate: {(closed['profit'] > 0).sum() / len(closed) * 100:.1f}%")
print(f"Avg Win: ${closed[closed['profit'] > 0]['profit'].mean():.2f}")
print(f"Avg Loss: ${closed[closed['profit'] < 0]['profit'].mean():.2f}")
```

### 4. Overgang naar Live
Als paper trading succesvol is (>50% win rate):
1. **Week 1-2**: Test met kleinere lot size (0.1-0.5 lots)
2. **Week 3-4**: Verhoog naar halve size (2.5 lots)
3. **Maand 2+**: Volle size (5.0 lots) als consistent winstgevend

---

## 🔒 Veiligheid

### Circuit Breakers
- **Max loss per trade**: $1,500 (1%)
- **Max daily loss**: $6,000 (4%)
- **Max positions**: 1 (jouw instelling)
- **Min confidence**: 75%
- **Stop loss**: Altijd ingesteld

### Best Practices
✅ Begin met paper trading
✅ Monitor dagelijks
✅ Evalueer wekelijks
✅ Pas lot size aan bij twijfel
✅ Stop bij 3 verliezen op rij (evalueer strategie)

---

## ❓ Veel Gestelde Vragen

**Q: Waarom 15 minuten interval?**
A: Balans tussen te veel en te weinig trades. 15 minuten geeft ~96 checks per dag, goed voor SMC scalping.

**Q: Kan ik vaker checken?**
A: Ja! Gebruik `--interval 5` voor elke 5 minuten (meer trades, meer AI calls).

**Q: Minder vaak?**
A: Gebruik `--interval 60` voor elk uur (minder trades, minder volatiel).

**Q: Waarom 1 positie tegelijk?**
A: Jouw voorkeur voor meer controle en focus. Minder risico, maar ook minder exposure.

**Q: Kan ik meer posities hebben?**
A: Ja! Verwijder `--max-positions 1` of gebruik `--max-positions 3` bijvoorbeeld.

**Q: Hoe stop ik de agent?**
A: Druk op `Ctrl+C` - de agent sluit netjes af en toont finale statistieken.

---

## 🌙 Volgende Stappen

1. **Installeer dependencies**
```bash
pip install -r requirements.txt
```

2. **Start Ollama** (in aparte terminal)
```bash
ollama serve
ollama pull qwen3-coder:30b
```

3. **Run de agent**
```bash
python src/agents/mt5_agent_smc.py --balance 150000 --interval 15 --max-positions 1
```

4. **Monitor en evalueer**
- Laat draaien voor 1-2 weken
- Analyseer resultaten
- Pas parameters aan indien nodig

5. **Overweeg live trading**
- Alleen als paper trading succesvol
- Begin met kleinere posities
- Scale geleidelijk op

---

**Succes met je $150K trading! 🚀**

*Voor vragen: check MT5_150K_ACCOUNT_SETUP.md voor meer details*

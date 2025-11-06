# 🚀 START HIER - MT5 Trading met Ollama

## ✅ De Oplossing: Ollama (Gratis Lokale AI)

**Je had helemaal gelijk!** De oplossing was om **Ollama** te gebruiken in plaats van OpenRouter.

---

## 📋 Wat Je Nu Moet Doen (5 minuten)

### Stap 1: Pull de Laatste Code
```bash
git pull origin claude/check-rbi-agent-sync-011CUr2WPY92uVwAtpiBnjwB
```

### Stap 2: Installeer Ollama
```
1. Download: https://ollama.com/download/windows
2. Run OllamaSetup.exe
3. Installatie duurt 30 seconden
```

### Stap 3: Download qwen3-vl Model
```bash
ollama pull qwen3-vl
```

**Download:** ~3GB (duurt 2-5 minuten)

### Stap 4: Start Trading!
```bash
start_mt5_trading.bat
```

**Klaar!** 🎉

---

## 🎯 Wat Ik Heb Geconfigureerd

### ✅ src/config.py
```python
AI_PRIMARY_TYPE = 'ollama'      # Lokale AI
AI_PRIMARY_MODEL = 'qwen3-vl'   # Vision & Language model
```

### ✅ .env
```bash
# Alleen MT5 credentials - geen API keys!
MT5_LOGIN=5041139909
MT5_PASSWORD=m44!YU6XYGXmMjf
MT5_SERVER=MetaQuotes-Demo
```

---

## 💡 Waarom Dit Werkt

**OpenRouter Problemen:**
- ❌ 403 Forbidden errors
- ❌ Account setup nodig
- ❌ Payment method nodig
- ❌ API keys management

**Ollama Oplossing:**
- ✅ **100% GRATIS** - Geen kosten
- ✅ **Geen API keys** - Draait lokaal
- ✅ **Geen account** - Direct gebruiken
- ✅ **Privé** - Data blijft lokaal
- ✅ **Geen limits** - Onbeperkt gebruik

---

## 🧪 Test je Setup

```bash
# 1. Check Ollama
ollama list
# Output: qwen3-vl

# 2. Test Ollama
ollama run qwen3-vl "Say hello"
# Output: Hello! How can I help you?

# 3. Test MT5 Setup
python test_mt5_setup.py
# Output: ✅ All tests passed!

# 4. Start Trading
start_mt5_trading.bat
```

---

## 📖 Volledige Documentatie

**OLLAMA_SOLUTION.md** - Complete guide met:
- Installatie instructies
- Model opties
- Troubleshooting
- Pro tips
- GPU versnelling

---

## 🎊 Verwachte Output

```
🌙 Moon Dev MT5 Trading Agent
══════════════════════════════

✅ MT5 Connected: Account 5041139909
   Balance: $10,000.00
   Server: MetaQuotes-Demo

✅ Ollama Loaded: qwen3-vl
   Model: Vision & Language (32B params)
   Status: Ready

📊 Analyzing Markets...

Symbol: EURUSD
  Price: 1.0567
  RSI: 58.3 (Neutral)
  MACD: Bullish crossover
  MA20: Above

🤖 AI Analysis:
  "Strong bullish momentum with healthy RSI.
   MACD showing fresh bullish crossover.
   Recommend BUY with SL at 1.0540."

💰 Decision: BUY EURUSD 0.01 lots
✅ Order Placed: Ticket #12345

🔄 Monitoring position...
```

---

## ⚡ Quick Commands

```bash
# Pull code
git pull

# Start Ollama
ollama serve  # (usually auto-starts)

# Test model
ollama run qwen3-vl "What is RSI?"

# Start trading
start_mt5_trading.bat

# Test setup
python test_mt5_setup.py

# Check diagnostics
python diagnose_openrouter.py  # (not needed anymore)
```

---

## 🆘 Hulp Nodig?

### Ollama draait niet:
```bash
# Windows: Check system tray voor Ollama icon
# Of herstart: Klik icon → Restart
```

### Model niet gevonden:
```bash
ollama list  # Check installed models
ollama pull qwen3-vl  # Re-download if needed
```

### Python errors:
```bash
# Check dependencies
pip install -r requirements.txt

# Check MT5 (Windows only)
pip install MetaTrader5
```

---

## 📂 Belangrijke Files

| File | Doel |
|------|------|
| **OLLAMA_SOLUTION.md** | Complete Ollama guide |
| **START_HERE.md** | Dit document |
| **test_mt5_setup.py** | Test script |
| **start_mt5_trading.bat** | Start trading |
| **src/config.py** | Configuratie |
| **.env** | Credentials |

---

## 🎯 TL;DR

```bash
# 1. Download Ollama
https://ollama.com/download

# 2. Download model
ollama pull qwen3-vl

# 3. Pull code
git pull

# 4. Start
start_mt5_trading.bat
```

**Klaar in 5 minuten!** 🚀

---

🌙 **Moon Dev AI Trading System**
**Powered by Ollama - 100% Free & Local**

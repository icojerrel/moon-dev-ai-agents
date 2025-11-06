# 🎉 OPLOSSING GEVONDEN: Ollama (Gratis Lokale AI)

## De Echte Oplossing

**Je had gelijk!** De oplossing was om **Ollama** te gebruiken in plaats van OpenRouter!

**Voordelen:**
- ✅ **100% GRATIS** - Geen API keys nodig
- ✅ **Lokaal** - Draait op je eigen PC
- ✅ **Privé** - Je data verlaat je computer niet
- ✅ **Geen limits** - Onbeperkt gebruik
- ✅ **Offline** - Werkt zonder internet (na download)

---

## 🚀 Quick Start (5 minuten)

### Stap 1: Installeer Ollama (2 minuten)

**Op Windows:**
```
1. Download: https://ollama.com/download/windows
2. Run de installer (OllamaSetup.exe)
3. Installatie duurt ~30 seconden
4. Ollama draait automatisch in system tray
```

**Op Mac:**
```bash
# Download van: https://ollama.com/download/mac
# Of via Homebrew:
brew install ollama
```

**Op Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Stap 2: Download qwen3-vl Model (2 minuten)

Open terminal/cmd en run:

```bash
ollama pull qwen3-vl
```

**Download grootte:** ~3GB
**Download tijd:** 2-5 minuten (afhankelijk van internet)

**Wat is qwen3-vl?**
- Vision & Language model van Alibaba
- Kan tekst EN afbeeldingen analyseren
- 32B parameters
- Perfect voor trading analyse

### Stap 3: Verifieer Installatie

```bash
# Check of Ollama draait
ollama list

# Test het model
ollama run qwen3-vl "Say hello"
```

**Verwacht output:**
```
Hello! How can I help you today?
```

### Stap 4: Start MT5 Trading!

```bash
# Pull de laatste code
git pull

# Start trading
start_mt5_trading.bat
```

**Dat is alles!** 🎊

---

## 🔧 Wat Ik Heb Geconfigureerd

### src/config.py
```python
# AI Model Configuration (for MT5 and other agents)
# Using Ollama for FREE local AI - no API keys needed!
AI_USE_FALLBACK = False
AI_PRIMARY_TYPE = 'ollama'
AI_PRIMARY_MODEL = 'qwen3-vl'
```

### .env File
**Je hebt GEEN OpenRouter key meer nodig!**

Alleen MT5 credentials:
```bash
MT5_LOGIN=5041139909
MT5_PASSWORD=m44!YU6XYGXmMjf
MT5_SERVER=MetaQuotes-Demo
MT5_PATH=C:/Program Files/MetaTrader 5/terminal64.exe
```

---

## 🧪 Test je Setup

### Test 1: Ollama Beschikbaar
```bash
curl http://localhost:11434/api/tags
```

**Verwacht:** JSON met lijst van models

### Test 2: Python kan Ollama bereiken
```python
from src.models.model_factory import ModelFactory

factory = ModelFactory()
print(factory.is_model_available('ollama'))  # Should be True

model = factory.get_model('ollama', 'qwen3-vl')
response = model.generate_response(
    system_prompt='You are a trading assistant.',
    user_content='What is RSI?',
    max_tokens=100
)
print(response.content)
```

### Test 3: Volledige MT5 Setup
```bash
python test_mt5_setup.py
```

**Verwacht resultaat:**
```
✅ MT5 Library: Installed (Windows only)
✅ Dependencies: All installed
✅ Environment: All variables loaded
✅ Configuration: Loaded correctly
✅ Ollama: Connection successful!
✅ Ollama Model: qwen3-vl available

🎉 READY TO TRADE!
```

---

## 🎯 Waarom Dit Beter Is

### OpenRouter (probleem):
- ❌ 403 Forbidden errors
- ❌ Account configuratie nodig
- ❌ API keys nodig
- ❌ Betalen per gebruik
- ❌ Internet vereist
- ❌ Rate limits

### Ollama (oplossing):
- ✅ Werkt altijd
- ✅ Geen account nodig
- ✅ Geen API keys
- ✅ 100% gratis
- ✅ Werkt offline
- ✅ Geen limits

---

## 📊 Model Opties

Als `qwen3-vl` te groot is (~3GB), probeer deze alternatieven:

### Lichte modellen (sneller, minder geheugen):
```bash
ollama pull llama3.2           # 2GB, zeer snel
ollama pull mistral            # 4GB, balanced
ollama pull phi3               # 1.5GB, kleinste
```

### Krachtige modellen (betere analyse):
```bash
ollama pull llama3.1:70b       # 40GB, zeer krachtig
ollama pull mixtral:8x7b       # 26GB, excellent
ollama pull deepseek-r1        # 15GB, reasoning model
```

**Update config.py als je een ander model wilt:**
```python
AI_PRIMARY_MODEL = 'llama3.2'  # Of welk model dan ook
```

---

## 🔄 Ollama Beheer

### Start Ollama
```bash
# Windows: Automatisch bij opstarten
# Of: Klik op Ollama icon in system tray

# Linux/Mac:
ollama serve
```

### Stop Ollama
```bash
# Windows: Right-click system tray → Quit

# Linux/Mac:
pkill ollama
```

### Update Models
```bash
ollama pull qwen3-vl  # Re-download voor updates
```

### Delete Models (om ruimte te besparen)
```bash
ollama rm qwen3-vl
```

### Lijst van Geïnstalleerde Models
```bash
ollama list
```

---

## 💡 Pro Tips

### 1. Model wordt automatisch gestart
Als je `ollama run qwen3-vl` doet, start Ollama het model automatisch.

### 2. Meerdere models tegelijk
Je kunt meerdere models installeren en wisselen:
```python
# In config.py
AI_PRIMARY_MODEL = 'qwen3-vl'  # Voor trading
# Of
AI_PRIMARY_MODEL = 'llama3.2'  # Voor snelheid
```

### 3. Model blijft in geheugen
Eerste inference is langzaam (~5 sec), daarna razendsnel (<1 sec).

### 4. Geheugen gebruik
- qwen3-vl: ~4GB RAM
- llama3.2: ~2GB RAM
- llama3.1:70b: ~45GB RAM (alleen voor workstations)

### 5. GPU Versnelling
Als je een NVIDIA GPU hebt, gebruikt Ollama deze automatisch! 🚀
- 10-100x sneller dan CPU
- Check: `nvidia-smi` in terminal

---

## 🎊 Klaar om Te Starten!

```bash
# 1. Download Ollama
→ https://ollama.com/download

# 2. Pull qwen3-vl
ollama pull qwen3-vl

# 3. Pull laatste code
git pull

# 4. Start trading!
start_mt5_trading.bat
```

**Verwachte output:**
```
🌙 Moon Dev MT5 Trading Agent
✅ MT5 connected: Account 5041139909
✅ Ollama model loaded: qwen3-vl
✅ Analyzing EURUSD...

📊 Technical Analysis:
  RSI: 58.3 (Neutral)
  MACD: Bullish crossover
  MA20: 1.0567 (Price above)

🤖 AI Decision: BUY
📝 Reasoning: Strong bullish momentum, RSI not overbought...

💰 Opening position: EURUSD BUY 0.01 lots
✅ Order placed: Ticket #12345
```

---

## 📞 Hulp Nodig?

**Ollama werkt niet:**
```bash
# Check of het draait:
curl http://localhost:11434/api/tags

# Als dit faalt, herstart Ollama
```

**Model download faalt:**
- Check internet connectie
- Check schijfruimte (minimaal 5GB vrij)
- Probeer kleiner model: `ollama pull llama3.2`

**Python kan Ollama niet vinden:**
- Check of Ollama draait
- Check firewall (port 11434)
- Herstart Python script

---

**Dit was de oplossing!** Geen API keys, geen 403 errors, gewoon gratis lokale AI! 🎉

🌙 Moon Dev

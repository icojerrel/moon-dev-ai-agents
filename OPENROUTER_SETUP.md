# 🌐 OpenRouter + Ollama Fallback Setup

Complete guide for using OpenRouter with automatic Ollama fallback for AI-powered trading.

---

## 🎯 Why OpenRouter + Ollama?

**OpenRouter** gives you access to **50+ AI models** through one unified API:
- ✅ Claude (Anthropic)
- ✅ GPT-4 (OpenAI)
- ✅ Gemini (Google)
- ✅ Llama (Meta)
- ✅ Mistral, DeepSeek, Qwen, and more!

**Ollama** provides **free local AI** as backup:
- ✅ Works offline
- ✅ No API costs
- ✅ Privacy (data stays local)
- ✅ Automatic fallback if OpenRouter fails

**Result**: Best of both worlds - Cloud AI quality with local reliability!

---

## 📋 Step 1: Get OpenRouter API Key (2 min)

1. Go to https://openrouter.ai/
2. Click "Sign Up" (Google/GitHub login works)
3. Go to https://openrouter.ai/keys
4. Click "Create Key"
5. Copy key (starts with `sk-or-v1-...`)
6. Add $5-10 credit: https://openrouter.ai/credits

**Pricing** (examples):
- Claude 3.5 Sonnet: $3/1M input tokens, $15/1M output
- GPT-4 Turbo: $10/1M input, $30/1M output
- Llama 3.1 70B: $0.52/1M input, $0.75/1M output (cheapest!)

💡 **Tip**: Start with $5 - goes a long way for trading bots!

---

## 📋 Step 2: Install Ollama (Local AI) (5 min)

### Windows:

1. Download: https://ollama.com/download/windows
2. Run installer: `OllamaSetup.exe`
3. Ollama starts automatically (runs in background)
4. Open PowerShell and test:
   ```bash
   ollama --version
   ```

5. Download a model:
   ```bash
   ollama pull llama3.2
   ```

6. Test it works:
   ```bash
   ollama run llama3.2 "Hello"
   ```

### Mac/Linux:

```bash
# Download and install
curl https://ollama.ai/install.sh | sh

# Pull model
ollama pull llama3.2

# Test
ollama run llama3.2 "Hello"
```

**Popular Models:**
- `llama3.2` (3B) - Fast, small, recommended for fallback
- `llama3.1` (8B) - Balanced
- `qwen2.5:7b` - Good for reasoning
- `deepseek-r1:7b` - Advanced reasoning

💡 **Tip**: Use `llama3.2` for trading - fast and reliable!

---

## 📋 Step 3: Configure .env File

Open `.env` (or run `create_env_file.bat` on Windows):

```bash
# OpenRouter API Key (Primary)
OPENROUTER_API_KEY=sk-or-v1-YOUR_ACTUAL_KEY_HERE

# MT5 Credentials
MT5_LOGIN=5041139909
MT5_PASSWORD=m44!YU6XYGXmMjf
MT5_SERVER=MetaQuotes-Demo
```

**That's it!** The system is pre-configured for OpenRouter → Ollama fallback.

---

## ⚙️ Step 4: Configure AI Model (Optional)

The system uses **smart defaults**, but you can customize in `src/config.py`:

```python
# AI Model Fallback Configuration
AI_USE_FALLBACK = True  # Enable fallback
AI_PRIMARY_TYPE = 'openrouter'  # Primary provider
AI_PRIMARY_MODEL = 'anthropic/claude-3.5-sonnet'  # OpenRouter model
AI_FALLBACK_TYPE = 'ollama'  # Fallback provider
AI_FALLBACK_MODEL = 'llama3.2'  # Local model
```

**Popular OpenRouter Models:**

```python
# Budget-friendly
AI_PRIMARY_MODEL = 'meta-llama/llama-3.1-70b-instruct'  # $0.52/1M tokens

# Balanced
AI_PRIMARY_MODEL = 'anthropic/claude-3.5-sonnet'  # $3/1M tokens (default)

# Premium
AI_PRIMARY_MODEL = 'openai/gpt-4-turbo'  # $10/1M tokens

# Specialized
AI_PRIMARY_MODEL = 'deepseek/deepseek-r1'  # Reasoning model
AI_PRIMARY_MODEL = 'perplexity/llama-3.1-sonar-large-128k-online'  # With internet
```

**List all models**: https://openrouter.ai/models

---

## 🚀 Step 5: Test the Setup

### Test OpenRouter Only:

```bash
python -c "from src.models.openrouter_model import OpenRouterModel; OpenRouterModel.list_popular_models()"
```

### Test Ollama Only:

```bash
ollama run llama3.2 "What are 3 key forex indicators?"
```

### Test Fallback System:

```bash
python -c "from src.models.fallback_model import create_openrouter_ollama_fallback; import os; model = create_openrouter_ollama_fallback(os.getenv('OPENROUTER_API_KEY')); print(model.generate_response('You are a trader', 'What is RSI?'))"
```

**Expected Output:**
```
🔧 Creating OpenRouter → Ollama Fallback
✨ Moon Dev's OpenRouter initialized: anthropic/claude-3.5-sonnet
✅ Fallback Model initialized: openrouter → ollama

🎯 Trying primary: openrouter
✅ Primary model succeeded (openrouter)
```

---

## 🎮 Step 6: Run MT5 Trading Bot

```bash
# Start trading
start_mt5_trading.bat
```

**What Happens:**

1. **OpenRouter tries first** (Claude 3.5 Sonnet by default)
   - Fast, intelligent trading analysis
   - Uses your API credits

2. **If OpenRouter fails** → **Ollama takes over** (Llama 3.2)
   - Free local processing
   - Still gets trading decisions
   - No interruption!

**Console Output:**
```
🔄 Initializing OpenRouter with Ollama fallback...
✨ Moon Dev's OpenRouter initialized: anthropic/claude-3.5-sonnet
   Claude 3.5 Sonnet - Best balanced model
✅ Fallback Model initialized: openrouter → ollama

📊 Analyzing EURUSD...
🎯 Trying primary: openrouter
🤔 OpenRouter anthropic/claude-3.5-sonnet is thinking...
✅ OpenRouter response received (487 chars)
✅ Primary model succeeded (openrouter)

🟢 BUY SIGNAL: EURUSD
   Price: 1.04567
   AI Reasoning: Bullish momentum confirmed...
```

---

## 📊 Monitor Usage & Statistics

The bot tracks which model is used:

```python
# In your trading agent
agent.model.print_statistics()
```

**Output:**
```
📊 OpenRouter→Ollama Statistics
==================================================
Total Requests: 48

Primary (openrouter):
  Attempts: 45
  Successes: 43
  Success Rate: 95.6%

Fallback (ollama):
  Attempts: 3
  Successes: 3
  Success Rate: 100.0%
==================================================
```

💡 **Insight**: OpenRouter handles 95%+ of requests. Ollama catches the rest!

---

## 💰 Cost Tracking

### OpenRouter Dashboard:
- https://openrouter.ai/activity
- Real-time usage tracking
- Cost per model/request

**Typical MT5 Bot Costs:**
- ~100 trading decisions/day
- ~500 tokens per decision
- **Claude 3.5 Sonnet**: ~$0.23/day
- **Llama 3.1 70B**: ~$0.04/day

**Monthly**: $1.20 - $7 depending on model

---

## 🔧 Troubleshooting

### "Failed to initialize OpenRouter"

**Check:**
1. API key in `.env` correct?
2. Have credits? → https://openrouter.ai/credits
3. Test key:
   ```bash
   curl https://openrouter.ai/api/v1/models \
     -H "Authorization: Bearer sk-or-v1-YOUR_KEY"
   ```

### "Ollama not available"

**Check:**
1. Ollama running?
   ```bash
   # Windows: Check system tray for Ollama icon
   # Mac/Linux:
   ps aux | grep ollama
   ```

2. Start Ollama:
   ```bash
   # Windows: Search "Ollama" in Start menu
   # Mac/Linux:
   ollama serve
   ```

3. Model downloaded?
   ```bash
   ollama list
   # If empty:
   ollama pull llama3.2
   ```

### "Insufficient credits"

Add credits: https://openrouter.ai/credits

Or temporarily use only Ollama:
```python
# src/config.py
AI_USE_FALLBACK = False
AI_PRIMARY_TYPE = 'ollama'
AI_PRIMARY_MODEL = 'llama3.2'
```

### "Both models failed"

1. Check OpenRouter key and credits
2. Check Ollama is running: `ollama list`
3. Check console for specific error
4. Test each model independently (see Step 5)

---

## 🎯 Best Practices

### For Production Trading:

1. **Use OpenRouter primary** - Better analysis quality
2. **Keep Ollama running** - Instant fallback
3. **Monitor costs** - Set alerts on OpenRouter
4. **Test fallback** - Manually stop Ollama to verify OpenRouter works
5. **Review statistics** - Check fallback usage patterns

### Model Selection:

**Fast + Cheap:**
```python
AI_PRIMARY_MODEL = 'meta-llama/llama-3.1-8b-instruct'  # $0.12/1M
AI_FALLBACK_MODEL = 'llama3.2'
```

**Balanced (Default):**
```python
AI_PRIMARY_MODEL = 'anthropic/claude-3.5-sonnet'  # $3/1M
AI_FALLBACK_MODEL = 'llama3.2'
```

**Premium:**
```python
AI_PRIMARY_MODEL = 'openai/gpt-4-turbo'  # $10/1M
AI_FALLBACK_MODEL = 'llama3.1'  # Larger fallback
```

---

## 📚 Additional Resources

- **OpenRouter Docs**: https://openrouter.ai/docs
- **OpenRouter Models**: https://openrouter.ai/models
- **Ollama Models**: https://ollama.com/library
- **Ollama Docs**: https://github.com/ollama/ollama

---

## 🎉 You're Ready!

**Setup Summary:**
- ✅ OpenRouter API key added
- ✅ Ollama installed and running
- ✅ Model downloaded (`llama3.2`)
- ✅ `.env` configured
- ✅ Fallback tested

**Start Trading:**
```bash
start_mt5_trading.bat
```

**Watch the magic:**
- OpenRouter analyzes markets with Claude/GPT-4
- If internet drops → Ollama takes over locally
- Trading never stops! 🚀

Built with 🌙 by Moon Dev

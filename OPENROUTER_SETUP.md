# 🌙 OpenRouter-Only Setup Guide

## ✅ ONE API KEY FOR ALL AI MODELS

This repository is configured to use **OpenRouter exclusively** for all AI model access. This means you only need **ONE API key** instead of managing 6+ separate provider keys.

---

## 🚀 Quick Setup (3 Steps)

### 1. Get Your OpenRouter API Key

Visit: **https://openrouter.ai/keys**

- Create an account (free)
- Generate an API key (starts with `sk-or-v1-...`)
- Add credits to your account: https://openrouter.ai/credits

### 2. Add to `.env` File

```bash
# Copy the example file
cp .env_example .env

# Edit .env and add your key
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

### 3. Start Using!

```python
from src.models.model_factory import ModelFactory

factory = ModelFactory()

# Use ANY model through OpenRouter
model = factory.get_model("openrouter", "deepseek/deepseek-r1")
response = model.generate_response(
    system_prompt="You are a trading expert.",
    user_content="Analyze this momentum strategy...",
    temperature=0.7
)

print(response.content)
```

---

## 💰 Why OpenRouter?

### Cost Savings

| Provider | Direct API | Via OpenRouter | Savings |
|----------|-----------|----------------|---------|
| Claude 3.5 Sonnet | $3/$15 | $3/$15 | Same |
| GPT-4o | $2.50/$10 | $2.50/$10 | Same |
| DeepSeek R1 | $0.55/$2.19 | $0.55/$2.19 | Same |
| Gemini 2.5 Flash | $0.10/$0.40 | $0.10/$0.40 | Same |

**Often CHEAPER or same price as direct API!**

### Other Benefits

✅ **Single dashboard** - Track all model usage in one place
✅ **No subscriptions** - Pay-as-you-go credits only
✅ **Automatic fallbacks** - If one model is down, try another
✅ **100+ models** - Access to every major AI model
✅ **Unified API** - Same code works for all models
✅ **Better rate limits** - Pool limits across all models

---

## 🤖 Recommended Models

### For Trading Strategies (Best Value)

```python
# DeepSeek R1 - Best for reasoning, cheapest
model = factory.get_model("openrouter", "deepseek/deepseek-r1")
# Cost: $0.55/$2.19 per 1M tokens

# Kimi K2-0905 - 256k context, great for long documents
model = factory.get_model("openrouter", "moonshotai/kimi-k2-0905")
# Cost: $1/$3 per 1M tokens
```

### For Fast Inference

```python
# Gemini 2.5 Flash - Fastest, cheapest
model = factory.get_model("openrouter", "google/gemini-2.5-flash")
# Cost: $0.10/$0.40 per 1M tokens

# GPT-4o Mini - Fast OpenAI model
model = factory.get_model("openrouter", "openai/gpt-4o-mini")
# Cost: $0.15/$0.60 per 1M tokens
```

### For Complex Tasks

```python
# Claude 3.5 Sonnet - Best balanced model
model = factory.get_model("openrouter", "anthropic/claude-3.5-sonnet")
# Cost: $3/$15 per 1M tokens

# GPT-4o - Strong reasoning
model = factory.get_model("openrouter", "openai/gpt-4o")
# Cost: $2.50/$10 per 1M tokens
```

### For Coding

```python
# Kimi K2-0905 - Top coding model, 256k context
model = factory.get_model("openrouter", "moonshotai/kimi-k2-0905")
# Cost: $1/$3 per 1M tokens

# Claude 3.5 Sonnet - Excellent for code
model = factory.get_model("openrouter", "anthropic/claude-3.5-sonnet")
# Cost: $3/$15 per 1M tokens
```

---

## 📊 All Available Models (25 Total)

Full list with specs in: `src/models/openrouter_model.py`

**Providers:**
- 🔵 OpenAI (GPT-4o, GPT-5, O1 family)
- 🟣 Anthropic (Claude 3.x, 4.5 family)
- 🔴 Google (Gemini 2.5)
- 🟢 DeepSeek (R1, Chat)
- 🟡 Meta (Llama 3.3)
- ⚫ xAI (Grok 2)
- 🔵 Moonshot AI (Kimi K2-0905)
- 🟠 Mistral, Cohere, GLM

---

## 🧪 Testing

### Test All Setup

```bash
# Test OpenRouter connection
python3 test_openrouter_simple.py

# Test specific models
python3 test_openrouter.py

# Test Kimi K2-0905
python3 test_kimi_model.py
```

### Test in Code

```python
from src.models.model_factory import ModelFactory

factory = ModelFactory()

# Check if OpenRouter is available
if factory.is_model_available("openrouter"):
    print("✅ OpenRouter is ready!")
else:
    print("❌ OpenRouter not configured")
```

---

## ⚠️ Troubleshooting

### "Access denied" Error

**Cause:** No credits in OpenRouter account
**Fix:** Add credits at https://openrouter.ai/credits

### "API key not found"

**Cause:** OPENROUTER_API_KEY not set in `.env`
**Fix:**
```bash
# Make sure .env file exists
ls -la .env

# Check if key is set
grep OPENROUTER_API_KEY .env
```

### "Model not found"

**Cause:** Wrong model name format
**Fix:** Use provider/model format:
- ✅ `"openrouter", "deepseek/deepseek-r1"`
- ❌ `"deepseek", "deepseek-r1"`

---

## 🔄 Migration from Direct APIs

If you were using individual provider keys before:

### OLD Way (Multiple Keys)
```python
# Required 6+ API keys in .env:
# ANTHROPIC_KEY, OPENAI_KEY, DEEPSEEK_KEY, etc.

from src.models.model_factory import ModelFactory
factory = ModelFactory()

# Each provider needed separate key
claude = factory.get_model("claude", "claude-3-5-sonnet")
gpt = factory.get_model("openai", "gpt-4o")
deepseek = factory.get_model("deepseek", "deepseek-r1")
```

### NEW Way (One Key)
```python
# Only need 1 API key in .env:
# OPENROUTER_API_KEY

from src.models.model_factory import ModelFactory
factory = ModelFactory()

# All models through OpenRouter
claude = factory.get_model("openrouter", "anthropic/claude-3.5-sonnet")
gpt = factory.get_model("openrouter", "openai/gpt-4o")
deepseek = factory.get_model("openrouter", "deepseek/deepseek-r1")
```

**Benefits:**
- ✅ 1 API key instead of 6+
- ✅ 1 billing dashboard
- ✅ Same or cheaper pricing
- ✅ Automatic fallbacks
- ✅ Better rate limits

---

## 💡 Pro Tips

### 1. Start Cheap
```python
# Use DeepSeek R1 for development/testing
model = factory.get_model("openrouter", "deepseek/deepseek-r1")
# Only $0.55/$2.19 per 1M tokens!
```

### 2. Use Swarm Agent for Consensus
```python
# Get multiple model opinions (uses OpenRouter)
from src.agents.swarm_agent import SwarmAgent

swarm = SwarmAgent()
results = swarm.query("Should I enter this trade?")
# Queries 6+ models in parallel, generates consensus
```

### 3. Monitor Costs
Check usage at: https://openrouter.ai/activity

### 4. Set Budget Limits
Configure spending limits at: https://openrouter.ai/settings

---

## 🌙 Built with Love by Moon Dev

Need help?
- GitHub: https://github.com/moondevonyt/moon-dev-ai-agents
- YouTube: https://youtube.com/@moondevonyt

Happy trading! 🚀

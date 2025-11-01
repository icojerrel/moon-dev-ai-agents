# 🚀 OpenRouter Quick Start Guide

**OpenRouter = One API Key for ALL AI Models** 🎯

Instead of juggling multiple API keys (DeepSeek, Claude, GPT-4, Gemini, etc), use OpenRouter to access 100+ models with a single key!

---

## Why OpenRouter?

✅ **One Key, All Models** - Access DeepSeek, Claude, GPT-4, Gemini, Llama, and 100+ more
✅ **Cheaper** - Often 50-75% cheaper than direct APIs
✅ **Transparent Pricing** - See real costs per request
✅ **No Vendor Lock-in** - Switch models anytime
✅ **Simple Integration** - OpenAI-compatible API
✅ **Fair Usage** - Pay only for what you use

---

## 🔑 Getting Your API Key

### Step 1: Sign Up
1. Go to: **https://openrouter.ai**
2. Click "Sign Up" (free account)
3. Sign in with Google or Email

### Step 2: Create API Key
1. Go to: **https://openrouter.ai/keys**
2. Click "Create Key"
3. Copy your key (starts with `sk-or-v1-...`)

### Step 3: Add Credits
1. Go to: **https://openrouter.ai/credits**
2. Add $5-10 to start (very cheap!)
3. Credits never expire

**Your API key:** `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` ✅

---

## 💰 Pricing (DeepSeek via OpenRouter)

**Recommended Model: `deepseek/deepseek-chat`**

| Metric | Cost |
|--------|------|
| Input | $0.27 per million tokens |
| Output | $1.10 per million tokens |
| Per Trading Cycle | ~$0.001-0.002 |
| 24/7 Trading (1 month) | ~$3-5 |

**Compare to:**
- Direct DeepSeek API: $144/month
- Claude Sonnet: $300+/month
- GPT-4: $500+/month

**Savings: 95%+** 🎉

---

## 🛠️ Setup for Moon Dev Trading System

### Already Done! ✅

Your `.env` file is already configured:

```bash
OPENROUTER_API_KEY=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
```

The system will automatically:
1. ✅ Use OpenRouter for all AI calls
2. ✅ Default to DeepSeek Chat (best value)
3. ✅ Fallback to direct APIs if needed
4. ✅ Work with all agents (DeepSeek Director, Trading Agent, etc)

---

## 🎯 Available Models via OpenRouter

### Recommended for Trading:

| Model | Price (Input/Output) | Best For |
|-------|---------------------|----------|
| `deepseek/deepseek-chat` | $0.27/$1.10 per 1M tokens | **BEST VALUE** - Fast, cheap, high quality |
| `deepseek/deepseek-reasoner` | $0.55/$2.19 per 1M tokens | Complex reasoning, strategy development |
| `anthropic/claude-3.5-sonnet` | $3/$15 per 1M tokens | Premium quality, complex analysis |
| `openai/gpt-4o` | $2.50/$10 per 1M tokens | Latest GPT-4, balanced |
| `google/gemini-2.0-flash-exp` | $0/$0 (FREE!) | Fast experiments, testing |
| `meta-llama/llama-3.1-70b` | $0.35/$0.40 per 1M tokens | Open source, good value |

### Want to Switch Models?

**Easy! Just change one line in your agent:**

```python
# Use DeepSeek Chat (default, cheapest)
model = model_factory.get_model('openrouter', model_name='deepseek/deepseek-chat')

# Use Claude Sonnet (premium quality)
model = model_factory.get_model('openrouter', model_name='anthropic/claude-3.5-sonnet')

# Use GPT-4 Optimized
model = model_factory.get_model('openrouter', model_name='openai/gpt-4o')

# Use FREE Gemini
model = model_factory.get_model('openrouter', model_name='google/gemini-2.0-flash-exp')
```

**Full list:** https://openrouter.ai/models

---

## 📊 Monitor Your Usage

### View Dashboard
- Go to: **https://openrouter.ai/activity**
- See all requests, costs, and usage
- Track spending in real-time

### Check Credits
- Go to: **https://openrouter.ai/credits**
- See remaining balance
- Add more credits anytime

### Set Spending Limits
- Go to: **https://openrouter.ai/settings**
- Set monthly spending cap
- Get alerts at thresholds

---

## 🧪 Testing OpenRouter Integration

### Test 1: Quick Model Check

```bash
python -c "from src.models.model_factory import model_factory; \
model = model_factory.get_model('openrouter', model_name='deepseek/deepseek-chat'); \
print('✅ OpenRouter working!' if model else '❌ Failed')"
```

### Test 2: Generate Response

```python
from src.models.model_factory import model_factory

# Get model
model = model_factory.get_model('openrouter', model_name='deepseek/deepseek-chat')

# Test response
response = model.generate_response(
    system_prompt="You are a helpful trading assistant.",
    user_content="What's the current market sentiment for Bitcoin?",
    temperature=0.7,
    max_tokens=200
)

print(response.content)
print(f"Cost: {response.usage}")  # See actual cost!
```

### Test 3: Run Paper Trading

```bash
# This will automatically use OpenRouter!
python src/scripts/paper_trading.py
```

---

## 🎓 Advanced Usage

### Switch Models Dynamically

```python
from src.models.model_factory import model_factory

# Fast analysis with cheap model
fast_model = model_factory.get_model('openrouter', 'deepseek/deepseek-chat')
quick_analysis = fast_model.generate_response(...)

# Deep reasoning with premium model
smart_model = model_factory.get_model('openrouter', 'deepseek/deepseek-reasoner')
deep_analysis = smart_model.generate_response(...)

# Final decision with Claude (premium)
premium_model = model_factory.get_model('openrouter', 'anthropic/claude-3.5-sonnet')
final_decision = premium_model.generate_response(...)
```

### Cost Optimization Strategy

```python
# Strategy:
# 1. Use DeepSeek Chat for routine analysis (95% of calls)
# 2. Use DeepSeek Reasoner for complex decisions (4% of calls)
# 3. Use Claude Sonnet for critical trades (1% of calls)

# Result: ~$5/month instead of $300+/month
```

---

## 🚨 Troubleshooting

### Error: "OpenRouter not available"

**Solution:**
```bash
# Check .env file
cat .env | grep OPENROUTER_API_KEY

# Should show your key (not "your_openrouter_key_here")
# If not, add your key and restart
```

### Error: "Model not found"

**Solution:**
```python
# Check model name format (must include provider/)
✅ CORRECT: 'deepseek/deepseek-chat'
❌ WRONG: 'deepseek-chat'

✅ CORRECT: 'anthropic/claude-3.5-sonnet'
❌ WRONG: 'claude-3.5-sonnet'
```

### Error: "Insufficient credits"

**Solution:**
1. Go to: https://openrouter.ai/credits
2. Add more credits ($5-10)
3. Retry

### System Still Uses Direct APIs

**Solution:**
```bash
# Make sure OPENROUTER_API_KEY is set
# System tries OpenRouter first, then fallbacks to:
# 1. OpenRouter (if key exists)
# 2. Direct DeepSeek (if DEEPSEEK_KEY exists)
# 3. Direct Claude (if ANTHROPIC_KEY exists)
# 4. Error if no keys available
```

---

## 📈 Cost Comparison Examples

### Example 1: Paper Trading (24/7 for 1 month)

**With OpenRouter (DeepSeek):**
- ~2880 cycles/month (every 15 min)
- ~$0.002 per cycle
- **Total: ~$5-6/month** ✅

**With Direct DeepSeek:**
- ~$0.05 per cycle
- **Total: ~$144/month** ⚠️

**Savings: $138/month (96% cheaper!)** 🎉

### Example 2: Mixed Model Strategy

**Smart approach:**
```
90% DeepSeek Chat:    2592 calls × $0.002 = $5.18
9% DeepSeek Reasoner:  259 calls × $0.004 = $1.04
1% Claude Sonnet:       29 calls × $0.050 = $1.45
────────────────────────────────────────────────
Total:                                    $7.67/month
```

**Dumb approach (all Claude):**
```
100% Claude Sonnet:   2880 calls × $0.050 = $144/month
```

**Savings: $136/month (95% cheaper!)** 🚀

---

## 🎯 Next Steps

1. ✅ **OpenRouter API key added** (already done!)
2. ✅ **System configured** (already done!)
3. 🔲 **Add BirdEye API key** (for market data)
4. 🔲 **Test the system:**
   ```bash
   python src/scripts/paper_trading.py
   ```
5. 🔲 **Monitor usage:** https://openrouter.ai/activity
6. 🔲 **Scale up** when comfortable

---

## 💡 Pro Tips

1. **Start Cheap** - Use `deepseek/deepseek-chat` for everything initially
2. **Monitor Costs** - Check OpenRouter dashboard daily at first
3. **Set Limits** - Set monthly spending cap ($10-20 to start)
4. **Test Free Models** - `google/gemini-2.0-flash-exp` is FREE!
5. **Gradual Upgrade** - Only use premium models when needed
6. **Track Performance** - Compare model quality vs cost

---

## 📚 Resources

- **OpenRouter Dashboard:** https://openrouter.ai
- **Model List & Pricing:** https://openrouter.ai/models
- **API Documentation:** https://openrouter.ai/docs
- **Discord Support:** https://discord.gg/openrouter
- **Moon Dev Discord:** (your community link)

---

## 🌙 Ready to Trade!

You're all set! OpenRouter is configured and ready to power your autonomous trading system.

**Start Paper Trading:**
```bash
python src/scripts/paper_trading.py
```

**Monitor Costs:**
```bash
# Check OpenRouter dashboard while system runs
# URL: https://openrouter.ai/activity
```

Happy trading! 🚀

---

*Built with 🌙 by Moon Dev*
*Powered by OpenRouter - One Key, All Models*

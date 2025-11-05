# ✅ Setup Complete - MT5 Trading Bot with OpenRouter

**Date:** November 5, 2025
**Status:** CONFIGURED & READY FOR TESTING

---

## 🎉 What's Been Set Up

### 1. **MT5 Demo Account** ✅

```
Account:  [Configured in .env]
Password: [Configured in .env]
Server:   MetaQuotes-Demo
Type:     DEMO (risk-free testing)
```

**Status:** ✅ Fully configured in `.env`

### 2. **OpenRouter AI Integration** ✅

```
API:      OpenRouter unified API
Key:      [YOUR_KEY_HERE] (get from OpenRouter)
Primary:  DeepSeek Chat V3 (powerful & affordable)
Fallback: Claude Sonnet 4.5 (reliable)
```

**Available Models via OpenRouter:**
- 🤖 Claude (Anthropic): 3.5 Sonnet, 3.5 Haiku
- 🧠 GPT-4 (OpenAI): GPT-4o, GPT-4o-mini, O1-mini
- 🌟 Gemini (Google): Pro 1.5, Flash 1.5
- 🦙 Llama (Meta): 3.3 70B Instruct
- 💎 DeepSeek: R1, Chat V3
- ⚡ Mistral: Large
- 200+ more models available!

**Dashboard:** https://openrouter.ai/

### 3. **Trading Configuration** ⚙️

```python
MT5_ENABLED = True                    # Agent enabled
MT5_MAX_POSITIONS = 1                 # Max 1 position (strict risk)
MT5_MAX_POSITION_SIZE = 1.0           # 1.0 lots max
MT5_MIN_CONFIDENCE = 75               # 75% AI confidence required

# Trading Hours Filter
MT5_USE_TRADING_HOURS_FILTER = True   # Only trade optimal hours
MT5_STRICT_HOURS = True               # Best hours only
```

**Optimal Trading Hours:**
- Forex: London/NY overlap (13:00-17:00 UTC / 14:00-18:00 NL)
- Gold: NY session (13:00-20:00 UTC)
- Indices: Mid-day (15:00-20:00 UTC)
- Stocks: Mid-day (15:30-19:30 UTC)

### 4. **Starting Balance** 💰

```
SANDBOX_STARTING_BALANCE = 150,000
```

Virtual 150k for realistic demo testing.

### 5. **Security** 🔒

- ✅ `.env` file protected by `.gitignore`
- ✅ Credentials never committed to git
- ✅ Demo account only (no real money risk)
- ✅ Read-only password available

---

## 📋 What You Need to Do Next

### **STEP 1: Check OpenRouter Credits** 🔑

The OpenRouter API test showed "Access denied". This usually means:

1. **No credits on account**
   - Go to: https://openrouter.ai/credits
   - Add credits ($5-10 is plenty for testing)
   - DeepSeek V3 costs: ~$0.27 per 1M tokens (very cheap!)

2. **API key not active**
   - Go to: https://openrouter.ai/settings/keys
   - Check if key is enabled
   - Regenerate if needed

3. **Rate limits**
   - Check usage dashboard
   - May need to wait if limits hit

**Action:** Add $5-10 credits to OpenRouter account

### **STEP 2: Test OpenRouter Connection** 🧪

Once credits are added, test AI integration:

```bash
python -c "
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv('OPENROUTER_API_KEY'),
    base_url='https://openrouter.ai/api/v1',
    default_headers={
        'HTTP-Referer': 'https://moon.dev',
        'X-Title': 'Moon Dev Trading Bot'
    }
)

response = client.chat.completions.create(
    model='deepseek/deepseek-chat-v3-0324',
    messages=[
        {'role': 'system', 'content': 'You are a trading assistant.'},
        {'role': 'user', 'content': 'Say hello in 5 words.'}
    ],
    max_tokens=50
)

print(f'✅ AI Response: {response.choices[0].message.content}')
print('🎉 OpenRouter works!')
"
```

**Expected:** AI greeting in 5 words

### **STEP 3: Test MT5 Connection** 💹

**IMPORTANT:** MetaTrader 5 Python library only works on **Windows**.

If on Windows:

```bash
# Install MT5 package
pip install MetaTrader5

# Test connection
python -c "
import MetaTrader5 as mt5
import os
from dotenv import load_dotenv

load_dotenv()

if mt5.initialize():
    print('✅ MT5 initialized!')

    login = int(os.getenv('MT5_LOGIN'))
    password = os.getenv('MT5_PASSWORD')
    server = os.getenv('MT5_SERVER')

    if mt5.login(login, password, server):
        account = mt5.account_info()
        print(f'✅ Account: {account.login}')
        print(f'💰 Balance: {account.balance} {account.currency}')
        print(f'💵 Equity: {account.equity}')
    else:
        print('❌ Login failed')

    mt5.shutdown()
else:
    print('❌ MT5 initialize failed')
"
```

**Expected:**
```
✅ MT5 initialized!
✅ Account: [your account number]
💰 Balance: 10000.00 USD
💵 Equity: 10000.00
```

If on Linux/Mac:
- Use Windows VM or VPS
- Or use broker's web-based MT5 for manual testing
- Python code will run on Windows deployment

### **STEP 4: Setup Telegram Alerts** 📱 (Highly Recommended)

Get real-time trade notifications on your phone:

```bash
# 1. Open Telegram, search @BotFather
# 2. Send: /newbot
# 3. Name: "MT5 Trading Bot"
# 4. Username: "my_mt5_trading_bot"
# 5. Copy TOKEN from BotFather
# 6. Start chat with your bot
# 7. Search @userinfobot, send message
# 8. Copy your CHAT_ID
```

Then update `.env`:
```bash
TELEGRAM_ALERTS_ENABLED=true
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_CHAT_ID=123456789
```

**Benefits:**
- See every trade decision in real-time
- Get alerts on errors/issues
- Monitor bot remotely
- Free to use!

### **STEP 5: Run Trading Hours Filter Test** 🕐

Test the intelligent trading hours system:

```bash
python src/utils/trading_hours.py
```

**Expected output:**
```
📊 Current Session Info:
  session: London/NY Overlap (or current session)
  current_time_nl: 2025-11-05 17:51:10 CET/CEST

🕐 Optimal Trading Times (STRICT mode):
✅ FOREX      - ✅ London/NY Overlap - BEST forex hours
✅ METALS     - ✅ London/NY Overlap - BEST gold hours
✅ INDICES    - ✅ US indices optimal hours
```

### **STEP 6: Run MT5 Agent (Test Mode)** 🚀

Once OpenRouter works and MT5 connects, test the agent:

```bash
python src/agents/mt5_trading_agent.py
```

**What it will do:**
1. Show current market session
2. Check account balance
3. Analyze configured symbols (EURUSD, GBPUSD, etc.)
4. Check if trading hours are optimal
5. Get AI analysis of markets
6. Suggest trades (won't execute without your confirmation)

**Expected output:**
```
🌙 MT5 Trading Agent - Analysis Cycle
============================================================

🕐 Market Session: London/NY Overlap
⏰ Time (UTC): 2025-11-05 16:51:10 UTC
🇳🇱 Time (NL):  2025-11-05 17:51:10 CET/CEST
📅 Day: Wednesday

💰 Account Balance: 10000.00 USD
💵 Equity: 10000.00 USD

🔍 Analyzing EURUSD...
✅ 💱 EUR/USD (forex): ✅ London/NY Overlap - BEST forex hours
[AI analysis follows...]
```

---

## 🛠️ Configuration Files

### **`.env`** (Your Local Config - NOT committed to git)

```bash
# MT5 Credentials
MT5_LOGIN=your_mt5_account_number
MT5_PASSWORD=your_mt5_password
MT5_SERVER=MetaQuotes-Demo

# OpenRouter AI
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Telegram (optional but recommended)
TELEGRAM_ALERTS_ENABLED=false
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

### **`src/config.py`** (Global Settings - Committed to git)

```python
# MT5 Trading
MT5_ENABLED = True
MT5_MAX_POSITIONS = 1  # Maximum 1 position at a time
MT5_MODEL_TYPE = 'openrouter'
MT5_MODEL_NAME = 'deepseek/deepseek-chat-v3-0324'
MT5_FALLBACK_MODEL = 'anthropic/claude-sonnet-4.5'

# Trading Hours Filter
MT5_USE_TRADING_HOURS_FILTER = True
MT5_STRICT_HOURS = True

# Sandbox
SANDBOX_STARTING_BALANCE = 150000
```

---

## 📊 Configured Symbols

Currently monitoring:

**Forex:**
- EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, NZDUSD

**Metals:**
- XAUUSD (Gold)

**Indices:**
- US30, NAS100, SPX500

**Stocks:** (Optional)
- AAPL, MSFT, GOOGL

You can edit these in `src/config.py`:
```python
MT5_FOREX_PAIRS = ['EURUSD', 'GBPUSD', ...]
MT5_METALS = ['XAUUSD']
MT5_INDICES = ['US30', 'NAS100', 'SPX500']
```

---

## 🔥 Key Features Enabled

### 1. **Multi-Model AI via OpenRouter**
- Switch between 200+ models instantly
- Cost optimization per task
- Automatic fallback on errors
- Single API for all providers

### 2. **Intelligent Trading Hours Filter**
- Only trades during high volatility
- Asset-specific optimal hours
- Avoids weekend gaps
- Avoids Monday/Friday risks

### 3. **Strict Risk Management**
- Maximum 1 position at a time
- AI confidence threshold (75%+)
- Stop loss/take profit on every trade
- Asset-specific position sizing

### 4. **Multi-Asset Support**
- Forex pairs (major)
- Precious metals (gold, silver)
- Stock indices (US30, NAS100, SPX500)
- Individual stocks (optional)

### 5. **Netherlands Timezone Display**
- Shows UTC and Dutch time (CET/CEST)
- Daylight saving automatic
- Easy to understand session times

---

## 💰 Cost Estimates

### **OpenRouter Costs:**

**DeepSeek Chat V3** (Primary model):
- Input: $0.27 per 1M tokens
- Output: $1.10 per 1M tokens
- ~$0.50 per day of 24/7 trading (estimated)
- ~$15/month for continuous operation

**Claude Sonnet 4.5** (Fallback - if DeepSeek fails):
- Input: $3.00 per 1M tokens
- Output: $15.00 per 1M tokens
- Only used on primary model errors

**Recommendation:** Start with $10 credits for testing

### **MT5 Demo Account:**
- **FREE** ✅
- No real money at risk
- Perfect for learning and testing

---

## 🚨 Important Notes

### **Demo Account Only**
- This is a DEMO account
- Virtual money only
- No real financial risk
- Perfect for testing and learning

### **Windows Requirement for MT5**
- MetaTrader5 Python library requires Windows
- For Linux/Mac: use Windows VM or deploy to Windows VPS
- Alternative: Use broker web platform manually

### **OpenRouter Credits**
- Need to add credits before AI works
- Very affordable ($5-10 for extensive testing)
- Pay-as-you-go (no subscriptions)

### **Trading Hours Filter**
- System will skip trades during low-volatility
- This is GOOD - better trade quality
- Don't disable unless testing

### **Max 1 Position Limit**
- Strict risk control
- Prevents over-exposure
- Can be changed in config (not recommended for beginners)

---

## 📚 Documentation Files

- `TRADING_HOURS_INTEGRATION.md` - Trading hours system guide
- `MULTI_ASSET_TRADING.md` - Multi-asset setup guide
- `MT5_README.md` - MT5 integration guide
- `PRODUCTION_DEPLOY.md` - Deployment guide
- `src/models/README.md` - Model factory documentation

---

## 🎯 Quick Start Checklist

- [x] MT5 credentials configured
- [x] OpenRouter API key added
- [x] MT5 enabled in config
- [x] Trading hours filter configured
- [x] Starting balance set (150k)
- [x] DeepSeek V3 + Claude fallback configured
- [ ] Add OpenRouter credits ($5-10)
- [ ] Test OpenRouter connection
- [ ] Test MT5 connection (on Windows)
- [ ] Setup Telegram alerts (optional)
- [ ] Run trading hours test
- [ ] Run MT5 agent test

---

## 🚀 Ready to Go!

Your system is **configured and ready**. Just need:

1. **Add credits to OpenRouter** ($5-10)
2. **Test on Windows** (for MT5 Python library)
3. **Optional: Setup Telegram alerts**

Then run:
```bash
python src/agents/mt5_trading_agent.py
```

And watch your AI trading assistant analyze the markets! 🤖📈

---

## 🆘 Troubleshooting

### "OpenRouter Access Denied"
→ Add credits at https://openrouter.ai/credits

### "MT5 initialize failed"
→ Must run on Windows, or use Windows VM

### "All symbols skipped"
→ Outside optimal trading hours (this is normal!)

### "No AI models available"
→ Check OPENROUTER_API_KEY in .env

---

**Built with ❤️ by Moon Dev 🌙**

*Trade smarter with AI - Only during optimal market conditions!*

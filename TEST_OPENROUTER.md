# 🧪 OpenRouter Testing Guide

**Voor:** Lokale machine (Windows/Mac/Linux zonder IP block)
**Doel:** Testen of OpenRouter + DeepSeek V3 werkt na de fixes

---

## 📋 Pre-Test Checklist

- [ ] Git repo up-to-date: `git pull origin claude/continue-work-011CUq1JWCHDeiRR6WoX9U33`
- [ ] `.env` file aanwezig met OpenRouter key
- [ ] Python dependencies: `pip install -r requirements.txt` (of essentials)
- [ ] MT5 account credentials in `.env`

---

## 🧪 Test 1: Basis OpenRouter Connectie (30 sec)

**Script:** `tests/test_openrouter_basic.py`

```bash
python tests/test_openrouter_basic.py
```

**Verwacht:**
```
🧪 Testing OpenRouter Basic Connection...

1. Loading environment...
   ✅ OPENROUTER_API_KEY found

2. Testing OpenRouter with DeepSeek V3...
   📡 Sending request...
   ✅ Response received!

   AI said: "Hello! I'm ready to assist with your trading analysis."

   Model: deepseek/deepseek-chat-v3-0324
   Tokens used: ~25

🎉 SUCCESS! OpenRouter + DeepSeek V3 works perfectly!
```

**Als het faalt:**
- Check `.env` - is OPENROUTER_API_KEY correct?
- Check OpenRouter dashboard - credits beschikbaar?
- Probeer andere model: `qwen/qwen-2.5-72b-instruct`

---

## 🧪 Test 2: ModelFactory Integration (1 min)

**Script:** `tests/test_modelfactory_openrouter.py`

```bash
python tests/test_modelfactory_openrouter.py
```

**Verwacht:**
```
🧪 Testing ModelFactory with OpenRouter...

1. Import model_factory singleton...
   ✅ Imported successfully

2. Get OpenRouter model...
   ✅ Model initialized: openrouter
   ✅ Model name: deepseek/deepseek-chat-v3-0324

3. Test generate_response...
   🤔 OpenRouter (deepseek/deepseek-chat-v3-0324) is thinking...
   ✅ Response: [AI trading advice]

4. Check fallback configuration...
   Primary: deepseek/deepseek-chat-v3-0324 ✅
   Fallback: anthropic/claude-sonnet-4.5 ✅

🎉 ModelFactory + OpenRouter works perfectly!
```

---

## 🧪 Test 3: MT5 Agent Quick Test (2 min)

**Let op:** MT5 Python library werkt alleen op Windows!

**Script:** `tests/test_mt5_agent_simple.py`

```bash
# Op Windows met MT5 geïnstalleerd:
python tests/test_mt5_agent_simple.py

# Op Mac/Linux (zonder MT5):
python tests/test_mt5_agent_simple.py --skip-mt5
```

**Verwacht (Windows met MT5):**
```
🧪 Testing MT5 Agent with OpenRouter...

1. MT5 Connection...
   ✅ MT5 initialized
   ✅ Logged in: 98594810
   💰 Balance: 150000.00 USD

2. Agent Initialization...
   ✅ Initialized MT5 agent with openrouter (deepseek/deepseek-chat-v3-0324)
   ✅ Using trading hours filter: True
   ✅ Max positions: 1

3. Trading Hours Check...
   🕐 Current session: London/NY Overlap
   ✅ EURUSD: Optimal trading time

4. AI Analysis Test...
   🤔 OpenRouter (deepseek/deepseek-chat-v3-0324) is thinking...
   ✅ Got analysis for EURUSD
   Action: [BUY/SELL/HOLD]
   Confidence: [0-100]%
   Reasoning: [AI explanation]

🎉 MT5 Agent + OpenRouter works perfectly!
```

**Verwacht (Mac/Linux --skip-mt5):**
```
⚠️  Skipping MT5 connection (not on Windows)

2. Agent Initialization (mock)...
   ✅ OpenRouter model loaded
   ✅ Model: deepseek/deepseek-chat-v3-0324

3. AI Analysis Test...
   ✅ AI analysis works without MT5

🎉 OpenRouter AI works! (MT5 needs Windows)
```

---

## 🧪 Test 4: Trading Hours Filter (30 sec)

```bash
python src/utils/trading_hours.py
```

**Verwacht:**
```
🕐 Optimal Trading Times (STRICT mode):

✅ FOREX      - ✅ [Current session status]
✅ METALS     - ✅ [Current session status]
✅ INDICES    - ✅ [Current session status]
✅ STOCKS     - ✅ [Current session status]
✅ CRYPTO     - ✅ [Current session status]
```

---

## 🧪 Test 5: Full MT5 Agent Run (Windows only, 5 min)

**Let op:** Alleen op Windows met MT5!

```bash
python src/agents/mt5_trading_agent.py
```

**Verwacht:**
```
🌙 MT5 Trading Agent - Analysis Cycle
============================================================

🕐 Market Session: London/NY Overlap
⏰ Time (UTC): 2025-11-05 18:00:00 UTC
🇳🇱 Time (NL):  2025-11-05 19:00:00 CET/CEST
📅 Day: Wednesday

💰 Account Balance: 150000.00 USD
💵 Equity: 150000.00 USD
📊 Margin Level: 0.00%
💸 Profit: 0.00 USD

📈 Open Positions: 0

🔍 Analyzing EURUSD...
✅ 💱 EUR/USD (forex): ✅ London/NY Overlap - BEST forex hours
🤔 OpenRouter (deepseek/deepseek-chat-v3-0324) is thinking...

[AI Analysis results...]

Action: HOLD / BUY / SELL
Confidence: XX%
Reasoning: [AI explanation]

[Repeats for GBPUSD, USDJPY...]

============================================================
✅ Analysis cycle complete
============================================================
```

---

## ❌ Troubleshooting

### Error: "Access denied"

**Oorzaak:** OpenRouter API issue

**Oplossingen:**
1. Check `.env` - key correct?
2. Check https://openrouter.ai/credits - credits available?
3. Check https://openrouter.ai/keys - key active?
4. Try regenerating key

### Error: "ModelFactory.create_model() not found"

**Oorzaak:** Oude code versie

**Oplossing:**
```bash
git pull origin claude/continue-work-011CUq1JWCHDeiRR6WoX9U33
# Ensure laatste commit is: "Fix OpenRouter SDK implementation"
```

### Error: "No module named 'MetaTrader5'"

**Oorzaak:** Niet op Windows of MT5 niet geïnstalleerd

**Oplossing:**
- Mac/Linux: Gebruik `--skip-mt5` flag
- Windows: `pip install MetaTrader5`
- Of gebruik mock mode voor AI testing

### Error: "MT5 initialize failed"

**Oorzaak:** MT5 software niet geïnstalleerd

**Oplossing:**
1. Download MT5: https://www.metatrader5.com/en/download
2. Install en start MT5
3. Login met demo account
4. Run test opnieuw

### Warning: "Outside optimal trading hours"

**Dit is GEEN error!** System werkt correct:
- Trading hours filter is actief
- Current time is niet optimal voor die asset
- Agent skip automatisch (dit is goed!)

---

## 📊 Success Criteria

Test is **geslaagd** als:

- [x] Test 1: OpenRouter connectie werkt
- [x] Test 2: ModelFactory integration werkt
- [x] Test 3: MT5 Agent initialiseert (Windows) of AI werkt (Mac/Linux)
- [x] Test 4: Trading hours filter werkt
- [x] Test 5: Full agent run compleet (Windows only)

**Minimaal vereist:**
- Test 1 ✅ (basis connectie)
- Test 2 ✅ (model factory)

Als deze 2 werken → OpenRouter SDK is correct!

---

## 🎯 Quick Start Test Sequence

**Snelste test (1 min):**
```bash
# 1. Pull latest code
git pull

# 2. Test basis OpenRouter
python tests/test_openrouter_basic.py

# 3. Als succesvol:
echo "✅ OpenRouter SDK works! Ready for trading!"
```

---

## 📝 Test Report Template

Na testen, vul in:

```
OpenRouter Test Results
Date: [DATUM]
Machine: [Windows/Mac/Linux]
Python: [VERSION]

Test 1 - Basic OpenRouter:    [ ] PASS [ ] FAIL
Test 2 - ModelFactory:         [ ] PASS [ ] FAIL
Test 3 - MT5 Agent:            [ ] PASS [ ] FAIL [ ] SKIP
Test 4 - Trading Hours:        [ ] PASS [ ] FAIL
Test 5 - Full Agent Run:       [ ] PASS [ ] FAIL [ ] SKIP

Notes:
[Eventuele errors of opmerkingen]

Overall: [ ] ✅ SUCCESS [ ] ❌ FAILED
```

---

## 🚀 Na Succesvolle Test

Als alles werkt:

1. **Deploy naar productie**
   - Windows VPS met MT5
   - Run agent 24/7
   - Monitor via Telegram

2. **Setup Telegram alerts**
   - Real-time trade notifications
   - Error alerts
   - Daily summaries

3. **Monitor performance**
   - Check OpenRouter usage dashboard
   - Track AI accuracy
   - Monitor costs

4. **Optimize**
   - Try different models
   - Adjust confidence thresholds
   - Fine-tune trading hours

---

**Ready to test? Run:**
```bash
python tests/test_openrouter_basic.py
```

**Good luck! 🚀**

---

*Built with ❤️ by Moon Dev 🌙*

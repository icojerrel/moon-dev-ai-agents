# 🚀 MT5 Quick Start (5 Minutes)

Get MT5 paper trading running in 5 minutes on Windows.

## Prerequisites
- ✅ Windows PC
- ✅ Python 3.8+ installed
- ✅ MetaTrader 5 installed ([download](https://www.metatrader5.com/en/download))

---

## Step 1: Install Dependencies (1 min)

```bash
# Run the automated installer
install_mt5_windows.bat

# OR manually:
pip install MetaTrader5
```

---

## Step 2: Create MT5 Demo Account (2 min)

1. Open MetaTrader 5
2. **File → Open an Account**
3. Select **MetaQuotes-Demo**
4. Choose **"Open a demo account"**
5. Fill details:
   - Deposit: $10,000
   - Leverage: 1:100
6. **Save your credentials:**
   - Login: `________`
   - Password: `________`
   - Server: `MetaQuotes-Demo`

---

## Step 3: Configure Bot (1 min)

Edit `.env` file:

```bash
# MT5 Credentials
MT5_LOGIN=12345678                    # Your account number
MT5_PASSWORD=YourPassword123          # Your password
MT5_SERVER=MetaQuotes-Demo            # Your server

# AI Key (pick one)
GROK_API_KEY=xai-your_key_here       # xAI (recommended)
GROQ_API_KEY=your_key_here           # or Groq
OPENAI_KEY=your_key_here             # or OpenAI
```

Enable MT5 agent in `src/main.py`:

```python
ACTIVE_AGENTS = {
    'mt5': True,  # ✅ Enable this
}
```

---

## Step 4: Run Bot (1 min)

```bash
# Test connection
python src/agents/mt5_utils.py

# Run trading bot
python src/agents/mt5_trading_agent.py

# OR run with main orchestrator
python src/main.py
```

**Expected output:**
```
✅ Connected to MT5 account: 12345678
💰 Balance: $10000.00
📊 Analyzing EURUSD...
```

---

## Configuration Tips

### Safe Testing Settings

Edit `src/config.py`:

```python
MT5_LOT_SIZE = 0.01              # Micro lot
MT5_MAX_POSITIONS = 3            # Max 3 trades
MT5_RISK_PERCENT = 0.5           # Risk 0.5% per trade
MT5_STOP_LOSS_POINTS = 500       # 50 pip stop loss
```

### Trading Symbols

```python
MT5_SYMBOLS = [
    'EURUSD',  # Major pairs (low spread)
    'GBPUSD',
    'USDJPY',
    'XAUUSD',  # Gold (volatile!)
]
```

### Trading Frequency

```python
SLEEP_BETWEEN_RUNS_MINUTES = 15  # Check every 15 min
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "MT5 library not available" | Install: `pip install MetaTrader5` (Windows only) |
| "Failed to initialize MT5" | Make sure MT5 is **running** |
| "Failed to login" | Check credentials in `.env` (exact server name!) |
| "Symbol not found" | Check symbol name in MT5 Market Watch |
| "Not enough money" | Reduce `MT5_LOT_SIZE` to 0.01 |

---

## Where Are My Trades?

- **MT5 Terminal**: View → Terminal (Ctrl+T) → Trade tab
- **Trade Logs**: `src/data/mt5_trading_agent/trades_YYYYMMDD.csv`
- **Console Output**: Real-time trading decisions and reasoning

---

## Next Steps

📖 **Full guide**: [MT5_SETUP_GUIDE.md](MT5_SETUP_GUIDE.md)

📊 **Customize AI**: Edit `AI_MODEL_TYPE` in `mt5_trading_agent.py`

🎯 **Add strategies**: Modify `get_ai_decision()` logic

🤖 **Multiple brokers**: Create copies of agent for different accounts

---

## Safety Reminders

- ✅ Test on **demo** first
- ✅ Start with **micro lots** (0.01)
- ✅ Always use **stop losses**
- ⚠️ Demo performance ≠ Live performance
- 📉 Never risk money you can't afford to lose

---

Built with 🌙 by Moon Dev

Questions? Check full guide or join Discord!

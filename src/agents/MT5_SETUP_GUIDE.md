# 🌙 Moon Dev's MetaTrader 5 Setup Guide

Complete guide for setting up live paper trading with MT5 on Windows.

## 📋 Table of Contents
1. [Requirements](#requirements)
2. [MT5 Installation](#mt5-installation)
3. [Demo Account Setup](#demo-account-setup)
4. [Python Setup](#python-setup)
5. [Configuration](#configuration)
6. [Running the Bot](#running-the-bot)
7. [Troubleshooting](#troubleshooting)

---

## Requirements

### System Requirements
- **Windows OS** (MT5 Python library only works on Windows)
- **Python 3.8+** (recommended: 3.11)
- **MetaTrader 5 Terminal** installed
- **Internet connection** for MT5 connection

### Python Dependencies
All dependencies are in `requirements.txt`:
```bash
pandas>=2.0.0
pandas-ta>=0.3.14b0
MetaTrader5>=5.0.45  # Windows only
```

---

## MT5 Installation

### Step 1: Download MetaTrader 5

1. Go to [MetaQuotes official website](https://www.metatrader5.com/en/download)
2. Download MT5 for Windows
3. Run the installer (typically `mt5setup.exe`)
4. Follow installation wizard
5. Default path: `C:\Program Files\MetaTrader 5\terminal64.exe`

### Step 2: Verify Installation

- Launch MT5 from Start Menu or Desktop shortcut
- You should see the main MT5 interface
- Note the installation path (needed for configuration)

---

## Demo Account Setup

### Step 3: Create Demo Account

1. **Open MT5 Terminal**

2. **File → Open an Account**

3. **Select a Broker**
   - For practice: Choose **MetaQuotes-Demo**
   - For real paper trading: Choose your preferred broker (Admiral Markets, IC Markets, XM, etc.)

4. **Choose "Open a demo account"**

5. **Fill Account Details**
   ```
   Account Type: Demo
   Leverage: 1:100 (recommended for forex)
   Deposit: $10,000 (or whatever you want to practice with)
   Base Currency: USD
   ```

6. **Save Credentials**
   - Login: (e.g., 12345678)
   - Password: (save this securely!)
   - Server: (e.g., MetaQuotes-Demo)

**⚠️ IMPORTANT:** Write down these credentials - you'll need them for configuration!

### Step 4: Test Login

- Go to **Tools → Options → Server**
- Make sure you're connected (green indicator in bottom right)
- You should see live prices in the Market Watch

---

## Python Setup

### Step 5: Install Python Dependencies

Open **Command Prompt** (or Anaconda Prompt if using conda):

```bash
# Navigate to project directory
cd path\to\moon-dev-ai-agents

# Activate conda environment (if using conda)
conda activate tflow

# Install MT5 library
pip install MetaTrader5

# Install other dependencies (if not already)
pip install -r requirements.txt
```

**Verify Installation:**
```bash
python -c "import MetaTrader5 as mt5; print(f'MT5 version: {mt5.__version__}')"
```

Expected output: `MT5 version: 5.0.45` (or similar)

---

## Configuration

### Step 6: Configure Environment Variables

Edit your `.env` file (create from `.env_example` if needed):

```bash
# MetaTrader 5 Credentials
MT5_LOGIN=12345678                           # Your demo account login
MT5_PASSWORD=your_password_here              # Your demo account password
MT5_SERVER=MetaQuotes-Demo                   # Your broker server
MT5_PATH=C:/Program Files/MetaTrader 5/terminal64.exe  # Path to MT5 executable

# AI Model Keys (at least one required)
ANTHROPIC_KEY=your_claude_key_here
OPENAI_KEY=your_openai_key_here
DEEPSEEK_KEY=your_deepseek_key_here
GROQ_API_KEY=your_groq_key_here
GROK_API_KEY=your_xai_key_here
```

**Common MT5 Servers:**
- MetaQuotes-Demo (demo server)
- YourBroker-Demo (broker-specific demo)
- YourBroker-Live (live trading - use caution!)

### Step 7: Configure Trading Settings

Edit `src/config.py`:

```python
# Enable MT5
MT5_ENABLED = True

# Trading symbols
MT5_SYMBOLS = [
    'EURUSD',  # Forex majors
    'GBPUSD',
    'USDJPY',
    'XAUUSD',  # Gold
    # Add more symbols as needed
]

# Risk management
MT5_LOT_SIZE = 0.01           # Position size (0.01 = micro lot)
MT5_MAX_POSITIONS = 5         # Max concurrent positions
MT5_RISK_PERCENT = 1.0        # Risk 1% per trade

# Stop loss / Take profit
MT5_USE_STOP_LOSS = True
MT5_STOP_LOSS_POINTS = 500    # 50 points = 0.0050 for forex
MT5_USE_TAKE_PROFIT = True
MT5_TAKE_PROFIT_POINTS = 1000 # 100 points = 0.0100 for forex

# Trading interval
SLEEP_BETWEEN_RUNS_MINUTES = 15  # Analyze every 15 minutes
```

### Step 8: Enable MT5 Agent in Main

Edit `src/main.py`:

```python
# Agent Configuration
ACTIVE_AGENTS = {
    'risk': False,
    'trading': False,
    'strategy': False,
    'copybot': False,
    'sentiment': False,
    'mt5': True,       # ✅ Enable MT5 agent
}
```

---

## Running the Bot

### Option 1: Run Standalone MT5 Agent

Best for testing and development:

```bash
# Test connection first
python src/agents/mt5_utils.py

# Run MT5 trading agent
python src/agents/mt5_trading_agent.py
```

### Option 2: Run with Main Orchestrator

Run all active agents together:

```bash
python src/main.py
```

**Expected Output:**
```
🌙 Moon Dev's MT5 AI Trading Agent Initialized
✅ Connected to MT5 account: 12345678
📊 Server: MetaQuotes-Demo
💰 Balance: $10000.00
💵 Equity: $10000.00

============================================================
📊 TRADING STATISTICS
============================================================
💰 Balance: $10000.00
💵 Equity: $10000.00
📈 Profit: $0.00
📊 Margin Level: 0.00%
🎯 Open Positions: 0
📝 Trades Today: 0
============================================================

📊 Analyzing EURUSD...
⏸️ EURUSD: No trade signal
   Reasoning: Price ranging between MA20 and MA50, awaiting clearer signal...
```

---

## Troubleshooting

### Issue 1: "MT5 library not available"

**Problem:** Can't import MetaTrader5 module

**Solutions:**
1. Make sure you're on Windows (library doesn't work on Mac/Linux)
2. Install the library:
   ```bash
   pip install MetaTrader5
   ```
3. Verify installation:
   ```bash
   python -c "import MetaTrader5; print('OK')"
   ```

### Issue 2: "Failed to initialize MT5"

**Problem:** Can't connect to MT5 terminal

**Solutions:**
1. Make sure MT5 is **running** (open the MT5 application)
2. Check MT5_PATH in `.env` points to correct location:
   ```bash
   # Common paths:
   C:/Program Files/MetaTrader 5/terminal64.exe
   C:/Program Files (x86)/MetaTrader 5/terminal64.exe
   ```
3. Try without MT5_PATH (auto-detection):
   ```bash
   # In .env, leave MT5_PATH empty or comment it out
   # MT5_PATH=
   ```

### Issue 3: "Failed to login to MT5 account"

**Problem:** Authentication failed

**Solutions:**
1. Verify credentials in `.env`:
   - MT5_LOGIN (numeric account number)
   - MT5_PASSWORD (case-sensitive!)
   - MT5_SERVER (exact server name)

2. Check server name in MT5:
   - Open MT5 → Tools → Options → Server
   - Copy exact server name (case-sensitive!)

3. Make sure account is active:
   - Demo accounts expire after 30 days of inactivity
   - Create a new demo account if expired

### Issue 4: "Symbol XXXUSD not found"

**Problem:** Symbol not available on your broker

**Solutions:**
1. Check available symbols in MT5:
   - View → Market Watch (Ctrl+M)
   - Right-click → Show All

2. Update MT5_SYMBOLS in `config.py` with available symbols

3. Common symbol name differences:
   - Some brokers: `EURUSDm`, `EURUSD.a`, `#EURUSD`
   - Check exact name in Market Watch

### Issue 5: "Order failed: Not enough money"

**Problem:** Insufficient margin for trade

**Solutions:**
1. Reduce lot size in `config.py`:
   ```python
   MT5_LOT_SIZE = 0.01  # Try smaller size
   ```

2. Reduce max positions:
   ```python
   MT5_MAX_POSITIONS = 3
   ```

3. Check account balance in MT5

### Issue 6: "No data returned for symbol"

**Problem:** Can't fetch historical data

**Solutions:**
1. Make sure symbol is visible in Market Watch:
   - MT5 → Market Watch → Right-click symbol → Chart Window

2. Wait for MT5 to download history:
   - Tools → Options → Charts → Max bars in history
   - Let MT5 run for a few minutes to sync

3. Try different timeframe:
   ```python
   MT5_TIMEFRAME = 'H1'  # Try H1, H4, or D1
   ```

---

## Testing Best Practices

### Start Small
```python
# Recommended settings for testing
MT5_LOT_SIZE = 0.01           # Micro lot
MT5_MAX_POSITIONS = 3         # Max 3 positions
MT5_RISK_PERCENT = 0.5        # Risk only 0.5%
SLEEP_BETWEEN_RUNS_MINUTES = 60  # Check every hour
```

### Monitor Performance
- Check trade logs: `src/data/mt5_trading_agent/trades_YYYYMMDD.csv`
- Monitor positions in MT5 terminal
- Review AI reasoning in console output

### Risk Management
- ✅ Always use stop losses
- ✅ Never risk more than 1-2% per trade
- ✅ Test on demo before live trading
- ✅ Monitor margin levels
- ⚠️ Demo ≠ Live (slippage, execution speed differ)

---

## Advanced Configuration

### Custom AI Models

Edit `src/agents/mt5_trading_agent.py`:

```python
# Change AI model
AI_MODEL_TYPE = 'xai'      # Options: groq, openai, claude, deepseek, xai, ollama
AI_MODEL_NAME = None       # None = default, or specify exact model
```

**Recommended Models:**
- **xAI Grok-4-fast-reasoning**: Best value, fast, 2M context
- **Groq Llama 3.3 70B**: Ultra-fast inference
- **Claude Sonnet**: Most balanced
- **DeepSeek R1**: Advanced reasoning

### Multiple Broker Accounts

You can run separate agents for different brokers:

```python
# Create mt5_trading_agent_broker1.py
# Configure different MT5_LOGIN, MT5_SERVER, etc.
```

### Custom Trading Logic

Modify `execute_trade()` in `mt5_trading_agent.py`:
- Add custom filters (time of day, news events)
- Implement trailing stops
- Add position sizing algorithms

---

## Support

**Issues?**
- Check logs: `src/data/mt5_trading_agent/`
- Enable debug mode (increase verbosity)
- Join Moon Dev Discord for community support
- Check YouTube tutorials: [@moondevonyt](https://youtube.com/@moondevonyt)

**Resources:**
- [MT5 Python Documentation](https://www.mql5.com/en/docs/python_metatrader5)
- [Moon Dev GitHub](https://github.com/moondevonyt/moon-dev-ai-agents-for-trading)
- [MT5 Symbol Specifications](https://www.metatrader5.com/en/terminal/help/start/symbols)

---

## 🚨 Disclaimer

This is **experimental software** for educational purposes only:
- ✅ Demo trading encouraged
- ⚠️ Live trading at your own risk
- ❌ No guarantee of profitability
- 📉 Substantial risk of loss

**Always:**
- Test thoroughly on demo
- Start with minimal position sizes
- Never risk money you can't afford to lose
- Understand the risks of algorithmic trading

---

Built with 🌙 by Moon Dev
Follow for more: [@moondevonyt](https://youtube.com/@moondevonyt)

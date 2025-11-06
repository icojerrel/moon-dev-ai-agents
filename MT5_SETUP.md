# 🌙 Moon Dev's MT5 Paper Trading Setup Guide

**AI-Powered Paper Trading in MetaTrader 5 using Qwen3-Coder:30b**

## 🎯 What You Get

- ✅ **Paper Trading Mode** - Test strategies without risking real money
- ✅ **AI-Powered Decisions** - Qwen3-coder:30b analyzes markets and makes trade decisions
- ✅ **Automatic Trading** - Runs continuously, analyzing markets every hour
- ✅ **Risk Management** - Built-in position sizing and max position limits
- ✅ **Virtual Portfolio Tracking** - Tracks all trades, P/L, and balance
- ✅ **MT5 Integration** - Works with MetaTrader 5 for real market data

---

## 📋 Prerequisites

### 1. MetaTrader 5
Download and install MT5:
- **Windows**: https://www.metatrader5.com/en/download
- **Mac**: Use Wine or download from https://www.metatrader5.com/en/terminal/help/start_advanced/install_mac
- **Linux**: Use Wine

### 2. Python Dependencies
```bash
pip install MetaTrader5 pandas termcolor python-dotenv
```

### 3. Ollama with Qwen3-Coder
```bash
# Start Ollama
ollama serve

# Pull the model (if not already done)
ollama pull qwen3-coder:30b
```

---

## 🚀 Quick Start

### Option 1: Direct Python (Recommended for Testing)

```bash
# Make sure Ollama is running
ollama serve  # In separate terminal

# Run the agent
python src/agents/mt5_agent.py

# With custom settings
python src/agents/mt5_agent.py --balance 50000 --interval 30
```

### Option 2: Docker (Recommended for Production)

```bash
# Start Ollama and agents
docker-compose up -d

# Run MT5 agent in container
docker-compose exec trading-agents python src/agents/mt5_agent.py
```

---

## 💻 MT5 Setup

### Windows

1. **Install MT5**
   - Download from https://www.metatrader5.com/en/download
   - Install and create a demo account

2. **Enable Algo Trading**
   - Open MT5
   - Tools → Options → Expert Advisors
   - ✅ Check "Allow automated trading"
   - ✅ Check "Allow DLL imports"

3. **Test Connection**
   ```python
   python src/mt5/mt5_connection.py
   ```

### Mac/Linux

1. **Install Wine**
   ```bash
   # Mac
   brew install wine-stable

   # Linux (Ubuntu)
   sudo apt install wine
   ```

2. **Install MT5 via Wine**
   ```bash
   wine mt5setup.exe
   ```

3. **Python MT5 Library**
   The MetaTrader5 library works best on Windows. For Mac/Linux:
   - Run MT5 agent in Docker (recommended)
   - Or use paper trading mode only (no real MT5 connection needed)

---

## 🎮 Usage

### Paper Trading (Default)

```bash
# Start with $10,000 virtual balance
python src/agents/mt5_agent.py

# Start with $50,000 virtual balance
python src/agents/mt5_agent.py --balance 50000

# Run analysis every 30 minutes (default is 60)
python src/agents/mt5_agent.py --interval 30
```

### Live Trading (⚠️ Real Money!)

```bash
# ONLY USE AFTER THOROUGH TESTING!
python src/agents/mt5_agent.py --live
```

---

## 📊 How It Works

### 1. Market Analysis Cycle

```
Every 60 minutes (configurable):
├─ 1. Get account status
├─ 2. Manage existing positions
│    ├─ Check P/L
│    ├─ Close profitable positions (>$50 profit)
│    └─ Cut losing positions (>$20 loss)
├─ 3. Analyze each symbol (EURUSD, GBPUSD, USDJPY)
│    ├─ Get recent candlestick data (50 bars, 1H timeframe)
│    ├─ Send to qwen3-coder:30b for analysis
│    ├─ AI responds with: DECISION, CONFIDENCE, REASONING, SL, TP
│    └─ Execute trade if confidence > 70%
└─ 4. Wait for next cycle
```

### 2. AI Analysis

The agent sends market data to qwen3-coder:30b:

```
Symbol: EURUSD
Current Price: 1.08450
20-candle Change: +0.45%
20-candle High: 1.08650
20-candle Low: 1.08250

Recent 5 candles:
[OHLC data]
```

AI responds with structured decision:

```
DECISION: BUY
CONFIDENCE: 82
REASONING: Price bounced off 20-candle low with increasing volume,
           showing strong bullish momentum. RSI suggests oversold reversal.
STOP_LOSS: 1.08200
TAKE_PROFIT: 1.08800
```

### 3. Trade Execution

If confidence >= 70%:
- Calculate position size (2% risk per trade)
- Execute BUY or SELL order
- Set stop loss and take profit
- Track position in virtual portfolio

### 4. Position Management

Every cycle checks open positions:
- Take profit if P/L > $50
- Cut loss if P/L < -$20
- Update P/L based on current price

---

## 🔧 Configuration

### Trading Parameters

Edit `src/agents/mt5_agent.py`:

```python
# In MT5TradingAgent.__init__:

self.max_positions = 3           # Max concurrent positions
self.risk_per_trade = 0.02       # 2% risk per trade
self.symbols = ["EURUSD", "GBPUSD", "USDJPY"]  # Trading symbols
```

### AI Model Settings

Use different Ollama models:

```python
# In MT5TradingAgent.__init__, change:
self.model = self.factory.get_model("ollama", "qwen3-coder:30b")

# To:
self.model = self.factory.get_model("ollama", "deepseek-r1")  # More reasoning
self.model = self.factory.get_model("ollama", "llama3.2")     # Faster
```

Or use external API:

```python
# Use GPT-4 for decisions (costs money!)
self.model = self.factory.get_model("openai", "gpt-4o")
```

### Exit Rules

Edit `manage_positions()` in `mt5_agent.py`:

```python
# Current logic:
if pos['profit'] > 50:      # Take profit at $50
    self.mt5.close_position(pos['ticket'])
elif pos['profit'] < -20:   # Stop loss at -$20
    self.mt5.close_position(pos['ticket'])

# Change to your preference:
if pos['profit'] > 100:     # More aggressive TP
    ...
elif pos['profit'] < -50:   # Wider SL
    ...
```

---

## 📁 Data Storage

### Paper Trading History

All paper trades are saved to:
```
src/data/mt5_paper/paper_trades.json
```

Format:
```json
{
  "initial_balance": 10000,
  "current_balance": 10245.50,
  "open_positions": [...],
  "trade_history": [
    {
      "ticket": 1,
      "symbol": "EURUSD",
      "type": "BUY",
      "volume": 0.01,
      "entry_price": 1.08450,
      "exit_price": 1.08650,
      "profit": 20.00,
      "open_time": "2025-01-15T10:30:00",
      "close_time": "2025-01-15T12:45:00",
      "status": "CLOSED"
    }
  ]
}
```

### Analyze Results

```python
import json
import pandas as pd

# Load trade history
with open('src/data/mt5_paper/paper_trades.json') as f:
    data = json.load(f)

# Calculate stats
df = pd.DataFrame(data['trade_history'])
closed = df[df['status'] == 'CLOSED']

print(f"Total Trades: {len(closed)}")
print(f"Win Rate: {(closed['profit'] > 0).sum() / len(closed) * 100:.1f}%")
print(f"Avg Profit: ${closed['profit'].mean():.2f}")
print(f"Total P/L: ${closed['profit'].sum():.2f}")
```

---

## 🎯 Example Run

```bash
$ python src/agents/mt5_agent.py --balance 10000 --interval 60

======================================================================
  🌙 Moon Dev's MT5 Trading Agent
  Powered by Qwen3-Coder:30b
======================================================================

📝 PAPER TRADING MODE - No real trades will be executed!
💰 Virtual balance: $10,000.00
🤖 Initializing AI model...
✅ AI Model loaded: qwen3-coder:30b

🚀 Starting trading loop...
  Interval: 60 minutes
  Symbols: EURUSD, GBPUSD, USDJPY
  Max Positions: 3
  Risk per Trade: 2.0%

  Press Ctrl+C to stop

██████████████████████████████████████████████████████████████████████
  CYCLE 1 - 2025-01-15 10:00:00
██████████████████████████████████████████████████████████████████████

💰 Account Status:
  Balance: $10,000.00
  Equity: $10,000.00
  P/L: $0.00

🔍 Analyzing EURUSD...
🤔 AI is analyzing...
✅ Analysis complete in 8.3s

📊 EURUSD Analysis:
  Decision: BUY
  Confidence: 82%
  Reasoning: Price bounced off 20-candle low with volume increase

======================================================================
📊 TRADE SIGNAL
======================================================================
  Symbol: EURUSD
  Decision: BUY
  Confidence: 82%
  Reasoning: Price bounced off 20-candle low with volume increase
  Entry Price: 1.08450
  Stop Loss: 1.08200
  Take Profit: 1.08800
  Lot Size: 0.01
======================================================================

📝 Paper trade opened:
   Symbol: EURUSD
   Type: BUY
   Volume: 0.01 lots
   Entry: 1.0845
   SL: 1.082
   TP: 1.088

✅ Trade executed! Ticket: 1

...

😴 Sleeping for 60 minutes...
```

---

## 🐛 Troubleshooting

### MT5 Connection Failed

**Problem**: `MT5 initialization failed`

**Solution**:
1. Make sure MT5 is installed and running
2. Check that algo trading is enabled (Tools → Options → Expert Advisors)
3. Try restarting MT5
4. Use paper trading mode: No MT5 connection needed!

### Ollama Not Available

**Problem**: `❌ Ollama not available!`

**Solution**:
```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Pull model
ollama pull qwen3-coder:30b

# Terminal 3: Run agent
python src/agents/mt5_agent.py
```

### No Market Data

**Problem**: `Could not get candles for EURUSD`

**Solution**:
1. Check MT5 is connected to a broker
2. Verify symbol name is correct (EURUSD vs EUR/USD)
3. In paper trading mode, you might not get real data (mock data is used)

### Trade Not Executed

**Problem**: AI recommends trade but nothing happens

**Solution**:
- Check confidence is >= 70%
- Verify max positions limit not reached (default: 3)
- Check account has sufficient balance
- Look for error messages in output

---

## 📈 Performance Tips

### 1. Optimize Analysis Interval

```bash
# More frequent (more trades, higher costs)
python src/agents/mt5_agent.py --interval 15  # Every 15 minutes

# Less frequent (fewer trades, lower costs)
python src/agents/mt5_agent.py --interval 240  # Every 4 hours
```

### 2. Adjust Confidence Threshold

In `mt5_agent.py`, change:

```python
# More conservative (fewer trades)
if analysis['confidence'] >= 85:  # Instead of 70

# More aggressive (more trades)
if analysis['confidence'] >= 60:
```

### 3. Add More Symbols

```python
self.symbols = [
    "EURUSD", "GBPUSD", "USDJPY",  # Majors
    "AUDUSD", "USDCAD", "NZDUSD",  # More majors
    "XAUUSD"  # Gold
]
```

### 4. Use Multiple Timeframes

Modify `analyze_market()` to get multiple timeframes:

```python
candles_h1 = self.mt5.get_candles(symbol, "H1", 50)
candles_h4 = self.mt5.get_candles(symbol, "H4", 50)
candles_d1 = self.mt5.get_candles(symbol, "D1", 50)

# Include all in AI prompt for better context
```

---

## 🚀 Next Steps

1. **Run Paper Trading for 1 Month**
   - Track results in `paper_trades.json`
   - Analyze win rate, avg profit, drawdown
   - Tweak parameters based on results

2. **Backtest Strategies**
   - Use RBI agent to generate strategies
   - Test on historical data
   - Integrate best strategies into MT5 agent

3. **Advanced Features**
   - Add sentiment analysis from news
   - Implement trailing stops
   - Use multiple AI models for voting
   - Add correlation analysis

4. **Go Live (Only After Extensive Testing!)**
   - Start with micro lots (0.01)
   - Use demo account first
   - Monitor closely for first week
   - Gradually increase position size

---

## ⚠️ Risk Warning

**IMPORTANT**: This is experimental software.

- ✅ **DO**: Test extensively in paper trading mode
- ✅ **DO**: Start with small position sizes
- ✅ **DO**: Monitor the bot regularly
- ✅ **DO**: Use stop losses

- ❌ **DON'T**: Use money you can't afford to lose
- ❌ **DON'T**: Run unattended without testing
- ❌ **DON'T**: Trust AI blindly
- ❌ **DON'T**: Overtrade (respect max positions limit)

**Past performance does not guarantee future results.**

---

## 🌙 Built with Love by Moon Dev

Questions? Join the Discord or check out:
- YouTube: [@moondevonyt](https://youtube.com/@moondevonyt)
- GitHub: [moon-dev-ai-agents](https://github.com/moon-dev-ai-agents-for-trading)

**Happy Paper Trading! 🚀**

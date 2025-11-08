# 💹 MetaTrader 5 Integration Guide

This guide explains how to set up and use the MetaTrader 5 (MT5) integration with Moon Dev's AI Trading System.

## 🎯 Overview

The MT5 integration allows you to:
- Trade forex pairs (EURUSD, GBPUSD, etc.)
- Trade CFDs (indices, commodities, crypto)
- Use AI analysis for entry/exit decisions
- Manage positions programmatically
- Fetch real-time and historical market data

## 📋 Prerequisites

### 1. MetaTrader 5 Account

You need an MT5 account from a broker. Options include:

**Demo Accounts (Recommended for Testing):**
- [MetaQuotes Demo](https://web.metatrader.app/terminal?mode=demo&lang=en)
- Most brokers offer free demo accounts with virtual funds

**Live Accounts:**
- Research and choose a regulated broker
- Popular options: IC Markets, FTMO, Pepperstone, etc.
- **⚠️ Only use live accounts after thorough testing!**

### 2. MetaTrader 5 Terminal

**For Windows:**
- Download MT5 terminal from your broker
- Install normally

**For Mac/Linux:**
- Install Wine: `brew install wine-stable` (Mac) or use package manager (Linux)
- Download Windows MT5 terminal
- Install via Wine
- Note the installation path for configuration

**For Web-Only (Limited):**
- Some features may not work with web-only access
- Desktop terminal recommended for full functionality

## 🔧 Installation

### 1. Install Python Package

The MT5 integration is included in requirements.txt:

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install MetaTrader5>=5.0.45
```

### 2. Configure Environment Variables

Edit your `.env` file (copy from `.env_example` if needed):

```bash
# MetaTrader 5 Credentials
MT5_LOGIN=12345678                    # Your MT5 account number
MT5_PASSWORD=YourPassword123          # Your MT5 account password
MT5_SERVER=MetaQuotes-Demo            # Broker server name
MT5_PATH=                             # Leave empty for auto-detect, or specify path
```

**Finding Your Server Name:**
- Open MT5 terminal
- Go to Tools → Options → Server
- Copy the exact server name (e.g., "ICMarkets-Demo", "Pepperstone-Demo")

### 3. Configure Trading Settings

Edit `src/config.py`:

```python
# MetaTrader 5 Settings 💹
MT5_ENABLED = True  # Set to True to enable MT5 agent

MT5_SYMBOLS = [
    'EURUSD',  # Add/remove symbols as needed
    'GBPUSD',
    'USDJPY',
]

MT5_MAX_POSITION_SIZE = 0.01  # Max lots per trade (0.01 = micro lot)
MT5_MAX_POSITIONS = 3          # Max concurrent positions
MT5_MODEL_TYPE = 'anthropic'   # AI model to use
MT5_MIN_CONFIDENCE = 70        # Minimum AI confidence to trade
```

## 🚀 Usage

### Standalone Execution

Run the MT5 agent independently:

```bash
python src/agents/mt5_trading_agent.py
```

This will:
1. Connect to your MT5 account
2. Display account balance and equity
3. Analyze configured symbols using AI
4. Execute trades based on AI recommendations
5. Run continuously (or once for testing)

### Integration with Main System

Add MT5 agent to your main orchestrator in `src/main.py`:

```python
from src.agents.mt5_trading_agent import MT5TradingAgent

# In ACTIVE_AGENTS dict:
ACTIVE_AGENTS = {
    'risk': True,
    'mt5': True,  # Enable MT5 agent
    # ... other agents
}

# In run_agents() function:
mt5_agent = MT5TradingAgent(
    symbols=MT5_SYMBOLS,
    model_type=MT5_MODEL_TYPE,
    max_position_size=MT5_MAX_POSITION_SIZE,
    max_positions=MT5_MAX_POSITIONS
) if ACTIVE_AGENTS.get('mt5') else None

# In main loop:
if mt5_agent:
    cprint("\n💹 Running MT5 Trading Analysis...", "cyan")
    mt5_agent.run_analysis_cycle()
```

## 📊 Features

### Market Data

Get OHLCV data for any symbol:

```python
from src.nice_funcs_mt5 import get_ohlcv_data

df = get_ohlcv_data('EURUSD', timeframe='1H', bars=500)
# Returns DataFrame with Open, High, Low, Close, Volume
```

### Account Information

```python
from src.nice_funcs_mt5 import get_account_info

account = get_account_info()
print(f"Balance: {account['balance']}")
print(f"Equity: {account['equity']}")
print(f"Profit: {account['profit']}")
```

### Position Management

```python
from src.nice_funcs_mt5 import (
    get_positions,
    market_buy,
    market_sell,
    close_position,
    close_all_positions
)

# Get open positions
positions = get_positions()

# Open positions
ticket = market_buy('EURUSD', volume=0.01, sl=1.0800, tp=1.0900)
ticket = market_sell('GBPUSD', volume=0.01)

# Close specific position
close_position(ticket)

# Close all positions
close_all_positions()
```

### Technical Indicators

```python
from src.nice_funcs_mt5 import get_ohlcv_data, add_technical_indicators

df = get_ohlcv_data('EURUSD', timeframe='4H', bars=200)
df = add_technical_indicators(df)

# Now df includes:
# - SMA_20, SMA_50, SMA_200
# - RSI
# - MACD, MACD_Signal, MACD_Hist
# - BB_Upper, BB_Middle, BB_Lower
```

## 🎛️ Trading Parameters

### Position Sizing

**Lot Sizes:**
- `1.0` = Standard lot (100,000 units)
- `0.1` = Mini lot (10,000 units)
- `0.01` = Micro lot (1,000 units)

**Example Risk Calculation:**
```python
# For EURUSD at 1.0850
# 0.01 lots = 1,000 units
# 10 pips = $1 profit/loss
# 50 pip SL = $5 risk per micro lot
```

### Stop Loss / Take Profit

The agent calculates SL/TP in pips:

```python
# AI suggests:
# - 20 pip stop loss
# - 40 pip take profit
# = 1:2 risk/reward ratio
```

### Timeframes

Supported timeframes:
- `1m`, `5m`, `15m`, `30m` - Minute charts
- `1H`, `4H` - Hourly charts
- `1D` - Daily
- `1W` - Weekly
- `1M` - Monthly

## ⚠️ Risk Management

### Important Safety Features

1. **Position Limits:**
   - `MT5_MAX_POSITIONS`: Prevents over-exposure
   - `MT5_MAX_POSITION_SIZE`: Limits lot size

2. **Confidence Threshold:**
   - `MT5_MIN_CONFIDENCE`: Only trades high-probability setups
   - Default 70% minimum

3. **Risk Agent Integration:**
   - Works with existing risk management system
   - Monitors total portfolio exposure

### Testing Strategy

**ALWAYS test with demo accounts first:**

1. Start with demo account
2. Run for at least 1-2 weeks
3. Monitor all trades and AI decisions
4. Verify risk management works correctly
5. Only then consider live trading with small amounts

### Live Trading Checklist

Before going live:
- [ ] Tested for minimum 2 weeks on demo
- [ ] Verified all trades execute correctly
- [ ] Checked slippage and spread costs
- [ ] Confirmed risk limits are appropriate
- [ ] Started with minimum position sizes (0.01 lots)
- [ ] Set up alerts for position monitoring
- [ ] Understand your broker's margin requirements
- [ ] Have emergency stop procedures in place

## 🔍 Monitoring & Debugging

### Test Connection

```bash
python src/nice_funcs_mt5.py
```

This standalone test will:
- Connect to MT5
- Show account info
- Fetch sample data for EURUSD/GBPUSD
- Display technical indicators
- List open positions

### Common Issues

**"MT5 initialize() failed"**
- MT5 terminal is not installed
- Terminal is not running (on Windows)
- Incorrect MT5_PATH (on Mac/Linux with Wine)

**"MT5 login failed"**
- Wrong credentials in .env
- Wrong server name
- Account disabled by broker
- Network connection issue

**"Symbol not found"**
- Symbol not available on your broker
- Incorrect symbol name (use broker's exact naming)
- Symbol not enabled in Market Watch

**"Order failed"**
- Insufficient margin
- Market is closed
- Position size too small/large
- Invalid SL/TP levels

### Logs

The agent uses colored terminal output:
- 🟢 Green: Successful operations
- 🔴 Red: Errors
- 🟡 Yellow: Warnings/info
- 🔵 Cyan: Analysis updates

## 🌐 Platform Compatibility

### Windows
✅ Full support - native MT5 terminal

### Mac (Intel/Apple Silicon)
✅ Works via Wine/Crossover
- Install Wine: `brew install wine-stable`
- Install MT5 Windows version through Wine
- Set `MT5_PATH` in .env

### Linux
✅ Works via Wine
- Install Wine via package manager
- Install MT5 Windows version
- May need to configure Wine prefix

### Cloud/VPS
✅ Recommended for 24/7 operation
- Use Windows VPS for best compatibility
- Or Linux VPS with Wine
- Ensure stable internet connection

## 🔗 Integration with Other Agents

The MT5 agent works alongside:

**Risk Agent** (`risk_agent.py`):
- Monitors total portfolio risk
- Enforces position limits
- Can close positions if limits breached

**Sentiment Agent** (`sentiment_agent.py`):
- Analyzes Twitter sentiment for USD, EUR, GBP
- Provides macro context for forex trades

**Research Agent** (`research_agent.py`):
- Generates strategy ideas
- Can backtest forex strategies

**Chat Agent** (`chat_agent.py`):
- Reports trade executions to live stream
- Announces significant positions

## 📚 Advanced Usage

### Custom Strategy Integration

Create custom strategies in `src/strategies/`:

```python
class ForexScalperStrategy(BaseStrategy):
    name = "forex_scalper"

    def generate_signals(self, symbol, market_data):
        # Your custom logic
        return {
            "action": "BUY",
            "confidence": 85,
            "reasoning": "5-min uptrend with RSI oversold bounce"
        }
```

### Multiple Broker Accounts

Run separate instances for different brokers:

```python
# Account 1: IC Markets
agent1 = MT5TradingAgent(
    symbols=['EURUSD', 'GBPUSD'],
    # Will use default .env credentials
)

# Account 2: Different credentials
# Set environment variables programmatically
os.environ['MT5_LOGIN'] = '87654321'
os.environ['MT5_SERVER'] = 'AnotherBroker-Live'
agent2 = MT5TradingAgent(symbols=['XAUUSD'])
```

### Backtesting Integration

Use RBI agent to backtest MT5 strategies:

```bash
python src/agents/rbi_agent.py
# Provide MT5 strategy description
# Agent will code and backtest it
```

## 🆘 Support

**Documentation:**
- MT5 Python docs: https://www.mql5.com/en/docs/python_metatrader5
- Moon Dev YouTube: See project README for playlist

**Community:**
- Join Moon Dev Discord (link in main README)
- Ask questions in #mt5-integration channel

**Debugging:**
1. Test connection with standalone script first
2. Check MT5 terminal is running (Windows)
3. Verify credentials in .env are correct
4. Ensure symbols exist on your broker
5. Check terminal's Expert Advisors are enabled

## ⚖️ Legal & Risk Disclaimers

**IMPORTANT:**
- This is experimental software for educational purposes
- Past performance does not indicate future results
- Trading forex/CFDs carries substantial risk of loss
- You can lose more than your initial investment (with margin)
- No guarantee of profitability
- Test extensively before live trading
- Only trade with money you can afford to lose
- Seek professional financial advice before live trading
- Moon Dev is not a licensed financial advisor

**Regulatory Compliance:**
- Ensure your broker is properly regulated
- Automated trading may have specific regulations in your jurisdiction
- Check local laws before using automated trading systems

---

**Built with ❤️ by Moon Dev 🌙**

For more information, see the main README and join the Discord community!

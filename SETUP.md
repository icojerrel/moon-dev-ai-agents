# Moon Dev AI Agents - Setup Guide

## Quick Start (Critical Steps)

### 1. Activate Conda Environment
```bash
conda activate tflow
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

This will install all required packages including:
- pandas, numpy (data handling)
- anthropic, openai, groq, deepseek (AI models)
- python-dotenv (environment variables)
- termcolor (console colors)
- backtesting, pandas-ta, ta-lib (trading/backtesting)
- And 20+ more packages

### 3. Create .env File
```bash
cp .env_example .env
```

Then edit `.env` and add your actual API keys:

**CRITICAL - Required for basic operation:**
- `ANTHROPIC_KEY` - Claude API (for AI agents)
- `BIRDEYE_API_KEY` - Solana token data
- `SOLANA_PRIVATE_KEY` - Your wallet (Base58 format)
- `RPC_ENDPOINT` - Helius or other Solana RPC

**Optional - For specific features:**
- `OPENAI_KEY` - GPT models
- `GROQ_API_KEY` - Fast inference
- `DEEPSEEK_KEY` - Reasoning models
- `MOONDEV_API_KEY` - Custom signals
- `COINGECKO_API_KEY` - Token metadata
- `YOUTUBE_API_KEY` - YouTube integration
- `TWILIO_*` - Phone agent
- `TWITTER_*` - Tweet agent

### 4. Configure Trading Settings

Edit `src/config.py` to set:
- `MONITORED_TOKENS` - Which tokens to trade
- `usd_size` - Position size (default: $25)
- `MAX_LOSS_USD` - Circuit breaker (default: $25)
- `MINIMUM_BALANCE_USD` - Minimum balance (default: $50)
- Wallet address (line 32) - Replace placeholder

### 5. Run the System

**Option A: Run main orchestrator**
```bash
python src/main.py
```

**Option B: Run individual agents**
```bash
python src/agents/trading_agent.py
python src/agents/risk_agent.py
python src/agents/rbi_agent.py
python src/agents/sentiment_agent.py
# ... any agent can run standalone
```

**Option C: Backtest strategies**
```bash
python src/agents/rbi_agent.py
# Provide YouTube URL, PDF, or strategy description
```

## What Was Fixed

This setup includes recent critical fixes:

1. **Fixed import error in main.py** (line 12)
   - Changed `from config import *` → `from src.config import *`
   - Now consistent with all agents

2. **Fixed Linux-incompatible path in config.py** (line 101)
   - Changed `/Volumes/Moon 26/OBS` → `os.path.expanduser('~/Videos/OBS')`
   - Now works cross-platform (Mac/Linux/Windows)

## System Architecture

```
src/
├── main.py              # Orchestrator (runs multiple agents in loop)
├── config.py            # Global configuration
├── nice_funcs.py        # Shared trading utilities (1,200+ functions)
├── agents/              # 43 specialized AI agents
│   ├── trading_agent.py      # LLM trading decisions
│   ├── risk_agent.py         # Portfolio risk management
│   ├── rbi_agent.py          # Research-Backtest-Implement
│   ├── sentiment_agent.py    # Twitter sentiment
│   └── ...38 more agents
├── models/              # LLM provider abstraction
│   └── model_factory.py      # Unified interface for Claude/GPT/Groq/etc
├── strategies/          # User-defined strategies
└── data/                # Agent outputs, analysis results
```

## Agent Activation

By default, **all agents are OFF** in `main.py`. To enable agents:

Edit `src/main.py` line 29-34:
```python
ACTIVE_AGENTS = {
    'risk': True,       # Enable risk management
    'trading': True,    # Enable LLM trading
    'strategy': False,  # Strategy-based trading
    'copybot': False,   # CopyBot monitoring
    'sentiment': False, # Twitter sentiment
}
```

Or run agents directly:
```bash
python src/agents/whale_agent.py      # Whale activity tracker
python src/agents/funding_agent.py    # Funding rate analysis
python src/agents/clips_agent.py      # Video clipping automation
```

## Testing the Setup

**Test 1: Check imports**
```bash
python -c "from src.config import *; print('Config loaded ✓')"
python -c "from src.models.model_factory import ModelFactory; print('Models loaded ✓')"
```

**Test 2: Check API keys**
```bash
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('ANTHROPIC_KEY' in os.environ)"
```

**Test 3: Run a simple agent**
```bash
python src/agents/sentiment_agent.py
```

## Troubleshooting

**Problem: ModuleNotFoundError**
- Solution: Run `pip install -r requirements.txt` in `tflow` conda env

**Problem: API key errors**
- Solution: Check `.env` file exists and has valid keys

**Problem: "No such file or directory: /Volumes/Moon 26/OBS"**
- Solution: Already fixed! Update to latest config.py

**Problem: Import error in main.py**
- Solution: Already fixed! Update to latest main.py

**Problem: ta-lib installation fails**
- Solution Linux: `sudo apt-get install ta-lib`
- Solution Mac: `brew install ta-lib`

## Next Steps

1. **Start with risk agent**: Validates your setup and checks portfolio
2. **Try RBI agent**: Generate backtests from YouTube videos
3. **Enable trading agents**: Start with paper trading (low position sizes)
4. **Monitor performance**: Check `src/data/` for agent outputs
5. **Join Discord**: Community support and weekly updates

## Security Reminders

- **NEVER commit .env file** (already in .gitignore)
- **NEVER print API keys** in logs
- **START WITH SMALL POSITIONS** ($25 default)
- **USE CIRCUIT BREAKERS** (MAX_LOSS_USD setting)
- **ROTATE KEYS** if accidentally exposed

## Resources

- YouTube: Moon Dev channel (weekly updates)
- Discord: Community and support
- GitHub: Issues and discussions
- CLAUDE.md: Detailed development guide

---

**System Status After Setup:**
- ✅ Dependencies installed
- ✅ .env configured with API keys
- ✅ config.py updated with wallet/settings
- ✅ Import errors fixed
- ✅ Paths Linux-compatible
- 🚀 Ready to run!

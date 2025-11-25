# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an experimental AI trading system that orchestrates **50+ specialized AI agents** to analyze markets, execute strategies, and manage risk across cryptocurrency markets (primarily Solana, HyperLiquid, and MetaTrader 5). The project uses a modular agent architecture with unified LLM provider abstraction supporting Claude, GPT-4/GPT-5, DeepSeek, Groq, Gemini, xAI (Grok), OpenRouter (200+ models), and local Ollama models.

## Key Development Commands

### Environment Setup
```bash
# Use existing conda environment (DO NOT create new virtual environments)
conda activate tflow

# Install/update dependencies
pip install -r requirements.txt

# IMPORTANT: Update requirements.txt every time you add a new package
pip freeze > requirements.txt
```

### Running the System
```bash
# Run main orchestrator (controls multiple agents)
python src/main.py

# Run individual agents standalone (any agent in src/agents/ can run independently)
python src/agents/trading_agent.py
python src/agents/risk_agent.py
python src/agents/rbi_agent.py
python src/agents/swarm_agent.py
python src/agents/websearch_agent.py
# ... 50+ agents available
```

### Backtesting
```bash
# Use backtesting.py library with pandas_ta or talib for indicators
# RBI Agent with parallel backtesting (18 threads, 20+ data sources)
python src/agents/rbi_agent_pp_multi.py

# Web dashboard for backtesting
cd src/data/rbi_pp_multi
python app.py  # Opens on http://localhost:8001
```

### Docker
```bash
# Build and run with docker-compose
docker-compose up -d

# Run tests in Docker
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

### Testing
```bash
# Run test suite
./run_tests.sh

# Or directly with pytest
pytest tests/ -v
```

## Architecture Overview

### Core Structure
```
moon-dev-ai-agents/
├── src/
│   ├── agents/              # 50+ specialized AI agents (each <800 lines)
│   ├── models/              # LLM provider abstraction (ModelFactory pattern)
│   ├── strategies/          # User-defined trading strategies
│   │   └── custom/          # Custom strategy implementations
│   ├── scripts/             # Standalone utility scripts
│   ├── data/                # Agent outputs, memory, analysis results
│   ├── utils/               # Shared utilities (alerts, logging, health monitoring)
│   ├── config.py            # Global configuration (positions, risk limits, API settings)
│   ├── main.py              # Main orchestrator for multi-agent loop
│   ├── nice_funcs.py        # 1,178 lines of shared trading utilities
│   ├── nice_funcs_hl.py     # 378 lines Hyperliquid-specific utilities
│   ├── nice_funcs_mt5.py    # 787 lines MetaTrader 5 utilities
│   └── ezbot.py             # Legacy trading controller
├── docs/                    # Agent-specific documentation (35+ docs)
├── tests/                   # Test suite
├── monitoring/              # Health monitoring scripts
├── CLAUDE.md                # This file
├── README.md                # Project README
├── PRODUCTION_DEPLOY.md     # Production deployment guide
├── MULTI_ASSET_TRADING.md   # Multi-asset trading documentation
├── TRADING_HOURS_INTEGRATION.md  # Trading hours management
├── docker-compose.yml       # Docker configuration
├── requirements.txt         # Python dependencies
└── .env_example             # Example environment variables
```

### Agent Ecosystem (50+ Agents)

**Trading Agents**:
- `trading_agent` - Dual-mode AI trading (single model or 6-model swarm consensus)
- `strategy_agent` - Manages and executes user-defined strategies
- `risk_agent` - Portfolio risk management with circuit breakers
- `copybot_agent` - Monitors copy bot for potential trades
- `mt5_trading_agent` - MetaTrader 5 integration for forex/stocks

**Market Analysis**:
- `sentiment_agent` - Twitter sentiment analysis with voice alerts
- `whale_agent` - Whale activity monitoring and alerts
- `funding_agent` - Funding rates analysis across exchanges
- `liquidation_agent` - Liquidation event tracking with AI analysis
- `chartanalysis_agent` - Chart analysis with AI buy/sell recommendations
- `coingecko_agent` - CoinGecko API integration for market data
- `new_or_top_agent` - Tracks new and trending tokens
- `listingarb_agent` - Pre-exchange listing arbitrage opportunities
- `fundingarb_agent` - Funding rate arbitrage between HyperLiquid and Solana

**Content Creation**:
- `chat_agent` - YouTube live stream chat moderation and responses
- `clips_agent` - Video clipping automation
- `realtime_clips_agent` - Real-time OBS stream clipping
- `shortvid_agent` - Short-form video generation
- `tweet_agent` - AI-powered tweet generation
- `video_agent` - Parallel video generation using OpenAI Sora 2
- `phone_agent` - AI phone call handling
- `stream_agent` - Stream management utilities

**Strategy Development**:
- `rbi_agent` - Research-Based Inference (codes backtests from videos/PDFs)
- `rbi_agent_v2`, `rbi_agent_v3` - Enhanced RBI versions
- `rbi_agent_pp_multi` - Parallel backtesting with 18 threads, 20+ data sources
- `rbi_batch_backtester` - Batch backtest processing
- `backtest_runner` - Backtest execution engine
- `research_agent` - Fills ideas.txt for automated strategy research
- `websearch_agent` - Web scraping for trading strategy resources

**Specialized**:
- `sniper_agent` - New Solana token launch detection and sniping
- `solana_agent` - Solana meme token analysis
- `tx_agent` - Transaction monitoring for copy list
- `million_agent` - Uses Gemini's million-token context window
- `tiktok_agent` - TikTok scraping for consumer data (social arbitrage)
- `compliance_agent` - Ad compliance checking for Facebook/TikTok
- `housecoin_agent` - DCA agent with AI confirmation (1 House = 1 Housecoin)
- `polymarket_agent` - Prediction market trading on Polymarket
- `swarm_agent` - 6-model parallel consensus (Claude, GPT, Gemini, Grok, DeepSeek)
- `focus_agent` - Productivity monitoring with audio sampling
- `prompt_agent` - Interactive prompt enhancement tool
- `code_runner_agent` - Dynamic code execution engine

Each agent can run independently or as part of the main orchestrator loop.

### LLM Integration (Model Factory)

Located at `src/models/model_factory.py` and `src/models/README.md`

**Unified Interface**: All agents use `ModelFactory.create_model()` for consistent LLM access

**Supported Providers**:
- **Anthropic Claude** (default) - Claude 3 Opus/Sonnet/Haiku
- **OpenAI** - GPT-4o, GPT-5, O1, O3-mini
- **DeepSeek** - DeepSeek Chat, Reasoner, R1 (excellent for strategy research)
- **Groq** - Fast inference (Mixtral, Llama 3.x, DeepSeek R1 distilled)
- **Google Gemini** - Gemini 2.0 Flash, 1.5 Pro/Flash (multimodal)
- **xAI** - Grok-4 models
- **OpenRouter** - Access to 200+ models (Qwen, GLM, and more)
- **Ollama** - Local models (DeepSeek R1, Llama 3.2, Gemma 2B)

**Key Pattern**:
```python
from src.models.model_factory import ModelFactory

# Single model
model = ModelFactory.create_model('anthropic')  # or 'openai', 'deepseek', 'groq', etc.
response = model.generate_response(system_prompt, user_content, temperature, max_tokens)

# Multi-model consensus (swarm pattern)
from src.agents.swarm_agent import SwarmAgent
swarm = SwarmAgent()
result = swarm.get_consensus("What's the market outlook?")
# Returns majority vote + individual model responses
```

### Configuration Management

**Primary Config**: `src/config.py`
- Trading settings: `MONITORED_TOKENS`, `EXCLUDED_TOKENS`, position sizing (`usd_size`, `max_usd_order_size`)
- Risk management: `CASH_PERCENTAGE`, `MAX_POSITION_PERCENTAGE`, `MAX_LOSS_USD`, `MAX_GAIN_USD`, `MINIMUM_BALANCE_USD`
- Agent behavior: `SLEEP_BETWEEN_RUNS_MINUTES`, `ACTIVE_AGENTS` dict in `main.py`
- AI settings: `AI_MODEL`, `AI_MAX_TOKENS`, `AI_TEMPERATURE`
- Swarm mode: `USE_SWARM_MODE` (toggle between single model vs 6-model consensus)

**Environment Variables**: `.env` (see `.env_example`)
- Trading APIs: `BIRDEYE_API_KEY`, `MOONDEV_API_KEY`, `COINGECKO_API_KEY`
- AI Services: `ANTHROPIC_KEY`, `OPENAI_KEY`, `DEEPSEEK_KEY`, `GROQ_API_KEY`, `GEMINI_KEY`, `XAI_API_KEY`, `OPENROUTER_API_KEY`
- Blockchain: `SOLANA_PRIVATE_KEY`, `HYPER_LIQUID_ETH_PRIVATE_KEY`, `RPC_ENDPOINT`

### Shared Utilities

**Trading Utilities**:
- `src/nice_funcs.py` (1,178 lines): Core trading functions for Solana/BirdEye
  - Data: `token_overview()`, `token_price()`, `get_position()`, `get_ohlcv_data()`
  - Trading: `market_buy()`, `market_sell()`, `chunk_kill()`, `open_position()`
  - Analysis: Technical indicators, PnL calculations, rug pull detection

- `src/nice_funcs_hl.py` (378 lines): HyperLiquid-specific utilities
  - Perpetuals trading, position management, liquidation data

- `src/nice_funcs_mt5.py` (787 lines): MetaTrader 5 utilities
  - Forex/stocks trading, traditional market integration

**System Utilities** (`src/utils/`):
- `alerts.py` - Alert system for trading signals and events
- `health_monitor.py` - System health monitoring and diagnostics
- `logger.py` - Unified logging infrastructure
- `trading_hours.py` - Trading hours management (market open/close detection)
- `mt5_helpers.py` - MetaTrader 5 helper functions
- `mock_mt5.py` - MT5 mock for testing without live connection

**API Integration**:
- `src/agents/api.py`: `MoonDevAPI` class for custom Moon Dev API endpoints
  - `get_liquidation_data()`, `get_funding_data()`, `get_oi_data()`, `get_copybot_follow_list()`

### Data Flow Pattern

```
Config/Input → Agent Init → API Data Fetch → Data Parsing →
LLM Analysis (via ModelFactory) → Decision Output →
Result Storage (CSV/JSON in src/data/) → Optional Trade Execution →
Health Monitoring & Alerts
```

## Development Rules

### File Management
- **Keep files under 800 lines** - if longer, split into new files and update README
- **DO NOT move files without asking** - you can create new files but no moving
- **NEVER create new virtual environments** - use existing `conda activate tflow`
- **Update requirements.txt** after adding any new package: `pip freeze > requirements.txt`

### Backtesting
- Use `backtesting.py` library (NOT their built-in indicators)
- Use `pandas_ta` or `talib` for technical indicators instead
- For parallel backtesting, use `rbi_agent_pp_multi.py` (18 threads, 20+ data sources)
- Results saved to `src/data/rbi_pp_multi/backtest_stats.csv`

### Code Style
- **No fake/synthetic data** - always use real data or fail the script
- **Minimal error handling** - user wants to see errors, not over-engineered try/except blocks
- **No API key exposure** - never show keys from `.env` in output
- **Color-coded logging** - use `termcolor` for console output consistency

### Agent Development Pattern

When creating new agents:
1. Inherit from base patterns in existing agents (see `src/agents/base_agent.py`)
2. Use `ModelFactory` for LLM access
3. Store outputs in `src/data/[agent_name]/`
4. Make agent independently executable (standalone script with `if __name__ == "__main__"`)
5. Add configuration to `config.py` if needed
6. Follow naming: `[purpose]_agent.py`
7. Document in `docs/[agent_name].md`
8. Keep under 800 lines (split if needed)

### Testing Strategies

Place strategy definitions in `src/strategies/` folder:
```python
from src.strategies.base_strategy import BaseStrategy

class YourStrategy(BaseStrategy):
    name = "strategy_name"
    description = "what it does"

    def generate_signals(self, token_address, market_data):
        return {
            "action": "BUY"|"SELL"|"NOTHING",
            "confidence": 0-100,
            "reasoning": "explanation"
        }
```

Custom strategies go in `src/strategies/custom/`

## Important Context

### Risk-First Philosophy
- Risk Agent runs first in main loop before any trading decisions
- Configurable circuit breakers (`MAX_LOSS_USD`, `MINIMUM_BALANCE_USD`)
- AI confirmation for position-closing decisions (configurable via `USE_AI_CONFIRMATION`)
- Health monitoring tracks system performance and errors

### Data Sources
1. **BirdEye API** - Solana token data (price, volume, liquidity, OHLCV)
2. **Moon Dev API** - Custom signals (liquidations, funding rates, OI, copybot data)
3. **CoinGecko API** - 15,000+ token metadata, market caps, sentiment
4. **Helius RPC** - Solana blockchain interaction
5. **HyperLiquid** - Perpetuals trading, funding rates
6. **MetaTrader 5** - Traditional markets (forex, stocks)
7. **Polymarket** - Prediction market data via WebSocket

### Autonomous Execution
- Main loop runs every 15 minutes by default (`SLEEP_BETWEEN_RUNS_MINUTES`)
- Agents handle errors gracefully and continue execution
- Keyboard interrupt (Ctrl+C) for graceful shutdown
- All agents log to console with color-coded output (termcolor)
- Health monitoring tracks uptime and performance

### Trading Hours Integration
- `src/utils/trading_hours.py` manages market hours
- Supports forex (24/5), stocks (9:30-16:00 ET), crypto (24/7)
- Automatic holiday detection
- Configurable pre-market/after-hours trading

### Multi-Model Swarm Consensus
The project supports **swarm intelligence** via `swarm_agent.py`:
1. Query 6 AI models in parallel (Claude 4.5, GPT-5, Gemini 2.5, Grok-4, DeepSeek, DeepSeek-R1 local)
2. Generate majority vote consensus
3. Return structured JSON with individual model responses
4. Cost: ~45-60 seconds per query vs 10s single model
5. Toggle via `USE_SWARM_MODE` in config.py

### AI-Driven Strategy Generation (RBI Agent)
1. User provides: YouTube video URL / PDF / trading idea text
2. AI (DeepSeek-R1 or other) analyzes and extracts strategy logic
3. Generates `backtesting.py` compatible code
4. Executes backtest across 20+ data sources in parallel
5. Only saves strategies returning > 1% (configurable via `SAVE_IF_OVER_RETURN`)
6. Tries to optimize to 50% target return (`TARGET_RETURN`)
7. Cost: ~$0.027 per backtest execution (~6 minutes)
8. Results viewable via web dashboard at http://localhost:8001

**RBI Versions**:
- `rbi_agent.py` - Original single-threaded version
- `rbi_agent_v2.py`, `rbi_agent_v3.py` - Enhanced versions
- `rbi_agent_pp_multi.py` - **Recommended**: 18-thread parallel version with web dashboard
- `rbi_batch_backtester.py` - Batch processing for multiple strategies

## Common Patterns

### Adding New Agent
1. Create `src/agents/your_agent.py`
2. Implement standalone execution logic with `if __name__ == "__main__"`
3. Add to `ACTIVE_AGENTS` in `main.py` if needed for orchestration
4. Use `ModelFactory` for LLM calls
5. Store results in `src/data/your_agent/`
6. Document in `docs/your_agent.md`
7. Add tests in `tests/test_your_agent.py`

### Switching AI Models

**Single Model** - Edit `config.py`:
```python
AI_MODEL = "claude-3-haiku-20240307"  # Fast, cheap
# AI_MODEL = "claude-3-sonnet-20240229"  # Balanced
# AI_MODEL = "claude-3-opus-20240229"  # Most powerful
# AI_MODEL = "gpt-4o"  # OpenAI's best
# AI_MODEL = "gpt-5"  # Next-gen GPT
```

**Per-Agent Model Selection** via ModelFactory:
```python
model = ModelFactory.create_model('deepseek')  # Reasoning tasks
model = ModelFactory.create_model('groq')      # Fast inference
model = ModelFactory.create_model('openrouter', 'qwen/qvq-72b-preview')  # Specific model via OpenRouter
```

**Swarm Mode** (6-model consensus):
```python
# In config.py
USE_SWARM_MODE = True  # Enable swarm consensus

# Or use swarm_agent directly
from src.agents.swarm_agent import SwarmAgent
swarm = SwarmAgent()
result = swarm.get_consensus("Analyze BTC market")
print(result['consensus'])  # Majority vote result
print(result['votes'])      # Individual model responses
```

### Reading Market Data
```python
from src.nice_funcs import token_overview, get_ohlcv_data, token_price

# Get comprehensive token data (Solana)
overview = token_overview(token_address)

# Get price history
ohlcv = get_ohlcv_data(token_address, timeframe='1H', days_back=3)

# Get current price
price = token_price(token_address)

# HyperLiquid data
from src.nice_funcs_hl import get_hl_position, get_hl_funding_rate

# MetaTrader 5 data
from src.nice_funcs_mt5 import get_mt5_price, get_mt5_positions
```

### Using the Swarm Agent
```python
from src.agents.swarm_agent import SwarmAgent

swarm = SwarmAgent()
result = swarm.get_consensus(
    query="Should I buy Bitcoin now?",
    context="BTC is at $45k, RSI is 65, funding rate is positive"
)

print(f"Consensus: {result['consensus']}")
print(f"Confidence: {result['confidence']}%")
for model, response in result['votes'].items():
    print(f"{model}: {response}")
```

### Health Monitoring
```python
from src.utils.health_monitor import HealthMonitor

monitor = HealthMonitor()
monitor.log_agent_run("trading_agent", success=True)
status = monitor.get_system_health()
print(status)  # Returns uptime, error rate, agent performance
```

### Trading Hours Check
```python
from src.utils.trading_hours import is_market_open, get_next_market_open

# Check if market is open
if is_market_open('forex'):
    # Execute forex trade
    pass

if is_market_open('stocks'):
    # Execute stock trade via MT5
    pass

# Get next market open time
next_open = get_next_market_open('stocks')
print(f"NYSE opens at: {next_open}")
```

## Production Deployment

See `PRODUCTION_DEPLOY.md` for full details.

**Quick Start**:
1. Set up systemd service: `moondev-trading.service`
2. Configure environment variables
3. Enable health monitoring
4. Set up log rotation
5. Configure alerts

**Docker Deployment**:
```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

**Monitoring**:
```bash
# Check service status
systemctl status moondev-trading

# View logs
journalctl -u moondev-trading -f

# Health check
curl http://localhost:8080/health
```

## Testing

The project includes comprehensive tests in `tests/`:
- Unit tests for individual agents
- Integration tests for trading workflows
- Mock data for safe testing
- Docker test environment

**Running Tests**:
```bash
# All tests
./run_tests.sh

# Specific test
pytest tests/test_trading_agent.py -v

# With coverage
pytest --cov=src tests/

# Docker tests
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## Documentation

Agent-specific documentation in `docs/`:
- `api.md` - API integration guide
- `rbi_agent.md` - RBI agent comprehensive guide
- `swarm_agent.md` - Swarm consensus documentation
- `polymarket_agent.md` - Polymarket integration
- `prompt_agent.md` - Prompt enhancement guide
- `websearch_agent.md` - Web search agent usage
- Individual agent docs for all 50+ agents

## Project Philosophy

This is an **experimental, educational project** demonstrating AI agent patterns through algorithmic trading:
- No guarantees of profitability (substantial risk of loss)
- Open source and free for learning
- YouTube-driven development with weekly updates ([@moondevonyt](https://www.youtube.com/@moondevonyt))
- Community-supported via [Discord](https://discord.gg/8UPuVZ53bh)
- No token associated with project (avoid scams - Moon Dev will never DM you)

The goal is to democratize AI agent development and show practical multi-agent orchestration patterns that can be applied beyond trading.

## Recent Updates

**Major Features Added**:
- ✅ OpenRouter integration (200+ models)
- ✅ xAI Grok integration
- ✅ Swarm consensus (6-model voting)
- ✅ MetaTrader 5 support (forex/stocks)
- ✅ Polymarket integration
- ✅ Trading hours management
- ✅ Health monitoring system
- ✅ Docker containerization
- ✅ Production deployment guides
- ✅ Comprehensive test suite
- ✅ RBI parallel backtesting with web dashboard
- ✅ Websearch agent for strategy research
- ✅ 50+ agents (growing weekly)

**Coming Soon** (see `README.md` ROADMAP):
- Base Chain integration
- HyperLiquid spot trading
- Trending agent
- Position sizing agent
- Regime detection agents
- Extended exchange support

---

*Built with 💖 by Moon Dev 🌙 - Pioneering the future of AI-powered trading*

**Last Updated**: 2025-11-25

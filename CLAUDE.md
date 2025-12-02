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
│   ├── nice_funcs_hyperliquid.py  # HyperLiquid-specific utilities
│   ├── nice_funcs_hl.py     # Backwards compatibility alias for nice_funcs_hyperliquid
│   ├── nice_funcs_mt5.py    # 787 lines MetaTrader 5 utilities
│   └── ezbot.py             # Legacy trading controller
├── docs/                    # Agent-specific documentation (42+ docs)
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
- `volume_agent` - Volume spike detection on HyperLiquid with SwarmAgent analysis
- `funding_agent` - Funding rates analysis across exchanges
- `funding_agent_2` - Enhanced funding rate scanner with AI voice alerts (all HyperLiquid symbols)
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
- `scraper_agent` - Batch URL processing with Selenium and SwarmAgent AI analysis

**Specialized**:
- `sniper_agent` - New Solana token launch detection and sniping
- `solana_agent` - Solana meme token analysis
- `tx_agent` - Transaction monitoring for copy list
- `million_agent` - Uses Gemini's million-token context window
- `tiktok_agent` - TikTok scraping for consumer data (social arbitrage)
- `compliance_agent` - Ad compliance checking for Facebook/TikTok
- `housecoin_agent` - DCA agent with AI confirmation (1 House = 1 Housecoin)
- `polymarket_agent` - Prediction market trading on Polymarket
- `polymarket_websearch_agent` - Enhanced Polymarket integration with web search
- `swarm_agent` - 7-model parallel consensus (Claude Sonnet, Claude Opus, GPT, Gemini, Grok, DeepSeek, DeepSeek-R1)
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

**🚀 Performance & Optimization Utilities** (`src/utils/` - **NEW**):
- `position_sizing.py` - Kelly Criterion & advanced position sizing algorithms
  - Kelly Criterion optimization (full, half, quarter Kelly)
  - Fixed fraction sizing
  - Volatility-adjusted sizing
  - Risk per trade calculation
  - Used by trading agents for optimal position sizing

- `cache_manager.py` - Multi-tier intelligent caching layer (90% API reduction)
  - LRU memory cache (fastest, first-tier)
  - Redis cache (persistent, optional second-tier)
  - Decorator pattern: `@cache_manager.cached(ttl_seconds=60)`
  - **Performance**: 10,000x faster cache hits vs API calls
  - **Cost savings**: ~$50-100/month in API fees

- `async_api_client.py` - High-performance async HTTP client (7x faster than requests)
  - httpx-based with connection pooling
  - Parallel request support: 10 requests in ~1.4s vs ~10s
  - Automatic retries with exponential backoff
  - Rate limiting protection
  - Integrated with cache_manager

- `portfolio_optimizer.py` - Advanced portfolio optimization using Modern Portfolio Theory
  - Mean-Variance optimization (Markowitz)
  - Risk Parity / Equal Risk Contribution
  - Hierarchical Risk Parity (HRP)
  - CVaR (Conditional Value at Risk) minimization
  - Maximum Sharpe, Minimum Volatility strategies
  - Uses skfolio library when available (fallback to simple optimization)
  - Calculate portfolio metrics (Sharpe, max drawdown, VaR, CVaR)
  - Rebalancing suggestions with configurable thresholds

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

### 🚀 Using Kelly Criterion Position Sizing (NEW)
```python
from src.utils.position_sizing import kelly_criterion, position_size_usd, quarter_kelly

# Calculate optimal position size
kelly_frac = quarter_kelly(
    win_rate=0.60,       # 60% win rate from backtests
    avg_win_pct=0.15,    # Average win: +15%
    avg_loss_pct=0.10    # Average loss: -10%
)
# Result: 0.0833 (8.33% of capital)

# Convert to USD with safety caps
position_usd = position_size_usd(
    kelly_fraction=kelly_frac,
    capital_usd=10000,
    max_position_pct=0.20  # Never risk more than 20%
)
# Result: $833.33

# Use in trading agent
from src.agents.trading_agent import execute_trade
execute_trade(token_address, amount_usd=float(position_usd))
```

### 🚀 Using Intelligent Caching (NEW)
```python
from src.utils.cache_manager import cache_manager

# Method 1: Decorator pattern (recommended)
@cache_manager.cached(ttl_seconds=60, key_prefix="price")
def get_token_price(address):
    return expensive_api_call(address)

# First call: fetches from API (1 second)
price1 = get_token_price("ABC123")

# Second call: returns cached (0.001 second) - 1000x faster!
price2 = get_token_price("ABC123")

# Method 2: Direct caching
result = cache_manager.get_or_compute(
    key="token:overview:ABC123",
    compute_func=lambda: fetch_token_overview("ABC123"),
    ttl_seconds=300  # Cache for 5 minutes
)

# Show cache statistics
cache_manager.print_stats()
# Memory Cache Hit Rate: 85.2%
# Overall Cache Hit Rate: 92.1%
# API cost savings: ~$80/month
```

### 🚀 Using Async HTTP Client (NEW)
```python
from src.utils.async_api_client import AsyncAPIClient
import asyncio

async def fetch_multiple_tokens():
    client = AsyncAPIClient()

    # Fetch 10 tokens in parallel (1.4s vs 10s sequential)
    urls = [f"https://api.birdeye.so/token/{addr}" for addr in token_addresses]
    results = await client.get_multiple(urls)

    # With caching (even faster!)
    token_data = await client.get_cached(
        url="https://api.birdeye.so/token/ABC123",
        ttl_seconds=60
    )

    await client.close()
    return results

# Run async code
results = asyncio.run(fetch_multiple_tokens())
```

### 🚀 Using Portfolio Optimizer (NEW)
```python
from src.utils.portfolio_optimizer import PortfolioOptimizer
import pandas as pd

# Create optimizer
optimizer = PortfolioOptimizer(
    method='cvar',  # Minimize tail risk
    risk_measure='cvar'
)

# Prepare historical returns data
returns = pd.DataFrame({
    'BTC': [...],  # Daily returns
    'ETH': [...],
    'SOL': [...]
})

# Optimize portfolio weights
weights = optimizer.optimize(
    returns_df=returns,
    constraints={'min_weight': 0.10, 'max_weight': 0.40}
)
# Result: {'BTC': 0.40, 'ETH': 0.35, 'SOL': 0.25}

# Calculate portfolio metrics
metrics = optimizer.calculate_portfolio_metrics(returns, weights)
print(f"Expected Return: {metrics['expected_return']:.2%}")
print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
print(f"Max Drawdown: {metrics['max_drawdown']:.2%}")

# Suggest rebalancing trades
current_weights = {'BTC': 0.50, 'ETH': 0.30, 'SOL': 0.20}
trades = optimizer.suggest_rebalancing(current_weights, weights, threshold=0.05)
# Result: {'BTC': -0.10, 'ETH': 0.05, 'SOL': 0.05} (buy ETH/SOL, sell BTC)
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
- `volume_agent.md` - Volume spike detection guide
- `volume_agent_README.md` - Extended volume agent documentation
- `scraper_agent.md` - Scraper agent usage
- `giveaway_agent.md` - Giveaway agent guide
- `hyperliquid.md` - HyperLiquid integration overview
- `HYPERLIQUID_SETUP.md` - HyperLiquid setup instructions
- `PATH_FIXES_README.md` - Path configuration fixes
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
- ✅ Swarm consensus (upgraded to 7-model voting with Claude Opus 4.5)
- ✅ MetaTrader 5 support (forex/stocks)
- ✅ Polymarket integration with websearch enhancement
- ✅ Trading hours management
- ✅ Health monitoring system
- ✅ Docker containerization
- ✅ Production deployment guides
- ✅ Comprehensive test suite
- ✅ RBI parallel backtesting with web dashboard
- ✅ Websearch agent for strategy research
- ✅ 50+ agents (growing weekly)

**Latest Upstream Merge (2025-12-01)**:
- ✅ New agents: volume_agent, funding_agent_2, scraper_agent, polymarket_websearch_agent
- ✅ Claude Opus 4.5 support in SwarmAgent (7-model consensus)
- ✅ Enhanced HyperLiquid utilities (nice_funcs_hyperliquid.py)
- ✅ Backwards compatibility maintained (nice_funcs_hl.py alias)
- ✅ Improved liquidation_agent and polymarket_agent
- ✅ 7 new documentation files
- ✅ Security fixes: API key protection, wallet address environment variables, input validation layer

**Coming Soon** (see `README.md` ROADMAP):
- Base Chain integration
- HyperLiquid spot trading
- Trending agent
- Position sizing agent
- Regime detection agents
- Extended exchange support

---

*Built with 💖 by Moon Dev 🌙 - Pioneering the future of AI-powered trading*

**Last Updated**: 2025-12-01

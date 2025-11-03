# SKILL.md - Agent Skills & Capabilities Reference

## Overview

This document catalogs all agent skills, capabilities, and usage patterns in the Moon Dev AI Agents system. Use this as your guide for understanding what each agent can do, when to use them, and how to extend their capabilities.

## Table of Contents

- [Agent Skill Categories](#agent-skill-categories)
- [Skill Matrix](#skill-matrix)
- [Agent Profiles](#agent-profiles)
- [Skill Development Patterns](#skill-development-patterns)
- [When to Use Which Agent](#when-to-use-which-agent)
- [Extending Agent Skills](#extending-agent-skills)
- [Skill Dependencies](#skill-dependencies)

---

## Agent Skill Categories

### 🎯 Core Trading Skills
Agents that execute trading decisions, manage positions, and interact with markets.

**Key Capabilities:**
- Market order execution (buy/sell)
- Position sizing and allocation
- Portfolio rebalancing
- Entry/exit timing
- Slippage management

**Agents with these skills:**
- `trading_agent.py` - LLM-based trading decisions
- `strategy_agent.py` - Strategy execution framework
- `copybot_agent.py` - Mirror trading from top performers
- `sniper_agent.py` - Fast token launch trading
- `fundingarb_agent.py` - Funding rate arbitrage

---

### 🛡️ Risk Management Skills
Agents that protect capital and enforce safety limits.

**Key Capabilities:**
- Portfolio value calculation
- PnL tracking (USD and percentage)
- Circuit breaker enforcement
- Position limit monitoring
- AI-powered risk override decisions
- Balance logging and tracking

**Agents with these skills:**
- `risk_agent.py` - Primary risk management agent

---

### 📊 Market Analysis Skills
Agents that gather and analyze market data.

**Key Capabilities:**
- Technical indicator calculation (MA, RSI, MACD, etc.)
- OHLCV data collection and processing
- Price action analysis
- Volume pattern recognition
- Trend identification
- Multi-timeframe analysis

**Agents with these skills:**
- `trading_agent.py` - Technical analysis for decisions
- `chartanalysis_agent.py` - Visual chart analysis
- `whale_agent.py` - Large transaction monitoring
- `liquidation_agent.py` - Liquidation event tracking
- `funding_agent.py` - Funding rate monitoring

---

### 🧠 Strategy Development Skills
Agents that research, create, and test trading strategies.

**Key Capabilities:**
- YouTube video transcript extraction
- PDF strategy document parsing
- Strategy logic extraction from content
- Backtesting code generation
- Strategy debugging and optimization
- Performance metric calculation
- Multi-model AI reasoning (GPT-5, DeepSeek, Claude, Ollama)

**Agents with these skills:**
- `rbi_agent.py` (v1, v2, v3) - Research-Backtest-Implement pipeline
- `research_agent.py` - Strategy research and idea generation
- `backtest_runner.py` - Backtest execution

---

### 📡 Data Collection Skills
Agents that gather real-time market intelligence.

**Key Capabilities:**
- Twitter/X sentiment analysis
- Whale wallet tracking
- Liquidation event monitoring
- Funding rate collection
- Token discovery (new launches)
- CoinGecko API integration
- BirdEye API integration
- Moon Dev API integration

**Agents with these skills:**
- `sentiment_agent.py` - Twitter sentiment tracking
- `whale_agent.py` - Whale activity monitoring
- `liquidation_agent.py` - Liquidation data collection
- `funding_agent.py` - Funding rate tracking
- `new_or_top_agent.py` - New token discovery
- `coingecko_agent.py` - CoinGecko data integration
- `tx_agent.py` - Transaction monitoring

---

### 🎨 Content Creation Skills
Agents that produce media and communication content.

**Key Capabilities:**
- Video clipping and editing
- Audio generation (ElevenLabs, OpenAI TTS)
- Twitter thread creation
- Real-time video capture (OBS)
- Image/screenshot analysis
- Tweet optimization
- Chat moderation and responses

**Agents with these skills:**
- `clips_agent.py` - Long-form to short-form video conversion
- `realtime_clips_agent.py` - Real-time stream clipping
- `tweet_agent.py` - Twitter content generation
- `video_agent.py` - Video production from text
- `chat_agent.py` - YouTube live chat moderation
- `tiktok_agent.py` - TikTok content analysis

---

### 📞 Communication Skills
Agents that interact with users and external systems.

**Key Capabilities:**
- Voice synthesis (OpenAI TTS)
- Phone call handling
- Live chat monitoring
- Question answering
- Alert generation
- Voice announcements

**Agents with these skills:**
- `phone_agent.py` - Phone call automation
- `chat_agent.py` - Chat moderation and responses
- `whale_agent.py` - Voice alerts for whale activity
- `sentiment_agent.py` - Voice alerts for sentiment shifts
- `funding_agent.py` - Voice alerts for funding opportunities
- `liquidation_agent.py` - Voice alerts for liquidations

---

### 🔍 Specialized Skills
Unique agent capabilities that don't fit standard categories.

**Key Capabilities:**
- Arbitrage opportunity detection (listing arbitrage)
- Compliance checking (ad content)
- Focus/productivity tracking
- Context window utilization (1M+ tokens)
- Social data extraction
- Token rugpull detection
- Copy trader analysis

**Agents with these skills:**
- `listingarb_agent.py` - Pre-listing arbitrage opportunities
- `compliance_agent.py` - Ad compliance checking
- `focus_agent.py` - Productivity monitoring
- `million_agent.py` - Large context processing
- `tiktok_agent.py` - Social trend analysis
- `solana_agent.py` - Meme token analysis

---

## Skill Matrix

| Agent | Trading | Risk Mgmt | Analysis | Strategy Dev | Data Collection | Content | Communication | Specialized |
|-------|---------|-----------|----------|--------------|-----------------|---------|---------------|-------------|
| `trading_agent` | ✅ Primary | ❌ | ✅ Technical | ❌ | ✅ OHLCV | ❌ | ❌ | ❌ |
| `risk_agent` | ❌ | ✅ Primary | ✅ PnL | ❌ | ❌ | ❌ | ❌ | ❌ |
| `strategy_agent` | ✅ Primary | ❌ | ✅ Signals | ✅ Execution | ❌ | ❌ | ❌ | ❌ |
| `rbi_agent` | ❌ | ❌ | ❌ | ✅ Primary | ❌ | ❌ | ❌ | ✅ Multi-source |
| `sentiment_agent` | ❌ | ❌ | ✅ Sentiment | ❌ | ✅ Twitter | ❌ | ✅ Voice | ❌ |
| `whale_agent` | ❌ | ❌ | ✅ Whale | ❌ | ✅ Blockchain | ❌ | ✅ Voice | ❌ |
| `liquidation_agent` | ❌ | ❌ | ✅ Liquids | ❌ | ✅ Exchanges | ❌ | ✅ Voice | ❌ |
| `funding_agent` | ❌ | ❌ | ✅ Funding | ❌ | ✅ Exchanges | ❌ | ✅ Voice | ❌ |
| `chartanalysis_agent` | ❌ | ❌ | ✅ Charts | ❌ | ✅ Charts | ❌ | ❌ | ❌ |
| `copybot_agent` | ✅ Copy | ❌ | ✅ Copybot | ❌ | ✅ API | ❌ | ❌ | ❌ |
| `clips_agent` | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ Video | ❌ | ✅ Clipping |
| `tweet_agent` | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ Twitter | ❌ | ❌ |
| `chat_agent` | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ Primary | ❌ |
| `phone_agent` | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ Phone | ❌ |
| `sniper_agent` | ✅ Snipe | ❌ | ✅ New Tokens | ❌ | ✅ Launches | ❌ | ❌ | ✅ Speed |
| `listingarb_agent` | ✅ Arb | ❌ | ✅ Pre-list | ❌ | ✅ CoinGecko | ❌ | ❌ | ✅ Arbitrage |
| `focus_agent` | ❌ | ❌ | ✅ Audio | ❌ | ✅ Mic | ❌ | ✅ Voice | ✅ Productivity |
| `compliance_agent` | ❌ | ❌ | ✅ Content | ❌ | ❌ | ❌ | ❌ | ✅ Compliance |

---

## Agent Profiles

### 🤖 Trading Agent (`trading_agent.py`)

**Primary Skill:** LLM-based trading decision making

**Capabilities:**
- Analyzes OHLCV data with technical indicators (MA20, MA40, RSI)
- Accepts strategy signals from Strategy Agent
- Generates BUY/SELL/NOTHING recommendations with confidence scores
- Calculates optimal portfolio allocations
- Executes position entries using `ai_entry()`
- Handles position exits with `chunk_kill()`
- Model-agnostic (supports xAI Grok, Claude, GPT, DeepSeek, Groq, Ollama)

**Input:** Market data (OHLCV), strategy signals (optional)

**Output:** Trading recommendations, portfolio allocations, executed trades

**Configuration:**
- `AI_MODEL_TYPE` - Model provider selection
- `AI_MODEL_NAME` - Specific model name
- `AI_TEMPERATURE` - Response randomness
- `AI_MAX_TOKENS` - Response length

**When to use:** When you need intelligent, context-aware trading decisions based on market conditions and optional strategy signals.

---

### 🛡️ Risk Agent (`risk_agent.py`)

**Primary Skill:** Portfolio risk management and circuit breakers

**Capabilities:**
- Calculates real-time portfolio value across all tokens
- Tracks PnL (both USD and percentage)
- Enforces `MAX_LOSS_USD`, `MAX_GAIN_USD`, `MINIMUM_BALANCE_USD`
- AI-powered override decisions (can keep positions open if strong reversal signals)
- Logs portfolio balance every N hours
- Closes all monitored positions when limits breached
- Supports both Claude and DeepSeek models

**Input:** Portfolio holdings, position data, market data (15m and 5m timeframes)

**Output:** Risk assessments, position close orders, override decisions

**Configuration:**
- `USE_PERCENTAGE` - Toggle percentage vs USD limits
- `MAX_LOSS_PERCENT/USD` - Maximum allowable loss
- `MAX_GAIN_PERCENT/USD` - Maximum gain before taking profits
- `MINIMUM_BALANCE_USD` - Stop-out threshold
- `USE_AI_CONFIRMATION` - Enable/disable AI override consultation
- `MODEL_OVERRIDE` - Use DeepSeek for risk decisions

**When to use:** Run continuously (main loop first agent). Essential for capital preservation.

---

### 📊 Strategy Agent (`strategy_agent.py`)

**Primary Skill:** User-defined strategy execution framework

**Capabilities:**
- Loads strategies from `src/strategies/` folder
- Executes `generate_signals()` method on each strategy
- Collects market data for strategy analysis
- Aggregates signals from multiple strategies
- Passes signals to Trading Agent for execution
- Supports custom strategy inheritance from `BaseStrategy`

**Input:** Token addresses, market data

**Output:** Strategy signals (action, confidence, reasoning)

**Strategy Template:**
```python
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

**When to use:** When you have specific trading strategies to test or deploy.

---

### 🧠 RBI Agent (`rbi_agent.py`, `rbi_agent_v2.py`, `rbi_agent_v3.py`)

**Primary Skill:** Automated strategy research, backtesting, and implementation

**Capabilities:**
- **Research Phase:**
  - Extracts YouTube video transcripts
  - Parses PDF trading documents
  - Analyzes text-based strategy descriptions
  - Generates unique strategy names
  - Uses multi-model approach (GPT-5, DeepSeek, Claude, Ollama)

- **Backtest Phase:**
  - Generates `backtesting.py` compatible code
  - Implements entry/exit logic
  - Adds risk management rules
  - Uses TA-Lib or pandas-ta for indicators
  - Wraps all indicators in `self.I()`

- **Debug Phase:**
  - Fixes syntax errors
  - Corrects position sizing (rounds to integers)
  - Ensures proper stop loss/take profit levels
  - Preserves strategy logic

- **Package Phase:**
  - Removes all `backtesting.lib` imports
  - Replaces with talib/pandas-ta equivalents
  - Converts crossover functions to array comparisons

**Input:**
- YouTube URLs (auto-extracts transcript)
- PDF URLs (auto-extracts text)
- Text strategy descriptions
- `src/data/rbi/ideas.txt` file

**Output:**
- Research analysis: `src/data/rbi/MM_DD_YYYY/research/`
- Initial backtest: `src/data/rbi/MM_DD_YYYY/backtests/`
- Package-optimized: `src/data/rbi/MM_DD_YYYY/backtests_package/`
- Final backtest: `src/data/rbi/MM_DD_YYYY/backtests_final/`

**Model Configuration:**
```python
RESEARCH_CONFIG = {"type": "openai", "name": "gpt-5"}
BACKTEST_CONFIG = {"type": "openai", "name": "gpt-5"}
DEBUG_CONFIG = {"type": "openai", "name": "gpt-5"}
PACKAGE_CONFIG = {"type": "openai", "name": "gpt-5"}
```

**Cost:** ~$0.027 per backtest (with DeepSeek), ~6 minutes execution time

**When to use:**
- When you find interesting strategies on YouTube
- When you have PDF strategy documents to implement
- When you want to rapidly prototype strategy ideas
- When you need to backtest many ideas quickly

**Version Differences:**
- v1: Original implementation
- v2: Improved error handling and multi-model support
- v3: Enhanced iteration with return % targets

---

### 🐋 Whale Agent (`whale_agent.py`)

**Primary Skill:** Large transaction monitoring and alerts

**Capabilities:**
- Monitors blockchain for large transactions (>$100k default)
- Analyzes whale activity patterns
- Generates voice alerts using OpenAI TTS
- Tracks wallet addresses of interest
- Provides context on whale's trading history
- Configurable threshold amounts

**Input:** Blockchain transaction data, whale wallet list

**Output:** Voice announcements, whale activity logs

**Configuration:**
- `WHALE_THRESHOLD_USD` - Minimum transaction size to alert
- `VOICE_MODEL` - TTS model (tts-1 or tts-1-hd)
- `VOICE_NAME` - Voice selection (nova, alloy, echo, fable, onyx, shimmer)
- `VOICE_SPEED` - Speech rate (0.25 to 4.0)

**When to use:** When you want real-time alerts on significant market moves by large players.

---

### 📰 Sentiment Agent (`sentiment_agent.py`)

**Primary Skill:** Twitter sentiment analysis with voice alerts

**Capabilities:**
- Scrapes Twitter using twikit
- Analyzes sentiment using HuggingFace transformers
- Tracks specified tokens (Bitcoin, Ethereum, Solana, etc.)
- Calculates sentiment scores (-1 to +1 scale)
- Logs sentiment history to CSV
- Voice announcements for extreme sentiment (>0.4 threshold)
- Browser-like headers to avoid detection

**Input:** Twitter credentials, token list

**Output:** Sentiment scores, historical CSV, voice alerts

**Configuration:**
- `TOKENS_TO_TRACK` - List of tokens to monitor
- `TWEETS_PER_RUN` - Number of tweets to analyze
- `SENTIMENT_ANNOUNCE_THRESHOLD` - Voice alert trigger level
- `CHECK_INTERVAL_MINUTES` - Update frequency

**Setup Required:**
1. Run `src/scripts/twitter_login.py` to generate `cookies.json`
2. Add Twitter credentials to `.env`

**When to use:** When you want to gauge market sentiment and catch extreme mood shifts.

---

### 💧 Liquidation Agent (`liquidation_agent.py`)

**Primary Skill:** Liquidation event monitoring across exchanges

**Capabilities:**
- Tracks liquidation events (15min, 1hr, 4hr windows)
- Analyzes liquidation spikes using AI
- Voice alerts for significant liquidations
- Cross-exchange aggregation
- Provides technical context (support/resistance levels)
- Detects cascade liquidation risk

**Input:** Exchange liquidation APIs (via Moon Dev API)

**Output:** Liquidation analysis, voice alerts, opportunity assessments

**When to use:** To identify potential reversal points and high volatility periods.

---

### 💸 Funding Agent (`funding_agent.py`)

**Primary Skill:** Funding rate monitoring and arbitrage detection

**Capabilities:**
- Monitors funding rates across exchanges
- Identifies extreme funding situations
- AI analysis of funding rate opportunities
- Voice alerts for arbitrage setups
- Technical context for funding trades
- Historical funding rate tracking

**Input:** Exchange funding rate APIs

**Output:** Funding analysis, voice alerts, trade opportunities

**When to use:** For funding rate arbitrage and understanding market positioning.

---

### 📈 Chart Analysis Agent (`chartanalysis_agent.py`)

**Primary Skill:** Visual chart analysis using AI

**Capabilities:**
- Accepts chart images or generates from data
- Analyzes price action patterns
- Identifies support/resistance levels
- Detects chart patterns (head & shoulders, triangles, etc.)
- Provides BUY/SELL/NOTHING recommendations
- Explains technical reasoning

**Input:** Chart images, OHLCV data

**Output:** Trading recommendations with technical analysis

**When to use:** When you want AI to "see" the chart like a human trader would.

---

### 🎥 Clips Agent (`clips_agent.py`)

**Primary Skill:** Long-form video to short-form clip conversion

**Capabilities:**
- Extracts YouTube video transcripts
- Identifies interesting/valuable segments
- Cuts video clips (5 minutes to 2 hours)
- Processes local video files
- Automates clip creation workflow
- Integration with CapCut workflow

**Input:**
- YouTube URLs
- Local video files in `src/data/videos/raw_clips/`

**Output:** Edited clips in `src/data/videos/finished_vids/`

**Monetization:** $69 per 10k views (increases with volume)

**When to use:** To create monetizable short-form content from long educational videos.

---

### 💬 Chat Agent (`chat_agent.py`)

**Primary Skill:** YouTube live stream chat moderation

**Capabilities:**
- Monitors YouTube live chat in real-time
- Answers common questions automatically
- Moderates spam and inappropriate content
- Maintains FAQ knowledge base
- Responds with personality/style consistency
- Logs all interactions

**Input:** YouTube live stream ID, FAQ database

**Output:** Chat responses, moderation actions, interaction logs

**When to use:** During live streams to handle chat at scale while you focus on content.

---

### 📞 Phone Agent (`phone_agent.py`)

**Primary Skill:** Automated phone call handling

**Capabilities:**
- Answers incoming calls
- Uses speech recognition (STT)
- Generates voice responses (TTS)
- Routes calls based on intent
- Handles common questions
- Logs call transcripts

**Input:** Twilio phone number, call configuration

**Output:** Call handling, transcripts, caller intent

**When to use:** To automate customer support or information inquiries via phone.

---

### ⚡ Sniper Agent (`sniper_agent.py`)

**Primary Skill:** Fast execution on new token launches

**Capabilities:**
- Monitors for new Solana token launches
- Rapid analysis of token characteristics
- Fast execution (snipe buys)
- Rugpull detection
- Liquidity checks
- Contract verification

**Input:** Solana blockchain events, new token addresses

**Output:** Buy orders on promising launches, risk assessments

**When to use:** For early entry on new token launches (high risk/reward).

---

### 🔀 Listing Arbitrage Agent (`listingarb_agent.py`)

**Primary Skill:** Pre-listing arbitrage opportunity detection

**Capabilities:**
- Identifies tokens on CoinGecko before major exchange listings
- Parallel AI analysis (technical + fundamental)
- Predicts listing probability
- Calculates risk/reward ratios
- Monitors listing announcements
- Position sizing recommendations

**Input:** CoinGecko API, exchange listing patterns

**Output:** Pre-listing opportunities, analysis reports

**When to use:** To capture gains from exchange listing announcements.

---

### 🧘 Focus Agent (`focus_agent.py`)

**Primary Skill:** Productivity monitoring via audio sampling

**Capabilities:**
- Randomly samples audio during work sessions
- Analyzes audio for focus indicators
- Provides focus scores
- Voice alerts when focus drops
- Integrates with voice-to-code workflows
- ~$10/month operating cost

**Input:** Microphone audio, sampling configuration

**Output:** Focus scores, productivity alerts

**When to use:** During coding sessions to maintain productivity.

---

### ✅ Compliance Agent (`compliance_agent.py`)

**Primary Skill:** Ad content compliance checking

**Capabilities:**
- Analyzes ad copy for compliance issues
- Checks Facebook ad requirements
- TikTok compliance (coming soon)
- Identifies restricted claims
- Suggests compliant alternatives
- Reduces ad rejection rates

**Input:** Ad copy, platform (Facebook/TikTok)

**Output:** Compliance assessment, suggested edits

**When to use:** Before submitting ads to avoid rejections.

---

### 🌐 Million Agent (`million_agent.py`)

**Primary Skill:** Large context window utilization (1M+ tokens)

**Capabilities:**
- Processes entire codebases
- Analyzes long documents
- Maintains context across extended interactions
- Uses Gemini's extended context
- Knowledge base integration

**Input:** Large text documents, full codebases

**Output:** Analysis with full context retention

**When to use:** When you need to analyze very large documents or entire projects.

---

### 📱 TikTok Agent (`tiktok_agent.py`)

**Primary Skill:** Social trend analysis and data extraction

**Capabilities:**
- Scrolls TikTok feed
- Captures screenshots of videos + comments
- Extracts consumer sentiment
- Identifies trending topics
- Social arbitrage opportunities
- Feeds data into trading algorithms

**Input:** TikTok account, search terms

**Output:** Social trend data, consumer insights

**When to use:** For social arbitrage trading based on viral trends.

---

### 🎯 TX Agent (`tx_agent.py`)

**Primary Skill:** Transaction monitoring for specific wallets

**Capabilities:**
- Watches transactions from copy list
- Prints transaction details
- Optional auto-tab open for quick analysis
- Real-time alerts
- Integration with copy trading strategy

**Input:** Wallet addresses to monitor

**Output:** Transaction alerts, trade signals

**When to use:** When copy trading successful wallets.

---

### 🪙 Solana Agent (`solana_agent.py`)

**Primary Skill:** Meme token analysis on Solana

**Capabilities:**
- Combines sniper and TX agent data
- Analyzes meme token characteristics
- Social signal integration
- Community analysis
- Risk assessment for meme plays

**Input:** New token launches, social signals

**Output:** Meme token opportunities, risk ratings

**When to use:** For meme coin trading on Solana.

---

### 🔬 Research Agent (`research_agent.py`)

**Primary Skill:** Strategy idea generation

**Capabilities:**
- Fills `ideas.txt` for RBI Agent
- Browses trading communities
- Identifies promising strategies
- Curates YouTube videos
- Finds trading PDFs
- Automates research pipeline

**Input:** Research sources, search criteria

**Output:** Populated `ideas.txt` file

**When to use:** To automate strategy discovery and feed RBI Agent indefinitely.

---

### 🎬 Realtime Clips Agent (`realtime_clips_agent.py`)

**Primary Skill:** Live stream clipping with OBS

**Capabilities:**
- Captures live stream via OBS
- Creates clips in real-time
- Immediate clip availability
- Lower latency than post-processing
- Integration with streaming workflow

**Input:** OBS stream, clip triggers

**Output:** Real-time video clips

**When to use:** During live streams for instant clip creation.

---

## Skill Development Patterns

### Pattern 1: BaseAgent Inheritance

All agents inherit from `BaseAgent` class:

```python
from src.agents.base_agent import BaseAgent

class YourAgent(BaseAgent):
    def __init__(self):
        super().__init__('your_agent_type')
        # Your initialization

    def run(self):
        # Your main logic
        pass
```

### Pattern 2: LLM Integration via Model Factory

Use the unified model factory for all LLM calls:

```python
from src.models.model_factory import ModelFactory

# Initialize model
model = ModelFactory.create_model('anthropic')  # or 'openai', 'deepseek', 'groq', etc.

# Generate response
response = model.generate_response(
    system_prompt="You are a trading AI",
    user_content="Analyze this data: ...",
    temperature=0.7,
    max_tokens=1000
)
```

### Pattern 3: Data Collection

Standard pattern for gathering market data:

```python
from src import nice_funcs as n

# Get token overview
overview = n.token_overview(token_address)

# Get OHLCV data
ohlcv = n.get_ohlcv_data(token_address, timeframe='1H', days_back=3)

# Get current price
price = n.token_price(token_address)

# Get position
position = n.get_position(token_address)
```

### Pattern 4: Trading Execution

Standard pattern for executing trades:

```python
from src import nice_funcs as n
from src.config import *

# Buy position
n.market_buy(token_address, amount_usd)

# Sell position
n.market_sell(token_address, amount_usd)

# Close position completely
n.chunk_kill(token_address, max_usd_order_size, slippage)

# AI-powered entry
n.ai_entry(token_address, amount_usd)
```

### Pattern 5: Voice Alerts

Standard pattern for voice announcements:

```python
import openai
from pathlib import Path

def announce(text):
    """Generate and play voice announcement"""
    response = openai.audio.speech.create(
        model="tts-1",  # or "tts-1-hd"
        voice="nova",   # alloy, echo, fable, onyx, nova, shimmer
        input=text
    )

    # Save and play audio
    speech_file = Path("temp_speech.mp3")
    response.stream_to_file(speech_file)
    # Play audio (platform-specific)
```

### Pattern 6: Data Storage

Standard pattern for storing agent outputs:

```python
import pandas as pd
from pathlib import Path

# Create data directory
data_dir = Path("src/data/your_agent")
data_dir.mkdir(parents=True, exist_ok=True)

# Save DataFrame
df.to_csv(data_dir / "output.csv", index=False)

# Save JSON
import json
with open(data_dir / "output.json", 'w') as f:
    json.dump(data, f, indent=2)
```

---

## When to Use Which Agent

### Scenario: I want to execute trades based on technical analysis
**Use:** `trading_agent.py`
- Analyzes OHLCV data with technical indicators
- Provides BUY/SELL/NOTHING recommendations
- Executes portfolio allocations

### Scenario: I have a specific trading strategy to implement
**Use:** `strategy_agent.py` + create strategy in `src/strategies/`
- Define your strategy logic
- Strategy Agent executes it
- Integrates with Trading Agent

### Scenario: I found a strategy on YouTube I want to test
**Use:** `rbi_agent.py`
- Add YouTube URL to `src/data/rbi/ideas.txt`
- Automatically extracts, codes, and backtests strategy
- Gets backtested code ready to run

### Scenario: I want to protect my capital from large losses
**Use:** `risk_agent.py`
- Run continuously in main loop (first agent)
- Enforces PnL limits
- AI-powered override decisions

### Scenario: I want to know when whales are moving
**Use:** `whale_agent.py`
- Real-time whale transaction monitoring
- Voice alerts for large moves
- Wallet tracking

### Scenario: I want to gauge market sentiment on Twitter
**Use:** `sentiment_agent.py`
- Real-time Twitter sentiment analysis
- Voice alerts for extreme sentiment
- Historical tracking

### Scenario: I want to catch liquidation cascade opportunities
**Use:** `liquidation_agent.py`
- Monitors liquidations across exchanges
- Voice alerts for spikes
- Reversal opportunity detection

### Scenario: I want to trade funding rate arbitrage
**Use:** `funding_agent.py` + `fundingarb_agent.py`
- Monitors funding rates
- Identifies arbitrage opportunities
- Voice alerts for setups

### Scenario: I want to analyze a chart like a human would
**Use:** `chartanalysis_agent.py`
- Visual chart pattern recognition
- Technical analysis with reasoning
- BUY/SELL/NOTHING with explanation

### Scenario: I want to copy successful traders
**Use:** `copybot_agent.py` + `tx_agent.py`
- Monitors wallet transactions
- Executes copycat trades
- Risk filtering

### Scenario: I want to snipe new token launches
**Use:** `sniper_agent.py` + `solana_agent.py`
- Fast execution on launches
- Rugpull detection
- Meme token analysis

### Scenario: I want to catch pre-listing arbitrage
**Use:** `listingarb_agent.py`
- CoinGecko monitoring
- Listing prediction
- Position before announcement

### Scenario: I want to create short videos from long content
**Use:** `clips_agent.py`
- Automated clipping
- Monetization potential ($69 per 10k views)

### Scenario: I want to moderate my YouTube live chat
**Use:** `chat_agent.py`
- Real-time moderation
- Automated responses
- FAQ handling

### Scenario: I need to handle phone calls automatically
**Use:** `phone_agent.py`
- Call answering
- Intent routing
- Transcript logging

### Scenario: I want to maintain focus while coding
**Use:** `focus_agent.py`
- Productivity monitoring
- Focus alerts
- Voice-to-code optimization

### Scenario: I need to check ad compliance
**Use:** `compliance_agent.py`
- Facebook/TikTok compliance
- Reduces rejections
- Compliant alternative suggestions

### Scenario: I need to analyze a very large document
**Use:** `million_agent.py`
- 1M+ token context window
- Full codebase analysis
- Extended context retention

### Scenario: I want to track social trends for trading
**Use:** `tiktok_agent.py`
- Social arbitrage
- Trend detection
- Consumer sentiment

---

## Extending Agent Skills

### Adding a New Skill to Existing Agent

1. **Identify the capability gap**
2. **Add the skill method to the agent class**
3. **Integrate with existing run() method**
4. **Update configuration if needed**
5. **Document in SKILL.md**

Example:

```python
class TradingAgent:
    # Existing methods...

    def calculate_sharpe_ratio(self, returns):
        """New skill: Calculate Sharpe Ratio"""
        mean_return = returns.mean()
        std_return = returns.std()
        sharpe = mean_return / std_return
        return sharpe

    def run(self):
        # Existing logic...

        # Use new skill
        returns = self.get_historical_returns()
        sharpe = self.calculate_sharpe_ratio(returns)
        print(f"Portfolio Sharpe Ratio: {sharpe:.2f}")
```

### Creating a New Agent with Custom Skills

1. **Inherit from BaseAgent**
2. **Implement required methods**
3. **Add to `src/agents/` directory**
4. **Make independently executable**
5. **Optionally integrate with `main.py`**

Template:

```python
"""
🌙 Moon Dev's [Your Agent Name]
Built with love by Moon Dev 🚀

Description: What this agent does

Skills:
- Skill 1
- Skill 2
- Skill 3
"""

from src.agents.base_agent import BaseAgent
from src.models.model_factory import ModelFactory
from src import nice_funcs as n
from src.config import *
from termcolor import cprint

class YourAgent(BaseAgent):
    def __init__(self):
        super().__init__('your_agent')

        # Initialize AI model
        self.model = ModelFactory.create_model('anthropic')

        # Your setup
        cprint("🌙 Your Agent initialized!", "green")

    def skill_1(self):
        """Description of skill 1"""
        # Implementation
        pass

    def skill_2(self):
        """Description of skill 2"""
        # Implementation
        pass

    def run(self):
        """Main execution logic"""
        try:
            # Your agent logic
            self.skill_1()
            self.skill_2()

        except Exception as e:
            cprint(f"❌ Error: {e}", "red")

def main():
    """Standalone execution"""
    agent = YourAgent()

    while True:
        try:
            agent.run()
            time.sleep(SLEEP_BETWEEN_RUNS_MINUTES * 60)
        except KeyboardInterrupt:
            cprint("\n👋 Shutting down...", "yellow")
            break

if __name__ == "__main__":
    main()
```

---

## Skill Dependencies

### Core Dependencies
All agents depend on:
- `src/config.py` - Global configuration
- `src/nice_funcs.py` - Shared trading utilities
- `src/models/model_factory.py` - LLM abstraction

### Trading Dependencies
Trading agents require:
- BirdEye API (`BIRDEYE_API_KEY`)
- Solana RPC endpoint (`RPC_ENDPOINT`)
- Wallet private key (`SOLANA_PRIVATE_KEY`)

### Analysis Dependencies
Analysis agents require:
- Market data APIs (BirdEye, CoinGecko)
- Moon Dev API (`MOONDEV_API_KEY`) for specialized data

### Content Dependencies
Content agents require:
- OpenAI API (`OPENAI_KEY`) for TTS
- ElevenLabs API for premium voice
- FFmpeg for video processing

### Communication Dependencies
Communication agents require:
- Twilio (phone agent)
- Twitter API credentials (sentiment, tweet agents)
- YouTube API (chat, clips agents)

### AI Model Dependencies

Agents can use any of these models via ModelFactory:

**Anthropic Claude:**
- `claude-3-5-haiku-latest` (fast, cheap)
- `claude-3-5-sonnet-latest` (balanced)
- `claude-3-opus-latest` (powerful)

**OpenAI:**
- `gpt-4o` (latest)
- `gpt-5` (newest)
- `o3` (reasoning)

**xAI:**
- `grok-4-fast-reasoning` (2M context, cheap)
- `grok-4-0709` (most intelligent)

**DeepSeek:**
- `deepseek-chat` (general use)
- `deepseek-reasoner` (complex reasoning)

**Groq:**
- `llama-3.3-70b-versatile` (fast inference)

**Google:**
- `gemini-pro` (large context)

**Ollama (Local):**
- `llama3.2` (local inference)
- `deepseek-r1` (local reasoning)

---

## Skill Composition & Chaining

Agents can compose their skills to create more complex behaviors:

### Example: Multi-Agent Signal Generation

```python
# main.py orchestrates multiple agents

# 1. Risk Agent checks if we can trade
risk_ok = risk_agent.run()

if risk_ok:
    # 2. Sentiment Agent provides market mood
    sentiment = sentiment_agent.get_current_sentiment()

    # 3. Whale Agent provides smart money flow
    whale_activity = whale_agent.get_recent_activity()

    # 4. Strategy Agent generates signals
    strategy_signals = strategy_agent.run()

    # 5. Trading Agent makes final decision
    # Combines all inputs
    trading_agent.run_trading_cycle(
        strategy_signals=strategy_signals,
        sentiment=sentiment,
        whale_activity=whale_activity
    )
```

### Example: RBI Research Pipeline

```python
# Research Agent → RBI Agent → Trading Agent

# 1. Research Agent finds strategies
research_agent.discover_strategies()  # Populates ideas.txt

# 2. RBI Agent processes ideas
rbi_agent.run()  # Creates backtests

# 3. Manual review of backtests
# 4. Implement best strategies in src/strategies/

# 5. Strategy Agent executes them
strategy_agent.run()
```

---

## Performance & Cost Optimization

### Model Selection by Task

**Fast/Cheap Tasks:** (sentiment, moderation, simple analysis)
- Groq with Llama 3.3 (extremely fast)
- Claude Haiku (fast, cheap)
- xAI Grok Fast Reasoning (cheap, 2M context)

**Balanced Tasks:** (trading decisions, strategy signals)
- Claude Sonnet (reliable, good reasoning)
- GPT-4o (versatile, good quality)

**Complex Reasoning:** (strategy research, deep analysis)
- DeepSeek Reasoner (excellent for complex logic)
- OpenAI o3 (strong reasoning)
- Claude Opus (highest quality)

**Large Context:** (full codebase analysis)
- Gemini Pro (1M+ tokens)
- xAI Grok (2M tokens)

**Local/Private:**
- Ollama with Llama 3.2 or DeepSeek-R1

### Cost Examples (Approximate)

- **Claude Haiku:** $0.25 per 1M input tokens
- **GPT-4o:** $2.50 per 1M input tokens
- **DeepSeek Chat:** $0.14 per 1M input tokens
- **DeepSeek Reasoner:** $0.55 per 1M input tokens
- **Groq:** Free tier available, very fast
- **xAI Grok Fast:** $0.50 per 1M input tokens
- **Ollama:** Free (runs locally)

### Optimization Tips

1. **Use cheaper models for simple tasks** (sentiment, moderation)
2. **Reserve expensive models for critical decisions** (trading, risk)
3. **Cache repetitive prompts** (reduce token usage)
4. **Use streaming for long responses** (better UX)
5. **Batch API calls when possible** (reduce overhead)
6. **Use local models for privacy-sensitive tasks** (Ollama)

---

## Skill Roadmap

### Planned Skills (Future Development)

**Advanced Risk Management:**
- Portfolio optimization (Markowitz, Kelly Criterion)
- Multi-asset correlation analysis
- Dynamic position sizing based on volatility

**Enhanced Analysis:**
- Order book depth analysis
- Market microstructure analysis
- Cross-exchange arbitrage detection

**New Communication Channels:**
- Discord bot integration
- Telegram bot integration
- Slack integration

**Advanced Content:**
- Automated thumbnail generation
- SEO optimization for video titles
- Multi-platform content distribution

**Strategy Development:**
- Genetic algorithm strategy optimization
- Automated hyperparameter tuning
- Walk-forward analysis

**Blockchain Integration:**
- Smart contract interaction
- On-chain analytics
- MEV opportunity detection

---

## Contributing New Skills

To contribute a new skill or agent:

1. **Fork the repository**
2. **Create your agent in `src/agents/`**
3. **Follow the patterns in this document**
4. **Keep code under 800 lines** (split if longer)
5. **Add comprehensive docstrings**
6. **Update SKILL.md with your agent profile**
7. **Test independently before PR**
8. **Submit pull request with description**

### Skill Contribution Checklist

- [ ] Agent inherits from BaseAgent
- [ ] Uses ModelFactory for LLM calls
- [ ] Independently executable (has `if __name__ == "__main__"`)
- [ ] Stores outputs in `src/data/agent_name/`
- [ ] Configuration options in `config.py` if needed
- [ ] Documented in SKILL.md
- [ ] Code under 800 lines
- [ ] Follows Moon Dev naming conventions (emoji + description)
- [ ] Error handling is minimal (show errors, don't hide)
- [ ] No synthetic data (uses real data or fails)

---

## Conclusion

This skill reference provides a comprehensive overview of all agent capabilities in the Moon Dev AI Agents system. Use it to:

- **Understand** what each agent can do
- **Choose** the right agent for your task
- **Extend** agents with new capabilities
- **Create** new agents following established patterns
- **Compose** multiple agents for complex workflows

Remember: Agents are specialized tools. The system's power comes from orchestrating multiple agents together, each contributing their unique skills to achieve your trading or automation goals.

**Moon Dev's Philosophy:** Simple agents with clear skills, composed together for emergent complexity. 🌙

---

*Built with love by Moon Dev 🚀*

*Last Updated: January 2025*

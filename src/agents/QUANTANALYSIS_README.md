# 🌙 QuantAnalysis Agent

**Multi-Agent Trading Analysis System inspired by QuantAgent Research (Y-Research, Stony Brook University)**

## Overview

The QuantAnalysis Agent is Moon Dev's implementation of a sophisticated multi-agent trading analysis system based on the QuantAgent research paper. It decomposes trading analysis into four specialized AI agents that work together to generate comprehensive trading recommendations.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   QUANTANALYSIS AGENT                        │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  INDICATOR   │  │   PATTERN    │  │    TREND     │     │
│  │    AGENT     │  │    AGENT     │  │    AGENT     │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                  │                  │              │
│         └──────────────────┼──────────────────┘              │
│                            │                                 │
│                   ┌────────▼────────┐                        │
│                   │   DECISION      │                        │
│                   │     AGENT       │                        │
│                   └────────┬────────┘                        │
│                            │                                 │
│                            ▼                                 │
│                  Trading Recommendation                      │
│              (BUY/SELL/NOTHING + Risk Params)               │
└─────────────────────────────────────────────────────────────┘
```

## The Four Agents

### 1. 🔵 Indicator Agent
**Purpose:** Compute and analyze technical indicators

**Indicators Used:**
- RSI (14 period) - Momentum assessment
- MACD (12, 26, 9) - Trend convergence/divergence
- Stochastic Oscillator (14, 3) - Momentum extremes
- SMA 20 & 50 - Trend confirmation

**Output:**
- Direction: BULLISH / BEARISH / NEUTRAL
- Summary of indicator signals
- Confidence level (0-100%)

### 2. 🟢 Pattern Agent
**Purpose:** Identify chart patterns and formations

**Analysis:**
- Chart pattern recognition (triangles, flags, head & shoulders, etc.)
- Support/resistance level identification
- Breakout/breakdown detection
- Pattern strength assessment

**Output:**
- Pattern detected (e.g., "Ascending Triangle", "Bull Flag")
- Direction bias: BULLISH / BEARISH / NEUTRAL
- Pattern description
- Confidence level (0-100%)

### 3. 🟡 Trend Agent
**Purpose:** Analyze trend direction, strength, and consolidation

**Analysis:**
- Overall trend direction (uptrend, downtrend, sideways)
- Trend strength assessment
- Moving average alignment
- Volatility analysis for consolidation zones

**Output:**
- Trend direction: UPTREND / DOWNTREND / SIDEWAYS
- Trend strength: STRONG / MODERATE / WEAK
- Trend description
- Confidence level (0-100%)

### 4. 🔴 Decision Agent
**Purpose:** Synthesize all agent outputs into final trading decision

**Synthesis:**
- Combines all three agent analyses
- Looks for confirmations across agents
- Assesses overall risk/reward
- Generates final trade recommendation

**Output:**
- Action: BUY / SELL / NOTHING
- Position type: LONG / SHORT
- Entry reasoning
- Stop-loss suggestion
- Take-profit suggestion
- Overall confidence (0-100%)

## Configuration

### In `config.py`:

```python
# QuantAnalysis Agent Settings 📊
ENABLE_QUANTANALYSIS = True  # Enable/disable the agent
QUANT_MIN_CONFIDENCE = 50    # Minimum confidence to act (0-100)
QUANT_HIGH_CONFIDENCE = 75   # High confidence threshold
QUANT_TIMEFRAME = '1H'       # Analysis timeframe: 15m, 1H, 4H, 1D
QUANT_LOOKBACK_BARS = 100    # Number of candles to analyze
QUANT_AGENT_WEIGHT = 0.4     # Weight in final decision (0.0-1.0)
```

### In `main.py`:

```python
ACTIVE_AGENTS = {
    'quantanalysis': True,  # Enable QuantAnalysis agent
    # ... other agents
}
```

## Usage

### Standalone Execution

```bash
# Run single analysis
python src/agents/quantanalysis_agent.py
```

### Integration with Trading Agent

The QuantAnalysis signals are automatically integrated into the trading_agent.py when enabled:

```python
from src.agents.quantanalysis_agent import QuantAnalysisAgent

# Initialize
quant_agent = QuantAnalysisAgent()

# Analyze a symbol
analysis = quant_agent.analyze(
    symbol="BTC",
    timeframe="1H",
    bars=100
)

# Use results
if analysis and analysis['action'] != 'NOTHING':
    print(f"Signal: {analysis['action']}")
    print(f"Confidence: {analysis['confidence']}%")
    print(f"Reasoning: {analysis['reasoning']}")
```

### Via Main Orchestrator

```bash
# Enable in config.py: ENABLE_QUANTANALYSIS = True
# Enable in main.py: ACTIVE_AGENTS['quantanalysis'] = True

python src/main.py
```

## Output Format

```python
{
    'symbol': 'BTC',
    'action': 'BUY',                    # BUY, SELL, or NOTHING
    'confidence': 78,                    # 0-100
    'position_type': 'LONG',            # LONG or SHORT
    'reasoning': '...',                  # Entry reasoning
    'stop_loss': '...',                  # Stop-loss suggestion
    'take_profit': '...',                # Take-profit suggestion
    'timeframe': '1H',
    'timestamp': '2025-01-27T10:30:00',
    'analysis_time_seconds': 12.5,
    'component_analyses': {
        'indicator': {
            'direction': 'BULLISH',
            'confidence': 75,
            'summary': '...'
        },
        'pattern': {
            'pattern': 'Bull Flag',
            'direction': 'BULLISH',
            'confidence': 80
        },
        'trend': {
            'direction': 'UPTREND',
            'strength': 'STRONG',
            'confidence': 82
        }
    }
}
```

## Testing

Run the test script to verify the agent works correctly:

```bash
python test_quantanalysis.py
```

Expected output:
- ✅ Agent initialization
- ✅ Data fetching from HyperLiquid
- ✅ All 4 agents execute successfully
- ✅ Final decision with confidence levels

## Integration with Trading System

The QuantAnalysis agent integrates seamlessly with the existing Moon Dev trading system:

1. **Signals to Trading Agent**: QuantAnalysis signals are passed to trading_agent.py for final decision-making
2. **Weight-Based Combination**: Configure `QUANT_AGENT_WEIGHT` to balance with other signal sources
3. **Risk Management**: Stop-loss and take-profit suggestions feed into risk_agent.py
4. **Backtesting**: Use RBI agent to backtest strategies based on QuantAnalysis signals

## Research Background

This implementation is inspired by the paper:
**"QuantAgent: Price-Driven Multi-Agent LLMs for High-Frequency Trading"**
by Fei Xiong, Xiang Zhang, Aosong Feng, Siqi Sun, and Chenyu You
Y-Research, Stony Brook University
arXiv:2509.09995

Key innovations from the research:
- Multi-agent decomposition of trading analysis
- Specialized agents with domain-specific tools
- Structured reasoning capabilities
- Demonstrated performance on Bitcoin and Nasdaq futures

## Differences from Original QuantAgent

Moon Dev's implementation includes several enhancements:

1. **ModelFactory Integration**: Uses unified LLM abstraction (supports Claude, GPT-4, DeepSeek, etc.)
2. **HyperLiquid Data**: Fetches real-time data from HyperLiquid instead of Yahoo Finance
3. **Modular Design**: Follows Moon Dev's agent pattern (standalone + orchestrated execution)
4. **Extended Indicators**: Additional technical indicators via pandas_ta
5. **Risk Parameters**: Explicit stop-loss and take-profit suggestions
6. **Backtesting Integration**: Compatible with RBI agent for strategy validation

## Performance Considerations

- **Analysis Time**: ~10-15 seconds per symbol (4 sequential AI calls)
- **API Costs**: ~4 AI API calls per analysis (keep in mind with high-frequency use)
- **Data Requirements**: Requires HyperLiquid data access
- **Vision Models**: Best results with vision-capable models (Claude 3.5 Sonnet, GPT-4 Vision)

## Tips for Best Results

1. **Use High Confidence Threshold**: Set `QUANT_MIN_CONFIDENCE = 70` for higher quality signals
2. **Combine with Other Agents**: Use `QUANT_AGENT_WEIGHT` to balance with sentiment and whale signals
3. **Appropriate Timeframes**:
   - 15m: High noise, use for scalping
   - 1H: Balanced, recommended for most strategies
   - 4H/1D: Lower noise, better for swing trading
4. **Backtest First**: Always backtest QuantAnalysis-based strategies with RBI agent before live trading

## Troubleshooting

### Common Issues

**"No data available"**
- Check HyperLiquid API access
- Verify symbol is correct (use HyperLiquid format: "BTC", not "BTC-USD")

**"Model initialization failed"**
- Check API keys in .env file
- Verify model type is available (requires vision-capable model)

**"Low confidence signals"**
- Normal behavior when market conditions are unclear
- Adjust `QUANT_MIN_CONFIDENCE` threshold
- Try different timeframes

**"Analysis too slow"**
- Expected: 4 sequential AI calls take time
- Consider running less frequently
- Use faster models (Groq, DeepSeek) for development

## Future Enhancements

Potential improvements:
- [ ] Parallel agent execution for faster analysis
- [ ] Multi-timeframe analysis (analyze 1H + 4H + 1D simultaneously)
- [ ] Visual chart analysis using vision models
- [ ] Agent disagreement detection and resolution
- [ ] Historical performance tracking per agent
- [ ] Adaptive confidence thresholds based on market conditions

## Credits

**Original Research:** Y-Research, Stony Brook University
**Implementation:** Moon Dev 🌙
**Inspired By:** QuantAgent: Price-Driven Multi-Agent LLMs for High-Frequency Trading

---

Built with love by Moon Dev 🚀

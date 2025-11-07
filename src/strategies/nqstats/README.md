# NQStats Trading Strategies

Backtesting implementations based on **NQStats.com** statistical analysis with 10-20 years of historical data (2004-2025).

## Overview

These strategies leverage probability-based edges derived from extensive historical analysis of Nasdaq-100 E-Mini (NQ) futures price behavior. While developed for NQ futures, the principles can be adapted to other instruments with proper session time adjustments.

## Implemented Strategies

### 1. 9AM Hour Continuation Strategy (`nq_9am_hour_continuation.py`)

**Statistical Edge:** 67-70% probability
**Data Source:** 10-20 year historical sample

#### Core Logic

- Trades in direction of 9am hour close (9:30am-10:30am EST)
- If 9am hour closes green: 67% probability entire session closes green
- 70% probability NY session (4pm > 9:30am) closes green

#### Entry Criteria

- **Timing:** After 10:30am (completion of 9am hour)
- **Direction:** Follow 9am hour direction (green = long, red = short)
- **Optimal Window:** First 20-minute segment has 89% retracement probability
- **Avoid:** Middle segment (20-40 minutes) entries

#### Exit Rules

- **End of Session:** Close at 4pm
- **Break of Structure:** Exit if price breaks 9:30am session open
- **Stop Loss:** 9am hour extreme (low for longs, high for shorts)

#### Risk Management

- 2% equity risk per trade
- Position sizing based on stop loss distance

#### Key Insights from NQStats

- First 20-min segment: Highest retracement probability (up to 89%)
- Second segment (20-40min): Lower probability (~47%)
- Third segment (40-60min): Wick formation zone
- 9am hour anomaly: Due to volatility, first 20min high/low often unreliable

---

### 2. RTH Break Directional Bias Strategy (`nq_rth_break.py`)

**Statistical Edge:** 83.29% probability
**Data Source:** 10 year sample (2015-2025)

#### Core Logic

Compares current RTH (Regular Trading Hours) open with previous day RTH range (pRTH):

- **RTH:** 9:30am - 4:00pm EST
- **pRTH:** Previous day 9:30am - 4:00pm range

#### Entry Scenarios

**Scenario 1: RTH opens OUTSIDE pRTH (83.29% edge)**

- If RTH opens **above** pRTH high: Strong bullish bias (go LONG)
- If RTH opens **below** pRTH low: Strong bearish bias (go SHORT)
- **83.29% probability** price will NOT break opposite side of pRTH

**Scenario 2: RTH opens INSIDE pRTH (72.66% edge)**

- 72.66% probability of breaking at least one side
- Lower probability for both sides breaking OR staying inside
- *Currently not implemented - requires more complex logic*

#### Entry Criteria

- **Timing:** First 5-minute bar after RTH open (9:30am-9:35am)
- **Confirmation:** RTH open clearly outside pRTH range
- **Direction:** Trade in direction of break (above = long, below = short)

#### Exit Rules

- **Take Profit:** 1.5x pRTH range extension from entry
- **Stop Loss:** Opposite pRTH boundary
- **End of Session:** Close at 4pm

#### Risk Management

- 2% equity risk per trade
- Position sizing based on pRTH boundary stop distance
- Target multiplier: 1.5x previous day's RTH range

#### Key Insights from NQStats

- Highest edge when RTH gaps outside previous range
- Strong directional bias indicator
- Low probability of mean reversion when outside pRTH

---

## Additional NQStats Strategies (Not Yet Implemented)

### 3. Initial Balance Break (74-96% edge)

- IB = 9:30am-10:30am high/low
- 96% probability IB breaks before 4pm
- 83% probability IB breaks before 12pm
- Direction filter: IB close position predicts break direction (74-81%)

### 4. SDEV Mean Reversion (68% containment)

- Calculate daily ±1.0 SDEV from session open (±1.376%)
- 68.27% probability session closes within range
- Fade moves beyond +1.5 SDEV
- Quantitative pivot points based on standard deviation

### 5. Morning Judas Continuation (64-70%)

- Measure 9:30am vs 9:40am levels
- Up bias (9:40 > 9:30): 64% continuation to 10am
- Down bias (9:40 < 9:30): 70% continuation below 9:40
- Myth-buster: Continuation > Reversal

### 6. Noon Curve AM/PM Structure (74.3%)

- 74.3% probability high/low form on OPPOSITE sides of 12pm
- If AM sets low, expect PM to set high (and vice versa)
- Quarterly confluence tracking (Q1-Q4 segments)

### 7. Hour Stats Sweep Retracement (89%)

- If hour opens inside previous hour and sweeps high/low
- Trade retracement to current hour open
- First 20-min segment: 89% probability
- Avoid 9am hour due to volatility

### 8. ALN London Engulfment (98%)

- Compare Asian (8pm-2am), London (2am-8am), NY (8am-4pm)
- When London engulfs Asia: 98% NY breaks London boundary
- Directional bias based on which side breaks first

---

## Usage

### Running Backtests

```bash
# 9AM Hour Continuation Strategy
PYTHONPATH=/home/user/moon-dev-ai-agents python src/strategies/nqstats/nq_9am_hour_continuation.py

# RTH Break Directional Bias Strategy
PYTHONPATH=/home/user/moon-dev-ai-agents python src/strategies/nqstats/nq_rth_break.py
```

### Requirements

```python
# Core libraries
backtesting>=0.3.3
pandas>=1.3.0
talib>=0.4.0

# Data format
# CSV with columns: datetime, open, high, low, close, volume
# 15-minute timeframe recommended for intraday strategies
```

### Data Preparation

```python
import pandas as pd

# Load and prepare data
df = pd.read_csv('your_data.csv')
df.columns = df.columns.str.strip().str.lower()
df['datetime'] = pd.to_datetime(df['datetime'])
df.set_index('datetime', inplace=True)
df.columns = [col.capitalize() for col in df.columns]
```

---

## Important Notes

### Session Time Adjustments

These strategies are designed for **NQ futures with NYSE trading hours**:

- **RTH:** 9:30am - 4:00pm EST
- **Overnight:** 6:00pm - 9:30am EST (Asian/London sessions)

When applying to other instruments:

- **Crypto (24/7):** Define synthetic sessions or use UTC equivalents
- **Forex:** Adjust for London/NY session overlaps
- **Other Futures:** Match contract's primary trading hours

### Backtesting Considerations

1. **Commission:** Strategies use 0.2% (0.002) commission - adjust for your broker
2. **Slippage:** Not explicitly modeled - add slippage parameter for live trading
3. **Data Quality:** Requires clean 15-minute OHLCV data
4. **Session Gaps:** Overnight gaps can affect RTH break calculations
5. **Market Regime:** Statistics derived from 2004-2025 - may not reflect future conditions

### Risk Disclaimer

- **Past performance ≠ future results**
- These edges are **statistical**, not guaranteed
- Use proper risk management (stop losses, position sizing)
- Test thoroughly before live trading
- NQ futures are leveraged and volatile - substantial risk of loss

---

## Statistical Edge Philosophy

NQStats operates on the principle that price behavior follows **quantitative, math-derived probabilities**. Key concepts:

### Standard Deviation Pivots

- Market participants (especially institutional) use similar quantitative approaches
- Creates self-fulfilling prophecies at key statistical levels
- Higher probability of reversals at ±1.0, ±1.5, ±2.0 SDEV levels

### Time-Based Patterns

- **First 20 minutes of hour:** Wick formation, highest retracement probability
- **Middle 20 minutes:** Expansion phase, lower probability
- **Last 20 minutes:** Wick formation zone
- **9:30am volatility:** Market open injection makes first 20min unreliable

### Session Structure

- Market respects previous day's range (pRTH)
- Opening outside range = strong directional bias
- AM/PM symmetry (Noon Curve) = opposite side formation

---

## Implementation Roadmap

- [x] Strategy 1: 9AM Hour Continuation (67-70% edge)
- [x] Strategy 2: RTH Break Directional Bias (83.29% edge)
- [ ] Strategy 3: Initial Balance Break (74-96% edge)
- [ ] Strategy 4: SDEV Mean Reversion (68% edge)
- [ ] Strategy 5: Morning Judas Continuation (64-70% edge)
- [ ] Strategy 6: Noon Curve AM/PM Structure (74.3% edge)
- [ ] Strategy 7: Hour Stats Sweep Retracement (89% edge)
- [ ] Strategy 8: ALN London Engulfment (98% edge)

---

## References

- **Source:** nqstats.com
- **Data Sample:** 10-20 years (2004-2025)
- **Instrument:** Nasdaq-100 E-Mini Futures (NQ)
- **Contract Specs:** $20 x Nasdaq-100 index, 0.25 minimum tick

---

## Moon Dev's AI Trading System

Part of the experimental AI trading system demonstrating:

- Multi-agent orchestration
- Probability-based decision making
- Quantitative strategy development
- Educational open-source approach

**Built with love by Moon Dev**

*For educational purposes - no guarantees of profitability*

---

## Contributing

To add new NQStats strategies:

1. Extract strategy logic from NQStats.com data
2. Implement in standalone Python file
3. Follow naming convention: `nq_[strategy_name].py`
4. Include statistical edge and data source
5. Add entry/exit rules with proper risk management
6. Test on historical data
7. Update this README with strategy details

---

**Last Updated:** November 7, 2025
**Moon Dev AI Trading System**

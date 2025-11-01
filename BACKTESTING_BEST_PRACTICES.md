# 🌙 Moon Dev's Backtesting Best Practices

**Version**: 1.0
**Last Updated**: 2025-11-01
**Author**: Coordinator-Prime

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Framework Overview](#framework-overview)
3. [Creating Strategies](#creating-strategies)
4. [Data Requirements](#data-requirements)
5. [Performance Metrics](#performance-metrics)
6. [Common Pitfalls](#common-pitfalls)
7. [Optimization Guidelines](#optimization-guidelines)
8. [Walk-Forward Testing](#walk-forward-testing)
9. [Moon Dev Coding Standards](#moon-dev-coding-standards)
10. [Troubleshooting](#troubleshooting)

---

## Quick Start

### 5-Minute Backtest

```python
from backtesting import Backtest
from backtest_template import SMACrossoverStrategy, load_moondev_data
from backtest_metrics import analyze_performance, print_metrics

# 1. Load data
data = load_moondev_data('BTC-USD', '15m')

# 2. Run backtest
bt = Backtest(data, SMACrossoverStrategy, cash=100000, commission=0.002)
stats = bt.run()

# 3. Analyze results
metrics = analyze_performance(stats)
print_metrics(metrics)
```

### File Structure

```
src/strategies/
├── backtest_template.py      # Base classes and example strategies
├── backtest_metrics.py        # Performance analysis tools
├── example_backtest.py        # Complete working examples
└── custom/                    # Your custom strategies go here
    ├── my_strategy.py
    └── ...
```

---

## Framework Overview

### Architecture

Moon Dev's backtesting framework consists of three main components:

1. **backtest_template.py**: Base strategy classes, data loaders, indicator wrappers
2. **backtest_metrics.py**: Performance analysis, Moon Dev scoring, comparisons
3. **example_backtest.py**: Complete working examples and patterns

### Key Features

✅ **Real Data Only**: No synthetic or fake data (per CLAUDE.md guidelines)
✅ **pandas_ta Integration**: Use pandas_ta or talib for indicators (NOT backtesting.py built-ins)
✅ **Comprehensive Metrics**: Sharpe, Sortino, Calmar, Moon Dev Score, and more
✅ **Strategy Comparison**: Compare multiple strategies side-by-side
✅ **Parameter Optimization**: Built-in optimization with overfitting protection
✅ **Walk-Forward Testing**: Out-of-sample validation

---

## Creating Strategies

### Basic Strategy Template

```python
from backtest_template import MoonDevStrategy
from backtesting.lib import crossover

class MyStrategy(MoonDevStrategy):
    """
    Brief description of your strategy

    Entry Rules:
    - ...

    Exit Rules:
    - ...

    Parameters:
    - param1: Description (default: value)
    """

    # Strategy parameters (can be optimized)
    param1 = 20
    param2 = 50

    def init(self):
        """Initialize indicators - called once before backtest"""
        super().init()

        # Calculate indicators using self.I()
        self.indicator1 = self.I(self.sma, self.data.Close, self.param1)
        self.indicator2 = self.I(self.sma, self.data.Close, self.param2)

    def next(self):
        """Process next bar - called for each data point"""

        # Entry logic
        if crossover(self.indicator1, self.indicator2):
            if not self.position:
                self.buy()

        # Exit logic
        elif crossover(self.indicator2, self.indicator1):
            if self.position:
                self.position.close()
```

### Available Indicators (via pandas_ta)

All indicators are pre-wrapped in `MoonDevStrategy`:

```python
# Moving Averages
self.sma(series, period)           # Simple MA
self.ema(series, period)           # Exponential MA

# Oscillators
self.rsi(series, period=14)        # RSI
self.macd(series, fast, slow, signal)  # MACD (returns tuple)

# Volatility
self.bbands(series, period, std)   # Bollinger Bands (returns tuple)
self.atr(high, low, close, period) # Average True Range

# Trend
self.adx(high, low, close, period) # ADX
```

### Using pandas_ta Directly

For indicators not in the base class:

```python
import pandas_ta as ta

class AdvancedStrategy(MoonDevStrategy):
    def init(self):
        super().init()

        # Use any pandas_ta indicator
        self.stoch = self.I(ta.stoch, self.data.High, self.data.Low, self.data.Close)
        self.obv = self.I(ta.obv, self.data.Close, self.data.Volume)
```

---

## Data Requirements

### CSV Format

Your data must have these columns (case-insensitive):

```csv
datetime, open, high, low, close, volume
2023-01-01 00:00:00, 16531.83, 16532.69, 16509.11, 16510.82, 231.05
```

**Requirements**:
- `datetime`: Parseable datetime string
- `open, high, low, close`: OHLC prices
- `volume`: Trading volume (required even if not used)
- No NaN values
- Sorted chronologically (oldest to newest)

### Loading Data

```python
from backtest_template import load_ohlcv_data, load_moondev_data

# Method 1: Direct file path
data = load_ohlcv_data('path/to/data.csv')

# Method 2: Moon Dev standard format
data = load_moondev_data('BTC-USD', '15m')  # Loads from src/data/rbi/
```

### Data Quality Checklist

- [ ] No missing values (gaps in time)
- [ ] No duplicate timestamps
- [ ] Chronologically sorted
- [ ] Sufficient history (minimum 1000 bars recommended)
- [ ] Clean data (no extreme outliers or errors)

---

## Performance Metrics

### Standard Metrics

| Metric | Description | Good Target |
|--------|-------------|-------------|
| **Total Return %** | Overall profit/loss | > 20% annually |
| **Sharpe Ratio** | Risk-adjusted return | > 1.5 |
| **Sortino Ratio** | Downside risk-adjusted | > 2.0 |
| **Calmar Ratio** | Return / max drawdown | > 3.0 |
| **Max Drawdown %** | Worst peak-to-trough decline | < 15% |
| **Win Rate %** | Percentage of winning trades | > 55% |
| **Profit Factor** | Gross profit / gross loss | > 1.5 |
| **# Trades** | Total number of trades | 20-200 (not too few/many) |

### Moon Dev Score

Custom scoring system (0-100) that weights:

- **30 points**: Total return
- **20 points**: Sharpe ratio
- **15 points**: Win rate
- **15 points**: Max drawdown
- **10 points**: Profit factor
- **10 points**: Recovery factor

**Score Interpretation**:
- **90-100**: Excellent (rare, verify for overfitting)
- **70-89**: Good (solid strategy)
- **50-69**: Acceptable (needs improvement)
- **< 50**: Poor (redesign strategy)

### Using Metrics

```python
from backtest_metrics import analyze_performance, print_metrics

# Run backtest
stats = bt.run()

# Analyze
metrics = analyze_performance(stats)
print_metrics(metrics, detailed=True)

# Access specific metrics
print(f"Sharpe Ratio: {metrics['sharpe_ratio']}")
print(f"Moon Dev Score: {metrics['moondev_score']}")
```

---

## Common Pitfalls

### 1. **Look-Ahead Bias**

❌ **WRONG**: Using future data

```python
def next(self):
    # DON'T DO THIS - accessing future data!
    if self.data.Close[-1] < self.data.Close[1]:  # [1] is future!
        self.buy()
```

✅ **CORRECT**: Only use past data

```python
def next(self):
    # Use only current [-1] and historical [-2, -3, ...] data
    if self.data.Close[-1] < self.data.Close[-2]:
        self.buy()
```

### 2. **Overfitting**

❌ **WRONG**: Too many parameters/conditions

```python
class OverfittedStrategy(Strategy):
    # 10 parameters = overfitting!
    param1 = 12
    param2 = 26
    param3 = 9
    param4 = 14
    # ... etc

    def next(self):
        # 7 conditions = overfitting!
        if (self.indicator1[-1] > self.threshold1 and
            self.indicator2[-1] < self.threshold2 and
            self.indicator3[-1] > self.threshold3 and
            # ... etc):
            self.buy()
```

✅ **CORRECT**: Keep it simple

```python
class SimpleStrategy(Strategy):
    # 2-3 parameters max
    fast_ma = 20
    slow_ma = 50

    def next(self):
        # Simple conditions
        if crossover(self.fast, self.slow):
            self.buy()
```

**Overfitting Warning Signs**:
- More than 5 parameters
- More than 5 entry/exit conditions
- Perfect or near-perfect results (> 90% win rate, Sharpe > 5)
- Large difference between in-sample and out-of-sample performance

### 3. **Insufficient Testing Period**

❌ **WRONG**: Testing on 1 week of data
✅ **CORRECT**: Test on at least 6-12 months, ideally 2+ years

### 4. **Ignoring Transaction Costs**

❌ **WRONG**: No commission

```python
bt = Backtest(data, Strategy, cash=100000, commission=0.0)
```

✅ **CORRECT**: Include realistic fees

```python
bt = Backtest(data, Strategy, cash=100000, commission=0.002)  # 0.2%
```

### 5. **Not Using Stop Losses**

For live trading, always implement risk management:

```python
def next(self):
    if crossover(self.fast, self.slow):
        # Calculate stop loss (e.g., 2% below entry)
        stop_loss = self.data.Close[-1] * 0.98
        self.buy(sl=stop_loss)
```

---

## Optimization Guidelines

### Basic Optimization

```python
from backtesting import Backtest

bt = Backtest(data, MyStrategy, cash=100000, commission=0.002)

stats = bt.optimize(
    fast_period=range(10, 50, 5),      # Test 10, 15, 20, ..., 45
    slow_period=range(30, 100, 10),    # Test 30, 40, 50, ..., 90
    maximize='Sharpe Ratio',            # Optimize for Sharpe
    constraint=lambda p: p.fast_period < p.slow_period  # Ensure fast < slow
)

print(f"Best fast period: {stats._strategy.fast_period}")
print(f"Best slow period: {stats._strategy.slow_period}")
```

### Optimization Best Practices

1. **Optimize on limited parameter ranges**
   - Don't test 1-200 for MA period
   - Test logical ranges (e.g., 10-50 for fast MA)

2. **Use constraints**
   - Ensure parameters make sense (fast < slow)
   - Avoid impossible combinations

3. **Optimize for risk-adjusted metrics**
   - ✅ Sharpe Ratio, Sortino Ratio
   - ❌ Total Return (leads to overfitting)

4. **Test multiple objectives**
   ```python
   # Test both Sharpe and Calmar
   stats1 = bt.optimize(..., maximize='Sharpe Ratio')
   stats2 = bt.optimize(..., maximize='Calmar Ratio')
   ```

5. **Validate with walk-forward testing** (see next section)

---

## Walk-Forward Testing

Walk-forward testing prevents overfitting by testing on out-of-sample data.

### Simple Walk-Forward

```python
# 1. Split data
split = int(len(data) * 0.7)  # 70% train, 30% test
train_data = data.iloc[:split]
test_data = data.iloc[split:]

# 2. Optimize on training data
bt_train = Backtest(train_data, MyStrategy, cash=100000, commission=0.002)
stats_train = bt_train.optimize(
    param1=range(10, 50, 10),
    maximize='Sharpe Ratio'
)

# 3. Get optimized parameters
best_param1 = stats_train._strategy.param1

# 4. Test on out-of-sample data
class OptimizedStrategy(MyStrategy):
    param1 = best_param1  # Use optimized value

bt_test = Backtest(test_data, OptimizedStrategy, cash=100000, commission=0.002)
stats_test = bt_test.run()

# 5. Compare results
print(f"In-sample return: {stats_train['Return [%]']:.2f}%")
print(f"Out-of-sample return: {stats_test['Return [%]']:.2f}%")
```

### Interpreting Results

**Good Strategy** (generalizes well):
```
In-sample:     Return: 35%  Sharpe: 1.8
Out-of-sample: Return: 28%  Sharpe: 1.5
```
✅ Slight decrease is normal and acceptable

**Overfit Strategy** (doesn't generalize):
```
In-sample:     Return: 85%  Sharpe: 3.5
Out-of-sample: Return: -5%  Sharpe: 0.2
```
❌ Large drop indicates overfitting - simplify strategy

---

## Moon Dev Coding Standards

### File Naming

- Strategy files: `my_strategy.py` (snake_case)
- Class names: `MyStrategy` (PascalCase)
- Keep files under 800 lines (split if larger)

### Docstrings

```python
class MyStrategy(MoonDevStrategy):
    """
    One-line summary

    Entry Rules:
    - Condition 1
    - Condition 2

    Exit Rules:
    - Condition 1

    Parameters:
    - param1: Description (default: value)
    - param2: Description (default: value)

    Example:
        >>> bt = Backtest(data, MyStrategy, cash=100000, commission=0.002)
        >>> stats = bt.run()
    """
```

### Code Style

```python
# ✅ GOOD: Clear variable names
self.sma_fast = self.I(self.sma, self.data.Close, 20)
self.sma_slow = self.I(self.sma, self.data.Close, 50)

# ❌ BAD: Unclear names
self.s1 = self.I(self.sma, self.data.Close, 20)
self.s2 = self.I(self.sma, self.data.Close, 50)
```

### Error Handling

Per CLAUDE.md: Minimal error handling, let errors show:

```python
# ✅ GOOD: Let it fail if data is missing
data = load_moondev_data('BTC-USD', '15m')

# ❌ BAD: Over-engineered try/except
try:
    data = load_moondev_data('BTC-USD', '15m')
except FileNotFoundError:
    print("File not found, using default...")
    data = get_fake_data()  # NO FAKE DATA!
```

### Comments

```python
def next(self):
    # Buy signal: Fast MA crosses above slow MA
    if crossover(self.sma_fast, self.sma_slow):
        if not self.position:
            self.buy()

    # Exit signal: Fast MA crosses below slow MA
    elif crossover(self.sma_slow, self.sma_fast):
        if self.position:
            self.position.close()
```

---

## Troubleshooting

### Issue: "No module named 'backtesting'"

```bash
# Install backtesting.py library
pip install backtesting

# Update requirements.txt
pip freeze > requirements.txt
```

### Issue: "No module named 'pandas_ta'"

```bash
# Install pandas_ta
pip install pandas_ta

# Update requirements.txt
pip freeze > requirements.txt
```

### Issue: "All indicators return NaN"

**Cause**: Indicator period larger than data length

```python
# ❌ WRONG: 200-period SMA on 100 bars of data
self.sma = self.I(self.sma, self.data.Close, 200)  # Returns NaN!

# ✅ CORRECT: Use appropriate period
self.sma = self.I(self.sma, self.data.Close, 20)   # Works!
```

**Solution**: Ensure `indicator_period < len(data)`

### Issue: "No trades executed"

**Common causes**:

1. **Conditions never met**
   ```python
   # Debug: Print indicator values
   def next(self):
       print(f"Fast: {self.sma_fast[-1]}, Slow: {self.sma_slow[-1]}")
       # ... rest of logic
   ```

2. **Already in position**
   ```python
   # ❌ WRONG: Doesn't check position
   def next(self):
       if self.buy_signal:
           self.buy()  # Fails if already in position!

   # ✅ CORRECT: Check position first
   def next(self):
       if self.buy_signal and not self.position:
           self.buy()
   ```

3. **Insufficient data for indicators**
   - Ensure data has enough bars for indicator calculations

### Issue: "Strategy results look too good to be true"

**Possible causes**:

1. **Look-ahead bias** - Using future data
2. **Overfitting** - Too many parameters
3. **No transaction costs** - Add commission
4. **Data errors** - Check for unrealistic prices

**Validation**:
- Run walk-forward test
- Compare to buy-and-hold
- Check if Sharpe > 3 or Win Rate > 85% (suspicious)

### Issue: "Backtest runs very slow"

**Optimizations**:

```python
# 1. Reduce optimization range
# ❌ SLOW: Testing 4000 combinations
stats = bt.optimize(
    fast=range(1, 100, 1),      # 100 values
    slow=range(1, 100, 1),      # 100 values
    # = 100 * 100 = 10,000 combos
)

# ✅ FAST: Testing 40 combinations
stats = bt.optimize(
    fast=range(10, 50, 10),     # 5 values
    slow=range(30, 100, 20),    # 8 values
    # = 5 * 8 = 40 combos
)

# 2. Use smaller dataset for initial testing
data_subset = data.iloc[-1000:]  # Last 1000 bars only
```

---

## Quick Reference

### Backtesting Checklist

Before running a backtest:

- [ ] Data has no NaN values
- [ ] Data is sorted chronologically
- [ ] At least 1000 bars of data
- [ ] Commission is set (typically 0.001-0.003)
- [ ] Strategy has clear entry/exit rules
- [ ] No look-ahead bias in logic
- [ ] Parameters are reasonable (not overfit)

### Performance Targets

**Minimum Acceptable**:
- Return: > 15% annually
- Sharpe: > 1.0
- Max DD: < 25%
- Win Rate: > 45%

**Good Performance**:
- Return: > 30% annually
- Sharpe: > 1.5
- Max DD: < 15%
- Win Rate: > 55%

**Excellent Performance**:
- Return: > 50% annually
- Sharpe: > 2.0
- Max DD: < 10%
- Win Rate: > 65%

**Too Good (Check for Bugs!)**:
- Return: > 200% annually
- Sharpe: > 5.0
- Max DD: < 3%
- Win Rate: > 90%

---

## Additional Resources

### Moon Dev Documentation

- `CLAUDE.md` - Project guidelines and coding standards
- `README.md` - Project overview and setup
- `src/strategies/README.md` - Strategy development guide

### Example Files

- `src/strategies/backtest_template.py` - Base classes and examples
- `src/strategies/backtest_metrics.py` - Performance analysis
- `src/strategies/example_backtest.py` - Complete working examples

### External Resources

- [backtesting.py Documentation](https://kernc.github.io/backtesting.py/)
- [pandas_ta Documentation](https://github.com/twopirllc/pandas-ta)
- [TA-Lib Documentation](https://mrjbq7.github.io/ta-lib/)

---

## Need Help?

1. Check this guide's troubleshooting section
2. Review `example_backtest.py` for working examples
3. Ensure you're following Moon Dev coding standards (CLAUDE.md)
4. Ask in Moon Dev Discord community

---

**Last Updated**: 2025-11-01
**Version**: 1.0
**Maintained by**: Coordinator-Prime (Session 011CUgefbZrQTRbhNVZov8nn)

🌙 Happy backtesting! 🚀

# 🛡️ Moon Dev's Risk Management Guide

**Version**: 2.0 (Enhanced)
**Last Updated**: 2025-11-01
**Author**: Coordinator-Prime

---

## Table of Contents

1. [Overview](#overview)
2. [Enhanced Features](#enhanced-features)
3. [Risk Metrics Explained](#risk-metrics-explained)
4. [Position Sizing Methods](#position-sizing-methods)
5. [Correlation Analysis](#correlation-analysis)
6. [Risk Dashboard](#risk-dashboard)
7. [Configuration](#configuration)
8. [Usage Examples](#usage-examples)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

---

## Overview

Moon Dev's Risk Management system protects your trading capital through:

✅ **Real-time Monitoring**: Continuous portfolio risk assessment
✅ **Dynamic Position Sizing**: Volatility-adjusted position sizes
✅ **Correlation Tracking**: Prevent overexposure to correlated assets
✅ **AI-Powered Decisions**: Claude/DeepSeek analysis for limit breaches
✅ **Automated Protection**: Circuit breakers and automatic position closing
✅ **Comprehensive Reporting**: Risk dashboards and export capabilities

---

## Enhanced Features

### What's New in v2.0

**1. Volatility-Based Position Sizing**
- Automatically adjusts position sizes based on asset volatility
- Higher volatility = smaller positions
- Configurable target volatility levels

**2. Correlation Analysis**
- Tracks correlation between all portfolio positions
- Warns about concentrated exposure to correlated assets
- Visual correlation heat maps

**3. Kelly Criterion**
- Optimal position sizing based on win rate and risk/reward
- Fractional Kelly (1/4 Kelly) for conservative sizing
- Prevents over-leveraging

**4. Portfolio Risk Metrics**
- Value at Risk (VaR) at 95% confidence
- Conditional VaR (Expected Shortfall)
- Sharpe Ratio calculation
- Maximum Drawdown tracking

**5. Risk Dashboard**
- Real-time risk visualization
- Color-coded risk scores
- Active alert system
- Export to JSON/CSV

---

## Risk Metrics Explained

### Volatility

**What it measures**: Price fluctuation intensity

**Calculation**: Standard deviation of returns, annualized

**Interpretation**:
- < 30%: Low volatility (stable asset)
- 30-60%: Medium volatility (normal crypto)
- > 60%: High volatility (risky asset)

**Example**:
```python
from src.agents import risk_metrics as rm

volatility = rm.calculate_volatility(
    prices=price_series,
    window=20,
    annualize=True
)
print(f"Annual Volatility: {volatility*100:.1f}%")
```

### Value at Risk (VaR)

**What it measures**: Maximum expected loss at given confidence level

**Calculation**: Historical simulation method

**Interpretation**:
- VaR 95% = $500 means: "95% confident we won't lose more than $500"
- Remaining 5% can exceed this amount

**Formula**: `VaR = Percentile(Returns, 5%) × Portfolio Value`

### Conditional VaR (CVaR)

**What it measures**: Average loss beyond VaR threshold

**Why it matters**: Shows "tail risk" - how bad it gets when things go wrong

**Interpretation**:
- CVaR is always ≥ VaR
- Higher CVaR/VaR ratio = fatter tails (worse tail risk)

### Correlation

**What it measures**: How assets move together

**Range**: -1.0 to +1.0

**Interpretation**:
- +1.0: Perfect positive correlation (move together)
- 0.0: No correlation (independent)
- -1.0: Perfect negative correlation (move opposite)
- > 0.7: High correlation (diversification risk!)

### Risk Score

**What it measures**: Overall position risk (0-100)

**Components** (weighted):
- 40%: Volatility
- 30%: Correlation with portfolio
- 30%: Recent performance (losses increase score)

**Interpretation**:
- 0-40: Low risk (green)
- 40-70: Medium risk (yellow)
- 70-100: High risk (red)

---

## Position Sizing Methods

### 1. Volatility-Based Sizing

**Concept**: Target constant portfolio volatility

**Formula**:
```
Position Size = (Portfolio Value × Target Vol) / Asset Vol
```

**Example**:
- Portfolio: $10,000
- Target Vol: 2% daily
- Asset Vol: 50% annually (≈3% daily)
- Position Size = ($10,000 × 0.02) / 0.03 = $6,667

**Code**:
```python
position_size = rm.volatility_based_position_size(
    portfolio_value=10000,
    target_volatility=0.02,  # 2% daily target
    asset_volatility=0.50,   # 50% annual vol
    max_position_pct=0.20    # Max 20% of portfolio
)
```

**Pros**:
- Adapts to market conditions
- Reduces size in volatile markets
- Consistent portfolio risk

**Cons**:
- May size down too much in trending markets
- Requires historical volatility data

### 2. Kelly Criterion

**Concept**: Maximize long-term growth

**Formula**:
```
Kelly % = (Win Rate × Avg Win - Loss Rate × Avg Loss) / Avg Win
```

**Example**:
- Win Rate: 60%
- Avg Win: 5%
- Avg Loss: 3%
- Kelly = (0.6 × 0.05 - 0.4 × 0.03) / 0.05 = 36%
- **Use 1/4 Kelly = 9%** (conservative)

**Code**:
```python
position_size = rm.kelly_criterion_position_size(
    win_rate=0.60,
    avg_win=0.05,
    avg_loss=0.03,
    portfolio_value=10000,
    kelly_fraction=0.25,  # 1/4 Kelly
    max_position_pct=0.20
)
```

**Pros**:
- Mathematically optimal for growth
- Based on actual trading performance
- Prevents over-betting

**Cons**:
- Requires accurate win rate estimate
- Full Kelly too aggressive (use fractional)
- Past performance ≠ future results

### 3. Risk Parity

**Concept**: Each position contributes equal risk

**Formula**:
```
Position Size = (Portfolio × Risk Budget) / Volatility
```

**Example**:
- 4 positions, each gets 10% / 4 = 2.5% risk budget
- Higher vol assets get smaller $ allocation

**Code**:
```python
position_size = rm.risk_parity_position_size(
    portfolio_value=10000,
    asset_volatility=0.50,
    num_positions=4,
    target_risk_per_position=0.10
)
```

**Pros**:
- True diversification
- Not biased by price levels
- Balanced risk exposure

**Cons**:
- Can lead to concentrated $ positions
- Requires rebalancing

---

## Correlation Analysis

### Why It Matters

**Problem**: Having 5 different tokens that all move together = NOT diversified!

**Solution**: Track correlation and limit exposure to correlated assets

### Correlation Matrix

Visual representation of how all positions correlate:

```
        TokenA  TokenB  TokenC
TokenA   1.00    0.85    0.45
TokenB   0.85    1.00    0.52
TokenC   0.45    0.52    1.00
```

**Red flags**:
- TokenA ↔ TokenB correlation = 0.85 (HIGH! These move together)
- If both are large positions = concentration risk

### Concentration Limits

**Default Settings**:
- Max correlation threshold: 0.70
- Max correlated exposure: 40% of portfolio

**Example Alert**:
```
⚠️ High concentration: 55% in correlated assets (limit: 40%)

Correlated Asset Groups:
  • TokenA ↔ TokenB
    Correlation: 0.85
    Combined Exposure: 35%
```

**Action**: Reduce one of the correlated positions

---

## Risk Dashboard

### Overview Display

```
🌙 MOON DEV'S RISK DASHBOARD 🛡️
======================================================================

💼 PORTFOLIO SUMMARY
----------------------------------------------------------------------
  Total Value:        $10,525.50
  Start Balance:      $10,000.00
  PnL:                $525.50 (+5.26%)
  Positions:          3

📊 POSITIONS
----------------------------------------------------------------------

  TokenABC1234...
    Value:     $4,250.00 (40.4%)
    Volatility: 45.2%
    Risk Score: 62/100

  TokenDEF5678...
    Value:     $3,100.00 (29.4%)
    Volatility: 38.5%
    Risk Score: 48/100
```

### Risk Metrics

```
📈 RISK METRICS
----------------------------------------------------------------------
  Portfolio Volatility:  42.5%
  Value at Risk (95%):   $425.00
  CVaR (95%):            $580.00
  Sharpe Ratio:          1.75
  Max Drawdown:          8.5%
```

### Correlation Heat Map

```
🔥 CORRELATION HEAT MAP
----------------------------------------------------------------------
           TokenA   TokenB   TokenC
TokenA       1.00     0.85     0.42
TokenB       0.85     1.00     0.55
TokenC       0.42     0.55     1.00

  Legend:
    High (>0.7)     ← RED (Warning!)
    Medium (0.4-0.7) ← YELLOW
    Low (<0.4)       ← GREEN (Good!)
```

### Alerts

```
🚨 ACTIVE ALERTS
----------------------------------------------------------------------
  🔴 CRITICAL: Portfolio concentration detected (55% in correlated assets)
  🟠 HIGH: High risk score (75/100) for TokenABC
  🟡 MEDIUM: High volatility (68%) for TokenDEF
```

---

## Configuration

### config.py Settings

```python
# Risk Limits
MAX_LOSS_USD = 500.0          # Max loss before closing positions
MAX_GAIN_USD = 2000.0         # Max gain before taking profits
MINIMUM_BALANCE_USD = 8000.0  # Minimum portfolio balance

# Percentage-based limits (alternative)
USE_PERCENTAGE = True
MAX_LOSS_PERCENT = 5.0        # 5% max loss
MAX_GAIN_PERCENT = 20.0       # 20% max gain

# Position Sizing
MAX_POSITION_PERCENTAGE = 0.20  # Max 20% per position
usd_size = 500                   # Default position size

# AI Confirmation
USE_AI_CONFIRMATION = True      # Ask AI before closing positions

# Check Frequency
MAX_LOSS_GAIN_CHECK_HOURS = 12  # Check balance every 12 hours
```

### Risk Agent Settings (in risk_agent.py)

```python
# Volatility Targeting
TARGET_VOLATILITY = 0.02  # 2% daily portfolio volatility

# Correlation Limits
MAX_CORRELATION = 0.70          # Correlation threshold
MAX_CORRELATED_EXPOSURE = 0.40  # Max 40% in correlated assets

# Kelly Criterion
KELLY_FRACTION = 0.25  # Use 1/4 Kelly (conservative)

# Risk Scores
HIGH_RISK_THRESHOLD = 70  # Alert if risk score > 70
```

---

## Usage Examples

### Example 1: Run Enhanced Risk Check

```python
from src.agents.risk_agent import RiskAgent

# Initialize agent
agent = RiskAgent()

# Calculate and display enhanced metrics
metrics = agent.calculate_enhanced_metrics(show_dashboard=True)

# Access metrics
print(f"Portfolio VaR: ${metrics['var_95']:.2f}")
print(f"Portfolio CVaR: ${metrics['cvar_95']:.2f}")

# Check for concentration
if metrics['concentration']['is_concentrated']:
    print("⚠️ Portfolio is concentrated!")
```

### Example 2: Calculate Optimal Position Size

```python
from src.agents import risk_metrics as rm

# Method 1: Volatility-based
size_vol = rm.volatility_based_position_size(
    portfolio_value=10000,
    asset_volatility=0.55,
    target_volatility=0.02
)

# Method 2: Kelly Criterion
size_kelly = rm.kelly_criterion_position_size(
    win_rate=0.65,
    avg_win=0.06,
    avg_loss=0.03,
    portfolio_value=10000
)

print(f"Volatility-based: ${size_vol:.2f}")
print(f"Kelly Criterion: ${size_kelly:.2f}")
```

### Example 3: Analyze Correlation

```python
from src.agents import risk_metrics as rm

# Get price data for multiple tokens
price_data = {
    'TokenA': token_a_prices,  # pd.Series
    'TokenB': token_b_prices,
    'TokenC': token_c_prices
}

# Calculate correlation matrix
corr_matrix = rm.calculate_correlation_matrix(price_data)

# Check concentration
positions = {
    'TokenA': 4000,
    'TokenB': 3500,
    'TokenC': 2500
}

concentration = rm.check_portfolio_concentration(
    positions,
    corr_matrix,
    max_correlation=0.70
)

if concentration['is_concentrated']:
    print("⚠️ Reduce correlated positions!")
    for group in concentration['correlated_groups']:
        print(f"  {group['token_a']} ↔ {group['token_b']}")
        print(f"  Correlation: {group['correlation']:.2f}")
```

### Example 4: Export Risk Report

```python
from src.agents.risk_dashboard import RiskDashboard

dashboard = RiskDashboard()

# Generate report
report = dashboard.generate_risk_report(
    portfolio_value=portfolio_value,
    positions=position_metrics,
    metrics=risk_metrics,
    concentration=concentration_results
)

# Export to JSON
filepath = dashboard.export_risk_report(report, format='json')
print(f"Report saved to: {filepath}")
```

---

## Best Practices

### 1. Position Sizing

✅ **DO**:
- Use volatility-based sizing for dynamic markets
- Apply Kelly Criterion with fractional multiplier (1/4 or 1/2)
- Never exceed 20% of portfolio in single position
- Size down in high volatility environments

❌ **DON'T**:
- Use fixed position sizes across all assets
- Use full Kelly (too aggressive)
- Ignore volatility differences
- Over-concentrate in few positions

### 2. Correlation Management

✅ **DO**:
- Check correlation matrix regularly
- Limit total exposure to correlated assets (< 40%)
- Diversify across uncorrelated assets
- Monitor correlation changes over time

❌ **DON'T**:
- Assume different tokens = diversified
- Ignore high correlation warnings
- Concentrate in sector-specific tokens
- Trade only trending narratives

### 3. Risk Monitoring

✅ **DO**:
- Review risk dashboard daily
- Act on critical alerts immediately
- Export risk reports for record-keeping
- Adjust position sizes based on risk scores

❌ **DON'T**:
- Ignore high risk score warnings
- Override AI recommendations without analysis
- Let emotions override risk metrics
- Trade without checking portfolio risk first

### 4. Circuit Breakers

✅ **DO**:
- Set conservative loss limits (5-10%)
- Enable AI confirmation for limit breaches
- Test circuit breakers with small positions first
- Have manual override ability

❌ **DON'T**:
- Disable circuit breakers completely
- Set limits too tight (constant triggers)
- Ignore repeated limit breaches
- Override without reviewing metrics

---

## Troubleshooting

### Issue: "No positions to analyze"

**Cause**: No monitored tokens with active positions

**Solution**:
1. Check `config.py` MONITORED_TOKENS list
2. Verify you have positions in those tokens
3. Ensure tokens not in EXCLUDED_TOKENS

### Issue: Correlation matrix empty

**Cause**: Insufficient price data or < 2 positions

**Solution**:
1. Need at least 2 positions for correlation
2. Ensure 20+ periods of price data available
3. Check data fetching isn't failing

### Issue: VaR calculation returns 0

**Cause**: Insufficient common dates across positions

**Solution**:
1. Need at least 20 common data points
2. Check all positions have recent price history
3. Verify data fetching for all tokens

### Issue: Risk scores always high

**Cause**: Market-wide high volatility or losses

**Solution**:
1. This is normal in volatile markets
2. Consider reducing position sizes
3. Check if recent performance is negative
4. Review correlation with portfolio

### Issue: Dashboard not displaying

**Cause**: Terminal doesn't support colors or missing dependency

**Solution**:
```bash
pip install termcolor
```

If still issues, use `show_dashboard=False` and access metrics dict directly

---

## Quick Reference

### Key Metrics Targets

| Metric | Good | Acceptable | Warning |
|--------|------|------------|---------|
| Portfolio Volatility | < 30% | 30-50% | > 50% |
| Sharpe Ratio | > 2.0 | 1.0-2.0 | < 1.0 |
| Max Drawdown | < 10% | 10-20% | > 20% |
| Risk Score | 0-40 | 40-70 | 70-100 |
| Correlation | < 0.4 | 0.4-0.7 | > 0.7 |
| Position Size | < 10% | 10-20% | > 20% |

### Command Cheat Sheet

```bash
# Run risk agent standalone
python src/agents/risk_agent.py

# Run with enhanced metrics (in Python)
from src.agents.risk_agent import RiskAgent
agent = RiskAgent()
metrics = agent.calculate_enhanced_metrics()

# Export risk report
dashboard.export_risk_report(report, format='json')
```

---

## Additional Resources

### Files

- `src/agents/risk_agent.py` - Main risk agent
- `src/agents/risk_metrics.py` - Risk calculations
- `src/agents/risk_dashboard.py` - Visualization and reporting
- `src/config.py` - Risk configuration

### Documentation

- `CLAUDE.md` - Project guidelines
- `BACKTESTING_BEST_PRACTICES.md` - Strategy testing
- `README.md` - Project overview

---

**Last Updated**: 2025-11-01
**Version**: 2.0 (Enhanced Risk Management)
**Maintained by**: Coordinator-Prime

🛡️ Stay safe out there! 🌙

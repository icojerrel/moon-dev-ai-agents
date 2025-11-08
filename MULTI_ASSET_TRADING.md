# 💹 Multi-Asset Trading Guide

Complete guide for trading **Forex, Gold, Stocks, and Indices** with MT5 integration.

## 🎯 Overview

With MetaTrader 5, you can now trade across multiple asset classes:

| Asset Class | Examples | Characteristics |
|------------|----------|----------------|
| 💱 **Forex** | EUR/USD, GBP/USD, USD/JPY | High liquidity, 24/5 trading, tight spreads |
| 🏆 **Metals** | Gold (XAU/USD), Silver (XAG/USD) | Safe-haven, inflation hedge, volatile |
| 📈 **Indices** | US30, NAS100, SPX500 | Market sentiment, broader exposure |
| 📊 **Stocks** | AAPL, TSLA, GOOGL | Company-specific, earnings-driven |
| ⚡ **Energies** | Oil, Natural Gas | Supply/demand, geopolitical |
| 🪙 **Crypto** | BTC/USD, ETH/USD | 24/7, high volatility |

---

## 🔧 Configuration

### 1. Enable Asset Classes in `config.py`

```python
# Forex Pairs (Currency Trading)
MT5_FOREX_PAIRS = [
    'EURUSD',   # Most liquid pair
    'GBPUSD',   # Volatile, responds to UK data
    'USDJPY',   # Safe-haven pair
    'AUDUSD',   # Commodity currency
]

# Precious Metals
MT5_METALS = [
    'XAUUSD',   # Gold - safe haven, inflation hedge
]

# Stock Indices
MT5_INDICES = [
    'US30',     # Dow Jones - 30 blue chip stocks
    'NAS100',   # NASDAQ - tech heavy
    'SPX500',   # S&P 500 - broad US market
]

# Individual Stocks (check symbol names with your broker)
MT5_STOCKS = [
    'AAPL',     # Apple
    'MSFT',     # Microsoft
    'GOOGL',    # Google
]
```

### 2. Asset-Specific Settings

The system automatically adjusts for each asset class:

```python
# Position Sizing
MT5_POSITION_SIZES = {
    'forex': 0.01,      # Micro lot (1,000 units)
    'metals': 0.01,     # 1 oz of gold
    'indices': 0.10,    # Larger lots for indices
    'stocks': 1,        # 1 share
}

# Risk Parameters
MT5_RISK_PARAMS = {
    'forex': {
        'max_spread_pips': 3,       # Tight spreads expected
        'min_stop_loss_pips': 20,   # Minimum SL
        'max_stop_loss_pips': 100,  # Maximum SL
        'default_tp_ratio': 2.0,    # 2:1 risk/reward
    },
    'metals': {
        'max_spread_pips': 50,      # Gold has wider spreads
        'min_stop_loss_pips': 100,  # Larger swings
        'max_stop_loss_pips': 500,
        'default_tp_ratio': 2.5,
    },
    # ... etc
}
```

---

## 💱 Trading Forex (Currency Pairs)

### Best Pairs for Beginners

**Major Pairs** (lowest spreads, highest liquidity):
- EUR/USD - Most traded, tight spreads (1-2 pips)
- GBP/USD - Higher volatility, good for day trading
- USD/JPY - Asian market favorite, safe-haven

**Commodity Pairs**:
- AUD/USD - Follows gold and commodities
- NZD/USD - Similar to AUD, lower liquidity
- USD/CAD - Follows oil prices (inverse)

### Trading Sessions

```
📍 Asian Session (00:00-09:00 UTC)
   - Lower volatility
   - JPY pairs most active
   - Range-bound trading

📍 London Session (08:00-17:00 UTC)
   - Highest volume
   - EUR, GBP pairs active
   - Major breakouts occur

📍 New York Session (13:00-22:00 UTC)
   - High liquidity
   - USD pairs active
   - Overlap with London = most volatile

📍 Session Overlaps = Best Trading Opportunities
   - London/New York (13:00-17:00 UTC)
   - Asian/European (08:00-09:00 UTC)
```

### Forex Trading Example

```python
# Configuration
symbol = 'EURUSD'
timeframe = '1H'  # 1-hour charts for swing trades

# AI Analysis considers:
# ✓ Interest rate differentials (ECB vs Fed)
# ✓ Economic data (NFP, GDP, inflation)
# ✓ Technical levels (1.0500, 1.1000)
# ✓ Trend direction (SMA 20/50/200)

# Typical Trade Setup
Entry: 1.0850
Stop Loss: 1.0800 (50 pips)
Take Profit: 1.0950 (100 pips)
Risk/Reward: 1:2
Position Size: 0.01 lots
Risk: $5 (50 pips * $0.10/pip)
Potential Profit: $10
```

### Forex Key Factors

- 📊 **Economic Calendar**: NFP, CPI, GDP, Central Bank meetings
- 💰 **Interest Rates**: Higher rates = stronger currency
- 🏛️ **Central Banks**: Fed, ECB, BOE, BOJ policy
- 🌍 **Geopolitical Events**: Brexit, elections, trade wars
- 📈 **Correlations**: EUR/USD vs DXY (inverse)

---

## 🏆 Trading Gold (XAU/USD)

### Why Trade Gold?

- ✅ **Safe Haven**: Rises during uncertainty
- ✅ **Inflation Hedge**: Protects against currency devaluation
- ✅ **High Volatility**: Large daily ranges = opportunities
- ✅ **24-Hour Market**: Follows forex hours
- ✅ **Clear Trends**: Good for trend following

### Gold Trading Hours

```
🌏 Asian Session: Quiet, range-bound
🌍 London Session: Increased volatility
🌎 New York Session: HIGHEST volatility
   - US data releases move gold
   - Fed announcements = major moves
```

### Gold Trading Example

```python
# Configuration
symbol = 'XAUUSD'
timeframe = '4H'  # Gold trends on higher timeframes

# AI Analysis considers:
# ✓ US Dollar strength (DXY index)
# ✓ Real interest rates (10Y yields - inflation)
# ✓ Fed policy (hawkish = bearish gold)
# ✓ Geopolitical risk (wars, elections)
# ✓ Technical levels (1800, 1900, 2000)

# Typical Trade Setup
Entry: $2,050/oz
Stop Loss: $2,000 (500 pips)
Take Profit: $2,150 (1000 pips)
Risk/Reward: 1:2
Position Size: 0.01 lots
Risk: $50 (500 pips * $0.10/pip)
Potential Profit: $100
```

### Gold Key Factors

- 💵 **US Dollar**: Inverse correlation (strong $ = weak gold)
- 📈 **Real Yields**: Higher yields = bearish for gold
- 🏦 **Fed Policy**: Hawkish = bearish, Dovish = bullish
- ⚔️ **Geopolitics**: War, crisis = flight to safety
- 💰 **Inflation**: Higher inflation = bullish for gold
- 📊 **Technical Levels**: Gold respects round numbers (1800, 1900, 2000)

---

## 📈 Trading Indices (Stock Markets)

### Popular Indices

**US Indices:**
- **US30** (Dow Jones) - 30 blue-chip US stocks, price-weighted
- **NAS100** (NASDAQ) - 100 largest non-financial, tech-heavy
- **SPX500** (S&P 500) - 500 large-cap US stocks, broad market

**European Indices:**
- **GER40** (DAX) - 40 largest German companies
- **UK100** (FTSE) - 100 largest UK companies
- **FRA40** (CAC) - 40 largest French companies

### Index Trading Example

```python
# Configuration
symbol = 'US30'  # Dow Jones
timeframe = '1H'

# AI Analysis considers:
# ✓ Overall market sentiment (risk-on/risk-off)
# ✓ Economic growth (GDP, PMI)
# ✓ Earnings season results
# ✓ Fed policy (QE = bullish stocks)
# ✓ Technical support/resistance

# Typical Trade Setup
Entry: 38,500
Stop Loss: 38,300 (200 points)
Take Profit: 38,900 (400 points)
Risk/Reward: 1:2
Position Size: 0.10 lots
Risk: $20 (200 pts * $0.10/pt)
Potential Profit: $40
```

### Index Trading Hours

```
🌍 European Indices: 08:00-16:30 GMT
   - DAX, FTSE, CAC

🌎 US Indices: 14:30-21:00 GMT
   - Most volatile during US session
   - Pre-market: 09:00-14:30 (lower volume)
   - After-hours: 21:00-01:00 (thin liquidity)

⚠️ Avoid trading indices during:
   - First 15 minutes (erratic moves)
   - Last 15 minutes (closing volatility)
   - Holidays (low liquidity)
```

### Index Key Factors

- 📊 **Earnings Season**: Q1-Q4 corporate results
- 💰 **Central Banks**: QE, rate cuts = bullish
- 📈 **Economic Data**: GDP, unemployment, PMI
- 🏢 **Sector Rotation**: Tech, energy, financials
- 😰 **VIX**: High volatility = fear, bearish stocks
- 🔄 **Correlation**: Stocks down = gold/bonds up

---

## 📊 Trading Individual Stocks

### Popular Stocks on MT5

**Tech Giants:**
- AAPL (Apple) - Stable, follows earnings
- MSFT (Microsoft) - Cloud growth driver
- GOOGL (Google) - Ad revenue sensitive
- AMZN (Amazon) - E-commerce leader
- NVDA (NVIDIA) - AI boom beneficiary

**Note**: Symbol names vary by broker. Check with your MT5 broker for exact symbols.

### Stock Trading Example

```python
# Configuration
symbol = 'AAPL'  # Apple Inc.
timeframe = '1D'  # Daily charts for stocks

# AI Analysis considers:
# ✓ Company earnings and guidance
# ✓ Product launches and innovation
# ✓ Sector performance (tech sector)
# ✓ Overall market trend
# ✓ Technical support/resistance

# Typical Trade Setup
Entry: $180/share
Stop Loss: $175 (500 pips)
Take Profit: $190 (1000 pips)
Risk/Reward: 1:2
Position Size: 10 shares
Risk: $50 (10 shares * $5 move)
Potential Profit: $100
```

### Stock Key Factors

- 📈 **Earnings**: Quarterly results beat/miss
- 📰 **News**: Product launches, acquisitions
- 🏢 **Sector**: Tech, healthcare, energy trends
- 📊 **Market**: Overall S&P 500 direction
- 💰 **Valuation**: P/E ratio, growth rate
- 📉 **Relative Strength**: vs sector, vs market

---

## ⚙️ Asset-Specific Strategies

### Forex Strategy: Trend Following

```python
# Configuration
symbols = ['EURUSD', 'GBPUSD', 'USDJPY']
timeframe = '4H'
strategy = 'Trend Following'

# Rules:
# ✓ Price above SMA 200 = bullish trend
# ✓ SMA 20 crosses above SMA 50 = entry signal
# ✓ RSI > 50 confirms bullish momentum
# ✓ Entry on pullback to SMA 20
# ✓ SL below recent swing low
# ✓ TP at 2x SL distance
```

### Gold Strategy: Breakout Trading

```python
# Configuration
symbol = 'XAUUSD'
timeframe = '1D'
strategy = 'Range Breakout'

# Rules:
# ✓ Identify consolidation range (e.g., 2000-2050)
# ✓ Wait for breakout above resistance or below support
# ✓ Confirm with volume increase
# ✓ Entry on breakout bar close
# ✓ SL inside the range
# ✓ TP at range height projected from breakout
```

### Index Strategy: Mean Reversion

```python
# Configuration
symbol = 'SPX500'
timeframe = '1H'
strategy = 'Mean Reversion'

# Rules:
# ✓ Price deviates >2 std deviations from Bollinger Band mean
# ✓ RSI shows oversold (<30) or overbought (>70)
# ✓ Entry when price touches outer band
# ✓ SL beyond the band
# ✓ TP at middle Bollinger Band (mean)
```

---

## 🎯 Quick Start Guide

### Step 1: Choose Your Asset Class

**Beginners:**
- Start with **Forex** (EUR/USD) - most liquid, predictable
- Or **Gold** - clear trends, good for learning

**Intermediate:**
- Add **Indices** (US30, SPX500) - market sentiment
- Or **Major Stocks** (AAPL, MSFT) - company fundamentals

### Step 2: Enable in Config

```python
# src/config.py

MT5_ENABLED = True

# Choose 2-3 symbols to start
MT5_SYMBOLS = [
    'EURUSD',   # Forex
    'XAUUSD',   # Gold
    'US30',     # Index
]

# Conservative risk settings
MT5_MAX_POSITIONS = 3
MT5_MIN_CONFIDENCE = 75  # Only high-confidence trades
```

### Step 3: Run MT5 Agent

```bash
# Standalone
python src/agents/mt5_trading_agent.py

# Or with Docker
docker-compose --profile mt5 up -d mt5-agent

# View logs
docker-compose logs -f mt5-agent
```

### Step 4: Monitor Alerts

Receive Telegram alerts for:
- 🟢 **Trade Entries**: "BUY EURUSD @ 1.0850"
- 🏁 **Trade Exits**: "Closed XAUUSD @ 2050, +$50 profit"
- ⚠️ **Warnings**: "High spread detected on GBPUSD"
- ❌ **Errors**: "Failed to execute trade"

---

## 📊 Asset Comparison

| Factor | Forex | Gold | Indices | Stocks |
|--------|-------|------|---------|--------|
| **Liquidity** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Volatility** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Spreads** | Low (1-3 pips) | Medium (20-50) | Medium (5-50) | Varies |
| **Leverage** | High (1:500) | High (1:500) | Medium (1:100) | Low (1:20) |
| **Trading Hours** | 24/5 | 24/5 | Session-based | Session-based |
| **Beginner Friendly** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |

---

## ⚠️ Risk Management

### Position Sizing by Asset

```python
# Risk 1% of account per trade

Account: $10,000
Risk per trade: $100 (1%)

Forex (EURUSD):
  - SL: 50 pips
  - Position: 0.02 lots
  - Risk: $10/pip * 50 = $100 ✓

Gold (XAUUSD):
  - SL: 500 pips
  - Position: 0.02 lots
  - Risk: $0.20/pip * 500 = $100 ✓

Index (US30):
  - SL: 200 points
  - Position: 0.05 lots
  - Risk: $0.50/pt * 200 = $100 ✓
```

### Correlation Management

**Don't trade correlated pairs simultaneously:**
- EUR/USD + GBP/USD = 80% correlated
- EUR/USD + USD/JPY = inversely correlated
- Gold + Silver = 80% correlated

**Safe combinations:**
- EUR/USD + Gold (different drivers)
- US30 + EUR/USD (different markets)
- Oil + JPY (minimal correlation)

---

## 🔍 Monitoring Your Trades

### Real-Time Alerts

```bash
# Telegram Alert Example:
🟢 BUY Signal: EUR/USD
📊 Asset Class: FOREX
💰 Entry: 1.0850
🛑 Stop Loss: 1.0800 (50 pips)
🎯 Take Profit: 1.0950 (100 pips)
📈 Confidence: 82%
💡 Reason: Bullish momentum, price above SMA 200,
   RSI breakout above 50
```

### Log Monitoring

```bash
# Real-time logs
tail -f logs/mt5_agent.log

# Trade-specific logs
tail -f logs/trades.log
```

---

## 🎓 Learning Resources

### Understanding Each Market

**Forex:**
- [BabyPips School](https://www.babypips.com/learn/forex) - Free forex education
- Focus on: interest rates, central banks, economic calendar

**Gold:**
- Study: DXY (dollar index), 10-year yields, Fed policy
- Gold = anti-dollar trade

**Indices:**
- Follow: SPY, QQQ ETFs for sentiment
- Watch: VIX (volatility index), sector rotation

**Stocks:**
- Research: company earnings, sector trends
- Tools: finviz.com for stock screeners

---

## ✅ Best Practices

1. **Start Small**: Demo account for 2+ weeks
2. **One Market**: Master forex before adding gold/indices
3. **Few Symbols**: Trade 2-3 symbols maximum
4. **Risk Management**: Never risk >1-2% per trade
5. **Patience**: Wait for high-confidence setups (>75%)
6. **Journal**: Track all trades for review
7. **Avoid News**: Don't trade during major news events
8. **Correlation**: Don't double up on correlated assets

---

## 📞 Support

**Broker Compatibility:**
- Test symbols with your broker first
- Symbol names may differ (e.g., XAUUSD vs GOLD)
- Some brokers don't offer stocks/crypto via MT5

**Issues:**
- Check symbol availability: Tools → Market Watch → Add symbol
- Verify trading hours for each asset
- Confirm margin requirements with broker

---

**Built with ❤️ by Moon Dev 🌙**

Happy trading across all markets! 🚀📈💰

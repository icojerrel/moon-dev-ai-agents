# 🧪 Testing Guide

Complete testing guide for Moon Dev AI Trading System with sandbox environment.

## 🎯 Overview

The testing suite provides comprehensive validation of the trading system using:
- **Mock MT5 Simulator** - Simulates real broker without requiring connection
- **Sandbox Mode** - Test with virtual money and generated market data
- **Docker Testing** - Isolated, reproducible test environment
- **Multi-Asset Tests** - Validates forex, gold, indices, stocks

## 🚀 Quick Start

### Run All Tests (Docker)

```bash
# Run complete test suite
./run_tests.sh

# Output will show:
# ✅ Mock MT5 Simulator
# ✅ Asset Detection & Helpers
# ✅ Comprehensive Sandbox Tests
#
# 🎉 ALL TESTS PASSED!
```

### Run Individual Tests

```bash
# Test mock MT5 simulator
python src/utils/mock_mt5.py

# Test asset detection
python src/utils/mt5_helpers.py

# Test comprehensive sandbox
python tests/test_mt5_sandbox.py
```

## 🐳 Docker Test Environment

### Build Test Containers

```bash
docker-compose -f docker-compose.test.yml build
```

### Run Specific Tests

```bash
# Mock MT5 simulator
docker-compose -f docker-compose.test.yml run --rm test-mock-mt5

# Asset detection
docker-compose -f docker-compose.test.yml run --rm test-asset-detection

# Full sandbox suite
docker-compose -f docker-compose.test.yml run --rm test-sandbox
```

### Clean Up

```bash
docker-compose -f docker-compose.test.yml down -v
```

## 📋 Test Suite Components

### 1. Mock MT5 Simulator (`src/utils/mock_mt5.py`)

Simulates full MT5 trading environment:

```python
from src.utils.mock_mt5 import MockMT5Simulator

# Create simulator
sim = MockMT5Simulator(starting_balance=10000)

# Get account info
account = sim.get_account_info()
print(f"Balance: ${account['balance']}")

# Generate market data
df = sim.generate_ohlcv_data('EURUSD', timeframe='1H', bars=100)

# Open position
ticket = sim.market_buy('EURUSD', volume=0.01, sl=1.0800, tp=1.0900)

# Simulate market move
sim.simulate_market_move('EURUSD', 50)  # +50 pips

# Check profit
positions = sim.get_positions()
print(f"Profit: ${positions.iloc[0]['profit']:.2f}")

# Close position
sim.close_position(ticket)
```

**Features:**
- ✅ Realistic price generation (bullish, bearish, ranging trends)
- ✅ Position management (buy, sell, close)
- ✅ P&L calculation
- ✅ Account balance tracking
- ✅ Spread simulation
- ✅ Multi-asset support

### 2. Asset Detection Tests (`src/utils/mt5_helpers.py`)

Tests intelligent asset class detection:

```python
from src.utils.mt5_helpers import (
    detect_asset_class,
    format_asset_name,
    calculate_position_size
)

# Detect asset class
asset = detect_asset_class('EURUSD')  # Returns 'forex'
asset = detect_asset_class('XAUUSD')  # Returns 'metals'
asset = detect_asset_class('US30')    # Returns 'indices'

# Format with emojis
name, emoji = format_asset_name('EURUSD')
# Returns: ('EUR/USD', '💱')

# Calculate position size
size = calculate_position_size(
    symbol='EURUSD',
    account_balance=10000,
    risk_percent=1.0,  # Risk 1% = $100
    stop_loss_pips=50
)
# Returns: 0.2 lots
```

### 3. Comprehensive Sandbox Tests (`tests/test_mt5_sandbox.py`)

Complete system validation:

**Test Coverage:**
1. ✅ Account initialization
2. ✅ Asset class detection (forex, metals, indices, stocks)
3. ✅ Symbol information (bid/ask, spreads, point sizes)
4. ✅ OHLCV data generation (all trends, all assets)
5. ✅ Position sizing calculation
6. ✅ BUY position execution
7. ✅ SELL position execution
8. ✅ Maximum positions limit (1 position only)
9. ✅ Profit calculation with market moves
10. ✅ Loss calculation with market moves
11. ✅ Multi-asset trading (forex, gold, indices)
12. ✅ Account equity updates

**Sample Output:**

```
🌙 Moon Dev MT5 Sandbox Test Suite

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TEST: Account Initialization
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Account Login: 12345678
Starting Balance: $10000.00
Currency: USD
Leverage: 1:100
✅ PASSED: Account Initialization

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TEST: Asset Class Detection
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💱 EURUSD     → forex      (expected: forex)
💱 GBPUSD     → forex      (expected: forex)
🏆 XAUUSD     → metals     (expected: metals)
📈 US30       → indices    (expected: indices)
✅ PASSED: Asset Class Detection

...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TEST SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Tests: 12
Passed: 12
Failed: 0
Pass Rate: 100.0%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎉 ALL TESTS PASSED! System is ready for deployment.
```

## ⚙️ Configuration for Testing

### Enable Sandbox Mode

```python
# src/config.py

# Sandbox Settings
SANDBOX_MODE = True                  # Enable for testing
SANDBOX_STARTING_BALANCE = 10000     # Virtual balance
SANDBOX_USE_MOCK_DATA = True         # Generated market data
SANDBOX_SIMULATE_TRADES = True       # Simulate execution

# Strict Risk Control
MT5_MAX_POSITIONS = 1                # Only 1 position at a time
MT5_MIN_CONFIDENCE = 75              # High confidence trades only
```

### Environment Variables for Testing

```bash
# .env.test (create for testing)
SANDBOX_MODE=true
SANDBOX_STARTING_BALANCE=10000
LOG_LEVEL=DEBUG
JSON_LOGS=false

# No real API keys needed for sandbox
# System will use mock data
```

## 🧪 Test Scenarios

### Scenario 1: Forex Trading

```bash
# Test forex pairs
python -c "
from src.utils.mock_mt5 import MockMT5Simulator

sim = MockMT5Simulator()

# Generate bullish EUR/USD data
df = sim.generate_ohlcv_data('EURUSD', bars=100, trend='bullish')

# Open position
ticket = sim.market_buy('EURUSD', 0.01)

# Simulate +50 pip move
sim.simulate_market_move('EURUSD', 50)

# Check profit
positions = sim.get_positions()
print(f'Profit: \${positions.iloc[0][\"profit\"]:.2f}')
"
```

### Scenario 2: Gold Trading

```bash
# Test gold with larger moves
python -c "
from src.utils.mock_mt5 import MockMT5Simulator

sim = MockMT5Simulator()

# Generate ranging gold data
df = sim.generate_ohlcv_data('XAUUSD', bars=100, trend='ranging')

# Open position
ticket = sim.market_buy('XAUUSD', 0.01)

# Simulate +200 pip move
sim.simulate_market_move('XAUUSD', 200)

# Check profit (should be ~\$20 for 0.01 lots)
positions = sim.get_positions()
print(f'Profit: \${positions.iloc[0][\"profit\"]:.2f}')
"
```

### Scenario 3: Maximum 1 Position Limit

```bash
# Test position limit enforcement
python tests/test_mt5_sandbox.py --test max_positions_limit
```

### Scenario 4: Multi-Asset Portfolio

```bash
# Test trading across asset classes
python tests/test_mt5_sandbox.py --test multi_asset_trading
```

## 📊 Test Data Generation

### Market Trends

```python
# Bullish trend
df = sim.generate_ohlcv_data('EURUSD', trend='bullish')
# Prices generally increase

# Bearish trend
df = sim.generate_ohlcv_data('EURUSD', trend='bearish')
# Prices generally decrease

# Ranging market
df = sim.generate_ohlcv_data('EURUSD', trend='ranging')
# Prices oscillate within range

# Random walk
df = sim.generate_ohlcv_data('EURUSD', trend='random')
# No clear direction
```

### Asset-Specific Volatility

```python
# Forex: Lower volatility (0.5% per bar)
df = sim.generate_ohlcv_data('EURUSD')

# Gold: Medium volatility (1.5% per bar)
df = sim.generate_ohlcv_data('XAUUSD')

# Crypto: High volatility (3% per bar)
df = sim.generate_ohlcv_data('BTCUSD')
```

## 🔍 Debugging Tests

### Verbose Output

```bash
# Run with debug logging
LOG_LEVEL=DEBUG python tests/test_mt5_sandbox.py

# Docker with debug
docker-compose -f docker-compose.test.yml run --rm \
  -e LOG_LEVEL=DEBUG \
  test-sandbox
```

### Check Test Logs

```bash
# View test logs
tail -f logs/test_*.log

# Check for errors
grep ERROR logs/test_*.log
```

### Interactive Testing

```python
# Start Python REPL
python

>>> from src.utils.mock_mt5 import MockMT5Simulator
>>> sim = MockMT5Simulator()
>>>
>>> # Test interactively
>>> account = sim.get_account_info()
>>> print(account)
>>>
>>> # Open position
>>> ticket = sim.market_buy('EURUSD', 0.01)
>>> positions = sim.get_positions()
>>> print(positions)
```

## ✅ Pre-Deployment Checklist

Before deploying to production:

- [ ] All tests pass (`./run_tests.sh`)
- [ ] Max 1 position enforced (`MT5_MAX_POSITIONS = 1`)
- [ ] Position sizing validated for each asset class
- [ ] Profit/loss calculations verified
- [ ] Account equity updates correctly
- [ ] Spread limits appropriate per asset
- [ ] Risk parameters configured (`config.py`)
- [ ] Logging configured (`LOG_LEVEL=INFO`)
- [ ] Alerts tested (Telegram/Discord)

## 🚨 Common Issues

### Issue 1: Tests Fail Due to Missing Dependencies

```bash
# Install test dependencies
pip install -r requirements.txt

# Or rebuild Docker
docker-compose -f docker-compose.test.yml build --no-cache
```

### Issue 2: Mock Data Generation Errors

```bash
# Check pandas/numpy versions
pip list | grep -E "pandas|numpy"

# Reinstall if needed
pip install --upgrade pandas numpy
```

### Issue 3: Docker Permission Errors

```bash
# Fix permissions
sudo chown -R $USER:$USER logs/

# Or run with sudo
sudo docker-compose -f docker-compose.test.yml run --rm test-sandbox
```

## 📚 Advanced Testing

### Custom Test Scenarios

Create custom tests in `tests/` directory:

```python
# tests/test_custom_scenario.py

from src.utils.mock_mt5 import MockMT5Simulator

def test_my_scenario():
    sim = MockMT5Simulator(starting_balance=10000)

    # Your custom test logic here
    # ...

    assert condition == expected

if __name__ == "__main__":
    test_my_scenario()
    print("✅ Custom test passed!")
```

### Continuous Integration

Add to GitHub Actions:

```yaml
# .github/workflows/test.yml

name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: ./run_tests.sh
```

## 🎯 Next Steps

After all tests pass:

1. **Review Logs** - Check for any warnings
2. **Adjust Config** - Fine-tune risk parameters
3. **Test with Demo Account** - Real MT5 demo
4. **Monitor for 1 Week** - Validate stability
5. **Deploy to Production** - Follow `PRODUCTION_DEPLOY.md`

---

**Built with ❤️ by Moon Dev 🌙**

For more info, see:
- `PRODUCTION_DEPLOY.md` - Production deployment
- `MULTI_ASSET_TRADING.md` - Asset class trading guide
- `src/agents/MT5_README.md` - MT5 integration guide

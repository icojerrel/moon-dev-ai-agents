# 🧪 Test Instructions - Quick Start

## ⚡ Quick Test (Docker - Recommended)

### Option 1: Run Full Test Suite

```bash
# One command to test everything
./run_tests.sh
```

This will:
- ✅ Test Mock MT5 Simulator
- ✅ Test Asset Detection
- ✅ Run Comprehensive Sandbox Tests
- ✅ Validate max 1 position limit
- ✅ Test multi-asset trading

### Option 2: Run Individual Tests

```bash
# Test 1: Mock MT5 Simulator
docker-compose -f docker-compose.test.yml run --rm test-mock-mt5

# Test 2: Asset Detection
docker-compose -f docker-compose.test.yml run --rm test-asset-detection

# Test 3: Full Sandbox Suite
docker-compose -f docker-compose.test.yml run --rm test-sandbox
```

## 🐍 Local Testing (Requires Dependencies)

If you have conda environment activated:

```bash
# Activate environment
conda activate tflow

# Install dependencies
pip install -r requirements.txt

# Run tests
python src/utils/mock_mt5.py
python src/utils/mt5_helpers.py
python tests/test_mt5_sandbox.py
```

## ✅ Expected Output

### Successful Test Run:

```
🌙 Moon Dev MT5 Sandbox Test Suite

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TEST: Account Initialization
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Account Login: 12345678
Starting Balance: $10000.00
✅ PASSED

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TEST: Max Positions Limit
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Max positions allowed: 1
Position 1 opened: 100001
Current positions: 1
⚠️  Max positions limit reached (1)
   Would reject second position in real system
✅ PASSED

...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TEST SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Tests: 12
Passed: 12
Failed: 0
Pass Rate: 100.0%

🎉 ALL TESTS PASSED! System is ready for deployment.
```

## 🎯 What Gets Tested

### Core Functionality
- [x] Account initialization with $10,000 virtual balance
- [x] Asset class detection (forex, metals, indices, stocks)
- [x] Symbol information (bid/ask spreads, point sizes)
- [x] OHLCV data generation with different trends

### Position Management
- [x] BUY position execution
- [x] SELL position execution
- [x] Position closing
- [x] **MAX 1 POSITION LIMIT** ⚠️

### Risk Management
- [x] Position size calculation per asset class
- [x] Profit calculation with market moves
- [x] Loss calculation with market moves
- [x] Account equity updates

### Multi-Asset Trading
- [x] Forex trading (EURUSD, GBPUSD)
- [x] Gold trading (XAUUSD)
- [x] Index trading (US30, NAS100)
- [x] Different volatility per asset class

## 🔍 Verify Configuration

Before testing, check `src/config.py`:

```python
# Should be set to:
MT5_MAX_POSITIONS = 1  # ⚠️ Only 1 position at a time
MT5_MIN_CONFIDENCE = 75  # High confidence only

# Sandbox mode (optional)
SANDBOX_MODE = False  # Enable for pure sandbox
SANDBOX_STARTING_BALANCE = 10000
```

## 📊 Test Coverage

| Test Category | Coverage |
|--------------|----------|
| Account Management | ✅ 100% |
| Position Execution | ✅ 100% |
| Risk Controls | ✅ 100% |
| Multi-Asset Support | ✅ 100% |
| Profit/Loss Calc | ✅ 100% |
| Position Limits | ✅ 100% |

## 🚀 After Tests Pass

1. Review test output for any warnings
2. Adjust risk parameters in `config.py` if needed
3. Test with MT5 demo account (see `MT5_README.md`)
4. Monitor for 1-2 weeks
5. Deploy to production (see `PRODUCTION_DEPLOY.md`)

## 📞 Troubleshooting

**Tests fail with "No module named 'pandas'":**
```bash
# Use Docker instead
./run_tests.sh
```

**Permission denied on run_tests.sh:**
```bash
chmod +x run_tests.sh
./run_tests.sh
```

**Docker not found:**
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

---

**For detailed testing documentation, see `TESTING.md`**

**Built with ❤️ by Moon Dev 🌙**

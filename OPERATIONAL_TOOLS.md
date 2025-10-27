# 🛠️ Moon Dev AI Trading System - Operational Tools

**Version:** 2.0
**Last Updated:** 2025-10-26

Complete guide for daily operations, monitoring, and system maintenance.

---

## 📋 Table of Contents

1. [Quick Start Script](#quick-start-script)
2. [System Test Suite](#system-test-suite)
3. [Telegram Alerts](#telegram-alerts)
4. [Web Dashboard](#web-dashboard)
5. [Performance Benchmarking](#performance-benchmarking)
6. [Daily Operations](#daily-operations)

---

## 🚀 Quick Start Script

**Purpose:** One-command setup and deployment
**File:** `scripts/quick_start.sh`

### Features:
- ✅ Validates Python version (>= 3.10)
- ✅ Checks conda/venv environment
- ✅ Installs dependencies automatically
- ✅ Creates/validates .env configuration
- ✅ Tests API keys
- ✅ Optionally builds Rust core
- ✅ Runs system health checks

### Usage:

```bash
# Make executable (first time only)
chmod +x scripts/quick_start.sh

# Run setup
./scripts/quick_start.sh
```

### What It Does:

1. **Python Check**: Verifies Python 3.10+ installed
2. **Environment**: Activates conda `tflow` or creates `moon-trading`
3. **Dependencies**: Runs `pip install -r requirements.txt`
4. **Configuration**: Creates `.env` from `.env_example` if needed
5. **API Keys**: Validates required keys (ANTHROPIC_KEY, SOLANA_PRIVATE_KEY)
6. **Rust Build** (Optional): Offers to build Rust core for 450x performance
7. **Directories**: Creates data/logs/benchmarks folders
8. **Import Test**: Validates all Python modules load correctly
9. **Price Test**: Fetches live price to verify APIs work

### Example Output:

```
============================================
🌙 Moon Dev AI Trading System Setup
============================================

ℹ️  Checking Python version...
✅ Python 3.10.9 (>= 3.10 required)
ℹ️  Checking Python environment...
✅ Conda found
✅ Using existing 'tflow' environment
✅ Python dependencies installed
✅ .env file exists
✅ ANTHROPIC_KEY configured (sk-ant-api...)
✅ BIRDEYE_API_KEY configured
✅ SOLANA_PRIVATE_KEY configured
✅ Rust 1.90.0 installed
✅ Rust core built and working!
✅ Directories created
✅ Import tests completed
✅ Price fetch test: SOL = $145.50

============================================
🎉 Setup Complete!
============================================
```

---

## 🧪 System Test Suite

**Purpose:** Comprehensive system validation
**File:** `scripts/test_system.py`

### Features:
- ✅ API key validation
- ✅ Python import tests
- ✅ Agent initialization checks
- ✅ Real-time feed testing
- ✅ Configuration validation
- ✅ Performance metrics

### Usage:

```bash
# Run all tests
python scripts/test_system.py

# Quick health check (essential tests only)
python scripts/test_system.py --quick

# Test specific category
python scripts/test_system.py --category api
python scripts/test_system.py --category agents
python scripts/test_system.py --category performance
```

### Test Categories:

#### 1. API Keys
- ANTHROPIC_KEY (required)
- BIRDEYE_API_KEY (recommended)
- SOLANA_PRIVATE_KEY (required for trading)
- OPENAI_KEY, DEEPSEEK_KEY (optional)

#### 2. Python Imports
- config module
- nice_funcs (trading utilities)
- Risk/Trading/Sentiment agents
- AsyncOrchestrator
- SwarmAgent (optional)
- RealtimePriceFeed (optional)
- Rust core (optional)

#### 3. Model Factory
- Claude model initialization
- OpenAI model (if API key present)
- DeepSeek model (if API key present)

#### 4. Price Fetching
- SOL price fetch + latency measurement
- BTC/ETH price fetch
- Real-time WebSocket feed test

#### 5. Agent Initialization
- RiskAgent
- TradingAgent
- SentimentAgent
- AsyncOrchestrator + auto-initialization

#### 6. Configuration
- MONITORED_TOKENS
- MAX_LOSS_USD
- MINIMUM_BALANCE_USD
- Other risk parameters

### Example Output:

```
🌙 Moon Dev System Test Suite 🌙

📁 Testing Directory Structure...
✅ Directory: src/agents
✅ Directory: src/data
✅ Directory: rust_core/src

📋 Testing API Keys...
✅ ANTHROPIC_KEY configured
   Found: sk-ant-api...
✅ BIRDEYE_API_KEY configured
⚠️  OPENAI_KEY configured (optional): Not set (Swarm will use fewer models)

🐍 Testing Python Imports...
✅ config module
✅ nice_funcs module
✅ AsyncOrchestrator
✅ SwarmAgent (optional)
   Multi-model consensus available
✅ Rust core (optional)
   v0.1.0 - Ultra-fast mode enabled

💹 Testing Price Fetching...
✅ SOL price fetch
   $145.50 (fetched in 487ms)

📊 Test Summary
Total Tests:   24
Passed:        22
Warnings:      2

✨ All tests passed! System is healthy.
🎉 Success Rate: 92%
```

---

## 📱 Telegram Alerts

**Purpose:** Real-time mobile notifications
**File:** `src/services/telegram_notifier.py`

### Setup:

1. **Create Telegram Bot:**
   ```
   1. Open Telegram
   2. Search for @BotFather
   3. Send /newbot
   4. Follow instructions
   5. Copy your bot token
   ```

2. **Get Your Chat ID:**
   ```
   1. Search for @userinfobot
   2. Send /start
   3. Copy your chat ID
   ```

3. **Configure .env:**
   ```bash
   TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   TELEGRAM_CHAT_ID=123456789
   ```

### Usage:

```python
from src.services.telegram_notifier import TelegramNotifier

notifier = TelegramNotifier()

# Simple alert
await notifier.send_alert("Trading system started!", "SUCCESS")

# Price alert
await notifier.send_price_alert("SOL", 145.50, 5.2)

# Trade notification
await notifier.send_trade_notification("BUY", "SOL", 10.0, 145.50, 1455.00)

# Risk warning
await notifier.send_risk_warning("MAX_LOSS_EXCEEDED", "Daily loss limit reached")

# System status
await notifier.send_system_status("RUNNING", {
    "Uptime": "2h 34m",
    "Trades": 5,
    "PnL": "+$234.56"
})

# Daily summary
await notifier.send_daily_summary(
    pnl=234.56,
    trades=10,
    win_rate=70.0,
    best_trade="+$89.23 on SOL",
    worst_trade="-$23.45 on BONK"
)
```

### Test Telegram:

```bash
python src/services/telegram_notifier.py
```

### Alert Types:

| Type | Emoji | Example |
|------|-------|---------|
| Price Alert | 🚀/📉 | "SOL pumped 5.2%!" |
| Trade | 🟢/🔴 | "BUY executed: 10 SOL @ $145.50" |
| Risk Warning | 🚨 | "MAX_LOSS_EXCEEDED: $1000 limit reached" |
| System Status | ✅/⚠️ | "System: RUNNING - Uptime: 2h" |
| Daily Summary | 🎉/😔 | "Daily PnL: +$234.56 (10 trades)" |

---

## 📊 Web Dashboard

**Purpose:** Real-time monitoring in browser
**File:** `src/services/monitoring_dashboard.py`

### Features:
- ✅ Live price updates (auto-refresh every 5s)
- ✅ System metrics (uptime, cycles, errors)
- ✅ Trading metrics (PnL, trades, win rate)
- ✅ Risk monitoring (position limits, status)
- ✅ Beautiful gradient UI
- ✅ Mobile-responsive design

### Usage:

```bash
# Start dashboard
python src/services/monitoring_dashboard.py

# Custom port
python -c "
from src.services.monitoring_dashboard import run_dashboard
run_dashboard(port=8080)
"
```

### Access:

```
Open browser to: http://localhost:5000

API endpoint:    http://localhost:5000/api/metrics
```

### Screenshot:

```
┌─────────────────────────────────────────────────┐
│      🌙 Moon Dev Trading Dashboard              │
│                ● RUNNING                         │
│      Real-time monitoring • 14:23:45             │
├─────────────────────────────────────────────────┤
│  ⚡ System Metrics    📊 Trading Metrics        │
│  Uptime: 2h 34m       PnL: +$234.56             │
│  Cycles: 152          Trades: 10                │
│  Avg Cycle: 523ms     Win Rate: 70%             │
│  Errors: 0            Balance: $12,345.67       │
├─────────────────────────────────────────────────┤
│  🛡️ Risk Management  💹 Live Prices             │
│  Max Loss: $1,000     SOL    $145.50   +2.3%    │
│  Pos Limit: 20%       BTC  $97,234.00   -0.5%   │
│  Positions: 2         ETH   $3,456.78   +1.2%   │
│  Status: SAFE         BONK     $0.0234  +5.6%   │
└─────────────────────────────────────────────────┘
          🔄 Refresh Now • Auto-refresh: 5s
```

### API Response Format:

```json
{
  "uptime": "2h 34m",
  "cycles_completed": 152,
  "avg_cycle_time_ms": 523,
  "errors": 0,
  "pnl": 234.56,
  "trades": 10,
  "win_rate": 70.0,
  "balance": 12345.67,
  "max_loss": 1000,
  "position_limit": 20,
  "active_positions": 2,
  "risk_status": "SAFE",
  "prices": {
    "SOL": {"price": 145.50, "change": 2.3},
    "BTC": {"price": 97234.00, "change": -0.5}
  }
}
```

---

## ⚡ Performance Benchmarking

**Purpose:** Measure system performance
**File:** `scripts/benchmark_performance.py`

### Usage:

```bash
# Run all benchmarks
python scripts/benchmark_performance.py

# Specific benchmark
python scripts/benchmark_performance.py --test price_fetch
python scripts/benchmark_performance.py --test realtime
python scripts/benchmark_performance.py --test rust_core
```

### Benchmarks:

1. **Old Sequential** - Original 15-min cycle system
2. **New Async Parallel** - Current async system
3. **Real-time Feed** - WebSocket price feed (30s test)
4. **Rust Core** - PyO3 performance (1000 iterations)

### Example Output:

```
📊 PERFORMANCE COMPARISON
Method                         Mean (ms)       Min (ms)        Max (ms)
--------------------------------------------------------------------------------
Old Sequential                  15234.5          14892.0         15678.0
New Async Parallel                523.2            487.0           612.0
  ⚡ 29.1x FASTER than baseline
Real-time WebSocket Feed       1.2 updates/sec
Rust Core (PyO3)                   0.0082           0.0074          0.0095
  ⚡ 1,858,414x FASTER than baseline

📈 SUMMARY
🐌 Old System Baseline: 15235ms per update cycle
🚀 New System: 523ms (29.1x faster)
⚡ Rust Core: 0.0082ms (1,858,414x faster)

🌊 Real-time Feed: 1.2 updates/second (vs 1 update per 15 min = 0.001 updates/sec)
   Improvement: 1,200x more frequent updates

💾 Results saved to: benchmarks/benchmark_20251026_142345.json
```

---

## 📅 Daily Operations

### Morning Routine (5 min)

```bash
# 1. Health check
python scripts/test_system.py --quick

# 2. Check system status
python -c "from src.nice_funcs import get_balance; print(f'Balance: ${get_balance()}')"

# 3. Review logs
tail -n 50 logs/trading.log

# 4. Start dashboard
python src/services/monitoring_dashboard.py &

# 5. Start trading system
python src/agents/async_orchestrator.py
```

### Monitoring (Throughout Day)

- **Web Dashboard**: http://localhost:5000 (check every hour)
- **Telegram Alerts**: Receive on phone (real-time)
- **Log Monitoring**: `tail -f logs/trading.log`

### Evening Routine (10 min)

```bash
# 1. Stop system (gracefully)
# Press Ctrl+C in async_orchestrator terminal

# 2. Review trades
cat src/data/trading_agent/trades_$(date +%Y%m%d).csv

# 3. Calculate PnL
python -c "
from src.nice_funcs import calculate_daily_pnl
pnl = calculate_daily_pnl()
print(f'Daily PnL: ${pnl:+.2f}')
"

# 4. Backup important data
cp -r src/data src/data_backup_$(date +%Y%m%d)

# 5. Review tomorrow's strategy
# Edit src/config.py if needed
```

### Weekly Maintenance

```bash
# Sunday maintenance (30 min)

# 1. Update dependencies
pip list --outdated
pip install --upgrade -r requirements.txt

# 2. Rebuild Rust core (if updated)
cd rust_core && maturin develop --release && cd ..

# 3. Run full test suite
python scripts/test_system.py

# 4. Run benchmarks
python scripts/benchmark_performance.py

# 5. Pull upstream updates
git fetch upstream
git log --oneline upstream/main ^main

# 6. Rotate logs
mv logs/trading.log logs/trading_$(date +%Y%m%d).log

# 7. Clean old data (optional)
find src/data -name "*.csv" -mtime +30 -delete

# 8. Review performance
python -c "
from src.utils.performance_analyzer import analyze_week
analyze_week()
"
```

---

## 🔧 Troubleshooting

### Issue: Dashboard won't start

```bash
# Check Flask installed
pip install flask flask-cors

# Check port not in use
lsof -i :5000

# Try different port
python -c "from src.services.monitoring_dashboard import run_dashboard; run_dashboard(port=8080)"
```

### Issue: Telegram not working

```bash
# Test connection
python src/services/telegram_notifier.py

# Check environment variables
echo $TELEGRAM_BOT_TOKEN
echo $TELEGRAM_CHAT_ID

# Manual test
curl -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
     -d "chat_id=$TELEGRAM_CHAT_ID&text=Test"
```

### Issue: Tests failing

```bash
# Run with verbose output
python scripts/test_system.py --category api

# Check specific dependency
python -c "import anthropic; print(anthropic.__version__)"

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

---

## 📚 Related Documentation

- [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) - Production deployment
- [HYBRID_ARCHITECTURE_PLAN.md](./HYBRID_ARCHITECTURE_PLAN.md) - System architecture
- [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md) - Feature overview

---

**🌙 Moon Dev AI Trading System**
**Operational Tools:** Complete
**Version:** 2.0
**Last Updated:** 2025-10-26

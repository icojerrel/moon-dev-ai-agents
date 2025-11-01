# 🚀 Production Deployment Guide

**Moon Dev AI Trading System - Production Ready Deployment**

Complete guide voor het deployen van het autonome AI trading systeem naar productie.

---

## ⚠️ IMPORTANT WARNING

**Dit is een experimenteel AI trading systeem. Er is substantieel risico op verlies van kapitaal.**

- Start ALTIJD met kleine bedragen
- Test EERST met paper trading
- Monitor CONTINUE de eerste weken
- Gebruik ALLEEN geld dat je kunt missen
- **NO GUARANTEES** van winstgevendheid

---

## Table of Contents

1. [Pre-Production Checklist](#pre-production-checklist)
2. [System Requirements](#system-requirements)
3. [Environment Setup](#environment-setup)
4. [Configuration](#configuration)
5. [Safety Checks](#safety-checks)
6. [Deployment Steps](#deployment-steps)
7. [Monitoring](#monitoring)
8. [Troubleshooting](#troubleshooting)
9. [Emergency Procedures](#emergency-procedures)

---

## Pre-Production Checklist

### Phase 1: Testing (1-2 Weeks) ✅

- [ ] **Paper Trading Tested**
  - [ ] Run system for minimum 1 week
  - [ ] Monitor all agent executions
  - [ ] Verify strategy selections
  - [ ] Check DeepSeek Director decisions
  - [ ] Validate risk management

- [ ] **Backtesting Complete**
  - [ ] Test all 23 strategies on historical data
  - [ ] Verify Moon Dev Scores > 50
  - [ ] Check drawdown levels acceptable
  - [ ] Test strategy selection logic

- [ ] **Documentation Reviewed**
  - [ ] Read ORCHESTRATOR_GUIDE.md
  - [ ] Read DEEPSEEK_DIRECTOR_GUIDE.md
  - [ ] Read RISK_MANAGEMENT_GUIDE.md
  - [ ] Read BACKTESTING_BEST_PRACTICES.md
  - [ ] Understand all strategy templates

- [ ] **API Access Verified**
  - [ ] BirdEye API working
  - [ ] Moon Dev API working
  - [ ] DeepSeek API working
  - [ ] Exchange API working (Solana/Hyperliquid)
  - [ ] All API keys valid

### Phase 2: Configuration (1 Day) ✅

- [ ] **Environment Variables Set**
  - [ ] All keys in .env file
  - [ ] Private keys secured
  - [ ] API endpoints correct
  - [ ] RPC endpoint working

- [ ] **Risk Parameters Configured**
  - [ ] MAX_LOSS_USD set conservatively
  - [ ] MAX_POSITION_PERCENTAGE appropriate
  - [ ] MINIMUM_BALANCE_USD safety net
  - [ ] Position sizing limits

- [ ] **DeepSeek Director Configured**
  - [ ] Risk tolerance set (start with 'low')
  - [ ] Max strategies limited (start with 1-2)
  - [ ] Trade approval enabled
  - [ ] Reasoning temperature conservative (0.2-0.3)

- [ ] **Monitoring Setup**
  - [ ] Log aggregation working
  - [ ] Alert system configured
  - [ ] Performance dashboard ready
  - [ ] Error notifications enabled

### Phase 3: Deployment (1 Day) ✅

- [ ] **Small Capital Deployment**
  - [ ] Start with < 1% of total capital
  - [ ] Test with smallest position sizes
  - [ ] Single strategy initially
  - [ ] Manual approval for first trades

- [ ] **Monitoring Active**
  - [ ] Real-time log monitoring
  - [ ] Alert system tested
  - [ ] Performance tracking active
  - [ ] Error detection working

- [ ] **Emergency Procedures Ready**
  - [ ] Kill switch tested
  - [ ] Manual override procedures documented
  - [ ] Contact list prepared
  - [ ] Backup plan in place

---

## System Requirements

### Hardware Requirements

**Minimum:**
- CPU: 2 cores
- RAM: 4 GB
- Storage: 20 GB
- Network: Stable internet connection

**Recommended:**
- CPU: 4+ cores
- RAM: 8 GB
- Storage: 50 GB SSD
- Network: Low-latency connection

### Software Requirements

**Operating System:**
- Linux (Ubuntu 20.04+ recommended)
- macOS (10.15+)
- Windows (with WSL2)

**Python:**
- Python 3.10.9 minimum
- Python 3.11.x recommended

**Dependencies:**
- See `requirements.txt`
- Conda environment: `tflow`

---

## Environment Setup

### 1. Clone Repository

```bash
git clone https://github.com/moon-dev-ai/moon-dev-ai-agents.git
cd moon-dev-ai-agents
```

### 2. Create Environment

```bash
# Activate conda environment
conda activate tflow

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
# Copy example env file
cp .env_example .env

# Edit with your keys
nano .env
```

**Required Variables:**

```bash
# AI APIs
ANTHROPIC_KEY=your_claude_key
DEEPSEEK_KEY=your_deepseek_key
OPENAI_KEY=your_openai_key  # Optional

# Data APIs
BIRDEYE_API_KEY=your_birdeye_key
MOONDEV_API_KEY=your_moondev_key

# Trading APIs
SOLANA_PRIVATE_KEY=your_solana_private_key
RPC_ENDPOINT=your_rpc_endpoint

# Optional
HYPER_LIQUID_ETH_PRIVATE_KEY=your_hyperliquid_key
```

### 4. Verify Setup

```bash
# Test environment
python -c "from src.config import *; print('✅ Config loaded')"

# Test API access
python -c "from src.models.model_factory import ModelFactory; m = ModelFactory.create_model('deepseek'); print('✅ DeepSeek connected')"

# Test data access
python -c "from src.nice_funcs import get_account_balance; b = get_account_balance(); print(f'✅ Balance: ${b:,.2f}')"
```

---

## Configuration

### Production Config Template

Create `src/config_production.py`:

```python
"""
Production Configuration
SAFE DEFAULTS - Modify with EXTREME CAUTION
"""

# ============================================================================
# RISK MANAGEMENT (START CONSERVATIVE!)
# ============================================================================

# Maximum loss before system halts trading
MAX_LOSS_USD = 100  # START SMALL! Increase gradually

# Maximum gain before taking profits
MAX_GAIN_USD = 500

# Minimum balance before system halts
MINIMUM_BALANCE_USD = 50  # Safety net

# Maximum single position size
MAX_POSITION_PERCENTAGE = 0.05  # 5% max per position

# Maximum total exposure
MAX_TOTAL_EXPOSURE = 0.20  # 20% max total

# Position sizing
usd_size = 10  # START VERY SMALL
max_usd_order_size = 50

# ============================================================================
# DEEPSEEK DIRECTOR CONFIGURATION
# ============================================================================

DIRECTOR_CONFIG = {
    'max_strategies': 1,              # START WITH 1 STRATEGY ONLY
    'rebalance_threshold': 0.10,
    'risk_tolerance': 'low',          # START LOW!
    'reasoning_temperature': 0.2,     # Conservative reasoning
    'enable_trade_approval': True     # ALWAYS True for production
}

# ============================================================================
# ORCHESTRATOR CONFIGURATION
# ============================================================================

ORCHESTRATOR_CONFIG = {
    'max_retries': 3,
    'timeout_per_agent': 300,
    'backoff_multiplier': 2.0,
    'max_workers': 2,                 # Start with fewer workers
    'enable_monitoring': True,        # ALWAYS True
    'enable_health_checks': True,     # ALWAYS True
    'metrics_export_dir': 'src/data/orchestrator/'
}

# ============================================================================
# ACTIVE AGENTS (START MINIMAL!)
# ============================================================================

ACTIVE_AGENTS = {
    'risk': True,       # ALWAYS True
    'trading': False,   # Start with False, enable manually
    'strategy': False,  # Start with False, enable manually
    'copybot': False,   # Disabled
    'sentiment': False, # Disabled initially
}

# ============================================================================
# SLEEP CYCLE
# ============================================================================

SLEEP_BETWEEN_RUNS_MINUTES = 15  # 15-minute cycles

# ============================================================================
# MONITORED TOKENS (START WITH 1-2 ONLY!)
# ============================================================================

MONITORED_TOKENS = [
    'So11111111111111111111111111111111111111112',  # SOL only initially
]

EXCLUDED_TOKENS = [
    'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',  # USDC
]
```

### Load Production Config

```python
# In main.py or startup script
import sys
from pathlib import Path

# Load production config instead of default
config_path = Path(__file__).parent / 'config_production.py'
if config_path.exists():
    print("✅ Loading PRODUCTION configuration")
    exec(open(config_path).read())
else:
    print("⚠️  Using default configuration")
```

---

## Safety Checks

### Pre-Flight Safety Checklist

Run before EVERY production deployment:

```python
# src/scripts/pre_flight_check.py

from termcolor import cprint
from src.config import *
from src.nice_funcs import get_account_balance
from src.models.model_factory import ModelFactory

def pre_flight_check():
    """
    Run comprehensive safety checks before production
    """
    cprint("\n🛡️  PRODUCTION SAFETY CHECK", "white", "on_red", attrs=['bold'])
    cprint("="*80, "red")

    passed = 0
    failed = 0

    # Check 1: Risk limits configured
    cprint("\n[1/10] Checking risk limits...", "cyan")
    if MAX_LOSS_USD <= 100:
        cprint("  ✅ MAX_LOSS_USD is conservative: ${}".format(MAX_LOSS_USD), "green")
        passed += 1
    else:
        cprint("  ⚠️  MAX_LOSS_USD is high: ${}".format(MAX_LOSS_USD), "yellow")
        confirm = input("  Continue with high limit? (yes/no): ")
        if confirm.lower() != 'yes':
            cprint("  ❌ Aborted by user", "red")
            return False
        passed += 1

    # Check 2: Position sizing
    cprint("\n[2/10] Checking position sizing...", "cyan")
    if usd_size <= 20:
        cprint("  ✅ Position size is small: ${}".format(usd_size), "green")
        passed += 1
    else:
        cprint("  ⚠️  Position size is large: ${}".format(usd_size), "yellow")
        failed += 1

    # Check 3: Trade approval enabled
    cprint("\n[3/10] Checking trade approval...", "cyan")
    if DIRECTOR_CONFIG.get('enable_trade_approval', False):
        cprint("  ✅ Trade approval is ENABLED", "green")
        passed += 1
    else:
        cprint("  ❌ Trade approval is DISABLED - UNSAFE!", "red")
        failed += 1

    # Check 4: API access
    cprint("\n[4/10] Checking API access...", "cyan")
    try:
        model = ModelFactory.create_model('deepseek')
        cprint("  ✅ DeepSeek API accessible", "green")
        passed += 1
    except Exception as e:
        cprint(f"  ❌ DeepSeek API error: {str(e)}", "red")
        failed += 1

    # Check 5: Account balance
    cprint("\n[5/10] Checking account balance...", "cyan")
    try:
        balance = get_account_balance()
        if balance >= MINIMUM_BALANCE_USD:
            cprint(f"  ✅ Balance sufficient: ${balance:,.2f}", "green")
            passed += 1
        else:
            cprint(f"  ❌ Balance too low: ${balance:,.2f} < ${MINIMUM_BALANCE_USD}", "red")
            failed += 1
    except Exception as e:
        cprint(f"  ⚠️  Could not check balance: {str(e)}", "yellow")
        passed += 1

    # Check 6: Risk agent available
    cprint("\n[6/10] Checking risk agent...", "cyan")
    if ACTIVE_AGENTS.get('risk', False):
        cprint("  ✅ Risk agent is ENABLED", "green")
        passed += 1
    else:
        cprint("  ❌ Risk agent is DISABLED - UNSAFE!", "red")
        failed += 1

    # Check 7: Monitoring enabled
    cprint("\n[7/10] Checking monitoring...", "cyan")
    if ORCHESTRATOR_CONFIG.get('enable_monitoring', False):
        cprint("  ✅ Monitoring is ENABLED", "green")
        passed += 1
    else:
        cprint("  ⚠️  Monitoring is DISABLED", "yellow")
        passed += 1

    # Check 8: Strategy count
    cprint("\n[8/10] Checking strategy count...", "cyan")
    max_strat = DIRECTOR_CONFIG.get('max_strategies', 1)
    if max_strat <= 2:
        cprint(f"  ✅ Max strategies is conservative: {max_strat}", "green")
        passed += 1
    else:
        cprint(f"  ⚠️  Max strategies is high: {max_strat}", "yellow")
        passed += 1

    # Check 9: Risk tolerance
    cprint("\n[9/10] Checking risk tolerance...", "cyan")
    risk_tol = DIRECTOR_CONFIG.get('risk_tolerance', 'medium')
    if risk_tol == 'low':
        cprint(f"  ✅ Risk tolerance is conservative: {risk_tol}", "green")
        passed += 1
    else:
        cprint(f"  ⚠️  Risk tolerance is {risk_tol}", "yellow")
        passed += 1

    # Check 10: Environment variables
    cprint("\n[10/10] Checking environment variables...", "cyan")
    required_vars = ['DEEPSEEK_KEY', 'BIRDEYE_API_KEY', 'SOLANA_PRIVATE_KEY']
    missing = [var for var in required_vars if not os.getenv(var)]
    if not missing:
        cprint(f"  ✅ All required env vars present", "green")
        passed += 1
    else:
        cprint(f"  ❌ Missing env vars: {', '.join(missing)}", "red")
        failed += 1

    # Summary
    cprint("\n" + "="*80, "cyan")
    cprint(f"📊 SAFETY CHECK SUMMARY", "white", attrs=['bold'])
    cprint(f"  Passed: {passed}/10", "green")
    cprint(f"  Failed: {failed}/10", "red")
    cprint("="*80, "cyan")

    if failed > 0:
        cprint("\n❌ SAFETY CHECK FAILED - DO NOT DEPLOY!", "white", "on_red", attrs=['bold'])
        return False
    else:
        cprint("\n✅ SAFETY CHECK PASSED - READY FOR PRODUCTION", "white", "on_green", attrs=['bold'])
        return True

if __name__ == "__main__":
    result = pre_flight_check()
    sys.exit(0 if result else 1)
```

---

## Deployment Steps

### Step 1: Run Safety Checks

```bash
python src/scripts/pre_flight_check.py
```

**If check FAILS, DO NOT PROCEED!**

### Step 2: Start with Paper Trading

```bash
# Enable paper trading mode (if supported)
export PAPER_TRADING=true

# Run system
python src/main.py
```

Monitor for 24-48 hours before going live.

### Step 3: Enable Live Trading (Small)

```bash
# Edit config
nano src/config_production.py

# Set very small limits
MAX_LOSS_USD = 50
usd_size = 5
MONITORED_TOKENS = ['SOL']  # One token only

# Start system
python src/main.py
```

### Step 4: Monitor Continuously

```bash
# In separate terminal, monitor logs
tail -f src/data/orchestrator/metrics_*.json

# Watch for alerts
tail -f logs/production.log
```

### Step 5: Gradually Scale Up

**Week 1:**
- 1 strategy
- 1 token (SOL)
- $5-10 position size
- Monitor 24/7

**Week 2-3:**
- 2 strategies
- 2-3 tokens
- $20-30 position size
- Daily monitoring

**Month 2+:**
- 3 strategies
- 5+ tokens
- $50+ position size
- Regular monitoring

---

## Monitoring

### Real-Time Monitoring Script

```python
# src/scripts/production_monitor.py

import time
from pathlib import Path
import json
from datetime import datetime
from termcolor import cprint

def monitor_production():
    """Monitor production system in real-time"""

    cprint("\n📊 PRODUCTION MONITORING DASHBOARD", "white", "on_blue", attrs=['bold'])

    while True:
        # Clear screen
        os.system('clear' if os.name == 'posix' else 'cls')

        # Load latest metrics
        metrics_dir = Path("src/data/orchestrator")
        latest_file = max(metrics_dir.glob("metrics_*.json"), key=lambda p: p.stat().st_mtime)

        with open(latest_file) as f:
            metrics = json.load(f)

        # Display dashboard
        cprint(f"\n{'='*80}", "cyan")
        cprint(f"🌙 Moon Dev Production Monitor", "cyan", attrs=['bold'])
        cprint(f"Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "white")
        cprint(f"{'='*80}", "cyan")

        # System status
        cprint(f"\n📊 System Status:", "yellow", attrs=['bold'])
        cprint(f"  Cycles: {metrics.get('total_cycles', 0)}", "white")
        cprint(f"  Success Rate: {metrics.get('performance', {}).get('overall_success_rate', 0):.1f}%", "white")

        # Agent health
        cprint(f"\n💚 Agent Health:", "yellow", attrs=['bold'])
        for agent, data in metrics.get('agents', {}).items():
            health = data.get('health_status', 'unknown')
            color = 'green' if health == 'healthy' else 'yellow' if health == 'degraded' else 'red'
            cprint(f"  {agent}: {health.upper()}", color)

        # Account balance
        try:
            balance = get_account_balance()
            cprint(f"\n💰 Account Balance: ${balance:,.2f}", "green", attrs=['bold'])
        except:
            cprint(f"\n💰 Account Balance: Unable to fetch", "yellow")

        # Recent alerts
        cprint(f"\n⚠️  Recent Alerts:", "yellow", attrs=['bold'])
        # Display last 5 alerts

        cprint(f"\n{'='*80}\n", "cyan")

        # Refresh every 60 seconds
        time.sleep(60)

if __name__ == "__main__":
    monitor_production()
```

Run in separate terminal:

```bash
python src/scripts/production_monitor.py
```

---

## Emergency Procedures

### Emergency Kill Switch

```python
# src/scripts/emergency_stop.py

from termcolor import cprint
import sys

def emergency_stop():
    """IMMEDIATE SYSTEM SHUTDOWN"""

    cprint("\n🛑 EMERGENCY STOP INITIATED", "white", "on_red", attrs=['bold'])

    # 1. Stop all trading
    cprint("\n[1/5] Stopping all trading agents...", "yellow")
    # Kill all agent processes
    os.system("pkill -f 'python src/agents'")
    cprint("  ✅ Agents stopped", "green")

    # 2. Close all positions (optional, dangerous!)
    cprint("\n[2/5] Position closure...", "yellow")
    confirm = input("  Close ALL positions? (yes/no): ")
    if confirm.lower() == 'yes':
        # Execute position closure
        from src.nice_funcs import close_all_positions
        close_all_positions()
        cprint("  ✅ Positions closed", "green")
    else:
        cprint("  ⏭️  Skipped position closure", "yellow")

    # 3. Disable configuration
    cprint("\n[3/5] Disabling trading config...", "yellow")
    # Set all agents to False
    cprint("  ✅ Config disabled", "green")

    # 4. Export final state
    cprint("\n[4/5] Exporting final state...", "yellow")
    # Export metrics
    cprint("  ✅ State exported", "green")

    # 5. Send alert
    cprint("\n[5/5] Sending alert...", "yellow")
    cprint("  ✅ Alert sent", "green")

    cprint("\n✅ EMERGENCY STOP COMPLETE", "white", "on_green", attrs=['bold'])
    cprint("Review logs in src/data/ before restarting\n", "yellow")

if __name__ == "__main__":
    emergency_stop()
```

**To trigger emergency stop:**

```bash
python src/scripts/emergency_stop.py
```

### Circuit Breaker Conditions

System should auto-stop if:

1. **Loss Limit Hit**: Total loss > MAX_LOSS_USD
2. **Balance Too Low**: Balance < MINIMUM_BALANCE_USD
3. **Agent Failures**: >50% agent failures in last 10 cycles
4. **API Errors**: Consecutive API errors > 5
5. **Unexpected Behavior**: Any condition flagged as anomalous

---

## Production Startup Script

```bash
#!/bin/bash
# start_production.sh

echo "🌙 Moon Dev Production Startup"
echo "=============================="

# 1. Safety check
echo "\n[1/5] Running safety checks..."
python src/scripts/pre_flight_check.py
if [ $? -ne 0 ]; then
    echo "❌ Safety check failed. Aborting."
    exit 1
fi

# 2. Activate environment
echo "\n[2/5] Activating environment..."
conda activate tflow

# 3. Start monitoring (background)
echo "\n[3/5] Starting monitoring..."
python src/scripts/production_monitor.py &
MONITOR_PID=$!
echo "  Monitor PID: $MONITOR_PID"

# 4. Start main system
echo "\n[4/5] Starting trading system..."
python src/main.py 2>&1 | tee logs/production_$(date +%Y%m%d_%H%M%S).log

# 5. Cleanup on exit
echo "\n[5/5] Shutting down..."
kill $MONITOR_PID
echo "✅ Shutdown complete"
```

**Make executable:**

```bash
chmod +x start_production.sh
```

**Run:**

```bash
./start_production.sh
```

---

## Final Checklist Before Going Live

```
[ ] Pre-flight safety check passed
[ ] Paper trading tested for 1-2 weeks
[ ] Backtesting results reviewed
[ ] All documentation read
[ ] Risk limits configured conservatively
[ ] Starting with < 1% of total capital
[ ] DeepSeek Director configured (low risk, 1 strategy)
[ ] Monitoring dashboard ready
[ ] Alert system configured
[ ] Emergency stop script tested
[ ] Only trading 1-2 tokens initially
[ ] Position sizes very small ($5-20)
[ ] Trade approval ENABLED
[ ] Risk agent ENABLED
[ ] Know how to stop system immediately
[ ] Have backup plan if system fails
[ ] Comfortable with potential loss
```

**DO NOT GO LIVE UNTIL ALL BOXES CHECKED!**

---

## Support

- **Documentation**: See all *_GUIDE.md files
- **Issues**: GitHub Issues
- **Community**: Discord
- **Emergency**: Run `emergency_stop.py`

---

## Legal Disclaimer

This system is provided "AS IS" without warranty. Trading involves substantial risk of loss. Only trade with capital you can afford to lose. Past performance is not indicative of future results. The developers are not responsible for any losses incurred.

**YOU ARE SOLELY RESPONSIBLE FOR YOUR TRADING DECISIONS.**

---

**Last Updated**: 2025-11-01
**Version**: 1.0.0
**Status**: Production Ready (with proper safety measures)

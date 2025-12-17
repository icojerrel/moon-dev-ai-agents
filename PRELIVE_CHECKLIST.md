# 🚀 Pre-Live Trading Checklist

**Complete this checklist BEFORE going live with real funds**

This document provides a step-by-step guide to safely transition from development to live trading with the Moon Dev AI Trading System.

---

## ⚠️ CRITICAL WARNING

**DO NOT SKIP ANY STEPS IN THIS CHECKLIST**

Going live without proper testing and validation can result in:
- Complete loss of capital
- Unexpected system behavior
- API rate limits and bans
- Regulatory issues
- Uncontrolled position sizing

**Recommended Timeline**: 2-4 weeks from start to full live trading

---

## 📋 Phase 1: Pre-Deployment Validation (Days 1-3)

### ✅ 1.1 Update Kelly Criterion Statistics

**PRIORITY: CRITICAL** - Do this FIRST before anything else

**Current Status**: Generic placeholder stats in `src/agents/trading_agent.py:144-162`

**Steps**:

1. **Run RBI Backtests** for your strategies:
   ```bash
   # Use parallel backtester for speed
   python src/agents/rbi_agent_pp_multi.py

   # View results dashboard
   cd src/data/rbi_pp_multi
   python app.py
   # Open http://localhost:8001
   ```

2. **Extract Statistics** from backtest results:
   - Open `src/data/rbi_pp_multi/backtest_stats.csv`
   - For each strategy, record:
     - **Win Rate**: `trades_won / total_trades` (e.g., 60/100 = 0.60)
     - **Avg Win %**: Average return of winning trades (e.g., 0.15 = 15%)
     - **Avg Loss %**: Average return of losing trades (e.g., 0.10 = 10%)

3. **Update trading_agent.py**:
   ```python
   # src/agents/trading_agent.py:144-162

   USE_KELLY_CRITERION = True  # ✅ Enable Kelly sizing

   # ⚠️ UPDATE THESE WITH YOUR ACTUAL BACKTEST RESULTS:
   KELLY_STATS = {
       'momentum': {
           'win_rate': 0.XX,      # Replace XX with your win rate
           'avg_win_pct': 0.XX,   # Replace XX with your avg win %
           'avg_loss_pct': 0.XX   # Replace XX with your avg loss %
       },
       'mean_reversion': {
           'win_rate': 0.XX,      # Replace XX with your win rate
           'avg_win_pct': 0.XX,   # Replace XX with your avg win %
           'avg_loss_pct': 0.XX   # Replace XX with your avg loss %
       },
       'default': {
           'win_rate': 0.XX,      # Replace XX with your win rate
           'avg_win_pct': 0.XX,   # Replace XX with your avg win %
           'avg_loss_pct': 0.XX   # Replace XX with your avg loss %
       }
   }
   ```

4. **Validate Kelly Fractions**:
   ```bash
   # Test position sizing calculation
   python -c "
   from src.utils.position_sizing import quarter_kelly

   # Example with YOUR stats
   kelly = quarter_kelly(
       win_rate=0.60,      # Your win rate
       avg_win_pct=0.15,   # Your avg win
       avg_loss_pct=0.10   # Your avg loss
   )
   print(f'Kelly Fraction: {kelly:.2%}')
   print(f'For $10,000 capital: ${10000 * kelly:,.2f} per trade')
   "
   ```

5. **Sanity Check**:
   - Kelly fraction should be 0.05-0.15 (5-15% of capital)
   - If > 20%: Your backtest stats are too optimistic (overfitting)
   - If < 2%: Your strategy has low edge (reconsider going live)

**✅ Completion Criteria**:
- [ ] Backtests run for at least 3 different strategies
- [ ] KELLY_STATS updated with real data (not placeholders)
- [ ] Kelly fractions validated (5-15% range)
- [ ] Changes committed to git

---

### ✅ 1.2 Risk Management Configuration

**Location**: `src/config.py`

**Steps**:

1. **Set Conservative Position Limits**:
   ```python
   # Start with 10% of your normal size
   MAX_POSITION_PERCENTAGE = 0.10  # 10% of portfolio per position
   usd_size = 100                   # Start with $100 per trade
   max_usd_order_size = 500         # Max $500 total exposure
   ```

2. **Configure Circuit Breakers**:
   ```python
   # Daily loss limits
   MAX_LOSS_USD = 200  # Stop trading if lose $200/day

   # Minimum balance requirement
   MINIMUM_BALANCE_USD = 1000  # Don't trade below $1k balance

   # Cash reserve
   CASH_PERCENTAGE = 0.50  # Keep 50% in cash (conservative)
   ```

3. **Set Conservative Trading Frequency**:
   ```python
   SLEEP_BETWEEN_RUNS_MINUTES = 60  # Check every hour (not every 15 min)
   ```

4. **Enable AI Confirmation**:
   ```python
   # In risk_agent.py or trading_agent.py
   USE_AI_CONFIRMATION = True  # Require AI approval for exits
   ```

**✅ Completion Criteria**:
- [ ] Position limits set to 10% of normal size
- [ ] Circuit breakers configured
- [ ] Trading frequency reduced (60+ minutes)
- [ ] AI confirmation enabled
- [ ] Changes committed to git

---

### ✅ 1.3 API Key Validation

**Location**: `.env` file

**Steps**:

1. **Verify All Required Keys**:
   ```bash
   # Check .env file has all required keys
   grep -E "BIRDEYE_API_KEY|MOONDEV_API_KEY|ANTHROPIC_KEY|OPENAI_KEY" .env
   ```

2. **Test API Connectivity**:
   ```bash
   # Test BirdEye API
   python -c "
   from src.nice_funcs import token_price
   price = token_price('So11111111111111111111111111111111111111112')  # SOL
   print(f'SOL Price: ${price}')
   "

   # Test AI API
   python -c "
   from src.models.model_factory import ModelFactory
   model = ModelFactory.create_model('anthropic')
   response = model.generate_response('You are a helpful assistant', 'Say hello', 0.7, 100)
   print(f'AI Response: {response}')
   "
   ```

3. **Verify Rate Limits**:
   - BirdEye: Check your plan limits (requests/day)
   - AI APIs: Check token limits and costs
   - Moon Dev API: Verify access to premium endpoints

4. **Setup Demo Account Keys** (if available):
   ```bash
   # For HyperLiquid testnet
   HYPER_LIQUID_ETH_PRIVATE_KEY="0x..."  # Testnet key
   HYPER_LIQUID_USE_TESTNET=true

   # For MetaTrader 5 demo
   MT5_DEMO_ACCOUNT=true
   ```

**✅ Completion Criteria**:
- [ ] All required API keys present in .env
- [ ] API connectivity tested successfully
- [ ] Rate limits verified
- [ ] Demo/testnet keys configured (if available)

---

### ✅ 1.4 Local System Testing

**Steps**:

1. **Test Cache Performance**:
   ```bash
   # Run main.py for 5 minutes
   timeout 300 python src/main.py

   # Check cache stats (should see in console output)
   # Expected: 50-90% cache hit rate
   ```

2. **Test Prometheus Metrics**:
   ```bash
   # Start main.py in background
   python src/main.py &

   # Wait 30 seconds for startup
   sleep 30

   # Check metrics endpoint
   curl http://localhost:8000/metrics | head -20

   # Should see: trading_*, agent_*, api_*, system_* metrics

   # Kill background process
   pkill -f "python src/main.py"
   ```

3. **Test Regime Detection**:
   ```bash
   # Run trading agent once
   python -c "
   from src.agents.trading_agent import TradingAgent
   from src.config import MONITORED_TOKENS

   agent = TradingAgent()
   # Test on one token
   agent.run()
   "

   # Check console for regime detection output:
   # Should see: "📊 Market Regime Analysis for XXX..."
   ```

4. **Validate All Utilities Work**:
   ```bash
   # Run integration tests
   pytest tests/test_utils_integration.py -v

   # Expected: 28/28 tests PASSED
   ```

5. **Check Error Handling**:
   ```bash
   # Temporarily break API key in .env
   # Run main.py and verify graceful error handling
   # Restore API key
   ```

**✅ Completion Criteria**:
- [ ] Cache hit rate > 50%
- [ ] Prometheus metrics accessible
- [ ] Regime detection working
- [ ] All 28 integration tests passing
- [ ] Error handling graceful (no crashes)

---

## 📋 Phase 2: VPS Deployment (Days 4-7)

### ✅ 2.1 VPS Setup

**Recommended VPS Specs**:
- **CPU**: 2+ cores
- **RAM**: 4GB+ (8GB recommended)
- **Storage**: 20GB+ SSD
- **OS**: Ubuntu 22.04 LTS
- **Provider**: DigitalOcean ($24/month), Vultr ($18/month), Linode ($24/month)

**Steps**:

1. **Create VPS Instance**:
   - Choose Ubuntu 22.04 LTS
   - Enable SSH key authentication
   - Configure firewall (allow ports 22, 8000, 8001)

2. **Initial Server Setup**:
   ```bash
   # SSH into VPS
   ssh root@your-vps-ip

   # Update system
   apt update && apt upgrade -y

   # Install Python 3.11+
   apt install -y python3.11 python3.11-venv python3-pip git

   # Install system dependencies
   apt install -y build-essential libssl-dev libffi-dev python3-dev
   ```

3. **Clone Repository**:
   ```bash
   # Clone your fork
   cd /opt
   git clone https://github.com/YOUR-USERNAME/moon-dev-ai-agents.git
   cd moon-dev-ai-agents

   # Checkout your production branch
   git checkout claude/claude-md-mie887ck8uy5o75d-01CWBFiRvGoXnksGEazRyma7
   ```

4. **Setup Python Environment**:
   ```bash
   # Create virtual environment
   python3.11 -m venv venv
   source venv/bin/activate

   # Install dependencies
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. **Configure Environment Variables**:
   ```bash
   # Copy .env_example to .env
   cp .env_example .env

   # Edit .env with your API keys
   nano .env

   # ⚠️ IMPORTANT: Use DEMO/TESTNET keys for Phase 2
   # Set HYPER_LIQUID_USE_TESTNET=true
   # Use small position sizes for testing
   ```

6. **Test Installation**:
   ```bash
   # Quick test
   python src/main.py

   # Press Ctrl+C after 1-2 minutes
   # Verify: No errors, metrics server started, cache working
   ```

**✅ Completion Criteria**:
- [ ] VPS created and accessible via SSH
- [ ] Repository cloned and dependencies installed
- [ ] .env configured with demo/testnet keys
- [ ] Test run successful (no errors)

---

### ✅ 2.2 Systemd Service Setup

**Steps**:

1. **Create Service File**:
   ```bash
   sudo nano /etc/systemd/system/moondev-trading.service
   ```

2. **Add Service Configuration**:
   ```ini
   [Unit]
   Description=Moon Dev AI Trading System
   After=network.target

   [Service]
   Type=simple
   User=root
   WorkingDirectory=/opt/moon-dev-ai-agents
   Environment="PATH=/opt/moon-dev-ai-agents/venv/bin"
   ExecStart=/opt/moon-dev-ai-agents/venv/bin/python src/main.py
   Restart=always
   RestartSec=10
   StandardOutput=append:/var/log/moondev-trading/output.log
   StandardError=append:/var/log/moondev-trading/error.log

   [Install]
   WantedBy=multi-user.target
   ```

3. **Create Log Directory**:
   ```bash
   sudo mkdir -p /var/log/moondev-trading
   sudo chmod 755 /var/log/moondev-trading
   ```

4. **Enable and Start Service**:
   ```bash
   # Reload systemd
   sudo systemctl daemon-reload

   # Enable service (start on boot)
   sudo systemctl enable moondev-trading

   # Start service
   sudo systemctl start moondev-trading

   # Check status
   sudo systemctl status moondev-trading
   ```

5. **Monitor Logs**:
   ```bash
   # Real-time logs
   sudo journalctl -u moondev-trading -f

   # Or tail log files
   tail -f /var/log/moondev-trading/output.log
   ```

**✅ Completion Criteria**:
- [ ] Systemd service created
- [ ] Service starts without errors
- [ ] Service restarts automatically after crash
- [ ] Logs accessible and readable

---

### ✅ 2.3 Monitoring Setup

**Steps**:

1. **Verify Prometheus Metrics**:
   ```bash
   # Check metrics endpoint
   curl http://localhost:8000/metrics

   # Should see trading metrics, agent metrics, API metrics
   ```

2. **Setup Prometheus (Optional but Recommended)**:
   ```bash
   # Install Prometheus
   wget https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz
   tar xvfz prometheus-*.tar.gz
   cd prometheus-*

   # Create config
   cat > prometheus.yml << EOF
   global:
     scrape_interval: 15s

   scrape_configs:
     - job_name: 'moondev-trading'
       static_configs:
         - targets: ['localhost:8000']
   EOF

   # Run Prometheus
   ./prometheus --config.file=prometheus.yml &

   # Access at http://your-vps-ip:9090
   ```

3. **Setup Grafana (Optional)**:
   ```bash
   # Install Grafana
   sudo apt-get install -y software-properties-common
   sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
   wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
   sudo apt-get update
   sudo apt-get install grafana

   # Start Grafana
   sudo systemctl start grafana-server
   sudo systemctl enable grafana-server

   # Access at http://your-vps-ip:3000
   # Default login: admin/admin
   ```

4. **Create Alert Rules** (if using Prometheus):
   ```yaml
   # Create alert rules file
   cat > /opt/prometheus/alerts.yml << EOF
   groups:
     - name: trading_alerts
       interval: 1m
       rules:
         - alert: HighErrorRate
           expr: rate(system_errors_total[5m]) > 0.1
           annotations:
             summary: "High error rate detected"

         - alert: DailyLossLimit
           expr: trading_daily_pnl_usd < -200
           annotations:
             summary: "Daily loss limit exceeded"
   EOF
   ```

5. **Setup Health Check Endpoint** (optional):
   ```bash
   # Add to crontab for external monitoring
   crontab -e

   # Add line:
   # */5 * * * * curl -f http://localhost:8000/metrics || echo "Trading system down" | mail -s "Alert" your@email.com
   ```

**✅ Completion Criteria**:
- [ ] Prometheus metrics accessible
- [ ] Prometheus server running (optional)
- [ ] Grafana dashboard created (optional)
- [ ] Alert rules configured (optional)
- [ ] Health check endpoint monitored

---

### ✅ 2.4 Demo Account Testing (24-48 Hours)

**CRITICAL**: Run with demo/testnet accounts for at least 24-48 hours

**Steps**:

1. **Verify Demo Configuration**:
   ```bash
   # Check .env has testnet settings
   grep -i testnet .env

   # Should see: HYPER_LIQUID_USE_TESTNET=true
   ```

2. **Monitor Key Metrics** (24-48 hours):

   **Every 4 Hours, Check**:
   - System uptime: `sudo systemctl status moondev-trading`
   - Error rate: `grep ERROR /var/log/moondev-trading/output.log | wc -l`
   - Cache hit rate: Look for cache stats in logs
   - Regime detection: Verify regime changes detected
   - Position sizing: Check Kelly fractions calculated

   **Create Monitoring Checklist**:
   ```bash
   # Create monitoring script
   cat > /opt/moon-dev-ai-agents/monitor_demo.sh << 'EOF'
   #!/bin/bash

   echo "=== Moon Dev Trading System Health Check ==="
   echo "Time: $(date)"
   echo ""

   echo "1. Service Status:"
   systemctl is-active moondev-trading
   echo ""

   echo "2. Uptime:"
   systemctl show moondev-trading --property=ActiveEnterTimestamp
   echo ""

   echo "3. Recent Errors:"
   grep ERROR /var/log/moondev-trading/output.log | tail -5
   echo ""

   echo "4. Metrics Available:"
   curl -s http://localhost:8000/metrics | grep -c "^trading_"
   echo ""

   echo "5. Cache Performance:"
   grep "Cache Hit Rate" /var/log/moondev-trading/output.log | tail -1
   echo ""

   echo "6. Latest Activity:"
   tail -20 /var/log/moondev-trading/output.log
   EOF

   chmod +x /opt/moon-dev-ai-agents/monitor_demo.sh

   # Run every 4 hours
   crontab -e
   # Add: 0 */4 * * * /opt/moon-dev-ai-agents/monitor_demo.sh >> /var/log/moondev-trading/health_check.log
   ```

3. **Record Observations**:

   Create tracking spreadsheet with columns:
   - Timestamp
   - Uptime (hours)
   - Error count
   - Cache hit rate
   - Trades executed (if any)
   - Regime changes detected
   - Notes/Issues

4. **Test Emergency Shutdown**:
   ```bash
   # Test graceful shutdown
   sudo systemctl stop moondev-trading

   # Verify no orphan processes
   ps aux | grep python

   # Restart
   sudo systemctl start moondev-trading
   ```

5. **Test Recovery from Crash**:
   ```bash
   # Simulate crash
   sudo kill -9 $(pgrep -f "python src/main.py")

   # Wait 30 seconds
   sleep 30

   # Verify auto-restart
   sudo systemctl status moondev-trading
   # Should show: active (running)
   ```

**✅ Completion Criteria**:
- [ ] System running continuously for 24-48 hours
- [ ] Zero critical errors
- [ ] Cache hit rate > 70%
- [ ] Regime detection working consistently
- [ ] Auto-restart working after crash
- [ ] All monitoring scripts functional
- [ ] Health check log shows consistent uptime

---

## 📋 Phase 3: Gradual Live Rollout (Weeks 2-4)

### ✅ 3.1 Phase 3A: Micro Positions (Week 2)

**Goal**: Test with real money at 10% of normal size

**Steps**:

1. **Update Configuration**:
   ```python
   # src/config.py

   # Start with MICRO positions
   usd_size = 50                    # $50 per trade (10% of normal)
   max_usd_order_size = 250         # Max $250 total exposure
   MAX_POSITION_PERCENTAGE = 0.05   # 5% of portfolio max

   # Keep conservative settings
   MAX_LOSS_USD = 100               # Stop at $100 daily loss
   CASH_PERCENTAGE = 0.60           # Keep 60% in cash
   SLEEP_BETWEEN_RUNS_MINUTES = 60  # Check hourly
   ```

2. **Switch to Live API Keys**:
   ```bash
   # On VPS, edit .env
   nano /opt/moon-dev-ai-agents/.env

   # ⚠️ REMOVE testnet settings
   # HYPER_LIQUID_USE_TESTNET=false  # or comment out

   # ⚠️ ADD live keys (with small balances!)
   SOLANA_PRIVATE_KEY="your-live-key-here"
   HYPER_LIQUID_ETH_PRIVATE_KEY="your-live-key-here"
   ```

3. **Fund Accounts with Small Amounts**:
   - **Recommended**: $1,000-2,000 total
   - Spread across platforms (Solana, HyperLiquid)
   - Use separate trading wallets (NOT your main wallet)

4. **Restart Service**:
   ```bash
   sudo systemctl restart moondev-trading

   # Monitor closely for first hour
   sudo journalctl -u moondev-trading -f
   ```

5. **Monitor Daily** (7 days):

   **Daily Checklist**:
   - [ ] Check PnL: `grep "PnL" /var/log/moondev-trading/output.log`
   - [ ] Verify position sizes: Should be ~$50 per trade
   - [ ] Check for errors: `grep ERROR /var/log/moondev-trading/output.log`
   - [ ] Verify Kelly fractions: Should be 5-15%
   - [ ] Review regime detection: Are regime changes reasonable?
   - [ ] Check cache performance: Should be >80% hit rate by now

   **Create Daily Report**:
   ```bash
   cat > /opt/moon-dev-ai-agents/daily_report.sh << 'EOF'
   #!/bin/bash

   echo "=== Daily Trading Report - $(date +%Y-%m-%d) ==="

   echo -e "\n📊 PnL Summary:"
   grep "Total PnL" /var/log/moondev-trading/output.log | tail -5

   echo -e "\n💰 Positions:"
   grep "Position size" /var/log/moondev-trading/output.log | tail -10

   echo -e "\n📈 Regime Detection:"
   grep "Market Regime" /var/log/moondev-trading/output.log | tail -5

   echo -e "\n⚠️ Errors:"
   grep ERROR /var/log/moondev-trading/output.log | wc -l

   echo -e "\n🎯 Cache Performance:"
   grep "Cache Hit Rate" /var/log/moondev-trading/output.log | tail -1
   EOF

   chmod +x /opt/moon-dev-ai-agents/daily_report.sh

   # Run daily at 8 AM
   crontab -e
   # Add: 0 8 * * * /opt/moon-dev-ai-agents/daily_report.sh | mail -s "Trading Report" your@email.com
   ```

**✅ Week 2 Success Criteria**:
- [ ] Net PnL >= 0 (break even or profit)
- [ ] No position exceeded $50
- [ ] Zero critical errors
- [ ] All circuit breakers working (test by simulating loss)
- [ ] Kelly sizing calculations working correctly
- [ ] Regime detection adapting strategies appropriately

**❌ Week 2 Failure Criteria** (STOP and debug if ANY occur):
- Net PnL < -$200 (more than 2x daily loss limit)
- Any position > $100 (sizing bug)
- More than 5 errors per day
- Cache hit rate < 50% (performance issue)
- Consistent regime detection failures

---

### ✅ 3.2 Phase 3B: Small Positions (Week 3)

**Goal**: Increase to 30% of normal size IF Week 2 successful

**Prerequisites**:
- Week 2 net positive or break even
- Zero critical bugs found
- Monitoring working perfectly

**Steps**:

1. **Increase Position Sizes**:
   ```python
   # src/config.py

   usd_size = 150                   # $150 per trade (30% of normal)
   max_usd_order_size = 750         # Max $750 total exposure
   MAX_POSITION_PERCENTAGE = 0.10   # 10% of portfolio max

   # Slightly relax limits
   MAX_LOSS_USD = 300               # $300 daily loss limit
   CASH_PERCENTAGE = 0.50           # 50% cash reserve
   SLEEP_BETWEEN_RUNS_MINUTES = 30  # Check every 30 minutes
   ```

2. **Add More Capital** (if needed):
   - Increase to $3,000-5,000 total
   - Maintain risk management (never risk more than 2% per trade)

3. **Update and Deploy**:
   ```bash
   # Commit config changes
   git add src/config.py
   git commit -m "🚀 Phase 3B: Increase to 30% position sizes"
   git push

   # On VPS, pull changes
   cd /opt/moon-dev-ai-agents
   git pull

   # Restart service
   sudo systemctl restart moondev-trading
   ```

4. **Enhanced Monitoring** (daily):
   - Check Prometheus dashboard (if setup)
   - Review all trades manually
   - Verify Kelly sizing still appropriate
   - Monitor API costs (should be lower due to caching)
   - Check regime transitions make sense

5. **Weekly Review**:
   - Calculate Sharpe ratio: `(avg_return - risk_free_rate) / std_dev`
   - Calculate max drawdown
   - Review win rate vs. backtests
   - Adjust Kelly stats if needed

**✅ Week 3 Success Criteria**:
- [ ] Net PnL > 0 (profitable)
- [ ] Win rate within 10% of backtest expectations
- [ ] No position exceeded $150
- [ ] Sharpe ratio > 0.5
- [ ] Max drawdown < 15%

**❌ Week 3 Failure Criteria** (REDUCE size if ANY occur):
- Net PnL < -$500
- Win rate 20%+ below backtest expectations
- Sharpe ratio < 0
- Max drawdown > 25%

---

### ✅ 3.3 Phase 3C: Normal Positions (Week 4)

**Goal**: Reach target position sizes IF Week 3 successful

**Prerequisites**:
- Week 3 profitable
- Sharpe ratio > 0.5
- Max drawdown < 15%

**Steps**:

1. **Final Position Size Configuration**:
   ```python
   # src/config.py

   usd_size = 500                   # $500 per trade (normal size)
   max_usd_order_size = 2500        # Max $2,500 total exposure
   MAX_POSITION_PERCENTAGE = 0.15   # 15% of portfolio max

   # Standard risk limits
   MAX_LOSS_USD = 1000              # $1,000 daily loss limit
   CASH_PERCENTAGE = 0.40           # 40% cash reserve
   SLEEP_BETWEEN_RUNS_MINUTES = 15  # Check every 15 minutes
   ```

2. **Capital Requirements**:
   - Minimum $10,000 total capital
   - Recommended $20,000-50,000 for proper diversification

3. **Deploy Final Configuration**:
   ```bash
   git add src/config.py
   git commit -m "🚀 Phase 3C: Full production position sizes"
   git push

   # On VPS
   cd /opt/moon-dev-ai-agents
   git pull
   sudo systemctl restart moondev-trading
   ```

4. **Production Monitoring**:

   **Daily**:
   - Review all trades
   - Check PnL
   - Verify regime detection
   - Monitor API costs

   **Weekly**:
   - Calculate performance metrics (Sharpe, drawdown, win rate)
   - Review strategy performance individually
   - Optimize Kelly stats based on live results
   - Adjust position sizing if needed

   **Monthly**:
   - Full portfolio review
   - Strategy optimization
   - Cost analysis (API, AI, infrastructure)
   - Risk management review

5. **Optimization Loop**:
   ```bash
   # Every 2 weeks, update Kelly stats based on live results
   # Extract from Prometheus metrics or logs
   # Update KELLY_STATS in trading_agent.py
   # Backtest any new strategies before deploying
   ```

**✅ Week 4 Success Criteria**:
- [ ] Consistent profitability (>60% win rate)
- [ ] Sharpe ratio > 1.0
- [ ] Max drawdown < 20%
- [ ] All monitoring systems working
- [ ] API costs < 5% of profits

---

## 📋 Phase 4: Ongoing Operations

### ✅ 4.1 Regular Maintenance

**Daily Tasks** (5 minutes):
- [ ] Check system uptime
- [ ] Review overnight trades
- [ ] Verify no errors
- [ ] Check Prometheus metrics

**Weekly Tasks** (30 minutes):
- [ ] Review performance metrics
- [ ] Update Kelly stats if needed
- [ ] Check for system updates
- [ ] Review API costs
- [ ] Backup configuration and data

**Monthly Tasks** (2 hours):
- [ ] Full portfolio review
- [ ] Strategy optimization
- [ ] Update dependencies (`pip install -U -r requirements.txt`)
- [ ] Security audit (API keys, access logs)
- [ ] Cost-benefit analysis

---

### ✅ 4.2 Emergency Procedures

**Emergency Shutdown**:
```bash
# SSH into VPS
ssh root@your-vps-ip

# Stop trading immediately
sudo systemctl stop moondev-trading

# Verify stopped
sudo systemctl status moondev-trading

# Check current positions
# (manually close if needed)
```

**Emergency Contacts**:
- Exchange support numbers
- API provider support
- VPS provider support

**Emergency Scenarios**:

1. **Flash Crash**:
   - Stop service immediately
   - Manually close all positions
   - Review what happened
   - Adjust stop losses before restarting

2. **API Issues**:
   - Check API status pages
   - Switch to backup API if available
   - Reduce trading frequency
   - Contact API support

3. **System Compromise**:
   - Stop service immediately
   - Rotate all API keys
   - Review access logs
   - Restore from backup
   - Audit security

4. **Unexpected Losses**:
   - Stop service
   - Review all trades
   - Check if circuit breakers failed
   - Verify Kelly stats are correct
   - Reduce position sizes
   - Restart cautiously

---

### ✅ 4.3 Optimization Opportunities

**After 30 Days Live**:

1. **Strategy Performance Analysis**:
   - Which strategies are most profitable?
   - Which regimes perform best?
   - Which tokens have best results?
   - Disable underperforming strategies

2. **Kelly Stats Refinement**:
   - Update with live performance data
   - Separate stats by market regime
   - Adjust for changing market conditions

3. **Cost Optimization**:
   - Review API usage patterns
   - Increase cache TTLs if appropriate
   - Consider API plan upgrades/downgrades
   - Optimize AI model selection (cheaper models for simple tasks)

4. **Scaling**:
   - Add more strategies (via RBI agent)
   - Expand to more tokens
   - Increase position sizes (if consistently profitable)
   - Add more exchanges

---

## 🎯 Final Checklist Before Going Live

**Phase 1: Pre-Deployment** ✅
- [ ] Kelly stats updated with real backtest data
- [ ] Risk management configured conservatively
- [ ] All API keys validated
- [ ] Local testing successful (28/28 tests passing)

**Phase 2: VPS Deployment** ✅
- [ ] VPS setup and configured
- [ ] Systemd service running
- [ ] Monitoring configured
- [ ] 24-48 hour demo run successful

**Phase 3: Gradual Rollout** ✅
- [ ] Week 2: Micro positions profitable or break-even
- [ ] Week 3: Small positions with Sharpe > 0.5
- [ ] Week 4: Normal positions with consistent results

**Phase 4: Ongoing** ✅
- [ ] Daily monitoring routine established
- [ ] Emergency procedures documented
- [ ] Optimization schedule created

---

## ⚠️ Final Warnings

**NEVER**:
- ❌ Skip the gradual rollout phases
- ❌ Use production keys without testing on demo first
- ❌ Increase position sizes after losses (revenge trading)
- ❌ Disable risk management features
- ❌ Trade with money you can't afford to lose
- ❌ Ignore circuit breakers or error alerts
- ❌ Run without monitoring for more than 24 hours

**ALWAYS**:
- ✅ Monitor daily (at minimum)
- ✅ Keep detailed records of all changes
- ✅ Test new strategies on demo first
- ✅ Maintain cash reserves
- ✅ Have emergency shutdown procedures ready
- ✅ Keep API keys secure
- ✅ Review performance weekly

---

## 📞 Support Resources

**Documentation**:
- `README.md` - Project overview
- `CLAUDE.md` - Development guide
- `PRODUCTION_DEPLOY.md` - Deployment guide
- `docs/` - Agent-specific documentation

**Community**:
- Discord: https://discord.gg/8UPuVZ53bh
- YouTube: @moondevonyt
- GitHub Issues: Report bugs and requests

**Emergency**:
- Exchange support (for trading issues)
- VPS provider support (for infrastructure issues)
- Community Discord (for strategy/configuration help)

---

**Last Updated**: 2025-12-17

**Version**: 1.0

**Status**: Production-Ready ✅

---

*Good luck, trade safe, and may the moon be with you! 🌙*

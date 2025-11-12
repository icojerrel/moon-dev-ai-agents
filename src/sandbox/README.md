# 🧪 Sandbox Environment - AI Agent Memory Testing

Accelerate memory learning by simulating weeks of trading in minutes.

## 🎯 Purpose

The Sandbox Environment allows you to:
- **Rapidly populate memory databases** with realistic trading data
- **Test cross-agent intelligence** with shared memory pools
- **Verify memory system** works correctly before production
- **Compress learning curve** from weeks to hours

## 🚀 Quick Start

### Basic Usage

```bash
# Quick test (1 day, ~10 seconds)
python src/sandbox/run_sandbox.py --scenario quick

# Week simulation (7 days, ~1 minute)
python src/sandbox/run_sandbox.py --scenario week

# Full month (30 days, ~5 minutes)
python src/sandbox/run_sandbox.py --scenario month

# Run all scenarios
python src/sandbox/run_sandbox.py --all
```

### Python API

```python
from src.sandbox import create_sandbox

# Create sandbox with mock agents
sandbox = create_sandbox()

# Run simulation
metrics = sandbox.run_simulation(days=7, verbose=True)

# Check results
print(f"Total decisions: {metrics.total_decisions}")
print(f"BUY: {metrics.buy_decisions}")
print(f"SELL: {metrics.sell_decisions}")

# Check memory growth
stats = sandbox.get_memory_stats()
for db_name, info in stats.items():
    print(f"{db_name}: {info['total_memories']} memories")
```

## 📊 Available Scenarios

### 1. Quick Test
```bash
python src/sandbox/run_sandbox.py --scenario quick
```
- **Duration**: ~10 seconds
- **Data**: 1 day (96 candles)
- **Purpose**: Verify setup, fast feedback
- **Agents**: Trading, Sentiment, Whale

### 2. Week Simulation
```bash
python src/sandbox/run_sandbox.py --scenario week
```
- **Duration**: ~1 minute
- **Data**: 7 days (672 candles)
- **Purpose**: Build meaningful memory dataset
- **Agents**: Trading, Sentiment, Whale, Funding, Risk

### 3. Month Simulation
```bash
python src/sandbox/run_sandbox.py --scenario month
```
- **Duration**: ~3-5 minutes
- **Data**: 30 days (2,880 candles)
- **Purpose**: Full memory population
- **Agents**: All 7 major agents

### 4. Stress Test
```bash
python src/sandbox/run_sandbox.py --scenario stress
```
- **Duration**: ~10 minutes
- **Data**: Maximum available
- **Purpose**: Test performance limits
- **Agents**: All 10 agents

### 5. Cross-Agent Intelligence Test
```bash
python src/sandbox/run_sandbox.py --scenario cross-agent
```
- **Duration**: ~2 minutes
- **Purpose**: Verify shared memory pool coordination
- **Tests**: Market analysis agents → Trading agent

## 🎓 What Gets Tested

### Memory Population
```
Before Sandbox:
- trading_agent.db: 0 memories
- market_analysis_shared.db: 0 memories
- Total: 0 memories

After Week Simulation:
- trading_agent.db: ~1,000 memories
- market_analysis_shared.db: ~3,000 memories (3 agents)
- Total: ~5,000 memories

After Month Simulation:
- trading_agent.db: ~4,000 memories
- market_analysis_shared.db: ~12,000 memories
- Total: ~20,000+ memories
```

### Cross-Agent Intelligence

**Shared Pool Test**:
1. Sentiment agent analyzes 7 days → stores in shared pool
2. Whale agent detects movements → stores in shared pool
3. Funding agent tracks rates → stores in shared pool
4. Trading agent queries pool → gets coordinated signals!

**Verification**:
```bash
# After cross-agent test
python src/agents/memory_cli.py stats market_analysis_shared

# Should show memories from all 3 agents
# Verify cross-agent context available
```

### Learning Curve

**Metrics Tracked**:
- Total decisions made
- BUY/SELL/HOLD distribution
- Decision confidence over time
- Memory query performance
- Cross-agent coordination

**Expected Results**:
```
Week 1: Random decisions (no memory context)
Week 2: Starting to reference past (basic memory)
Week 3: Coordinated signals (shared pool working)
Week 4: Informed decisions (full memory context)
```

## 📁 Output Files

### Results Export
```
src/data/sandbox/
├── week_simulation_results.json       # Week scenario results
├── month_simulation_results.json      # Month scenario results
└── sandbox_report_YYYYMMDD_HHMMSS.json  # Comprehensive report
```

### Report Format
```json
{
  "timestamp": "2025-11-12T10:00:00",
  "scenarios_run": ["quick", "week", "month"],
  "results": {
    "quick": {
      "total_decisions": 288,
      "buy_decisions": 95,
      "sell_decisions": 87,
      "hold_decisions": 106,
      "duration_seconds": 8.5
    }
  },
  "memory_stats": {
    "trading_agent": {
      "total_memories": 1000,
      "size_mb": 0.5
    }
  }
}
```

## 🔧 Advanced Usage

### Custom Agents

```python
from src.sandbox import SandboxEnvironment

# Use real agents instead of mocks
from src.agents.trading_agent import TradingAgent
from src.agents.sentiment_agent import SentimentAgent

agents = [
    TradingAgent(),
    SentimentAgent()
]

sandbox = SandboxEnvironment(agents=agents)
metrics = sandbox.run_simulation(days=7)
```

### Custom Data

```python
# Use different historical data
sandbox = SandboxEnvironment(
    historical_data_path="path/to/your/data.csv"
)
```

### Speed Multiplier

```python
# Run simulation faster (skip delays)
sandbox = SandboxEnvironment(speed_multiplier=10)
```

## 📊 Monitoring Progress

### During Simulation

```bash
# Watch memory databases grow in real-time
watch -n 5 'python src/agents/memory_cli.py summary'
```

### After Simulation

```bash
# View memory statistics
python src/agents/memory_cli.py summary

# Check specific agent
python src/agents/memory_cli.py stats trading_agent

# Query memories
python src/agents/memory_cli.py query trading_agent BTC
```

## ✅ Verification Checklist

After running sandbox scenarios:

- [ ] Memory databases created (5-8 databases)
- [ ] Databases populated with memories (>1000 per agent)
- [ ] Shared pools contain cross-agent data
- [ ] Analytics tools can query memories
- [ ] No errors in simulation logs
- [ ] Performance acceptable (<10 min for month)

## 🎯 Expected Results

### Performance Benchmarks

| Scenario | Candles | Agents | Decisions | Duration |
|----------|---------|--------|-----------|----------|
| Quick | 96 | 3 | 288 | ~10 sec |
| Week | 672 | 5 | 3,360 | ~1 min |
| Month | 2,880 | 7 | 20,160 | ~5 min |
| Stress | 10,000+ | 10 | 100,000+ | ~10 min |

### Memory Growth

| Scenario | Total Memories | Database Size | Growth Rate |
|----------|----------------|---------------|-------------|
| Quick | ~300 | 0.2 MB | 30/sec |
| Week | ~3,000 | 1.5 MB | 50/sec |
| Month | ~20,000 | 10 MB | 70/sec |

## 🐛 Troubleshooting

### "No historical data found"

```bash
# Ensure BTC-USD-15m.csv exists
ls src/data/rbi/BTC-USD-15m.csv

# Or specify custom path
python src/sandbox/run_sandbox.py --scenario quick --data path/to/data.csv
```

### "MemoriSDK not installed"

```bash
# Install MemoriSDK
pip install memorisdk

# Verify installation
python -c "from memori import Memori; print('OK')"
```

### Slow performance

```python
# Reduce verbosity
metrics = sandbox.run_simulation(days=7, verbose=False)

# Use fewer agents
agents = [MockAgent("TradingAgent")]  # Only 1 agent

# Or reduce data
metrics = sandbox.run_simulation(num_candles=100)
```

## 💡 Pro Tips

1. **Start Small**: Run `quick` first to verify setup
2. **Monitor Memory**: Use `memory_cli.py` during simulation
3. **Export Results**: Always export for later analysis
4. **Test Cross-Agent**: Run `cross-agent` to verify shared pools
5. **Regular Cleanup**: Optimize databases after big simulations

```bash
# After big simulation
python src/agents/memory_cli.py optimize trading_agent
```

## 🔮 Future Enhancements

Planned features:
- [ ] Real agent integration (not just mocks)
- [ ] Multiple market scenarios (bull, bear, crash)
- [ ] Performance profiling
- [ ] Memory compression strategies
- [ ] Parallel scenario execution
- [ ] Web-based visualization
- [ ] A/B testing framework

## 📚 Related Documentation

- [MemoriSDK Integration Guide](../../MEMORISDK_COMPLETE_IMPLEMENTATION.md)
- [Memory Analytics](../agents/memory_analytics.py)
- [Memory CLI](../agents/memory_cli.py)
- [Test Results](../../MEMORISDK_TEST_RESULTS.md)

---

**Status**: ✅ Production Ready

**Version**: 1.0.0

**Last Updated**: 2025-11-12

# MemoriSDK Integration Plan for Moon Dev AI Agents

## Executive Summary

**Recommendation: YES - High value for merge**

MemoriSDK offers significant advantages over current JSON-based memory with minimal integration effort. Cost-effective, scales better, and enables cross-session learning for 48+ agent ecosystem.

## Current State Analysis

### Existing Memory System
- **Location**: `src/data/rbi/memory/agents/`, per-agent JSON files
- **Pattern**: Manual load/save in agents (coingecko_agent.py:302, listingarb_agent.py:242)
- **Structure**: Simple dictionaries (`conversations`, `decisions`, `portfolio_history`)
- **Limitations**:
  - No semantic search
  - No cross-agent learning
  - Manual memory injection
  - Poor scalability for large histories

### MemoriSDK Advantages
- **Cost**: 80-90% cheaper than vector DBs
- **Intelligence**: Automatic entity extraction & categorization
- **Compatibility**: Works with existing Anthropic/OpenAI code
- **Scalability**: SQL-based (SQLite → PostgreSQL path)
- **Cross-session**: Agents improve over time
- **Transparent**: Single `memori.enable()` call

## Integration Strategy

### Phase 1: Pilot (Week 1) - 3 Agents

**Target Agents**: chat_agent, trading_agent, risk_agent

**Installation**:
```bash
conda activate tflow
pip install memorisdk
pip freeze > requirements.txt
```

**Code Changes** (minimal):

```python
# src/agents/chat_agent.py
from memorisdk import Memori

class ChatAgent:
    def __init__(self):
        # Add memory
        self.memori = Memori(
            mode='auto',  # Dynamic search per query
            db_path='./src/data/memory/chat_agent.db'
        )
        self.memori.enable()

        # Existing code remains unchanged
        self.model = ModelFactory.create_model('anthropic')
        # ...
```

**Testing Criteria**:
- [ ] Memory persists across restarts
- [ ] Context relevance improves over 10+ conversations
- [ ] Response quality comparison (with/without memory)
- [ ] Performance overhead < 200ms per query

### Phase 2: Expansion (Week 2-3) - 10 Agents

**Target Agents**:
- Market analysis: sentiment_agent, whale_agent, funding_agent
- Strategy: strategy_agent, rbi_agent
- Content: tweet_agent, video_agent
- Specialized: copybot_agent, sniper_agent

**Shared Memory Patterns**:

```python
# Option A: Per-agent isolation
memori = Memori(db_path=f'./src/data/memory/{agent_name}.db')

# Option B: Shared memory for related agents (recommended)
# All market analysis agents share knowledge
memori = Memori(db_path='./src/data/memory/market_analysis_shared.db')
```

**A/B Testing**:
- Run agents with/without memory in parallel
- Compare decision quality over 7 days
- Measure PnL attribution (if trading)

### Phase 3: Production Scale (Week 4+)

**Database Migration**:
```python
# Development: SQLite
memori = Memori(db_type='sqlite', db_path='./memory.db')

# Production: PostgreSQL
memori = Memori(
    db_type='postgresql',
    db_config={
        'host': 'localhost',
        'port': 5432,
        'database': 'moon_agents_memory',
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD')
    }
)
```

**Advanced Features**:
1. **Cross-Agent Queries**:
   ```python
   # Risk agent queries trading agent's past decisions
   risk_agent.memori.search("high volatility trades that lost money")
   ```

2. **Memory Analytics Dashboard**:
   - SQL queries on memory.db for insights
   - "Most referenced tokens in last 30 days"
   - "Agent consensus patterns"

3. **Memory Management**:
   ```python
   # Background cleanup every 6 hours (built-in)
   # Manual cleanup for old sessions
   memori.cleanup_before(date='2025-01-01')
   ```

## Use Case Examples

### 1. Multi-Agent Coordination
**Current Problem**: Agents make independent decisions without shared learning

**With MemoriSDK**:
```python
# Trading agent learns from risk agent warnings
trading_agent.memori.enable()  # Auto-retrieves: "risk_agent flagged high volatility 2 hours ago"

# RBI agent learns from past backtest results
rbi_agent.memori.search("successful mean reversion strategies on BTC")
```

### 2. Market Pattern Recognition
**Current Problem**: No memory of past market conditions

**With MemoriSDK**:
```python
# Whale agent recognizes similar patterns
whale_agent.query("large wallet movements before 20% pumps")
# Auto-retrieves: "Similar pattern on 2025-01-15 led to SOL rally"
```

### 3. Strategy Evolution
**Current Problem**: RBI agent doesn't learn from past backtests

**With MemoriSDK**:
- Backtest results automatically stored with context
- Next strategy generation considers: "RSI divergence strategies performed poorly in low volume conditions"
- Semantic search: "Find backtests with Sharpe > 2.0 on 15m timeframes"

## Implementation Guidelines

### File Structure
```
src/
├── data/
│   └── memory/
│       ├── chat_agent.db          # Per-agent SQLite
│       ├── trading_agent.db
│       ├── market_analysis.db     # Shared across sentiment/whale/funding
│       └── strategy_development.db # Shared across rbi/research/strategy
└── agents/
    └── memory_config.py           # Centralized memory configuration
```

### Configuration (src/agents/memory_config.py)
```python
"""Centralized MemoriSDK configuration for all agents"""
from memorisdk import Memori
import os

# Memory modes per agent type
MEMORY_CONFIGS = {
    'chat': {'mode': 'auto', 'db': 'chat_agent.db'},
    'trading': {'mode': 'combined', 'db': 'trading_agent.db'},  # Both conscious + auto
    'market_analysis': {'mode': 'auto', 'db': 'market_analysis.db', 'shared': True},
    'strategy': {'mode': 'auto', 'db': 'strategy_development.db', 'shared': True},
}

def get_memori(agent_type: str) -> Memori:
    """Factory function for agent memory"""
    config = MEMORY_CONFIGS.get(agent_type, {'mode': 'auto', 'db': 'default.db'})

    return Memori(
        mode=config['mode'],
        db_path=f"./src/data/memory/{config['db']}"
    )
```

### Agent Integration Pattern
```python
# Standard pattern for all agents
from src.agents.memory_config import get_memori

class AnyAgent:
    def __init__(self):
        # Enable memory
        self.memori = get_memori('trading')  # or 'chat', 'market_analysis', etc.
        self.memori.enable()

        # Existing initialization
        self.model = ModelFactory.create_model('anthropic')

    # No other changes needed - memory works automatically!
```

## Migration Path from Current System

### Backward Compatibility
```python
# Keep existing JSON loading for historical data
def migrate_old_memory(agent_name: str):
    """One-time migration from JSON to MemoriSDK"""
    old_file = f"./src/data/{agent_name}.json"
    if os.path.exists(old_file):
        with open(old_file, 'r') as f:
            old_data = json.load(f)

        # Inject into new memory
        memori = get_memori(agent_name)
        for conv in old_data.get('conversations', []):
            memori.add_memory(
                content=conv['message'],
                metadata={'timestamp': conv['timestamp'], 'migrated': True}
            )

        # Archive old file
        os.rename(old_file, f"{old_file}.archived")
```

## Cost Analysis

### Current System
- Storage: ~free (JSON files)
- Compute: Manual memory management overhead
- Scalability: Poor (linear search through JSON)

### With MemoriSDK
- Storage: SQLite ~free, PostgreSQL ~$20/month
- Compute: **80-90% cheaper than vector DBs**
- Inference: Minimal overhead (~50-200ms per query)
- ROI: Better decisions → improved PnL

**Example**: If memory improves trading decisions by 1% → easily pays for itself

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Integration bugs | Medium | Pilot with 3 agents first |
| Performance overhead | Low | A/B test, set timeout limits |
| Database corruption | Medium | Daily backups, SQLite is robust |
| Breaking existing code | Low | Memory is additive, doesn't replace |
| Vendor lock-in | Low | Open source, SQL export available |

## Success Metrics

**Week 1 (Pilot)**:
- [ ] 3 agents running with MemoriSDK
- [ ] No crashes or errors
- [ ] Measurable context improvement

**Week 3 (Expansion)**:
- [ ] 10+ agents using memory
- [ ] Cross-agent memory queries working
- [ ] A/B test shows quality improvement

**Week 6 (Production)**:
- [ ] All active agents on MemoriSDK
- [ ] PostgreSQL migration complete
- [ ] Analytics dashboard deployed
- [ ] Documented case studies of memory-driven decisions

## Next Steps

1. **Immediate** (Today):
   - [x] Review this plan
   - [ ] Approve pilot phase
   - [ ] `pip install memorisdk`

2. **Week 1**:
   - [ ] Integrate chat_agent, trading_agent, risk_agent
   - [ ] Test for 7 days
   - [ ] Document learnings

3. **Week 2-3**:
   - [ ] Expand to 10 agents
   - [ ] Set up shared memory pools
   - [ ] Run A/B tests

4. **Week 4+**:
   - [ ] PostgreSQL migration
   - [ ] Analytics dashboard
   - [ ] Full production deployment

## Conclusion

**STRONGLY RECOMMEND MERGE**

MemoriSDK is a perfect fit for this multi-agent trading system:
- ✅ Minimal code changes (2-3 lines per agent)
- ✅ Significant intelligence upgrade
- ✅ Cost-effective (cheaper than alternatives)
- ✅ Scales with 48+ agents
- ✅ Works with existing Anthropic/OpenAI integration
- ✅ Low risk (pilot approach)

The current JSON-based system works but has hit its limits. MemoriSDK provides the next evolution: agents that learn and improve over time.

**ROI**: If memory improves decision quality by even 5%, it pays for itself immediately in this trading context.

---

*Document created: 2025-11-12*
*Author: Claude Code Analysis*
*Status: Ready for Review*

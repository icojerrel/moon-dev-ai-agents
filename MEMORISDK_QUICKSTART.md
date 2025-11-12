# MemoriSDK Quick Start Guide

🎉 **MemoriSDK is now integrated!** Here's how to start using it.

## Prerequisites

You must be using the `tflow` conda environment (per CLAUDE.md):

```bash
conda activate tflow
```

## Installation (One-Time Setup)

```bash
# 1. Make sure you're in the conda environment
conda activate tflow

# 2. Install MemoriSDK
pip install memorisdk

# 3. Verify installation
python -c "from memorisdk import Memori; print('✅ MemoriSDK ready!')"
```

## Test the Integration

### Quick Test

```bash
# Run the test suite
python tests/test_memory_integration.py
```

Expected output: **7/7 tests passing** ✅

### Test Individual Agents

```bash
# Trading agent
python src/agents/trading_agent.py

# Risk agent
python src/agents/risk_agent.py

# Chat agent (requires Restream credentials in .env)
python src/agents/chat_agent.py
```

Look for this in the output:
```
🧠 [Agent name] memory enabled with MemoriSDK!
```

## What Changed?

### For Users
- **Nothing breaks** - all agents work exactly as before
- **New capability** - agents now remember conversations across sessions
- **Automatic** - memory works without any code changes in your usage
- **Fallback** - if MemoriSDK isn't installed, agents work normally without memory

### For Developers

Each integrated agent now has these 3 lines added:

```python
from src.agents.memory_config import get_memori

self.memori = get_memori('agent_type')
if self.memori:
    self.memori.enable()
```

That's it! Memory now works automatically.

## How It Works

1. **Automatic Context Injection**
   - When you talk to an agent, MemoriSDK searches past conversations
   - Relevant context is automatically added to the LLM prompt
   - No manual memory management needed

2. **Entity Extraction**
   - MemoriSDK extracts important entities (tokens, prices, decisions)
   - Categorizes into: facts, preferences, skills, rules, context
   - Builds a knowledge graph over time

3. **Cross-Session Learning**
   - Memory persists across agent restarts
   - Agents get smarter over time
   - Can reference decisions made days/weeks ago

## Examples

### Trading Agent Memory

**Without MemoriSDK**:
```
User: Should I buy SOL?
Agent: [analyzes current market data only]
```

**With MemoriSDK**:
```
User: Should I buy SOL?
Agent: [automatically retrieves]
  - "You asked about SOL 3 days ago, price was $98"
  - "We bought SOL on Jan 10, made 12% profit"
  - "Risk agent flagged high volatility for SOL yesterday"
[makes decision with full context]
```

### Risk Agent Memory

**Without MemoriSDK**:
```
Check daily limits → make decision → done
```

**With MemoriSDK**:
```
Check daily limits → [remembers]
  - "Similar situation on Jan 8, override was wrong"
  - "High volatility tokens usually recover in 2-3 days"
  - "Our best overrides had >90% confidence"
→ makes better decision with historical context
```

### Chat Agent Memory

**Without MemoriSDK**:
```
User: What's the best strategy?
Agent: [generic response]
```

**With MemoriSDK**:
```
User: What's the best strategy?
Agent: [remembers]
  - "You asked about mean reversion strategies last week"
  - "You prefer 15m timeframes"
  - "You're focused on BTC and SOL"
→ personalized response
```

## Memory Modes

Each agent uses a different memory mode:

| Agent | Mode | Why |
|-------|------|-----|
| Chat | auto | Dynamic search per query |
| Trading | combined | Both conscious + auto for critical decisions |
| Risk | conscious | Explicit context injection |
| Market Analysis | auto | Shared knowledge pool |

## Checking Memory

Memory is stored in SQLite databases:

```bash
# List memory databases
ls -lh src/data/memory/

# Example output:
# chat_agent.db           (100 KB)
# trading_agent.db        (250 KB)
# risk_agent.db          (180 KB)
```

To inspect a database:

```bash
# Install sqlite3 if needed
sudo apt-get install sqlite3

# Query the database
sqlite3 src/data/memory/trading_agent.db ".tables"
sqlite3 src/data/memory/trading_agent.db "SELECT * FROM conversations LIMIT 5;"
```

## Disabling Memory (Optional)

If you want to run an agent WITHOUT memory:

```python
# In the agent code, change:
self.memori = get_memori('trading')

# To:
self.memori = get_memori('trading', disable=True)

# Or just:
self.memori = None
```

## Performance

- **Latency**: ~50-200ms per LLM call (for memory retrieval)
- **Storage**: Databases start at ~100KB, grow with usage
- **Cost**: 80-90% cheaper than vector database alternatives (like Pinecone)
- **Background**: Memory gets optimized every 6 hours automatically

## Troubleshooting

### "ModuleNotFoundError: No module named 'memorisdk'"

```bash
# Make sure you're in conda environment
conda activate tflow

# Install MemoriSDK
pip install memorisdk

# Verify
python -c "from memorisdk import Memori; print('OK')"
```

### Memory not showing in agent logs

If you don't see "🧠 memory enabled" message:
1. Check that MemoriSDK is installed: `pip list | grep memorisdk`
2. Check Python environment: `which python` (should be in conda)
3. Look for warnings in agent output

### Tests fail with "Memory returned None"

This is OK! The system gracefully degrades if MemoriSDK isn't installed.

To fix:
```bash
conda activate tflow
pip install memorisdk
python tests/test_memory_integration.py
```

## Next Steps

### Phase 1 (✅ Complete)
- chat_agent, trading_agent, risk_agent integrated

### Phase 2 (Upcoming - Week 2-3)
- Expand to 10 agents total
- Implement shared memory pools
- A/B testing (with/without memory)

### Phase 3 (Upcoming - Week 4+)
- PostgreSQL for production scale
- Memory analytics dashboard
- Cross-agent memory queries

## Resources

- **Full Plan**: MEMORISDK_INTEGRATION_PLAN.md
- **Evaluation**: MEMORISDK_EVALUATION.md
- **Implementation Notes**: MEMORISDK_IMPLEMENTATION_NOTES.md
- **POC Demo**: examples/memorisdk_poc.py
- **MemoriSDK Docs**: https://gibsonai.github.io/memori/

## Questions?

1. Check implementation notes: `MEMORISDK_IMPLEMENTATION_NOTES.md`
2. Run test suite: `python tests/test_memory_integration.py`
3. Review POC demo: `python examples/memorisdk_poc.py`

---

**TL;DR**:
```bash
conda activate tflow
pip install memorisdk
python tests/test_memory_integration.py
python src/agents/trading_agent.py  # Look for "🧠 memory enabled" message
```

🚀 **That's it! Your agents now have persistent memory!**

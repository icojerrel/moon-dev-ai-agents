# RBI Agent Memory Integration 🧠

## Overview

The RBI (Research-Backtest-Implement) Agent now includes persistent memory capabilities using the mem-layer library. This allows the agent to:

- Remember all strategy research sessions
- Track backtest success/failure rates
- Store learnings from errors
- Recall similar strategies before processing new ideas
- Build a knowledge base of successful patterns

## Features Added

### 1. **Memory Initialization**
```python
memory = get_rbi_memory()  # Gets research scope memory
```

The RBI agent uses the `research` scope for all its memories, separate from trading operations.

### 2. **Strategy Research Tracking**
Every strategy research phase is remembered:
```python
remember_strategy_research(
    memory,
    strategy_name="QuantumMomentum",
    idea_source="YouTube video about...",
    strategy_description="Uses quantum indicators for...",
    success=True
)
```

**Stored Information:**
- Strategy name
- Idea source (truncated to 200 chars)
- Strategy description (truncated to 500 chars)
- Success/failure status
- Timestamp

### 3. **Backtest Result Tracking**
All backtest creation attempts are logged:
```python
remember_backtest_result(
    memory,
    strategy_name="QuantumMomentum",
    success=True,
    error_msg=None,  # or error message if failed
    code_length=1500
)
```

**Stored Information:**
- Strategy name
- Success/failure
- Error message (if failed)
- Generated code length
- Timestamp

### 4. **Learning Capture**
The agent captures learnings from both successes and failures:
```python
remember_rbi_learning(
    memory,
    strategy_name="QuantumMomentum",
    lesson="Successfully completed full RBI cycle",
    category="success"  # or "error", "general"
)
```

**Categories:**
- `success`: What worked well
- `error`: Problems encountered
- `general`: General insights

### 5. **Similar Strategy Recall**
Before processing a new idea, the agent checks for similar past strategies:
```python
similar = recall_similar_strategies(
    memory,
    strategy_description="momentum trading strategy",
    limit=3
)
```

This helps avoid duplicate work and learn from past attempts.

### 6. **RBI Context Retrieval**
Get comprehensive context about past RBI sessions:
```python
context = get_rbi_context(memory, strategy_name="OptionalName")
```

**Returns:**
```python
{
    "recent_strategies": [
        {"name": "QuantumMomentum", "success": True},
        {"name": "AdaptiveTrend", "success": False}
    ],
    "successful_backtests": [
        "QuantumMomentum",
        "NeuralBreakout"
    ],
    "learnings": [
        {
            "content": "Successfully completed full RBI cycle...",
            "category": "success"
        }
    ]
}
```

### 7. **Memory Linking**
Related memories are linked together:
```python
# Link research → backtest → final
memory.link_memories(research_id, backtest_id, "TEMPORAL_SEQUENCE")
memory.link_memories(backtest_id, final_id, "TEMPORAL_SEQUENCE")
```

This creates a graph of the complete RBI process for each strategy.

### 8. **Automatic Memory Export**
After each successful strategy completion, memory is exported:
```python
export_path = memory.export_memory()
# Saves to: src/data/memory/memory_export_research_YYYYMMDD_HHMMSS.json
```

## Memory Workflow

```
┌─────────────────────────────────────────────┐
│  1. Initialize Memory (research scope)      │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  2. Recall Similar Strategies               │
│     - Search past research                  │
│     - Display similar strategies            │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  3. Research Phase                          │
│     - Extract strategy                      │
│     - Remember research ──┐                 │
└───────────────────────────┼─────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────┐
│  4. Backtest Phase                          │
│     - Create backtest code                  │
│     - Remember backtest result ──┐          │
│     - Link to research           │          │
└──────────────────────────────────┼──────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────┐
│  5. Package & Debug Phases                  │
│     - (No memory tracking - optimization)   │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  6. Final Success                           │
│     - Remember completion                   │
│     - Add success learning                  │
│     - Link all phases                       │
│     - Export memory snapshot                │
└─────────────────────────────────────────────┘
```

## Error Handling

Memory failures don't stop the RBI process:

```python
try:
    remember_strategy_research(...)
except Exception as e:
    cprint(f"⚠️  Failed to save memory: {e}", "yellow")
    # Process continues...
```

All memory operations are wrapped in try-except blocks to ensure:
- Memory failures don't crash the agent
- User is notified of memory issues
- RBI process continues normally

## Memory Queries

### Get All Successful Strategies
```python
successful = memory.query("tags:rbi AND tags:success")
for node in successful.nodes:
    print(f"✓ {node.metadata['strategy_name']}")
```

### Get Recent Research
```python
recent = memory.query("tags:rbi AND tags:research")
for node in recent.nodes[:5]:  # Last 5
    print(f"📊 {node.content}")
```

### Search by Strategy Name
```python
results = memory.search_memories("Quantum", limit=10)
for result in results:
    print(f"Found: {result['content']}")
```

### Get All Errors
```python
errors = memory.query("tags:agent_note AND tags:RBI_Agent")
for node in errors.nodes:
    if node.metadata.get("category") == "error":
        print(f"❌ {node.content}")
```

## Configuration

Memory can be controlled via `src/config.py`:

```python
MEMORY_ENABLED = True  # Enable/disable memory
MEMORY_SCOPE = "trading"  # Default scope (RBI uses "research")
MEMORY_AUTO_SAVE = True  # Auto-save after runs
MEMORY_RECALL_LIMIT = 10  # Number of memories to recall
MEMORY_IMPORTANCE_THRESHOLD = 0.7  # Min importance to retain
MEMORY_EXPORT_INTERVAL = 24  # Export every N hours
```

## Benefits

1. **Avoid Duplicate Work**: See if similar strategies were already tested
2. **Learn from Failures**: Track what caused backtest failures
3. **Pattern Recognition**: Identify successful strategy patterns
4. **Progress Tracking**: View complete history of RBI sessions
5. **Knowledge Retention**: Never lose insights from past work
6. **Continuous Improvement**: Each run improves the knowledge base

## Memory Storage

All RBI memories are stored in:
```
src/data/memory/
├── *.db                        # SQLite database (gitignored)
├── *.json                      # Exported snapshots (gitignored)
└── memory_export_research_*.json  # Timestamped exports
```

## Example Memory Graph

After processing 3 strategies, the memory graph might look like:

```
QuantumMomentum (Research) ──┐
                             │
                             ├── Backtest Created ──┐
                             │                      │
                             │                      ├── Complete ✓
                             │
AdaptiveTrend (Research) ────┐
                             │
                             ├── Backtest Failed ✗
                             │
                             ├── Learning: "Need more indicators"
                             │
NeuralBreakout (Research) ───┐
                             │
                             ├── Backtest Created ──┐
                             │                      │
                             │                      ├── Complete ✓
```

## Future Enhancements

Potential future improvements:
- Strategy performance correlation analysis
- Automatic strategy recommendation
- Pattern-based backtest optimization
- Success rate analytics dashboard
- Cross-agent memory sharing (RBI → Trading Agent)

## Troubleshooting

### Memory Not Saving
- Check `MEMORY_ENABLED = True` in config
- Verify mem-layer is installed: `pip install mem-layer`
- Check write permissions on `src/data/memory/`

### Import Errors
```bash
pip install mem-layer
pip install -r requirements.txt
```

### Memory Queries Return Empty
- Ensure you've processed at least one strategy
- Check memory scope is "research"
- Verify memory files exist in `src/data/memory/`

---

**Built with 🌙 by Moon Dev's AI Assistant**

For questions or issues, see the main project README or open an issue on GitHub.

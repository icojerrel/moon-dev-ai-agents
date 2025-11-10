# Memory Layer Integration Guide

## Overview

The memory layer provides persistent, cross-agent memory for the 48+ AI trading agents using [mem-layer](https://github.com/icojerrel/mem-layer). This enables agents to:

- **Share insights** across agent boundaries
- **Remember past decisions** and outcomes
- **Cache API responses** to reduce costs
- **Coordinate actions** through temporal awareness
- **Learn from history** across sessions

## Quick Start

### 1. Basic Usage

```python
from src.memory import AgentMemory, MemoryScope

# Initialize memory for your agent
memory = AgentMemory(agent_name="my_agent")

# Store an insight
memory.store(
    "BTC showing bullish divergence on 4H",
    scope=MemoryScope.MARKET_ANALYSIS,
    priority="high"
)

# Retrieve recent memories
recent_insights = memory.get_recent(
    scope=MemoryScope.MARKET_ANALYSIS,
    hours=24
)

# Broadcast critical alert to all agents
memory.broadcast(
    "Flash crash detected on SOL!",
    scope=MemoryScope.ALERTS,
    priority="critical"
)
```

### 2. Integration Pattern

Add memory to any agent in 4 steps:

```python
# Step 1: Import
from src.memory import AgentMemory, MemoryScope

# Step 2: Initialize in __init__
class MyAgent:
    def __init__(self):
        # ... existing init code ...

        self.memory = AgentMemory(agent_name="my_agent")
        if self.memory.enabled:
            print("🧠 Memory layer initialized")

# Step 3: Store insights during execution
def analyze_market(self, token):
    # ... analysis logic ...

    if self.memory and self.memory.enabled:
        self.memory.store(
            f"Analysis for {token}: {result}",
            scope=MemoryScope.MARKET_ANALYSIS,
            priority="medium"
        )

# Step 4: Read relevant context before decisions
def make_decision(self):
    if self.memory and self.memory.enabled:
        # Check for risk warnings
        alerts = self.memory.get_recent(
            scope=MemoryScope.ALERTS,
            hours=1,
            priority="critical"
        )
```

## Memory Scopes

Each scope has specific retention policies and access controls:

### Trading Scopes
- **`RISK`**: Risk warnings, circuit breakers (30 days)
- **`TRADING`**: Trade executions, P&L (30 days)
- **`STRATEGY`**: Strategy performance, signals (7 days)

### Analysis Scopes
- **`MARKET_ANALYSIS`**: Market data, sentiment (7 days)
- **`SENTIMENT`**: Social sentiment, news (7 days)
- **`WHALE`**: Whale activity tracking (7 days)
- **`FUNDING`**: Funding rates, OI data (7 days)
- **`LIQUIDATION`**: Liquidation events (7 days)

### Coordination Scopes
- **`GLOBAL`**: Shared insights across all agents (14 days)
- **`ALERTS`**: Critical events requiring attention (30 days)
- **`CACHE`**: API response caching (15 minutes)

## API Reference

### AgentMemory Class

#### `store(content, scope, priority, metadata=None)`
Store a memory/insight.

**Parameters:**
- `content` (str): The insight or observation to store
- `scope` (MemoryScope): Memory category
- `priority` (str): "critical", "high", "medium", or "low"
- `metadata` (dict): Optional structured data

**Returns:** bool - True if stored successfully

**Example:**
```python
memory.store(
    "Position closed with 15% profit",
    scope=MemoryScope.TRADING,
    priority="high",
    metadata={
        "token": "SOL",
        "profit_pct": 15.2,
        "entry_price": 100,
        "exit_price": 115.2
    }
)
```

#### `get_recent(scope=None, hours=1.0, priority=None, limit=None)`
Retrieve recent memories.

**Parameters:**
- `scope` (MemoryScope): Filter by scope (None = all accessible)
- `hours` (float): How far back to search
- `priority` (str): Filter by priority level
- `limit` (int): Max memories to return

**Returns:** List[Dict] - Sorted by recency

**Example:**
```python
# Get last hour's risk warnings
warnings = memory.get_recent(
    scope=MemoryScope.RISK,
    hours=1,
    priority="high"
)

for warning in warnings:
    print(f"{warning['agent']}: {warning['content']}")
```

#### `broadcast(content, scope=ALERTS, priority="high", metadata=None)`
Broadcast important insight to all agents.

**Example:**
```python
memory.broadcast(
    "Market volatility spike detected",
    priority="critical",
    metadata={"vix_level": 45}
)
```

#### `cache_api_response(api_name, endpoint, response_data, ttl_minutes=15)`
Cache API response to reduce duplicate calls.

**Example:**
```python
# Before API call - check cache
cached = memory.get_cached_response("birdeye", f"/token/{token_address}")
if cached:
    return cached

# Make API call
response = api.get_token_data(token_address)

# Store in cache
memory.cache_api_response("birdeye", f"/token/{token_address}", response)
```

#### `handoff(to_agent, message, context=None)`
Hand off information to another specific agent.

**Example:**
```python
# From whale_agent to trading_agent
memory.handoff(
    to_agent="trading_agent",
    message="Large accumulation detected on BTC",
    context={"token": "BTC", "volume_usd": 5_000_000}
)
```

#### `get_handoffs()`
Get messages handed off to this agent.

**Example:**
```python
handoffs = memory.get_handoffs()
for handoff in handoffs:
    print(f"From {handoff['metadata']['from_agent']}: {handoff['content']}")
```

## Configuration

Edit `src/config.py` to customize memory behavior:

```python
# Enable/disable memory system
ENABLE_MEMORY = True

# Database location
MEMORY_DB_PATH = "src/data/memory/agent_memory.db"

# Retention period for critical data
MEMORY_RETENTION_DAYS = 30

# Enable API caching to reduce costs
ENABLE_MEMORY_CACHING = True

# Allow agents to share insights
ENABLE_CROSS_AGENT_SHARING = True
```

Advanced configuration in `src/memory/memory_config.py`:
- Retention policies per scope
- Access control (which agents can read which scopes)
- Priority levels
- Temporal decay settings

## Use Cases

### 1. Risk Coordination
**Problem**: trading_agent doesn't see risk_agent warnings until too late

**Solution**:
```python
# In risk_agent.py
if balance < MINIMUM_BALANCE:
    memory.broadcast(
        f"CRITICAL: Balance ${balance} below minimum!",
        scope=MemoryScope.ALERTS,
        priority="critical"
    )

# In trading_agent.py (before trading)
alerts = memory.get_recent(scope=MemoryScope.ALERTS, hours=1)
if any("CRITICAL" in a['content'] for a in alerts):
    print("⚠️ Risk alert active - skipping trades")
    return
```

### 2. Strategy Performance Tracking
**Problem**: No way to know if strategies actually work over time

**Solution**:
```python
# When opening position
memory.store(
    f"Strategy: {strategy_name} signaled BUY on {token}",
    scope=MemoryScope.STRATEGY,
    priority="high",
    metadata={"strategy": strategy_name, "entry_price": price}
)

# When closing position
memory.store(
    f"Strategy: {strategy_name} result: {pnl_pct}%",
    scope=MemoryScope.STRATEGY,
    metadata={"strategy": strategy_name, "pnl_pct": pnl_pct}
)

# Later: analyze strategy performance
strategy_results = memory.get_recent(
    scope=MemoryScope.STRATEGY,
    hours=7*24  # Last week
)
# Calculate win rate, avg PnL, etc.
```

### 3. API Cost Reduction
**Problem**: Agents repeatedly call expensive APIs for same data

**Solution**:
```python
def get_token_overview(token):
    # Check cache first (15min TTL)
    cached = memory.get_cached_response("birdeye", f"overview/{token}")
    if cached:
        print("💾 Using cached data")
        return cached

    # Cache miss - fetch from API
    data = birdeye_api.token_overview(token)

    # Cache for next time
    memory.cache_api_response("birdeye", f"overview/{token}", data)
    return data
```

### 4. Multi-Agent Workflows
**Problem**: sentiment_agent finds important news, but trading_agent doesn't see it

**Solution**:
```python
# In sentiment_agent.py
if sentiment_score < -0.8:  # Very negative
    memory.handoff(
        to_agent="trading_agent",
        message=f"Extreme negative sentiment on {token}",
        context={"sentiment": sentiment_score, "source": "twitter"}
    )

# In trading_agent.py
handoffs = memory.get_handoffs()
for msg in handoffs:
    if "negative sentiment" in msg['content']:
        print(f"⚠️ Sentiment warning: {msg['content']}")
        # Adjust position sizing or skip trade
```

## Integration Examples

### Example 1: sentiment_agent.py

```python
from src.memory import AgentMemory, MemoryScope

class SentimentAgent:
    def __init__(self):
        self.memory = AgentMemory(agent_name="sentiment_agent")

    def analyze_sentiment(self, token):
        # Check cache first
        cached = self.memory.get_cached_response("twitter", f"sentiment/{token}")
        if cached:
            return cached

        # Fetch sentiment
        sentiment = self.fetch_twitter_sentiment(token)

        # Cache result
        self.memory.cache_api_response("twitter", f"sentiment/{token}", sentiment)

        # Store analysis
        self.memory.store(
            f"Sentiment for {token}: {sentiment['score']}",
            scope=MemoryScope.SENTIMENT,
            priority="medium",
            metadata=sentiment
        )

        # Alert if extreme
        if abs(sentiment['score']) > 0.8:
            self.memory.broadcast(
                f"EXTREME sentiment on {token}: {sentiment['score']}",
                priority="high"
            )

        return sentiment
```

### Example 2: whale_agent.py

```python
from src.memory import AgentMemory, MemoryScope

class WhaleAgent:
    def __init__(self):
        self.memory = AgentMemory(agent_name="whale_agent")

    def track_whale_movements(self):
        movements = self.fetch_whale_transactions()

        for move in movements:
            if move['value_usd'] > 1_000_000:  # $1M+
                # Store whale activity
                self.memory.store(
                    f"Whale movement: ${move['value_usd']:,.0f} {move['token']}",
                    scope=MemoryScope.WHALE,
                    priority="high",
                    metadata=move
                )

                # Alert trading_agent
                self.memory.handoff(
                    to_agent="trading_agent",
                    message=f"Large {move['type']} detected: ${move['value_usd']:,.0f}",
                    context=move
                )
```

## Best Practices

### 1. **Check Before Storing**
```python
if self.memory and self.memory.enabled:
    self.memory.store(...)
```
Always check if memory is available before using it.

### 2. **Use Appropriate Scopes**
- Trading decisions → `TRADING`
- Risk events → `RISK`
- Market analysis → `MARKET_ANALYSIS`
- Critical alerts → `ALERTS`

### 3. **Set Correct Priorities**
- `critical`: System-level events (circuit breakers, major losses)
- `high`: Important decisions (trade executions, risk warnings)
- `medium`: Regular observations (market analysis, sentiment)
- `low`: Background data (cached responses)

### 4. **Include Metadata**
Store structured data for later analysis:
```python
memory.store(
    "Trade executed",
    metadata={
        "token": token,
        "action": "BUY",
        "price": entry_price,
        "amount_usd": position_size,
        "strategy": strategy_name
    }
)
```

### 5. **Cache Expensive API Calls**
```python
# Before calling API
cached = memory.get_cached_response(api_name, endpoint)
if cached:
    return cached

# After API call
memory.cache_api_response(api_name, endpoint, response)
```

### 6. **Broadcast Sparingly**
Only broadcast truly important events:
```python
# Good: Critical system event
memory.broadcast("Circuit breaker triggered!", priority="critical")

# Bad: Routine observation
# memory.broadcast("Price moved 1%", priority="low")  # Don't do this
```

## Troubleshooting

### Memory Not Working?
1. Check `ENABLE_MEMORY = True` in `config.py`
2. Verify mem-layer is installed: `pip list | grep mem-layer`
3. Check database path exists: `src/data/memory/`
4. Look for import errors in agent logs

### Slow Performance?
1. Reduce `MAX_MEMORIES_PER_QUERY` in `memory_config.py`
2. Decrease retention periods for non-critical scopes
3. Use more specific scope filters when querying

### Memory Growing Too Large?
1. Run cleanup: `memory.cleanup_old_memories()`
2. Adjust retention policies in `memory_config.py`
3. Reduce cache TTL for `CACHE` scope

## Future Enhancements

Potential improvements for the memory system:

1. **Semantic Search**: Query memories by meaning, not just tags
2. **Performance Analytics**: Built-in strategy performance tracking
3. **Memory Compression**: Summarize old memories instead of deleting
4. **Cross-Session Learning**: Train models on historical memory data
5. **Memory Visualization**: Dashboard showing agent interactions
6. **Conflict Resolution**: Handle contradictory memories from different agents

## Support

- Documentation: This file
- Example implementations: `risk_agent.py`, `trading_agent.py`
- mem-layer docs: https://github.com/icojerrel/mem-layer
- Issues: Create GitHub issue or ask in Discord

---

**Remember**: The memory layer is optional. Agents work fine without it, but gain significant coordination benefits with it enabled.

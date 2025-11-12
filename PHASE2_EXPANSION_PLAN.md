# Phase 2: Expansion Plan

## Agent Groups & Memory Architecture

### Group 1: Market Analysis (SHARED MEMORY POOL)
**Database**: `market_analysis_shared.db`
**Mode**: `auto` (dynamic search)
**Agents**:
1. sentiment_agent.py - Market sentiment analysis
2. whale_agent.py - Large wallet movements
3. funding_agent.py - Funding rates and OI data

**Benefit**: Cross-agent intelligence
- Whale agent sees sentiment trends
- Sentiment agent sees funding pressure
- Funding agent sees whale movements
- Combined: "Whales accumulating + positive sentiment + low funding = strong buy signal"

### Group 2: Strategy Development (SHARED MEMORY POOL)
**Database**: `strategy_development.db`
**Mode**: `auto` (dynamic search)
**Agents**:
4. strategy_agent.py - Strategy execution
5. rbi_agent.py - Research-Based Inference (backtest generation)

**Benefit**: Strategy learning
- RBI learns from past backtest results
- Strategy agent learns from RBI insights
- Combined: "Similar RSI strategy failed in low volume (RBI backtest 2 weeks ago)"

### Group 3: Content Creation (SHARED MEMORY POOL)
**Database**: `content_creation.db`
**Mode**: `auto` (dynamic search)
**Agents**:
6. tweet_agent.py - Twitter content
7. video_agent.py - Video content

**Benefit**: Content consistency
- Tweet agent knows recent video topics
- Video agent knows tweet performance
- Combined: "Don't repeat yesterday's tweet topic in today's video"

### Group 4: Specialized Trading (INDIVIDUAL MEMORY)
**Mode**: `combined` or `conscious` (critical decisions)
**Agents**:
8. copybot_agent.py - Copy trading (`copybot_agent.db`)
9. sniper_agent.py - Token sniping (`sniper_agent.db`)
10. solana_agent.py - Solana-specific trading (`solana_agent.db`)

**Benefit**: Specialized learning
- Each needs isolated memory for specialized strategies
- High-frequency decisions benefit from conscious + auto mode

## Implementation Order

### Batch 1: Market Analysis (30 min)
- ✅ sentiment_agent.py
- ✅ whale_agent.py
- ✅ funding_agent.py
- Test shared memory coordination

### Batch 2: Strategy Development (20 min)
- ✅ strategy_agent.py
- ✅ rbi_agent.py
- Test strategy learning

### Batch 3: Content Creation (20 min)
- ✅ tweet_agent.py
- ✅ video_agent.py
- Test content consistency

### Batch 4: Specialized Trading (20 min)
- ✅ copybot_agent.py
- ✅ sniper_agent.py
- ✅ solana_agent.py
- Test individual memory isolation

## Expected Results

**Total Agents with Memory**: 13 (3 from Phase 1 + 10 from Phase 2)

**Memory Databases**:
- chat_agent.db (individual)
- trading_agent.db (individual)
- risk_agent.db (individual)
- **market_analysis_shared.db** (3 agents) ⭐
- **strategy_development.db** (2 agents) ⭐
- **content_creation.db** (2 agents) ⭐
- copybot_agent.db (individual)
- sniper_agent.db (individual)
- solana_agent.db (individual)

**New Capabilities**:
- Cross-agent intelligence via shared memory
- Strategy evolution over time
- Content topic coordination
- Specialized strategy learning

## Testing Strategy

After each batch:
1. Verify "memory enabled" messages in logs
2. Check database file creation
3. Test agent functionality
4. Verify shared vs individual memory

Final validation:
- Run all 13 agents
- Query shared databases for cross-agent entries
- Validate memory isolation for specialized agents
- Performance testing (latency impact)

Ready to proceed? Let's start with Batch 1: Market Analysis! 🚀

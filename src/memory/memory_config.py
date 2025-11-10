"""
Memory configuration for AI trading agents.

Defines memory scopes, retention policies, and access patterns
for the 48+ specialized trading agents.
"""

from enum import Enum
from typing import Dict, List
from datetime import timedelta


class MemoryScope(Enum):
    """Memory scopes for different agent types and data categories."""

    # Core trading scopes
    RISK = "risk"                    # Risk warnings, circuit breakers, loss events
    TRADING = "trading"              # Trade executions, positions, P&L
    MARKET_ANALYSIS = "market"       # Market data, sentiment, whale activity
    STRATEGY = "strategy"            # Strategy performance, backtests, signals

    # Specialized scopes
    SENTIMENT = "sentiment"          # Social sentiment, news analysis
    WHALE = "whale"                  # Whale wallet tracking, large movements
    FUNDING = "funding"              # Funding rates, OI data
    LIQUIDATION = "liquidation"      # Liquidation events
    COPYBOT = "copybot"             # Copybot follow list, performance

    # Cross-agent coordination
    GLOBAL = "global"                # Shared insights across all agents
    ALERTS = "alerts"                # Important events requiring multi-agent awareness

    # Data caching
    CACHE = "cache"                  # API response caching to reduce costs


class MemoryConfig:
    """Configuration for memory retention and access policies."""

    # Retention policies (how long to keep memories)
    RETENTION_POLICIES: Dict[MemoryScope, timedelta] = {
        # Critical data - keep for 30 days
        MemoryScope.RISK: timedelta(days=30),
        MemoryScope.TRADING: timedelta(days=30),
        MemoryScope.ALERTS: timedelta(days=30),

        # Analysis data - keep for 7 days
        MemoryScope.MARKET_ANALYSIS: timedelta(days=7),
        MemoryScope.STRATEGY: timedelta(days=7),
        MemoryScope.SENTIMENT: timedelta(days=7),
        MemoryScope.WHALE: timedelta(days=7),
        MemoryScope.FUNDING: timedelta(days=7),
        MemoryScope.LIQUIDATION: timedelta(days=7),
        MemoryScope.COPYBOT: timedelta(days=7),

        # Global coordination - keep for 14 days
        MemoryScope.GLOBAL: timedelta(days=14),

        # Cache - keep for 15 minutes (one agent loop cycle)
        MemoryScope.CACHE: timedelta(minutes=15),
    }

    # Access control: which agents can read from which scopes
    SCOPE_ACCESS: Dict[str, List[MemoryScope]] = {
        # Risk agent - reads all scopes to assess overall risk
        "risk_agent": [
            MemoryScope.RISK,
            MemoryScope.TRADING,
            MemoryScope.MARKET_ANALYSIS,
            MemoryScope.ALERTS,
            MemoryScope.GLOBAL,
        ],

        # Trading agent - reads risk warnings and market data
        "trading_agent": [
            MemoryScope.RISK,
            MemoryScope.TRADING,
            MemoryScope.MARKET_ANALYSIS,
            MemoryScope.STRATEGY,
            MemoryScope.ALERTS,
            MemoryScope.GLOBAL,
            MemoryScope.CACHE,
        ],

        # Sentiment agent - reads sentiment and market data
        "sentiment_agent": [
            MemoryScope.SENTIMENT,
            MemoryScope.MARKET_ANALYSIS,
            MemoryScope.GLOBAL,
            MemoryScope.CACHE,
        ],

        # Whale agent - reads whale activity and market data
        "whale_agent": [
            MemoryScope.WHALE,
            MemoryScope.MARKET_ANALYSIS,
            MemoryScope.ALERTS,
            MemoryScope.GLOBAL,
            MemoryScope.CACHE,
        ],

        # Strategy agent - reads all performance and market data
        "strategy_agent": [
            MemoryScope.STRATEGY,
            MemoryScope.TRADING,
            MemoryScope.MARKET_ANALYSIS,
            MemoryScope.RISK,
            MemoryScope.GLOBAL,
        ],

        # Default for other agents
        "default": [
            MemoryScope.GLOBAL,
            MemoryScope.ALERTS,
            MemoryScope.CACHE,
        ],
    }

    # Priority levels for memory retrieval
    PRIORITY_LEVELS = {
        "critical": 10,    # Circuit breakers, major losses
        "high": 7,         # Trade executions, risk warnings
        "medium": 5,       # Market insights, strategy signals
        "low": 3,          # Cached data, general observations
    }

    # Database path for mem-layer storage
    DB_PATH = "src/data/memory/agent_memory.db"

    # Max memories to retrieve per query (avoid context overload)
    MAX_MEMORIES_PER_QUERY = 20

    # Enable/disable features
    ENABLE_TEMPORAL_DECAY = True   # Older memories have lower relevance
    ENABLE_CROSS_AGENT_SHARING = True  # Agents can see each other's insights
    ENABLE_CACHING = True          # Cache API responses

"""
AgentMemory: Lightweight wrapper around mem-layer for AI trading agents.

Provides simple interface for agents to:
- Store insights, decisions, and observations
- Retrieve relevant past memories
- Share context across agent boundaries
- Cache API responses to reduce costs
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

try:
    from mem_layer import MemoryGraph
    MEM_LAYER_AVAILABLE = True
except ImportError:
    MEM_LAYER_AVAILABLE = False
    print("Warning: mem-layer not available. Memory features disabled.")

from src.memory.memory_config import MemoryScope, MemoryConfig


class AgentMemory:
    """
    Simple memory interface for trading agents.

    Usage:
        memory = AgentMemory(agent_name="risk_agent")

        # Store a memory
        memory.store("Risk warning: BTC volatility high",
                    scope=MemoryScope.RISK,
                    priority="high")

        # Retrieve relevant memories
        memories = memory.get_recent(scope=MemoryScope.RISK, hours=1)

        # Share insight with other agents
        memory.broadcast("Major whale movement detected on SOL",
                        scope=MemoryScope.ALERTS)
    """

    def __init__(self, agent_name: str, config: Optional[MemoryConfig] = None):
        """
        Initialize memory interface for an agent.

        Args:
            agent_name: Name of the agent (e.g., "risk_agent", "trading_agent")
            config: Optional custom configuration (defaults to MemoryConfig)
        """
        self.agent_name = agent_name
        self.config = config or MemoryConfig()
        self.enabled = MEM_LAYER_AVAILABLE and self._should_enable()

        if self.enabled:
            self._init_memory_graph()
        else:
            self.graph = None

    def _should_enable(self) -> bool:
        """Check if memory should be enabled (from config.py)."""
        try:
            from src.config import ENABLE_MEMORY
            return ENABLE_MEMORY
        except (ImportError, AttributeError):
            return True  # Default to enabled if config not found

    def _init_memory_graph(self):
        """Initialize mem-layer graph database."""
        # Ensure directory exists
        db_path = Path(self.config.DB_PATH)
        db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize graph
        self.graph = MemoryGraph(db_path=str(db_path))

    def store(self,
              content: str,
              scope: MemoryScope = MemoryScope.GLOBAL,
              priority: str = "medium",
              metadata: Optional[Dict] = None) -> bool:
        """
        Store a memory/insight.

        Args:
            content: The insight, observation, or decision to store
            scope: Memory scope (RISK, TRADING, MARKET_ANALYSIS, etc.)
            priority: "critical", "high", "medium", or "low"
            metadata: Optional additional data (token_address, price, etc.)

        Returns:
            True if stored successfully, False otherwise
        """
        if not self.enabled:
            return False

        try:
            # Build memory data
            memory_data = {
                "agent": self.agent_name,
                "scope": scope.value,
                "priority": priority,
                "timestamp": datetime.now().isoformat(),
                "content": content,
            }

            # Add metadata if provided
            if metadata:
                memory_data["metadata"] = metadata

            # Store in graph
            self.graph.add_memory(
                content=content,
                tags=[scope.value, self.agent_name, priority],
                metadata=memory_data
            )

            return True

        except Exception as e:
            print(f"[{self.agent_name}] Failed to store memory: {e}")
            return False

    def get_recent(self,
                   scope: Optional[MemoryScope] = None,
                   hours: float = 1.0,
                   priority: Optional[str] = None,
                   limit: Optional[int] = None) -> List[Dict]:
        """
        Get recent memories from specified scope.

        Args:
            scope: Filter by scope (None = all accessible scopes)
            hours: How many hours back to search
            priority: Filter by priority level
            limit: Max memories to return (defaults to config)

        Returns:
            List of memory dictionaries sorted by relevance/recency
        """
        if not self.enabled:
            return []

        try:
            # Determine which scopes to search
            if scope:
                scopes = [scope.value]
            else:
                # Get all accessible scopes for this agent
                accessible = self.config.SCOPE_ACCESS.get(
                    self.agent_name,
                    self.config.SCOPE_ACCESS["default"]
                )
                scopes = [s.value for s in accessible]

            # Calculate time threshold
            since = datetime.now() - timedelta(hours=hours)

            # Query memories
            memories = []
            for scope_name in scopes:
                results = self.graph.search_memories(
                    tags=[scope_name],
                    limit=limit or self.config.MAX_MEMORIES_PER_QUERY
                )

                for result in results:
                    metadata = result.get("metadata", {})
                    timestamp = datetime.fromisoformat(metadata.get("timestamp", datetime.now().isoformat()))

                    # Filter by time
                    if timestamp < since:
                        continue

                    # Filter by priority if specified
                    if priority and metadata.get("priority") != priority:
                        continue

                    memories.append({
                        "content": result.get("content"),
                        "scope": metadata.get("scope"),
                        "priority": metadata.get("priority"),
                        "agent": metadata.get("agent"),
                        "timestamp": timestamp,
                        "metadata": metadata.get("metadata", {})
                    })

            # Sort by timestamp (most recent first)
            memories.sort(key=lambda x: x["timestamp"], reverse=True)

            return memories[:limit] if limit else memories

        except Exception as e:
            print(f"[{self.agent_name}] Failed to retrieve memories: {e}")
            return []

    def broadcast(self,
                  content: str,
                  scope: MemoryScope = MemoryScope.ALERTS,
                  priority: str = "high",
                  metadata: Optional[Dict] = None) -> bool:
        """
        Broadcast important insight to all agents.

        This is a convenience method for high-priority cross-agent communication.

        Args:
            content: The alert/insight to broadcast
            scope: Typically ALERTS or GLOBAL
            priority: Usually "high" or "critical"
            metadata: Optional additional context

        Returns:
            True if broadcast successfully
        """
        return self.store(
            content=f"[BROADCAST] {content}",
            scope=scope,
            priority=priority,
            metadata=metadata
        )

    def cache_api_response(self,
                          api_name: str,
                          endpoint: str,
                          response_data: Any,
                          ttl_minutes: int = 15) -> bool:
        """
        Cache API response to reduce duplicate calls.

        Args:
            api_name: API name (e.g., "birdeye", "coingecko")
            endpoint: Endpoint or identifier
            response_data: Response to cache (will be JSON serialized)
            ttl_minutes: How long to cache (default: 15 min = one loop cycle)

        Returns:
            True if cached successfully
        """
        if not self.enabled or not self.config.ENABLE_CACHING:
            return False

        try:
            cache_key = f"{api_name}:{endpoint}"

            return self.store(
                content=json.dumps(response_data),
                scope=MemoryScope.CACHE,
                priority="low",
                metadata={
                    "cache_key": cache_key,
                    "ttl_minutes": ttl_minutes,
                    "api_name": api_name,
                    "endpoint": endpoint
                }
            )
        except Exception as e:
            print(f"[{self.agent_name}] Failed to cache API response: {e}")
            return False

    def get_cached_response(self,
                           api_name: str,
                           endpoint: str,
                           max_age_minutes: int = 15) -> Optional[Any]:
        """
        Retrieve cached API response if available and fresh.

        Args:
            api_name: API name
            endpoint: Endpoint identifier
            max_age_minutes: Maximum age to consider valid

        Returns:
            Cached response data or None if not found/expired
        """
        if not self.enabled or not self.config.ENABLE_CACHING:
            return None

        try:
            cache_key = f"{api_name}:{endpoint}"

            # Get recent cache entries
            memories = self.get_recent(
                scope=MemoryScope.CACHE,
                hours=max_age_minutes / 60.0,
                limit=1
            )

            for memory in memories:
                metadata = memory.get("metadata", {})
                if metadata.get("cache_key") == cache_key:
                    # Parse cached response
                    return json.loads(memory["content"])

            return None

        except Exception as e:
            print(f"[{self.agent_name}] Failed to get cached response: {e}")
            return None

    def handoff(self,
                to_agent: str,
                message: str,
                context: Optional[Dict] = None) -> bool:
        """
        Hand off information to another specific agent.

        Args:
            to_agent: Target agent name
            message: Message/context to pass
            context: Optional structured data

        Returns:
            True if handoff stored successfully
        """
        metadata = context or {}
        metadata["to_agent"] = to_agent
        metadata["from_agent"] = self.agent_name

        return self.store(
            content=f"[HANDOFF to {to_agent}] {message}",
            scope=MemoryScope.GLOBAL,
            priority="high",
            metadata=metadata
        )

    def get_handoffs(self) -> List[Dict]:
        """
        Get messages handed off to this agent.

        Returns:
            List of handoff messages for this agent
        """
        if not self.enabled:
            return []

        try:
            # Get recent global memories
            memories = self.get_recent(
                scope=MemoryScope.GLOBAL,
                hours=24,  # Check last 24 hours
                limit=50
            )

            # Filter for handoffs to this agent
            handoffs = []
            for memory in memories:
                metadata = memory.get("metadata", {})
                if metadata.get("to_agent") == self.agent_name:
                    handoffs.append(memory)

            return handoffs

        except Exception as e:
            print(f"[{self.agent_name}] Failed to get handoffs: {e}")
            return []

    def cleanup_old_memories(self):
        """Remove expired memories based on retention policies."""
        if not self.enabled:
            return

        try:
            for scope, retention in self.config.RETENTION_POLICIES.items():
                cutoff = datetime.now() - retention

                # This would require mem-layer to support deletion by timestamp
                # For now, this is a placeholder for future implementation
                pass

        except Exception as e:
            print(f"[{self.agent_name}] Failed to cleanup memories: {e}")

    def get_stats(self) -> Dict:
        """Get memory usage statistics."""
        if not self.enabled:
            return {"enabled": False}

        try:
            stats = {
                "enabled": True,
                "agent": self.agent_name,
                "accessible_scopes": [
                    s.value for s in self.config.SCOPE_ACCESS.get(
                        self.agent_name,
                        self.config.SCOPE_ACCESS["default"]
                    )
                ],
            }

            return stats

        except Exception as e:
            return {"enabled": True, "error": str(e)}

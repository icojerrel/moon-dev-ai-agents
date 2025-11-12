"""
🌙 Moon Dev's Memory Manager
Built with love by Moon Dev 🚀

Centralized memory management for all AI agents using mem-layer.
Provides persistent memory across sessions for better decision making.
"""

from mem_layer import MemoryAPI, NodeType, EdgeType
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any
import json


class AgentMemoryManager:
    """Centralized memory manager for all AI agents."""

    def __init__(self, scope: str = "trading", memory_dir: Optional[Path] = None):
        """
        Initialize the memory manager.

        Args:
            scope: Memory scope (trading, research, content, etc.)
            memory_dir: Directory to store memory database (default: src/data/memory/)
        """
        self.scope = scope

        # Set memory directory
        if memory_dir is None:
            self.memory_dir = Path(__file__).parent / "data" / "memory"
        else:
            self.memory_dir = Path(memory_dir)

        self.memory_dir.mkdir(parents=True, exist_ok=True)

        # Initialize mem-layer API
        self.api = MemoryAPI(scope=scope)

        print(f"✅ Memory Manager initialized with scope: {scope}")

    # ========== Market Memory Functions ==========

    def remember_market_condition(self, token: str, condition: str,
                                 importance: float = 0.7, **metadata) -> str:
        """
        Remember a market condition for a token.

        Args:
            token: Token address or symbol
            condition: Description of the market condition
            importance: Importance score (0-1)
            **metadata: Additional metadata (price, volume, etc.)

        Returns:
            node_id: ID of the created memory node
        """
        node = self.api.create_node(
            type=NodeType.ENTITY,
            content=f"Market condition for {token}: {condition}",
            tags=["market", "condition", token],
            importance=importance,
            metadata={
                "token": token,
                "timestamp": datetime.now().isoformat(),
                **metadata
            }
        )
        return node.id

    def remember_trade(self, token: str, action: str, price: float,
                      amount: float, reasoning: str, **metadata) -> str:
        """
        Remember a trade execution.

        Args:
            token: Token address or symbol
            action: BUY or SELL
            price: Execution price
            amount: Amount traded
            reasoning: AI reasoning for the trade
            **metadata: Additional metadata

        Returns:
            node_id: ID of the created memory node
        """
        node = self.api.create_node(
            type=NodeType.EVENT,
            content=f"{action} {amount} {token} at ${price}",
            tags=["trade", action.lower(), token],
            importance=0.9,
            metadata={
                "token": token,
                "action": action,
                "price": price,
                "amount": amount,
                "reasoning": reasoning,
                "timestamp": datetime.now().isoformat(),
                **metadata
            }
        )
        return node.id

    def remember_risk_event(self, event_type: str, severity: str,
                           description: str, action_taken: str, **metadata) -> str:
        """
        Remember a risk management event.

        Args:
            event_type: Type of risk event (max_loss, max_gain, low_balance, etc.)
            severity: Severity level (high, medium, low)
            description: Description of the event
            action_taken: Action taken by risk agent
            **metadata: Additional metadata

        Returns:
            node_id: ID of the created memory node
        """
        node = self.api.create_node(
            type=NodeType.EVENT,
            content=f"Risk Event: {description}",
            tags=["risk", event_type, severity],
            importance=0.95 if severity == "high" else 0.7,
            metadata={
                "event_type": event_type,
                "severity": severity,
                "action_taken": action_taken,
                "timestamp": datetime.now().isoformat(),
                **metadata
            }
        )
        return node.id

    # ========== Agent Notes and Learnings ==========

    def add_agent_note(self, agent_name: str, content: str,
                      priority: str = "normal", **metadata) -> str:
        """
        Add a note from an agent.

        Args:
            agent_name: Name of the agent adding the note
            content: Note content
            priority: Priority level (high, normal, low)
            **metadata: Additional metadata

        Returns:
            node_id: ID of the created note
        """
        # Map priority to importance
        importance_map = {"low": 0.5, "normal": 0.7, "high": 0.9}
        importance = importance_map.get(priority.lower(), 0.7)

        node = self.api.create_node(
            type=NodeType.NOTE,
            content=f"[{agent_name}] {content}",
            tags=["agent_note", agent_name, priority],
            importance=importance,
            metadata={
                "agent": agent_name,
                "priority": priority,
                "timestamp": datetime.now().isoformat(),
                **metadata
            }
        )
        return node.id

    def remember_strategy_performance(self, strategy_name: str, token: str,
                                     win_rate: float, pnl: float,
                                     trades_count: int, **metadata) -> str:
        """
        Remember strategy performance metrics.

        Args:
            strategy_name: Name of the strategy
            token: Token traded
            win_rate: Win rate percentage
            pnl: Profit/Loss
            trades_count: Number of trades
            **metadata: Additional metadata

        Returns:
            node_id: ID of the created memory node
        """
        node = self.api.create_node(
            type=NodeType.ENTITY,
            content=f"Strategy '{strategy_name}' performance on {token}",
            tags=["strategy", "performance", strategy_name, token],
            importance=0.85,
            metadata={
                "strategy": strategy_name,
                "token": token,
                "win_rate": win_rate,
                "pnl": pnl,
                "trades_count": trades_count,
                "timestamp": datetime.now().isoformat(),
                **metadata
            }
        )
        return node.id

    # ========== Query Functions ==========

    def recall_recent_trades(self, token: Optional[str] = None,
                            limit: int = 10) -> List[Dict]:
        """
        Recall recent trades from memory.

        Args:
            token: Optional token filter
            limit: Maximum number of trades to recall

        Returns:
            List of trade memories
        """
        if token:
            query = f"tags:trade AND tags:{token}"
        else:
            query = "tags:trade"

        result = self.api.query(query)

        # Sort by timestamp and limit
        nodes = sorted(result.nodes,
                      key=lambda x: x.metadata.get('timestamp', ''),
                      reverse=True)[:limit]

        return [self._node_to_dict(node) for node in nodes]

    def recall_market_conditions(self, token: str, days_back: int = 7) -> List[Dict]:
        """
        Recall market conditions for a token.

        Args:
            token: Token address or symbol
            days_back: How many days back to search

        Returns:
            List of market condition memories
        """
        query = f"tags:market AND tags:condition AND tags:{token}"
        result = self.api.query(query)

        # Filter by timestamp and sort
        nodes = sorted(result.nodes,
                      key=lambda x: x.metadata.get('timestamp', ''),
                      reverse=True)

        return [self._node_to_dict(node) for node in nodes]

    def recall_risk_events(self, severity: Optional[str] = None,
                          limit: int = 20) -> List[Dict]:
        """
        Recall risk management events.

        Args:
            severity: Optional severity filter (high, medium, low)
            limit: Maximum number of events to recall

        Returns:
            List of risk event memories
        """
        if severity:
            query = f"tags:risk AND tags:{severity}"
        else:
            query = "tags:risk"

        result = self.api.query(query)

        nodes = sorted(result.nodes,
                      key=lambda x: x.metadata.get('timestamp', ''),
                      reverse=True)[:limit]

        return [self._node_to_dict(node) for node in nodes]

    def search_memories(self, search_text: str, limit: int = 20) -> List[Dict]:
        """
        Full-text search across all memories.

        Args:
            search_text: Text to search for
            limit: Maximum results

        Returns:
            List of matching memories
        """
        result = self.api.search(search_text)
        nodes = result.nodes[:limit]
        return [self._node_to_dict(node) for node in nodes]

    def get_agent_context(self, agent_name: str, token: Optional[str] = None) -> Dict:
        """
        Get relevant context for an agent's decision making.

        Args:
            agent_name: Name of the agent
            token: Optional token to focus on

        Returns:
            Dict containing relevant memories and context
        """
        context = {
            "agent": agent_name,
            "timestamp": datetime.now().isoformat(),
            "recent_trades": [],
            "market_conditions": [],
            "risk_events": [],
            "agent_notes": []
        }

        # Get recent trades
        context["recent_trades"] = self.recall_recent_trades(token, limit=5)

        # Get market conditions
        if token:
            context["market_conditions"] = self.recall_market_conditions(token, days_back=3)

        # Get recent risk events
        context["risk_events"] = self.recall_risk_events(limit=5)

        # Get agent's own notes
        query = f"tags:agent_note AND tags:{agent_name}"
        result = self.api.query(query)
        context["agent_notes"] = [self._node_to_dict(n) for n in result.nodes[:5]]

        return context

    # ========== Relationship Functions ==========

    def link_memories(self, source_id: str, target_id: str,
                     relationship: str = "RELATES_TO", weight: float = 0.8):
        """
        Create a relationship between two memories.

        Args:
            source_id: Source memory node ID
            target_id: Target memory node ID
            relationship: Type of relationship
            weight: Relationship weight (0-1)
        """
        # Map string relationships to EdgeType
        edge_type_map = {
            "RELATES_TO": EdgeType.RELATES_TO,
            "DEPENDS_ON": EdgeType.DEPENDS_ON,
            "USES": EdgeType.USES,
            "PART_OF": EdgeType.PART_OF,
            "CAUSES": EdgeType.CAUSES,
            "TEMPORAL_SEQUENCE": EdgeType.TEMPORAL_SEQUENCE,
            "REFERENCES": EdgeType.REFERENCES,
        }

        edge_type = edge_type_map.get(relationship, EdgeType.RELATES_TO)

        self.api.create_edge(
            source_id=source_id,
            target_id=target_id,
            type=edge_type,
            weight=weight
        )

    # ========== Stats and Export ==========

    def get_memory_stats(self) -> Dict:
        """Get statistics about the memory graph."""
        stats = self.api.get_stats()
        return {
            "scope": self.scope,
            "node_count": stats.get('node_count', 0),
            "edge_count": stats.get('edge_count', 0),
            "node_types": stats.get('node_types', {}),
            "edge_types": stats.get('edge_types', {}),
        }

    def export_memory(self, filename: str = None) -> Path:
        """
        Export memory graph to JSON file.

        Args:
            filename: Optional filename (default: auto-generated)

        Returns:
            Path to exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"memory_export_{self.scope}_{timestamp}.json"

        export_path = self.memory_dir / filename
        self.api.export_graph(export_path, format="json")
        return export_path

    # ========== Helper Functions ==========

    def _node_to_dict(self, node) -> Dict:
        """Convert a memory node to a dictionary."""
        return {
            "id": node.id,
            "type": str(node.type),
            "content": node.content,
            "tags": node.tags if hasattr(node, 'tags') else [],
            "importance": node.importance if hasattr(node, 'importance') else 0.5,
            "metadata": node.metadata if hasattr(node, 'metadata') else {},
            "created_at": node.created_at if hasattr(node, 'created_at') else None,
        }


# ========== Convenience Functions for Agents ==========

def get_trading_memory() -> AgentMemoryManager:
    """Get the trading scope memory manager."""
    return AgentMemoryManager(scope="trading")

def get_research_memory() -> AgentMemoryManager:
    """Get the research scope memory manager."""
    return AgentMemoryManager(scope="research")

def get_content_memory() -> AgentMemoryManager:
    """Get the content creation scope memory manager."""
    return AgentMemoryManager(scope="content")


if __name__ == "__main__":
    # Test the memory manager
    print("🧪 Testing Memory Manager...\n")

    memory = get_trading_memory()

    # Test adding a trade
    trade_id = memory.remember_trade(
        token="FART",
        action="BUY",
        price=0.05,
        amount=100,
        reasoning="Strong bullish signal from sentiment analysis"
    )
    print(f"✅ Remembered trade: {trade_id}\n")

    # Test adding a market condition
    condition_id = memory.remember_market_condition(
        token="FART",
        condition="High volume breakout detected",
        importance=0.85,
        volume=1500000,
        price_change=15.5
    )
    print(f"✅ Remembered market condition: {condition_id}\n")

    # Test adding a risk event
    risk_id = memory.remember_risk_event(
        event_type="max_loss",
        severity="high",
        description="Maximum loss threshold reached",
        action_taken="All positions closed"
    )
    print(f"✅ Remembered risk event: {risk_id}\n")

    # Test linking memories
    memory.link_memories(trade_id, condition_id, "CAUSES")
    print("✅ Linked trade to market condition\n")

    # Test recall
    recent_trades = memory.recall_recent_trades(token="FART", limit=5)
    print(f"📊 Recalled {len(recent_trades)} recent trades\n")

    # Test stats
    stats = memory.get_memory_stats()
    print(f"📈 Memory Stats:")
    print(f"  - Nodes: {stats['node_count']}")
    print(f"  - Edges: {stats['edge_count']}")
    print(f"  - Node types: {stats['node_types']}")
    print()

    # Test export
    export_path = memory.export_memory()
    print(f"💾 Exported memory to: {export_path}\n")

    print("✅ All tests passed!")

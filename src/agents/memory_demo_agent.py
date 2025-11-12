"""
🌙 Moon Dev's Memory Demo Agent
Built with love by Moon Dev 🚀

Demonstrates how to integrate mem-layer memory into any agent.
This is a reference implementation that other agents can follow.
"""

import sys
from pathlib import Path
from termcolor import colored, cprint
from datetime import datetime

# Add project root to path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.memory_manager import get_trading_memory
from src.config import MEMORY_ENABLED, MEMORY_RECALL_LIMIT


class MemoryDemoAgent:
    """Demo agent showing memory integration patterns."""

    def __init__(self, use_memory: bool = True):
        """Initialize the demo agent."""
        self.name = "MemoryDemoAgent"
        self.use_memory = use_memory and MEMORY_ENABLED

        # Initialize memory if enabled
        if self.use_memory:
            self.memory = get_trading_memory()
            cprint(f"✅ {self.name} initialized with memory enabled", "green")
        else:
            self.memory = None
            cprint(f"⚠️  {self.name} initialized WITHOUT memory", "yellow")

    def analyze_market(self, token: str, price: float, volume: int):
        """
        Analyze market and demonstrate memory usage.

        This shows the pattern that other agents should follow:
        1. Recall relevant memories
        2. Make decision
        3. Store new memories
        4. Link related memories
        """
        cprint(f"\n{'='*60}", "cyan")
        cprint(f"🔍 Analyzing {token} at ${price}", "cyan", attrs=["bold"])
        cprint(f"{'='*60}", "cyan")

        # ========== STEP 1: Recall Past Memories ==========
        if self.use_memory:
            cprint("\n📚 Recalling past memories...", "yellow")

            # Get agent context (all relevant memories)
            context = self.memory.get_agent_context(
                agent_name=self.name,
                token=token
            )

            # Display recent trades
            if context["recent_trades"]:
                cprint(f"\n  Recent trades for {token}:", "white")
                for trade in context["recent_trades"][:3]:
                    action = trade["metadata"].get("action", "UNKNOWN")
                    trade_price = trade["metadata"].get("price", 0)
                    color = "green" if action == "BUY" else "red"
                    print(f"    - {colored(action, color)} at ${trade_price}")
            else:
                print("    - No previous trades found")

            # Display market conditions
            if context["market_conditions"]:
                cprint(f"\n  Past market conditions:", "white")
                for condition in context["market_conditions"][:2]:
                    print(f"    - {condition['content']}")

            # Display risk events
            if context["risk_events"]:
                cprint(f"\n  Recent risk events:", "white")
                for event in context["risk_events"][:2]:
                    severity = event["metadata"].get("severity", "unknown")
                    color = "red" if severity == "high" else "yellow"
                    print(f"    - {colored(event['content'], color)}")

        # ========== STEP 2: Make Trading Decision ==========
        cprint(f"\n🤖 Making trading decision...", "cyan")

        # Simulate analysis (in real agent, this would use LLM)
        decision = "BUY"
        confidence = 0.75
        reasoning = f"Price ${price} showing bullish signals with high volume"

        cprint(f"  Decision: {colored(decision, 'green')}", "white")
        cprint(f"  Confidence: {confidence*100}%", "white")
        cprint(f"  Reasoning: {reasoning}", "white")

        # ========== STEP 3: Store New Memories ==========
        if self.use_memory:
            cprint(f"\n💾 Storing memories...", "yellow")

            # Remember the market condition
            condition_id = self.memory.remember_market_condition(
                token=token,
                condition=f"High volume ({volume:,}) with bullish momentum",
                importance=0.8,
                price=price,
                volume=volume,
                trend="bullish"
            )
            print(f"  ✅ Stored market condition (ID: {condition_id[:8]}...)")

            # Remember the trade decision
            trade_id = self.memory.remember_trade(
                token=token,
                action=decision,
                price=price,
                amount=100,  # Example amount
                reasoning=reasoning,
                confidence=confidence
            )
            print(f"  ✅ Stored trade decision (ID: {trade_id[:8]}...)")

            # Add an agent note
            note_id = self.memory.add_agent_note(
                agent_name=self.name,
                content=f"Executed {decision} on {token} with {confidence*100}% confidence",
                priority="high"
            )
            print(f"  ✅ Added agent note (ID: {note_id[:8]}...)")

            # ========== STEP 4: Link Related Memories ==========
            cprint(f"\n🔗 Linking related memories...", "yellow")

            # Link trade to market condition (condition causes trade)
            self.memory.link_memories(
                source_id=condition_id,
                target_id=trade_id,
                relationship="CAUSES",
                weight=0.9
            )
            print(f"  ✅ Linked trade to market condition")

        # ========== STEP 5: Display Memory Stats ==========
        if self.use_memory:
            cprint(f"\n📊 Memory Statistics:", "cyan")
            stats = self.memory.get_memory_stats()
            print(f"  Total memories: {stats['node_count']}")
            print(f"  Relationships: {stats['edge_count']}")
            print(f"  Memory types: {stats['node_types']}")

    def simulate_risk_event(self, event_type: str, severity: str):
        """Simulate a risk event and demonstrate risk memory storage."""
        cprint(f"\n{'='*60}", "red")
        cprint(f"⚠️  Risk Event: {event_type}", "red", attrs=["bold"])
        cprint(f"{'='*60}", "red")

        if self.use_memory:
            # Store risk event
            risk_id = self.memory.remember_risk_event(
                event_type=event_type,
                severity=severity,
                description=f"{event_type} threshold reached",
                action_taken="Positions evaluated for closure",
                portfolio_value=10000,
                loss_amount=500
            )

            cprint(f"\n💾 Risk event stored (ID: {risk_id[:8]}...)", "yellow")

            # Recall all high severity risk events
            cprint(f"\n📚 Recalling all high severity risk events...", "yellow")
            risk_events = self.memory.recall_risk_events(severity="high", limit=5)

            if risk_events:
                for event in risk_events:
                    event_data = event["metadata"]
                    print(f"  - {event['content']}")
                    print(f"    Action: {event_data.get('action_taken', 'N/A')}")
                    print(f"    Time: {event_data.get('timestamp', 'N/A')}")
            else:
                print("  - No high severity events found")

    def demonstrate_memory_search(self):
        """Demonstrate full-text search across all memories."""
        cprint(f"\n{'='*60}", "magenta")
        cprint(f"🔍 Memory Search Demo", "magenta", attrs=["bold"])
        cprint(f"{'='*60}", "magenta")

        if not self.use_memory:
            cprint("Memory not enabled!", "red")
            return

        # Search for specific terms
        search_terms = ["bullish", "risk", "BUY"]

        for term in search_terms:
            cprint(f"\n🔎 Searching for: '{term}'", "cyan")
            results = self.memory.search_memories(term, limit=3)

            if results:
                for i, result in enumerate(results, 1):
                    print(f"  {i}. {result['content'][:60]}...")
                    print(f"     Tags: {', '.join(result['tags'][:3])}")
            else:
                print(f"  - No results found")

    def export_memory_report(self):
        """Export memory to JSON for analysis."""
        if not self.use_memory:
            cprint("\n⚠️  Memory not enabled, cannot export", "yellow")
            return

        cprint(f"\n{'='*60}", "green")
        cprint(f"💾 Exporting Memory", "green", attrs=["bold"])
        cprint(f"{'='*60}", "green")

        export_path = self.memory.export_memory()
        cprint(f"\n✅ Memory exported to: {export_path}", "green")
        cprint(f"📁 File size: {export_path.stat().st_size:,} bytes", "white")


def main():
    """Run the memory demo agent."""
    cprint("\n" + "="*60, "cyan", attrs=["bold"])
    cprint("🌙 Moon Dev's Memory Demo Agent 🌙", "cyan", attrs=["bold"])
    cprint("="*60 + "\n", "cyan", attrs=["bold"])

    # Initialize agent with memory
    agent = MemoryDemoAgent(use_memory=True)

    # Demo 1: Analyze market with memory
    agent.analyze_market(
        token="FART",
        price=0.052,
        volume=1500000
    )

    # Demo 2: Simulate another trade
    agent.analyze_market(
        token="AI16Z",
        price=1.25,
        volume=850000
    )

    # Demo 3: Simulate a risk event
    agent.simulate_risk_event(
        event_type="max_loss",
        severity="high"
    )

    # Demo 4: Demonstrate search
    agent.demonstrate_memory_search()

    # Demo 5: Export memory
    agent.export_memory_report()

    cprint("\n" + "="*60, "green", attrs=["bold"])
    cprint("✅ Demo Complete!", "green", attrs=["bold"])
    cprint("="*60 + "\n", "green", attrs=["bold"])

    cprint("📖 Integration Guide for Other Agents:", "cyan", attrs=["bold"])
    print("""
1. Import memory manager:
   from src.memory_manager import get_trading_memory

2. Initialize in __init__:
   self.memory = get_trading_memory()

3. Recall context before decisions:
   context = self.memory.get_agent_context(self.name, token)

4. Store important decisions:
   self.memory.remember_trade(token, action, price, amount, reasoning)

5. Link related memories:
   self.memory.link_memories(source_id, target_id, "CAUSED_BY")

See src/agents/memory_demo_agent.py for full examples!
    """)


if __name__ == "__main__":
    main()

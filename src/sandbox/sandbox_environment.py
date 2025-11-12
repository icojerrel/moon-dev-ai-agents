"""
Sandbox Environment for AI Trading Agents with MemoriSDK

Simulates realistic trading scenarios to rapidly populate memory databases
and test cross-agent intelligence without risking real capital.

Author: Moon Dev AI Trading System
Date: 2025-11-12
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
from dataclasses import dataclass, asdict
import time

# Add project root to path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from src.agents.memory_analytics import MemoryAnalytics


@dataclass
class MarketCandle:
    """Represents a market data candle"""
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float

    def to_dict(self):
        return asdict(self)


@dataclass
class TradingDecision:
    """Represents an agent's trading decision"""
    timestamp: str
    agent: str
    token: str
    action: str  # BUY, SELL, HOLD
    price: float
    confidence: int
    reasoning: str
    memory_context: Optional[str] = None

    def to_dict(self):
        return asdict(self)


@dataclass
class SandboxMetrics:
    """Track sandbox performance metrics"""
    total_decisions: int = 0
    buy_decisions: int = 0
    sell_decisions: int = 0
    hold_decisions: int = 0
    memories_created: int = 0
    cross_agent_queries: int = 0
    simulation_duration_seconds: float = 0.0

    def to_dict(self):
        return asdict(self)


class SandboxEnvironment:
    """
    Sandbox environment for testing AI trading agents with memory.

    Features:
    - Load historical market data
    - Simulate agent decisions
    - Populate memory databases
    - Test cross-agent intelligence
    - Generate analytics reports
    """

    def __init__(
        self,
        historical_data_path: Optional[str] = None,
        agents: Optional[List] = None,
        speed_multiplier: int = 1
    ):
        """
        Initialize sandbox environment.

        Args:
            historical_data_path: Path to CSV with OHLCV data
            agents: List of agent instances to test
            speed_multiplier: Speed up simulation (1 = real-time)
        """
        self.historical_data_path = historical_data_path or self._find_historical_data()
        self.agents = agents or []
        self.speed_multiplier = speed_multiplier

        # Tracking
        self.current_index = 0
        self.decisions: List[TradingDecision] = []
        self.metrics = SandboxMetrics()
        self.start_time = None

        # Memory analytics
        self.analytics = MemoryAnalytics()

        print(f"🧪 Sandbox Environment Initialized")
        print(f"   Data: {self.historical_data_path}")
        print(f"   Agents: {len(self.agents)}")
        print(f"   Speed: {speed_multiplier}x")

    def _find_historical_data(self) -> str:
        """Find historical data file in project"""
        possible_paths = [
            "src/data/rbi/BTC-USD-15m.csv",
            "src/data/BTC-USD-15m.csv",
            "data/BTC-USD-15m.csv",
        ]

        for path in possible_paths:
            full_path = Path(project_root) / path
            if full_path.exists():
                return str(full_path)

        raise FileNotFoundError(
            "No historical data found. Please provide path to OHLCV CSV file."
        )

    def load_historical_data(self) -> List[MarketCandle]:
        """Load historical market data from CSV"""
        import csv

        candles = []

        try:
            with open(self.historical_data_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    candle = MarketCandle(
                        timestamp=row.get('timestamp', row.get('date', '')),
                        open=float(row.get('open', 0)),
                        high=float(row.get('high', 0)),
                        low=float(row.get('low', 0)),
                        close=float(row.get('close', 0)),
                        volume=float(row.get('volume', 0))
                    )
                    candles.append(candle)

            print(f"✅ Loaded {len(candles)} historical candles")
            return candles

        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return []

    def simulate_agent_decision(
        self,
        agent,
        candle: MarketCandle,
        market_context: Dict
    ) -> TradingDecision:
        """
        Simulate an agent making a trading decision.

        This is a simplified simulation - in production, agents would
        use their full decision-making logic.
        """
        # Simplified decision logic for sandbox
        # In reality, agents would use their actual analyze() methods

        agent_name = agent.__class__.__name__

        # Simulate different agent behaviors
        if "trading" in agent_name.lower():
            # Trading agent: More decisive
            if candle.close > candle.open:
                action = "BUY" if candle.volume > 1000 else "HOLD"
                confidence = 75
            else:
                action = "SELL" if candle.volume > 1000 else "HOLD"
                confidence = 70
            reasoning = f"Price {'rising' if action == 'BUY' else 'falling'}, volume: {candle.volume:.0f}"

        elif "sentiment" in agent_name.lower():
            # Sentiment agent: Analyzes market mood
            action = "BUY" if candle.close > candle.open else "SELL"
            confidence = 65
            reasoning = f"Market sentiment {'bullish' if action == 'BUY' else 'bearish'}"

        elif "whale" in agent_name.lower():
            # Whale agent: Detects large movements
            if candle.volume > 2000:
                action = "BUY" if candle.close > candle.open else "SELL"
                confidence = 80
                reasoning = f"Large volume detected: {candle.volume:.0f}"
            else:
                action = "HOLD"
                confidence = 50
                reasoning = "No significant whale activity"

        else:
            # Default behavior
            action = "HOLD"
            confidence = 50
            reasoning = "Default hold position"

        decision = TradingDecision(
            timestamp=candle.timestamp,
            agent=agent_name,
            token="BTC",
            action=action,
            price=candle.close,
            confidence=confidence,
            reasoning=reasoning,
            memory_context=None  # Would be populated by agent's memory
        )

        # Track metrics
        self.metrics.total_decisions += 1
        if action == "BUY":
            self.metrics.buy_decisions += 1
        elif action == "SELL":
            self.metrics.sell_decisions += 1
        else:
            self.metrics.hold_decisions += 1

        return decision

    def simulate_candle(self, candle: MarketCandle):
        """Process one market candle through all agents"""
        market_context = {
            'current_price': candle.close,
            'volume': candle.volume,
            'trend': 'up' if candle.close > candle.open else 'down'
        }

        # Each agent analyzes the candle
        for agent in self.agents:
            decision = self.simulate_agent_decision(agent, candle, market_context)
            self.decisions.append(decision)

            # In production, memory would be stored here
            # agent.memori.store(decision)

    def run_simulation(
        self,
        num_candles: Optional[int] = None,
        days: Optional[int] = None,
        verbose: bool = True
    ) -> SandboxMetrics:
        """
        Run sandbox simulation.

        Args:
            num_candles: Number of candles to simulate (overrides days)
            days: Number of days to simulate (96 candles per day for 15min)
            verbose: Print progress updates

        Returns:
            SandboxMetrics with results
        """
        self.start_time = time.time()

        # Load data
        candles = self.load_historical_data()
        if not candles:
            print("❌ No data to simulate")
            return self.metrics

        # Determine how many candles to process
        if num_candles:
            total_candles = min(num_candles, len(candles))
        elif days:
            total_candles = min(days * 96, len(candles))  # 96 x 15min = 24h
        else:
            total_candles = len(candles)

        if verbose:
            print(f"\n🚀 Starting simulation: {total_candles} candles")
            print(f"   Agents: {len(self.agents)}")
            print(f"   Estimated decisions: {total_candles * len(self.agents)}")

        # Simulate each candle
        for i, candle in enumerate(candles[:total_candles]):
            self.simulate_candle(candle)

            # Progress updates
            if verbose and (i + 1) % 100 == 0:
                progress = ((i + 1) / total_candles) * 100
                print(f"   Progress: {progress:.1f}% ({i + 1}/{total_candles})")

        # Calculate duration
        self.metrics.simulation_duration_seconds = time.time() - self.start_time

        if verbose:
            self._print_summary()

        return self.metrics

    def _print_summary(self):
        """Print simulation summary"""
        print(f"\n{'='*80}")
        print(f"  ✅ SIMULATION COMPLETE")
        print(f"{'='*80}\n")

        print(f"📊 Metrics:")
        print(f"   Total Decisions: {self.metrics.total_decisions}")
        print(f"   BUY: {self.metrics.buy_decisions} ({self.metrics.buy_decisions/self.metrics.total_decisions*100:.1f}%)")
        print(f"   SELL: {self.metrics.sell_decisions} ({self.metrics.sell_decisions/self.metrics.total_decisions*100:.1f}%)")
        print(f"   HOLD: {self.metrics.hold_decisions} ({self.metrics.hold_decisions/self.metrics.total_decisions*100:.1f}%)")
        print(f"   Duration: {self.metrics.simulation_duration_seconds:.2f} seconds")
        print(f"   Speed: {self.metrics.total_decisions / self.metrics.simulation_duration_seconds:.0f} decisions/sec")

    def get_decisions_by_agent(self, agent_name: str) -> List[TradingDecision]:
        """Get all decisions made by specific agent"""
        return [d for d in self.decisions if agent_name in d.agent]

    def get_decisions_by_action(self, action: str) -> List[TradingDecision]:
        """Get all decisions of specific type (BUY, SELL, HOLD)"""
        return [d for d in self.decisions if d.action == action]

    def export_results(self, output_path: str):
        """Export simulation results to JSON"""
        results = {
            'metrics': self.metrics.to_dict(),
            'decisions': [d.to_dict() for d in self.decisions],
            'timestamp': datetime.now().isoformat()
        }

        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"📁 Results exported to: {output_path}")

    def get_memory_stats(self) -> Dict:
        """Get current memory database statistics"""
        return self.analytics.get_all_stats()


class MockAgent:
    """Mock agent for sandbox testing when real agents aren't available"""

    def __init__(self, name: str, behavior: str = "neutral"):
        self.__class__.__name__ = name
        self.behavior = behavior
        self.memori = None  # Mock memory


# Convenience function
def create_sandbox(
    data_path: Optional[str] = None,
    agent_types: Optional[List[str]] = None
) -> SandboxEnvironment:
    """
    Create a sandbox environment with mock agents.

    Args:
        data_path: Path to historical data CSV
        agent_types: List of agent types to simulate

    Returns:
        Configured SandboxEnvironment
    """
    agent_types = agent_types or ['TradingAgent', 'SentimentAgent', 'WhaleAgent']

    agents = [MockAgent(name) for name in agent_types]

    return SandboxEnvironment(
        historical_data_path=data_path,
        agents=agents,
        speed_multiplier=1
    )


if __name__ == "__main__":
    # Quick test
    print("\n🧪 Sandbox Environment - Quick Test\n")

    try:
        sandbox = create_sandbox()
        metrics = sandbox.run_simulation(days=1, verbose=True)

        print("\n💾 Memory Database Status:")
        stats = sandbox.get_memory_stats()
        for db_name, info in stats.items():
            print(f"   {db_name}: {info.get('total_memories', 0)} memories")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

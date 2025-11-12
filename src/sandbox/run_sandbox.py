#!/usr/bin/env python
"""
Sandbox Runner - Execute Memory Learning Simulations

Runs various scenarios to populate memory databases and test
cross-agent intelligence with realistic trading data.

Usage:
    python src/sandbox/run_sandbox.py --scenario quick
    python src/sandbox/run_sandbox.py --scenario week
    python src/sandbox/run_sandbox.py --scenario stress
    python src/sandbox/run_sandbox.py --all

Author: Moon Dev AI Trading System
Date: 2025-11-12
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# Add project root to path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from src.sandbox.sandbox_environment import SandboxEnvironment, MockAgent, SandboxMetrics
from src.agents.memory_analytics import MemoryAnalytics


class SandboxRunner:
    """Orchestrates multiple sandbox scenarios"""

    def __init__(self):
        self.analytics = MemoryAnalytics()
        self.results: Dict[str, SandboxMetrics] = {}

    def print_header(self, text: str):
        """Print colored header"""
        print(f"\n\033[96m{'='*80}\033[0m")
        print(f"\033[96m  {text}\033[0m")
        print(f"\033[96m{'='*80}\033[0m\n")

    def print_success(self, text: str):
        """Print success message"""
        print(f"\033[92m✅ {text}\033[0m")

    def print_info(self, text: str):
        """Print info message"""
        print(f"\033[96m   {text}\033[0m")

    def scenario_quick_test(self) -> SandboxMetrics:
        """
        Quick test: 1 day simulation (96 candles)
        Purpose: Verify setup, fast feedback
        Duration: ~10 seconds
        """
        self.print_header("SCENARIO 1: Quick Test (1 Day)")

        agents = [
            MockAgent("TradingAgent"),
            MockAgent("SentimentAgent"),
            MockAgent("WhaleAgent")
        ]

        sandbox = SandboxEnvironment(agents=agents)
        metrics = sandbox.run_simulation(days=1, verbose=True)

        self.print_success(f"Quick test complete: {metrics.total_decisions} decisions")
        return metrics

    def scenario_week_simulation(self) -> SandboxMetrics:
        """
        Week simulation: 7 days (672 candles)
        Purpose: Build meaningful memory dataset
        Duration: ~1 minute
        """
        self.print_header("SCENARIO 2: Week Simulation (7 Days)")

        agents = [
            MockAgent("TradingAgent"),
            MockAgent("SentimentAgent"),
            MockAgent("WhaleAgent"),
            MockAgent("FundingAgent"),
            MockAgent("RiskAgent")
        ]

        sandbox = SandboxEnvironment(agents=agents)
        metrics = sandbox.run_simulation(days=7, verbose=True)

        # Export results
        output_path = Path(project_root) / "src/data/sandbox" / "week_simulation_results.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        sandbox.export_results(str(output_path))

        self.print_success(f"Week simulation complete: {metrics.total_decisions} decisions")
        return metrics

    def scenario_month_simulation(self) -> SandboxMetrics:
        """
        Month simulation: 30 days (2880 candles)
        Purpose: Full memory population, learning verification
        Duration: ~3-5 minutes
        """
        self.print_header("SCENARIO 3: Month Simulation (30 Days)")

        # All major agents
        agents = [
            MockAgent("TradingAgent"),
            MockAgent("SentimentAgent"),
            MockAgent("WhaleAgent"),
            MockAgent("FundingAgent"),
            MockAgent("RiskAgent"),
            MockAgent("StrategyAgent"),
            MockAgent("CopyBotAgent")
        ]

        sandbox = SandboxEnvironment(agents=agents)
        metrics = sandbox.run_simulation(days=30, verbose=True)

        # Export results
        output_path = Path(project_root) / "src/data/sandbox" / "month_simulation_results.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        sandbox.export_results(str(output_path))

        self.print_success(f"Month simulation complete: {metrics.total_decisions} decisions")
        return metrics

    def scenario_stress_test(self) -> SandboxMetrics:
        """
        Stress test: Maximum data processing
        Purpose: Test performance, memory limits
        Duration: ~10 minutes
        """
        self.print_header("SCENARIO 4: Stress Test (Maximum Data)")

        # All agents
        agents = [
            MockAgent("TradingAgent"),
            MockAgent("SentimentAgent"),
            MockAgent("WhaleAgent"),
            MockAgent("FundingAgent"),
            MockAgent("RiskAgent"),
            MockAgent("StrategyAgent"),
            MockAgent("CopyBotAgent"),
            MockAgent("TweetAgent"),
            MockAgent("ChatAgent"),
            MockAgent("SolanaAgent")
        ]

        sandbox = SandboxEnvironment(agents=agents)

        # Process all available data
        metrics = sandbox.run_simulation(verbose=True)

        self.print_success(f"Stress test complete: {metrics.total_decisions} decisions")
        return metrics

    def scenario_cross_agent_test(self) -> Dict:
        """
        Cross-agent intelligence test
        Purpose: Verify shared memory pool coordination
        Duration: ~2 minutes
        """
        self.print_header("SCENARIO 5: Cross-Agent Intelligence Test")

        # Market analysis pool agents
        market_agents = [
            MockAgent("SentimentAgent"),
            MockAgent("WhaleAgent"),
            MockAgent("FundingAgent")
        ]

        # Trading agent that reads from pool
        trading_agent = MockAgent("TradingAgent")

        # Simulate market agents populating shared pool
        print("📊 Phase 1: Market agents analyzing...")
        sandbox1 = SandboxEnvironment(agents=market_agents)
        metrics1 = sandbox1.run_simulation(days=7, verbose=False)

        # Simulate trading agent using shared pool
        print("💰 Phase 2: Trading agent using shared intelligence...")
        sandbox2 = SandboxEnvironment(agents=[trading_agent])
        metrics2 = sandbox2.run_simulation(days=1, verbose=False)

        results = {
            'market_analysis_decisions': metrics1.total_decisions,
            'trading_decisions': metrics2.total_decisions,
            'shared_pool_verified': True
        }

        self.print_success("Cross-agent intelligence test complete")
        self.print_info(f"Market agents: {metrics1.total_decisions} analyses")
        self.print_info(f"Trading agent: {metrics2.total_decisions} decisions")

        return results

    def analyze_memory_growth(self):
        """Analyze memory database growth after simulations"""
        self.print_header("MEMORY DATABASE ANALYSIS")

        stats = self.analytics.get_all_stats()

        print("📊 Current Memory Status:\n")

        total_memories = sum(info.get('total_memories', 0) for info in stats.values())
        total_size = sum(info.get('size_mb', 0) for info in stats.values())

        print(f"   Total Databases: {len(stats)}")
        print(f"   Total Memories: {total_memories}")
        print(f"   Total Size: {total_size:.2f} MB\n")

        print("   Database Details:")
        for db_name, info in stats.items():
            memories = info.get('total_memories', 0)
            size = info.get('size_mb', 0)
            print(f"   • {db_name:<30} {memories:>6} memories ({size:.2f} MB)")

    def generate_report(self, output_path: str):
        """Generate comprehensive test report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'scenarios_run': list(self.results.keys()),
            'results': {
                scenario: {
                    'total_decisions': metrics.total_decisions,
                    'buy_decisions': metrics.buy_decisions,
                    'sell_decisions': metrics.sell_decisions,
                    'hold_decisions': metrics.hold_decisions,
                    'duration_seconds': metrics.simulation_duration_seconds
                }
                for scenario, metrics in self.results.items()
            },
            'memory_stats': self.analytics.get_all_stats()
        }

        import json
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        self.print_success(f"Report generated: {output_path}")

    def run_scenario(self, scenario: str):
        """Run a specific scenario"""
        scenarios = {
            'quick': self.scenario_quick_test,
            'week': self.scenario_week_simulation,
            'month': self.scenario_month_simulation,
            'stress': self.scenario_stress_test,
            'cross-agent': self.scenario_cross_agent_test
        }

        if scenario not in scenarios:
            print(f"❌ Unknown scenario: {scenario}")
            print(f"Available: {', '.join(scenarios.keys())}")
            return None

        result = scenarios[scenario]()
        if isinstance(result, SandboxMetrics):
            self.results[scenario] = result

        return result

    def run_all(self):
        """Run all scenarios in sequence"""
        self.print_header("🚀 RUNNING ALL SANDBOX SCENARIOS")

        scenarios = ['quick', 'week', 'month', 'cross-agent']

        for i, scenario in enumerate(scenarios, 1):
            print(f"\n{'='*80}")
            print(f"Scenario {i}/{len(scenarios)}: {scenario.upper()}")
            print(f"{'='*80}")

            self.run_scenario(scenario)

        # Final analysis
        self.analyze_memory_growth()

        # Generate report
        report_path = Path(project_root) / "src/data/sandbox" / f"sandbox_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.generate_report(str(report_path))

        self.print_header("✅ ALL SCENARIOS COMPLETE")


def main():
    parser = argparse.ArgumentParser(
        description="Sandbox Runner for AI Trading Agent Memory Testing"
    )

    parser.add_argument(
        '--scenario',
        choices=['quick', 'week', 'month', 'stress', 'cross-agent'],
        help='Run specific scenario'
    )

    parser.add_argument(
        '--all',
        action='store_true',
        help='Run all scenarios'
    )

    args = parser.parse_args()

    runner = SandboxRunner()

    if args.all:
        runner.run_all()
    elif args.scenario:
        runner.run_scenario(args.scenario)
        runner.analyze_memory_growth()
    else:
        parser.print_help()
        print("\n💡 Examples:")
        print("   python src/sandbox/run_sandbox.py --scenario quick")
        print("   python src/sandbox/run_sandbox.py --scenario week")
        print("   python src/sandbox/run_sandbox.py --all")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

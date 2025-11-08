"""
🌙 Moon Dev's 24-Hour Test Results Analyzer
Built with love by Moon Dev 🚀

Comprehensive analysis of 24-hour test results including:
- Performance metrics
- Decision analysis
- Trade patterns
- Error analysis
- Recommendations
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from termcolor import cprint
from collections import Counter

class TestResultsAnalyzer:
    """Analyze 24-hour test results"""

    def __init__(self, results_file: Path):
        self.results_file = results_file

        with open(results_file, 'r') as f:
            self.data = json.load(f)

        self.stats = self.data.get('statistics', {})
        self.cycles = self.data.get('cycles', [])
        self.decisions = self.data.get('decisions', [])
        self.trades = self.data.get('trades', [])
        self.errors = self.data.get('errors', [])
        self.config = self.data.get('config', {})

    def analyze_all(self):
        """Run complete analysis"""
        self.display_header()
        self.analyze_test_summary()
        self.analyze_cycles()
        self.analyze_decisions()
        self.analyze_trades()
        self.analyze_errors()
        self.analyze_performance()
        self.generate_recommendations()

    def display_header(self):
        """Display analysis header"""
        print("\n" + "=" * 80)
        cprint("🌙 Moon Dev's 24-Hour Test Results Analysis", "cyan", attrs=["bold"])
        print("=" * 80)
        cprint(f"📄 File: {self.results_file.name}", "white")
        cprint(f"📅 Start: {self.data.get('start_time', 'N/A')}", "white")
        cprint(f"📅 End: {self.data.get('end_time', 'N/A')}", "white")
        print("=" * 80 + "\n")

    def analyze_test_summary(self):
        """Display test summary"""
        cprint("📊 Test Summary", "cyan", attrs=["bold"])
        print("-" * 80)

        # Configuration
        cprint("\n🔧 Configuration:", "yellow")
        print(f"  Model: {self.config.get('model_name', 'N/A')}")
        print(f"  Max Positions: {self.config.get('max_positions', 'N/A')}")
        print(f"  Trading Hours Filter: {self.config.get('use_trading_hours_filter', 'N/A')}")
        print(f"  Starting Balance: ${self.config.get('starting_balance', 0):,.2f}")
        print(f"  Sandbox Mode: {self.config.get('sandbox_mode', 'N/A')}")

        # Statistics
        cprint("\n📈 Statistics:", "yellow")
        print(f"  Total Cycles: {self.stats.get('total_cycles', 0)}")
        print(f"  Successful Cycles: {self.stats.get('successful_cycles', 0)} ({self._percentage(self.stats.get('successful_cycles', 0), self.stats.get('total_cycles', 1))}%)")
        print(f"  Failed Cycles: {self.stats.get('failed_cycles', 0)} ({self._percentage(self.stats.get('failed_cycles', 0), self.stats.get('total_cycles', 1))}%)")
        print(f"  Total Decisions: {self.stats.get('total_decisions', 0)}")
        print(f"  Total Trades: {self.stats.get('total_trades', 0)}")
        print(f"  Total Errors: {self.stats.get('total_errors', 0)}")

        # Timing
        if 'test_duration_seconds' in self.stats:
            hours = self.stats['test_duration_seconds'] / 3600
            cprint(f"\n⏱️  Duration: {hours:.2f} hours ({self.stats['test_duration_seconds']:.0f} seconds)", "yellow")

        if 'avg_cycle_duration' in self.stats:
            print(f"  Average Cycle Duration: {self.stats['avg_cycle_duration']:.1f}s")
            print(f"  Min Cycle Duration: {self.stats['min_cycle_duration']:.1f}s")
            print(f"  Max Cycle Duration: {self.stats['max_cycle_duration']:.1f}s")

        print()

    def analyze_cycles(self):
        """Analyze cycle patterns"""
        cprint("🔄 Cycle Analysis", "cyan", attrs=["bold"])
        print("-" * 80)

        if not self.cycles:
            cprint("  No cycle data available", "yellow")
            print()
            return

        # Success rate over time
        total = len(self.cycles)
        successful = sum(1 for c in self.cycles if c.get('success', False))
        failed = total - successful

        print(f"  Success Rate: {self._percentage(successful, total)}% ({successful}/{total})")
        print(f"  Failure Rate: {self._percentage(failed, total)}% ({failed}/{total})")

        # Cycle duration distribution
        durations = [c.get('duration_seconds', 0) for c in self.cycles]
        if durations:
            avg_duration = sum(durations) / len(durations)
            print(f"\n  Average Duration: {avg_duration:.1f}s")
            print(f"  Fastest Cycle: {min(durations):.1f}s")
            print(f"  Slowest Cycle: {max(durations):.1f}s")

        # Identify problematic cycles
        slow_cycles = [i for i, c in enumerate(self.cycles) if c.get('duration_seconds', 0) > avg_duration * 1.5]
        if slow_cycles:
            cprint(f"\n  ⚠️  Slow Cycles (>1.5x avg): {len(slow_cycles)}", "yellow")
            for cycle_num in slow_cycles[:5]:  # Show first 5
                print(f"    - Cycle #{cycle_num + 1}: {self.cycles[cycle_num].get('duration_seconds', 0):.1f}s")

        print()

    def analyze_decisions(self):
        """Analyze trading decisions"""
        cprint("🧠 Decision Analysis", "cyan", attrs=["bold"])
        print("-" * 80)

        if not self.decisions:
            cprint("  No decision data available", "yellow")
            print()
            return

        print(f"  Total Decisions: {len(self.decisions)}")

        # Analyze decision types if available
        # This would depend on the structure of decision data
        decisions_per_cycle = len(self.decisions) / max(len(self.cycles), 1)
        print(f"  Decisions per Cycle: {decisions_per_cycle:.2f}")

        print()

    def analyze_trades(self):
        """Analyze trade patterns"""
        cprint("💼 Trade Analysis", "cyan", attrs=["bold"])
        print("-" * 80)

        if not self.trades:
            cprint("  No trades executed during test", "yellow")
            cprint("  This may be expected if:", "white")
            print("    - Trading hours filter was active")
            print("    - Market conditions didn't meet criteria")
            print("    - AI decided not to trade")
            print()
            return

        print(f"  Total Trades: {len(self.trades)}")
        trades_per_cycle = len(self.trades) / max(len(self.cycles), 1)
        print(f"  Trades per Cycle: {trades_per_cycle:.2f}")

        print()

    def analyze_errors(self):
        """Analyze errors"""
        cprint("⚠️  Error Analysis", "cyan", attrs=["bold"])
        print("-" * 80)

        if not self.errors:
            cprint("  ✅ No errors! Perfect execution!", "green")
            print()
            return

        print(f"  Total Errors: {len(self.errors)}")

        # Error frequency
        error_messages = [e.get('error', '') for e in self.errors]
        error_counts = Counter(error_messages)

        cprint("\n  Most Common Errors:", "yellow")
        for error, count in error_counts.most_common(5):
            print(f"    - ({count}x) {error[:100]}...")

        # Error timeline
        if len(self.errors) > 1:
            first_error_cycle = self.errors[0].get('cycle', 'N/A')
            last_error_cycle = self.errors[-1].get('cycle', 'N/A')
            print(f"\n  First Error: Cycle #{first_error_cycle}")
            print(f"  Last Error: Cycle #{last_error_cycle}")

        print()

    def analyze_performance(self):
        """Analyze overall performance"""
        cprint("📈 Performance Analysis", "cyan", attrs=["bold"])
        print("-" * 80)

        # Calculate uptime
        if 'test_duration_seconds' in self.stats and 'total_cycles' in self.stats:
            expected_cycles = self.stats['test_duration_seconds'] / (15 * 60)  # 15 min intervals
            actual_cycles = self.stats['total_cycles']
            uptime = (actual_cycles / expected_cycles) * 100 if expected_cycles > 0 else 0
            print(f"  System Uptime: {uptime:.1f}%")
            print(f"  Expected Cycles: {expected_cycles:.0f}")
            print(f"  Actual Cycles: {actual_cycles}")

        # Success rate
        if 'successful_cycles' in self.stats and 'total_cycles' in self.stats:
            success_rate = self._percentage(self.stats['successful_cycles'], self.stats['total_cycles'])
            print(f"\n  Success Rate: {success_rate}%")

            if success_rate >= 95:
                cprint("  ✅ Excellent performance!", "green")
            elif success_rate >= 80:
                cprint("  👍 Good performance", "cyan")
            elif success_rate >= 60:
                cprint("  ⚠️  Acceptable performance - room for improvement", "yellow")
            else:
                cprint("  ❌ Poor performance - needs investigation", "red")

        print()

    def generate_recommendations(self):
        """Generate recommendations based on analysis"""
        cprint("💡 Recommendations", "cyan", attrs=["bold"])
        print("-" * 80)

        recommendations = []

        # Check error rate
        if self.stats.get('total_errors', 0) > 0:
            error_rate = self._percentage(self.stats['total_errors'], self.stats['total_cycles'])
            if error_rate > 10:
                recommendations.append(("High error rate detected", "Review error logs and fix underlying issues", "high"))
            elif error_rate > 5:
                recommendations.append(("Moderate error rate", "Monitor errors and investigate patterns", "medium"))

        # Check success rate
        success_rate = self._percentage(self.stats.get('successful_cycles', 0), self.stats.get('total_cycles', 1))
        if success_rate < 80:
            recommendations.append(("Low success rate", "Review failed cycles and improve error handling", "high"))

        # Check cycle duration
        if 'avg_cycle_duration' in self.stats:
            if self.stats['avg_cycle_duration'] > 120:  # 2 minutes
                recommendations.append(("Slow cycle execution", "Optimize AI calls or data fetching", "medium"))

        # Check trade activity
        if len(self.trades) == 0 and len(self.cycles) > 10:
            recommendations.append(("No trades executed", "Review trading criteria - may be too strict", "low"))

        # Display recommendations
        if recommendations:
            for i, (issue, action, priority) in enumerate(recommendations, 1):
                color = {"high": "red", "medium": "yellow", "low": "cyan"}[priority]
                cprint(f"\n  {i}. {issue}", color, attrs=["bold"])
                print(f"     Action: {action}")
                print(f"     Priority: {priority.upper()}")
        else:
            cprint("  ✅ No major issues detected! System is performing well.", "green")

        print("\n" + "=" * 80 + "\n")

    def _percentage(self, value: int, total: int) -> float:
        """Calculate percentage"""
        if total == 0:
            return 0.0
        return round((value / total) * 100, 1)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Analyze 24-hour test results')
    parser.add_argument('file', type=str, nargs='?', help='Path to results JSON file')
    parser.add_argument('--latest', action='store_true', help='Analyze latest results file')

    args = parser.parse_args()

    # Determine results file
    if args.latest or not args.file:
        results_dir = Path(__file__).parent / 'results'
        if not results_dir.exists():
            cprint("❌ Results directory not found", "red")
            sys.exit(1)

        json_files = sorted(results_dir.glob('24h_test_*.json'), key=lambda x: x.stat().st_mtime, reverse=True)
        if not json_files:
            cprint("❌ No results files found", "red")
            sys.exit(1)

        results_file = json_files[0]
        cprint(f"📄 Analyzing latest file: {results_file.name}", "cyan")
    else:
        results_file = Path(args.file)
        if not results_file.exists():
            cprint(f"❌ File not found: {results_file}", "red")
            sys.exit(1)

    # Analyze results
    analyzer = TestResultsAnalyzer(results_file)
    analyzer.analyze_all()


if __name__ == "__main__":
    main()

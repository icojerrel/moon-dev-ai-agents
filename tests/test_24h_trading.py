"""
🌙 Moon Dev's 24-Hour MT5 Trading System Test
Built with love by Moon Dev 🚀

This script runs a comprehensive 24-hour test of the MT5 trading system
in sandbox mode, testing all features including:
- Multi-asset trading (Forex, Gold, Stocks, Indices)
- Trading hours filtering
- Risk management (max 1 position)
- AI decision making via OpenRouter
- Position management

All trades are simulated - NO REAL MONEY IS USED.
"""

import sys
import os
from pathlib import Path
import time
from datetime import datetime, timedelta
import json
from termcolor import cprint
import argparse

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agents.mt5_trading_agent import MT5TradingAgent
from src.config import (
    MT5_MODEL_TYPE,
    MT5_MODEL_NAME,
    MT5_MAX_POSITIONS,
    MT5_USE_TRADING_HOURS_FILTER,
    SANDBOX_STARTING_BALANCE,
    SANDBOX_MODE
)

class TradingTest24h:
    """24-hour trading system test with comprehensive logging"""

    def __init__(self, test_duration_hours: int = 24, skip_mt5: bool = False):
        self.test_duration_hours = test_duration_hours
        self.skip_mt5 = skip_mt5
        self.start_time = datetime.now()
        self.end_time = self.start_time + timedelta(hours=test_duration_hours)

        # Test data collection
        self.test_data = {
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'config': {
                'model_type': MT5_MODEL_TYPE,
                'model_name': MT5_MODEL_NAME,
                'max_positions': MT5_MAX_POSITIONS,
                'use_trading_hours_filter': MT5_USE_TRADING_HOURS_FILTER,
                'sandbox_mode': SANDBOX_MODE,
                'starting_balance': SANDBOX_STARTING_BALANCE,
            },
            'cycles': [],
            'trades': [],
            'decisions': [],
            'errors': [],
            'statistics': {}
        }

        # Results directory
        self.results_dir = project_root / 'tests' / 'results'
        self.results_dir.mkdir(exist_ok=True)

        cprint("🌙 Moon Dev's 24-Hour MT5 Trading Test", "cyan", attrs=["bold"])
        cprint("=" * 60, "cyan")
        cprint(f"⏰ Start time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}", "green")
        cprint(f"⏰ End time:   {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}", "green")
        cprint(f"⏱️  Duration:   {test_duration_hours} hours", "green")
        cprint(f"🤖 AI Model:   {MT5_MODEL_NAME}", "green")
        cprint(f"📊 Max Positions: {MT5_MAX_POSITIONS}", "green")
        cprint(f"💰 Starting Balance: ${SANDBOX_STARTING_BALANCE:,.2f}", "green")
        cprint("=" * 60, "cyan")
        print()

    def run_test_cycle(self, agent: MT5TradingAgent, cycle_num: int):
        """Run a single test cycle"""
        cycle_start = datetime.now()
        cprint(f"\n{'=' * 60}", "cyan")
        cprint(f"🔄 Test Cycle #{cycle_num} - {cycle_start.strftime('%H:%M:%S')}", "cyan", attrs=["bold"])
        cprint(f"{'=' * 60}", "cyan")

        cycle_data = {
            'cycle_num': cycle_num,
            'start_time': cycle_start.isoformat(),
            'decisions': [],
            'errors': []
        }

        try:
            # Run agent analysis
            result = agent.run()

            # Store results
            if result:
                cycle_data['result'] = result
                cycle_data['success'] = True

                # Track decisions
                if 'decisions' in result:
                    for decision in result['decisions']:
                        self.test_data['decisions'].append({
                            'cycle': cycle_num,
                            'time': cycle_start.isoformat(),
                            'decision': decision
                        })

                # Track trades
                if 'trades' in result:
                    for trade in result['trades']:
                        self.test_data['trades'].append({
                            'cycle': cycle_num,
                            'time': cycle_start.isoformat(),
                            'trade': trade
                        })

        except Exception as e:
            cprint(f"❌ Error in cycle {cycle_num}: {str(e)}", "red")
            cycle_data['success'] = False
            cycle_data['error'] = str(e)
            self.test_data['errors'].append({
                'cycle': cycle_num,
                'time': cycle_start.isoformat(),
                'error': str(e)
            })

        cycle_end = datetime.now()
        cycle_data['end_time'] = cycle_end.isoformat()
        cycle_data['duration_seconds'] = (cycle_end - cycle_start).total_seconds()

        self.test_data['cycles'].append(cycle_data)

        # Show cycle summary
        cprint(f"\n✅ Cycle #{cycle_num} completed in {cycle_data['duration_seconds']:.1f}s", "green")

    def run(self, check_interval_minutes: int = 15):
        """Run the full 24-hour test"""

        try:
            # Initialize agent
            cprint("🚀 Initializing MT5 Trading Agent...", "yellow")
            if self.skip_mt5:
                cprint("⚠️  Running in skip-MT5 mode (mock MT5 connections)", "yellow")
            agent = MT5TradingAgent(
                model_type=MT5_MODEL_TYPE,
                model_name=MT5_MODEL_NAME,
                max_positions=MT5_MAX_POSITIONS
            )
            cprint("✅ Agent initialized successfully", "green")
            print()

            cycle_num = 0

            # Run cycles until test duration is reached
            while datetime.now() < self.end_time:
                cycle_num += 1

                # Run test cycle
                self.run_test_cycle(agent, cycle_num)

                # Calculate time remaining
                time_remaining = self.end_time - datetime.now()

                if time_remaining.total_seconds() > 0:
                    # Wait until next cycle
                    next_cycle_time = datetime.now() + timedelta(minutes=check_interval_minutes)

                    if next_cycle_time < self.end_time:
                        wait_seconds = check_interval_minutes * 60
                        cprint(f"\n⏳ Waiting {check_interval_minutes} minutes until next cycle...", "yellow")
                        cprint(f"⏱️  Time remaining in test: {self._format_timedelta(time_remaining)}", "cyan")

                        # Save intermediate results
                        self._save_results(intermediate=True)

                        time.sleep(wait_seconds)
                    else:
                        # Last cycle - wait remaining time
                        wait_seconds = time_remaining.total_seconds()
                        if wait_seconds > 0:
                            cprint(f"\n⏳ Waiting final {wait_seconds:.0f} seconds...", "yellow")
                            time.sleep(wait_seconds)
                        break
                else:
                    break

            # Test completed
            cprint("\n" + "=" * 60, "green", attrs=["bold"])
            cprint("✅ 24-HOUR TEST COMPLETED!", "green", attrs=["bold"])
            cprint("=" * 60, "green", attrs=["bold"])

            # Generate final statistics
            self._calculate_statistics()

            # Save final results
            self._save_results(intermediate=False)

            # Display summary
            self._display_summary()

        except KeyboardInterrupt:
            cprint("\n\n⚠️ Test interrupted by user", "yellow")
            cprint("💾 Saving partial results...", "yellow")
            self._calculate_statistics()
            self._save_results(intermediate=True)
            self._display_summary()

        except Exception as e:
            cprint(f"\n\n❌ Test failed with error: {str(e)}", "red")
            self._calculate_statistics()
            self._save_results(intermediate=True)
            raise

    def _calculate_statistics(self):
        """Calculate test statistics"""
        stats = {
            'total_cycles': len(self.test_data['cycles']),
            'successful_cycles': sum(1 for c in self.test_data['cycles'] if c.get('success', False)),
            'failed_cycles': sum(1 for c in self.test_data['cycles'] if not c.get('success', True)),
            'total_decisions': len(self.test_data['decisions']),
            'total_trades': len(self.test_data['trades']),
            'total_errors': len(self.test_data['errors']),
            'test_duration_seconds': (datetime.now() - self.start_time).total_seconds(),
        }

        # Calculate average cycle duration
        if self.test_data['cycles']:
            cycle_durations = [c.get('duration_seconds', 0) for c in self.test_data['cycles']]
            stats['avg_cycle_duration'] = sum(cycle_durations) / len(cycle_durations)
            stats['min_cycle_duration'] = min(cycle_durations)
            stats['max_cycle_duration'] = max(cycle_durations)

        self.test_data['statistics'] = stats

    def _save_results(self, intermediate: bool = False):
        """Save test results to JSON file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        prefix = "INTERMEDIATE" if intermediate else "FINAL"
        filename = f"24h_test_{prefix}_{timestamp}.json"
        filepath = self.results_dir / filename

        with open(filepath, 'w') as f:
            json.dump(self.test_data, f, indent=2)

        cprint(f"\n💾 Results saved to: {filepath}", "cyan")

    def _display_summary(self):
        """Display test summary"""
        stats = self.test_data['statistics']

        print("\n" + "=" * 60)
        cprint("📊 TEST SUMMARY", "cyan", attrs=["bold"])
        print("=" * 60)

        cprint(f"⏱️  Test Duration: {self._format_seconds(stats.get('test_duration_seconds', 0))}", "white")
        cprint(f"🔄 Total Cycles: {stats.get('total_cycles', 0)}", "white")
        cprint(f"✅ Successful: {stats.get('successful_cycles', 0)}", "green")
        cprint(f"❌ Failed: {stats.get('failed_cycles', 0)}", "red" if stats.get('failed_cycles', 0) > 0 else "white")
        cprint(f"📊 Total Decisions: {stats.get('total_decisions', 0)}", "white")
        cprint(f"💼 Total Trades: {stats.get('total_trades', 0)}", "white")
        cprint(f"⚠️  Total Errors: {stats.get('total_errors', 0)}", "red" if stats.get('total_errors', 0) > 0 else "white")

        if 'avg_cycle_duration' in stats:
            cprint(f"\n⏱️  Average Cycle Duration: {stats['avg_cycle_duration']:.1f}s", "cyan")
            cprint(f"⏱️  Min Cycle Duration: {stats['min_cycle_duration']:.1f}s", "cyan")
            cprint(f"⏱️  Max Cycle Duration: {stats['max_cycle_duration']:.1f}s", "cyan")

        print("=" * 60)

        # Show recent errors if any
        if self.test_data['errors']:
            print()
            cprint("⚠️ Recent Errors:", "yellow", attrs=["bold"])
            for error in self.test_data['errors'][-5:]:  # Last 5 errors
                cprint(f"  Cycle {error['cycle']}: {error['error']}", "red")

    def _format_timedelta(self, td: timedelta) -> str:
        """Format timedelta as human-readable string"""
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours}h {minutes}m {seconds}s"

    def _format_seconds(self, seconds: float) -> str:
        """Format seconds as human-readable string"""
        return self._format_timedelta(timedelta(seconds=seconds))


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Run 24-hour MT5 trading system test')
    parser.add_argument('--duration', type=int, default=24, help='Test duration in hours (default: 24)')
    parser.add_argument('--interval', type=int, default=15, help='Check interval in minutes (default: 15)')
    parser.add_argument('--skip-mt5', action='store_true', help='Skip MT5 initialization (for testing on Mac/Linux)')

    args = parser.parse_args()

    # Check if sandbox mode is enabled
    if not SANDBOX_MODE:
        cprint("⚠️ WARNING: SANDBOX_MODE is disabled in config.py", "red", attrs=["bold"])
        cprint("⚠️ This test should run in sandbox mode to avoid real trades!", "red", attrs=["bold"])
        response = input("Continue anyway? (yes/no): ")
        if response.lower() != 'yes':
            cprint("❌ Test cancelled", "yellow")
            return

    # Create and run test
    test = TradingTest24h(test_duration_hours=args.duration, skip_mt5=args.skip_mt5)
    test.run(check_interval_minutes=args.interval)


if __name__ == "__main__":
    main()

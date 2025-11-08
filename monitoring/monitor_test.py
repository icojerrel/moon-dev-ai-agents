"""
🌙 Moon Dev's 24-Hour Test Monitor
Built with love by Moon Dev 🚀

Real-time monitoring of the 24-hour trading test
Watches for new results and displays live statistics
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
from termcolor import cprint
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class TestMonitor(FileSystemEventHandler):
    """Monitor test results directory for updates"""

    def __init__(self, results_dir: Path):
        self.results_dir = results_dir
        self.last_stats = None

    def on_created(self, event):
        """Handle new file creation"""
        if event.is_directory:
            return

        if event.src_path.endswith('.json'):
            cprint(f"\n📄 New result file: {Path(event.src_path).name}", "cyan")
            self.display_latest_stats()

    def on_modified(self, event):
        """Handle file modification"""
        if event.is_directory:
            return

        if event.src_path.endswith('.json') and 'INTERMEDIATE' in event.src_path:
            self.display_latest_stats()

    def display_latest_stats(self):
        """Display latest test statistics"""
        try:
            # Find latest result file
            json_files = sorted(self.results_dir.glob('24h_test_*.json'), key=lambda x: x.stat().st_mtime, reverse=True)

            if not json_files:
                cprint("⏳ Waiting for test results...", "yellow")
                return

            latest_file = json_files[0]

            with open(latest_file, 'r') as f:
                data = json.load(f)

            stats = data.get('statistics', {})

            # Only display if stats changed
            if stats == self.last_stats:
                return

            self.last_stats = stats

            # Display statistics
            now = datetime.now().strftime('%H:%M:%S')
            print("\n" + "=" * 60)
            cprint(f"📊 Test Statistics Update - {now}", "cyan", attrs=["bold"])
            print("=" * 60)

            # Basic stats
            cprint(f"🔄 Total Cycles: {stats.get('total_cycles', 0)}", "white")
            cprint(f"✅ Successful: {stats.get('successful_cycles', 0)}", "green")
            cprint(f"❌ Failed: {stats.get('failed_cycles', 0)}", "red" if stats.get('failed_cycles', 0) > 0 else "white")
            cprint(f"📊 Decisions: {stats.get('total_decisions', 0)}", "white")
            cprint(f"💼 Trades: {stats.get('total_trades', 0)}", "white")
            cprint(f"⚠️  Errors: {stats.get('total_errors', 0)}", "red" if stats.get('total_errors', 0) > 0 else "white")

            # Timing stats
            if 'avg_cycle_duration' in stats:
                cprint(f"\n⏱️  Avg Cycle: {stats['avg_cycle_duration']:.1f}s", "cyan")
                cprint(f"⏱️  Min Cycle: {stats['min_cycle_duration']:.1f}s", "cyan")
                cprint(f"⏱️  Max Cycle: {stats['max_cycle_duration']:.1f}s", "cyan")

            # Test duration
            if 'test_duration_seconds' in stats:
                hours = stats['test_duration_seconds'] / 3600
                cprint(f"\n⏳ Running for: {hours:.2f} hours", "yellow")

            print("=" * 60)

        except Exception as e:
            cprint(f"❌ Error reading stats: {str(e)}", "red")

    def start_monitoring(self):
        """Start monitoring the results directory"""
        cprint("🔍 Starting test monitor...", "cyan", attrs=["bold"])
        cprint(f"📂 Watching: {self.results_dir}", "white")
        cprint("Press Ctrl+C to stop monitoring\n", "yellow")

        observer = Observer()
        observer.schedule(self, str(self.results_dir), recursive=False)
        observer.start()

        try:
            # Display initial stats if available
            self.display_latest_stats()

            # Keep monitoring
            while True:
                time.sleep(5)
                self.display_latest_stats()

        except KeyboardInterrupt:
            cprint("\n\n⏹️  Monitoring stopped", "yellow")
            observer.stop()

        observer.join()


def main():
    """Main entry point"""
    results_dir = Path('/results')

    if not results_dir.exists():
        cprint(f"❌ Results directory not found: {results_dir}", "red")
        cprint("Make sure the volume is mounted correctly", "yellow")
        sys.exit(1)

    monitor = TestMonitor(results_dir)
    monitor.start_monitoring()


if __name__ == "__main__":
    main()

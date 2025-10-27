#!/usr/bin/env python3
"""
🌙 Moon Dev's Performance Benchmark Tool 🌙

Measures and compares performance of:
- Old system (main.py sequential 15-min cycle)
- New system (async orchestrator + real-time feeds)
- Rust core (when available)

Usage:
    python scripts/benchmark_performance.py

    # Specific benchmark
    python scripts/benchmark_performance.py --test price_fetch
    python scripts/benchmark_performance.py --test agent_execution
"""

import asyncio
import time
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Tuple
from termcolor import colored, cprint
from statistics import mean, stdev

# Add project root to path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

# Imports
from src.nice_funcs import token_price

# Check for real-time feed
try:
    from src.services.realtime_price_feed import RealtimePriceFeed
    REALTIME_FEED_AVAILABLE = True
except ImportError:
    REALTIME_FEED_AVAILABLE = False

# Check for Rust core
try:
    import moon_rust_core
    RUST_CORE_AVAILABLE = True
except ImportError:
    RUST_CORE_AVAILABLE = False


class PerformanceBenchmark:
    """Performance benchmarking tool"""

    def __init__(self):
        self.results: Dict[str, Dict] = {}

    def measure_time(self, func, *args, **kwargs) -> Tuple[float, any]:
        """
        Measure execution time of a function

        Returns:
            Tuple of (time_ms, result)
        """
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        return (end - start) * 1000, result

    async def measure_time_async(self, func, *args, **kwargs) -> Tuple[float, any]:
        """
        Measure execution time of async function

        Returns:
            Tuple of (time_ms, result)
        """
        start = time.perf_counter()
        result = await func(*args, **kwargs)
        end = time.perf_counter()
        return (end - start) * 1000, result

    def benchmark_price_fetch_old(self, iterations: int = 10) -> Dict:
        """
        Benchmark old price fetching method (nice_funcs.token_price)

        Args:
            iterations: Number of iterations to run

        Returns:
            Dict with timing statistics
        """
        cprint("\n📊 Benchmarking OLD price fetch (Python REST API)...", "yellow")

        timings = []
        tokens = ['SOL', 'BTC', 'ETH']

        for i in range(iterations):
            start = time.perf_counter()

            # Sequential fetching (how old system worked)
            for token in tokens:
                try:
                    price = token_price(token)
                except Exception:
                    pass

            end = time.perf_counter()
            elapsed_ms = (end - start) * 1000
            timings.append(elapsed_ms)

            print(f"  Iteration {i+1}/{iterations}: {elapsed_ms:.0f}ms")

        return {
            'method': 'Old Sequential',
            'mean_ms': mean(timings),
            'stdev_ms': stdev(timings) if len(timings) > 1 else 0,
            'min_ms': min(timings),
            'max_ms': max(timings),
            'iterations': iterations
        }

    async def benchmark_price_fetch_async(self, iterations: int = 10) -> Dict:
        """
        Benchmark async price fetching (parallel)

        Args:
            iterations: Number of iterations to run

        Returns:
            Dict with timing statistics
        """
        cprint("\n📊 Benchmarking NEW price fetch (Async parallel)...", "yellow")

        timings = []
        tokens = ['SOL', 'BTC', 'ETH']

        for i in range(iterations):
            start = time.perf_counter()

            # Parallel fetching
            tasks = []
            for token in tokens:
                async def fetch_price(t):
                    try:
                        return token_price(t)
                    except Exception:
                        return None

                tasks.append(fetch_price(token))

            await asyncio.gather(*tasks)

            end = time.perf_counter()
            elapsed_ms = (end - start) * 1000
            timings.append(elapsed_ms)

            print(f"  Iteration {i+1}/{iterations}: {elapsed_ms:.0f}ms")

        return {
            'method': 'New Async Parallel',
            'mean_ms': mean(timings),
            'stdev_ms': stdev(timings) if len(timings) > 1 else 0,
            'min_ms': min(timings),
            'max_ms': max(timings),
            'iterations': iterations
        }

    async def benchmark_price_fetch_realtime(self, duration_seconds: int = 30) -> Dict:
        """
        Benchmark real-time price feed

        Args:
            duration_seconds: How long to run

        Returns:
            Dict with timing statistics
        """
        if not REALTIME_FEED_AVAILABLE:
            return {
                'method': 'Real-time Feed',
                'error': 'Not available'
            }

        cprint(f"\n📊 Benchmarking REAL-TIME feed ({duration_seconds}s)...", "yellow")

        feed = RealtimePriceFeed()
        await feed.connect()

        tokens = ['SOL', 'BTC', 'ETH']
        feed.subscribe(tokens)

        # Track updates
        update_times = []
        update_count = 0

        def on_update(token, data):
            nonlocal update_count
            update_count += 1

        feed.add_subscriber(on_update)

        # Run for duration
        start_time = time.time()
        task = asyncio.create_task(feed.start())

        await asyncio.sleep(duration_seconds)

        # Stop feed
        feed.running = False
        task.cancel()

        await feed.disconnect()

        elapsed = time.time() - start_time

        return {
            'method': 'Real-time WebSocket Feed',
            'total_updates': update_count,
            'updates_per_second': update_count / elapsed,
            'duration_seconds': elapsed
        }

    def benchmark_rust_core(self, iterations: int = 1000) -> Dict:
        """
        Benchmark Rust core price fetching

        Args:
            iterations: Number of iterations

        Returns:
            Dict with timing statistics
        """
        if not RUST_CORE_AVAILABLE:
            return {
                'method': 'Rust Core',
                'error': 'Not available (build with: cd rust_core && maturin develop --release)'
            }

        cprint(f"\n📊 Benchmarking RUST CORE ({iterations} iterations)...", "yellow")

        timings = []

        for i in range(iterations):
            start = time.perf_counter()
            price = moon_rust_core.get_realtime_price('SOL')
            end = time.perf_counter()

            elapsed_ms = (end - start) * 1000
            timings.append(elapsed_ms)

            if i % 100 == 0:
                print(f"  Iteration {i+1}/{iterations}: {elapsed_ms:.4f}ms")

        return {
            'method': 'Rust Core (PyO3)',
            'mean_ms': mean(timings),
            'stdev_ms': stdev(timings) if len(timings) > 1 else 0,
            'min_ms': min(timings),
            'max_ms': max(timings),
            'iterations': iterations
        }

    def print_comparison(self, results: List[Dict]):
        """
        Print comparison table of results

        Args:
            results: List of benchmark results
        """
        cprint("\n" + "="*80, "cyan")
        cprint("📊 PERFORMANCE COMPARISON", "cyan", attrs=['bold'])
        cprint("="*80, "cyan")

        # Print header
        print(f"\n{'Method':<30} {'Mean (ms)':<15} {'Min (ms)':<15} {'Max (ms)':<15}")
        print("-" * 80)

        baseline_mean = None

        for result in results:
            if 'error' in result:
                print(f"{result['method']:<30} ❌ {result['error']}")
                continue

            mean_ms = result.get('mean_ms')
            min_ms = result.get('min_ms')
            max_ms = result.get('max_ms')

            if mean_ms is not None:
                # Set baseline (first result)
                if baseline_mean is None:
                    baseline_mean = mean_ms

                # Calculate improvement
                improvement = baseline_mean / mean_ms if mean_ms > 0 else 0

                print(f"{result['method']:<30} {mean_ms:>10.2f}      {min_ms:>10.2f}      {max_ms:>10.2f}")

                if improvement > 1:
                    cprint(f"{'':>30} ⚡ {improvement:.1f}x FASTER than baseline", "green")

            elif 'updates_per_second' in result:
                print(f"{result['method']:<30} {result['updates_per_second']:.1f} updates/sec")

        # Print summary
        cprint("\n" + "="*80, "cyan")
        cprint("📈 SUMMARY", "cyan", attrs=['bold'])
        cprint("="*80, "cyan")

        if baseline_mean:
            cprint(f"\n🐌 Old System Baseline: {baseline_mean:.0f}ms per update cycle", "red")

            # Calculate new system improvement
            new_results = [r for r in results if r.get('method') == 'New Async Parallel']
            if new_results and 'mean_ms' in new_results[0]:
                new_mean = new_results[0]['mean_ms']
                improvement = baseline_mean / new_mean
                cprint(f"🚀 New System: {new_mean:.0f}ms ({improvement:.1f}x faster)", "green", attrs=['bold'])

            # Rust improvement
            rust_results = [r for r in results if r.get('method') == 'Rust Core (PyO3)']
            if rust_results and 'mean_ms' in rust_results[0]:
                rust_mean = rust_results[0]['mean_ms']
                improvement = baseline_mean / rust_mean
                cprint(f"⚡ Rust Core: {rust_mean:.4f}ms ({improvement:.0f}x faster)", "green", attrs=['bold'])

        # Real-time feed stats
        realtime_results = [r for r in results if r.get('method') == 'Real-time WebSocket Feed']
        if realtime_results and 'updates_per_second' in realtime_results[0]:
            ups = realtime_results[0]['updates_per_second']
            cprint(f"\n🌊 Real-time Feed: {ups:.1f} updates/second (vs 1 update per 15 min = 0.001 updates/sec)", "green")
            improvement = ups / 0.001
            cprint(f"   Improvement: {improvement:.0f}x more frequent updates", "green", attrs=['bold'])

    async def run_all_benchmarks(self):
        """Run all benchmarks"""
        cprint("\n" + "="*80, "green")
        cprint("🌙 Moon Dev Performance Benchmark Suite 🌙", "green", attrs=['bold'])
        cprint("="*80, "green")

        results = []

        # 1. Old sequential
        old_result = self.benchmark_price_fetch_old(iterations=5)
        results.append(old_result)

        # 2. New async parallel
        new_result = await self.benchmark_price_fetch_async(iterations=5)
        results.append(new_result)

        # 3. Real-time feed
        realtime_result = await self.benchmark_price_fetch_realtime(duration_seconds=15)
        results.append(realtime_result)

        # 4. Rust core
        rust_result = self.benchmark_rust_core(iterations=1000)
        results.append(rust_result)

        # Print comparison
        self.print_comparison(results)

        # Save results
        self._save_results(results)

    def _save_results(self, results: List[Dict]):
        """Save benchmark results to file"""
        import json
        from datetime import datetime

        output_dir = Path(project_root) / "benchmarks"
        output_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"benchmark_{timestamp}.json"

        with open(output_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'results': results
            }, f, indent=2)

        cprint(f"\n💾 Results saved to: {output_file}", "cyan")


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Moon Dev Performance Benchmark")
    parser.add_argument('--test', help="Specific test to run (price_fetch, rust_core, realtime)")
    args = parser.parse_args()

    benchmark = PerformanceBenchmark()

    if args.test:
        if args.test == 'price_fetch':
            old = benchmark.benchmark_price_fetch_old(iterations=10)
            new = await benchmark.benchmark_price_fetch_async(iterations=10)
            benchmark.print_comparison([old, new])

        elif args.test == 'rust_core':
            rust = benchmark.benchmark_rust_core(iterations=10000)
            benchmark.print_comparison([rust])

        elif args.test == 'realtime':
            realtime = await benchmark.benchmark_price_fetch_realtime(duration_seconds=30)
            benchmark.print_comparison([realtime])

        else:
            cprint(f"❌ Unknown test: {args.test}", "red")
    else:
        await benchmark.run_all_benchmarks()


if __name__ == "__main__":
    asyncio.run(main())

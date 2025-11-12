#!/usr/bin/env python
"""
Backtest-to-Memory CLI

Command-line interface for managing backtest knowledge in memory databases.

Usage:
    python src/backtest/backtest_cli.py load --limit 100
    python src/backtest/backtest_cli.py load --agent strategy --limit 50
    python src/backtest/backtest_cli.py load --directory src/data/rbi/03_13_2025/backtests_final
    python src/backtest/backtest_cli.py analyze
    python src/backtest/backtest_cli.py best --n 10

Author: Moon Dev AI Trading System
Date: 2025-11-12
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from src.backtest.backtest_to_memory import (
    BacktestToMemoryBridge,
    BacktestMemoryIntegration,
    populate_memory_from_backtests
)


def print_header(text: str):
    """Print colored header"""
    print(f"\n\033[96m{'='*80}\033[0m")
    print(f"\033[96m  {text}\033[0m")
    print(f"\033[96m{'='*80}\033[0m\n")


def print_success(text: str):
    """Print success message"""
    print(f"\033[92m✅ {text}\033[0m")


def print_info(text: str):
    """Print info message"""
    print(f"\033[96m   {text}\033[0m")


def print_error(text: str):
    """Print error message"""
    print(f"\033[91m❌ {text}\033[0m")


def cmd_load(args):
    """Load backtest strategies into memory"""
    print_header("LOADING BACKTESTS INTO MEMORY")

    if args.directory:
        # Load from specific directory
        bridge = BacktestToMemoryBridge()
        directory = Path(args.directory)

        if not directory.exists():
            print_error(f"Directory not found: {directory}")
            return

        results = bridge.load_directory(
            directory=directory,
            agent_type=args.agent,
            limit=args.limit
        )

    else:
        # Load from all backtests
        results = populate_memory_from_backtests(
            limit=args.limit,
            agent_type=args.agent
        )

    # Print results
    print_header("LOADING RESULTS")
    print_info(f"Total files: {results['total']}")
    print_info(f"Successfully loaded: {results['success']}")
    print_info(f"Failed: {results['failed']}")
    print_info(f"Success rate: {results['success_rate']:.1f}%")

    if results['success'] > 0:
        print_success(f"Loaded {results['success']} strategies into {args.agent} memory!")


def cmd_analyze(args):
    """Analyze loaded strategies"""
    print_header("ANALYZING LOADED STRATEGIES")

    bridge = BacktestToMemoryBridge()

    # Load strategies first if needed
    if not bridge.loaded_strategies:
        print_info("Loading strategies for analysis...")
        bridge.load_all_backtests(limit=args.limit)

    analysis = bridge.analyze_loaded_strategies()

    if 'error' in analysis:
        print_error(analysis['error'])
        return

    print_info(f"Total loaded: {analysis['total_loaded']}")
    print_info(f"Successful: {analysis['successful_strategies']}")
    print_info(f"Success rate: {analysis['success_rate']:.1f}%")

    # Export if requested
    if args.export:
        bridge.export_loaded_strategies(args.export)
        print_success(f"Exported to: {args.export}")


def cmd_best(args):
    """Show best performing strategies"""
    print_header(f"TOP {args.n} PERFORMING STRATEGIES")

    bridge = BacktestToMemoryBridge()

    # Load strategies
    print_info("Loading and analyzing strategies...")
    bridge.load_all_backtests(limit=args.limit)

    # Get best
    best = bridge.get_best_strategies(n=args.n, metric=args.metric)

    if not best:
        print_error("No strategies with performance data found")
        return

    print(f"\n📊 Top {len(best)} strategies by {args.metric}:\n")

    for i, strategy in enumerate(best, 1):
        print(f"   {i}. {strategy.strategy_name}")
        print(f"      Return: {strategy.return_pct or 'N/A'}%")
        print(f"      Sharpe: {strategy.sharpe_ratio or 'N/A'}")
        print(f"      Win Rate: {strategy.win_rate or 'N/A'}%")
        print(f"      File: {Path(strategy.file_path).name}")
        print()


def cmd_find(args):
    """Find backtest files"""
    print_header("FINDING BACKTEST FILES")

    bridge = BacktestToMemoryBridge()

    pattern = args.pattern or "**/*_BTFinal.py"
    files = bridge.find_backtest_files(pattern=pattern, limit=args.limit)

    print_info(f"Pattern: {pattern}")
    print_info(f"Found: {len(files)} files")

    if args.verbose and files:
        print("\n📁 Files:")
        for i, f in enumerate(files[:args.limit or 20], 1):
            print(f"   {i}. {f.relative_to(bridge.backtest_root)}")


def cmd_populate(args):
    """Populate specific agent memory with best strategies"""
    print_header(f"POPULATING {args.agent.upper()} MEMORY")

    integration = BacktestMemoryIntegration()

    if args.agent == 'strategy':
        results = integration.populate_strategy_memory(
            limit=args.limit,
            finalized_only=not args.all
        )
    elif args.agent == 'trading':
        results = integration.populate_trading_memory(best_n=args.limit)
    else:
        print_error(f"Unsupported agent type: {args.agent}")
        print_info("Supported: strategy, trading")
        return

    print_success(f"Populated {args.agent} memory with {results['success']} strategies")


def main():
    parser = argparse.ArgumentParser(
        description="Backtest-to-Memory Bridge CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Load 100 strategies into strategy memory
  %(prog)s load --limit 100 --agent strategy

  # Load specific directory
  %(prog)s load --directory src/data/rbi/03_13_2025/backtests_final

  # Find all backtest files
  %(prog)s find --pattern "**/*_BTFinal.py"

  # Show top 10 best strategies
  %(prog)s best --n 10 --metric return_pct

  # Analyze loaded strategies
  %(prog)s analyze --export results.json

  # Populate trading memory with best strategies
  %(prog)s populate --agent trading --limit 50
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Load command
    parser_load = subparsers.add_parser('load', help='Load backtests into memory')
    parser_load.add_argument('--agent', default='strategy', help='Agent type (strategy, trading)')
    parser_load.add_argument('--limit', type=int, default=100, help='Maximum files to load')
    parser_load.add_argument('--directory', help='Specific directory to load from')

    # Analyze command
    parser_analyze = subparsers.add_parser('analyze', help='Analyze loaded strategies')
    parser_analyze.add_argument('--limit', type=int, default=200, help='Strategies to analyze')
    parser_analyze.add_argument('--export', help='Export results to file')

    # Best command
    parser_best = subparsers.add_parser('best', help='Show best strategies')
    parser_best.add_argument('--n', type=int, default=10, help='Number of strategies')
    parser_best.add_argument('--metric', default='return_pct',
                            choices=['return_pct', 'sharpe_ratio', 'win_rate'],
                            help='Metric to sort by')
    parser_best.add_argument('--limit', type=int, default=200, help='Strategies to consider')

    # Find command
    parser_find = subparsers.add_parser('find', help='Find backtest files')
    parser_find.add_argument('--pattern', help='Glob pattern')
    parser_find.add_argument('--limit', type=int, help='Maximum files to show')
    parser_find.add_argument('--verbose', action='store_true', help='Show file list')

    # Populate command
    parser_populate = subparsers.add_parser('populate', help='Populate agent memory')
    parser_populate.add_argument('--agent', required=True,
                                choices=['strategy', 'trading'],
                                help='Agent to populate')
    parser_populate.add_argument('--limit', type=int, default=50, help='Number of strategies')
    parser_populate.add_argument('--all', action='store_true',
                                help='Include non-finalized strategies')

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    # Route commands
    try:
        if args.command == 'load':
            cmd_load(args)
        elif args.command == 'analyze':
            cmd_analyze(args)
        elif args.command == 'best':
            cmd_best(args)
        elif args.command == 'find':
            cmd_find(args)
        elif args.command == 'populate':
            cmd_populate(args)
        else:
            parser.print_help()

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print_error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

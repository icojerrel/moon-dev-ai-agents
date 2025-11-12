#!/usr/bin/env python
"""
Memory CLI - Command-line interface for MemoriSDK memory management

Usage:
    python src/agents/memory_cli.py summary
    python src/agents/memory_cli.py stats <database_name>
    python src/agents/memory_cli.py query <database_name> [search_term]
    python src/agents/memory_cli.py export <database_name> <output_file>
    python src/agents/memory_cli.py optimize <database_name>
    python src/agents/memory_cli.py search <search_term>

Author: Moon Dev AI Trading System
Date: 2025-11-12
"""

import sys
import argparse
from pathlib import Path
from termcolor import cprint
from memory_analytics import MemoryAnalytics, print_summary, query_all_agents


def cmd_summary():
    """Display memory system summary."""
    print_summary()


def cmd_stats(db_name: str):
    """Display detailed stats for a database."""
    analytics = MemoryAnalytics()
    db_file = analytics.memory_dir / f"{db_name}.db"

    if not db_file.exists():
        cprint(f"❌ Database not found: {db_name}", "red")
        cprint(f"\nAvailable databases:", "yellow")
        for db in analytics.get_all_databases():
            print(f"  • {db.stem}")
        return

    info = analytics.get_database_info(db_file)

    cprint(f"\n📊 Database: {db_name}", "cyan", attrs=["bold"])
    print("="*80)
    print(f"  Path: {info['path']}")
    print(f"  Size: {info['size_mb']:.2f} MB")
    print(f"  Modified: {info['modified']}")
    print(f"\n  Total Memories: {info['total_memories']}")

    if 'long_term_count' in info:
        print(f"    - Long-term: {info['long_term_count']}")
    if 'short_term_count' in info:
        print(f"    - Short-term: {info['short_term_count']}")
    if 'chat_history_count' in info:
        print(f"    - Chat history: {info['chat_history_count']}")

    print(f"\n  Tables ({len(info['tables'])}):")
    for table in info['tables']:
        print(f"    • {table}")

    # Get timeline
    timeline = analytics.get_memory_timeline(db_name, days=7)
    if timeline:
        print(f"\n  📈 Memory Timeline (Last 7 days):")
        for entry in timeline:
            print(f"    {entry['date']}: {entry['count']} memories")

    # Get top entities
    entities = analytics.get_top_entities(db_name, limit=10)
    if entities:
        print(f"\n  🔝 Top Entities:")
        for entity, count in entities.items():
            print(f"    {entity}: {count} mentions")

    print("="*80 + "\n")


def cmd_query(db_name: str, search_term: str = None, limit: int = 20):
    """Query a memory database."""
    analytics = MemoryAnalytics()

    cprint(f"\n🔍 Querying: {db_name}", "cyan", attrs=["bold"])
    if search_term:
        print(f"Search term: {search_term}")
    print("="*80)

    results = analytics.query_memory(db_name, search_term=search_term, limit=limit)

    if not results:
        cprint("\n  No results found", "yellow")
    else:
        print(f"\n  Found {len(results)} results:\n")
        for i, result in enumerate(results, 1):
            print(f"\n  [{i}] Source: {result.get('source', 'unknown')}")
            if 'timestamp' in result:
                print(f"      Time: {result['timestamp']}")
            if 'created_at' in result:
                print(f"      Created: {result['created_at']}")

            content = result.get('content', result.get('message', result.get('data', 'No content')))
            print(f"      Content: {str(content)[:200]}")

            if i >= limit:
                break

    print("\n" + "="*80 + "\n")


def cmd_export(db_name: str, output_file: str, format: str = 'json'):
    """Export a memory database."""
    analytics = MemoryAnalytics()

    cprint(f"\n📤 Exporting: {db_name} → {output_file}", "cyan", attrs=["bold"])
    print("="*80)

    success = analytics.export_memory(db_name, output_file, format=format)

    if success:
        cprint(f"\n✅ Export successful!", "green")
        print(f"  File: {output_file}")
        print(f"  Format: {format}")
    else:
        cprint(f"\n❌ Export failed", "red")

    print("="*80 + "\n")


def cmd_optimize(db_name: str):
    """Optimize a memory database."""
    analytics = MemoryAnalytics()

    cprint(f"\n⚡ Optimizing: {db_name}", "cyan", attrs=["bold"])
    print("="*80)

    success = analytics.optimize_database(db_name)

    if success:
        cprint(f"\n✅ Optimization complete!", "green")
    else:
        cprint(f"\n❌ Optimization failed", "red")

    print("="*80 + "\n")


def cmd_search(search_term: str):
    """Search across all databases."""
    query_all_agents(search_term, limit=50)


def cmd_list():
    """List all available databases."""
    analytics = MemoryAnalytics()
    databases = analytics.get_all_databases()

    cprint("\n📁 Available Databases:", "cyan", attrs=["bold"])
    print("="*80)

    for db in databases:
        info = analytics.get_database_info(db)
        shared = "🌊 Shared" if "shared" in db.name else "🤖 Agent"
        print(f"  {shared:12} {db.stem:<30} {info['size_mb']:>6.2f} MB  ({info['total_memories']:>5} memories)")

    print("="*80 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Memory CLI - MemoriSDK Management Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s summary                           # Show system summary
  %(prog)s list                              # List all databases
  %(prog)s stats trading_agent               # Show stats for trading agent
  %(prog)s query trading_agent SOL           # Query for SOL in trading agent
  %(prog)s search BTC                        # Search all databases for BTC
  %(prog)s export trading_agent out.json     # Export to JSON
  %(prog)s optimize trading_agent            # Optimize database
        """
    )

    parser.add_argument('command', help='Command to execute')
    parser.add_argument('args', nargs='*', help='Command arguments')
    parser.add_argument('--limit', type=int, default=20, help='Result limit for queries')
    parser.add_argument('--format', default='json', choices=['json', 'csv'], help='Export format')

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    # Route commands
    try:
        if args.command == 'summary':
            cmd_summary()

        elif args.command == 'list':
            cmd_list()

        elif args.command == 'stats':
            if not args.args:
                cprint("❌ Error: stats requires database name", "red")
                print("Usage: memory_cli.py stats <database_name>")
                sys.exit(1)
            cmd_stats(args.args[0])

        elif args.command == 'query':
            if not args.args:
                cprint("❌ Error: query requires database name", "red")
                print("Usage: memory_cli.py query <database_name> [search_term]")
                sys.exit(1)
            db_name = args.args[0]
            search_term = args.args[1] if len(args.args) > 1 else None
            cmd_query(db_name, search_term, limit=args.limit)

        elif args.command == 'search':
            if not args.args:
                cprint("❌ Error: search requires search term", "red")
                print("Usage: memory_cli.py search <search_term>")
                sys.exit(1)
            cmd_search(args.args[0])

        elif args.command == 'export':
            if len(args.args) < 2:
                cprint("❌ Error: export requires database name and output file", "red")
                print("Usage: memory_cli.py export <database_name> <output_file>")
                sys.exit(1)
            cmd_export(args.args[0], args.args[1], format=args.format)

        elif args.command == 'optimize':
            if not args.args:
                cprint("❌ Error: optimize requires database name", "red")
                print("Usage: memory_cli.py optimize <database_name>")
                sys.exit(1)
            cmd_optimize(args.args[0])

        else:
            cprint(f"❌ Unknown command: {args.command}", "red")
            parser.print_help()
            sys.exit(1)

    except KeyboardInterrupt:
        cprint("\n\n⚠️  Interrupted by user", "yellow")
        sys.exit(0)
    except Exception as e:
        cprint(f"\n❌ Error: {e}", "red")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

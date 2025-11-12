"""
Memory Analytics and Query Utilities for MemoriSDK

Provides tools for:
- Querying memory databases
- Getting statistics and insights
- Cross-agent memory queries
- Memory management and optimization

Author: Moon Dev AI Trading System
Date: 2025-11-12
Phase: 3 (Analytics & Optimization)
"""

import os
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from collections import defaultdict
import json
from loguru import logger


class MemoryAnalytics:
    """
    Analytics and query utilities for MemoriSDK memory databases.

    Example:
        analytics = MemoryAnalytics()
        stats = analytics.get_all_stats()
        results = analytics.query_memory('trading', 'SOL', days_back=7)
    """

    def __init__(self, memory_dir: Optional[Path] = None):
        """
        Initialize memory analytics.

        Args:
            memory_dir: Path to memory databases (defaults to src/data/memory/)
        """
        if memory_dir is None:
            base_path = Path(__file__).parent.parent
            memory_dir = base_path / "data" / "memory"

        self.memory_dir = Path(memory_dir)

        if not self.memory_dir.exists():
            logger.warning(f"Memory directory not found: {self.memory_dir}")
            self.memory_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"MemoryAnalytics initialized: {self.memory_dir}")


    def get_all_databases(self) -> List[Path]:
        """
        Get list of all memory database files.

        Returns:
            List of Path objects for .db files
        """
        if not self.memory_dir.exists():
            return []

        return list(self.memory_dir.glob("*.db"))


    def get_database_info(self, db_path: Path) -> Dict[str, Any]:
        """
        Get information about a specific database.

        Args:
            db_path: Path to database file

        Returns:
            Dictionary with database info
        """
        if not db_path.exists():
            return {"error": "Database not found"}

        info = {
            "name": db_path.name,
            "path": str(db_path),
            "size_mb": db_path.stat().st_size / (1024 * 1024),
            "modified": datetime.fromtimestamp(db_path.stat().st_mtime).isoformat(),
            "tables": [],
            "total_memories": 0
        }

        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            # Get tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            info["tables"] = [row[0] for row in cursor.fetchall()]

            # Get memory counts
            if "long_term_memory" in info["tables"]:
                cursor.execute("SELECT COUNT(*) FROM long_term_memory")
                info["long_term_count"] = cursor.fetchone()[0]

            if "short_term_memory" in info["tables"]:
                cursor.execute("SELECT COUNT(*) FROM short_term_memory")
                info["short_term_count"] = cursor.fetchone()[0]

            if "chat_history" in info["tables"]:
                cursor.execute("SELECT COUNT(*) FROM chat_history")
                info["chat_history_count"] = cursor.fetchone()[0]

            info["total_memories"] = (
                info.get("long_term_count", 0) +
                info.get("short_term_count", 0) +
                info.get("chat_history_count", 0)
            )

            conn.close()

        except Exception as e:
            logger.error(f"Error getting database info: {e}")
            info["error"] = str(e)

        return info


    def get_all_stats(self) -> Dict[str, Dict]:
        """
        Get statistics for all memory databases.

        Returns:
            Dictionary mapping database names to their stats
        """
        stats = {}
        databases = self.get_all_databases()

        for db_path in databases:
            stats[db_path.stem] = self.get_database_info(db_path)

        return stats


    def query_memory(
        self,
        db_name: str,
        search_term: str = None,
        days_back: int = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Query a specific memory database.

        Args:
            db_name: Database name (e.g., 'trading_agent', 'market_analysis_shared')
            search_term: Optional search term for filtering
            days_back: Optional number of days to look back
            limit: Maximum number of results

        Returns:
            List of memory entries
        """
        # Find database file
        db_file = self.memory_dir / f"{db_name}.db"
        if not db_file.exists():
            # Try without .db extension
            db_file = self.memory_dir / db_name
            if not db_file.exists():
                logger.error(f"Database not found: {db_name}")
                return []

        results = []

        try:
            conn = sqlite3.connect(str(db_file))
            conn.row_factory = sqlite3.Row  # Return rows as dictionaries
            cursor = conn.cursor()

            # Build query based on available tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]

            # Query long-term memory
            if "long_term_memory" in tables:
                query = "SELECT * FROM long_term_memory"
                params = []

                if days_back:
                    # Note: Assuming timestamp column exists
                    # Adjust based on actual schema
                    query += " WHERE created_at >= datetime('now', ?)"
                    params.append(f'-{days_back} days')

                query += f" ORDER BY created_at DESC LIMIT {limit}"

                cursor.execute(query, params if params else ())
                for row in cursor.fetchall():
                    entry = dict(row)
                    entry['source'] = 'long_term_memory'
                    entry['database'] = db_name
                    results.append(entry)

            # Query chat history
            if "chat_history" in tables:
                query = "SELECT * FROM chat_history"
                params = []

                if search_term:
                    query += " WHERE content LIKE ?"
                    params.append(f'%{search_term}%')

                query += f" ORDER BY timestamp DESC LIMIT {limit}"

                cursor.execute(query, params if params else ())
                for row in cursor.fetchall():
                    entry = dict(row)
                    entry['source'] = 'chat_history'
                    entry['database'] = db_name
                    results.append(entry)

            conn.close()

        except Exception as e:
            logger.error(f"Error querying memory: {e}")

        return results[:limit]


    def query_shared_pool(self, pool_name: str, search_term: str = None) -> List[Dict]:
        """
        Query a shared memory pool.

        Args:
            pool_name: Pool name (market_analysis, strategy, content)
            search_term: Optional search term

        Returns:
            List of memory entries from the pool
        """
        pool_mapping = {
            'market_analysis': 'market_analysis_shared',
            'strategy': 'strategy_development',
            'content': 'content_creation'
        }

        db_name = pool_mapping.get(pool_name, pool_name)
        return self.query_memory(db_name, search_term=search_term)


    def get_top_entities(self, db_name: str, limit: int = 10) -> Dict[str, int]:
        """
        Get most frequently mentioned entities in a database.

        Args:
            db_name: Database name
            limit: Number of top entities to return

        Returns:
            Dictionary mapping entities to their frequency
        """
        # This is a simplified version - actual implementation would need
        # to parse memory content and extract entities
        logger.info(f"Getting top entities for {db_name}")

        memories = self.query_memory(db_name, limit=1000)

        # Simple word frequency analysis
        # In production, use NLP/entity extraction
        entity_count = defaultdict(int)

        for memory in memories:
            # Extract content from memory entry
            content = ""
            if 'content' in memory:
                content = memory['content']
            elif 'message' in memory:
                content = memory['message']
            elif 'data' in memory:
                try:
                    data = json.loads(memory['data'])
                    content = str(data)
                except:
                    content = str(memory['data'])

            # Simple tokenization (improve with NLP)
            words = content.upper().split()
            for word in words:
                # Look for common tokens
                if word in ['SOL', 'BTC', 'ETH', 'USDC', 'USDT']:
                    entity_count[word] += 1

        # Return top N
        sorted_entities = sorted(entity_count.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_entities[:limit])


    def get_memory_timeline(self, db_name: str, days: int = 7) -> List[Dict]:
        """
        Get memory creation timeline for the last N days.

        Args:
            db_name: Database name
            days: Number of days to analyze

        Returns:
            List of day-wise memory counts
        """
        db_file = self.memory_dir / f"{db_name}.db"
        if not db_file.exists():
            return []

        timeline = []

        try:
            conn = sqlite3.connect(str(db_file))
            cursor = conn.cursor()

            # Get tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]

            if "chat_history" in tables:
                # Query for daily counts
                query = """
                    SELECT
                        DATE(timestamp) as date,
                        COUNT(*) as count
                    FROM chat_history
                    WHERE timestamp >= datetime('now', ?)
                    GROUP BY DATE(timestamp)
                    ORDER BY date DESC
                """

                cursor.execute(query, (f'-{days} days',))
                for row in cursor.fetchall():
                    timeline.append({
                        'date': row[0],
                        'count': row[1],
                        'database': db_name
                    })

            conn.close()

        except Exception as e:
            logger.error(f"Error getting timeline: {e}")

        return timeline


    def export_memory(
        self,
        db_name: str,
        output_file: str,
        format: str = 'json'
    ) -> bool:
        """
        Export memory database to file.

        Args:
            db_name: Database name
            output_file: Output file path
            format: Export format (json, csv)

        Returns:
            True if successful
        """
        memories = self.query_memory(db_name, limit=10000)

        try:
            if format == 'json':
                with open(output_file, 'w') as f:
                    json.dump(memories, f, indent=2, default=str)
                logger.success(f"Exported {len(memories)} memories to {output_file}")
                return True

            elif format == 'csv':
                import csv
                if memories:
                    keys = memories[0].keys()
                    with open(output_file, 'w', newline='') as f:
                        writer = csv.DictWriter(f, fieldnames=keys)
                        writer.writeheader()
                        writer.writerows(memories)
                    logger.success(f"Exported {len(memories)} memories to {output_file}")
                    return True

        except Exception as e:
            logger.error(f"Error exporting memory: {e}")
            return False


    def optimize_database(self, db_name: str) -> bool:
        """
        Optimize a memory database (VACUUM).

        Args:
            db_name: Database name

        Returns:
            True if successful
        """
        db_file = self.memory_dir / f"{db_name}.db"
        if not db_file.exists():
            logger.error(f"Database not found: {db_name}")
            return False

        try:
            conn = sqlite3.connect(str(db_file))
            cursor = conn.cursor()

            # Get size before
            size_before = db_file.stat().st_size / (1024 * 1024)

            # Run VACUUM
            cursor.execute("VACUUM")
            conn.commit()
            conn.close()

            # Get size after
            size_after = db_file.stat().st_size / (1024 * 1024)
            saved = size_before - size_after

            logger.success(
                f"Optimized {db_name}: {size_before:.2f} MB → {size_after:.2f} MB "
                f"(saved {saved:.2f} MB)"
            )
            return True

        except Exception as e:
            logger.error(f"Error optimizing database: {e}")
            return False


    def get_summary(self) -> Dict:
        """
        Get a summary of the entire memory system.

        Returns:
            Dictionary with system-wide statistics
        """
        databases = self.get_all_databases()
        stats = self.get_all_stats()

        total_size = sum(info.get('size_mb', 0) for info in stats.values())
        total_memories = sum(info.get('total_memories', 0) for info in stats.values())

        summary = {
            'total_databases': len(databases),
            'total_size_mb': round(total_size, 2),
            'total_memories': total_memories,
            'databases': {}
        }

        # Categorize databases
        for db_name, info in stats.items():
            if 'shared' in db_name:
                category = 'shared_pools'
            else:
                category = 'individual_agents'

            if category not in summary['databases']:
                summary['databases'][category] = []

            summary['databases'][category].append({
                'name': db_name,
                'size_mb': round(info.get('size_mb', 0), 2),
                'memories': info.get('total_memories', 0)
            })

        return summary


# Convenience functions

def print_summary():
    """Print a formatted summary of the memory system."""
    analytics = MemoryAnalytics()
    summary = analytics.get_summary()

    print("\n" + "="*80)
    print("  MEMORY SYSTEM SUMMARY")
    print("="*80)

    print(f"\n📊 Overview:")
    print(f"  Total Databases: {summary['total_databases']}")
    print(f"  Total Size: {summary['total_size_mb']} MB")
    print(f"  Total Memories: {summary['total_memories']}")

    if 'shared_pools' in summary['databases']:
        print(f"\n🌊 Shared Memory Pools:")
        for db in summary['databases']['shared_pools']:
            print(f"  • {db['name']:<30} {db['size_mb']:>6.2f} MB  ({db['memories']:>5} memories)")

    if 'individual_agents' in summary['databases']:
        print(f"\n🤖 Individual Agent Memories:")
        for db in summary['databases']['individual_agents']:
            print(f"  • {db['name']:<30} {db['size_mb']:>6.2f} MB  ({db['memories']:>5} memories)")

    print("\n" + "="*80 + "\n")


def query_all_agents(search_term: str, limit: int = 50):
    """
    Query all agent memories for a search term.

    Args:
        search_term: Term to search for
        limit: Results per database
    """
    analytics = MemoryAnalytics()
    databases = analytics.get_all_databases()

    print(f"\n🔍 Searching all agents for: '{search_term}'")
    print("="*80)

    total_results = 0

    for db_path in databases:
        db_name = db_path.stem
        results = analytics.query_memory(db_name, search_term=search_term, limit=limit)

        if results:
            print(f"\n📁 {db_name} ({len(results)} results)")
            for i, result in enumerate(results[:5], 1):
                content = result.get('content', result.get('message', 'No content'))
                print(f"  {i}. {content[:100]}...")

            total_results += len(results)

    print(f"\n📊 Total results: {total_results}")
    print("="*80 + "\n")


# Main execution for testing
if __name__ == "__main__":
    print("\n🧠 MemoriSDK Analytics & Query Utilities\n")

    # Test analytics
    analytics = MemoryAnalytics()

    # Print summary
    print_summary()

    # Test queries
    print("\n📊 Database Statistics:")
    stats = analytics.get_all_stats()
    for db_name, info in stats.items():
        print(f"\n{db_name}:")
        print(f"  Size: {info.get('size_mb', 0):.2f} MB")
        print(f"  Tables: {', '.join(info.get('tables', []))}")
        print(f"  Total memories: {info.get('total_memories', 0)}")

    # Test export
    print("\n📤 Testing export functionality...")
    if stats:
        first_db = list(stats.keys())[0]
        output_file = f"/tmp/memory_export_{first_db}.json"
        success = analytics.export_memory(first_db, output_file, format='json')
        if success:
            print(f"✅ Exported to: {output_file}")

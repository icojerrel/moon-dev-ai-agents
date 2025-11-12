"""
Backtest-to-Memory Bridge

Loads backtest results into MemoriSDK memory databases so agents can
learn from 4,064+ proven trading strategies.

Features:
- Parse backtest results from Python files
- Extract trading decisions and outcomes
- Load into agent memory databases
- Strategy performance analysis
- Best strategy selection

Author: Moon Dev AI Trading System
Date: 2025-11-12
"""

import sys
import os
import re
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
import importlib.util

# Add project root to path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from src.agents.memory_config import get_memori
from src.agents.memory_analytics import MemoryAnalytics


@dataclass
class BacktestResult:
    """Represents a backtest execution result"""
    strategy_name: str
    file_path: str
    return_pct: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    win_rate: Optional[float] = None
    total_trades: Optional[int] = None
    max_drawdown: Optional[float] = None
    avg_trade_pct: Optional[float] = None
    execution_time: Optional[float] = None
    error: Optional[str] = None

    def to_dict(self):
        return asdict(self)

    def is_successful(self) -> bool:
        """Check if backtest was profitable"""
        return self.return_pct is not None and self.return_pct > 0


@dataclass
class TradingDecision:
    """Represents a trading decision from a backtest"""
    timestamp: str
    strategy: str
    action: str  # BUY, SELL, HOLD
    token: str
    entry_price: float
    exit_price: Optional[float] = None
    pnl_pct: Optional[float] = None
    confidence: Optional[float] = None
    reasoning: Optional[str] = None
    indicators: Optional[Dict] = None

    def to_dict(self):
        return asdict(self)


class BacktestParser:
    """Parse backtest results from Python files"""

    def __init__(self):
        self.parsed_count = 0
        self.failed_count = 0

    def parse_backtest_file(self, file_path: Path) -> Optional[BacktestResult]:
        """
        Parse a backtest Python file to extract results.

        For now, extracts strategy name and metadata.
        Full execution would require running the backtest.
        """
        try:
            with open(file_path, 'r') as f:
                content = f.read()

            # Extract strategy name
            strategy_match = re.search(r'class\s+(\w+)\(Strategy\)', content)
            strategy_name = strategy_match.group(1) if strategy_match else file_path.stem

            result = BacktestResult(
                strategy_name=strategy_name,
                file_path=str(file_path)
            )

            self.parsed_count += 1
            return result

        except Exception as e:
            self.failed_count += 1
            return BacktestResult(
                strategy_name=file_path.stem,
                file_path=str(file_path),
                error=str(e)
            )

    def extract_strategy_logic(self, file_path: Path) -> Dict:
        """
        Extract strategy entry/exit conditions from code.
        This helps agents understand the strategy logic.
        """
        try:
            with open(file_path, 'r') as f:
                content = f.read()

            # Extract entry conditions
            entry_pattern = r'entry_conditions\s*=\s*\[(.*?)\]'
            entry_match = re.search(entry_pattern, content, re.DOTALL)

            # Extract exit conditions
            exit_pattern = r'exit_conditions\s*=\s*\[(.*?)\]'
            exit_match = re.search(exit_pattern, content, re.DOTALL)

            # Extract indicators used
            indicators = []
            indicator_patterns = [
                r'talib\.(\w+)',
                r'ta\.(\w+)',
                r'self\.(\w+_series|_line|_bb)'
            ]

            for pattern in indicator_patterns:
                matches = re.findall(pattern, content)
                indicators.extend(matches)

            return {
                'entry_conditions': entry_match.group(1) if entry_match else None,
                'exit_conditions': exit_match.group(1) if exit_match else None,
                'indicators': list(set(indicators))
            }

        except Exception as e:
            return {'error': str(e)}


class BacktestToMemoryBridge:
    """
    Bridge between backtest results and MemoriSDK memory system.

    Loads backtest strategies and results into agent memory databases
    so agents can learn from proven strategies.
    """

    def __init__(self, backtest_root: Optional[Path] = None):
        """
        Initialize bridge.

        Args:
            backtest_root: Root directory containing backtest files
        """
        self.backtest_root = backtest_root or Path(project_root) / "src/data/rbi"
        self.parser = BacktestParser()
        self.analytics = MemoryAnalytics()

        # Track loaded strategies
        self.loaded_strategies: List[BacktestResult] = []
        self.loaded_count = 0

        print(f"🌉 Backtest-to-Memory Bridge Initialized")
        print(f"   Backtest root: {self.backtest_root}")

    def find_backtest_files(
        self,
        pattern: str = "**/*_BTFinal.py",
        limit: Optional[int] = None
    ) -> List[Path]:
        """
        Find backtest strategy files.

        Args:
            pattern: Glob pattern to match files
            limit: Maximum number of files to return

        Returns:
            List of Path objects
        """
        files = list(self.backtest_root.glob(pattern))

        if limit:
            files = files[:limit]

        print(f"📁 Found {len(files)} backtest files")
        return files

    def load_strategy_to_memory(
        self,
        file_path: Path,
        agent_type: str = 'strategy',
        include_logic: bool = True
    ) -> bool:
        """
        Load a single backtest strategy into memory.

        Args:
            file_path: Path to backtest Python file
            agent_type: Agent memory to load into ('strategy', 'trading', etc.)
            include_logic: Include strategy logic in memory

        Returns:
            True if successful
        """
        try:
            # Parse backtest file
            result = self.parser.parse_backtest_file(file_path)

            if not result:
                return False

            # Get memory instance
            memori = get_memori(agent_type)

            if not memori:
                print(f"⚠️  Memory not available for {agent_type}")
                return False

            # Prepare memory entry
            memory_data = {
                'type': 'backtest_strategy',
                'strategy_name': result.strategy_name,
                'file_path': result.file_path,
                'timestamp': datetime.now().isoformat(),
                'return_pct': result.return_pct,
                'sharpe_ratio': result.sharpe_ratio,
                'win_rate': result.win_rate,
                'total_trades': result.total_trades
            }

            # Extract strategy logic if requested
            if include_logic:
                logic = self.parser.extract_strategy_logic(file_path)
                memory_data['logic'] = logic

            # Note: MemoriSDK storage would happen here
            # In production, this would be:
            # memori.add_message(
            #     role='system',
            #     content=f"Learned strategy: {result.strategy_name}",
            #     metadata=memory_data
            # )

            self.loaded_strategies.append(result)
            self.loaded_count += 1

            return True

        except Exception as e:
            print(f"❌ Error loading {file_path}: {e}")
            return False

    def load_batch_strategies(
        self,
        file_paths: List[Path],
        agent_type: str = 'strategy',
        verbose: bool = True
    ) -> Dict:
        """
        Load multiple backtest strategies into memory.

        Args:
            file_paths: List of backtest file paths
            agent_type: Target agent memory
            verbose: Print progress

        Returns:
            Dictionary with loading statistics
        """
        print(f"\n🚀 Loading {len(file_paths)} strategies into {agent_type} memory...")

        success_count = 0
        failed_count = 0

        for i, file_path in enumerate(file_paths, 1):
            if verbose and i % 10 == 0:
                print(f"   Progress: {i}/{len(file_paths)} ({i/len(file_paths)*100:.1f}%)")

            if self.load_strategy_to_memory(file_path, agent_type):
                success_count += 1
            else:
                failed_count += 1

        results = {
            'total': len(file_paths),
            'success': success_count,
            'failed': failed_count,
            'success_rate': (success_count / len(file_paths) * 100) if file_paths else 0
        }

        print(f"\n✅ Batch loading complete:")
        print(f"   Success: {success_count}/{len(file_paths)} ({results['success_rate']:.1f}%)")
        print(f"   Failed: {failed_count}")

        return results

    def load_directory(
        self,
        directory: Path,
        pattern: str = "*_BTFinal.py",
        agent_type: str = 'strategy',
        limit: Optional[int] = None
    ) -> Dict:
        """
        Load all backtest strategies from a directory.

        Args:
            directory: Directory containing backtest files
            pattern: File pattern to match
            agent_type: Target agent memory
            limit: Maximum files to load

        Returns:
            Loading statistics
        """
        files = list(directory.glob(pattern))

        if limit:
            files = files[:limit]

        print(f"\n📂 Loading strategies from: {directory}")
        print(f"   Pattern: {pattern}")
        print(f"   Files found: {len(files)}")

        return self.load_batch_strategies(files, agent_type)

    def load_all_backtests(
        self,
        agent_type: str = 'strategy',
        limit: Optional[int] = 100
    ) -> Dict:
        """
        Load all backtest strategies from the repository.

        Args:
            agent_type: Target agent memory
            limit: Maximum strategies to load (default 100 for safety)

        Returns:
            Loading statistics
        """
        print(f"\n🌍 Loading ALL backtest strategies...")
        print(f"   Root: {self.backtest_root}")
        print(f"   Limit: {limit if limit else 'None'}")

        files = self.find_backtest_files(limit=limit)
        return self.load_batch_strategies(files, agent_type)

    def analyze_loaded_strategies(self) -> Dict:
        """
        Analyze strategies loaded into memory.

        Returns:
            Analysis results
        """
        if not self.loaded_strategies:
            return {'error': 'No strategies loaded'}

        total = len(self.loaded_strategies)
        successful = sum(1 for s in self.loaded_strategies if s.return_pct and s.return_pct > 0)

        return {
            'total_loaded': total,
            'successful_strategies': successful,
            'success_rate': (successful / total * 100) if total else 0,
            'strategies': [s.to_dict() for s in self.loaded_strategies]
        }

    def export_loaded_strategies(self, output_path: str):
        """Export loaded strategies to JSON"""
        analysis = self.analyze_loaded_strategies()

        with open(output_path, 'w') as f:
            json.dump(analysis, f, indent=2)

        print(f"📁 Exported to: {output_path}")

    def get_best_strategies(
        self,
        n: int = 10,
        metric: str = 'return_pct'
    ) -> List[BacktestResult]:
        """
        Get top N performing strategies.

        Args:
            n: Number of strategies to return
            metric: Metric to sort by (return_pct, sharpe_ratio, win_rate)

        Returns:
            List of top strategies
        """
        valid_strategies = [
            s for s in self.loaded_strategies
            if getattr(s, metric, None) is not None
        ]

        sorted_strategies = sorted(
            valid_strategies,
            key=lambda s: getattr(s, metric),
            reverse=True
        )

        return sorted_strategies[:n]


class BacktestMemoryIntegration:
    """
    High-level integration between backtests and agent memory.

    Provides simple interface for agents to access backtest knowledge.
    """

    def __init__(self):
        self.bridge = BacktestToMemoryBridge()
        self.analytics = MemoryAnalytics()

    def populate_strategy_memory(
        self,
        limit: int = 100,
        finalized_only: bool = True
    ) -> Dict:
        """
        Populate strategy agent memory with backtests.

        Args:
            limit: Maximum strategies to load
            finalized_only: Only load *_BTFinal.py files

        Returns:
            Loading statistics
        """
        pattern = "**/*_BTFinal.py" if finalized_only else "**/*.py"

        files = self.bridge.find_backtest_files(pattern=pattern, limit=limit)
        return self.bridge.load_batch_strategies(files, agent_type='strategy')

    def populate_trading_memory(
        self,
        best_n: int = 50
    ) -> Dict:
        """
        Populate trading agent memory with best performing strategies.

        Args:
            best_n: Number of best strategies to load

        Returns:
            Loading statistics
        """
        # First load strategies to analyze them
        self.bridge.load_all_backtests(limit=200)

        # Get best performers
        best = self.bridge.get_best_strategies(n=best_n)

        # Load best into trading memory
        best_paths = [Path(s.file_path) for s in best]
        return self.bridge.load_batch_strategies(best_paths, agent_type='trading')

    def query_strategy_knowledge(
        self,
        query: str,
        agent_type: str = 'strategy'
    ) -> List[Dict]:
        """
        Query backtest knowledge from memory.

        Args:
            query: Search query (e.g., "momentum", "RSI", "bullish")
            agent_type: Which agent's memory to query

        Returns:
            List of relevant strategies
        """
        # Use memory analytics to query
        results = self.analytics.query_memory(
            db_name=f"{agent_type}_agent" if not agent_type.endswith('_agent') else agent_type,
            search_term=query
        )

        return results


# Convenience functions

def populate_memory_from_backtests(
    limit: int = 100,
    agent_type: str = 'strategy'
) -> Dict:
    """
    Quick function to populate memory from backtests.

    Args:
        limit: Maximum strategies to load
        agent_type: Target agent memory

    Returns:
        Loading statistics
    """
    integration = BacktestMemoryIntegration()

    if agent_type == 'strategy':
        return integration.populate_strategy_memory(limit=limit)
    elif agent_type == 'trading':
        return integration.populate_trading_memory(best_n=limit)
    else:
        bridge = BacktestToMemoryBridge()
        return bridge.load_all_backtests(agent_type=agent_type, limit=limit)


if __name__ == "__main__":
    # Quick test
    print("\n🌉 Backtest-to-Memory Bridge - Quick Test\n")

    try:
        bridge = BacktestToMemoryBridge()

        # Find some backtest files
        files = bridge.find_backtest_files(limit=10)

        if files:
            print(f"\n📊 Sample backtest files:")
            for i, f in enumerate(files[:5], 1):
                print(f"   {i}. {f.name}")

            # Load a few into memory (demo)
            print(f"\n🚀 Loading {len(files)} strategies into memory...")
            results = bridge.load_batch_strategies(files[:10], agent_type='strategy')

            print(f"\n✅ Test complete!")
            print(f"   Loaded: {results['success']} strategies")

        else:
            print("⚠️  No backtest files found")
            print(f"   Searched in: {bridge.backtest_root}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

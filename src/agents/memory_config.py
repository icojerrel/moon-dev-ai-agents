"""
Centralized MemoriSDK Configuration for Moon Dev AI Agents

This module provides a unified memory configuration system for all agents,
enabling persistent memory, cross-session learning, and shared knowledge pools.

Usage:
    from src.agents.memory_config import get_memori

    # In any agent __init__:
    self.memori = get_memori('trading')
    self.memori.enable()

Author: Moon Dev AI Trading System
Date: 2025-11-12
"""

import os
from pathlib import Path
from typing import Dict, Optional
from loguru import logger

# Conditional import - gracefully handle if memorisdk not installed
try:
    from memori import Memori
    MEMORISDK_AVAILABLE = True
except ImportError:
    logger.warning("MemoriSDK not installed. Run: pip install memorisdk")
    MEMORISDK_AVAILABLE = False
    Memori = None


# Memory storage directory
MEMORY_DIR = Path(__file__).parent.parent / "data" / "memory"
MEMORY_DIR.mkdir(parents=True, exist_ok=True)


# Memory configuration per agent type
MEMORY_CONFIGS: Dict[str, dict] = {
    # Chat agents - auto mode for dynamic context retrieval
    'chat': {
        'mode': 'auto',
        'db': 'chat_agent.db',
        'shared': False,
        'description': 'Chat agent with automatic context injection'
    },

    # Trading agents - combined mode (conscious + auto) for critical decisions
    'trading': {
        'mode': 'combined',
        'db': 'trading_agent.db',
        'shared': False,
        'description': 'Trading agent with both conscious and auto memory'
    },

    # Risk management - conscious mode for explicit risk context
    'risk': {
        'mode': 'conscious',
        'db': 'risk_agent.db',
        'shared': False,
        'description': 'Risk agent with conscious memory injection'
    },

    # Market analysis agents - shared database for coordinated insights
    'market_analysis': {
        'mode': 'auto',
        'db': 'market_analysis_shared.db',
        'shared': True,
        'description': 'Shared memory for whale, sentiment, funding agents'
    },

    # Strategy development - shared for RBI, research, strategy agents
    'strategy': {
        'mode': 'auto',
        'db': 'strategy_development.db',
        'shared': True,
        'description': 'Shared memory for strategy development agents'
    },

    # Content creation agents
    'content': {
        'mode': 'auto',
        'db': 'content_creation.db',
        'shared': True,
        'description': 'Shared memory for tweet, video, clips agents'
    },

    # Default fallback configuration
    'default': {
        'mode': 'auto',
        'db': 'default_agent.db',
        'shared': False,
        'description': 'Default memory configuration'
    }
}


def get_memori(
    agent_type: str = 'default',
    custom_db_path: Optional[str] = None,
    mode: Optional[str] = None,
    disable: bool = False
) -> Optional[Memori]:
    """
    Factory function to get configured Memori instance for an agent.

    Args:
        agent_type: Type of agent (chat, trading, risk, market_analysis, etc.)
        custom_db_path: Optional custom database path (overrides config)
        mode: Optional mode override (auto, conscious, combined)
        disable: If True, returns None (for A/B testing or debugging)

    Returns:
        Configured Memori instance or None if disabled/unavailable

    Example:
        # Standard usage
        memori = get_memori('trading')
        if memori:
            memori.enable()

        # Custom configuration
        memori = get_memori('custom', custom_db_path='./my_memory.db', mode='conscious')

        # Disable memory for testing
        memori = get_memori('trading', disable=True)  # Returns None
    """

    # Return None if explicitly disabled
    if disable:
        logger.info(f"Memory disabled for agent type: {agent_type}")
        return None

    # Check if MemoriSDK is available
    if not MEMORISDK_AVAILABLE:
        logger.warning(f"MemoriSDK not available for agent type: {agent_type}")
        return None

    # Get configuration for agent type
    config = MEMORY_CONFIGS.get(agent_type, MEMORY_CONFIGS['default'])

    # Determine database path
    if custom_db_path:
        db_path = custom_db_path
    else:
        db_path = str(MEMORY_DIR / config['db'])

    # Determine mode
    memory_mode = mode if mode else config['mode']

    # Log configuration
    logger.info(f"Initializing memory for {agent_type}: mode={memory_mode}, db={db_path}")
    if config['shared']:
        logger.info(f"  → Shared memory pool: {config['description']}")

    try:
        # Convert db_path to SQLite connection string
        if not db_path.startswith('sqlite:///'):
            # Ensure absolute path
            if not os.path.isabs(db_path):
                db_path = os.path.abspath(db_path)
            db_path = f"sqlite:///{db_path}"

        # Map mode to conscious_ingest and auto_ingest parameters
        conscious_ingest = memory_mode in ['conscious', 'combined']
        auto_ingest = memory_mode in ['auto', 'combined']

        # Create Memori instance
        memori = Memori(
            database_connect=db_path,
            conscious_ingest=conscious_ingest,
            auto_ingest=auto_ingest,
            shared_memory=config.get('shared', False)
        )

        logger.success(f"Memory initialized for {agent_type}")
        return memori

    except Exception as e:
        logger.error(f"Failed to initialize memory for {agent_type}: {e}")
        return None


def get_memory_stats(agent_type: str = None) -> Dict:
    """
    Get statistics about memory usage.

    Args:
        agent_type: Optional agent type to check (if None, checks all)

    Returns:
        Dictionary with memory statistics
    """
    stats = {}

    if agent_type:
        config = MEMORY_CONFIGS.get(agent_type, MEMORY_CONFIGS['default'])
        db_path = MEMORY_DIR / config['db']
        stats[agent_type] = {
            'exists': db_path.exists(),
            'size_mb': db_path.stat().st_size / (1024 * 1024) if db_path.exists() else 0,
            'shared': config['shared'],
            'mode': config['mode']
        }
    else:
        # Check all agent types
        for atype, config in MEMORY_CONFIGS.items():
            if atype == 'default':
                continue
            db_path = MEMORY_DIR / config['db']
            stats[atype] = {
                'exists': db_path.exists(),
                'size_mb': db_path.stat().st_size / (1024 * 1024) if db_path.exists() else 0,
                'shared': config['shared'],
                'mode': config['mode']
            }

    return stats


def cleanup_old_memory(days: int = 30) -> None:
    """
    Clean up old memory entries (if using SQLite, can run VACUUM).

    Args:
        days: Number of days to keep (not implemented yet - placeholder)
    """
    logger.info(f"Memory cleanup requested for entries older than {days} days")
    logger.warning("Cleanup not yet implemented - MemoriSDK handles this automatically")
    # Note: MemoriSDK has background cleanup every 6 hours
    pass


# Export main function and config
__all__ = ['get_memori', 'get_memory_stats', 'cleanup_old_memory', 'MEMORY_CONFIGS']


# Log available memory configurations on import
if __name__ != "__main__":
    logger.info("MemoriSDK configuration loaded")
    logger.info(f"Available agent types: {', '.join([k for k in MEMORY_CONFIGS.keys() if k != 'default'])}")
    logger.info(f"Memory directory: {MEMORY_DIR}")

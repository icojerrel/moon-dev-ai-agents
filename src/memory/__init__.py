"""
Memory management module for AI trading agents.

This module provides a lightweight wrapper around mem-layer for
agent coordination and persistent memory across trading sessions.
"""

from src.memory.agent_memory import AgentMemory
from src.memory.memory_config import MemoryScope, MemoryConfig

__all__ = ['AgentMemory', 'MemoryScope', 'MemoryConfig']

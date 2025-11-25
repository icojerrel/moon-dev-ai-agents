"""
🌙 Moon Dev's Structured Event System
Built with love by Moon Dev 🚀

Enables web UI integration without modifying agent code structure.
Based on patterns from autonomous-researcher.

Usage:
    from src.utils.event_emitter import emit_trading_event

    # In your agent:
    emit_trading_event("TRADE_EXECUTED", {
        "token": token_address,
        "action": "BUY",
        "amount_usd": 25.0,
        "price": 0.00123
    })

    # Enable events via environment variable:
    export MOONDEV_ENABLE_EVENTS=true
"""

import os
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum


class EventType(Enum):
    """Standard event types for Moon Dev trading system"""

    # Trading Events
    TRADE_EXECUTED = "TRADE_EXECUTED"
    POSITION_OPENED = "POSITION_OPENED"
    POSITION_CLOSED = "POSITION_CLOSED"
    ORDER_FILLED = "ORDER_FILLED"
    ORDER_CANCELLED = "ORDER_CANCELLED"

    # Analysis Events
    WHALE_DETECTED = "WHALE_DETECTED"
    SENTIMENT_CHANGE = "SENTIMENT_CHANGE"
    FUNDING_ALERT = "FUNDING_ALERT"
    LIQUIDATION_SPIKE = "LIQUIDATION_SPIKE"

    # Risk Events
    RISK_WARNING = "RISK_WARNING"
    RISK_BREACH = "RISK_BREACH"
    CIRCUIT_BREAKER = "CIRCUIT_BREAKER"
    POSITION_LIMIT = "POSITION_LIMIT"

    # Agent Events
    AGENT_START = "AGENT_START"
    AGENT_COMPLETE = "AGENT_COMPLETE"
    AGENT_ERROR = "AGENT_ERROR"
    ANALYSIS_START = "ANALYSIS_START"
    ANALYSIS_COMPLETE = "ANALYSIS_COMPLETE"

    # Backtest Events
    BACKTEST_START = "BACKTEST_START"
    BACKTEST_COMPLETE = "BACKTEST_COMPLETE"
    STRATEGY_GENERATED = "STRATEGY_GENERATED"

    # Market Events
    PRICE_ALERT = "PRICE_ALERT"
    VOLUME_SPIKE = "VOLUME_SPIKE"
    NEW_TOKEN_DETECTED = "NEW_TOKEN_DETECTED"


def emit_event(event_type: str, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
    """
    Emit a structured event for web UI consumption

    Events are only emitted when MOONDEV_ENABLE_EVENTS environment variable is set.
    This keeps CLI output clean while enabling rich web UI integration.

    Args:
        event_type: Type of event (use EventType enum or string)
        data: Event-specific data dictionary
        metadata: Optional metadata (agent name, session ID, etc.)

    Event format:
        ::MOONDEV_EVENT::{"type": "TRADE_EXECUTED", "timestamp": "...", "data": {...}, "metadata": {...}}
    """
    if not os.environ.get("MOONDEV_ENABLE_EVENTS"):
        return

    # Handle EventType enum
    if isinstance(event_type, EventType):
        event_type = event_type.value

    payload = {
        "type": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        "data": data,
        "metadata": metadata or {}
    }

    # Use special prefix that frontend parser can look for
    print(f"::MOONDEV_EVENT::{json.dumps(payload)}")
    sys.stdout.flush()


# Convenience functions for common events

def emit_trading_event(action: str, token: str, amount_usd: float, price: float,
                       success: bool = True, agent: str = "unknown"):
    """
    Emit a trading event (BUY/SELL)

    Args:
        action: BUY or SELL
        token: Token address
        amount_usd: Trade amount in USD
        price: Execution price
        success: Whether trade was successful
        agent: Name of agent executing trade
    """
    emit_event(EventType.TRADE_EXECUTED, {
        "action": action,
        "token": token,
        "amount_usd": amount_usd,
        "price": price,
        "success": success,
        "agent": agent
    })


def emit_whale_event(token: str, whale_address: str, action: str, amount: float):
    """
    Emit a whale activity detection event

    Args:
        token: Token address
        whale_address: Whale wallet address
        action: What the whale did (BUY, SELL, TRANSFER)
        amount: Amount in tokens
    """
    emit_event(EventType.WHALE_DETECTED, {
        "token": token,
        "whale_address": whale_address,
        "action": action,
        "amount": amount
    })


def emit_risk_event(level: str, message: str, current_loss: float = None,
                    positions_affected: list = None):
    """
    Emit a risk management event

    Args:
        level: WARNING, BREACH, or CIRCUIT_BREAKER
        message: Risk message
        current_loss: Current loss in USD (if applicable)
        positions_affected: List of affected positions
    """
    event_map = {
        "WARNING": EventType.RISK_WARNING,
        "BREACH": EventType.RISK_BREACH,
        "CIRCUIT_BREAKER": EventType.CIRCUIT_BREAKER
    }

    emit_event(event_map.get(level, EventType.RISK_WARNING), {
        "level": level,
        "message": message,
        "current_loss": current_loss,
        "positions_affected": positions_affected or []
    })


def emit_agent_lifecycle(agent_name: str, status: str, duration: float = None,
                         error: str = None):
    """
    Emit agent lifecycle event (start, complete, error)

    Args:
        agent_name: Name of the agent
        status: START, COMPLETE, or ERROR
        duration: Execution duration in seconds (for COMPLETE)
        error: Error message (for ERROR status)
    """
    event_map = {
        "START": EventType.AGENT_START,
        "COMPLETE": EventType.AGENT_COMPLETE,
        "ERROR": EventType.AGENT_ERROR
    }

    emit_event(event_map.get(status, EventType.AGENT_START), {
        "agent": agent_name,
        "status": status,
        "duration": duration,
        "error": error
    })


def emit_backtest_event(strategy_name: str, status: str, results: Dict[str, Any] = None):
    """
    Emit backtest event

    Args:
        strategy_name: Name of strategy being tested
        status: START or COMPLETE
        results: Backtest results (for COMPLETE status)
    """
    event_map = {
        "START": EventType.BACKTEST_START,
        "COMPLETE": EventType.BACKTEST_COMPLETE
    }

    emit_event(event_map.get(status, EventType.BACKTEST_START), {
        "strategy": strategy_name,
        "status": status,
        "results": results or {}
    })


def emit_market_event(event_type: str, token: str, value: float, threshold: float = None):
    """
    Emit market-related event (price alert, volume spike, etc.)

    Args:
        event_type: PRICE_ALERT, VOLUME_SPIKE, etc.
        token: Token address
        value: Current value
        threshold: Threshold that triggered event (if applicable)
    """
    emit_event(event_type, {
        "token": token,
        "value": value,
        "threshold": threshold
    })


# Event statistics (for debugging/monitoring)
_event_counter: Dict[str, int] = {}


def get_event_stats() -> Dict[str, int]:
    """
    Get event emission statistics

    Returns:
        Dictionary of event types and their counts
    """
    return _event_counter.copy()


def _track_event(event_type: str):
    """Internal: Track event for statistics"""
    global _event_counter
    _event_counter[event_type] = _event_counter.get(event_type, 0) + 1


# Wrap emit_event to track statistics
_original_emit = emit_event


def emit_event_tracked(event_type: str, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
    """Emit event and track statistics"""
    _track_event(event_type if isinstance(event_type, str) else event_type.value)
    return _original_emit(event_type, data, metadata)


# Replace emit_event with tracked version
emit_event = emit_event_tracked


# Export main functions
__all__ = [
    'EventType',
    'emit_event',
    'emit_trading_event',
    'emit_whale_event',
    'emit_risk_event',
    'emit_agent_lifecycle',
    'emit_backtest_event',
    'emit_market_event',
    'get_event_stats',
]

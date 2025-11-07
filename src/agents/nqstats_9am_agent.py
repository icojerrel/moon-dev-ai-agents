"""
🌙 Moon Dev's 9AM Hour Continuation Agent
9AM Hour Continuation Trading Agent

Based on NQStats.com 20-year historical data (2004-2024)
Statistical Edge: 67-70% probability

Strategy:
- Trade in direction of 9am hour close (9:30am-10:30am EST)
- If 9am hour closes green → 67% probability entire session closes green
- If 9am hour closes green → 70% probability NY session (4pm > 9:30am) closes green
- Highest probability continuation edge in NQStats data

Built with love by Moon Dev 🚀
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, time as dt_time, timedelta
from termcolor import cprint
from pathlib import Path

# Add project root to path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.nice_funcs import token_price, get_ohlcv_data, token_overview
from src.config import AI_MODEL, AI_MAX_TOKENS, AI_TEMPERATURE

# ============================================================================
# CONFIGURATION
# ============================================================================

# 9AM Hour parameters from NQStats (20-year data)
SESSION_CLOSE_PROBABILITY = 67  # % probability entire session closes in 9am hour direction
NY_SESSION_PROBABILITY = 70  # % probability NY session (4pm > 9:30am) closes in 9am hour direction

# 9AM Hour times (EST)
HOUR_9AM_START_HOUR = 9
HOUR_9AM_START_MINUTE = 30
HOUR_9AM_END_HOUR = 10
HOUR_9AM_END_MINUTE = 30

# Session times (EST)
SESSION_OPEN_HOUR = 9
SESSION_OPEN_MINUTE = 30
SESSION_CLOSE_HOUR = 16
SESSION_CLOSE_MINUTE = 0

# Trading parameters
MIN_CONFIDENCE = 60  # Minimum confidence % to trade
POSITION_SIZE_PERCENT = 2.0  # % of portfolio per trade

# ============================================================================
# 9AM HOUR CALCULATION FUNCTIONS
# ============================================================================

def get_9am_hour_data(df, current_date):
    """
    Get 9am hour data (9:30am-10:30am EST)

    Returns: dict with hour_9am_open, hour_9am_close, hour_9am_high, hour_9am_low, direction
    """
    # Calculate 9am hour timeframe
    hour_9am_start = datetime.combine(
        current_date,
        dt_time(HOUR_9AM_START_HOUR, HOUR_9AM_START_MINUTE)
    )
    hour_9am_end = datetime.combine(
        current_date,
        dt_time(HOUR_9AM_END_HOUR, HOUR_9AM_END_MINUTE)
    )

    # Filter data for 9am hour
    hour_9am_data = df[
        (df.index >= hour_9am_start) &
        (df.index <= hour_9am_end)
    ]

    if len(hour_9am_data) == 0:
        return None

    hour_9am_open = hour_9am_data['open'].iloc[0]
    hour_9am_close = hour_9am_data['close'].iloc[-1]
    hour_9am_high = hour_9am_data['high'].max()
    hour_9am_low = hour_9am_data['low'].min()
    hour_9am_range = hour_9am_high - hour_9am_low

    # Determine direction
    if hour_9am_close > hour_9am_open:
        direction = 'BULLISH'
        move_size = hour_9am_close - hour_9am_open
    elif hour_9am_close < hour_9am_open:
        direction = 'BEARISH'
        move_size = hour_9am_open - hour_9am_close
    else:
        direction = 'NEUTRAL'
        move_size = 0

    return {
        'hour_9am_open': hour_9am_open,
        'hour_9am_close': hour_9am_close,
        'hour_9am_high': hour_9am_high,
        'hour_9am_low': hour_9am_low,
        'hour_9am_range': hour_9am_range,
        'direction': direction,
        'move_size': move_size,
        'move_percent': (move_size / hour_9am_open * 100) if hour_9am_open > 0 else 0
    }

def check_hour_complete(current_time):
    """
    Check if 9am hour is complete (past 10:30am)

    Returns: bool, minutes_since_completion
    """
    hour_9am_end_time = dt_time(HOUR_9AM_END_HOUR, HOUR_9AM_END_MINUTE)
    current_time_only = current_time.time()

    if current_time_only >= hour_9am_end_time:
        # Calculate minutes since 10:30am
        today_hour_end = datetime.combine(current_time.date(), hour_9am_end_time)
        minutes_since = (current_time - today_hour_end).total_seconds() / 60
        return True, int(minutes_since)
    else:
        return False, 0

def calculate_targets_and_stops(hour_9am_data):
    """
    Calculate target and stop loss based on 9am hour direction

    Returns: dict with signal, stop_loss, target, reasoning
    """
    direction = hour_9am_data['direction']
    hour_9am_open = hour_9am_data['hour_9am_open']
    hour_9am_close = hour_9am_data['hour_9am_close']
    hour_9am_high = hour_9am_data['hour_9am_high']
    hour_9am_low = hour_9am_data['hour_9am_low']
    hour_9am_range = hour_9am_data['hour_9am_range']

    if direction == 'BULLISH':
        # Go LONG
        signal = 'BUY'
        stop_loss = hour_9am_low  # Stop at 9am hour low
        # Target: Session high or 1.5x 9am hour range above entry
        target = hour_9am_close + (hour_9am_range * 1.5)
        reasoning = f"🟢 9AM HOUR CLOSED GREEN: {NY_SESSION_PROBABILITY}% probability NY session closes higher than 9:30am open. Trade continuation LONG. Stop at 9am hour low (${stop_loss:.4f}). Target: ${target:.4f}."

    elif direction == 'BEARISH':
        # Go SHORT
        signal = 'SELL'
        stop_loss = hour_9am_high  # Stop at 9am hour high
        # Target: Session low or 1.5x 9am hour range below entry
        target = hour_9am_close - (hour_9am_range * 1.5)
        reasoning = f"🔴 9AM HOUR CLOSED RED: {NY_SESSION_PROBABILITY}% probability NY session closes lower than 9:30am open. Trade continuation SHORT. Stop at 9am hour high (${stop_loss:.4f}). Target: ${target:.4f}."

    else:
        # NEUTRAL - no edge
        signal = 'NOTHING'
        stop_loss = None
        target = None
        reasoning = f"⚪ 9AM HOUR CLOSED FLAT: No directional edge. 9am hour open (${hour_9am_open:.4f}) equals close (${hour_9am_close:.4f}). Wait for next session."

    return {
        'signal': signal,
        'stop_loss': stop_loss,
        'target': target,
        'reasoning': reasoning
    }

def check_stop_hit(current_price, targets_stops, hour_9am_data):
    """
    Check if stop loss has been hit

    Returns: bool, reasoning
    """
    direction = hour_9am_data['direction']

    if direction == 'BULLISH':
        # Stop = 9am hour low breached
        if current_price < targets_stops['stop_loss']:
            return True, f"❌ STOP HIT: Price breached 9am hour low (${targets_stops['stop_loss']:.4f}). This is the 30% scenario where continuation failed."
        return False, None

    elif direction == 'BEARISH':
        # Stop = 9am hour high breached
        if current_price > targets_stops['stop_loss']:
            return True, f"❌ STOP HIT: Price breached 9am hour high (${targets_stops['stop_loss']:.4f}). This is the 30% scenario where continuation failed."
        return False, None

    return False, None

def check_target_hit(current_price, targets_stops, hour_9am_data):
    """
    Check if target has been hit

    Returns: bool, reasoning
    """
    direction = hour_9am_data['direction']

    if direction == 'BULLISH' and targets_stops['target']:
        if current_price >= targets_stops['target']:
            return True, f"✅ TARGET HIT: Price reached ${targets_stops['target']:.4f}. This is the {NY_SESSION_PROBABILITY}% winning scenario."
        return False, None

    elif direction == 'BEARISH' and targets_stops['target']:
        if current_price <= targets_stops['target']:
            return True, f"✅ TARGET HIT: Price reached ${targets_stops['target']:.4f}. This is the {NY_SESSION_PROBABILITY}% winning scenario."
        return False, None

    return False, None

# ============================================================================
# SIGNAL GENERATION
# ============================================================================

def generate_9am_signal(token_address):
    """
    Generate 9AM Hour Continuation trading signal

    Returns: dict with signal, confidence, reasoning
    """
    cprint(f"\n{'='*80}", "cyan")
    cprint(f"🕐 9AM HOUR CONTINUATION AGENT - {token_address}", "cyan")
    cprint(f"{'='*80}", "cyan")

    try:
        # Get OHLCV data (5-minute bars for hour precision)
        df = get_ohlcv_data(token_address, timeframe='5m', days_back=2)

        if df is None or len(df) == 0:
            return {
                'signal': 'NOTHING',
                'confidence': 0,
                'reasoning': 'No OHLCV data available'
            }

        # Get current price
        current_price = token_price(token_address)
        if not current_price:
            return {
                'signal': 'NOTHING',
                'confidence': 0,
                'reasoning': 'Unable to get current price'
            }

        # Get current time
        current_time = datetime.now()
        current_date = current_time.date()

        # Check if 9am hour is complete
        hour_complete, minutes_since = check_hour_complete(current_time)

        if not hour_complete:
            return {
                'signal': 'NOTHING',
                'confidence': 0,
                'reasoning': f'⏰ 9AM HOUR NOT COMPLETE: Currently {current_time.strftime("%H:%M")} EST. Wait until after 10:30am for 9am hour close confirmation.'
            }

        # Get 9am hour data
        hour_9am_data = get_9am_hour_data(df, current_date)
        if not hour_9am_data:
            return {
                'signal': 'NOTHING',
                'confidence': 0,
                'reasoning': 'Unable to get 9am hour data. Ensure market is open during RTH (9:30am-4pm EST).'
            }

        # Calculate targets and stops
        targets_stops = calculate_targets_and_stops(hour_9am_data)

        # Check if stop or target hit
        stop_hit, stop_reasoning = check_stop_hit(current_price, targets_stops, hour_9am_data)
        target_hit, target_reasoning = check_target_hit(current_price, targets_stops, hour_9am_data)

        # Print analysis
        cprint(f"\n📊 9AM Hour Data (9:30am-10:30am):", "yellow")
        cprint(f"  Open: ${hour_9am_data['hour_9am_open']:.4f}", "yellow")
        cprint(f"  Close: ${hour_9am_data['hour_9am_close']:.4f}", "yellow")
        cprint(f"  High: ${hour_9am_data['hour_9am_high']:.4f}", "yellow")
        cprint(f"  Low: ${hour_9am_data['hour_9am_low']:.4f}", "yellow")
        cprint(f"  Range: ${hour_9am_data['hour_9am_range']:.4f}", "yellow")
        cprint(f"  Direction: {hour_9am_data['direction']}", "green" if hour_9am_data['direction'] == 'BULLISH' else "red")
        cprint(f"  Move: {hour_9am_data['move_percent']:.2f}%", "yellow")

        cprint(f"\n💰 Current Price: ${current_price:.4f}", "yellow")
        cprint(f"⏱️  Minutes Since 10:30am: {minutes_since}", "cyan")

        if targets_stops['stop_loss']:
            cprint(f"\n🎯 Trade Setup:", "cyan")
            cprint(f"  Signal: {targets_stops['signal']}", "green" if targets_stops['signal'] == 'BUY' else "red")
            cprint(f"  Stop Loss: ${targets_stops['stop_loss']:.4f}", "red")
            cprint(f"  Target: ${targets_stops['target']:.4f}", "green")

        # Generate final signal
        signal = 'NOTHING'
        confidence = 0
        reasoning = ""

        if target_hit:
            signal = 'NOTHING'
            confidence = 100
            reasoning = target_reasoning

        elif stop_hit:
            signal = 'NOTHING'
            confidence = 0
            reasoning = stop_reasoning

        else:
            signal = targets_stops['signal']
            confidence = NY_SESSION_PROBABILITY
            reasoning = targets_stops['reasoning']

        cprint(f"\n🎯 Signal: {signal}", "green" if signal == "BUY" else "red" if signal == "SELL" else "yellow")
        cprint(f"📊 Confidence: {confidence}%", "cyan")
        cprint(f"💡 Reasoning: {reasoning}", "white")

        return {
            'signal': signal,
            'confidence': confidence,
            'reasoning': reasoning,
            'hour_9am_data': hour_9am_data,
            'targets_stops': targets_stops,
            'stop_hit': stop_hit,
            'target_hit': target_hit,
            'current_price': current_price,
            'minutes_since_completion': minutes_since
        }

    except Exception as e:
        cprint(f"❌ Error in 9AM Hour analysis: {str(e)}", "red")
        import traceback
        traceback.print_exc()
        return {
            'signal': 'NOTHING',
            'confidence': 0,
            'reasoning': f'Error: {str(e)}'
        }

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""
    cprint("\n🌙 Moon Dev's 9AM Hour Continuation Agent", "cyan")
    cprint("🕐 Quantitative Session Direction Trading", "cyan")
    cprint("📈 Based on 20-year NQStats data (70% continuation probability)\\n", "cyan")

    # Example usage - replace with actual token address
    test_token = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # USDC for testing

    result = generate_9am_signal(test_token)

    cprint(f"\n{'='*80}", "green")
    cprint("📋 FINAL RESULT:", "green")
    cprint(f"{'='*80}", "green")
    cprint(f"Signal: {result['signal']}", "yellow")
    cprint(f"Confidence: {result['confidence']}%", "yellow")
    cprint(f"Reasoning: {result['reasoning']}", "white")

if __name__ == "__main__":
    main()

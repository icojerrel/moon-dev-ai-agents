"""
🌙 Moon Dev's Morning Judas Continuation Agent
Morning Judas Continuation Trading Agent

Based on NQStats.com 20-year historical data (2004-2024)
Statistical Edge: 64-70% probability

Strategy:
- NOT a reversal pattern (myth busted by NQStats data!)
- 9:30am-10am move sets directional bias for entire session
- If 9:30am-10am closes GREEN → 70% probability 4pm > 10am
- If 9:30am-10am closes RED → 70% probability 4pm < 10am
- Continuation pattern, not reversal

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

# Morning Judas parameters from NQStats (20-year data)
SESSION_CLOSE_PROBABILITY = 64  # % probability entire session closes in Judas direction
HOUR_10AM_CLOSE_PROBABILITY = 70  # % probability 4pm close continues past 10am close

# Morning Judas times (EST)
JUDAS_START_HOUR = 9
JUDAS_START_MINUTE = 30
JUDAS_END_HOUR = 10
JUDAS_END_MINUTE = 0

# Session times (EST)
SESSION_CLOSE_HOUR = 16
SESSION_CLOSE_MINUTE = 0

# Trading parameters
MIN_CONFIDENCE = 60  # Minimum confidence % to trade
POSITION_SIZE_PERCENT = 2.0  # % of portfolio per trade

# ============================================================================
# MORNING JUDAS CALCULATION FUNCTIONS
# ============================================================================

def get_judas_period_data(df, current_date):
    """
    Get Morning Judas period data (9:30am-10am EST)

    Returns: dict with judas_open, judas_close, judas_high, judas_low, direction
    """
    # Calculate Judas period timeframe
    judas_start = datetime.combine(
        current_date,
        dt_time(JUDAS_START_HOUR, JUDAS_START_MINUTE)
    )
    judas_end = datetime.combine(
        current_date,
        dt_time(JUDAS_END_HOUR, JUDAS_END_MINUTE)
    )

    # Filter data for Judas period
    judas_data = df[
        (df.index >= judas_start) &
        (df.index <= judas_end)
    ]

    if len(judas_data) == 0:
        return None

    judas_open = judas_data['open'].iloc[0]
    judas_close = judas_data['close'].iloc[-1]
    judas_high = judas_data['high'].max()
    judas_low = judas_data['low'].min()
    judas_range = judas_high - judas_low

    # Determine direction (CONTINUATION, not reversal!)
    if judas_close > judas_open:
        direction = 'BULLISH'
        move_size = judas_close - judas_open
        color = 'GREEN'
    elif judas_close < judas_open:
        direction = 'BEARISH'
        move_size = judas_open - judas_close
        color = 'RED'
    else:
        direction = 'NEUTRAL'
        move_size = 0
        color = 'FLAT'

    return {
        'judas_open': judas_open,
        'judas_close': judas_close,
        'judas_high': judas_high,
        'judas_low': judas_low,
        'judas_range': judas_range,
        'direction': direction,
        'color': color,
        'move_size': move_size,
        'move_percent': (move_size / judas_open * 100) if judas_open > 0 else 0
    }

def check_judas_period_complete(current_time):
    """
    Check if Morning Judas period is complete (past 10am)

    Returns: bool, minutes_since_completion
    """
    judas_end_time = dt_time(JUDAS_END_HOUR, JUDAS_END_MINUTE)
    current_time_only = current_time.time()

    if current_time_only >= judas_end_time:
        # Calculate minutes since 10am
        today_judas_end = datetime.combine(current_time.date(), judas_end_time)
        minutes_since = (current_time - today_judas_end).total_seconds() / 60
        return True, int(minutes_since)
    else:
        return False, 0

def calculate_targets_and_stops(judas_data):
    """
    Calculate target and stop loss based on Morning Judas CONTINUATION

    Returns: dict with signal, stop_loss, target, reasoning
    """
    direction = judas_data['direction']
    color = judas_data['color']
    judas_open = judas_data['judas_open']
    judas_close = judas_data['judas_close']
    judas_high = judas_data['judas_high']
    judas_low = judas_data['judas_low']
    judas_range = judas_data['judas_range']

    if direction == 'BULLISH':
        # Go LONG (CONTINUATION, not reversal!)
        signal = 'BUY'
        stop_loss = judas_low  # Stop at Judas period low
        # Target: 1.5x Judas range above close
        target = judas_close + (judas_range * 1.5)
        reasoning = f"🟢 JUDAS PERIOD CLOSED {color}: {HOUR_10AM_CLOSE_PROBABILITY}% probability 4pm close > 10am close (${judas_close:.4f}). Trade CONTINUATION LONG (NOT reversal!). Stop at Judas low (${stop_loss:.4f}). Target: ${target:.4f}."

    elif direction == 'BEARISH':
        # Go SHORT (CONTINUATION, not reversal!)
        signal = 'SELL'
        stop_loss = judas_high  # Stop at Judas period high
        # Target: 1.5x Judas range below close
        target = judas_close - (judas_range * 1.5)
        reasoning = f"🔴 JUDAS PERIOD CLOSED {color}: {HOUR_10AM_CLOSE_PROBABILITY}% probability 4pm close < 10am close (${judas_close:.4f}). Trade CONTINUATION SHORT (NOT reversal!). Stop at Judas high (${stop_loss:.4f}). Target: ${target:.4f}."

    else:
        # NEUTRAL - no edge
        signal = 'NOTHING'
        stop_loss = None
        target = None
        reasoning = f"⚪ JUDAS PERIOD CLOSED FLAT: No directional edge. 9:30am-10am open (${judas_open:.4f}) equals close (${judas_close:.4f}). Wait for next session."

    return {
        'signal': signal,
        'stop_loss': stop_loss,
        'target': target,
        'reasoning': reasoning
    }

def check_stop_hit(current_price, targets_stops, judas_data):
    """
    Check if stop loss has been hit

    Returns: bool, reasoning
    """
    direction = judas_data['direction']

    if direction == 'BULLISH':
        # Stop = Judas period low breached
        if current_price < targets_stops['stop_loss']:
            return True, f"❌ STOP HIT: Price breached Judas low (${targets_stops['stop_loss']:.4f}). This is the 30% scenario where continuation failed."
        return False, None

    elif direction == 'BEARISH':
        # Stop = Judas period high breached
        if current_price > targets_stops['stop_loss']:
            return True, f"❌ STOP HIT: Price breached Judas high (${targets_stops['stop_loss']:.4f}). This is the 30% scenario where continuation failed."
        return False, None

    return False, None

def check_target_hit(current_price, targets_stops, judas_data):
    """
    Check if target has been hit

    Returns: bool, reasoning
    """
    direction = judas_data['direction']

    if direction == 'BULLISH' and targets_stops['target']:
        if current_price >= targets_stops['target']:
            return True, f"✅ TARGET HIT: Price reached ${targets_stops['target']:.4f}. This is the {HOUR_10AM_CLOSE_PROBABILITY}% winning scenario."
        return False, None

    elif direction == 'BEARISH' and targets_stops['target']:
        if current_price <= targets_stops['target']:
            return True, f"✅ TARGET HIT: Price reached ${targets_stops['target']:.4f}. This is the {HOUR_10AM_CLOSE_PROBABILITY}% winning scenario."
        return False, None

    return False, None

# ============================================================================
# SIGNAL GENERATION
# ============================================================================

def generate_judas_signal(token_address):
    """
    Generate Morning Judas Continuation trading signal

    Returns: dict with signal, confidence, reasoning
    """
    cprint(f"\n{'='*80}", "cyan")
    cprint(f"🌅 MORNING JUDAS CONTINUATION AGENT - {token_address}", "cyan")
    cprint(f"{'='*80}", "cyan")

    try:
        # Get OHLCV data (5-minute bars for period precision)
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

        # Check if Judas period is complete
        judas_complete, minutes_since = check_judas_period_complete(current_time)

        if not judas_complete:
            return {
                'signal': 'NOTHING',
                'confidence': 0,
                'reasoning': f'⏰ JUDAS PERIOD NOT COMPLETE: Currently {current_time.strftime("%H:%M")} EST. Wait until after 10:00am for 9:30am-10am close confirmation.'
            }

        # Get Judas period data
        judas_data = get_judas_period_data(df, current_date)
        if not judas_data:
            return {
                'signal': 'NOTHING',
                'confidence': 0,
                'reasoning': 'Unable to get Morning Judas period data. Ensure market is open during RTH (9:30am-4pm EST).'
            }

        # Calculate targets and stops
        targets_stops = calculate_targets_and_stops(judas_data)

        # Check if stop or target hit
        stop_hit, stop_reasoning = check_stop_hit(current_price, targets_stops, judas_data)
        target_hit, target_reasoning = check_target_hit(current_price, targets_stops, judas_data)

        # Print analysis
        cprint(f"\n📊 Morning Judas Period (9:30am-10am):", "yellow")
        cprint(f"  Open: ${judas_data['judas_open']:.4f}", "yellow")
        cprint(f"  Close: ${judas_data['judas_close']:.4f}", "yellow")
        cprint(f"  High: ${judas_data['judas_high']:.4f}", "yellow")
        cprint(f"  Low: ${judas_data['judas_low']:.4f}", "yellow")
        cprint(f"  Range: ${judas_data['judas_range']:.4f}", "yellow")
        cprint(f"  Direction: {judas_data['direction']} ({judas_data['color']})", "green" if judas_data['direction'] == 'BULLISH' else "red")
        cprint(f"  Move: {judas_data['move_percent']:.2f}%", "yellow")

        cprint(f"\n💰 Current Price: ${current_price:.4f}", "yellow")
        cprint(f"⏱️  Minutes Since 10am: {minutes_since}", "cyan")

        cprint(f"\n💡 MYTH BUSTER:", "magenta")
        cprint(f"  Morning Judas is CONTINUATION (not reversal)!", "magenta")
        cprint(f"  NQStats 20-year data proves {HOUR_10AM_CLOSE_PROBABILITY}% continuation edge", "magenta")

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
            confidence = HOUR_10AM_CLOSE_PROBABILITY
            reasoning = targets_stops['reasoning']

        cprint(f"\n🎯 Signal: {signal}", "green" if signal == "BUY" else "red" if signal == "SELL" else "yellow")
        cprint(f"📊 Confidence: {confidence}%", "cyan")
        cprint(f"💡 Reasoning: {reasoning}", "white")

        return {
            'signal': signal,
            'confidence': confidence,
            'reasoning': reasoning,
            'judas_data': judas_data,
            'targets_stops': targets_stops,
            'stop_hit': stop_hit,
            'target_hit': target_hit,
            'current_price': current_price,
            'minutes_since_completion': minutes_since
        }

    except Exception as e:
        cprint(f"❌ Error in Morning Judas analysis: {str(e)}", "red")
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
    cprint("\n🌙 Moon Dev's Morning Judas Continuation Agent", "cyan")
    cprint("🌅 Quantitative Continuation Trading (NOT Reversal!)", "cyan")
    cprint("📈 Based on 20-year NQStats data (70% continuation probability)\\n", "cyan")
    cprint("💡 MYTH BUSTED: Morning Judas is CONTINUATION, not reversal!\\n", "magenta")

    # Example usage - replace with actual token address
    test_token = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # USDC for testing

    result = generate_judas_signal(test_token)

    cprint(f"\n{'='*80}", "green")
    cprint("📋 FINAL RESULT:", "green")
    cprint(f"{'='*80}", "green")
    cprint(f"Signal: {result['signal']}", "yellow")
    cprint(f"Confidence: {result['confidence']}%", "yellow")
    cprint(f"Reasoning: {result['reasoning']}", "white")

if __name__ == "__main__":
    main()

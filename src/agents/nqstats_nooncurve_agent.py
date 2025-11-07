"""
🌙 Moon Dev's Noon Curve AM/PM Structure Agent
Noon Curve AM/PM Structure Trading Agent

Based on NQStats.com 20-year historical data (2004-2024)
Statistical Edge: 74.3% probability

Strategy:
- Compare AM session (9:30am-12pm) vs PM session (12pm-4pm)
- If AM makes extreme HIGH → 74.3% probability PM makes extreme LOW
- If AM makes extreme LOW → 74.3% probability PM makes extreme HIGH
- "Noon curve" inflection point creates opposite extremes pattern

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

# Noon Curve parameters from NQStats (20-year data)
OPPOSITE_EXTREME_PROBABILITY = 74.3  # % probability PM makes opposite extreme vs AM

# Session times (EST)
RTH_OPEN_HOUR = 9
RTH_OPEN_MINUTE = 30
NOON_HOUR = 12
NOON_MINUTE = 0
RTH_CLOSE_HOUR = 16
RTH_CLOSE_MINUTE = 0

# Trading parameters
MIN_CONFIDENCE = 70  # Minimum confidence % to trade
POSITION_SIZE_PERCENT = 2.0  # % of portfolio per trade

# ============================================================================
# NOON CURVE CALCULATION FUNCTIONS
# ============================================================================

def get_am_session_data(df, current_date):
    """
    Get AM session data (9:30am-12pm EST)

    Returns: dict with AM_high, AM_low, AM_open, AM_close, AM_extreme_type
    """
    # Calculate AM session timeframe
    am_start = datetime.combine(
        current_date,
        dt_time(RTH_OPEN_HOUR, RTH_OPEN_MINUTE)
    )
    am_end = datetime.combine(
        current_date,
        dt_time(NOON_HOUR, NOON_MINUTE)
    )

    # Filter data for AM session
    am_data = df[
        (df.index >= am_start) &
        (df.index < am_end)
    ]

    if len(am_data) == 0:
        return None

    AM_high = am_data['high'].max()
    AM_low = am_data['low'].min()
    AM_open = am_data['open'].iloc[0]
    AM_close = am_data['close'].iloc[-1]
    AM_range = AM_high - AM_low

    # Determine which extreme was more significant
    # If AM high is further from open than AM low, AM extreme is HIGH
    distance_to_high = AM_high - AM_open
    distance_to_low = AM_open - AM_low

    if distance_to_high > distance_to_low:
        AM_extreme_type = 'HIGH'
        AM_extreme_value = AM_high
    else:
        AM_extreme_type = 'LOW'
        AM_extreme_value = AM_low

    return {
        'AM_high': AM_high,
        'AM_low': AM_low,
        'AM_open': AM_open,
        'AM_close': AM_close,
        'AM_range': AM_range,
        'AM_extreme_type': AM_extreme_type,
        'AM_extreme_value': AM_extreme_value,
        'distance_to_high': distance_to_high,
        'distance_to_low': distance_to_low
    }

def get_pm_session_data(df, current_date):
    """
    Get PM session data (12pm-4pm EST)

    Returns: dict with PM_high, PM_low, PM_open, PM_close
    """
    # Calculate PM session timeframe
    pm_start = datetime.combine(
        current_date,
        dt_time(NOON_HOUR, NOON_MINUTE)
    )
    pm_end = datetime.combine(
        current_date,
        dt_time(RTH_CLOSE_HOUR, RTH_CLOSE_MINUTE)
    )

    # Filter data for PM session
    pm_data = df[
        (df.index >= pm_start) &
        (df.index <= pm_end)
    ]

    if len(pm_data) == 0:
        return None

    PM_high = pm_data['high'].max()
    PM_low = pm_data['low'].min()
    PM_open = pm_data['open'].iloc[0] if len(pm_data) > 0 else None
    PM_close = pm_data['close'].iloc[-1] if len(pm_data) > 0 else None
    PM_range = PM_high - PM_low

    return {
        'PM_high': PM_high,
        'PM_low': PM_low,
        'PM_open': PM_open,
        'PM_close': PM_close,
        'PM_range': PM_range
    }

def check_past_noon(current_time):
    """
    Check if current time is past noon (12pm)

    Returns: bool, minutes_since_noon
    """
    noon_time = dt_time(NOON_HOUR, NOON_MINUTE)
    current_time_only = current_time.time()

    if current_time_only >= noon_time:
        # Calculate minutes since noon
        today_noon = datetime.combine(current_time.date(), noon_time)
        minutes_since = (current_time - today_noon).total_seconds() / 60
        return True, int(minutes_since)
    else:
        return False, 0

def calculate_targets_and_stops(am_data, pm_data, current_price):
    """
    Calculate target and stop loss based on AM extreme and expected PM opposite extreme

    Returns: dict with signal, stop_loss, target, confidence, reasoning
    """
    AM_extreme_type = am_data['AM_extreme_type']
    AM_high = am_data['AM_high']
    AM_low = am_data['AM_low']
    AM_range = am_data['AM_range']

    if AM_extreme_type == 'HIGH':
        # AM made extreme HIGH → expect PM to make extreme LOW
        signal = 'SELL'
        stop_loss = AM_high  # Stop if breaks above AM high (continuation instead of reversal)
        target = AM_low - (AM_range * 0.5)  # Target below AM low
        reasoning = f"🔴 AM EXTREME HIGH: AM session made extreme high (${AM_high:.4f}). {OPPOSITE_EXTREME_PROBABILITY}% probability PM session (12pm-4pm) makes extreme LOW (opposite extreme). Trade SHORT from noon. Stop: ${stop_loss:.4f}. Target: ${target:.4f}."

    elif AM_extreme_type == 'LOW':
        # AM made extreme LOW → expect PM to make extreme HIGH
        signal = 'BUY'
        stop_loss = AM_low  # Stop if breaks below AM low (continuation instead of reversal)
        target = AM_high + (AM_range * 0.5)  # Target above AM high
        reasoning = f"🟢 AM EXTREME LOW: AM session made extreme low (${AM_low:.4f}). {OPPOSITE_EXTREME_PROBABILITY}% probability PM session (12pm-4pm) makes extreme HIGH (opposite extreme). Trade LONG from noon. Stop: ${stop_loss:.4f}. Target: ${target:.4f}."

    else:
        # Neutral AM session
        signal = 'NOTHING'
        stop_loss = None
        target = None
        reasoning = f"⚪ AM SESSION NEUTRAL: No clear AM extreme. AM high (${AM_high:.4f}) and low (${AM_low:.4f}) equidistant from open. No noon curve edge."

    return {
        'signal': signal,
        'stop_loss': stop_loss,
        'target': target,
        'confidence': OPPOSITE_EXTREME_PROBABILITY,
        'reasoning': reasoning
    }

def check_stop_hit(current_price, targets_stops, am_data):
    """
    Check if stop loss has been hit (AM extreme breached)

    Returns: bool, reasoning
    """
    AM_extreme_type = am_data['AM_extreme_type']

    if AM_extreme_type == 'HIGH':
        # Stop = AM high breached (continuation up instead of reversal down)
        if current_price > targets_stops['stop_loss']:
            return True, f"❌ STOP HIT: Price broke above AM high (${targets_stops['stop_loss']:.4f}). This is the 25.7% scenario where noon curve reversal failed (continuation instead)."
        return False, None

    elif AM_extreme_type == 'LOW':
        # Stop = AM low breached (continuation down instead of reversal up)
        if current_price < targets_stops['stop_loss']:
            return True, f"❌ STOP HIT: Price broke below AM low (${targets_stops['stop_loss']:.4f}). This is the 25.7% scenario where noon curve reversal failed (continuation instead)."
        return False, None

    return False, None

def check_target_hit(current_price, targets_stops, am_data):
    """
    Check if target has been hit (opposite extreme reached)

    Returns: bool, reasoning
    """
    AM_extreme_type = am_data['AM_extreme_type']

    if AM_extreme_type == 'HIGH' and targets_stops['target']:
        # Target = below AM low
        if current_price <= targets_stops['target']:
            return True, f"✅ TARGET HIT: PM session made opposite extreme LOW (${targets_stops['target']:.4f}). This is the {OPPOSITE_EXTREME_PROBABILITY}% winning scenario."
        return False, None

    elif AM_extreme_type == 'LOW' and targets_stops['target']:
        # Target = above AM high
        if current_price >= targets_stops['target']:
            return True, f"✅ TARGET HIT: PM session made opposite extreme HIGH (${targets_stops['target']:.4f}). This is the {OPPOSITE_EXTREME_PROBABILITY}% winning scenario."
        return False, None

    return False, None

# ============================================================================
# SIGNAL GENERATION
# ============================================================================

def generate_nooncurve_signal(token_address):
    """
    Generate Noon Curve AM/PM Structure trading signal

    Returns: dict with signal, confidence, reasoning
    """
    cprint(f"\n{'='*80}", "cyan")
    cprint(f"🌓 NOON CURVE AM/PM STRUCTURE AGENT - {token_address}", "cyan")
    cprint(f"{'='*80}", "cyan")

    try:
        # Get OHLCV data (5-minute bars for session precision)
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

        # Check if past noon
        past_noon, minutes_since_noon = check_past_noon(current_time)

        if not past_noon:
            return {
                'signal': 'NOTHING',
                'confidence': 0,
                'reasoning': f'⏰ NOT YET NOON: Currently {current_time.strftime("%H:%M")} EST. Wait until after 12pm for AM session extreme confirmation and noon curve setup.'
            }

        # Get AM session data
        am_data = get_am_session_data(df, current_date)
        if not am_data:
            return {
                'signal': 'NOTHING',
                'confidence': 0,
                'reasoning': 'Unable to get AM session data. Ensure market is open during RTH (9:30am-4pm EST).'
            }

        # Get PM session data (may be incomplete)
        pm_data = get_pm_session_data(df, current_date)

        # Calculate targets and stops
        targets_stops = calculate_targets_and_stops(am_data, pm_data, current_price)

        # Check if stop or target hit
        stop_hit, stop_reasoning = check_stop_hit(current_price, targets_stops, am_data)
        target_hit, target_reasoning = check_target_hit(current_price, targets_stops, am_data)

        # Print analysis
        cprint(f"\n📊 AM Session (9:30am-12pm):", "yellow")
        cprint(f"  High: ${am_data['AM_high']:.4f}", "yellow")
        cprint(f"  Low: ${am_data['AM_low']:.4f}", "yellow")
        cprint(f"  Range: ${am_data['AM_range']:.4f}", "yellow")
        cprint(f"  Extreme Type: {am_data['AM_extreme_type']}", "red" if am_data['AM_extreme_type'] == 'HIGH' else "green")
        cprint(f"  Extreme Value: ${am_data['AM_extreme_value']:.4f}", "yellow")

        if pm_data:
            cprint(f"\n📊 PM Session (12pm-4pm) - In Progress:", "yellow")
            cprint(f"  High: ${pm_data['PM_high']:.4f}", "yellow")
            cprint(f"  Low: ${pm_data['PM_low']:.4f}", "yellow")

        cprint(f"\n💰 Current Price: ${current_price:.4f}", "yellow")
        cprint(f"⏱️  Minutes Since Noon: {minutes_since_noon}", "cyan")

        if targets_stops['stop_loss']:
            cprint(f"\n🎯 Noon Curve Trade Setup:", "cyan")
            cprint(f"  Expected: PM makes opposite extreme vs AM {am_data['AM_extreme_type']}", "cyan")
            cprint(f"  Signal: {targets_stops['signal']}", "green" if targets_stops['signal'] == 'BUY' else "red")
            cprint(f"  Stop Loss: ${targets_stops['stop_loss']:.4f}", "red")
            cprint(f"  Target: ${targets_stops['target']:.4f}", "green")
            cprint(f"  Confidence: {targets_stops['confidence']:.1f}%", "cyan")

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
            confidence = targets_stops['confidence']
            reasoning = targets_stops['reasoning']

        cprint(f"\n🎯 Signal: {signal}", "green" if signal == "BUY" else "red" if signal == "SELL" else "yellow")
        cprint(f"📊 Confidence: {confidence:.1f}%", "cyan")
        cprint(f"💡 Reasoning: {reasoning}", "white")

        return {
            'signal': signal,
            'confidence': confidence,
            'reasoning': reasoning,
            'am_data': am_data,
            'pm_data': pm_data,
            'targets_stops': targets_stops,
            'stop_hit': stop_hit,
            'target_hit': target_hit,
            'current_price': current_price,
            'minutes_since_noon': minutes_since_noon
        }

    except Exception as e:
        cprint(f"❌ Error in Noon Curve analysis: {str(e)}", "red")
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
    cprint("\n🌙 Moon Dev's Noon Curve AM/PM Structure Agent", "cyan")
    cprint("🌓 Quantitative Session Reversal Trading", "cyan")
    cprint("📈 Based on 20-year NQStats data (74.3% opposite extreme probability)\\n", "cyan")

    # Example usage - replace with actual token address
    test_token = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # USDC for testing

    result = generate_nooncurve_signal(test_token)

    cprint(f"\n{'='*80}", "green")
    cprint("📋 FINAL RESULT:", "green")
    cprint(f"{'='*80}", "green")
    cprint(f"Signal: {result['signal']}", "yellow")
    cprint(f"Confidence: {result['confidence']:.1f}%", "yellow")
    cprint(f"Reasoning: {result['reasoning']}", "white")

if __name__ == "__main__":
    main()

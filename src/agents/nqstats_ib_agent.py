"""
🌙 Moon Dev's Initial Balance Breakout Agent
Initial Balance (IB) Breakout Trading Agent

Based on NQStats.com 20-year historical data (2004-2024)
Statistical Edge: 74-96% probability

Strategy:
- Initial Balance (IB) = 9:30am-10:30am high/low range
- IB Break UP → 81% probability session closes above IB low
- IB Break DOWN → 74% probability session closes below IB high
- Failed break (breaks both sides) → 96% probability closes inside IB (mean reversion)

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

# Initial Balance parameters from NQStats (20-year data)
IB_BREAK_UP_PROBABILITY = 81  # % probability session closes above IB low after IB break up
IB_BREAK_DOWN_PROBABILITY = 74  # % probability session closes below IB high after IB break down
FAILED_BREAK_PROBABILITY = 96  # % probability closes inside IB after breaking both sides

# Initial Balance times (EST)
IB_START_HOUR = 9
IB_START_MINUTE = 30
IB_END_HOUR = 10
IB_END_MINUTE = 30

# Session times (EST)
SESSION_CLOSE_HOUR = 16
SESSION_CLOSE_MINUTE = 0

# Trading parameters
MIN_CONFIDENCE = 70  # Minimum confidence % to trade
POSITION_SIZE_PERCENT = 2.0  # % of portfolio per trade
TARGET_MULTIPLE = 1.5  # Target = 1.5x IB range from breakout

# ============================================================================
# INITIAL BALANCE CALCULATION FUNCTIONS
# ============================================================================

def get_initial_balance(df, current_date):
    """
    Get Initial Balance (IB) data (9:30am-10:30am EST)

    Returns: dict with IB_high, IB_low, IB_range, IB_open, IB_close
    """
    # Calculate IB timeframe
    ib_start = datetime.combine(
        current_date,
        dt_time(IB_START_HOUR, IB_START_MINUTE)
    )
    ib_end = datetime.combine(
        current_date,
        dt_time(IB_END_HOUR, IB_END_MINUTE)
    )

    # Filter data for IB period
    ib_data = df[
        (df.index >= ib_start) &
        (df.index <= ib_end)
    ]

    if len(ib_data) == 0:
        return None

    IB_high = ib_data['high'].max()
    IB_low = ib_data['low'].min()
    IB_range = IB_high - IB_low
    IB_open = ib_data['open'].iloc[0]
    IB_close = ib_data['close'].iloc[-1]

    return {
        'IB_high': IB_high,
        'IB_low': IB_low,
        'IB_range': IB_range,
        'IB_open': IB_open,
        'IB_close': IB_close,
        'IB_midpoint': (IB_high + IB_low) / 2
    }

def check_ib_complete(current_time):
    """
    Check if Initial Balance period is complete (past 10:30am)

    Returns: bool, minutes_since_completion
    """
    ib_end_time = dt_time(IB_END_HOUR, IB_END_MINUTE)
    current_time_only = current_time.time()

    if current_time_only >= ib_end_time:
        # Calculate minutes since 10:30am
        today_ib_end = datetime.combine(current_time.date(), ib_end_time)
        minutes_since = (current_time - today_ib_end).total_seconds() / 60
        return True, int(minutes_since)
    else:
        return False, 0

def detect_ib_break(df, current_time, ib_data):
    """
    Detect if IB high or low has been broken after 10:30am

    Returns: 'BREAK_UP', 'BREAK_DOWN', 'FAILED_BREAK', or 'NO_BREAK'
    """
    # Get data after IB period
    ib_end_time = datetime.combine(
        current_time.date(),
        dt_time(IB_END_HOUR, IB_END_MINUTE)
    )

    post_ib_data = df[df.index > ib_end_time]

    if len(post_ib_data) == 0:
        return 'NO_BREAK', None

    post_ib_high = post_ib_data['high'].max()
    post_ib_low = post_ib_data['low'].min()

    # Check for failed break (broke both IB high and low)
    broke_high = post_ib_high > ib_data['IB_high']
    broke_low = post_ib_low < ib_data['IB_low']

    if broke_high and broke_low:
        return 'FAILED_BREAK', {
            'post_ib_high': post_ib_high,
            'post_ib_low': post_ib_low
        }
    elif broke_high:
        return 'BREAK_UP', {
            'breakout_level': ib_data['IB_high'],
            'post_ib_high': post_ib_high
        }
    elif broke_low:
        return 'BREAK_DOWN', {
            'breakout_level': ib_data['IB_low'],
            'post_ib_low': post_ib_low
        }
    else:
        return 'NO_BREAK', {
            'post_ib_high': post_ib_high,
            'post_ib_low': post_ib_low
        }

def calculate_targets_and_stops(break_type, ib_data, break_info):
    """
    Calculate target and stop loss based on IB break type

    Returns: dict with signal, stop_loss, target, confidence, reasoning
    """
    IB_high = ib_data['IB_high']
    IB_low = ib_data['IB_low']
    IB_range = ib_data['IB_range']
    IB_midpoint = ib_data['IB_midpoint']

    if break_type == 'BREAK_UP':
        # IB broke to upside
        signal = 'BUY'
        stop_loss = IB_low  # Stop at IB low
        target = IB_high + (IB_range * TARGET_MULTIPLE)
        confidence = IB_BREAK_UP_PROBABILITY
        reasoning = f"🟢 IB BREAK UP: Price broke above IB high (${IB_high:.4f}). {IB_BREAK_UP_PROBABILITY}% probability session closes above IB low. Trade continuation LONG. Stop: ${stop_loss:.4f}. Target: ${target:.4f}."

    elif break_type == 'BREAK_DOWN':
        # IB broke to downside
        signal = 'SELL'
        stop_loss = IB_high  # Stop at IB high
        target = IB_low - (IB_range * TARGET_MULTIPLE)
        confidence = IB_BREAK_DOWN_PROBABILITY
        reasoning = f"🔴 IB BREAK DOWN: Price broke below IB low (${IB_low:.4f}). {IB_BREAK_DOWN_PROBABILITY}% probability session closes below IB high. Trade continuation SHORT. Stop: ${stop_loss:.4f}. Target: ${target:.4f}."

    elif break_type == 'FAILED_BREAK':
        # Failed break (broke both sides) - MEAN REVERSION
        # Determine which side to fade
        signal = 'NOTHING'  # Need current price to determine direction
        stop_loss = None
        target = IB_midpoint
        confidence = FAILED_BREAK_PROBABILITY
        reasoning = f"⚠️ FAILED IB BREAK: Price broke BOTH IB high (${IB_high:.4f}) and IB low (${IB_low:.4f}). {FAILED_BREAK_PROBABILITY}% probability session closes INSIDE IB range. FADE the extreme and target IB midpoint (${IB_midpoint:.4f}). Highest probability mean reversion setup!"

    else:
        # NO_BREAK - still inside IB
        signal = 'NOTHING'
        stop_loss = None
        target = None
        confidence = 50
        reasoning = f"⚪ NO IB BREAK: Price still trading inside IB range (${IB_low:.4f} - ${IB_high:.4f}). Wait for breakout above IB high or below IB low for directional edge."

    return {
        'signal': signal,
        'stop_loss': stop_loss,
        'target': target,
        'confidence': confidence,
        'reasoning': reasoning
    }

def refine_failed_break_signal(current_price, ib_data):
    """
    For failed breaks, determine which direction to fade

    Returns: dict with refined signal
    """
    IB_high = ib_data['IB_high']
    IB_low = ib_data['IB_low']
    IB_midpoint = ib_data['IB_midpoint']

    # If closer to IB high, fade SHORT
    if current_price > IB_midpoint:
        signal = 'SELL'
        stop_loss = IB_high * 1.01  # Stop just above IB high
        reasoning = f"🔴 FAILED BREAK - FADE SHORT: Price near IB high (${IB_high:.4f}). {FAILED_BREAK_PROBABILITY}% probability closes inside IB. Target: IB midpoint (${IB_midpoint:.4f})."

    # If closer to IB low, fade LONG
    else:
        signal = 'BUY'
        stop_loss = IB_low * 0.99  # Stop just below IB low
        reasoning = f"🟢 FAILED BREAK - FADE LONG: Price near IB low (${IB_low:.4f}). {FAILED_BREAK_PROBABILITY}% probability closes inside IB. Target: IB midpoint (${IB_midpoint:.4f})."

    return {
        'signal': signal,
        'stop_loss': stop_loss,
        'target': IB_midpoint,
        'confidence': FAILED_BREAK_PROBABILITY,
        'reasoning': reasoning
    }

# ============================================================================
# SIGNAL GENERATION
# ============================================================================

def generate_ib_signal(token_address):
    """
    Generate Initial Balance Breakout trading signal

    Returns: dict with signal, confidence, reasoning
    """
    cprint(f"\n{'='*80}", "cyan")
    cprint(f"⚖️ INITIAL BALANCE BREAKOUT AGENT - {token_address}", "cyan")
    cprint(f"{'='*80}", "cyan")

    try:
        # Get OHLCV data (5-minute bars for IB precision)
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

        # Check if IB is complete
        ib_complete, minutes_since = check_ib_complete(current_time)

        if not ib_complete:
            return {
                'signal': 'NOTHING',
                'confidence': 0,
                'reasoning': f'⏰ INITIAL BALANCE NOT COMPLETE: Currently {current_time.strftime("%H:%M")} EST. Wait until after 10:30am for IB establishment.'
            }

        # Get Initial Balance
        ib_data = get_initial_balance(df, current_date)
        if not ib_data:
            return {
                'signal': 'NOTHING',
                'confidence': 0,
                'reasoning': 'Unable to get Initial Balance data. Ensure market is open during RTH (9:30am-4pm EST).'
            }

        # Detect IB break
        break_type, break_info = detect_ib_break(df, current_time, ib_data)

        # Calculate targets and stops
        targets_stops = calculate_targets_and_stops(break_type, ib_data, break_info)

        # For failed breaks, refine signal based on current price
        if break_type == 'FAILED_BREAK':
            targets_stops = refine_failed_break_signal(current_price, ib_data)

        # Print analysis
        cprint(f"\n📊 Initial Balance (9:30am-10:30am):", "yellow")
        cprint(f"  High: ${ib_data['IB_high']:.4f}", "yellow")
        cprint(f"  Low: ${ib_data['IB_low']:.4f}", "yellow")
        cprint(f"  Range: ${ib_data['IB_range']:.4f}", "yellow")
        cprint(f"  Midpoint: ${ib_data['IB_midpoint']:.4f}", "yellow")

        cprint(f"\n💰 Current Price: ${current_price:.4f}", "yellow")
        cprint(f"⏱️  Minutes Since 10:30am: {minutes_since}", "cyan")

        cprint(f"\n🎯 IB Break Analysis:", "cyan")
        cprint(f"  Break Type: {break_type}", "cyan")

        if break_info:
            if 'breakout_level' in break_info:
                cprint(f"  Breakout Level: ${break_info['breakout_level']:.4f}", "cyan")
            if 'post_ib_high' in break_info:
                cprint(f"  Post-IB High: ${break_info['post_ib_high']:.4f}", "cyan")
            if 'post_ib_low' in break_info:
                cprint(f"  Post-IB Low: ${break_info['post_ib_low']:.4f}", "cyan")

        if targets_stops['stop_loss']:
            cprint(f"\n🎯 Trade Setup:", "cyan")
            cprint(f"  Signal: {targets_stops['signal']}", "green" if targets_stops['signal'] == 'BUY' else "red")
            cprint(f"  Stop Loss: ${targets_stops['stop_loss']:.4f}", "red")
            cprint(f"  Target: ${targets_stops['target']:.4f}", "green")
            cprint(f"  Confidence: {targets_stops['confidence']}%", "cyan")

        # Generate final signal
        signal = targets_stops['signal']
        confidence = targets_stops['confidence']
        reasoning = targets_stops['reasoning']

        cprint(f"\n🎯 Signal: {signal}", "green" if signal == "BUY" else "red" if signal == "SELL" else "yellow")
        cprint(f"📊 Confidence: {confidence}%", "cyan")
        cprint(f"💡 Reasoning: {reasoning}", "white")

        return {
            'signal': signal,
            'confidence': confidence,
            'reasoning': reasoning,
            'ib_data': ib_data,
            'break_type': break_type,
            'break_info': break_info,
            'targets_stops': targets_stops,
            'current_price': current_price,
            'minutes_since_completion': minutes_since
        }

    except Exception as e:
        cprint(f"❌ Error in IB analysis: {str(e)}", "red")
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
    cprint("\n🌙 Moon Dev's Initial Balance Breakout Agent", "cyan")
    cprint("⚖️ Quantitative IB Breakout Trading", "cyan")
    cprint("📈 Based on 20-year NQStats data (74-96% probability)\\n", "cyan")

    # Example usage - replace with actual token address
    test_token = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # USDC for testing

    result = generate_ib_signal(test_token)

    cprint(f"\n{'='*80}", "green")
    cprint("📋 FINAL RESULT:", "green")
    cprint(f"{'='*80}", "green")
    cprint(f"Signal: {result['signal']}", "yellow")
    cprint(f"Confidence: {result['confidence']}%", "yellow")
    cprint(f"Reasoning: {result['reasoning']}", "white")

if __name__ == "__main__":
    main()

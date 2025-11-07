"""
🌙 Moon Dev's Hour Stats Sweep Retracement Agent
Hourly Sweep Retracement Trading Agent

Based on NQStats.com 20-year historical data (2004-2024)
Statistical Edge: 89% probability

Strategy:
- When current hour sweeps previous hour high/low
- 89% probability price retraces to current hour open
- Within first 20 minutes of hour (0-20min segment)
- Avoid second segment (20-40min = only 47% probability)

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

# Hour Stats parameters from NQStats (20-year data)
RETRACEMENT_PROBABILITY = 89  # % probability in first 20-min segment
SECOND_SEGMENT_PROBABILITY = 47  # % probability in 20-40min segment (AVOID!)

# Trading parameters
MIN_CONFIDENCE = 70  # Minimum confidence % to trade
POSITION_SIZE_PERCENT = 2.0  # % of portfolio per trade
STOP_BUFFER_POINTS = 10  # Points beyond previous hour extreme for stop

# Time segments (minutes from hour open)
FIRST_SEGMENT_END = 20  # 0-20 minutes (89% edge)
SECOND_SEGMENT_START = 20  # 20-40 minutes (47% edge - AVOID)
SECOND_SEGMENT_END = 40

# Session times (EST)
SESSION_OPEN_HOUR = 9   # 9:30am
SESSION_CLOSE_HOUR = 16  # 4:00pm

# ============================================================================
# HOUR STATS CALCULATION FUNCTIONS
# ============================================================================

def get_previous_hour_range(df, current_time):
    """
    Get previous hour's high, low, and open

    Returns: dict with prev_hour_high, prev_hour_low, prev_hour_open
    """
    # Calculate previous hour start
    current_hour_start = current_time.replace(minute=0, second=0, microsecond=0)
    prev_hour_start = current_hour_start - timedelta(hours=1)
    prev_hour_end = current_hour_start

    # Filter data for previous hour
    prev_hour_data = df[
        (df.index >= prev_hour_start) &
        (df.index < prev_hour_end)
    ]

    if len(prev_hour_data) == 0:
        return None

    return {
        'prev_hour_high': prev_hour_data['high'].max(),
        'prev_hour_low': prev_hour_data['low'].min(),
        'prev_hour_open': prev_hour_data['open'].iloc[0],
        'prev_hour_close': prev_hour_data['close'].iloc[-1]
    }

def get_current_hour_data(df, current_time):
    """
    Get current hour's open and data

    Returns: dict with current_hour_open, minutes_into_hour
    """
    current_hour_start = current_time.replace(minute=0, second=0, microsecond=0)

    # Filter data for current hour
    current_hour_data = df[
        (df.index >= current_hour_start) &
        (df.index <= current_time)
    ]

    if len(current_hour_data) == 0:
        return None

    # Calculate minutes into current hour
    minutes_into_hour = (current_time - current_hour_start).total_seconds() / 60

    return {
        'current_hour_open': current_hour_data['open'].iloc[0],
        'current_hour_high': current_hour_data['high'].max(),
        'current_hour_low': current_hour_data['low'].min(),
        'minutes_into_hour': int(minutes_into_hour)
    }

def detect_sweep(current_price, current_hour_data, prev_hour_data):
    """
    Detect if current hour has swept previous hour high or low

    Returns: 'HIGH_SWEEP', 'LOW_SWEEP', or None
    """
    prev_high = prev_hour_data['prev_hour_high']
    prev_low = prev_hour_data['prev_hour_low']
    current_high = current_hour_data['current_hour_high']
    current_low = current_hour_data['current_hour_low']

    # High sweep: current hour broke above previous hour high
    if current_high > prev_high:
        return 'HIGH_SWEEP'

    # Low sweep: current hour broke below previous hour low
    if current_low < prev_low:
        return 'LOW_SWEEP'

    return None

def calculate_time_segment(minutes_into_hour):
    """
    Determine which time segment we're in

    Returns: 'FIRST_SEGMENT' (0-20min, 89% edge), 'SECOND_SEGMENT' (20-40min, 47%), 'LATER' (40-60min)
    """
    if minutes_into_hour <= FIRST_SEGMENT_END:
        return 'FIRST_SEGMENT'
    elif minutes_into_hour <= SECOND_SEGMENT_END:
        return 'SECOND_SEGMENT'
    else:
        return 'LATER'

# ============================================================================
# SIGNAL GENERATION
# ============================================================================

def generate_hourstats_signal(token_address):
    """
    Generate Hour Stats Sweep Retracement trading signal

    Returns: dict with signal, confidence, reasoning
    """
    cprint(f"\n{'='*80}", "cyan")
    cprint(f"⏰ HOUR STATS SWEEP RETRACEMENT AGENT - {token_address}", "cyan")
    cprint(f"{'='*80}", "cyan")

    try:
        # Get OHLCV data (5-minute bars for intraday precision)
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

        # Get previous hour data
        prev_hour_data = get_previous_hour_range(df, current_time)
        if not prev_hour_data:
            return {
                'signal': 'NOTHING',
                'confidence': 0,
                'reasoning': 'Unable to get previous hour data'
            }

        # Get current hour data
        current_hour_data = get_current_hour_data(df, current_time)
        if not current_hour_data:
            return {
                'signal': 'NOTHING',
                'confidence': 0,
                'reasoning': 'Unable to get current hour data'
            }

        # Determine time segment
        minutes_into_hour = current_hour_data['minutes_into_hour']
        time_segment = calculate_time_segment(minutes_into_hour)

        # Detect sweep
        sweep_type = detect_sweep(current_price, current_hour_data, prev_hour_data)

        # Print analysis
        cprint(f"\n📊 Previous Hour Data:", "yellow")
        cprint(f"  High: ${prev_hour_data['prev_hour_high']:.4f}", "yellow")
        cprint(f"  Low: ${prev_hour_data['prev_hour_low']:.4f}", "yellow")
        cprint(f"  Open: ${prev_hour_data['prev_hour_open']:.4f}", "yellow")

        cprint(f"\n📊 Current Hour Data:", "yellow")
        cprint(f"  Open: ${current_hour_data['current_hour_open']:.4f}", "yellow")
        cprint(f"  High: ${current_hour_data['current_hour_high']:.4f}", "yellow")
        cprint(f"  Low: ${current_hour_data['current_hour_low']:.4f}", "yellow")
        cprint(f"  Minutes Into Hour: {minutes_into_hour}", "yellow")

        cprint(f"\n💰 Current Price: ${current_price:.4f}", "yellow")
        cprint(f"⏱️  Time Segment: {time_segment}", "cyan")
        cprint(f"🎯 Sweep Detected: {sweep_type if sweep_type else 'None'}", "cyan")

        # Generate signal based on sweep retracement logic
        signal = 'NOTHING'
        confidence = 0
        reasoning = ""

        # ONLY trade in FIRST_SEGMENT (0-20 minutes)
        if time_segment != 'FIRST_SEGMENT':
            if time_segment == 'SECOND_SEGMENT':
                signal = 'NOTHING'
                confidence = 47
                reasoning = f"⚠️ SECOND SEGMENT (20-40min): Only 47% probability - AVOID TRADING. Wait for next hour or exit existing positions."
            else:
                signal = 'NOTHING'
                confidence = 0
                reasoning = f"⏰ Late in hour (>{SECOND_SEGMENT_END}min): Hour Stats edge expired. Wait for next hour."

        # HIGH SWEEP -> FADE SHORT (expect retracement to current hour open)
        elif sweep_type == 'HIGH_SWEEP':
            current_hour_open = current_hour_data['current_hour_open']
            stop_loss = prev_hour_data['prev_hour_high'] + (STOP_BUFFER_POINTS / 10000)  # Convert points to price

            # Check if we're above current hour open (retracement not complete)
            if current_price > current_hour_open:
                signal = 'SELL'
                confidence = 89
                reasoning = f"🔴 HIGH SWEEP DETECTED: Price swept previous hour high (${prev_hour_data['prev_hour_high']:.4f}). {RETRACEMENT_PROBABILITY}% probability of retracement to current hour open (${current_hour_open:.4f}) within first 20 minutes. Minutes into hour: {minutes_into_hour}. Stop: ${stop_loss:.4f}."
            else:
                signal = 'NOTHING'
                confidence = 0
                reasoning = f"✅ HIGH SWEEP RETRACEMENT COMPLETE: Price already at/below current hour open (${current_hour_open:.4f}). Target achieved."

        # LOW SWEEP -> FADE LONG (expect retracement to current hour open)
        elif sweep_type == 'LOW_SWEEP':
            current_hour_open = current_hour_data['current_hour_open']
            stop_loss = prev_hour_data['prev_hour_low'] - (STOP_BUFFER_POINTS / 10000)  # Convert points to price

            # Check if we're below current hour open (retracement not complete)
            if current_price < current_hour_open:
                signal = 'BUY'
                confidence = 89
                reasoning = f"🟢 LOW SWEEP DETECTED: Price swept previous hour low (${prev_hour_data['prev_hour_low']:.4f}). {RETRACEMENT_PROBABILITY}% probability of retracement to current hour open (${current_hour_open:.4f}) within first 20 minutes. Minutes into hour: {minutes_into_hour}. Stop: ${stop_loss:.4f}."
            else:
                signal = 'NOTHING'
                confidence = 0
                reasoning = f"✅ LOW SWEEP RETRACEMENT COMPLETE: Price already at/above current hour open (${current_hour_open:.4f}). Target achieved."

        # NO SWEEP
        else:
            signal = 'NOTHING'
            confidence = 0
            reasoning = f"⚪ NO SWEEP DETECTED: Current hour has not swept previous hour high (${prev_hour_data['prev_hour_high']:.4f}) or low (${prev_hour_data['prev_hour_low']:.4f}). Wait for sweep to occur. Minutes into hour: {minutes_into_hour}."

        cprint(f"\n🎯 Signal: {signal}", "green" if signal == "BUY" else "red" if signal == "SELL" else "yellow")
        cprint(f"📊 Confidence: {confidence}%", "cyan")
        cprint(f"💡 Reasoning: {reasoning}", "white")

        return {
            'signal': signal,
            'confidence': confidence,
            'reasoning': reasoning,
            'prev_hour_data': prev_hour_data,
            'current_hour_data': current_hour_data,
            'sweep_type': sweep_type,
            'time_segment': time_segment,
            'minutes_into_hour': minutes_into_hour,
            'current_price': current_price
        }

    except Exception as e:
        cprint(f"❌ Error in Hour Stats analysis: {str(e)}", "red")
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
    cprint("\n🌙 Moon Dev's Hour Stats Sweep Retracement Agent", "cyan")
    cprint("⏰ Quantitative Hourly Mean Reversion Trading", "cyan")
    cprint("📈 Based on 20-year NQStats data (89% probability in first 20min)\\n", "cyan")

    # Example usage - replace with actual token address
    test_token = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # USDC for testing

    result = generate_hourstats_signal(test_token)

    cprint(f"\n{'='*80}", "green")
    cprint("📋 FINAL RESULT:", "green")
    cprint(f"{'='*80}", "green")
    cprint(f"Signal: {result['signal']}", "yellow")
    cprint(f"Confidence: {result['confidence']}%", "yellow")
    cprint(f"Reasoning: {result['reasoning']}", "white")

if __name__ == "__main__":
    main()

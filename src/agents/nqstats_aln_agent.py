"""
🌙 Moon Dev's ALN Sessions Analysis Agent
Asian-London-New York (ALN) Sessions Trading Agent

Based on NQStats.com 20-year historical data (2004-2024)
Statistical Edge: 73-98% probability

Strategy:
- ALN = Asian (6pm-3am) / London (3am-9:30am) / New York (9:30am-4pm)
- **London Engulfment** (98% edge - HIGHEST IN ALL NQSTATS DATA!):
  - If London engulfs entire Asian range
  - AND NY open inside London range
  - Then 98% probability NY makes new extreme in London's direction
- Asian session LOW → 73% probability RTH stays above Asian low

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

# ALN parameters from NQStats (20-year data)
LONDON_ENGULFMENT_PROBABILITY = 98  # % probability (HIGHEST EDGE!)
ASIAN_LOW_PROBABILITY = 73  # % probability RTH stays above Asian low

# Session times (EST)
ASIAN_START_HOUR = 18  # 6pm previous day
ASIAN_START_MINUTE = 0
ASIAN_END_HOUR = 3  # 3am current day
ASIAN_END_MINUTE = 0

LONDON_START_HOUR = 3  # 3am
LONDON_START_MINUTE = 0
LONDON_END_HOUR = 9  # 9:30am
LONDON_END_MINUTE = 30

NY_OPEN_HOUR = 9  # 9:30am
NY_OPEN_MINUTE = 30
NY_CLOSE_HOUR = 16  # 4pm
NY_CLOSE_MINUTE = 0

# Trading parameters
MIN_CONFIDENCE = 70  # Minimum confidence % to trade
POSITION_SIZE_PERCENT = 2.0  # % of portfolio per trade

# ============================================================================
# ALN SESSION CALCULATION FUNCTIONS
# ============================================================================

def get_asian_session_data(df, current_date):
    """
    Get Asian session data (6pm previous day - 3am current day EST)

    Returns: dict with Asian_high, Asian_low, Asian_range
    """
    # Asian session starts previous day at 6pm
    prev_date = current_date - timedelta(days=1)

    # Calculate Asian session timeframe
    asian_start = datetime.combine(
        prev_date,
        dt_time(ASIAN_START_HOUR, ASIAN_START_MINUTE)
    )
    asian_end = datetime.combine(
        current_date,
        dt_time(ASIAN_END_HOUR, ASIAN_END_MINUTE)
    )

    # Filter data for Asian session
    asian_data = df[
        (df.index >= asian_start) &
        (df.index < asian_end)
    ]

    if len(asian_data) == 0:
        return None

    Asian_high = asian_data['high'].max()
    Asian_low = asian_data['low'].min()
    Asian_range = Asian_high - Asian_low
    Asian_open = asian_data['open'].iloc[0]
    Asian_close = asian_data['close'].iloc[-1]

    return {
        'Asian_high': Asian_high,
        'Asian_low': Asian_low,
        'Asian_range': Asian_range,
        'Asian_open': Asian_open,
        'Asian_close': Asian_close
    }

def get_london_session_data(df, current_date):
    """
    Get London session data (3am - 9:30am EST)

    Returns: dict with London_high, London_low, London_range
    """
    # Calculate London session timeframe
    london_start = datetime.combine(
        current_date,
        dt_time(LONDON_START_HOUR, LONDON_START_MINUTE)
    )
    london_end = datetime.combine(
        current_date,
        dt_time(LONDON_END_HOUR, LONDON_END_MINUTE)
    )

    # Filter data for London session
    london_data = df[
        (df.index >= london_start) &
        (df.index < london_end)
    ]

    if len(london_data) == 0:
        return None

    London_high = london_data['high'].max()
    London_low = london_data['low'].min()
    London_range = London_high - London_low
    London_open = london_data['open'].iloc[0]
    London_close = london_data['close'].iloc[-1]

    # Determine London direction
    if London_close > London_open:
        London_direction = 'BULLISH'
    elif London_close < London_open:
        London_direction = 'BEARISH'
    else:
        London_direction = 'NEUTRAL'

    return {
        'London_high': London_high,
        'London_low': London_low,
        'London_range': London_range,
        'London_open': London_open,
        'London_close': London_close,
        'London_direction': London_direction
    }

def get_ny_open_price(df, current_date):
    """
    Get NY session open price (9:30am EST)

    Returns: float (NY open price)
    """
    ny_open_time = datetime.combine(
        current_date,
        dt_time(NY_OPEN_HOUR, NY_OPEN_MINUTE)
    )

    # Find NY open candle
    ny_open_data = df[
        (df.index >= ny_open_time) &
        (df.index < ny_open_time + timedelta(minutes=5))
    ]

    if len(ny_open_data) == 0:
        return None

    return ny_open_data['open'].iloc[0]

def check_london_engulfment(asian_data, london_data, ny_open):
    """
    Check if London Engulfment pattern exists (98% edge!)

    Conditions:
    1. London high > Asian high (engulfs upside)
    2. London low < Asian low (engulfs downside)
    3. NY open is INSIDE London range

    Returns: bool, reasoning
    """
    # Check if London engulfed entire Asian range
    london_engulfs_asian = (
        london_data['London_high'] > asian_data['Asian_high'] and
        london_data['London_low'] < asian_data['Asian_low']
    )

    # Check if NY open is inside London range
    ny_inside_london = (
        ny_open < london_data['London_high'] and
        ny_open > london_data['London_low']
    )

    if london_engulfs_asian and ny_inside_london:
        return True, f"✅ LONDON ENGULFMENT CONFIRMED: London (${london_data['London_low']:.4f} - ${london_data['London_high']:.4f}) engulfed entire Asian range (${asian_data['Asian_low']:.4f} - ${asian_data['Asian_high']:.4f}) AND NY opened inside London range (${ny_open:.4f}). {LONDON_ENGULFMENT_PROBABILITY}% edge!"
    elif london_engulfs_asian and not ny_inside_london:
        return False, f"⚠️ PARTIAL SETUP: London engulfed Asian BUT NY open (${ny_open:.4f}) is OUTSIDE London range. Pattern invalidated."
    else:
        return False, f"❌ NO ENGULFMENT: London did not engulf entire Asian range."

def check_past_ny_open(current_time):
    """
    Check if current time is past NY open (9:30am)

    Returns: bool, minutes_since_open
    """
    ny_open_time = dt_time(NY_OPEN_HOUR, NY_OPEN_MINUTE)
    current_time_only = current_time.time()

    if current_time_only >= ny_open_time:
        # Calculate minutes since 9:30am
        today_ny_open = datetime.combine(current_time.date(), ny_open_time)
        minutes_since = (current_time - today_ny_open).total_seconds() / 60
        return True, int(minutes_since)
    else:
        return False, 0

def calculate_targets_and_stops(london_data, asian_data, engulfment_exists):
    """
    Calculate target and stop loss based on London Engulfment pattern

    Returns: dict with signal, stop_loss, target, confidence, reasoning
    """
    London_direction = london_data['London_direction']
    London_high = london_data['London_high']
    London_low = london_data['London_low']
    London_range = london_data['London_range']

    if not engulfment_exists:
        # No engulfment - check Asian low pattern
        signal = 'NOTHING'
        stop_loss = asian_data['Asian_low']
        target = None
        confidence = ASIAN_LOW_PROBABILITY
        reasoning = f"⚪ NO ENGULFMENT: Watch Asian low (${asian_data['Asian_low']:.4f}). {ASIAN_LOW_PROBABILITY}% probability RTH stays above Asian low. Consider LONG if price stays above Asian low."

        return {
            'signal': signal,
            'stop_loss': stop_loss,
            'target': target,
            'confidence': confidence,
            'reasoning': reasoning
        }

    # London Engulfment exists - trade in London's direction
    if London_direction == 'BULLISH':
        signal = 'BUY'
        stop_loss = London_low  # Stop at London low
        target = London_high + London_range  # Target: New high beyond London
        reasoning = f"🟢 LONDON ENGULFMENT BULLISH: {LONDON_ENGULFMENT_PROBABILITY}% probability NY makes new extreme HIGH beyond London high (${London_high:.4f}). Trade LONG. Stop: ${stop_loss:.4f}. Target: ${target:.4f}."

    elif London_direction == 'BEARISH':
        signal = 'SELL'
        stop_loss = London_high  # Stop at London high
        target = London_low - London_range  # Target: New low beyond London
        reasoning = f"🔴 LONDON ENGULFMENT BEARISH: {LONDON_ENGULFMENT_PROBABILITY}% probability NY makes new extreme LOW beyond London low (${London_low:.4f}). Trade SHORT. Stop: ${stop_loss:.4f}. Target: ${target:.4f}."

    else:
        signal = 'NOTHING'
        stop_loss = None
        target = None
        reasoning = f"⚪ LONDON NEUTRAL: London session closed flat. No directional edge despite engulfment."

    return {
        'signal': signal,
        'stop_loss': stop_loss,
        'target': target,
        'confidence': LONDON_ENGULFMENT_PROBABILITY,
        'reasoning': reasoning
    }

# ============================================================================
# SIGNAL GENERATION
# ============================================================================

def generate_aln_signal(token_address):
    """
    Generate ALN Sessions trading signal

    Returns: dict with signal, confidence, reasoning
    """
    cprint(f"\n{'='*80}", "cyan")
    cprint(f"🌍 ALN SESSIONS ANALYSIS AGENT - {token_address}", "cyan")
    cprint(f"{'='*80}", "cyan")

    try:
        # Get OHLCV data (5-minute bars for session precision, need 2 days for Asian session)
        df = get_ohlcv_data(token_address, timeframe='5m', days_back=3)

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

        # Check if past NY open
        past_ny_open, minutes_since_open = check_past_ny_open(current_time)

        if not past_ny_open:
            return {
                'signal': 'NOTHING',
                'confidence': 0,
                'reasoning': f'⏰ NY NOT YET OPEN: Currently {current_time.strftime("%H:%M")} EST. Wait until after 9:30am for ALN pattern confirmation.'
            }

        # Get Asian session data
        asian_data = get_asian_session_data(df, current_date)
        if not asian_data:
            return {
                'signal': 'NOTHING',
                'confidence': 0,
                'reasoning': 'Unable to get Asian session data.'
            }

        # Get London session data
        london_data = get_london_session_data(df, current_date)
        if not london_data:
            return {
                'signal': 'NOTHING',
                'confidence': 0,
                'reasoning': 'Unable to get London session data.'
            }

        # Get NY open price
        ny_open = get_ny_open_price(df, current_date)
        if not ny_open:
            return {
                'signal': 'NOTHING',
                'confidence': 0,
                'reasoning': 'Unable to get NY open price.'
            }

        # Check for London Engulfment pattern
        engulfment_exists, engulfment_reasoning = check_london_engulfment(asian_data, london_data, ny_open)

        # Calculate targets and stops
        targets_stops = calculate_targets_and_stops(london_data, asian_data, engulfment_exists)

        # Print analysis
        cprint(f"\n📊 Asian Session (6pm-3am):", "yellow")
        cprint(f"  High: ${asian_data['Asian_high']:.4f}", "yellow")
        cprint(f"  Low: ${asian_data['Asian_low']:.4f}", "yellow")
        cprint(f"  Range: ${asian_data['Asian_range']:.4f}", "yellow")

        cprint(f"\n📊 London Session (3am-9:30am):", "yellow")
        cprint(f"  High: ${london_data['London_high']:.4f}", "yellow")
        cprint(f"  Low: ${london_data['London_low']:.4f}", "yellow")
        cprint(f"  Range: ${london_data['London_range']:.4f}", "yellow")
        cprint(f"  Direction: {london_data['London_direction']}", "green" if london_data['London_direction'] == 'BULLISH' else "red")

        cprint(f"\n📊 New York Session:", "yellow")
        cprint(f"  NY Open (9:30am): ${ny_open:.4f}", "yellow")
        cprint(f"  Current Price: ${current_price:.4f}", "yellow")
        cprint(f"  Minutes Since Open: {minutes_since_open}", "cyan")

        cprint(f"\n🎯 London Engulfment Analysis:", "cyan")
        cprint(f"  {engulfment_reasoning}", "green" if engulfment_exists else "yellow")

        if engulfment_exists:
            cprint(f"\n🚨 HIGHEST PROBABILITY SETUP IN NQSTATS DATA! 🚨", "magenta")
            cprint(f"  London Engulfment = {LONDON_ENGULFMENT_PROBABILITY}% edge", "magenta")

        if targets_stops['stop_loss']:
            cprint(f"\n🎯 Trade Setup:", "cyan")
            cprint(f"  Signal: {targets_stops['signal']}", "green" if targets_stops['signal'] == 'BUY' else "red")
            cprint(f"  Stop Loss: ${targets_stops['stop_loss']:.4f}", "red")
            if targets_stops['target']:
                cprint(f"  Target: ${targets_stops['target']:.4f}", "green")
            cprint(f"  Confidence: {targets_stops['confidence']:.0f}%", "cyan")

        # Generate final signal
        signal = targets_stops['signal']
        confidence = targets_stops['confidence']
        reasoning = targets_stops['reasoning']

        cprint(f"\n🎯 Signal: {signal}", "green" if signal == "BUY" else "red" if signal == "SELL" else "yellow")
        cprint(f"📊 Confidence: {confidence:.0f}%", "cyan")
        cprint(f"💡 Reasoning: {reasoning}", "white")

        return {
            'signal': signal,
            'confidence': confidence,
            'reasoning': reasoning,
            'asian_data': asian_data,
            'london_data': london_data,
            'ny_open': ny_open,
            'engulfment_exists': engulfment_exists,
            'targets_stops': targets_stops,
            'current_price': current_price,
            'minutes_since_open': minutes_since_open
        }

    except Exception as e:
        cprint(f"❌ Error in ALN analysis: {str(e)}", "red")
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
    cprint("\n🌙 Moon Dev's ALN Sessions Analysis Agent", "cyan")
    cprint("🌍 Asian-London-New York Session Trading", "cyan")
    cprint("📈 Based on 20-year NQStats data (73-98% probability)\\n", "cyan")
    cprint("🚨 London Engulfment = HIGHEST EDGE (98%) in all NQStats data! 🚨\\n", "magenta")

    # Example usage - replace with actual token address
    test_token = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # USDC for testing

    result = generate_aln_signal(test_token)

    cprint(f"\n{'='*80}", "green")
    cprint("📋 FINAL RESULT:", "green")
    cprint(f"{'='*80}", "green")
    cprint(f"Signal: {result['signal']}", "yellow")
    cprint(f"Confidence: {result['confidence']:.0f}%", "yellow")
    cprint(f"Reasoning: {result['reasoning']}", "white")

if __name__ == "__main__":
    main()

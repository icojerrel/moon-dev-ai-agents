"""
🌙 Moon Dev's RTH Break Directional Bias Agent
Regular Trading Hours Break Analysis Agent

Based on NQStats.com 20-year historical data (2004-2024)
Statistical Edge: 83.29% probability

Strategy:
- Compare current RTH open (9:30am EST) with previous day RTH range
- RTH opens OUTSIDE pRTH high → 83.29% probability WON'T break pRTH low
- RTH opens BELOW pRTH low → 83.29% probability WON'T break pRTH high
- Strong directional bias based on opening displacement

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

# RTH Break parameters from NQStats (20-year data)
RTH_BREAK_PROBABILITY = 83.29  # % probability won't break opposite side

# RTH session times (EST)
RTH_OPEN_HOUR = 9
RTH_OPEN_MINUTE = 30
RTH_CLOSE_HOUR = 16
RTH_CLOSE_MINUTE = 0

# Trading parameters
MIN_CONFIDENCE = 70  # Minimum confidence % to trade
POSITION_SIZE_PERCENT = 2.0  # % of portfolio per trade
TARGET_MULTIPLE = 1.5  # Target = 1.5x previous RTH range

# ============================================================================
# RTH CALCULATION FUNCTIONS
# ============================================================================

def get_rth_session_times(date):
    """
    Get RTH open and close times for a given date

    Returns: tuple of (rth_open, rth_close) datetime objects
    """
    rth_open = datetime.combine(date, dt_time(RTH_OPEN_HOUR, RTH_OPEN_MINUTE))
    rth_close = datetime.combine(date, dt_time(RTH_CLOSE_HOUR, RTH_CLOSE_MINUTE))
    return rth_open, rth_close

def get_previous_rth_range(df, current_date):
    """
    Get previous day's RTH range (high, low, open, close)

    Returns: dict with pRTH_high, pRTH_low, pRTH_open, pRTH_close, pRTH_range
    """
    # Calculate previous trading day (skip weekends)
    prev_date = current_date - timedelta(days=1)

    # Skip weekends
    while prev_date.weekday() >= 5:  # 5=Saturday, 6=Sunday
        prev_date = prev_date - timedelta(days=1)

    prev_rth_open, prev_rth_close = get_rth_session_times(prev_date)

    # Filter data for previous RTH session
    prev_rth_data = df[
        (df.index >= prev_rth_open) &
        (df.index <= prev_rth_close)
    ]

    if len(prev_rth_data) == 0:
        return None

    pRTH_high = prev_rth_data['high'].max()
    pRTH_low = prev_rth_data['low'].min()
    pRTH_range = pRTH_high - pRTH_low

    return {
        'pRTH_high': pRTH_high,
        'pRTH_low': pRTH_low,
        'pRTH_open': prev_rth_data['open'].iloc[0],
        'pRTH_close': prev_rth_data['close'].iloc[-1],
        'pRTH_range': pRTH_range,
        'pRTH_date': prev_date
    }

def get_current_rth_open(df, current_date):
    """
    Get current day's RTH open price (9:30am EST)

    Returns: float (RTH open price)
    """
    current_rth_open_time, _ = get_rth_session_times(current_date)

    # Find RTH open candle
    rth_open_data = df[
        (df.index >= current_rth_open_time) &
        (df.index < current_rth_open_time + timedelta(minutes=5))
    ]

    if len(rth_open_data) == 0:
        return None

    return rth_open_data['open'].iloc[0]

def analyze_rth_break(current_rth_open, prev_rth_data):
    """
    Analyze RTH break scenario

    Returns: dict with scenario, direction, stop_loss, target, probability
    """
    pRTH_high = prev_rth_data['pRTH_high']
    pRTH_low = prev_rth_data['pRTH_low']
    pRTH_range = prev_rth_data['pRTH_range']

    # Scenario 1: RTH opens OUTSIDE (ABOVE) pRTH high
    if current_rth_open > pRTH_high:
        displacement = current_rth_open - pRTH_high
        return {
            'scenario': 'OPENS_ABOVE_PRTH',
            'direction': 'BULLISH',
            'signal': 'BUY',
            'displacement': displacement,
            'stop_loss': pRTH_low,
            'target': current_rth_open + (pRTH_range * TARGET_MULTIPLE),
            'probability': RTH_BREAK_PROBABILITY,
            'reasoning': f"RTH opened ${displacement:.4f} ABOVE previous RTH high (${pRTH_high:.4f}). {RTH_BREAK_PROBABILITY}% probability price will NOT break opposite side (pRTH low: ${pRTH_low:.4f}). Strong bullish bias."
        }

    # Scenario 2: RTH opens OUTSIDE (BELOW) pRTH low
    elif current_rth_open < pRTH_low:
        displacement = pRTH_low - current_rth_open
        return {
            'scenario': 'OPENS_BELOW_PRTH',
            'direction': 'BEARISH',
            'signal': 'SELL',
            'displacement': displacement,
            'stop_loss': pRTH_high,
            'target': current_rth_open - (pRTH_range * TARGET_MULTIPLE),
            'probability': RTH_BREAK_PROBABILITY,
            'reasoning': f"RTH opened ${displacement:.4f} BELOW previous RTH low (${pRTH_low:.4f}). {RTH_BREAK_PROBABILITY}% probability price will NOT break opposite side (pRTH high: ${pRTH_high:.4f}). Strong bearish bias."
        }

    # Scenario 3: RTH opens INSIDE pRTH range
    else:
        position_in_range = (current_rth_open - pRTH_low) / pRTH_range * 100
        return {
            'scenario': 'OPENS_INSIDE_PRTH',
            'direction': 'NEUTRAL',
            'signal': 'NOTHING',
            'displacement': 0,
            'stop_loss': None,
            'target': None,
            'probability': 50,
            'reasoning': f"RTH opened INSIDE previous RTH range (${pRTH_low:.4f} - ${pRTH_high:.4f}). Position: {position_in_range:.1f}% of range. No directional edge. Wait for breakout above pRTH high or below pRTH low."
        }

def check_stop_hit(current_price, analysis, prev_rth_data):
    """
    Check if stop loss has been hit (opposite extreme breached)

    Returns: bool, reasoning
    """
    if analysis['scenario'] == 'OPENS_ABOVE_PRTH':
        # Stop = pRTH low breached
        if current_price < prev_rth_data['pRTH_low']:
            return True, f"❌ STOP HIT: Price breached pRTH low (${prev_rth_data['pRTH_low']:.4f}). This is the 16.71% scenario where directional bias failed."
        return False, None

    elif analysis['scenario'] == 'OPENS_BELOW_PRTH':
        # Stop = pRTH high breached
        if current_price > prev_rth_data['pRTH_high']:
            return True, f"❌ STOP HIT: Price breached pRTH high (${prev_rth_data['pRTH_high']:.4f}). This is the 16.71% scenario where directional bias failed."
        return False, None

    return False, None

# ============================================================================
# SIGNAL GENERATION
# ============================================================================

def generate_rth_signal(token_address):
    """
    Generate RTH Break Directional Bias trading signal

    Returns: dict with signal, confidence, reasoning
    """
    cprint(f"\n{'='*80}", "cyan")
    cprint(f"📈 RTH BREAK DIRECTIONAL BIAS AGENT - {token_address}", "cyan")
    cprint(f"{'='*80}", "cyan")

    try:
        # Get OHLCV data (5-minute bars for RTH precision)
        df = get_ohlcv_data(token_address, timeframe='5m', days_back=5)

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

        # Get current date
        current_date = datetime.now().date()

        # Get previous RTH range
        prev_rth_data = get_previous_rth_range(df, current_date)
        if not prev_rth_data:
            return {
                'signal': 'NOTHING',
                'confidence': 0,
                'reasoning': 'Unable to get previous RTH range data'
            }

        # Get current RTH open
        current_rth_open = get_current_rth_open(df, current_date)
        if not current_rth_open:
            return {
                'signal': 'NOTHING',
                'confidence': 0,
                'reasoning': 'Unable to get current RTH open price. Strategy only valid during RTH (9:30am-4pm EST).'
            }

        # Analyze RTH break
        analysis = analyze_rth_break(current_rth_open, prev_rth_data)

        # Check if stop hit
        stop_hit, stop_reasoning = check_stop_hit(current_price, analysis, prev_rth_data)

        # Print analysis
        cprint(f"\n📊 Previous RTH Data ({prev_rth_data['pRTH_date']}):", "yellow")
        cprint(f"  High: ${prev_rth_data['pRTH_high']:.4f}", "yellow")
        cprint(f"  Low: ${prev_rth_data['pRTH_low']:.4f}", "yellow")
        cprint(f"  Range: ${prev_rth_data['pRTH_range']:.4f}", "yellow")

        cprint(f"\n📊 Current RTH:", "yellow")
        cprint(f"  Open (9:30am): ${current_rth_open:.4f}", "yellow")
        cprint(f"  Current Price: ${current_price:.4f}", "yellow")

        cprint(f"\n🎯 RTH Break Analysis:", "cyan")
        cprint(f"  Scenario: {analysis['scenario']}", "cyan")
        cprint(f"  Direction: {analysis['direction']}", "cyan")
        if analysis['displacement'] > 0:
            cprint(f"  Displacement: ${analysis['displacement']:.4f}", "cyan")
        if analysis['stop_loss']:
            cprint(f"  Stop Loss: ${analysis['stop_loss']:.4f}", "red")
        if analysis['target']:
            cprint(f"  Target: ${analysis['target']:.4f}", "green")

        # Generate final signal
        signal = 'NOTHING'
        confidence = 0
        reasoning = ""

        if stop_hit:
            signal = 'NOTHING'
            confidence = 0
            reasoning = stop_reasoning

        elif analysis['scenario'] == 'OPENS_INSIDE_PRTH':
            signal = 'NOTHING'
            confidence = 50
            reasoning = analysis['reasoning']

        else:
            signal = analysis['signal']
            confidence = int(analysis['probability'])
            reasoning = analysis['reasoning']

        cprint(f"\n🎯 Signal: {signal}", "green" if signal == "BUY" else "red" if signal == "SELL" else "yellow")
        cprint(f"📊 Confidence: {confidence}%", "cyan")
        cprint(f"💡 Reasoning: {reasoning}", "white")

        return {
            'signal': signal,
            'confidence': confidence,
            'reasoning': reasoning,
            'prev_rth_data': prev_rth_data,
            'current_rth_open': current_rth_open,
            'analysis': analysis,
            'stop_hit': stop_hit,
            'current_price': current_price
        }

    except Exception as e:
        cprint(f"❌ Error in RTH Break analysis: {str(e)}", "red")
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
    cprint("\n🌙 Moon Dev's RTH Break Directional Bias Agent", "cyan")
    cprint("📈 Quantitative Session Break Trading", "cyan")
    cprint("📊 Based on 20-year NQStats data (83.29% directional probability)\\n", "cyan")

    # Example usage - replace with actual token address
    test_token = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # USDC for testing

    result = generate_rth_signal(test_token)

    cprint(f"\n{'='*80}", "green")
    cprint("📋 FINAL RESULT:", "green")
    cprint(f"{'='*80}", "green")
    cprint(f"Signal: {result['signal']}", "yellow")
    cprint(f"Confidence: {result['confidence']}%", "yellow")
    cprint(f"Reasoning: {result['reasoning']}", "white")

if __name__ == "__main__":
    main()

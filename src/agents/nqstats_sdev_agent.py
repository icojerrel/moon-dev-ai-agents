"""
🌙 Moon Dev's SDEV Analysis Agent
Standard Deviation Mean Reversion Trading Agent

Based on NQStats.com 20-year historical data (2004-2024)
Statistical Edge: 68-84% probability

Strategy:
- Calculate ±1.0 SDEV from session open (±1.376%)
- 68.27% probability session closes within ±1.0 SDEV range
- 84.13% probability session closes above -1.0 SDEV
- Fade moves beyond +1.5 SDEV expecting reversion

Built with love by Moon Dev 🚀
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, time as dt_time
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

# SDEV parameters from NQStats (20-year data)
DAILY_SDEV_PERCENTAGE = 1.376  # ±1.0 SDEV = ±1.376% from session open
HOURLY_SDEV_PERCENTAGE = 0.5   # For 1-hour timeframe intraday

# Probability thresholds
SDEV_1_0_PROBABILITY = 68.27  # % probability within ±1.0 SDEV
SDEV_ABOVE_NEG_1_PROBABILITY = 84.13  # % probability above -1.0 SDEV

# Trading parameters
MIN_CONFIDENCE = 60  # Minimum confidence % to trade
POSITION_SIZE_PERCENT = 2.0  # % of portfolio per trade

# Session times (EST)
SESSION_OPEN_HOUR = 9   # 9:30am
SESSION_OPEN_MINUTE = 30
SESSION_CLOSE_HOUR = 16  # 4:00pm

# ============================================================================
# SDEV CALCULATION FUNCTIONS
# ============================================================================

def calculate_session_open(df):
    """Get today's session open price (9:30am EST)"""
    today = datetime.now().date()
    session_opens = df[
        (df.index.date == today) &
        (df.index.hour == SESSION_OPEN_HOUR) &
        (df.index.minute == SESSION_OPEN_MINUTE)
    ]

    if len(session_opens) > 0:
        return session_opens['open'].iloc[0]

    # Fallback: use first price of today
    today_data = df[df.index.date == today]
    if len(today_data) > 0:
        return today_data['open'].iloc[0]

    return None

def calculate_sdev_levels(session_open, timeframe='daily'):
    """
    Calculate standard deviation levels from session open

    Returns: dict with SDEV levels and probabilities
    """
    if timeframe == 'daily':
        sdev_pct = DAILY_SDEV_PERCENTAGE
    else:
        sdev_pct = HOURLY_SDEV_PERCENTAGE

    levels = {
        'session_open': session_open,
        'sdev_0.5_upper': session_open * (1 + (sdev_pct * 0.5 / 100)),
        'sdev_0.5_lower': session_open * (1 - (sdev_pct * 0.5 / 100)),
        'sdev_1.0_upper': session_open * (1 + (sdev_pct / 100)),
        'sdev_1.0_lower': session_open * (1 - (sdev_pct / 100)),
        'sdev_1.5_upper': session_open * (1 + (sdev_pct * 1.5 / 100)),
        'sdev_1.5_lower': session_open * (1 - (sdev_pct * 1.5 / 100)),
        'sdev_2.0_upper': session_open * (1 + (sdev_pct * 2.0 / 100)),
        'sdev_2.0_lower': session_open * (1 - (sdev_pct * 2.0 / 100)),
    }

    return levels

def get_sdev_zone(current_price, sdev_levels):
    """Determine which SDEV zone current price is in"""
    session_open = sdev_levels['session_open']

    if current_price >= sdev_levels['sdev_2.0_upper']:
        return '+2.0_SDEV', 'EXTREME_OVERBOUGHT'
    elif current_price >= sdev_levels['sdev_1.5_upper']:
        return '+1.5_SDEV', 'STRONG_OVERBOUGHT'
    elif current_price >= sdev_levels['sdev_1.0_upper']:
        return '+1.0_SDEV', 'OVERBOUGHT'
    elif current_price >= sdev_levels['sdev_0.5_upper']:
        return '+0.5_SDEV', 'SLIGHTLY_OVERBOUGHT'
    elif current_price >= session_open:
        return 'ABOVE_MEAN', 'NEUTRAL_BULLISH'
    elif current_price >= sdev_levels['sdev_0.5_lower']:
        return '-0.5_SDEV', 'SLIGHTLY_OVERSOLD'
    elif current_price >= sdev_levels['sdev_1.0_lower']:
        return '-1.0_SDEV', 'OVERSOLD'
    elif current_price >= sdev_levels['sdev_1.5_lower']:
        return '-1.5_SDEV', 'STRONG_OVERSOLD'
    else:
        return '-2.0_SDEV', 'EXTREME_OVERSOLD'

def calculate_reversion_probability(zone, direction):
    """
    Calculate probability of mean reversion based on SDEV zone

    zone: Current SDEV zone
    direction: 'LONG' (fade shorts) or 'SHORT' (fade longs)
    """
    # Rubber band theory: further from mean = higher reversion probability
    probabilities = {
        'EXTREME_OVERBOUGHT': 84,  # >+2.0 SDEV
        'STRONG_OVERBOUGHT': 75,   # +1.5 to +2.0 SDEV
        'OVERBOUGHT': 68,          # +1.0 to +1.5 SDEV
        'SLIGHTLY_OVERBOUGHT': 55, # +0.5 to +1.0 SDEV
        'NEUTRAL_BULLISH': 50,
        'SLIGHTLY_OVERSOLD': 55,
        'OVERSOLD': 68,
        'STRONG_OVERSOLD': 75,
        'EXTREME_OVERSOLD': 84,
    }

    return probabilities.get(direction.split('_')[-1], 50)

# ============================================================================
# SIGNAL GENERATION
# ============================================================================

def generate_sdev_signal(token_address):
    """
    Generate SDEV-based trading signal

    Returns: dict with signal, confidence, reasoning
    """
    cprint(f"\n{'='*80}", "cyan")
    cprint(f"📊 SDEV ANALYSIS AGENT - {token_address}", "cyan")
    cprint(f"{'='*80}", "cyan")

    try:
        # Get OHLCV data (15-minute bars for intraday)
        df = get_ohlcv_data(token_address, timeframe='15m', days_back=2)

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

        # Get session open
        session_open = calculate_session_open(df)
        if not session_open:
            return {
                'signal': 'NOTHING',
                'confidence': 0,
                'reasoning': 'Unable to determine session open price'
            }

        # Calculate SDEV levels
        sdev_levels = calculate_sdev_levels(session_open, timeframe='daily')

        # Determine current zone
        zone, condition = get_sdev_zone(current_price, sdev_levels)

        # Print analysis
        cprint(f"\n📈 Session Open: ${session_open:.4f}", "yellow")
        cprint(f"💰 Current Price: ${current_price:.4f}", "yellow")
        cprint(f"📍 Current Zone: {zone} ({condition})", "yellow")

        cprint(f"\n🎯 SDEV Levels:", "cyan")
        cprint(f"  +2.0 SDEV: ${sdev_levels['sdev_2.0_upper']:.4f}", "red")
        cprint(f"  +1.5 SDEV: ${sdev_levels['sdev_1.5_upper']:.4f}", "yellow")
        cprint(f"  +1.0 SDEV: ${sdev_levels['sdev_1.0_upper']:.4f}", "green")
        cprint(f"  +0.5 SDEV: ${sdev_levels['sdev_0.5_upper']:.4f}", "white")
        cprint(f"  Session Open: ${session_open:.4f}", "cyan")
        cprint(f"  -0.5 SDEV: ${sdev_levels['sdev_0.5_lower']:.4f}", "white")
        cprint(f"  -1.0 SDEV: ${sdev_levels['sdev_1.0_lower']:.4f}", "green")
        cprint(f"  -1.5 SDEV: ${sdev_levels['sdev_1.5_lower']:.4f}", "yellow")
        cprint(f"  -2.0 SDEV: ${sdev_levels['sdev_2.0_lower']:.4f}", "red")

        # Generate signal based on mean reversion logic
        signal = 'NOTHING'
        confidence = 0
        reasoning = ""

        # FADE OVERBOUGHT (SHORT signal when price extends too far up)
        if 'EXTREME_OVERBOUGHT' in condition:
            signal = 'SELL'
            confidence = 84
            reasoning = f"🔴 EXTREME OVERBOUGHT: Price at {zone}, {84}% probability of reversion to mean. Fade the move expecting pullback to session open (${session_open:.4f}) or +0.5 SDEV (${sdev_levels['sdev_0.5_upper']:.4f})."

        elif 'STRONG_OVERBOUGHT' in condition:
            signal = 'SELL'
            confidence = 75
            reasoning = f"🟠 STRONG OVERBOUGHT: Price at {zone}, {75}% probability of reversion. Target: +0.5 SDEV (${sdev_levels['sdev_0.5_upper']:.4f}) or session open (${session_open:.4f})."

        elif 'OVERBOUGHT' in condition and current_price > sdev_levels['sdev_1.0_upper']:
            signal = 'SELL'
            confidence = 68
            reasoning = f"🟡 OVERBOUGHT: Price beyond +1.0 SDEV ({68.27}% containment zone). Fade for mean reversion. Stop: +2.0 SDEV (${sdev_levels['sdev_2.0_upper']:.4f})."

        # FADE OVERSOLD (BUY signal when price extends too far down)
        elif 'EXTREME_OVERSOLD' in condition:
            signal = 'BUY'
            confidence = 84
            reasoning = f"🟢 EXTREME OVERSOLD: Price at {zone}, {84.13}% probability above -1.0 SDEV. Strong reversion setup. Target: session open (${session_open:.4f})."

        elif 'STRONG_OVERSOLD' in condition:
            signal = 'BUY'
            confidence = 75
            reasoning = f"🟢 STRONG OVERSOLD: Price at {zone}, high reversion probability. Target: -0.5 SDEV (${sdev_levels['sdev_0.5_lower']:.4f}) to session open."

        elif 'OVERSOLD' in condition and current_price < sdev_levels['sdev_1.0_lower']:
            signal = 'BUY'
            confidence = 68
            reasoning = f"🟢 OVERSOLD: Price below -1.0 SDEV. {68.27}% probability of reversion. Stop: -2.0 SDEV (${sdev_levels['sdev_2.0_lower']:.4f})."

        # NEUTRAL ZONE
        else:
            signal = 'NOTHING'
            confidence = 50
            reasoning = f"⚪ NEUTRAL ZONE: Price near session open. Wait for price to extend beyond ±1.0 SDEV for high-probability mean reversion setup. Current zone: {zone}."

        cprint(f"\n🎯 Signal: {signal}", "green" if signal == "BUY" else "red" if signal == "SELL" else "yellow")
        cprint(f"📊 Confidence: {confidence}%", "cyan")
        cprint(f"💡 Reasoning: {reasoning}", "white")

        return {
            'signal': signal,
            'confidence': confidence,
            'reasoning': reasoning,
            'sdev_levels': sdev_levels,
            'current_zone': zone,
            'session_open': session_open,
            'current_price': current_price
        }

    except Exception as e:
        cprint(f"❌ Error in SDEV analysis: {str(e)}", "red")
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
    cprint("\n🌙 Moon Dev's SDEV Analysis Agent", "cyan")
    cprint("📊 Quantitative Mean Reversion Trading", "cyan")
    cprint("📈 Based on 20-year NQStats data (68-84% probabilities)\n", "cyan")

    # Example usage - replace with actual token address
    test_token = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # USDC for testing

    result = generate_sdev_signal(test_token)

    cprint(f"\n{'='*80}", "green")
    cprint("📋 FINAL RESULT:", "green")
    cprint(f"{'='*80}", "green")
    cprint(f"Signal: {result['signal']}", "yellow")
    cprint(f"Confidence: {result['confidence']}%", "yellow")
    cprint(f"Reasoning: {result['reasoning']}", "white")

if __name__ == "__main__":
    main()

"""
🌙 Moon Dev's SMC Indicator Module
Smart Money Concepts: IFVG, Breaker Blocks, Order Blocks, etc.
Built with love by Moon Dev 🚀
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from termcolor import cprint


class SMCIndicators:
    """Smart Money Concepts indicator detection"""

    @staticmethod
    def detect_ifvg(candles: pd.DataFrame, lookback: int = 50) -> List[Dict]:
        """
        Detect Imbalance Fair Value Gaps (IFVG)

        An IFVG occurs when there's a gap between candle 1's high and candle 3's low
        (for bullish) or candle 1's low and candle 3's high (for bearish), indicating
        institutional order flow imbalance.

        Args:
            candles: DataFrame with OHLC data
            lookback: How many recent candles to check

        Returns:
            List of IFVGs with details
        """
        ifvgs = []

        df = candles.tail(lookback).copy()
        df = df.reset_index(drop=True)

        for i in range(2, len(df)):
            # Bullish IFVG: Gap between candle[i-2].low and candle[i].high
            # Middle candle must have wick that doesn't fill the gap
            if i >= 2:
                gap_bottom = df.loc[i-2, 'High']
                gap_top = df.loc[i, 'Low']

                # Bullish IFVG: Price jumped up, leaving imbalance below
                if gap_bottom < gap_top:
                    # Check if middle candle doesn't fill gap
                    middle_low = df.loc[i-1, 'Low']
                    middle_high = df.loc[i-1, 'High']

                    if middle_low > gap_bottom and middle_high < gap_top:
                        # Valid bullish IFVG
                        ifvgs.append({
                            'type': 'BULLISH',
                            'top': gap_top,
                            'bottom': gap_bottom,
                            'size': gap_top - gap_bottom,
                            'candle_index': i,
                            'timestamp': df.loc[i, 'datetime'] if 'datetime' in df.columns else i,
                            'filled': False,
                            'current_price_relation': 'below'  # Will be updated
                        })

                # Bearish IFVG: Price dropped, leaving imbalance above
                gap_top_bear = df.loc[i-2, 'Low']
                gap_bottom_bear = df.loc[i, 'High']

                if gap_top_bear > gap_bottom_bear:
                    middle_low = df.loc[i-1, 'Low']
                    middle_high = df.loc[i-1, 'High']

                    if middle_high < gap_top_bear and middle_low > gap_bottom_bear:
                        # Valid bearish IFVG
                        ifvgs.append({
                            'type': 'BEARISH',
                            'top': gap_top_bear,
                            'bottom': gap_bottom_bear,
                            'size': gap_top_bear - gap_bottom_bear,
                            'candle_index': i,
                            'timestamp': df.loc[i, 'datetime'] if 'datetime' in df.columns else i,
                            'filled': False,
                            'current_price_relation': 'above'
                        })

        # Update current price relation for all IFVGs
        if len(df) > 0:
            current_price = df.iloc[-1]['Close']
            for ifvg in ifvgs:
                if current_price > ifvg['top']:
                    ifvg['current_price_relation'] = 'above'
                elif current_price < ifvg['bottom']:
                    ifvg['current_price_relation'] = 'below'
                else:
                    ifvg['current_price_relation'] = 'inside'
                    ifvg['filled'] = True

        return ifvgs

    @staticmethod
    def detect_breaker_blocks(candles: pd.DataFrame, lookback: int = 50) -> List[Dict]:
        """
        Detect Breaker Blocks

        A breaker block is a former support that gets broken and becomes resistance
        (bearish breaker) or former resistance that gets broken and becomes support
        (bullish breaker).

        Args:
            candles: DataFrame with OHLC data
            lookback: How many recent candles to check

        Returns:
            List of breaker blocks
        """
        breakers = []

        df = candles.tail(lookback).copy()
        df = df.reset_index(drop=True)

        if len(df) < 10:
            return breakers

        # Find swing highs and lows
        for i in range(5, len(df) - 5):
            # Swing High: Higher than 5 candles on each side
            is_swing_high = True
            for j in range(1, 6):
                if df.loc[i, 'High'] <= df.loc[i-j, 'High'] or df.loc[i, 'High'] <= df.loc[i+j, 'High']:
                    is_swing_high = False
                    break

            if is_swing_high:
                # Check if this resistance was broken to the upside (bullish breaker)
                resistance_level = df.loc[i, 'High']
                broken = False

                for j in range(i+1, len(df)):
                    if df.loc[j, 'Close'] > resistance_level:
                        broken = True
                        breakers.append({
                            'type': 'BULLISH_BREAKER',
                            'level': resistance_level,
                            'candle_index': i,
                            'broken_at': j,
                            'timestamp': df.loc[i, 'datetime'] if 'datetime' in df.columns else i,
                            'strength': 'strong' if (j - i) < 10 else 'weak'
                        })
                        break

            # Swing Low: Lower than 5 candles on each side
            is_swing_low = True
            for j in range(1, 6):
                if df.loc[i, 'Low'] >= df.loc[i-j, 'Low'] or df.loc[i, 'Low'] >= df.loc[i+j, 'Low']:
                    is_swing_low = False
                    break

            if is_swing_low:
                # Check if this support was broken to the downside (bearish breaker)
                support_level = df.loc[i, 'Low']
                broken = False

                for j in range(i+1, len(df)):
                    if df.loc[j, 'Close'] < support_level:
                        broken = True
                        breakers.append({
                            'type': 'BEARISH_BREAKER',
                            'level': support_level,
                            'candle_index': i,
                            'broken_at': j,
                            'timestamp': df.loc[i, 'datetime'] if 'datetime' in df.columns else i,
                            'strength': 'strong' if (j - i) < 10 else 'weak'
                        })
                        break

        return breakers

    @staticmethod
    def detect_order_blocks(candles: pd.DataFrame, lookback: int = 50) -> List[Dict]:
        """
        Detect Order Blocks

        An order block is the last up candle before a strong down move (bearish OB)
        or the last down candle before a strong up move (bullish OB).

        Args:
            candles: DataFrame with OHLC data
            lookback: How many recent candles to check

        Returns:
            List of order blocks
        """
        order_blocks = []

        df = candles.tail(lookback).copy()
        df = df.reset_index(drop=True)

        for i in range(1, len(df) - 3):
            # Bullish Order Block: Last red candle before strong green move
            if df.loc[i, 'Close'] < df.loc[i, 'Open']:  # Red candle
                # Check for strong up move in next 3 candles
                next_move = df.loc[i+1:i+4, 'Close'].max() - df.loc[i, 'Close']
                avg_range = df.loc[i-5:i, 'High'].subtract(df.loc[i-5:i, 'Low']).mean() if i >= 5 else 0.001

                if next_move > (avg_range * 2):  # Strong move = 2x average range
                    order_blocks.append({
                        'type': 'BULLISH_OB',
                        'top': df.loc[i, 'Open'],  # Top of red candle
                        'bottom': df.loc[i, 'Close'],  # Bottom of red candle
                        'candle_index': i,
                        'timestamp': df.loc[i, 'datetime'] if 'datetime' in df.columns else i,
                        'strength': 'strong' if next_move > (avg_range * 3) else 'medium'
                    })

            # Bearish Order Block: Last green candle before strong red move
            elif df.loc[i, 'Close'] > df.loc[i, 'Open']:  # Green candle
                # Check for strong down move in next 3 candles
                next_move = df.loc[i, 'Close'] - df.loc[i+1:i+4, 'Close'].min()
                avg_range = df.loc[i-5:i, 'High'].subtract(df.loc[i-5:i, 'Low']).mean() if i >= 5 else 0.001

                if next_move > (avg_range * 2):
                    order_blocks.append({
                        'type': 'BEARISH_OB',
                        'top': df.loc[i, 'Close'],  # Top of green candle
                        'bottom': df.loc[i, 'Open'],  # Bottom of green candle
                        'candle_index': i,
                        'timestamp': df.loc[i, 'datetime'] if 'datetime' in df.columns else i,
                        'strength': 'strong' if next_move > (avg_range * 3) else 'medium'
                    })

        return order_blocks

    @staticmethod
    def detect_liquidity_zones(candles: pd.DataFrame, lookback: int = 50) -> List[Dict]:
        """
        Detect Liquidity Zones (areas with multiple swing highs/lows)

        These are areas where stop losses cluster, making them targets for
        institutional traders.

        Args:
            candles: DataFrame with OHLC data
            lookback: How many recent candles to check

        Returns:
            List of liquidity zones
        """
        zones = []

        df = candles.tail(lookback).copy()
        df = df.reset_index(drop=True)

        # Find all swing highs
        swing_highs = []
        for i in range(3, len(df) - 3):
            if (df.loc[i, 'High'] > df.loc[i-1, 'High'] and
                df.loc[i, 'High'] > df.loc[i-2, 'High'] and
                df.loc[i, 'High'] > df.loc[i+1, 'High'] and
                df.loc[i, 'High'] > df.loc[i+2, 'High']):
                swing_highs.append(df.loc[i, 'High'])

        # Find all swing lows
        swing_lows = []
        for i in range(3, len(df) - 3):
            if (df.loc[i, 'Low'] < df.loc[i-1, 'Low'] and
                df.loc[i, 'Low'] < df.loc[i-2, 'Low'] and
                df.loc[i, 'Low'] < df.loc[i+1, 'Low'] and
                df.loc[i, 'Low'] < df.loc[i+2, 'Low']):
                swing_lows.append(df.loc[i, 'Low'])

        # Cluster swing highs (liquidity above)
        if len(swing_highs) >= 2:
            swing_highs_sorted = sorted(swing_highs)
            for i in range(len(swing_highs_sorted) - 1):
                diff = abs(swing_highs_sorted[i+1] - swing_highs_sorted[i])
                avg_range = df['High'].subtract(df['Low']).mean()

                if diff < (avg_range * 0.5):  # Close together
                    zones.append({
                        'type': 'SELL_SIDE_LIQUIDITY',
                        'level': (swing_highs_sorted[i] + swing_highs_sorted[i+1]) / 2,
                        'strength': 'high' if diff < (avg_range * 0.2) else 'medium'
                    })

        # Cluster swing lows (liquidity below)
        if len(swing_lows) >= 2:
            swing_lows_sorted = sorted(swing_lows)
            for i in range(len(swing_lows_sorted) - 1):
                diff = abs(swing_lows_sorted[i+1] - swing_lows_sorted[i])
                avg_range = df['High'].subtract(df['Low']).mean()

                if diff < (avg_range * 0.5):
                    zones.append({
                        'type': 'BUY_SIDE_LIQUIDITY',
                        'level': (swing_lows_sorted[i] + swing_lows_sorted[i+1]) / 2,
                        'strength': 'high' if diff < (avg_range * 0.2) else 'medium'
                    })

        return zones

    @staticmethod
    def get_market_structure(candles: pd.DataFrame) -> Dict:
        """
        Determine overall market structure (bullish, bearish, ranging)

        Args:
            candles: DataFrame with OHLC data

        Returns:
            Dict with market structure analysis
        """
        df = candles.tail(50).copy()
        df = df.reset_index(drop=True)  # Reset index to avoid KeyError

        if len(df) < 20:
            return {'structure': 'UNKNOWN', 'confidence': 0}

        # Find recent swing highs and lows
        recent_highs = []
        recent_lows = []

        for i in range(5, len(df) - 5):
            # Swing high
            if all(df.loc[i, 'High'] > df.loc[j, 'High'] for j in range(i-5, i)) and \
               all(df.loc[i, 'High'] > df.loc[j, 'High'] for j in range(i+1, i+6)):
                recent_highs.append((i, df.loc[i, 'High']))

            # Swing low
            if all(df.loc[i, 'Low'] < df.loc[j, 'Low'] for j in range(i-5, i)) and \
               all(df.loc[i, 'Low'] < df.loc[j, 'Low'] for j in range(i+1, i+6)):
                recent_lows.append((i, df.loc[i, 'Low']))

        # Analyze structure
        if len(recent_highs) >= 2 and len(recent_lows) >= 2:
            # Check for higher highs and higher lows (bullish)
            higher_highs = recent_highs[-1][1] > recent_highs[-2][1]
            higher_lows = recent_lows[-1][1] > recent_lows[-2][1]

            # Check for lower highs and lower lows (bearish)
            lower_highs = recent_highs[-1][1] < recent_highs[-2][1]
            lower_lows = recent_lows[-1][1] < recent_lows[-2][1]

            if higher_highs and higher_lows:
                return {
                    'structure': 'BULLISH',
                    'confidence': 85,
                    'last_high': recent_highs[-1][1],
                    'last_low': recent_lows[-1][1],
                    'trend': 'UPTREND'
                }
            elif lower_highs and lower_lows:
                return {
                    'structure': 'BEARISH',
                    'confidence': 85,
                    'last_high': recent_highs[-1][1],
                    'last_low': recent_lows[-1][1],
                    'trend': 'DOWNTREND'
                }
            else:
                return {
                    'structure': 'RANGING',
                    'confidence': 70,
                    'range_high': max([h[1] for h in recent_highs]),
                    'range_low': min([l[1] for l in recent_lows]),
                    'trend': 'SIDEWAYS'
                }

        return {'structure': 'UNKNOWN', 'confidence': 50}

    @staticmethod
    def format_smc_summary(candles: pd.DataFrame) -> str:
        """
        Generate a complete SMC analysis summary

        Args:
            candles: DataFrame with OHLC data

        Returns:
            Formatted string with all SMC indicators
        """
        ifvgs = SMCIndicators.detect_ifvg(candles)
        breakers = SMCIndicators.detect_breaker_blocks(candles)
        order_blocks = SMCIndicators.detect_order_blocks(candles)
        liquidity = SMCIndicators.detect_liquidity_zones(candles)
        structure = SMCIndicators.get_market_structure(candles)

        current_price = candles.iloc[-1]['Close']

        summary = []
        summary.append("=" * 60)
        summary.append("SMART MONEY CONCEPTS (SMC) ANALYSIS")
        summary.append("=" * 60)

        # Market Structure
        summary.append(f"\n📊 MARKET STRUCTURE:")
        summary.append(f"  Structure: {structure['structure']}")
        summary.append(f"  Confidence: {structure.get('confidence', 0)}%")
        summary.append(f"  Trend: {structure.get('trend', 'UNKNOWN')}")

        # IFVGs
        summary.append(f"\n💎 IMBALANCE FAIR VALUE GAPS (IFVGs): {len(ifvgs)}")
        unfilled_ifvgs = [ifvg for ifvg in ifvgs if not ifvg['filled']]
        if unfilled_ifvgs:
            summary.append(f"  Unfilled: {len(unfilled_ifvgs)}")
            for ifvg in unfilled_ifvgs[-3:]:  # Show last 3
                summary.append(f"    • {ifvg['type']} IFVG: {ifvg['bottom']:.5f} - {ifvg['top']:.5f}")
                summary.append(f"      Size: {ifvg['size']:.5f} | Status: {ifvg['current_price_relation']}")

        # Breaker Blocks
        summary.append(f"\n🔨 BREAKER BLOCKS: {len(breakers)}")
        if breakers:
            for breaker in breakers[-3:]:
                summary.append(f"    • {breaker['type']}: {breaker['level']:.5f}")
                summary.append(f"      Strength: {breaker['strength']}")

        # Order Blocks
        summary.append(f"\n📦 ORDER BLOCKS: {len(order_blocks)}")
        if order_blocks:
            for ob in order_blocks[-3:]:
                summary.append(f"    • {ob['type']}: {ob['bottom']:.5f} - {ob['top']:.5f}")
                summary.append(f"      Strength: {ob['strength']}")

        # Liquidity Zones
        summary.append(f"\n💧 LIQUIDITY ZONES: {len(liquidity)}")
        if liquidity:
            for liq in liquidity:
                summary.append(f"    • {liq['type']}: {liq['level']:.5f}")
                summary.append(f"      Strength: {liq['strength']}")

        summary.append("\n" + "=" * 60)

        return "\n".join(summary)


# Quick test
if __name__ == "__main__":
    import pandas as pd
    from datetime import datetime, timedelta

    # Create mock data for testing
    dates = pd.date_range(end=datetime.now(), periods=100, freq='H')
    mock_data = pd.DataFrame({
        'datetime': dates,
        'Open': [1.08 + (i * 0.0001) + (0.0005 * (i % 10 - 5)) for i in range(100)],
        'High': [1.08 + (i * 0.0001) + (0.0008 * (i % 10 - 5)) for i in range(100)],
        'Low': [1.08 + (i * 0.0001) + (0.0003 * (i % 10 - 5)) for i in range(100)],
        'Close': [1.08 + (i * 0.0001) + (0.0006 * (i % 10 - 5)) for i in range(100)],
        'Volume': [100] * 100
    })

    cprint("\n🧪 Testing SMC Indicators...\n", "cyan", attrs=["bold"])

    # Test each indicator
    ifvgs = SMCIndicators.detect_ifvg(mock_data)
    cprint(f"✅ IFVGs detected: {len(ifvgs)}", "green")

    breakers = SMCIndicators.detect_breaker_blocks(mock_data)
    cprint(f"✅ Breaker blocks detected: {len(breakers)}", "green")

    order_blocks = SMCIndicators.detect_order_blocks(mock_data)
    cprint(f"✅ Order blocks detected: {len(order_blocks)}", "green")

    liquidity = SMCIndicators.detect_liquidity_zones(mock_data)
    cprint(f"✅ Liquidity zones detected: {len(liquidity)}", "green")

    structure = SMCIndicators.get_market_structure(mock_data)
    cprint(f"✅ Market structure: {structure['structure']}", "green")

    # Print full summary
    cprint("\n" + SMCIndicators.format_smc_summary(mock_data), "white")

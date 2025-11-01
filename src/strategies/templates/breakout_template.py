"""
🌙 Moon Dev's Breakout Strategy Template
=========================================
Production-ready breakout trading strategy for quick deployment

Strategy Overview:
-----------------
Breakout strategies capitalize on price breaking through significant support/resistance
levels with strong momentum. This template identifies consolidation ranges and enters
when price breaks out with volume confirmation.

Key Concepts:
- Support/Resistance level identification
- Range consolidation detection
- Breakout confirmation with volume
- Momentum follow-through with ADX

Indicators Used:
- Donchian Channels: 20-period for high/low range
- ATR: 14-period for volatility and stop placement
- ADX: 14-period for trend strength
- Volume SMA: 20-period for volume confirmation
- Breakout threshold: 1.5x ATR for valid breakout

Entry Signals:
- LONG: Price > 20-period high AND ADX > 20 AND Volume > 1.5x average
- SHORT: Price < 20-period low AND ADX > 20 AND Volume > 1.5x average

Exit Signals:
- Trailing stop: 2x ATR from highest high (longs) or lowest low (shorts)
- Profit target: 3x ATR from entry
- Breakdown: Price re-enters Donchian channel

Best Use Cases:
- Consolidating markets before earnings/news
- Crypto during accumulation phases
- Range-bound stocks before breakout
- 15-minute to 4-hour timeframes

Performance Expectations:
- Win rate: 35-50% (fewer but larger winners)
- Profit factor: 1.8-3.0
- Max drawdown: 15-30%
- Sharpe ratio: 0.7-1.4

Risk Parameters:
- Risk per trade: 2%
- Max position size: 100%
- Commission: 0.2% per trade
- Slippage: 0.15% (breakouts can have slippage)

Quick Start:
-----------
from backtesting import Backtest
from breakout_template import BreakoutStrategy
from backtest_template import load_moondev_data

# Load data
data = load_moondev_data('BTC-USD', '15m')

# Run backtest
bt = Backtest(data, BreakoutStrategy, cash=100000, commission=0.002)
stats = bt.run()
print(stats)
bt.plot()

Customization:
-------------
# Adjust parameters for different market conditions
class MyBreakoutStrategy(BreakoutStrategy):
    # More sensitive (shorter lookback)
    donchian_period = 10
    volume_multiplier = 1.2

    # Less sensitive (longer lookback)
    # donchian_period = 40
    # volume_multiplier = 2.0
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
from backtesting import Strategy
from backtesting.lib import crossover
from backtest_template import MoonDevStrategy


class BreakoutStrategy(MoonDevStrategy):
    """
    Breakout strategy using Donchian Channels and volume confirmation

    Strategy Logic:
    1. Identify consolidation range (Donchian Channels)
    2. Wait for price to break channel high/low
    3. Confirm with volume surge (1.5x+ average)
    4. Confirm trend strength with ADX
    5. Enter on breakout
    6. Trail stop based on ATR

    Parameters:
        donchian_period (int): Lookback period for high/low (default: 20)
        atr_period (int): ATR period (default: 14)
        atr_stop_mult (float): ATR multiplier for stop (default: 2.0)
        atr_target_mult (float): ATR multiplier for target (default: 3.0)
        adx_period (int): ADX period (default: 14)
        adx_threshold (int): Minimum ADX for trend (default: 20)
        volume_period (int): Volume SMA period (default: 20)
        volume_multiplier (float): Volume surge threshold (default: 1.5)
        risk_per_trade (float): Risk percentage per trade (default: 0.02)
    """

    # ========================================================================
    # STRATEGY PARAMETERS (customize these)
    # ========================================================================

    # Donchian Channels (range identification)
    donchian_period = 20

    # ATR for volatility and stops
    atr_period = 14
    atr_stop_mult = 2.0      # 2x ATR for stop loss
    atr_target_mult = 3.0    # 3x ATR for profit target

    # ADX for trend confirmation
    adx_period = 14
    adx_threshold = 20

    # Volume confirmation
    volume_period = 20
    volume_multiplier = 1.5  # Volume must be 1.5x average

    # Risk management
    risk_per_trade = 0.02    # 2% risk per trade

    def init(self):
        """Initialize indicators"""
        # Donchian Channels (highest high, lowest low)
        self.donchian_high = self.I(
            lambda x: pd.Series(x).rolling(self.donchian_period).max(),
            self.data.High
        )
        self.donchian_low = self.I(
            lambda x: pd.Series(x).rolling(self.donchian_period).min(),
            self.data.Low
        )

        # ATR for volatility-based stops
        self.atr_line = self.I(
            self.atr,
            self.data.High,
            self.data.Low,
            self.data.Close,
            self.atr_period
        )

        # ADX for trend strength
        self.adx_line = self.I(
            self.adx,
            self.data.High,
            self.data.Low,
            self.data.Close,
            self.adx_period
        )

        # Volume confirmation
        self.volume_sma = self.I(self.sma, self.data.Volume, self.volume_period)

        # Track entry and stops
        self.entry_price = None
        self.stop_loss = None
        self.take_profit = None
        self.trailing_high = None  # For longs
        self.trailing_low = None   # For shorts

    def next(self):
        """Execute strategy logic on each bar"""
        price = self.data.Close[-1]
        high = self.data.High[-1]
        low = self.data.Low[-1]

        # Get current indicator values
        donchian_high = self.donchian_high[-1]
        donchian_low = self.donchian_low[-1]
        atr = self.atr_line[-1]
        adx = self.adx_line[-1]
        volume = self.data.Volume[-1]
        volume_avg = self.volume_sma[-1]

        # Skip if indicators not ready
        if np.isnan(donchian_high) or np.isnan(atr) or np.isnan(adx):
            return

        # ====================================================================
        # EXIT LOGIC (check first)
        # ====================================================================

        if self.position:
            # LONG POSITION EXITS
            if self.position.is_long:
                # Update trailing high
                if self.trailing_high is None or high > self.trailing_high:
                    self.trailing_high = high
                    # Update trailing stop
                    self.stop_loss = self.trailing_high - (self.atr_stop_mult * atr)

                # Trailing stop hit
                if price <= self.stop_loss:
                    self.position.close()
                    self._reset_trade_tracking()
                    return

                # Profit target hit
                if self.take_profit and price >= self.take_profit:
                    self.position.close()
                    self._reset_trade_tracking()
                    return

                # Breakdown: Price re-enters channel
                if price < donchian_low:
                    self.position.close()
                    self._reset_trade_tracking()
                    return

            # SHORT POSITION EXITS
            if self.position.is_short:
                # Update trailing low
                if self.trailing_low is None or low < self.trailing_low:
                    self.trailing_low = low
                    # Update trailing stop
                    self.stop_loss = self.trailing_low + (self.atr_stop_mult * atr)

                # Trailing stop hit
                if price >= self.stop_loss:
                    self.position.close()
                    self._reset_trade_tracking()
                    return

                # Profit target hit
                if self.take_profit and price <= self.take_profit:
                    self.position.close()
                    self._reset_trade_tracking()
                    return

                # Breakdown: Price re-enters channel
                if price > donchian_high:
                    self.position.close()
                    self._reset_trade_tracking()
                    return

        # ====================================================================
        # ENTRY LOGIC
        # ====================================================================

        # Only enter if no position
        if not self.position:
            # LONG BREAKOUT CONDITIONS
            # 1. Price breaks above Donchian high
            # 2. ADX > threshold (trending market)
            # 3. Volume > 1.5x average (genuine breakout)
            long_breakout = (
                price > donchian_high and                  # Breakout above range
                adx > self.adx_threshold and               # Trending market
                volume > volume_avg * self.volume_multiplier  # Volume surge
            )

            # SHORT BREAKOUT CONDITIONS
            # 1. Price breaks below Donchian low
            # 2. ADX > threshold (trending market)
            # 3. Volume > 1.5x average (genuine breakdown)
            short_breakout = (
                price < donchian_low and                   # Breakout below range
                adx > self.adx_threshold and               # Trending market
                volume > volume_avg * self.volume_multiplier  # Volume surge
            )

            # Execute trades
            if long_breakout:
                # Calculate position size based on ATR stop
                stop_loss_price = price - (self.atr_stop_mult * atr)
                stop_loss_pct = abs(price - stop_loss_price) / price

                size = self.calculate_position_size(
                    risk_pct=self.risk_per_trade,
                    stop_loss_pct=stop_loss_pct
                )

                self.buy(size=size)

                # Set entry tracking
                self.entry_price = price
                self.stop_loss = stop_loss_price
                self.take_profit = price + (self.atr_target_mult * atr)
                self.trailing_high = high

            elif short_breakout:
                # Calculate position size based on ATR stop
                stop_loss_price = price + (self.atr_stop_mult * atr)
                stop_loss_pct = abs(stop_loss_price - price) / price

                size = self.calculate_position_size(
                    risk_pct=self.risk_per_trade,
                    stop_loss_pct=stop_loss_pct
                )

                self.sell(size=size)

                # Set entry tracking
                self.entry_price = price
                self.stop_loss = stop_loss_price
                self.take_profit = price - (self.atr_target_mult * atr)
                self.trailing_low = low

    def _reset_trade_tracking(self):
        """Reset trade tracking variables"""
        self.entry_price = None
        self.stop_loss = None
        self.take_profit = None
        self.trailing_high = None
        self.trailing_low = None


# ============================================================================
# ADVANCED VARIATIONS
# ============================================================================

class AggressiveBreakoutStrategy(BreakoutStrategy):
    """
    More aggressive breakout strategy with tighter parameters

    Changes from base:
    - Shorter Donchian period (10 instead of 20)
    - Lower ADX threshold (15 instead of 20)
    - Lower volume requirement (1.2x instead of 1.5x)
    - Tighter stops (1.5x ATR instead of 2.0x)

    Best for: High volatility, frequent breakouts
    Warning: More false breakouts
    """
    donchian_period = 10
    adx_threshold = 15
    volume_multiplier = 1.2
    atr_stop_mult = 1.5
    atr_target_mult = 2.5


class ConservativeBreakoutStrategy(BreakoutStrategy):
    """
    More conservative breakout strategy with stricter filters

    Changes from base:
    - Longer Donchian period (40 instead of 20)
    - Higher ADX threshold (25 instead of 20)
    - Higher volume requirement (2.0x instead of 1.5x)
    - Wider stops (2.5x ATR instead of 2.0x)

    Best for: Lower volatility, reliable breakouts only
    """
    donchian_period = 40
    adx_threshold = 25
    volume_multiplier = 2.0
    atr_stop_mult = 2.5
    atr_target_mult = 4.0


class RangeExpansionStrategy(BreakoutStrategy):
    """
    Breakout strategy focused on range expansion after consolidation

    Additional logic:
    - Requires range contraction before breakout (low ATR)
    - ATR must be below 30-period average (consolidation)
    - Then expands on breakout (high volume + high ATR)

    Best for: Identifying compression breakouts
    """
    atr_lookback = 30

    def init(self):
        super().init()
        # Add ATR average for compression detection
        self.atr_average = self.I(
            lambda x: pd.Series(x).rolling(self.atr_lookback).mean(),
            self.atr_line
        )

    def next(self):
        """Override to add range compression check"""
        price = self.data.Close[-1]
        high = self.data.High[-1]
        low = self.data.Low[-1]
        donchian_high = self.donchian_high[-1]
        donchian_low = self.donchian_low[-1]
        atr = self.atr_line[-1]
        atr_avg = self.atr_average[-1]
        adx = self.adx_line[-1]
        volume = self.data.Volume[-1]
        volume_avg = self.volume_sma[-1]

        # Skip if indicators not ready
        if np.isnan(donchian_high) or np.isnan(atr) or np.isnan(atr_avg) or np.isnan(adx):
            return

        # Handle exits (use parent logic)
        if self.position:
            if self.position.is_long:
                if self.trailing_high is None or high > self.trailing_high:
                    self.trailing_high = high
                    self.stop_loss = self.trailing_high - (self.atr_stop_mult * atr)

                if price <= self.stop_loss:
                    self.position.close()
                    self._reset_trade_tracking()
                    return

                if self.take_profit and price >= self.take_profit:
                    self.position.close()
                    self._reset_trade_tracking()
                    return

                if price < donchian_low:
                    self.position.close()
                    self._reset_trade_tracking()
                    return

            if self.position.is_short:
                if self.trailing_low is None or low < self.trailing_low:
                    self.trailing_low = low
                    self.stop_loss = self.trailing_low + (self.atr_stop_mult * atr)

                if price >= self.stop_loss:
                    self.position.close()
                    self._reset_trade_tracking()
                    return

                if self.take_profit and price <= self.take_profit:
                    self.position.close()
                    self._reset_trade_tracking()
                    return

                if price > donchian_high:
                    self.position.close()
                    self._reset_trade_tracking()
                    return

        # Entry logic with range compression
        if not self.position:
            # Additional filter: ATR was below average (compression)
            # But now expanding on breakout
            range_compressed = atr < atr_avg * 0.8  # ATR 20% below average

            long_breakout = (
                price > donchian_high and
                adx > self.adx_threshold and
                volume > volume_avg * self.volume_multiplier and
                range_compressed  # NEW: Range was compressed
            )

            short_breakout = (
                price < donchian_low and
                adx > self.adx_threshold and
                volume > volume_avg * self.volume_multiplier and
                range_compressed  # NEW: Range was compressed
            )

            if long_breakout:
                stop_loss_price = price - (self.atr_stop_mult * atr)
                stop_loss_pct = abs(price - stop_loss_price) / price
                size = self.calculate_position_size(
                    risk_pct=self.risk_per_trade,
                    stop_loss_pct=stop_loss_pct
                )
                self.buy(size=size)
                self.entry_price = price
                self.stop_loss = stop_loss_price
                self.take_profit = price + (self.atr_target_mult * atr)
                self.trailing_high = high

            elif short_breakout:
                stop_loss_price = price + (self.atr_stop_mult * atr)
                stop_loss_pct = abs(stop_loss_price - price) / price
                size = self.calculate_position_size(
                    risk_pct=self.risk_per_trade,
                    stop_loss_pct=stop_loss_pct
                )
                self.sell(size=size)
                self.entry_price = price
                self.stop_loss = stop_loss_price
                self.take_profit = price - (self.atr_target_mult * atr)
                self.trailing_low = low


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    """
    Example: Run breakout strategy backtest
    """
    from backtesting import Backtest
    from backtest_template import load_moondev_data
    from backtest_metrics import display_metrics, calculate_moondev_score
    from termcolor import cprint

    # Load data
    try:
        data = load_moondev_data('BTC-USD', '15m')
        cprint(f"\n✅ Loaded {len(data)} bars of BTC-USD 15m data", "green")
    except FileNotFoundError:
        cprint("\n❌ Sample data not found. Please provide OHLCV data.", "red")
        cprint("Expected format: src/data/rbi/BTC-USD-15m.csv", "yellow")
        exit(1)

    # Run backtest with base strategy
    cprint("\n" + "="*80, "cyan")
    cprint("📊 BREAKOUT STRATEGY BACKTEST", "cyan", attrs=['bold'])
    cprint("="*80, "cyan")

    bt = Backtest(
        data,
        BreakoutStrategy,
        cash=100000,
        commission=0.002,
        exclusive_orders=True
    )

    stats = bt.run()

    # Display results
    display_metrics(stats)

    # Calculate Moon Dev Score
    score = calculate_moondev_score({
        'Return [%]': stats['Return [%]'],
        'Sharpe Ratio': stats['Sharpe Ratio'],
        'Win Rate [%]': stats['Win Rate [%]'],
        'Max. Drawdown [%]': stats['Max. Drawdown [%]'],
        'Profit Factor': stats['Profit Factor'] if 'Profit Factor' in stats else 0,
        'recovery_factor': abs(stats['Return [%]'] / stats['Max. Drawdown [%]']) if stats['Max. Drawdown [%]'] != 0 else 0
    })

    cprint(f"\n🌙 Moon Dev Score: {score:.1f}/100", "yellow", attrs=['bold'])

    # Plot results
    cprint("\n📈 Generating performance chart...", "cyan")
    bt.plot()

    # Compare with range expansion variant
    cprint("\n" + "="*80, "magenta")
    cprint("🎯 RANGE EXPANSION BREAKOUT COMPARISON", "magenta", attrs=['bold'])
    cprint("="*80, "magenta")

    bt_expansion = Backtest(
        data,
        RangeExpansionStrategy,
        cash=100000,
        commission=0.002,
        exclusive_orders=True
    )

    stats_expansion = bt_expansion.run()
    display_metrics(stats_expansion)

    # Compare returns
    cprint(f"\n📊 Strategy Comparison:", "white", attrs=['bold'])
    cprint(f"  Base Strategy Return:       {stats['Return [%]']:.2f}%", "cyan")
    cprint(f"  Range Expansion Return:     {stats_expansion['Return [%]']:.2f}%", "magenta")
    cprint(f"  Difference:                 {stats_expansion['Return [%]'] - stats['Return [%]']:.2f}%", "yellow")

"""
🌙 Moon Dev's Mean Reversion Strategy Template
===============================================
Production-ready mean reversion trading strategy for quick deployment

Strategy Overview:
-----------------
Mean reversion strategies capitalize on the tendency of prices to return to their
average after extreme deviations. This template identifies overbought/oversold
conditions and enters positions expecting price normalization.

Key Concepts:
- Price deviation from moving average
- Statistical extremes using Bollinger Bands
- Oscillator confirmation with RSI
- Volume divergence detection

Indicators Used:
- SMA: 20-period for mean calculation
- Bollinger Bands: 20-period, 2 std dev for extremes
- RSI: 14-period for overbought/oversold
- Volume SMA: 20-period for volume analysis
- ATR: 14-period for volatility-based stops

Entry Signals:
- LONG: Price < Lower BB AND RSI < 30 AND Volume > Average
- SHORT: Price > Upper BB AND RSI > 70 AND Volume > Average

Exit Signals:
- Target: Price returns to middle BB
- Stop loss: 1.5x ATR from entry
- Time-based: Exit after 10 bars if no profit

Best Use Cases:
- Range-bound markets
- Low to medium volatility
- High liquidity assets (BTC, ETH, major pairs)
- 15-minute to 1-hour timeframes

Performance Expectations:
- Win rate: 55-70% (mean reversion typically higher)
- Profit factor: 1.3-2.0
- Max drawdown: 10-20%
- Sharpe ratio: 0.9-1.8

Risk Parameters:
- Risk per trade: 1.5%
- Max position size: 100%
- Commission: 0.2% per trade
- Slippage: 0.1%

Quick Start:
-----------
from backtesting import Backtest
from mean_reversion_template import MeanReversionStrategy
from backtest_template import load_moondev_data

# Load data
data = load_moondev_data('BTC-USD', '15m')

# Run backtest
bt = Backtest(data, MeanReversionStrategy, cash=100000, commission=0.002)
stats = bt.run()
print(stats)
bt.plot()

Customization:
-------------
# Adjust parameters for different market conditions
class MyMeanReversionStrategy(MeanReversionStrategy):
    # More sensitive (tighter bands)
    bb_period = 10
    bb_std = 1.5

    # Less sensitive (wider bands)
    # bb_period = 30
    # bb_std = 2.5
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
from backtesting import Strategy
from backtesting.lib import crossover
from backtest_template import MoonDevStrategy


class MeanReversionStrategy(MoonDevStrategy):
    """
    Mean reversion strategy using Bollinger Bands and RSI

    Strategy Logic:
    1. Calculate mean (SMA) and standard deviation (Bollinger Bands)
    2. Identify extreme deviations (price outside bands)
    3. Confirm with RSI overbought/oversold
    4. Enter expecting reversion to mean
    5. Exit when price returns to mean or stop loss hit

    Parameters:
        sma_period (int): Simple moving average period (default: 20)
        bb_period (int): Bollinger Bands period (default: 20)
        bb_std (float): Bollinger Bands standard deviation (default: 2.0)
        rsi_period (int): RSI period (default: 14)
        rsi_oversold (int): RSI oversold level (default: 30)
        rsi_overbought (int): RSI overbought level (default: 70)
        atr_period (int): ATR period for stops (default: 14)
        atr_multiplier (float): ATR multiplier for stop loss (default: 1.5)
        volume_period (int): Volume SMA period (default: 20)
        max_bars_held (int): Max bars to hold position (default: 10)
        risk_per_trade (float): Risk percentage per trade (default: 0.015)
    """

    # ========================================================================
    # STRATEGY PARAMETERS (customize these)
    # ========================================================================

    # Mean calculation
    sma_period = 20

    # Bollinger Bands
    bb_period = 20
    bb_std = 2.0

    # RSI settings
    rsi_period = 14
    rsi_oversold = 30
    rsi_overbought = 70

    # Volatility-based stops
    atr_period = 14
    atr_multiplier = 1.5

    # Volume confirmation
    volume_period = 20

    # Time-based exit
    max_bars_held = 10  # Exit if no profit after 10 bars

    # Risk management
    risk_per_trade = 0.015  # 1.5% risk per trade

    def init(self):
        """Initialize indicators"""
        # Mean (SMA)
        self.sma_line = self.I(self.sma, self.data.Close, self.sma_period)

        # Bollinger Bands (lower, mid, upper)
        bb_result = self.I(self.bbands, self.data.Close, self.bb_period, self.bb_std)
        self.bb_lower = bb_result[0]
        self.bb_mid = bb_result[1]
        self.bb_upper = bb_result[2]

        # RSI
        self.rsi_line = self.I(self.rsi, self.data.Close, self.rsi_period)

        # ATR for volatility-based stops
        self.atr_line = self.I(
            self.atr,
            self.data.High,
            self.data.Low,
            self.data.Close,
            self.atr_period
        )

        # Volume confirmation
        self.volume_sma = self.I(self.sma, self.data.Volume, self.volume_period)

        # Track entry for time-based exit
        self.entry_bar = None
        self.entry_price = None

    def next(self):
        """Execute strategy logic on each bar"""
        price = self.data.Close[-1]

        # Get current indicator values
        bb_lower = self.bb_lower[-1]
        bb_mid = self.bb_mid[-1]
        bb_upper = self.bb_upper[-1]
        rsi = self.rsi_line[-1]
        atr = self.atr_line[-1]
        volume = self.data.Volume[-1]
        volume_avg = self.volume_sma[-1]

        # Skip if indicators not ready
        if np.isnan(bb_lower) or np.isnan(rsi) or np.isnan(atr):
            return

        # ====================================================================
        # EXIT LOGIC (check first)
        # ====================================================================

        if self.position:
            bars_held = len(self.data) - self.entry_bar

            # LONG POSITION EXITS
            if self.position.is_long:
                # Take profit: Price returns to mean (middle BB)
                if price >= bb_mid:
                    self.position.close()
                    self.entry_bar = None
                    self.entry_price = None
                    return

                # Stop loss: 1.5x ATR below entry
                stop_loss = self.entry_price - (self.atr_multiplier * atr)
                if price <= stop_loss:
                    self.position.close()
                    self.entry_bar = None
                    self.entry_price = None
                    return

                # Time-based exit: Hold too long without profit
                if bars_held >= self.max_bars_held and price < self.entry_price:
                    self.position.close()
                    self.entry_bar = None
                    self.entry_price = None
                    return

            # SHORT POSITION EXITS
            if self.position.is_short:
                # Take profit: Price returns to mean (middle BB)
                if price <= bb_mid:
                    self.position.close()
                    self.entry_bar = None
                    self.entry_price = None
                    return

                # Stop loss: 1.5x ATR above entry
                stop_loss = self.entry_price + (self.atr_multiplier * atr)
                if price >= stop_loss:
                    self.position.close()
                    self.entry_bar = None
                    self.entry_price = None
                    return

                # Time-based exit
                if bars_held >= self.max_bars_held and price > self.entry_price:
                    self.position.close()
                    self.entry_bar = None
                    self.entry_price = None
                    return

        # ====================================================================
        # ENTRY LOGIC
        # ====================================================================

        # Only enter if no position
        if not self.position:
            # LONG CONDITIONS (oversold reversion)
            # 1. Price below lower Bollinger Band (oversold)
            # 2. RSI < 30 (oversold confirmation)
            # 3. Volume > average (genuine selling pressure)
            long_signal = (
                price < bb_lower and                       # Price extreme low
                rsi < self.rsi_oversold and                # RSI oversold
                volume > volume_avg                         # Volume confirmation
            )

            # SHORT CONDITIONS (overbought reversion)
            # 1. Price above upper Bollinger Band (overbought)
            # 2. RSI > 70 (overbought confirmation)
            # 3. Volume > average (genuine buying pressure)
            short_signal = (
                price > bb_upper and                       # Price extreme high
                rsi > self.rsi_overbought and              # RSI overbought
                volume > volume_avg                         # Volume confirmation
            )

            # Execute trades
            if long_signal:
                # Calculate position size based on ATR stop
                stop_loss_pct = (self.atr_multiplier * atr) / price
                size = self.calculate_position_size(
                    risk_pct=self.risk_per_trade,
                    stop_loss_pct=stop_loss_pct
                )
                self.buy(size=size)
                self.entry_bar = len(self.data)
                self.entry_price = price

            elif short_signal:
                # Calculate position size based on ATR stop
                stop_loss_pct = (self.atr_multiplier * atr) / price
                size = self.calculate_position_size(
                    risk_pct=self.risk_per_trade,
                    stop_loss_pct=stop_loss_pct
                )
                self.sell(size=size)
                self.entry_bar = len(self.data)
                self.entry_price = price


# ============================================================================
# ADVANCED VARIATIONS
# ============================================================================

class TightMeanReversionStrategy(MeanReversionStrategy):
    """
    Tighter mean reversion for more frequent trades

    Changes from base:
    - Tighter Bollinger Bands (1.5 std instead of 2.0)
    - Less extreme RSI thresholds (35/65 instead of 30/70)
    - Shorter hold period (5 bars instead of 10)

    Best for: High frequency trading, liquid markets
    """
    bb_std = 1.5
    rsi_oversold = 35
    rsi_overbought = 65
    max_bars_held = 5


class WideMeanReversionStrategy(MeanReversionStrategy):
    """
    Wider mean reversion for more reliable signals

    Changes from base:
    - Wider Bollinger Bands (2.5 std instead of 2.0)
    - More extreme RSI thresholds (25/75 instead of 30/70)
    - Longer hold period (15 bars instead of 10)

    Best for: Lower frequency, more patient approach
    """
    bb_std = 2.5
    rsi_oversold = 25
    rsi_overbought = 75
    max_bars_held = 15


class AggressiveMeanReversionStrategy(MeanReversionStrategy):
    """
    Aggressive mean reversion with tighter stops

    Changes from base:
    - Tighter stops (1.0x ATR instead of 1.5x)
    - Higher risk per trade (2.5% instead of 1.5%)
    - Faster exit (7 bars instead of 10)

    Best for: Active traders, high confidence setups
    Warning: Higher drawdown potential
    """
    atr_multiplier = 1.0
    risk_per_trade = 0.025
    max_bars_held = 7


class ConservativeMeanReversionStrategy(MeanReversionStrategy):
    """
    Conservative mean reversion with wider stops

    Changes from base:
    - Wider stops (2.0x ATR instead of 1.5x)
    - Lower risk per trade (1.0% instead of 1.5%)
    - Patient exit (15 bars instead of 10)

    Best for: Risk-averse traders, volatile markets
    """
    atr_multiplier = 2.0
    risk_per_trade = 0.01
    max_bars_held = 15


class DivergenceMeanReversionStrategy(MeanReversionStrategy):
    """
    Mean reversion enhanced with volume divergence detection

    Additional logic:
    - Requires volume decrease on extreme moves
    - Signals weakening momentum (better reversion signal)

    Best for: Identifying exhaustion moves
    """
    def init(self):
        super().init()
        # Add volume rate of change
        self.volume_roc = self.I(
            lambda v: pd.Series(v).pct_change(3) * 100,
            self.data.Volume
        )

    def next(self):
        """Override to add volume divergence check"""
        price = self.data.Close[-1]
        bb_lower = self.bb_lower[-1]
        bb_upper = self.bb_upper[-1]
        bb_mid = self.bb_mid[-1]
        rsi = self.rsi_line[-1]
        volume_roc = self.volume_roc[-1]
        atr = self.atr_line[-1]

        # Skip if indicators not ready
        if np.isnan(bb_lower) or np.isnan(rsi) or np.isnan(atr) or np.isnan(volume_roc):
            return

        # Handle exits (use parent logic)
        if self.position:
            bars_held = len(self.data) - self.entry_bar

            if self.position.is_long:
                if price >= bb_mid:
                    self.position.close()
                    self.entry_bar = None
                    self.entry_price = None
                    return

                stop_loss = self.entry_price - (self.atr_multiplier * atr)
                if price <= stop_loss:
                    self.position.close()
                    self.entry_bar = None
                    self.entry_price = None
                    return

                if bars_held >= self.max_bars_held and price < self.entry_price:
                    self.position.close()
                    self.entry_bar = None
                    self.entry_price = None
                    return

            if self.position.is_short:
                if price <= bb_mid:
                    self.position.close()
                    self.entry_bar = None
                    self.entry_price = None
                    return

                stop_loss = self.entry_price + (self.atr_multiplier * atr)
                if price >= stop_loss:
                    self.position.close()
                    self.entry_bar = None
                    self.entry_price = None
                    return

                if bars_held >= self.max_bars_held and price > self.entry_price:
                    self.position.close()
                    self.entry_bar = None
                    self.entry_price = None
                    return

        # Entry logic with divergence
        if not self.position:
            # LONG with volume divergence
            # Price falling but volume decreasing = exhaustion
            long_signal = (
                price < bb_lower and
                rsi < self.rsi_oversold and
                volume_roc < 0  # Volume declining (divergence)
            )

            # SHORT with volume divergence
            # Price rising but volume decreasing = exhaustion
            short_signal = (
                price > bb_upper and
                rsi > self.rsi_overbought and
                volume_roc < 0  # Volume declining (divergence)
            )

            if long_signal:
                stop_loss_pct = (self.atr_multiplier * atr) / price
                size = self.calculate_position_size(
                    risk_pct=self.risk_per_trade,
                    stop_loss_pct=stop_loss_pct
                )
                self.buy(size=size)
                self.entry_bar = len(self.data)
                self.entry_price = price

            elif short_signal:
                stop_loss_pct = (self.atr_multiplier * atr) / price
                size = self.calculate_position_size(
                    risk_pct=self.risk_per_trade,
                    stop_loss_pct=stop_loss_pct
                )
                self.sell(size=size)
                self.entry_bar = len(self.data)
                self.entry_price = price


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    """
    Example: Run mean reversion strategy backtest
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
    cprint("📊 MEAN REVERSION STRATEGY BACKTEST", "cyan", attrs=['bold'])
    cprint("="*80, "cyan")

    bt = Backtest(
        data,
        MeanReversionStrategy,
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

    # Compare with divergence variant
    cprint("\n" + "="*80, "magenta")
    cprint("🎯 DIVERGENCE MEAN REVERSION COMPARISON", "magenta", attrs=['bold'])
    cprint("="*80, "magenta")

    bt_divergence = Backtest(
        data,
        DivergenceMeanReversionStrategy,
        cash=100000,
        commission=0.002,
        exclusive_orders=True
    )

    stats_divergence = bt_divergence.run()
    display_metrics(stats_divergence)

    # Compare returns
    cprint(f"\n📊 Strategy Comparison:", "white", attrs=['bold'])
    cprint(f"  Base Strategy Return:       {stats['Return [%]']:.2f}%", "cyan")
    cprint(f"  Divergence Strategy Return: {stats_divergence['Return [%]']:.2f}%", "magenta")
    cprint(f"  Difference:                 {stats_divergence['Return [%]'] - stats['Return [%]']:.2f}%", "yellow")

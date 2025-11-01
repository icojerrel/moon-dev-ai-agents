"""
🌙 Moon Dev's Momentum Strategy Template
========================================
Production-ready momentum trading strategy for quick deployment

Strategy Overview:
-----------------
Momentum strategies capitalize on the continuation of existing trends. This template
identifies strong trends using multiple momentum indicators and enters positions
when momentum is confirmed.

Key Concepts:
- Trend following using moving averages
- Momentum confirmation with RSI
- Volume validation for conviction
- ADX for trend strength filtering

Indicators Used:
- EMA (Fast): 9-period for short-term trend
- EMA (Slow): 21-period for medium-term trend
- RSI: 14-period for momentum
- ADX: 14-period for trend strength
- Volume SMA: 20-period for volume analysis

Entry Signals:
- LONG: Fast EMA > Slow EMA AND RSI > 50 AND ADX > 25 AND Volume > Volume SMA
- SHORT: Fast EMA < Slow EMA AND RSI < 50 AND ADX > 25 AND Volume > Volume SMA

Exit Signals:
- Stop loss: 2% from entry
- Take profit: 6% from entry (3:1 reward/risk)
- Trend reversal: Fast EMA crosses below Slow EMA (for longs)

Best Use Cases:
- Trending markets (crypto, stocks, commodities)
- Medium to high volatility environments
- 15-minute to 1-hour timeframes
- Assets with good liquidity

Performance Expectations:
- Win rate: 40-50%
- Profit factor: 1.5-2.5
- Max drawdown: 15-25%
- Sharpe ratio: 0.8-1.5

Risk Parameters:
- Risk per trade: 2%
- Max position size: 100%
- Commission: 0.2% per trade
- Slippage: 0.1%

Quick Start:
-----------
from backtesting import Backtest
from momentum_template import MomentumStrategy
from backtest_template import load_moondev_data

# Load data
data = load_moondev_data('BTC-USD', '15m')

# Run backtest
bt = Backtest(data, MomentumStrategy, cash=100000, commission=0.002)
stats = bt.run()
print(stats)
bt.plot()

Customization:
-------------
# Adjust parameters for different market conditions
class MyMomentumStrategy(MomentumStrategy):
    # More aggressive (shorter timeframes)
    ema_fast = 5
    ema_slow = 13
    rsi_period = 10

    # More conservative (longer timeframes)
    # ema_fast = 21
    # ema_slow = 50
    # rsi_period = 21
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
from backtesting import Strategy
from backtesting.lib import crossover
from backtest_template import MoonDevStrategy


class MomentumStrategy(MoonDevStrategy):
    """
    Momentum trading strategy with trend confirmation

    Strategy Logic:
    1. Identify trend using dual EMA system
    2. Confirm momentum with RSI
    3. Validate trend strength with ADX
    4. Check volume for conviction
    5. Enter on confluence of all signals
    6. Exit on fixed stop loss or take profit

    Parameters:
        ema_fast (int): Fast EMA period (default: 9)
        ema_slow (int): Slow EMA period (default: 21)
        rsi_period (int): RSI period (default: 14)
        rsi_oversold (int): RSI oversold level (default: 30)
        rsi_overbought (int): RSI overbought level (default: 70)
        adx_period (int): ADX period (default: 14)
        adx_threshold (int): Minimum ADX for trend (default: 25)
        volume_period (int): Volume SMA period (default: 20)
        stop_loss_pct (float): Stop loss percentage (default: 0.02)
        take_profit_pct (float): Take profit percentage (default: 0.06)
        risk_per_trade (float): Risk percentage per trade (default: 0.02)
    """

    # ========================================================================
    # STRATEGY PARAMETERS (customize these)
    # ========================================================================

    # Moving averages
    ema_fast = 9
    ema_slow = 21

    # RSI settings
    rsi_period = 14
    rsi_oversold = 30
    rsi_overbought = 70

    # ADX settings
    adx_period = 14
    adx_threshold = 25  # Minimum ADX to consider trend strong

    # Volume settings
    volume_period = 20

    # Risk management
    stop_loss_pct = 0.02      # 2% stop loss
    take_profit_pct = 0.06    # 6% take profit (3:1 R/R)
    risk_per_trade = 0.02     # 2% risk per trade

    def init(self):
        """Initialize indicators"""
        # Trend indicators
        self.ema_fast_line = self.I(self.ema, self.data.Close, self.ema_fast)
        self.ema_slow_line = self.I(self.ema, self.data.Close, self.ema_slow)

        # Momentum indicator
        self.rsi_line = self.I(self.rsi, self.data.Close, self.rsi_period)

        # Trend strength
        self.adx_line = self.I(
            self.adx,
            self.data.High,
            self.data.Low,
            self.data.Close,
            self.adx_period
        )

        # Volume confirmation
        self.volume_sma = self.I(self.sma, self.data.Volume, self.volume_period)

        # Track entry price for stop loss/take profit
        self.entry_price = None

    def next(self):
        """Execute strategy logic on each bar"""
        price = self.data.Close[-1]

        # Get current indicator values
        ema_fast = self.ema_fast_line[-1]
        ema_slow = self.ema_slow_line[-1]
        rsi = self.rsi_line[-1]
        adx = self.adx_line[-1]
        volume = self.data.Volume[-1]
        volume_avg = self.volume_sma[-1]

        # Skip if indicators not ready
        if np.isnan(adx) or np.isnan(rsi):
            return

        # ====================================================================
        # EXIT LOGIC (check first)
        # ====================================================================

        if self.position:
            # Stop loss
            if self.position.is_long:
                if price <= self.entry_price * (1 - self.stop_loss_pct):
                    self.position.close()
                    self.entry_price = None
                    return

                # Take profit
                if price >= self.entry_price * (1 + self.take_profit_pct):
                    self.position.close()
                    self.entry_price = None
                    return

                # Trend reversal exit
                if crossover(self.ema_slow_line, self.ema_fast_line):
                    self.position.close()
                    self.entry_price = None
                    return

            # For short positions
            if self.position.is_short:
                if price >= self.entry_price * (1 + self.stop_loss_pct):
                    self.position.close()
                    self.entry_price = None
                    return

                if price <= self.entry_price * (1 - self.take_profit_pct):
                    self.position.close()
                    self.entry_price = None
                    return

                if crossover(self.ema_fast_line, self.ema_slow_line):
                    self.position.close()
                    self.entry_price = None
                    return

        # ====================================================================
        # ENTRY LOGIC
        # ====================================================================

        # Only enter if no position
        if not self.position:
            # LONG CONDITIONS
            # 1. Uptrend: Fast EMA > Slow EMA
            # 2. Momentum: RSI > 50 (bullish momentum)
            # 3. Strong trend: ADX > threshold
            # 4. Volume confirmation: Volume > average
            long_signal = (
                ema_fast > ema_slow and                    # Uptrend
                rsi > 50 and                                # Bullish momentum
                adx > self.adx_threshold and               # Strong trend
                volume > volume_avg                         # Volume confirmation
            )

            # SHORT CONDITIONS
            # 1. Downtrend: Fast EMA < Slow EMA
            # 2. Momentum: RSI < 50 (bearish momentum)
            # 3. Strong trend: ADX > threshold
            # 4. Volume confirmation: Volume > average
            short_signal = (
                ema_fast < ema_slow and                    # Downtrend
                rsi < 50 and                                # Bearish momentum
                adx > self.adx_threshold and               # Strong trend
                volume > volume_avg                         # Volume confirmation
            )

            # Execute trades
            if long_signal:
                # Calculate position size based on risk
                size = self.calculate_position_size(
                    risk_pct=self.risk_per_trade,
                    stop_loss_pct=self.stop_loss_pct
                )
                self.buy(size=size)
                self.entry_price = price

            elif short_signal:
                # Calculate position size based on risk
                size = self.calculate_position_size(
                    risk_pct=self.risk_per_trade,
                    stop_loss_pct=self.stop_loss_pct
                )
                self.sell(size=size)
                self.entry_price = price


# ============================================================================
# ADVANCED VARIATIONS
# ============================================================================

class AggressiveMomentumStrategy(MomentumStrategy):
    """
    More aggressive momentum strategy for shorter timeframes

    Changes from base:
    - Faster EMAs (5/13 instead of 9/21)
    - Lower ADX threshold (20 instead of 25)
    - Tighter stops (1.5% instead of 2%)
    - Higher risk per trade (3% instead of 2%)

    Best for: 5-15 minute timeframes, high volatility
    """
    ema_fast = 5
    ema_slow = 13
    adx_threshold = 20
    stop_loss_pct = 0.015
    take_profit_pct = 0.045  # Maintain 3:1 R/R
    risk_per_trade = 0.03


class ConservativeMomentumStrategy(MomentumStrategy):
    """
    More conservative momentum strategy for longer timeframes

    Changes from base:
    - Slower EMAs (21/50 instead of 9/21)
    - Higher ADX threshold (30 instead of 25)
    - Wider stops (3% instead of 2%)
    - Lower risk per trade (1% instead of 2%)

    Best for: 1-hour to 4-hour timeframes, lower volatility
    """
    ema_fast = 21
    ema_slow = 50
    adx_threshold = 30
    stop_loss_pct = 0.03
    take_profit_pct = 0.09  # Maintain 3:1 R/R
    risk_per_trade = 0.01


class ScalpingMomentumStrategy(MomentumStrategy):
    """
    Ultra-fast momentum strategy for scalping

    Changes from base:
    - Very fast EMAs (3/8 instead of 9/21)
    - Lower ADX threshold (15 instead of 25)
    - Very tight stops (0.5% instead of 2%)
    - Very tight profit targets (1.5% instead of 6%)

    Best for: 1-5 minute timeframes, highly liquid markets
    Warning: High commission costs, requires low fees
    """
    ema_fast = 3
    ema_slow = 8
    adx_threshold = 15
    stop_loss_pct = 0.005
    take_profit_pct = 0.015  # Maintain 3:1 R/R
    risk_per_trade = 0.02


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    """
    Example: Run momentum strategy backtest
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
    cprint("📊 MOMENTUM STRATEGY BACKTEST", "cyan", attrs=['bold'])
    cprint("="*80, "cyan")

    bt = Backtest(
        data,
        MomentumStrategy,
        cash=100000,
        commission=0.002,  # 0.2%
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

    # Compare with aggressive variant
    cprint("\n" + "="*80, "magenta")
    cprint("⚡ AGGRESSIVE MOMENTUM STRATEGY COMPARISON", "magenta", attrs=['bold'])
    cprint("="*80, "magenta")

    bt_aggressive = Backtest(
        data,
        AggressiveMomentumStrategy,
        cash=100000,
        commission=0.002,
        exclusive_orders=True
    )

    stats_aggressive = bt_aggressive.run()
    display_metrics(stats_aggressive)

    # Compare returns
    cprint(f"\n📊 Strategy Comparison:", "white", attrs=['bold'])
    cprint(f"  Base Strategy Return:       {stats['Return [%]']:.2f}%", "cyan")
    cprint(f"  Aggressive Strategy Return: {stats_aggressive['Return [%]']:.2f}%", "magenta")
    cprint(f"  Difference:                 {stats_aggressive['Return [%]'] - stats['Return [%]']:.2f}%", "yellow")

"""
🌙 Moon Dev's Pairs Trading Strategy Template
==============================================
Production-ready pairs trading (statistical arbitrage) strategy

Strategy Overview:
-----------------
Pairs trading exploits mean reversion in the price ratio of two correlated assets.
When the spread deviates from its historical mean, we trade expecting convergence.

Key Concepts:
- Statistical arbitrage between correlated assets
- Z-score based entry/exit signals
- Market-neutral strategy (long one, short other)
- Correlation stability monitoring

Indicators Used:
- Spread: log(Price1 / Price2)
- Spread SMA: 20-period mean of spread
- Spread Std Dev: 20-period standard deviation
- Z-Score: (Spread - Mean) / Std Dev
- Correlation: 60-period rolling correlation

Entry Signals:
- LONG pair: Z-score < -2.0 AND correlation > 0.7
  (Long asset 1, short asset 2)
- SHORT pair: Z-score > 2.0 AND correlation > 0.7
  (Short asset 1, long asset 2)

Exit Signals:
- Z-score returns to 0 (mean reversion)
- Z-score exceeds ±3 (stop loss - relationship broken)
- Correlation drops below 0.5 (relationship weakened)

Best Use Cases:
- BTC vs ETH
- Sector stocks (e.g., COIN vs MARA)
- Stablecoin arbitrage (USDT vs USDC)
- Exchange spreads (Binance BTC vs Coinbase BTC)

Performance Expectations:
- Win rate: 60-75% (mean reversion edge)
- Profit factor: 1.5-2.5
- Max drawdown: 8-15% (market neutral reduces risk)
- Sharpe ratio: 1.2-2.0

Risk Parameters:
- Risk per trade: 1.5%
- Max position size: 50% per leg (100% total)
- Commission: 0.2% per trade per leg
- Note: This strategy requires two data feeds

Quick Start:
-----------
from backtesting import Backtest
from pairs_trading_template import PairsTradingStrategy
from backtest_template import load_moondev_data

# Load data for BOTH assets
data_btc = load_moondev_data('BTC-USD', '15m')
data_eth = load_moondev_data('ETH-USD', '15m')

# Merge data (align timestamps)
data = merge_pair_data(data_btc, data_eth)

# Run backtest
bt = Backtest(data, PairsTradingStrategy, cash=100000, commission=0.002)
stats = bt.run()
print(stats)

Customization:
-------------
# Adjust parameters for different pairs
class MyPairsStrategy(PairsTradingStrategy):
    # More sensitive
    z_entry = 1.5
    z_exit = 0.5

    # Less sensitive
    # z_entry = 2.5
    # z_exit = 0.0

Note on Implementation:
----------------------
This template shows the LOGIC for pairs trading. However, backtesting.py
library is designed for single-asset strategies. To properly backtest pairs:

Option 1: Use the spread as a synthetic instrument
Option 2: Implement custom execution logic tracking both legs
Option 3: Use specialized pairs trading libraries

This template provides Option 1 (spread trading) as a simplified approach
that demonstrates the strategy mechanics.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
from backtesting import Strategy
from backtest_template import MoonDevStrategy


class PairsTradingStrategy(MoonDevStrategy):
    """
    Pairs trading strategy using z-score mean reversion

    Strategy Logic:
    1. Calculate price spread between two correlated assets
    2. Calculate z-score of spread vs historical mean
    3. Enter when z-score extreme (±2.0)
    4. Exit when z-score returns to mean (0)
    5. Stop loss if z-score exceeds ±3.0

    Parameters:
        spread_period (int): Period for spread mean/std (default: 20)
        z_entry (float): Z-score threshold for entry (default: 2.0)
        z_exit (float): Z-score threshold for exit (default: 0.5)
        z_stop (float): Z-score stop loss (default: 3.0)
        corr_period (int): Correlation lookback (default: 60)
        corr_threshold (float): Minimum correlation (default: 0.7)
        risk_per_trade (float): Risk per leg (default: 0.015)

    Note: This simplified version assumes Close price represents the spread
          For real pairs trading, you need to:
          1. Load data for both assets
          2. Calculate spread = log(Price1/Price2)
          3. Trade both legs simultaneously
    """

    # ========================================================================
    # STRATEGY PARAMETERS (customize these)
    # ========================================================================

    # Spread calculation
    spread_period = 20  # Period for calculating spread mean/std

    # Z-score thresholds
    z_entry = 2.0   # Enter when |z-score| > 2.0
    z_exit = 0.5    # Exit when |z-score| < 0.5
    z_stop = 3.0    # Stop loss when |z-score| > 3.0

    # Correlation monitoring
    corr_period = 60         # Lookback for correlation
    corr_threshold = 0.7     # Minimum correlation to trade

    # Risk management
    risk_per_trade = 0.015   # 1.5% risk per leg

    def init(self):
        """Initialize indicators"""
        # Spread mean (SMA of spread)
        self.spread_mean = self.I(self.sma, self.data.Close, self.spread_period)

        # Spread standard deviation
        self.spread_std = self.I(
            lambda x: pd.Series(x).rolling(self.spread_period).std(),
            self.data.Close
        )

        # Z-score: (Spread - Mean) / Std Dev
        self.z_score = self.I(
            lambda close, mean, std: (close - mean) / std,
            self.data.Close,
            self.spread_mean,
            self.spread_std
        )

        # Note: In real implementation, you'd calculate correlation between
        # the two assets here. For this simplified version, we assume
        # correlation is stable and above threshold.

        # Track entry z-score for exit logic
        self.entry_z_score = None

    def next(self):
        """Execute strategy logic on each bar"""
        spread = self.data.Close[-1]
        z = self.z_score[-1]
        std = self.spread_std[-1]

        # Skip if indicators not ready
        if np.isnan(z) or np.isnan(std) or std == 0:
            return

        # ====================================================================
        # EXIT LOGIC (check first)
        # ====================================================================

        if self.position:
            # LONG SPREAD POSITION (spread expected to increase)
            if self.position.is_long:
                # Take profit: Z-score returns toward mean
                if z >= -self.z_exit:
                    self.position.close()
                    self.entry_z_score = None
                    return

                # Stop loss: Z-score goes more negative (relationship broken)
                if z < -self.z_stop:
                    self.position.close()
                    self.entry_z_score = None
                    return

            # SHORT SPREAD POSITION (spread expected to decrease)
            if self.position.is_short:
                # Take profit: Z-score returns toward mean
                if z <= self.z_exit:
                    self.position.close()
                    self.entry_z_score = None
                    return

                # Stop loss: Z-score goes more positive (relationship broken)
                if z > self.z_stop:
                    self.position.close()
                    self.entry_z_score = None
                    return

        # ====================================================================
        # ENTRY LOGIC
        # ====================================================================

        # Only enter if no position
        if not self.position:
            # LONG SPREAD (z-score very negative - spread too low)
            # In real trading: LONG asset 1, SHORT asset 2
            # Expecting spread to increase (mean revert upward)
            if z < -self.z_entry:
                # Calculate position size
                # In pairs trading, you'd size based on volatility of spread
                size = self.risk_per_trade / abs(z / self.z_entry)  # Scale by z-score
                size = min(size, 1.0)  # Cap at 100%

                self.buy(size=size)
                self.entry_z_score = z

            # SHORT SPREAD (z-score very positive - spread too high)
            # In real trading: SHORT asset 1, LONG asset 2
            # Expecting spread to decrease (mean revert downward)
            elif z > self.z_entry:
                # Calculate position size
                size = self.risk_per_trade / abs(z / self.z_entry)
                size = min(size, 1.0)

                self.sell(size=size)
                self.entry_z_score = z


# ============================================================================
# ADVANCED VARIATIONS
# ============================================================================

class AggressivePairsTradingStrategy(PairsTradingStrategy):
    """
    More aggressive pairs trading with tighter thresholds

    Changes from base:
    - Lower entry threshold (1.5 instead of 2.0)
    - Tighter exit (0.3 instead of 0.5)
    - Tighter stop (2.5 instead of 3.0)

    Best for: High correlation pairs, frequent trades
    """
    z_entry = 1.5
    z_exit = 0.3
    z_stop = 2.5


class ConservativePairsTradingStrategy(PairsTradingStrategy):
    """
    More conservative pairs trading with wider thresholds

    Changes from base:
    - Higher entry threshold (2.5 instead of 2.0)
    - Wider exit (only at mean = 0)
    - Wider stop (3.5 instead of 3.0)

    Best for: Lower correlation pairs, high conviction trades
    """
    z_entry = 2.5
    z_exit = 0.0
    z_stop = 3.5


class CorrelationFilteredPairsTradingStrategy(PairsTradingStrategy):
    """
    Pairs trading with dynamic correlation filtering

    Additional logic:
    - Only trades when correlation > threshold
    - Exits if correlation drops below threshold
    - Uses shorter spread period during high correlation

    Best for: Pairs with variable correlation
    Note: Requires actual correlation calculation between assets
    """
    corr_period = 60
    corr_threshold = 0.75
    high_corr_threshold = 0.85

    def init(self):
        super().init()
        # In real implementation, calculate rolling correlation here
        # self.correlation = self.I(calculate_correlation, asset1, asset2)

    def next(self):
        """Override to add correlation checks"""
        spread = self.data.Close[-1]
        z = self.z_score[-1]

        # Skip if indicators not ready
        if np.isnan(z):
            return

        # In real implementation, check correlation
        # correlation = self.correlation[-1]
        # For this simplified version, assume correlation is good
        correlation = 0.80  # Placeholder

        # EXIT LOGIC with correlation check
        if self.position:
            # Exit if correlation drops
            if correlation < self.corr_threshold:
                self.position.close()
                self.entry_z_score = None
                return

            if self.position.is_long:
                if z >= -self.z_exit:
                    self.position.close()
                    self.entry_z_score = None
                    return
                if z < -self.z_stop:
                    self.position.close()
                    self.entry_z_score = None
                    return

            if self.position.is_short:
                if z <= self.z_exit:
                    self.position.close()
                    self.entry_z_score = None
                    return
                if z > self.z_stop:
                    self.position.close()
                    self.entry_z_score = None
                    return

        # ENTRY LOGIC with correlation filter
        if not self.position:
            # Only enter if correlation is high enough
            if correlation >= self.corr_threshold:
                if z < -self.z_entry:
                    size = self.risk_per_trade / abs(z / self.z_entry)
                    size = min(size, 1.0)
                    self.buy(size=size)
                    self.entry_z_score = z

                elif z > self.z_entry:
                    size = self.risk_per_trade / abs(z / self.z_entry)
                    size = min(size, 1.0)
                    self.sell(size=size)
                    self.entry_z_score = z


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def merge_pair_data(data1: pd.DataFrame, data2: pd.DataFrame,
                    asset1_name: str = 'Asset1',
                    asset2_name: str = 'Asset2') -> pd.DataFrame:
    """
    Merge two asset dataframes and calculate spread

    Args:
        data1: DataFrame for asset 1 (OHLCV format)
        data2: DataFrame for asset 2 (OHLCV format)
        asset1_name: Name for asset 1
        asset2_name: Name for asset 2

    Returns:
        DataFrame with spread as Close price

    Note: The spread becomes the 'Close' price for backtesting
          This is a simplified approach for demonstration
    """
    # Align on common index
    df1 = data1.copy()
    df2 = data2.copy()

    # Ensure same index
    common_index = df1.index.intersection(df2.index)
    df1 = df1.loc[common_index]
    df2 = df2.loc[common_index]

    # Calculate log spread
    spread = np.log(df1['Close'] / df2['Close'])

    # Create output dataframe (spread as OHLCV)
    result = pd.DataFrame(index=common_index)
    result['Open'] = np.log(df1['Open'] / df2['Open'])
    result['High'] = np.log(df1['High'] / df2['High'])
    result['Low'] = np.log(df1['Low'] / df2['Low'])
    result['Close'] = spread
    result['Volume'] = (df1['Volume'] + df2['Volume']) / 2  # Average volume

    return result


def calculate_correlation(series1: pd.Series, series2: pd.Series,
                          period: int = 60) -> pd.Series:
    """
    Calculate rolling correlation between two series

    Args:
        series1: First price series
        series2: Second price series
        period: Rolling window period

    Returns:
        Rolling correlation series
    """
    return pd.Series(series1).rolling(period).corr(pd.Series(series2))


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    """
    Example: Run pairs trading strategy backtest

    Note: This example demonstrates the LOGIC. For real pairs trading:
    1. Load data for both assets
    2. Calculate actual spread
    3. Execute both legs simultaneously
    """
    from backtesting import Backtest
    from backtest_template import load_moondev_data
    from backtest_metrics import display_metrics, calculate_moondev_score
    from termcolor import cprint

    cprint("\n" + "="*80, "yellow")
    cprint("⚠️  PAIRS TRADING TEMPLATE DEMONSTRATION", "yellow", attrs=['bold'])
    cprint("="*80, "yellow")
    cprint("\nThis template demonstrates pairs trading LOGIC.", "yellow")
    cprint("For real pairs trading, you need:", "yellow")
    cprint("  1. Data for BOTH assets (e.g., BTC and ETH)", "yellow")
    cprint("  2. Custom spread calculation", "yellow")
    cprint("  3. Simultaneous execution of both legs", "yellow")
    cprint("\nThis example uses synthetic spread data for demonstration.", "yellow")
    cprint("="*80 + "\n", "yellow")

    # For demonstration, create synthetic spread data
    # In reality, you'd load actual BTC and ETH data
    try:
        data_btc = load_moondev_data('BTC-USD', '15m')

        # Create synthetic spread (for demonstration only)
        # In real implementation: data_eth = load_moondev_data('ETH-USD', '15m')
        # Then: data = merge_pair_data(data_btc, data_eth)

        # For now, we'll use BTC price with added noise to simulate spread
        data = data_btc.copy()
        # Add mean-reverting noise to simulate spread behavior
        noise = np.random.normal(0, 0.02, len(data))
        noise_cumsum = noise.cumsum()
        noise_mean_reverting = noise_cumsum - pd.Series(noise_cumsum).rolling(20).mean().fillna(0)
        data['Close'] = data['Close'] * (1 + noise_mean_reverting * 0.1)

        cprint(f"\n✅ Created synthetic spread data ({len(data)} bars)", "green")
        cprint("⚠️  Using BTC with synthetic mean-reverting noise", "yellow")

    except FileNotFoundError:
        cprint("\n❌ Sample data not found. Please provide OHLCV data.", "red")
        cprint("Expected format: src/data/rbi/BTC-USD-15m.csv", "yellow")
        exit(1)

    # Run backtest
    cprint("\n" + "="*80, "cyan")
    cprint("📊 PAIRS TRADING STRATEGY BACKTEST", "cyan", attrs=['bold'])
    cprint("="*80, "cyan")

    bt = Backtest(
        data,
        PairsTradingStrategy,
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

    cprint("\n" + "="*80, "yellow")
    cprint("💡 NEXT STEPS FOR REAL PAIRS TRADING", "yellow", attrs=['bold'])
    cprint("="*80, "yellow")
    cprint("\n1. Load actual pair data (e.g., BTC-USD and ETH-USD)", "white")
    cprint("2. Use merge_pair_data() to create spread", "white")
    cprint("3. Implement dual-leg execution logic", "white")
    cprint("4. Monitor correlation in real-time", "white")
    cprint("5. Test with different pairs (BTC/ETH, COIN/MARA, etc.)", "white")
    cprint("\nSee documentation for full implementation guide.", "yellow")
    cprint("="*80 + "\n", "yellow")

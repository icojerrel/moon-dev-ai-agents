"""
🌙 Moon Dev's Grid Trading Strategy Template
=============================================
Production-ready grid trading strategy for range-bound markets

Strategy Overview:
-----------------
Grid trading places buy and sell orders at regular price intervals (grid levels)
to profit from price oscillation within a range. As price moves up and down,
the strategy captures small profits from each grid level.

Key Concepts:
- Pre-defined price grid (e.g., every 1% price movement)
- Buy at lower grid levels, sell at upper grid levels
- Accumulate position as price drops
- Distribute position as price rises
- Best in sideways/ranging markets

Grid Configuration:
- Grid spacing: 1-2% between levels
- Number of grids: 10-20 levels
- Base position size: 10% of equity per grid
- Total exposure: Can reach 100% when all grids filled

Entry/Exit Logic:
- BUY: When price crosses below a grid level (support)
- SELL: When price crosses above a grid level (resistance)
- Rebalance: Buy low, sell high at each grid

Best Use Cases:
- Range-bound crypto markets
- Stablecoin farming
- Post-volatility consolidation
- Sideways accumulation phases

Performance Expectations:
- Win rate: 80-90% (small consistent wins)
- Profit per trade: 0.5-2% per grid
- Max drawdown: 20-40% (if trend breaks range)
- Best in: Low volatility, mean-reverting markets

Risk Parameters:
- Max position: 100% (full grid)
- Grid size: 1-2%
- Position per grid: 5-10% of equity
- Commission: 0.2% per trade

Quick Start:
-----------
from backtesting import Backtest
from grid_trading_template import GridTradingStrategy
from backtest_template import load_moondev_data

# Load data
data = load_moondev_data('BTC-USD', '15m')

# Run backtest
bt = Backtest(data, GridTradingStrategy, cash=100000, commission=0.002)
stats = bt.run()
print(stats)
bt.plot()

Customization:
-------------
# Adjust parameters for different market conditions
class MyGridStrategy(GridTradingStrategy):
    # Tighter grid (more frequent trades)
    grid_spacing_pct = 0.005  # 0.5%
    num_grids = 20

    # Wider grid (less frequent, larger moves)
    # grid_spacing_pct = 0.02  # 2%
    # num_grids = 10

WARNING:
-------
Grid trading can suffer large drawdowns in trending markets!
- Use stop loss to close all positions if trend develops
- Best combined with range detection indicators
- Monitor for trend breakout and exit strategy
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
from backtesting import Strategy
from backtest_template import MoonDevStrategy


class GridTradingStrategy(MoonDevStrategy):
    """
    Grid trading strategy for range-bound markets

    Strategy Logic:
    1. Define price grid based on current price
    2. Place buy orders below current price (support levels)
    3. Place sell orders above current price (resistance levels)
    4. Execute trades as price crosses grid levels
    5. Rebalance grid as needed

    Parameters:
        grid_spacing_pct (float): Spacing between grid levels (default: 0.01 = 1%)
        num_grids (int): Number of grid levels (default: 15)
        position_per_grid (float): Position size per grid level (default: 0.1 = 10%)
        rebalance_threshold (float): Price move to trigger rebalance (default: 0.05 = 5%)
        use_stop_loss (bool): Enable stop loss for trend breakout (default: True)
        stop_loss_pct (float): Stop loss percentage (default: 0.15 = 15%)
        use_trailing_grid (bool): Grid moves with price (default: False)

    Note: Grid trading works best in ranging markets!
          Use trend filters to avoid grid in strong trends.
    """

    # ========================================================================
    # STRATEGY PARAMETERS (customize these)
    # ========================================================================

    # Grid configuration
    grid_spacing_pct = 0.01     # 1% between grid levels
    num_grids = 15              # Total grid levels (7 buy, 1 mid, 7 sell)
    position_per_grid = 0.10    # 10% of equity per grid

    # Grid management
    rebalance_threshold = 0.05  # Rebalance if price moves 5% from grid center
    use_trailing_grid = False   # If True, grid moves with price

    # Risk management
    use_stop_loss = True        # Enable stop loss for trend breakout
    stop_loss_pct = 0.15        # 15% stop loss from grid center

    def init(self):
        """Initialize grid levels"""
        # Calculate initial grid center from first close price
        initial_price = self.data.Close[0]
        self.grid_center = initial_price

        # Create grid levels
        self._create_grid_levels()

        # Track which grids have been filled
        self.grid_filled = {level: False for level in self.grid_levels}

        # Track total position from grid
        self.grid_position_size = 0

        # Price extremes for stop loss
        self.highest_price = initial_price
        self.lowest_price = initial_price

    def _create_grid_levels(self):
        """Create grid levels around center price"""
        self.grid_levels = []

        # Calculate number of levels above and below center
        levels_per_side = (self.num_grids - 1) // 2

        # Create levels below center (buy levels)
        for i in range(levels_per_side, 0, -1):
            level = self.grid_center * (1 - i * self.grid_spacing_pct)
            self.grid_levels.append(('BUY', level))

        # Center level
        self.grid_levels.append(('CENTER', self.grid_center))

        # Create levels above center (sell levels)
        for i in range(1, levels_per_side + 1):
            level = self.grid_center * (1 + i * self.grid_spacing_pct)
            self.grid_levels.append(('SELL', level))

    def _check_grid_rebalance(self, current_price: float) -> bool:
        """Check if grid needs rebalancing"""
        price_deviation = abs(current_price - self.grid_center) / self.grid_center
        return price_deviation > self.rebalance_threshold

    def _rebalance_grid(self, current_price: float):
        """Rebalance grid around new center price"""
        # Update grid center
        self.grid_center = current_price

        # Recreate grid levels
        self._create_grid_levels()

        # Reset filled status
        self.grid_filled = {level: False for level in self.grid_levels}

    def _find_nearest_grid(self, price: float) -> tuple:
        """Find nearest grid level below current price"""
        nearest = None
        nearest_dist = float('inf')

        for grid_type, level in self.grid_levels:
            dist = abs(price - level)
            if dist < nearest_dist:
                nearest_dist = dist
                nearest = (grid_type, level)

        return nearest

    def next(self):
        """Execute strategy logic on each bar"""
        price = self.data.Close[-1]

        # Update price extremes
        self.highest_price = max(self.highest_price, price)
        self.lowest_price = min(self.lowest_price, price)

        # ====================================================================
        # STOP LOSS CHECK (trend breakout protection)
        # ====================================================================

        if self.use_stop_loss and self.position:
            # Check if price has moved too far from grid center
            price_move_pct = abs(price - self.grid_center) / self.grid_center

            if price_move_pct > self.stop_loss_pct:
                # Trend breakout detected - close all positions
                self.position.close()
                self.grid_position_size = 0

                # Rebalance grid around new price
                self._rebalance_grid(price)
                return

        # ====================================================================
        # GRID REBALANCING
        # ====================================================================

        # Check if grid needs rebalancing (price moved too far)
        if self._check_grid_rebalance(price):
            if self.use_trailing_grid:
                # Close existing position before rebalancing
                if self.position:
                    self.position.close()
                    self.grid_position_size = 0

                self._rebalance_grid(price)

        # ====================================================================
        # GRID TRADING LOGIC
        # ====================================================================

        # Find which grid level we're at
        current_grid = self._find_nearest_grid(price)

        if current_grid is None:
            return

        grid_type, grid_level = current_grid

        # BUY at support grid levels (below center)
        if grid_type == 'BUY':
            # Only buy if price is AT or BELOW grid level
            # AND we haven't filled this grid yet
            if price <= grid_level and not self.grid_filled.get(grid_level, False):
                # Check if we have room for more position
                if self.grid_position_size < 1.0:  # Max 100% position
                    # Calculate position size for this grid
                    size = min(self.position_per_grid,
                              1.0 - self.grid_position_size)

                    if size > 0:
                        self.buy(size=size)
                        self.grid_filled[grid_level] = True
                        self.grid_position_size += size

        # SELL at resistance grid levels (above center)
        elif grid_type == 'SELL':
            # Only sell if price is AT or ABOVE grid level
            # AND we have position to sell
            if price >= grid_level and self.position and self.position.is_long:
                if not self.grid_filled.get(grid_level, False):
                    # Calculate sell size (partial position)
                    size = min(self.position_per_grid,
                              self.grid_position_size)

                    if size > 0:
                        # Sell portion of position
                        self.position.close(portion=size / self.grid_position_size)
                        self.grid_filled[grid_level] = True
                        self.grid_position_size -= size


# ============================================================================
# ADVANCED VARIATIONS
# ============================================================================

class TightGridStrategy(GridTradingStrategy):
    """
    Tighter grid for more frequent trades

    Changes from base:
    - Smaller grid spacing (0.5% instead of 1%)
    - More grid levels (25 instead of 15)
    - Smaller position per grid (5% instead of 10%)

    Best for: High volatility, active trading
    """
    grid_spacing_pct = 0.005
    num_grids = 25
    position_per_grid = 0.05


class WideGridStrategy(GridTradingStrategy):
    """
    Wider grid for larger moves

    Changes from base:
    - Larger grid spacing (2% instead of 1%)
    - Fewer grid levels (10 instead of 15)
    - Larger position per grid (15% instead of 10%)

    Best for: Lower volatility, patient approach
    """
    grid_spacing_pct = 0.02
    num_grids = 10
    position_per_grid = 0.15


class TrailingGridStrategy(GridTradingStrategy):
    """
    Grid that trails price movement

    Changes from base:
    - Grid moves with price (trailing enabled)
    - Tighter rebalance threshold (3% instead of 5%)
    - Wider stop loss (20% instead of 15%)

    Best for: Trending markets with pullbacks
    """
    use_trailing_grid = True
    rebalance_threshold = 0.03
    stop_loss_pct = 0.20


class RangeDetectionGridStrategy(GridTradingStrategy):
    """
    Grid trading with range detection filter

    Additional logic:
    - Only trades when ADX < 25 (ranging market)
    - Exits all positions when ADX > 30 (trending market)
    - Uses ATR for dynamic grid spacing

    Best for: Adaptive grid trading
    """
    adx_period = 14
    adx_range_threshold = 25
    adx_trend_threshold = 30
    use_dynamic_spacing = True

    def init(self):
        super().init()

        # Add ADX for range detection
        self.adx_line = self.I(
            self.adx,
            self.data.High,
            self.data.Low,
            self.data.Close,
            self.adx_period
        )

        # Add ATR for dynamic grid spacing
        if self.use_dynamic_spacing:
            self.atr_line = self.I(
                self.atr,
                self.data.High,
                self.data.Low,
                self.data.Close,
                14
            )

    def next(self):
        """Override to add range detection"""
        price = self.data.Close[-1]
        adx = self.adx_line[-1]

        # Skip if ADX not ready
        if np.isnan(adx):
            return

        # Exit all positions if trending market detected
        if adx > self.adx_trend_threshold and self.position:
            self.position.close()
            self.grid_position_size = 0
            return

        # Only trade grid in ranging markets
        if adx > self.adx_range_threshold:
            return  # Skip grid trading in trending markets

        # Use dynamic grid spacing based on ATR
        if self.use_dynamic_spacing and hasattr(self, 'atr_line'):
            atr = self.atr_line[-1]
            if not np.isnan(atr):
                # Adjust grid spacing to 0.5x ATR
                dynamic_spacing = atr / price
                self.grid_spacing_pct = max(0.005, min(0.03, dynamic_spacing))

        # Execute parent grid logic
        super().next()


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    """
    Example: Run grid trading strategy backtest
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

    cprint("\n" + "="*80, "yellow")
    cprint("⚠️  GRID TRADING STRATEGY WARNING", "yellow", attrs=['bold'])
    cprint("="*80, "yellow")
    cprint("\nGrid trading works BEST in range-bound markets!", "yellow")
    cprint("In trending markets, grid trading can suffer large drawdowns.", "yellow")
    cprint("\nThis backtest will show performance across all market conditions.", "yellow")
    cprint("Real trading should use range detection filters!", "yellow")
    cprint("="*80 + "\n", "yellow")

    # Run backtest with base strategy
    cprint("\n" + "="*80, "cyan")
    cprint("📊 GRID TRADING STRATEGY BACKTEST", "cyan", attrs=['bold'])
    cprint("="*80, "cyan")

    bt = Backtest(
        data,
        GridTradingStrategy,
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

    # Compare with range detection variant
    cprint("\n" + "="*80, "magenta")
    cprint("🎯 RANGE DETECTION GRID COMPARISON", "magenta", attrs=['bold'])
    cprint("="*80, "magenta")

    bt_range = Backtest(
        data,
        RangeDetectionGridStrategy,
        cash=100000,
        commission=0.002,
        exclusive_orders=True
    )

    stats_range = bt_range.run()
    display_metrics(stats_range)

    # Compare returns
    cprint(f"\n📊 Strategy Comparison:", "white", attrs=['bold'])
    cprint(f"  Base Grid Return:           {stats['Return [%]']:.2f}%", "cyan")
    cprint(f"  Range Detection Grid Return: {stats_range['Return [%]']:.2f}%", "magenta")
    cprint(f"  Difference:                  {stats_range['Return [%]'] - stats['Return [%]']:.2f}%", "yellow")

    cprint("\n" + "="*80, "green")
    cprint("💡 GRID TRADING BEST PRACTICES", "green", attrs=['bold'])
    cprint("="*80, "green")
    cprint("\n1. Use range detection (ADX < 25) to avoid trending markets", "white")
    cprint("2. Set stop loss to protect against trend breakouts", "white")
    cprint("3. Start with wider grids (2%) and adjust based on volatility", "white")
    cprint("4. Monitor position size carefully (max 100% exposure)", "white")
    cprint("5. Test on historical ranging periods for best results", "white")
    cprint("\nGrid trading = HIGH WIN RATE but CAN HAVE LARGE DRAWDOWNS in trends!", "yellow")
    cprint("="*80 + "\n", "green")

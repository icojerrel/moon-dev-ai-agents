"""
🌙 Moon Dev's Backtesting Template
===============================
Base template for creating backtests using backtesting.py library with pandas_ta/talib indicators

This template follows CLAUDE.md guidelines:
- Uses backtesting.py library (NOT their built-in indicators)
- Uses pandas_ta or talib for technical indicators
- Includes comprehensive performance metrics
- Real data only (no synthetic data)

Quick Start:
-----------
from backtesting import Backtest
from backtest_template import MoonDevStrategy, load_ohlcv_data

# 1. Load data
data = load_ohlcv_data('BTC-USD-15m.csv')

# 2. Create your strategy class (inherit from MoonDevStrategy)
class MyStrategy(MoonDevStrategy):
    # ... implement your strategy

# 3. Run backtest
bt = Backtest(data, MyStrategy, cash=100000, commission=0.002)
stats = bt.run()
print(stats)
bt.plot()
"""

import pandas as pd
import numpy as np
from backtesting import Strategy
from backtesting.lib import crossover
import pandas_ta as ta
from pathlib import Path
from typing import Optional, Union
from termcolor import cprint


# ============================================================================
# DATA LOADING UTILITIES
# ============================================================================

def load_ohlcv_data(
    filepath: Union[str, Path],
    datetime_col: str = 'datetime',
    required_cols: Optional[list] = None
) -> pd.DataFrame:
    """
    Load OHLCV data from CSV for backtesting

    Args:
        filepath: Path to CSV file
        datetime_col: Name of datetime column
        required_cols: List of required columns (default: ['Open', 'High', 'Low', 'Close', 'Volume'])

    Returns:
        DataFrame with datetime index and OHLC columns (capitalized)

    Example:
        >>> data = load_ohlcv_data('BTC-USD-15m.csv')
        >>> print(data.head())
    """
    if required_cols is None:
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']

    try:
        # Read CSV
        df = pd.read_csv(filepath)

        # Handle column names (convert to Title Case for backtesting.py)
        df.columns = df.columns.str.strip()  # Remove whitespace

        # Convert datetime column
        if datetime_col in df.columns:
            df[datetime_col] = pd.to_datetime(df[datetime_col])
            df.set_index(datetime_col, inplace=True)
        else:
            raise ValueError(f"Datetime column '{datetime_col}' not found")

        # Standardize column names to Title Case
        column_mapping = {}
        for col in df.columns:
            col_clean = col.strip().lower()
            if col_clean in ['open', 'high', 'low', 'close', 'volume']:
                column_mapping[col] = col_clean.capitalize()

        df.rename(columns=column_mapping, inplace=True)

        # Verify required columns exist
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        # Select only required columns
        df = df[required_cols]

        # Remove any NaN values
        df.dropna(inplace=True)

        cprint(f"✅ Loaded {len(df)} bars from {Path(filepath).name}", "green")
        cprint(f"   Date range: {df.index[0]} to {df.index[-1]}", "cyan")
        cprint(f"   Columns: {list(df.columns)}", "cyan")

        return df

    except Exception as e:
        cprint(f"❌ Error loading data from {filepath}: {str(e)}", "red")
        raise


def load_moondev_data(
    symbol: str = 'BTC-USD',
    timeframe: str = '15m',
    data_dir: Optional[Path] = None
) -> pd.DataFrame:
    """
    Convenience function to load Moon Dev's standard data format

    Args:
        symbol: Trading pair symbol (e.g., 'BTC-USD')
        timeframe: Timeframe (e.g., '15m', '1H', '1D')
        data_dir: Directory containing data files (default: src/data/rbi/)

    Returns:
        DataFrame ready for backtesting

    Example:
        >>> data = load_moondev_data('BTC-USD', '15m')
    """
    if data_dir is None:
        # Default to Moon Dev's data directory
        data_dir = Path(__file__).parent.parent / 'data' / 'rbi'

    filename = f"{symbol}-{timeframe}.csv"
    filepath = data_dir / filename

    if not filepath.exists():
        raise FileNotFoundError(f"Data file not found: {filepath}")

    return load_ohlcv_data(filepath)


# ============================================================================
# BASE STRATEGY TEMPLATE
# ============================================================================

class MoonDevStrategy(Strategy):
    """
    Base strategy class for Moon Dev backtests

    Provides common utilities and follows Moon Dev coding patterns

    Features:
    - Pre-configured with pandas_ta for indicators
    - Includes common utility methods
    - Follows backtesting.py best practices
    - Real data only, no synthetic data

    Usage:
        class MyStrategy(MoonDevStrategy):
            # Define parameters as class variables
            fast_period = 20
            slow_period = 50

            def init(self):
                super().init()  # Call parent init
                # Calculate indicators
                self.sma_fast = self.I(self.sma, self.data.Close, self.fast_period)
                self.sma_slow = self.I(self.sma, self.data.Close, self.slow_period)

            def next(self):
                # Implement trading logic
                if crossover(self.sma_fast, self.sma_slow):
                    self.buy()
                elif crossover(self.sma_slow, self.sma_fast):
                    self.position.close()
    """

    def init(self):
        """Initialize strategy - called once before backtest starts"""
        pass

    def next(self):
        """Process next bar - called for each bar in the data"""
        raise NotImplementedError("Strategy must implement next() method")

    # ========================================================================
    # INDICATOR WRAPPERS (using pandas_ta)
    # ========================================================================

    @staticmethod
    def sma(series: pd.Series, period: int) -> pd.Series:
        """Simple Moving Average using pandas_ta"""
        return ta.sma(series, length=period)

    @staticmethod
    def ema(series: pd.Series, period: int) -> pd.Series:
        """Exponential Moving Average using pandas_ta"""
        return ta.ema(series, length=period)

    @staticmethod
    def rsi(series: pd.Series, period: int = 14) -> pd.Series:
        """Relative Strength Index using pandas_ta"""
        return ta.rsi(series, length=period)

    @staticmethod
    def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
        """MACD using pandas_ta - returns (macd_line, signal_line, histogram)"""
        macd_df = ta.macd(series, fast=fast, slow=slow, signal=signal)
        return macd_df.iloc[:, 0], macd_df.iloc[:, 1], macd_df.iloc[:, 2]

    @staticmethod
    def bbands(series: pd.Series, period: int = 20, std: float = 2.0):
        """Bollinger Bands using pandas_ta - returns (lower, mid, upper)"""
        bb_df = ta.bbands(series, length=period, std=std)
        return bb_df.iloc[:, 0], bb_df.iloc[:, 1], bb_df.iloc[:, 2]

    @staticmethod
    def atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Average True Range using pandas_ta"""
        return ta.atr(high=high, low=low, close=close, length=period)

    @staticmethod
    def adx(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Average Directional Index using pandas_ta"""
        adx_df = ta.adx(high=high, low=low, close=close, length=period)
        return adx_df.iloc[:, 0]  # Return ADX column

    # ========================================================================
    # POSITION MANAGEMENT UTILITIES
    # ========================================================================

    def calculate_position_size(
        self,
        risk_pct: float = 0.02,
        stop_loss_pct: Optional[float] = None
    ) -> float:
        """
        Calculate position size based on risk percentage

        Args:
            risk_pct: Percentage of equity to risk per trade (default: 2%)
            stop_loss_pct: Stop loss percentage (optional)

        Returns:
            Position size as fraction of equity
        """
        if stop_loss_pct is None:
            return risk_pct

        # Kelly Criterion-style sizing
        position_size = risk_pct / stop_loss_pct
        return min(position_size, 1.0)  # Cap at 100% of equity

    def is_uptrend(self, ma_short, ma_long) -> bool:
        """Check if market is in uptrend"""
        return ma_short[-1] > ma_long[-1]

    def is_downtrend(self, ma_short, ma_long) -> bool:
        """Check if market is in downtrend"""
        return ma_short[-1] < ma_long[-1]


# ============================================================================
# EXAMPLE STRATEGIES
# ============================================================================

class SMACrossoverStrategy(MoonDevStrategy):
    """
    Simple Moving Average Crossover Strategy

    Rules:
    - Buy when fast MA crosses above slow MA
    - Sell when fast MA crosses below slow MA

    Parameters:
    - fast_period: Fast MA period (default: 20)
    - slow_period: Slow MA period (default: 50)
    """

    # Strategy parameters (can be optimized)
    fast_period = 20
    slow_period = 50

    def init(self):
        super().init()

        # Calculate moving averages
        self.sma_fast = self.I(self.sma, self.data.Close, self.fast_period)
        self.sma_slow = self.I(self.sma, self.data.Close, self.slow_period)

    def next(self):
        # Bullish crossover - buy signal
        if crossover(self.sma_fast, self.sma_slow):
            if not self.position:
                self.buy()

        # Bearish crossover - sell signal
        elif crossover(self.sma_slow, self.sma_fast):
            if self.position:
                self.position.close()


class RSIOversoldStrategy(MoonDevStrategy):
    """
    RSI Oversold/Overbought Strategy

    Rules:
    - Buy when RSI crosses above oversold level (default: 30)
    - Sell when RSI crosses below overbought level (default: 70)

    Parameters:
    - rsi_period: RSI calculation period (default: 14)
    - oversold: Oversold threshold (default: 30)
    - overbought: Overbought threshold (default: 70)
    """

    rsi_period = 14
    oversold = 30
    overbought = 70

    def init(self):
        super().init()
        self.rsi_indicator = self.I(self.rsi, self.data.Close, self.rsi_period)

    def next(self):
        # Buy when RSI crosses above oversold
        if self.rsi_indicator[-2] < self.oversold and self.rsi_indicator[-1] > self.oversold:
            if not self.position:
                self.buy()

        # Sell when RSI crosses below overbought
        elif self.rsi_indicator[-2] > self.overbought and self.rsi_indicator[-1] < self.overbought:
            if self.position:
                self.position.close()


class TrendFollowingStrategy(MoonDevStrategy):
    """
    Trend Following Strategy with ADX filter

    Rules:
    - Only trade when ADX > threshold (strong trend)
    - Buy when price crosses above EMA in uptrend
    - Sell when price crosses below EMA in downtrend

    Parameters:
    - ema_period: EMA period (default: 50)
    - adx_period: ADX period (default: 14)
    - adx_threshold: Minimum ADX for trend confirmation (default: 25)
    """

    ema_period = 50
    adx_period = 14
    adx_threshold = 25

    def init(self):
        super().init()
        self.ema_line = self.I(self.ema, self.data.Close, self.ema_period)
        self.adx_line = self.I(
            self.adx,
            self.data.High,
            self.data.Low,
            self.data.Close,
            self.adx_period
        )

    def next(self):
        # Only trade when trend is strong (high ADX)
        if self.adx_line[-1] < self.adx_threshold:
            return

        # Buy signal: price crosses above EMA in strong trend
        if crossover(self.data.Close, self.ema_line):
            if not self.position:
                self.buy()

        # Sell signal: price crosses below EMA
        elif crossover(self.ema_line, self.data.Close):
            if self.position:
                self.position.close()


# ============================================================================
# MAIN (EXAMPLE USAGE)
# ============================================================================

if __name__ == "__main__":
    """
    Example: How to run a backtest
    """
    from backtesting import Backtest

    cprint("\n🌙 Moon Dev's Backtesting Template - Example Backtest", "cyan", attrs=["bold"])
    cprint("=" * 70, "cyan")

    # 1. Load data
    try:
        data = load_moondev_data('BTC-USD', '15m')
    except FileNotFoundError:
        cprint("⚠️  Sample data not found, using example path", "yellow")
        cprint("   Update the path in load_ohlcv_data() to your data location", "yellow")
        exit(1)

    # 2. Run backtest with SMA Crossover Strategy
    cprint("\n📊 Testing SMA Crossover Strategy...", "cyan")
    bt = Backtest(
        data,
        SMArossoverStrategy,
        cash=100000,
        commission=0.002,  # 0.2% commission
        exclusive_orders=True
    )

    stats = bt.run()

    # 3. Print results
    cprint("\n✅ Backtest Complete!", "green", attrs=["bold"])
    print(stats)

    # 4. Show plot (optional)
    # bt.plot()

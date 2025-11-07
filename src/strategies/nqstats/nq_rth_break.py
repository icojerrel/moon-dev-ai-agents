"""
NQ RTH Break Directional Bias Strategy
Based on NQStats.com 10-20 year historical data (2004-2025)

Strategy Logic:
- Compare current RTH open (9:30am EST) with previous day RTH range (pRTH)
- If RTH opens OUTSIDE pRTH: 83.29% probability price will NOT break opposite side
- If RTH opens INSIDE pRTH: 72.66% probability of breaking at least one side
- Entry: First 5-min bar confirmation
- Stop: pRTH boundary on opposite side
- Target: 1.5x pRTH range extension

Moon Dev's AI Trading System
Built with love by Moon Dev
"""

from backtesting import Backtest, Strategy
import pandas as pd
import talib
from datetime import datetime, time


class NQRTHBreak(Strategy):
    """
    RTH Break Directional Bias Strategy

    Highest probability NQStats edge: 83.29%
    Entry: RTH opens outside previous RTH range
    Stop: Opposite pRTH boundary
    Target: 1.5x pRTH range extension
    """

    # Parameters
    risk_percent = 2.0  # Risk 2% per trade
    rth_open_hour = 9  # 9:30am EST
    rth_close_hour = 16  # 4pm EST
    target_multiplier = 1.5  # 1.5x pRTH range for target

    def init(self):
        """Initialize strategy indicators and tracking variables"""
        # Track RTH ranges
        self.prev_rth_high = None
        self.prev_rth_low = None
        self.current_rth_open = None
        self.current_rth_high = None
        self.current_rth_low = None
        self.in_position = False
        self.entry_triggered = False
        self.current_day = None

    def next(self):
        """Strategy logic executed on each bar"""
        current_time = self.data.index[-1]
        current_hour = current_time.hour
        current_minute = current_time.minute
        current_date = current_time.date()

        # Get current OHLC
        current_open = self.data.Open[-1]
        current_high = self.data.High[-1]
        current_low = self.data.Low[-1]
        current_close = self.data.Close[-1]

        # Reset daily tracking on new day
        if current_date != self.current_day:
            self.current_day = current_date
            self.entry_triggered = False

            # Move current RTH to previous RTH
            if self.current_rth_high is not None and self.current_rth_low is not None:
                self.prev_rth_high = self.current_rth_high
                self.prev_rth_low = self.current_rth_low

            # Reset current RTH
            self.current_rth_high = None
            self.current_rth_low = None
            self.current_rth_open = None

        # Track RTH open (9:30am)
        if current_hour == self.rth_open_hour and current_minute == 30:
            self.current_rth_open = current_open

            # Initialize RTH high/low
            if self.current_rth_high is None:
                self.current_rth_high = current_high
            if self.current_rth_low is None:
                self.current_rth_low = current_low

        # Update RTH high/low during session
        if self.rth_open_hour <= current_hour < self.rth_close_hour:
            if self.current_rth_high is None or current_high > self.current_rth_high:
                self.current_rth_high = current_high
            if self.current_rth_low is None or current_low < self.current_rth_low:
                self.current_rth_low = current_low

        # Entry logic: First 5 minutes after RTH open
        if (current_hour == self.rth_open_hour and
            current_minute >= 30 and current_minute <= 35 and
            not self.entry_triggered and
            not self.position and
            self.prev_rth_high is not None and
            self.prev_rth_low is not None and
            self.current_rth_open is not None):

            prth_range = self.prev_rth_high - self.prev_rth_low

            # Scenario 1: RTH opens ABOVE previous RTH high (83.29% edge)
            if self.current_rth_open > self.prev_rth_high:
                # Strong bullish bias - go LONG
                stop_loss = self.prev_rth_high  # Stop at pRTH boundary
                target = self.current_rth_open + (prth_range * self.target_multiplier)
                risk_points = self.current_rth_open - stop_loss

                if risk_points > 0:
                    position_size = int(round((self.equity * self.risk_percent / 100) / risk_points))
                    if position_size > 0:
                        self.buy(size=position_size)
                        self.in_position = True
                        self.entry_triggered = True

            # Scenario 2: RTH opens BELOW previous RTH low (83.29% edge)
            elif self.current_rth_open < self.prev_rth_low:
                # Strong bearish bias - go SHORT
                stop_loss = self.prev_rth_low  # Stop at pRTH boundary
                target = self.current_rth_open - (prth_range * self.target_multiplier)
                risk_points = stop_loss - self.current_rth_open

                if risk_points > 0:
                    position_size = int(round((self.equity * self.risk_percent / 100) / risk_points))
                    if position_size > 0:
                        self.sell(size=position_size)
                        self.in_position = True
                        self.entry_triggered = True

            # Scenario 3: RTH opens INSIDE pRTH (72.66% probability of breaking one side)
            # Skip this scenario for now - lower probability, needs more complex logic

        # Exit logic
        if self.position:
            prth_range = self.prev_rth_high - self.prev_rth_low if self.prev_rth_high and self.prev_rth_low else 0

            # Exit at end of session (4pm)
            if current_hour >= self.rth_close_hour:
                self.position.close()
                self.in_position = False

            # Take profit: 1.5x pRTH range extension
            elif self.position.is_long:
                target = self.current_rth_open + (prth_range * self.target_multiplier)
                if current_close >= target:
                    self.position.close()
                    self.in_position = False

                # Stop loss: pRTH high (opposite boundary)
                elif current_close < self.prev_rth_high:
                    self.position.close()
                    self.in_position = False

            elif self.position.is_short:
                target = self.current_rth_open - (prth_range * self.target_multiplier)
                if current_close <= target:
                    self.position.close()
                    self.in_position = False

                # Stop loss: pRTH low (opposite boundary)
                elif current_close > self.prev_rth_low:
                    self.position.close()
                    self.in_position = False


def run_backtest():
    """Run the backtest on BTC-USD-15m data"""
    print("\n" + "="*80)
    print("NQ RTH Break Directional Bias Strategy Backtest")
    print("Based on NQStats.com 10-20 year historical data")
    print("Strategy Edge: 83.29% probability")
    print("="*80 + "\n")

    # Load data
    data_path = "/home/user/moon-dev-ai-agents/src/data/rbi/BTC-USD-15m.csv"
    print(f"Loading data from: {data_path}")

    df = pd.read_csv(data_path)

    # Clean column names
    df.columns = df.columns.str.strip().str.lower()

    # Drop unnamed columns
    df = df.drop(columns=[col for col in df.columns if 'unnamed' in col.lower()], errors='ignore')

    # Ensure proper datetime index
    df['datetime'] = pd.to_datetime(df['datetime'])
    df.set_index('datetime', inplace=True)

    # Capitalize OHLCV columns for backtesting.py
    df.columns = [col.capitalize() for col in df.columns]

    print(f"\nData loaded successfully!")
    print(f"  - Shape: {df.shape}")
    print(f"  - Date range: {df.index[0]} to {df.index[-1]}")
    print(f"  - Columns: {list(df.columns)}")

    # Run backtest
    print("\nRunning backtest...")
    bt = Backtest(
        df,
        NQRTHBreak,
        cash=1_000_000,
        commission=0.002,  # 0.2% commission
        exclusive_orders=True
    )

    stats = bt.run()

    # Print results
    print("\n" + "="*80)
    print("BACKTEST RESULTS - NQ RTH Break Directional Bias")
    print("="*80)
    print(stats)
    print("\n" + "="*80)
    print("Strategy Details:")
    print("="*80)
    print(stats._strategy)

    return stats


if __name__ == "__main__":
    stats = run_backtest()

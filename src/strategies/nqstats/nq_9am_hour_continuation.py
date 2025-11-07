"""
NQ 9AM Hour Continuation Strategy
Based on NQStats.com 10-20 year historical data (2004-2025)

Strategy Logic:
- Trade in direction of 9am hour close (9:30am-10:30am EST)
- If 9am hour closes green: 67% probability entire session closes green
- 70% probability NY session (4pm > 9:30am) closes green
- Entry timing: First 20-min segment has 89% retracement probability
- Avoid middle segment (20-40min) entries

Moon Dev's AI Trading System
Built with love by Moon Dev
"""

from backtesting import Backtest, Strategy
import pandas as pd
import talib
from datetime import datetime, time


class NQ9AMHourContinuation(Strategy):
    """
    9AM Hour Continuation Strategy

    Highest probability NQStats edge: 67-70%
    Entry: Direction of 9am hour close
    Stop: 9am hour extreme (high for shorts, low for longs)
    Target: End of session or break of 9:30am open
    """

    # Parameters
    risk_percent = 2.0  # Risk 2% per trade
    session_start_hour = 9  # 9:30am EST (adjusted to 9 for hour bar)
    session_end_hour = 16  # 4pm EST

    def init(self):
        """Initialize strategy indicators and tracking variables"""
        # No traditional indicators needed - pure price action
        # Track session structure
        self.in_position = False
        self.session_open = None
        self.hour_9am_open = None
        self.hour_9am_close = None
        self.hour_9am_high = None
        self.hour_9am_low = None

    def next(self):
        """Strategy logic executed on each bar"""
        current_time = self.data.index[-1]
        current_hour = current_time.hour
        current_minute = current_time.minute

        # Get current OHLC
        current_open = self.data.Open[-1]
        current_high = self.data.High[-1]
        current_low = self.data.Low[-1]
        current_close = self.data.Close[-1]

        # Track 9:30am session open (first bar of session)
        if current_hour == self.session_start_hour and current_minute == 30:
            self.session_open = current_open
            self.hour_9am_open = current_open

        # Track 9am hour completion (10:30am - end of first hour)
        if current_hour == 10 and current_minute == 30:
            self.hour_9am_close = self.data.Close[-1]
            self.hour_9am_high = max(self.data.High[-60:])  # Last 60 15-min bars = 1 hour
            self.hour_9am_low = min(self.data.Low[-60:])

            # Determine direction based on 9am hour
            if self.hour_9am_close > self.hour_9am_open:
                # Bullish 9am hour - 67% edge for green session
                direction = "LONG"
            else:
                # Bearish 9am hour
                direction = "SHORT"

            # Entry logic: Wait for first 20-min pullback (89% retracement probability)
            # Enter on next bar after 10:30am with 9am hour direction
            if direction == "LONG" and not self.position:
                # Calculate position size based on risk
                stop_loss = self.hour_9am_low
                risk_points = current_close - stop_loss
                if risk_points > 0:
                    position_size = int(round((self.equity * self.risk_percent / 100) / risk_points))
                    if position_size > 0:
                        self.buy(size=position_size)
                        self.in_position = True

            elif direction == "SHORT" and not self.position:
                # Calculate position size based on risk
                stop_loss = self.hour_9am_high
                risk_points = stop_loss - current_close
                if risk_points > 0:
                    position_size = int(round((self.equity * self.risk_percent / 100) / risk_points))
                    if position_size > 0:
                        self.sell(size=position_size)
                        self.in_position = True

        # Exit logic
        if self.position:
            # Exit at end of session (4pm)
            if current_hour >= self.session_end_hour:
                self.position.close()
                self.in_position = False

            # Exit if price breaks below session open for longs
            elif self.position.is_long and current_close < self.session_open:
                self.position.close()
                self.in_position = False

            # Exit if price breaks above session open for shorts
            elif self.position.is_short and current_close > self.session_open:
                self.position.close()
                self.in_position = False

            # Stop loss: 9am hour extremes
            elif self.position.is_long and current_close < self.hour_9am_low:
                self.position.close()
                self.in_position = False

            elif self.position.is_short and current_close > self.hour_9am_high:
                self.position.close()
                self.in_position = False


def run_backtest():
    """Run the backtest on BTC-USD-15m data"""
    print("\n" + "="*80)
    print("NQ 9AM Hour Continuation Strategy Backtest")
    print("Based on NQStats.com 10-20 year historical data")
    print("Strategy Edge: 67-70% probability")
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
        NQ9AMHourContinuation,
        cash=1_000_000,
        commission=0.002,  # 0.2% commission
        exclusive_orders=True
    )

    stats = bt.run()

    # Print results
    print("\n" + "="*80)
    print("BACKTEST RESULTS - NQ 9AM Hour Continuation")
    print("="*80)
    print(stats)
    print("\n" + "="*80)
    print("Strategy Details:")
    print("="*80)
    print(stats._strategy)

    return stats


if __name__ == "__main__":
    stats = run_backtest()

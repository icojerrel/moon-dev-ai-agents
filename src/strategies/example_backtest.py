"""
🌙 Moon Dev's Example Backtest
==============================
Complete example showing how to use the backtesting framework

This file demonstrates:
1. Loading OHLCV data
2. Creating custom strategies
3. Running backtests
4. Analyzing performance
5. Comparing multiple strategies
6. Optimizing parameters

Run this file directly:
    python src/strategies/example_backtest.py
"""

from backtesting import Backtest
from backtesting.lib import crossover
from backtest_template import (
    MoonDevStrategy,
    load_moondev_data,
    SMACrossoverStrategy,
    RSIOversoldStrategy,
    TrendFollowingStrategy
)
from backtest_metrics import (
    analyze_performance,
    print_metrics,
    compare_strategies,
    print_comparison
)
from termcolor import cprint
import pandas_ta as ta


# ============================================================================
# EXAMPLE CUSTOM STRATEGIES
# ============================================================================

class BollingerBandsStrategy(MoonDevStrategy):
    """
    Bollinger Bands Mean Reversion Strategy

    Entry:
    - Buy when price touches lower band
    - Sell when price touches upper band

    Parameters:
    - bb_period: Bollinger Bands period (default: 20)
    - bb_std: Standard deviations (default: 2.0)
    """

    bb_period = 20
    bb_std = 2.0

    def init(self):
        super().init()

        # Calculate Bollinger Bands
        bb_result = self.I(
            self.bbands,
            self.data.Close,
            self.bb_period,
            self.bb_std
        )
        self.bb_lower = bb_result[0]  # Lower band
        self.bb_mid = bb_result[1]     # Middle band
        self.bb_upper = bb_result[2]   # Upper band

    def next(self):
        price = self.data.Close[-1]

        # Buy when price touches lower band (oversold)
        if price <= self.bb_lower[-1]:
            if not self.position:
                self.buy()

        # Sell when price touches upper band (overbought)
        elif price >= self.bb_upper[-1]:
            if self.position:
                self.position.close()


class MACDCrossoverStrategy(MoonDevStrategy):
    """
    MACD Crossover Strategy

    Entry:
    - Buy when MACD crosses above signal line
    - Sell when MACD crosses below signal line

    Parameters:
    - macd_fast: Fast EMA period (default: 12)
    - macd_slow: Slow EMA period (default: 26)
    - macd_signal: Signal line period (default: 9)
    """

    macd_fast = 12
    macd_slow = 26
    macd_signal = 9

    def init(self):
        super().init()

        # Calculate MACD
        macd_result = self.I(
            self.macd,
            self.data.Close,
            self.macd_fast,
            self.macd_slow,
            self.macd_signal
        )
        self.macd_line = macd_result[0]
        self.signal_line = macd_result[1]

    def next(self):
        # Buy signal: MACD crosses above signal
        if crossover(self.macd_line, self.signal_line):
            if not self.position:
                self.buy()

        # Sell signal: MACD crosses below signal
        elif crossover(self.signal_line, self.macd_line):
            if self.position:
                self.position.close()


class MultiIndicatorStrategy(MoonDevStrategy):
    """
    Multi-Indicator Confirmation Strategy

    Entry Requirements (ALL must be true):
    - Price above 200 EMA (uptrend filter)
    - RSI between 40-60 (not overbought/oversold)
    - MACD > Signal (momentum confirmation)
    - Price > 20 SMA (short-term trend)

    Exit:
    - Price crosses below 20 SMA
    - Or RSI > 70 (overbought)

    Parameters:
    - ema_period: Trend filter EMA (default: 200)
    - sma_period: Entry trigger SMA (default: 20)
    - rsi_period: RSI period (default: 14)
    """

    ema_period = 200
    sma_period = 20
    rsi_period = 14

    def init(self):
        super().init()

        # Trend filter
        self.ema_long = self.I(self.ema, self.data.Close, self.ema_period)

        # Entry trigger
        self.sma_short = self.I(self.sma, self.data.Close, self.sma_period)

        # Momentum indicators
        self.rsi_indicator = self.I(self.rsi, self.data.Close, self.rsi_period)

        macd_result = self.I(self.macd, self.data.Close, 12, 26, 9)
        self.macd_line = macd_result[0]
        self.signal_line = macd_result[1]

    def next(self):
        price = self.data.Close[-1]

        # Entry conditions (all must be true)
        uptrend = price > self.ema_long[-1]
        rsi_neutral = 40 < self.rsi_indicator[-1] < 60
        macd_bullish = self.macd_line[-1] > self.signal_line[-1]
        price_above_sma = price > self.sma_short[-1]

        # Entry signal
        if uptrend and rsi_neutral and macd_bullish and price_above_sma:
            if not self.position:
                self.buy()

        # Exit conditions
        if self.position:
            exit_sma = price < self.sma_short[-1]
            exit_rsi = self.rsi_indicator[-1] > 70

            if exit_sma or exit_rsi:
                self.position.close()


# ============================================================================
# MAIN BACKTEST EXECUTION
# ============================================================================

def run_single_backtest():
    """Example: Run a single backtest"""

    cprint("\n" + "=" * 70, "cyan")
    cprint("🌙 EXAMPLE 1: Single Strategy Backtest", "cyan", attrs=["bold"])
    cprint("=" * 70, "cyan")

    # 1. Load data
    cprint("\n📊 Loading data...", "white")
    data = load_moondev_data('BTC-USD', '15m')

    # 2. Create backtest
    cprint("\n🚀 Running SMA Crossover Strategy...", "white")
    bt = Backtest(
        data,
        SMACrossoverStrategy,
        cash=100000,
        commission=0.002,  # 0.2% commission
        exclusive_orders=True
    )

    # 3. Run backtest
    stats = bt.run()

    # 4. Analyze performance
    metrics = analyze_performance(stats)
    print_metrics(metrics)

    # 5. Optional: Show plot
    # bt.plot()

    return stats, metrics


def run_strategy_comparison():
    """Example: Compare multiple strategies"""

    cprint("\n" + "=" * 70, "cyan")
    cprint("🌙 EXAMPLE 2: Strategy Comparison", "cyan", attrs=["bold"])
    cprint("=" * 70, "cyan")

    # Load data once
    cprint("\n📊 Loading data...", "white")
    data = load_moondev_data('BTC-USD', '15m')

    # List of strategies to test
    strategies = [
        ("SMA Crossover", SMACrossoverStrategy),
        ("RSI Oversold", RSIOversoldStrategy),
        ("Trend Following", TrendFollowingStrategy),
        ("Bollinger Bands", BollingerBandsStrategy),
        ("MACD Crossover", MACDCrossoverStrategy),
        ("Multi-Indicator", MultiIndicatorStrategy)
    ]

    # Run all backtests
    results = []
    for name, strategy_class in strategies:
        cprint(f"\n🚀 Testing {name}...", "white")

        bt = Backtest(
            data,
            strategy_class,
            cash=100000,
            commission=0.002,
            exclusive_orders=True
        )

        stats = bt.run()
        results.append((name, stats))

        # Quick summary
        total_return = stats.get("Return [%]", 0)
        sharpe = stats.get("Sharpe Ratio", 0)
        trades = stats.get("# Trades", 0)
        cprint(f"   Return: {total_return:.2f}% | Sharpe: {sharpe:.2f} | Trades: {trades}", "cyan")

    # Compare all strategies
    cprint("\n" + "=" * 70, "yellow")
    stats_list = [stat for _, stat in results]
    strategy_names = [name for name, _ in results]

    comparison_df = compare_strategies(stats_list, strategy_names)
    print_comparison(comparison_df)

    return comparison_df


def run_parameter_optimization():
    """Example: Optimize strategy parameters"""

    cprint("\n" + "=" * 70, "cyan")
    cprint("🌙 EXAMPLE 3: Parameter Optimization", "cyan", attrs=["bold"])
    cprint("=" * 70, "cyan")

    # Load data
    cprint("\n📊 Loading data...", "white")
    data = load_moondev_data('BTC-USD', '15m')

    # Create backtest
    bt = Backtest(
        data,
        SMACrossoverStrategy,
        cash=100000,
        commission=0.002,
        exclusive_orders=True
    )

    # Optimize parameters
    cprint("\n🔧 Optimizing SMA periods...", "yellow")
    cprint("   This may take a few minutes...", "yellow")

    stats = bt.optimize(
        fast_period=range(10, 50, 5),      # Test fast MA from 10 to 45
        slow_period=range(30, 100, 10),    # Test slow MA from 30 to 90
        maximize='Sharpe Ratio',            # Optimize for Sharpe Ratio
        constraint=lambda p: p.fast_period < p.slow_period  # Fast must be < Slow
    )

    # Print optimized parameters
    cprint("\n✅ Optimization Complete!", "green", attrs=["bold"])
    cprint(f"\n📈 Best Parameters:", "white", attrs=["bold"])
    cprint(f"   Fast Period: {stats._strategy.fast_period}", "white")
    cprint(f"   Slow Period: {stats._strategy.slow_period}", "white")

    # Analyze optimized results
    metrics = analyze_performance(stats)
    print_metrics(metrics)

    # Optional: Show plot
    # bt.plot()

    return stats


def run_walk_forward_test():
    """Example: Walk-forward analysis (out-of-sample testing)"""

    cprint("\n" + "=" * 70, "cyan")
    cprint("🌙 EXAMPLE 4: Walk-Forward Testing", "cyan", attrs=["bold"])
    cprint("=" * 70, "cyan")

    # Load data
    data = load_moondev_data('BTC-USD', '15m')

    # Split data into train/test
    split_point = int(len(data) * 0.7)  # 70% train, 30% test
    train_data = data.iloc[:split_point]
    test_data = data.iloc[split_point:]

    cprint(f"\n📊 Data split:", "white")
    cprint(f"   Training: {len(train_data)} bars ({train_data.index[0]} to {train_data.index[-1]})", "cyan")
    cprint(f"   Testing:  {len(test_data)} bars ({test_data.index[0]} to {test_data.index[-1]})", "cyan")

    # 1. Optimize on training data
    cprint("\n🔧 Optimizing on training data...", "yellow")
    bt_train = Backtest(train_data, SMACrossoverStrategy, cash=100000, commission=0.002)

    stats_train = bt_train.optimize(
        fast_period=range(10, 50, 10),
        slow_period=range(30, 100, 20),
        maximize='Sharpe Ratio',
        constraint=lambda p: p.fast_period < p.slow_period
    )

    best_fast = stats_train._strategy.fast_period
    best_slow = stats_train._strategy.slow_period

    cprint(f"\n✅ Optimized Parameters: Fast={best_fast}, Slow={best_slow}", "green")

    # 2. Test on out-of-sample data
    cprint("\n🧪 Testing on out-of-sample data...", "yellow")

    # Create strategy with optimized parameters
    class OptimizedSMAStrategy(SMACrossoverStrategy):
        fast_period = best_fast
        slow_period = best_slow

    bt_test = Backtest(test_data, OptimizedSMAStrategy, cash=100000, commission=0.002)
    stats_test = bt_test.run()

    # Compare in-sample vs out-of-sample
    cprint("\n📊 In-Sample vs Out-of-Sample Comparison:", "white", attrs=["bold"])
    cprint("-" * 70, "cyan")
    cprint(f"{'Metric':<25} {'In-Sample':<20} {'Out-of-Sample':<20}", "white", attrs=["bold"])
    cprint("-" * 70, "cyan")

    metrics_to_compare = [
        ("Total Return [%]", "Return [%]"),
        ("Sharpe Ratio", "Sharpe Ratio"),
        ("Max Drawdown [%]", "Max. Drawdown [%]"),
        ("Win Rate [%]", "Win Rate [%]"),
        ("# Trades", "# Trades")
    ]

    for display_name, stat_key in metrics_to_compare:
        in_sample = stats_train.get(stat_key, 0)
        out_of_sample = stats_test.get(stat_key, 0)
        cprint(f"{display_name:<25} {in_sample:<20.2f} {out_of_sample:<20.2f}", "white")

    cprint("-" * 70, "cyan")

    # Overfitting warning
    return_diff = abs(stats_train.get("Return [%]", 0) - stats_test.get("Return [%]", 0))
    if return_diff > 20:
        cprint("\n⚠️  WARNING: Large difference between in-sample and out-of-sample returns!", "red")
        cprint("   This may indicate overfitting. Consider simplifying the strategy.", "yellow")
    else:
        cprint("\n✅ Results are consistent - strategy generalizes well!", "green")

    return stats_train, stats_test


# ============================================================================
# RUN ALL EXAMPLES
# ============================================================================

def main():
    """Run all examples"""

    cprint("\n" + "=" * 70, "magenta")
    cprint("🌙 MOON DEV'S BACKTESTING FRAMEWORK - COMPLETE EXAMPLES", "magenta", attrs=["bold"])
    cprint("=" * 70, "magenta")

    try:
        # Example 1: Single backtest
        run_single_backtest()

        # Example 2: Strategy comparison
        run_strategy_comparison()

        # Example 3: Parameter optimization
        # COMMENTED OUT - can be slow, uncomment to test
        # run_parameter_optimization()

        # Example 4: Walk-forward testing
        # COMMENTED OUT - requires more data, uncomment to test
        # run_walk_forward_test()

        cprint("\n" + "=" * 70, "green")
        cprint("✅ ALL EXAMPLES COMPLETED SUCCESSFULLY!", "green", attrs=["bold"])
        cprint("=" * 70, "green")

        cprint("\n💡 Next Steps:", "cyan")
        cprint("   1. Modify the example strategies to test your own ideas", "white")
        cprint("   2. Uncomment optimization and walk-forward examples", "white")
        cprint("   3. Create your own custom strategies inheriting from MoonDevStrategy", "white")
        cprint("   4. Read BACKTESTING_BEST_PRACTICES.md for advanced tips", "white")

    except FileNotFoundError as e:
        cprint(f"\n❌ Error: {str(e)}", "red")
        cprint("\n💡 Make sure you have the sample data file:", "yellow")
        cprint("   /home/user/moon-dev-ai-agents/src/data/rbi/BTC-USD-15m.csv", "yellow")
        cprint("\n   Or update the data path in backtest_template.py", "yellow")

    except Exception as e:
        cprint(f"\n❌ Unexpected error: {str(e)}", "red")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

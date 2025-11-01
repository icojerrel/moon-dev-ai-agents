"""
🌙 Moon Dev Strategy Templates
===============================
Production-ready trading strategy templates for quick deployment

Available Templates:
-------------------
1. Momentum Strategy - Trend following with momentum confirmation
2. Mean Reversion Strategy - Statistical mean reversion trading
3. Breakout Strategy - Range breakout with volume confirmation
4. Pairs Trading Strategy - Statistical arbitrage between correlated assets
5. Grid Trading Strategy - Range-bound grid accumulation/distribution

Quick Import:
------------
from src.strategies.templates import (
    MomentumStrategy,
    MeanReversionStrategy,
    BreakoutStrategy,
    PairsTradingStrategy,
    GridTradingStrategy
)

Usage:
------
from backtesting import Backtest
from src.strategies.templates import MomentumStrategy
from src.strategies.backtest_template import load_moondev_data

data = load_moondev_data('BTC-USD', '15m')
bt = Backtest(data, MomentumStrategy, cash=100000, commission=0.002)
stats = bt.run()
print(stats)
bt.plot()

See individual template files for detailed documentation and variations.
"""

# Import all strategy classes
from .momentum_template import (
    MomentumStrategy,
    AggressiveMomentumStrategy,
    ConservativeMomentumStrategy,
    ScalpingMomentumStrategy
)

from .mean_reversion_template import (
    MeanReversionStrategy,
    TightMeanReversionStrategy,
    WideMeanReversionStrategy,
    AggressiveMeanReversionStrategy,
    ConservativeMeanReversionStrategy,
    DivergenceMeanReversionStrategy
)

from .breakout_template import (
    BreakoutStrategy,
    AggressiveBreakoutStrategy,
    ConservativeBreakoutStrategy,
    RangeExpansionStrategy
)

from .pairs_trading_template import (
    PairsTradingStrategy,
    AggressivePairsTradingStrategy,
    ConservativePairsTradingStrategy,
    CorrelationFilteredPairsTradingStrategy,
    merge_pair_data,
    calculate_correlation
)

from .grid_trading_template import (
    GridTradingStrategy,
    TightGridStrategy,
    WideGridStrategy,
    TrailingGridStrategy,
    RangeDetectionGridStrategy
)

__all__ = [
    # Momentum strategies
    'MomentumStrategy',
    'AggressiveMomentumStrategy',
    'ConservativeMomentumStrategy',
    'ScalpingMomentumStrategy',

    # Mean reversion strategies
    'MeanReversionStrategy',
    'TightMeanReversionStrategy',
    'WideMeanReversionStrategy',
    'AggressiveMeanReversionStrategy',
    'ConservativeMeanReversionStrategy',
    'DivergenceMeanReversionStrategy',

    # Breakout strategies
    'BreakoutStrategy',
    'AggressiveBreakoutStrategy',
    'ConservativeBreakoutStrategy',
    'RangeExpansionStrategy',

    # Pairs trading strategies
    'PairsTradingStrategy',
    'AggressivePairsTradingStrategy',
    'ConservativePairsTradingStrategy',
    'CorrelationFilteredPairsTradingStrategy',
    'merge_pair_data',
    'calculate_correlation',

    # Grid trading strategies
    'GridTradingStrategy',
    'TightGridStrategy',
    'WideGridStrategy',
    'TrailingGridStrategy',
    'RangeDetectionGridStrategy',
]

# Version info
__version__ = '1.0.0'
__author__ = 'Moon Dev'
__description__ = 'Production-ready trading strategy templates'

#!/usr/bin/env python3
"""
🌙 Moon Dev's Market Regime Detection Module 🌙

Identifies market regimes (trending, mean-reverting, high/low volatility) to enable
adaptive strategy selection. Different trading strategies perform better in different
market conditions - this module helps detect which regime we're in.

Regime Types:
-----------
1. TRENDING (Bullish/Bearish) - Strong directional movement
   - Best for: Trend following, momentum strategies
   - Indicators: High ADX, consistent returns direction

2. MEAN_REVERTING (Range-bound) - Sideways, oscillating price
   - Best for: Mean reversion, range trading
   - Indicators: Low ADX, price oscillates around moving average

3. HIGH_VOLATILITY (Chaotic) - Large price swings
   - Best for: Reduce position sizing, protective stops
   - Indicators: High standard deviation of returns

4. LOW_VOLATILITY (Calm) - Stable, predictable movement
   - Best for: Increase position sizing, tighter stops
   - Indicators: Low standard deviation of returns

Methods Implemented:
------------------
- Volatility-based regimes (rolling standard deviation)
- Trend strength detection (ADX-style calculation)
- Returns distribution analysis
- Regime transition detection
- Regime probability scoring

Built with love by Moon Dev 🚀
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
from typing import Dict, Tuple, List, Optional
from enum import Enum
from dataclasses import dataclass
from termcolor import colored, cprint

# Project setup
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))


class RegimeType(Enum):
    """Market regime types"""
    TRENDING_BULLISH = "trending_bullish"
    TRENDING_BEARISH = "trending_bearish"
    MEAN_REVERTING = "mean_reverting"
    HIGH_VOLATILITY = "high_volatility"
    LOW_VOLATILITY = "low_volatility"
    UNKNOWN = "unknown"


@dataclass
class RegimeSignal:
    """Regime detection signal with confidence"""
    regime: RegimeType
    confidence: float  # 0.0 to 1.0
    trend_strength: float  # -1.0 (strong bear) to 1.0 (strong bull)
    volatility_percentile: float  # 0.0 to 1.0
    mean_reversion_score: float  # 0.0 (trending) to 1.0 (mean reverting)
    metadata: Dict[str, float]


class RegimeDetector:
    """
    Market regime detection using multiple statistical methods.

    Usage:
        detector = RegimeDetector(lookback_period=50)
        regime = detector.detect_regime(price_series)

        if regime.regime == RegimeType.TRENDING_BULLISH:
            # Use trend-following strategy
        elif regime.regime == RegimeType.MEAN_REVERTING:
            # Use mean reversion strategy
    """

    def __init__(
        self,
        lookback_period: int = 50,
        volatility_threshold: float = 0.02,  # 2% daily volatility threshold
        trend_threshold: float = 0.3,  # ADX-style threshold for trend strength
        mean_reversion_threshold: float = 0.6  # Threshold for mean reversion detection
    ):
        """
        Initialize regime detector.

        Args:
            lookback_period: Number of periods to analyze (default 50)
            volatility_threshold: Daily volatility threshold for high/low regimes
            trend_threshold: Minimum trend strength for trending regime
            mean_reversion_threshold: Threshold for mean reversion classification
        """
        self.lookback_period = lookback_period
        self.volatility_threshold = volatility_threshold
        self.trend_threshold = trend_threshold
        self.mean_reversion_threshold = mean_reversion_threshold

    def detect_regime(
        self,
        prices: pd.Series,
        high: Optional[pd.Series] = None,
        low: Optional[pd.Series] = None
    ) -> RegimeSignal:
        """
        Detect current market regime from price data.

        Args:
            prices: Pandas Series of closing prices
            high: Optional Series of high prices (for better trend detection)
            low: Optional Series of low prices (for better trend detection)

        Returns:
            RegimeSignal with detected regime and confidence metrics
        """
        if len(prices) < self.lookback_period:
            return RegimeSignal(
                regime=RegimeType.UNKNOWN,
                confidence=0.0,
                trend_strength=0.0,
                volatility_percentile=0.5,
                mean_reversion_score=0.5,
                metadata={"error": "Insufficient data"}
            )

        # Calculate returns
        returns = prices.pct_change().dropna()

        # 1. Volatility Analysis
        vol_regime, vol_percentile = self._detect_volatility_regime(returns)

        # 2. Trend Analysis (ADX-style)
        trend_strength, trend_direction = self._calculate_trend_strength(
            prices, high, low
        )

        # 3. Mean Reversion Analysis
        mean_reversion_score = self._calculate_mean_reversion_score(prices)

        # 4. Combine signals to determine primary regime
        regime, confidence = self._combine_regime_signals(
            vol_regime=vol_regime,
            trend_strength=trend_strength,
            trend_direction=trend_direction,
            mean_reversion_score=mean_reversion_score
        )

        # Metadata for debugging/analysis
        metadata = {
            "volatility": returns.tail(20).std(),
            "volatility_percentile": vol_percentile,
            "trend_strength": trend_strength,
            "mean_reversion_score": mean_reversion_score,
            "avg_return": returns.tail(self.lookback_period).mean(),
            "sharpe_estimate": self._calculate_rolling_sharpe(returns)
        }

        return RegimeSignal(
            regime=regime,
            confidence=confidence,
            trend_strength=trend_strength * trend_direction,
            volatility_percentile=vol_percentile,
            mean_reversion_score=mean_reversion_score,
            metadata=metadata
        )

    def _detect_volatility_regime(
        self,
        returns: pd.Series
    ) -> Tuple[str, float]:
        """
        Detect if we're in high or low volatility regime.

        Returns:
            Tuple of (regime_string, volatility_percentile)
        """
        # Calculate rolling volatility
        rolling_vol = returns.rolling(window=20).std()
        current_vol = rolling_vol.iloc[-1]

        # Calculate percentile relative to lookback period
        historical_vol = rolling_vol.tail(self.lookback_period)
        percentile = (historical_vol < current_vol).sum() / len(historical_vol)

        if percentile > 0.8:
            return "high_volatility", percentile
        elif percentile < 0.2:
            return "low_volatility", percentile
        else:
            return "normal_volatility", percentile

    def _calculate_trend_strength(
        self,
        prices: pd.Series,
        high: Optional[pd.Series] = None,
        low: Optional[pd.Series] = None
    ) -> Tuple[float, int]:
        """
        Calculate trend strength using ADX-inspired methodology.

        Returns:
            Tuple of (strength: 0.0-1.0, direction: 1 for bull, -1 for bear)
        """
        # Use simple moving average crossover if high/low not available
        if high is None or low is None:
            return self._simple_trend_strength(prices)

        # Calculate True Range components
        tr1 = high - low
        tr2 = abs(high - prices.shift(1))
        tr3 = abs(low - prices.shift(1))
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        # Calculate directional movement
        up_move = high - high.shift(1)
        down_move = low.shift(1) - low

        pos_dm = pd.Series(0.0, index=prices.index)
        neg_dm = pd.Series(0.0, index=prices.index)

        pos_dm[(up_move > down_move) & (up_move > 0)] = up_move
        neg_dm[(down_move > up_move) & (down_move > 0)] = down_move

        # Smooth with EMA
        period = 14
        atr = true_range.ewm(span=period, adjust=False).mean()
        pos_di = 100 * (pos_dm.ewm(span=period, adjust=False).mean() / atr)
        neg_di = 100 * (neg_dm.ewm(span=period, adjust=False).mean() / atr)

        # Calculate ADX (trend strength)
        dx = 100 * abs(pos_di - neg_di) / (pos_di + neg_di)
        adx = dx.ewm(span=period, adjust=False).mean()

        # Normalize to 0-1 range (ADX typically 0-100)
        trend_strength = min(adx.iloc[-1] / 50.0, 1.0)  # 50+ ADX is very strong

        # Determine direction (1 for bull, -1 for bear)
        direction = 1 if pos_di.iloc[-1] > neg_di.iloc[-1] else -1

        return trend_strength, direction

    def _simple_trend_strength(self, prices: pd.Series) -> Tuple[float, int]:
        """
        Simple trend strength using moving average slopes.
        Fallback when high/low data not available.
        """
        # Calculate multiple moving averages
        ma_fast = prices.rolling(window=10).mean()
        ma_slow = prices.rolling(window=30).mean()

        # Trend direction
        direction = 1 if ma_fast.iloc[-1] > ma_slow.iloc[-1] else -1

        # Trend strength based on MA separation
        separation = abs(ma_fast.iloc[-1] - ma_slow.iloc[-1]) / ma_slow.iloc[-1]
        trend_strength = min(separation * 20, 1.0)  # Scale to 0-1

        # Also check slope consistency
        ma_slope = ma_fast.tail(10).diff().mean()
        slope_strength = min(abs(ma_slope) / prices.iloc[-1] * 100, 1.0)

        # Combine separation and slope
        combined_strength = (trend_strength + slope_strength) / 2

        return combined_strength, direction

    def _calculate_mean_reversion_score(self, prices: pd.Series) -> float:
        """
        Calculate how mean-reverting the price action is.

        Score close to 1.0 = strong mean reversion
        Score close to 0.0 = strong trending
        """
        # Calculate deviations from moving average
        ma = prices.rolling(window=20).mean()
        deviations = (prices - ma) / ma

        # Check how often price crosses the MA
        crossings = (deviations * deviations.shift(1) < 0).tail(self.lookback_period)
        crossing_rate = crossings.sum() / len(crossings)

        # Check autocorrelation of returns (negative = mean reverting)
        returns = prices.pct_change().dropna()
        if len(returns) > 1:
            autocorr = returns.tail(self.lookback_period).autocorr(lag=1)
            # Convert to 0-1 scale (negative autocorr = mean reverting)
            autocorr_score = max(0, -autocorr)
        else:
            autocorr_score = 0.5

        # Combine crossing rate and autocorrelation
        mean_reversion_score = (crossing_rate + autocorr_score) / 2

        return mean_reversion_score

    def _combine_regime_signals(
        self,
        vol_regime: str,
        trend_strength: float,
        trend_direction: int,
        mean_reversion_score: float
    ) -> Tuple[RegimeType, float]:
        """
        Combine all signals to determine primary regime with confidence.

        Returns:
            Tuple of (RegimeType, confidence: 0.0-1.0)
        """
        # Priority 1: Strong volatility regimes
        if vol_regime == "high_volatility":
            return RegimeType.HIGH_VOLATILITY, 0.8
        elif vol_regime == "low_volatility":
            return RegimeType.LOW_VOLATILITY, 0.8

        # Priority 2: Check for trending regime
        if trend_strength > self.trend_threshold:
            if trend_direction > 0:
                regime = RegimeType.TRENDING_BULLISH
            else:
                regime = RegimeType.TRENDING_BEARISH
            confidence = trend_strength  # Higher trend strength = higher confidence
            return regime, confidence

        # Priority 3: Check for mean reversion
        if mean_reversion_score > self.mean_reversion_threshold:
            return RegimeType.MEAN_REVERTING, mean_reversion_score

        # Default: Unknown/mixed regime
        return RegimeType.UNKNOWN, 0.5

    def _calculate_rolling_sharpe(self, returns: pd.Series, window: int = 20) -> float:
        """Calculate rolling Sharpe ratio estimate"""
        if len(returns) < window:
            return 0.0

        rolling_returns = returns.tail(window)
        mean_return = rolling_returns.mean()
        std_return = rolling_returns.std()

        if std_return == 0:
            return 0.0

        # Annualized Sharpe (assuming daily data, 252 trading days)
        sharpe = (mean_return / std_return) * np.sqrt(252)
        return sharpe

    def get_regime_recommendations(self, regime: RegimeSignal) -> Dict[str, str]:
        """
        Get trading recommendations based on detected regime.

        Returns:
            Dictionary with strategy recommendations
        """
        recommendations = {
            "regime": regime.regime.value,
            "confidence": f"{regime.confidence:.2f}",
            "strategy": "",
            "position_sizing": "",
            "stop_loss": "",
            "notes": ""
        }

        if regime.regime == RegimeType.TRENDING_BULLISH:
            recommendations.update({
                "strategy": "Trend following, momentum strategies",
                "position_sizing": "Normal to aggressive (use Kelly Criterion)",
                "stop_loss": "Wider stops (trailing stops work well)",
                "notes": "Follow the trend, don't fight it"
            })
        elif regime.regime == RegimeType.TRENDING_BEARISH:
            recommendations.update({
                "strategy": "Short-selling, inverse strategies, or stay cash",
                "position_sizing": "Conservative (reduce exposure)",
                "stop_loss": "Tight stops on longs, wider on shorts",
                "notes": "Bearish regime - protect capital first"
            })
        elif regime.regime == RegimeType.MEAN_REVERTING:
            recommendations.update({
                "strategy": "Mean reversion, range trading, pairs trading",
                "position_sizing": "Normal (use fixed fraction)",
                "stop_loss": "Tight stops at support/resistance",
                "notes": "Buy support, sell resistance"
            })
        elif regime.regime == RegimeType.HIGH_VOLATILITY:
            recommendations.update({
                "strategy": "Reduce activity, options strategies",
                "position_sizing": "Very conservative (half normal size)",
                "stop_loss": "Wider stops to avoid whipsaws",
                "notes": "High volatility = high risk, reduce exposure"
            })
        elif regime.regime == RegimeType.LOW_VOLATILITY:
            recommendations.update({
                "strategy": "Any strategy works, good for testing",
                "position_sizing": "Can be slightly aggressive",
                "stop_loss": "Tighter stops (less noise)",
                "notes": "Stable conditions, good for execution"
            })
        else:
            recommendations.update({
                "strategy": "Wait for clearer regime signal",
                "position_sizing": "Conservative",
                "stop_loss": "Standard stops",
                "notes": "Mixed signals - be cautious"
            })

        return recommendations


def print_regime_analysis(regime: RegimeSignal, prices: pd.Series):
    """Pretty print regime analysis to console"""
    cprint("\n" + "="*60, "cyan")
    cprint("🌙 MARKET REGIME ANALYSIS 🌙", "cyan", attrs=["bold"])
    cprint("="*60, "cyan")

    # Regime type with color
    regime_colors = {
        RegimeType.TRENDING_BULLISH: "green",
        RegimeType.TRENDING_BEARISH: "red",
        RegimeType.MEAN_REVERTING: "yellow",
        RegimeType.HIGH_VOLATILITY: "magenta",
        RegimeType.LOW_VOLATILITY: "blue",
        RegimeType.UNKNOWN: "white"
    }

    color = regime_colors.get(regime.regime, "white")
    cprint(f"\n📊 Current Regime: {regime.regime.value.upper()}", color, attrs=["bold"])
    cprint(f"🎯 Confidence: {regime.confidence:.1%}", color)

    # Metrics
    print(colored(f"\n📈 Trend Strength: ", "white") +
          colored(f"{regime.trend_strength:+.2f}", "green" if regime.trend_strength > 0 else "red"))
    print(colored(f"📉 Volatility Percentile: ", "white") +
          colored(f"{regime.volatility_percentile:.1%}", "yellow"))
    print(colored(f"🔄 Mean Reversion Score: ", "white") +
          colored(f"{regime.mean_reversion_score:.1%}", "cyan"))

    # Metadata
    if regime.metadata:
        cprint("\n📋 Additional Metrics:", "white", attrs=["bold"])
        for key, value in regime.metadata.items():
            if key != "error":
                print(f"   {key}: {value:.4f}")

    # Recommendations
    detector = RegimeDetector()
    recs = detector.get_regime_recommendations(regime)

    cprint("\n💡 TRADING RECOMMENDATIONS:", "cyan", attrs=["bold"])
    print(colored(f"   Strategy: ", "white") + colored(recs["strategy"], "yellow"))
    print(colored(f"   Position Sizing: ", "white") + colored(recs["position_sizing"], "yellow"))
    print(colored(f"   Stop Loss: ", "white") + colored(recs["stop_loss"], "yellow"))
    print(colored(f"   Notes: ", "white") + colored(recs["notes"], "green"))

    cprint("\n" + "="*60 + "\n", "cyan")


# ============================================
# 🧪 TESTING & EXAMPLES
# ============================================

if __name__ == "__main__":
    cprint("\n🧪 Testing Regime Detection Module\n", "cyan", attrs=["bold"])

    # Generate synthetic test data
    np.random.seed(42)
    dates = pd.date_range(start="2024-01-01", periods=200, freq="D")

    # Example 1: Trending Bullish Market
    cprint("=" * 60, "green")
    cprint("Example 1: TRENDING BULLISH MARKET", "green", attrs=["bold"])
    cprint("=" * 60, "green")

    trend = np.linspace(100, 150, 200)
    noise = np.random.normal(0, 2, 200)
    trending_prices = pd.Series(trend + noise, index=dates)

    detector = RegimeDetector(lookback_period=50)
    regime1 = detector.detect_regime(trending_prices)
    print_regime_analysis(regime1, trending_prices)

    # Example 2: Mean Reverting Market
    cprint("=" * 60, "yellow")
    cprint("Example 2: MEAN REVERTING MARKET", "yellow", attrs=["bold"])
    cprint("=" * 60, "yellow")

    mean_price = 100
    mean_rev = mean_price + 10 * np.sin(np.linspace(0, 10*np.pi, 200))
    noise = np.random.normal(0, 1, 200)
    mr_prices = pd.Series(mean_rev + noise, index=dates)

    regime2 = detector.detect_regime(mr_prices)
    print_regime_analysis(regime2, mr_prices)

    # Example 3: High Volatility Market
    cprint("=" * 60, "magenta")
    cprint("Example 3: HIGH VOLATILITY MARKET", "magenta", attrs=["bold"])
    cprint("=" * 60, "magenta")

    base = np.linspace(100, 105, 200)
    high_vol_noise = np.random.normal(0, 8, 200)  # High volatility
    hv_prices = pd.Series(base + high_vol_noise, index=dates)

    regime3 = detector.detect_regime(hv_prices)
    print_regime_analysis(regime3, hv_prices)

    cprint("✅ All regime detection tests completed!\n", "green", attrs=["bold"])

    # Usage example
    cprint("=" * 60, "cyan")
    cprint("📚 USAGE EXAMPLE", "cyan", attrs=["bold"])
    cprint("=" * 60, "cyan")
    print("""
# In your trading agent:
from src.utils.regime_detection import RegimeDetector, RegimeType

# Initialize detector
detector = RegimeDetector(lookback_period=50)

# Get current prices (from your data source)
prices = get_ohlcv_data(token_address)['close']

# Detect regime
regime = detector.detect_regime(prices)

# Adapt strategy based on regime
if regime.regime == RegimeType.TRENDING_BULLISH and regime.confidence > 0.7:
    # Use trend-following strategy
    strategy = "momentum"
    position_size = kelly_criterion(...)  # Aggressive sizing

elif regime.regime == RegimeType.MEAN_REVERTING and regime.confidence > 0.7:
    # Use mean reversion strategy
    strategy = "mean_reversion"
    position_size = fixed_fraction(...)  # Conservative sizing

elif regime.regime == RegimeType.HIGH_VOLATILITY:
    # Reduce exposure
    position_size = position_size * 0.5  # Half normal size

else:
    # Mixed signals - be cautious
    pass
    """)

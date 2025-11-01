"""
🌙 Moon Dev's Backtesting Performance Metrics
============================================
Comprehensive performance analysis tools for backtesting results

Includes:
- Risk-adjusted returns (Sharpe, Sortino, Calmar)
- Drawdown analysis
- Win rate and profit factor
- Trade statistics
- Custom Moon Dev metrics

Usage:
    from backtest_metrics import analyze_performance, compare_strategies

    # Analyze single strategy
    metrics = analyze_performance(stats)
    print_metrics(metrics)

    # Compare multiple strategies
    comparison = compare_strategies([stats1, stats2, stats3])
    print_comparison(comparison)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union
from termcolor import cprint
from datetime import datetime


# ============================================================================
# CORE PERFORMANCE METRICS
# ============================================================================

def calculate_sharpe_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.02,
    periods_per_year: int = 252
) -> float:
    """
    Calculate annualized Sharpe Ratio

    Args:
        returns: Series of returns
        risk_free_rate: Annual risk-free rate (default: 2%)
        periods_per_year: Trading periods per year (252 for daily, 8760 for hourly, etc.)

    Returns:
        Sharpe ratio (annualized)
    """
    if len(returns) == 0 or returns.std() == 0:
        return 0.0

    excess_returns = returns - (risk_free_rate / periods_per_year)
    sharpe = excess_returns.mean() / returns.std()
    return sharpe * np.sqrt(periods_per_year)


def calculate_sortino_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.02,
    periods_per_year: int = 252
) -> float:
    """
    Calculate annualized Sortino Ratio (downside deviation only)

    Args:
        returns: Series of returns
        risk_free_rate: Annual risk-free rate (default: 2%)
        periods_per_year: Trading periods per year

    Returns:
        Sortino ratio (annualized)
    """
    if len(returns) == 0:
        return 0.0

    excess_returns = returns - (risk_free_rate / periods_per_year)
    downside_returns = returns[returns < 0]

    if len(downside_returns) == 0 or downside_returns.std() == 0:
        return 0.0

    sortino = excess_returns.mean() / downside_returns.std()
    return sortino * np.sqrt(periods_per_year)


def calculate_calmar_ratio(
    total_return: float,
    max_drawdown: float,
    years: float
) -> float:
    """
    Calculate Calmar Ratio (return / max drawdown)

    Args:
        total_return: Total return (e.g., 0.25 for 25%)
        max_drawdown: Maximum drawdown (e.g., -0.15 for -15%)
        years: Number of years in backtest

    Returns:
        Calmar ratio
    """
    if max_drawdown == 0:
        return 0.0

    annualized_return = (1 + total_return) ** (1 / years) - 1
    return annualized_return / abs(max_drawdown)


def calculate_win_rate(trades: pd.DataFrame) -> float:
    """
    Calculate win rate from trades

    Args:
        trades: DataFrame with trade results

    Returns:
        Win rate (0.0 to 1.0)
    """
    if len(trades) == 0:
        return 0.0

    winning_trades = len(trades[trades['PnL'] > 0])
    return winning_trades / len(trades)


def calculate_profit_factor(trades: pd.DataFrame) -> float:
    """
    Calculate profit factor (gross profit / gross loss)

    Args:
        trades: DataFrame with trade results

    Returns:
        Profit factor
    """
    if len(trades) == 0:
        return 0.0

    gross_profit = trades[trades['PnL'] > 0]['PnL'].sum()
    gross_loss = abs(trades[trades['PnL'] < 0]['PnL'].sum())

    if gross_loss == 0:
        return float('inf') if gross_profit > 0 else 0.0

    return gross_profit / gross_loss


def calculate_max_consecutive_losses(trades: pd.DataFrame) -> int:
    """Calculate maximum consecutive losing trades"""
    if len(trades) == 0:
        return 0

    losses = (trades['PnL'] < 0).astype(int)
    consecutive = 0
    max_consecutive = 0

    for is_loss in losses:
        if is_loss:
            consecutive += 1
            max_consecutive = max(max_consecutive, consecutive)
        else:
            consecutive = 0

    return max_consecutive


def calculate_recovery_factor(total_return: float, max_drawdown: float) -> float:
    """
    Calculate recovery factor (total return / max drawdown)

    Args:
        total_return: Total return (e.g., 0.25 for 25%)
        max_drawdown: Maximum drawdown (e.g., -0.15 for -15%)

    Returns:
        Recovery factor
    """
    if max_drawdown == 0:
        return 0.0

    return total_return / abs(max_drawdown)


# ============================================================================
# COMPREHENSIVE PERFORMANCE ANALYSIS
# ============================================================================

def analyze_performance(
    stats: Union[pd.Series, Dict],
    equity_curve: Optional[pd.Series] = None,
    trades: Optional[pd.DataFrame] = None
) -> Dict:
    """
    Comprehensive performance analysis from backtest results

    Args:
        stats: Backtest statistics (from bt.run())
        equity_curve: Optional equity curve for additional metrics
        trades: Optional trades DataFrame

    Returns:
        Dictionary with comprehensive metrics
    """
    # Convert stats to dict if it's a Series
    if isinstance(stats, pd.Series):
        stats_dict = stats.to_dict()
    else:
        stats_dict = stats

    metrics = {
        "strategy": stats_dict.get("_strategy", "Unknown"),
        "start_date": stats_dict.get("Start", None),
        "end_date": stats_dict.get("End", None),

        # Return Metrics
        "total_return_pct": stats_dict.get("Return [%]", 0),
        "annual_return_pct": stats_dict.get("Return (Ann.) [%]", 0),
        "buy_hold_return_pct": stats_dict.get("Buy & Hold Return [%]", 0),

        # Risk Metrics
        "volatility_pct": stats_dict.get("Volatility (Ann.) [%]", 0),
        "max_drawdown_pct": stats_dict.get("Max. Drawdown [%]", 0),
        "max_drawdown_duration": stats_dict.get("Max. Drawdown Duration", None),

        # Risk-Adjusted Returns
        "sharpe_ratio": stats_dict.get("Sharpe Ratio", 0),
        "sortino_ratio": stats_dict.get("Sortino Ratio", 0),
        "calmar_ratio": stats_dict.get("Calmar Ratio", 0),

        # Trade Statistics
        "num_trades": stats_dict.get("# Trades", 0),
        "win_rate_pct": stats_dict.get("Win Rate [%]", 0),
        "best_trade_pct": stats_dict.get("Best Trade [%]", 0),
        "worst_trade_pct": stats_dict.get("Worst Trade [%]", 0),
        "avg_trade_pct": stats_dict.get("Avg. Trade [%]", 0),

        # Exposure
        "exposure_time_pct": stats_dict.get("Exposure Time [%]", 0),

        # Equity Stats
        "equity_final": stats_dict.get("Equity Final [$]", 0),
        "equity_peak": stats_dict.get("Equity Peak [$]", 0),
    }

    # Calculate additional metrics if trades available
    if trades is not None and len(trades) > 0:
        metrics["profit_factor"] = calculate_profit_factor(trades)
        metrics["max_consecutive_losses"] = calculate_max_consecutive_losses(trades)
        metrics["avg_win_pct"] = trades[trades['PnL'] > 0]['ReturnPct'].mean() if 'ReturnPct' in trades.columns else 0
        metrics["avg_loss_pct"] = trades[trades['PnL'] < 0]['ReturnPct'].mean() if 'ReturnPct' in trades.columns else 0

    # Calculate recovery factor
    if metrics["max_drawdown_pct"] != 0:
        metrics["recovery_factor"] = calculate_recovery_factor(
            metrics["total_return_pct"] / 100,
            metrics["max_drawdown_pct"] / 100
        )
    else:
        metrics["recovery_factor"] = 0.0

    # Moon Dev Quality Score (0-100)
    metrics["moondev_score"] = calculate_moondev_score(metrics)

    return metrics


def calculate_moondev_score(metrics: Dict) -> float:
    """
    Calculate Moon Dev's proprietary quality score (0-100)

    Scoring factors:
    - Total return: 30 points
    - Sharpe ratio: 20 points
    - Win rate: 15 points
    - Max drawdown: 15 points
    - Profit factor: 10 points
    - Recovery factor: 10 points

    Args:
        metrics: Dictionary of performance metrics

    Returns:
        Score from 0 to 100
    """
    score = 0.0

    # Total return (30 points max)
    # 100% return = 30 points, scaled linearly
    total_return = metrics.get("total_return_pct", 0) / 100
    score += min(total_return * 30, 30)

    # Sharpe ratio (20 points max)
    # Sharpe > 2.0 = 20 points
    sharpe = metrics.get("sharpe_ratio", 0)
    score += min(sharpe * 10, 20)

    # Win rate (15 points max)
    # 70%+ win rate = 15 points
    win_rate = metrics.get("win_rate_pct", 0) / 100
    if win_rate >= 0.70:
        score += 15
    else:
        score += win_rate * 21.43  # Scale to 15 points at 70%

    # Max drawdown (15 points max)
    # Less than 5% DD = 15 points, >50% DD = 0 points
    max_dd = abs(metrics.get("max_drawdown_pct", 50))
    if max_dd <= 5:
        score += 15
    elif max_dd <= 50:
        score += 15 * (1 - (max_dd - 5) / 45)

    # Profit factor (10 points max)
    # PF > 2.0 = 10 points
    pf = metrics.get("profit_factor", 0)
    score += min(pf * 5, 10)

    # Recovery factor (10 points max)
    # RF > 3.0 = 10 points
    rf = metrics.get("recovery_factor", 0)
    score += min(rf * 3.33, 10)

    return min(score, 100)  # Cap at 100


# ============================================================================
# COMPARISON & REPORTING
# ============================================================================

def compare_strategies(
    stats_list: List[Union[pd.Series, Dict]],
    strategy_names: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Compare multiple strategies side-by-side

    Args:
        stats_list: List of backtest statistics
        strategy_names: Optional list of strategy names

    Returns:
        DataFrame with comparison of all strategies
    """
    metrics_list = []

    for i, stats in enumerate(stats_list):
        metrics = analyze_performance(stats)

        if strategy_names and i < len(strategy_names):
            metrics["strategy"] = strategy_names[i]

        metrics_list.append(metrics)

    # Create comparison DataFrame
    comparison_df = pd.DataFrame(metrics_list)

    # Sort by MoonDev score (descending)
    comparison_df = comparison_df.sort_values("moondev_score", ascending=False)

    return comparison_df


def print_metrics(metrics: Dict, detailed: bool = True):
    """
    Pretty print performance metrics

    Args:
        metrics: Performance metrics dictionary
        detailed: Show all metrics or just summary
    """
    cprint("\n" + "=" * 70, "cyan")
    cprint(f"🌙 STRATEGY: {metrics['strategy']}", "cyan", attrs=["bold"])
    cprint("=" * 70, "cyan")

    # Moon Dev Score
    score = metrics.get("moondev_score", 0)
    score_color = "green" if score >= 70 else "yellow" if score >= 50 else "red"
    cprint(f"\n⭐ MOON DEV SCORE: {score:.1f}/100", score_color, attrs=["bold"])

    # Return Metrics
    cprint("\n📈 RETURNS:", "white", attrs=["bold"])
    cprint(f"   Total Return:        {metrics['total_return_pct']:>8.2f}%", "white")
    cprint(f"   Annual Return:       {metrics['annual_return_pct']:>8.2f}%", "white")
    cprint(f"   Buy & Hold Return:   {metrics['buy_hold_return_pct']:>8.2f}%", "white")

    # Risk Metrics
    cprint("\n📊 RISK:", "white", attrs=["bold"])
    cprint(f"   Max Drawdown:        {metrics['max_drawdown_pct']:>8.2f}%", "red")
    cprint(f"   Volatility (Annual): {metrics['volatility_pct']:>8.2f}%", "white")

    # Risk-Adjusted
    cprint("\n🎯 RISK-ADJUSTED:", "white", attrs=["bold"])
    cprint(f"   Sharpe Ratio:        {metrics['sharpe_ratio']:>8.2f}", "white")
    cprint(f"   Sortino Ratio:       {metrics['sortino_ratio']:>8.2f}", "white")
    cprint(f"   Calmar Ratio:        {metrics['calmar_ratio']:>8.2f}", "white")
    cprint(f"   Recovery Factor:     {metrics['recovery_factor']:>8.2f}", "white")

    # Trade Stats
    cprint("\n💼 TRADING:", "white", attrs=["bold"])
    cprint(f"   Number of Trades:    {metrics['num_trades']:>8.0f}", "white")
    cprint(f"   Win Rate:            {metrics['win_rate_pct']:>8.2f}%", "green")
    cprint(f"   Avg Trade:           {metrics['avg_trade_pct']:>8.2f}%", "white")

    if detailed and "profit_factor" in metrics:
        cprint(f"   Profit Factor:       {metrics['profit_factor']:>8.2f}", "white")
        cprint(f"   Max Consecutive Loss:{metrics.get('max_consecutive_losses', 0):>8.0f}", "white")

    # Exposure
    cprint(f"\n⏱️  Exposure Time:       {metrics['exposure_time_pct']:>8.2f}%", "cyan")

    cprint("=" * 70, "cyan")


def print_comparison(comparison_df: pd.DataFrame):
    """
    Print strategy comparison table

    Args:
        comparison_df: DataFrame from compare_strategies()
    """
    cprint("\n" + "=" * 100, "cyan")
    cprint("🏆 STRATEGY COMPARISON (Ranked by Moon Dev Score)", "cyan", attrs=["bold"])
    cprint("=" * 100, "cyan")

    # Select key columns for comparison
    columns_to_show = [
        "strategy",
        "moondev_score",
        "total_return_pct",
        "sharpe_ratio",
        "max_drawdown_pct",
        "win_rate_pct",
        "num_trades"
    ]

    # Filter columns that exist
    columns_to_show = [col for col in columns_to_show if col in comparison_df.columns]

    # Create display DataFrame
    display_df = comparison_df[columns_to_show].copy()

    # Rename columns for display
    display_df.columns = [
        "Strategy",
        "MD Score",
        "Return %",
        "Sharpe",
        "Max DD %",
        "Win Rate %",
        "# Trades"
    ]

    # Format numbers
    display_df = display_df.round(2)

    print(display_df.to_string(index=False))
    cprint("=" * 100, "cyan")

    # Highlight best strategy
    best = display_df.iloc[0]
    cprint(f"\n🥇 BEST STRATEGY: {best['Strategy']} (Score: {best['MD Score']:.1f})", "green", attrs=["bold"])


# ============================================================================
# EXPORT & REPORTING
# ============================================================================

def export_metrics_to_csv(metrics: Dict, filepath: str):
    """Export metrics to CSV file"""
    df = pd.DataFrame([metrics])
    df.to_csv(filepath, index=False)
    cprint(f"✅ Metrics exported to {filepath}", "green")


def export_comparison_to_csv(comparison_df: pd.DataFrame, filepath: str):
    """Export strategy comparison to CSV"""
    comparison_df.to_csv(filepath, index=False)
    cprint(f"✅ Comparison exported to {filepath}", "green")


# ============================================================================
# MAIN (EXAMPLE)
# ============================================================================

if __name__ == "__main__":
    """
    Example usage of metrics module
    """

    # Example backtest stats (from backtesting.py)
    example_stats = {
        "_strategy": "SMA Crossover",
        "Start": "2023-01-01",
        "End": "2024-01-01",
        "Return [%]": 45.5,
        "Return (Ann.) [%]": 45.5,
        "Buy & Hold Return [%]": 32.1,
        "Volatility (Ann.) [%]": 22.3,
        "Max. Drawdown [%]": -12.5,
        "Sharpe Ratio": 1.85,
        "Sortino Ratio": 2.45,
        "Calmar Ratio": 3.64,
        "# Trades": 42,
        "Win Rate [%]": 65.5,
        "Best Trade [%]": 8.2,
        "Worst Trade [%]": -3.5,
        "Avg. Trade [%]": 1.08,
        "Exposure Time [%]": 68.3,
        "Equity Final [$]": 145500,
        "Equity Peak [$]": 152000
    }

    # Analyze performance
    metrics = analyze_performance(example_stats)

    # Print metrics
    print_metrics(metrics)

    cprint("\n✨ Moon Dev's performance analysis complete!", "green", attrs=["bold"])

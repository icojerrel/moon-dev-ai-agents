"""
🌙 Moon Dev's Risk Metrics Module
Advanced risk calculations for position sizing and portfolio management

Includes:
- Volatility-based position sizing
- Correlation analysis between positions
- Kelly Criterion optimal sizing
- Portfolio risk metrics (VaR, CVaR, Sharpe)
- Position concentration limits
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


# ============================================================================
# VOLATILITY CALCULATIONS
# ============================================================================

def calculate_volatility(
    prices: pd.Series,
    window: int = 20,
    annualize: bool = True,
    periods_per_year: int = 35040  # 15-min periods per year
) -> float:
    """
    Calculate historical volatility (standard deviation of returns)

    Args:
        prices: Series of prices
        window: Rolling window for calculation (default: 20 periods)
        annualize: Whether to annualize the volatility (default: True)
        periods_per_year: Trading periods per year for annualization

    Returns:
        Volatility as decimal (e.g., 0.25 = 25%)
    """
    if len(prices) < window:
        return 0.0

    # Calculate returns
    returns = prices.pct_change().dropna()

    if len(returns) < window:
        return 0.0

    # Calculate standard deviation
    volatility = returns.rolling(window=window).std().iloc[-1]

    # Annualize if requested
    if annualize and volatility > 0:
        volatility = volatility * np.sqrt(periods_per_year)

    return volatility if not np.isnan(volatility) else 0.0


def calculate_atr_volatility(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    window: int = 14
) -> float:
    """
    Calculate Average True Range (ATR) as volatility measure

    Args:
        high: Series of high prices
        low: Series of low prices
        close: Series of close prices
        window: ATR period (default: 14)

    Returns:
        ATR value
    """
    if len(close) < window + 1:
        return 0.0

    # Calculate True Range
    high_low = high - low
    high_close = np.abs(high - close.shift())
    low_close = np.abs(low - close.shift())

    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)

    # Calculate ATR
    atr = true_range.rolling(window=window).mean().iloc[-1]

    return atr if not np.isnan(atr) else 0.0


def calculate_parkinson_volatility(
    high: pd.Series,
    low: pd.Series,
    window: int = 20,
    annualize: bool = True,
    periods_per_year: int = 35040
) -> float:
    """
    Parkinson volatility estimator (more efficient than standard volatility)
    Uses high-low range instead of close-to-close

    Args:
        high: Series of high prices
        low: Series of low prices
        window: Rolling window (default: 20)
        annualize: Whether to annualize
        periods_per_year: Periods per year for annualization

    Returns:
        Parkinson volatility
    """
    if len(high) < window:
        return 0.0

    # Calculate log high/low ratio
    log_hl = np.log(high / low)

    # Parkinson estimator
    parkinson = np.sqrt((log_hl ** 2).rolling(window=window).mean() / (4 * np.log(2)))
    volatility = parkinson.iloc[-1]

    # Annualize if requested
    if annualize and volatility > 0:
        volatility = volatility * np.sqrt(periods_per_year)

    return volatility if not np.isnan(volatility) else 0.0


# ============================================================================
# POSITION SIZING
# ============================================================================

def volatility_based_position_size(
    portfolio_value: float,
    target_volatility: float = 0.02,  # 2% daily volatility target
    asset_volatility: float = 0.0,
    max_position_pct: float = 0.20,  # Max 20% of portfolio
    min_position_pct: float = 0.01   # Min 1% of portfolio
) -> float:
    """
    Calculate position size based on volatility targeting

    Formula: Position Size = (Portfolio Value * Target Vol) / Asset Vol

    Args:
        portfolio_value: Total portfolio value in USD
        target_volatility: Target portfolio volatility (default: 2% daily)
        asset_volatility: Asset's historical volatility
        max_position_pct: Maximum position as % of portfolio
        min_position_pct: Minimum position as % of portfolio

    Returns:
        Position size in USD
    """
    if asset_volatility <= 0:
        # If no volatility data, use minimum position
        return portfolio_value * min_position_pct

    # Calculate volatility-adjusted size
    position_size = (portfolio_value * target_volatility) / asset_volatility

    # Apply portfolio percentage limits
    max_size = portfolio_value * max_position_pct
    min_size = portfolio_value * min_position_pct

    # Clamp to limits
    position_size = max(min_size, min(position_size, max_size))

    return position_size


def kelly_criterion_position_size(
    win_rate: float,
    avg_win: float,
    avg_loss: float,
    portfolio_value: float,
    kelly_fraction: float = 0.25,  # Use 1/4 Kelly for safety
    max_position_pct: float = 0.20
) -> float:
    """
    Calculate optimal position size using Kelly Criterion

    Formula: f* = (p*b - q) / b
    where:
        f* = optimal fraction of capital
        p = win probability
        b = win/loss ratio
        q = loss probability (1-p)

    Args:
        win_rate: Historical win rate (0-1)
        avg_win: Average win amount (as decimal, e.g., 0.05 = 5%)
        avg_loss: Average loss amount (as decimal, e.g., 0.03 = 3%)
        portfolio_value: Total portfolio value
        kelly_fraction: Fraction of Kelly to use (default: 0.25 for quarter Kelly)
        max_position_pct: Maximum position percentage

    Returns:
        Position size in USD
    """
    if avg_loss <= 0 or win_rate <= 0 or win_rate >= 1:
        # Invalid inputs, return conservative size
        return portfolio_value * 0.02

    # Calculate win/loss ratio
    win_loss_ratio = avg_win / avg_loss

    # Kelly formula
    kelly_pct = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio

    # Apply Kelly fraction (fractional Kelly for safety)
    kelly_pct = kelly_pct * kelly_fraction

    # Ensure positive and within limits
    kelly_pct = max(0.01, min(kelly_pct, max_position_pct))

    return portfolio_value * kelly_pct


def risk_parity_position_size(
    portfolio_value: float,
    asset_volatility: float,
    num_positions: int,
    target_risk_per_position: float = 0.10  # 10% risk per position
) -> float:
    """
    Risk parity position sizing - each position contributes equal risk

    Args:
        portfolio_value: Total portfolio value
        asset_volatility: Asset's volatility
        num_positions: Number of positions in portfolio
        target_risk_per_position: Target risk contribution per position

    Returns:
        Position size in USD
    """
    if asset_volatility <= 0 or num_positions <= 0:
        return portfolio_value * 0.05

    # Risk budget per position
    risk_budget = target_risk_per_position / num_positions

    # Position size = (Portfolio * Risk Budget) / Volatility
    position_size = (portfolio_value * risk_budget) / asset_volatility

    # Cap at reasonable maximum (50% of portfolio / num_positions)
    max_size = (portfolio_value * 0.50) / num_positions
    position_size = min(position_size, max_size)

    return position_size


# ============================================================================
# CORRELATION ANALYSIS
# ============================================================================

def calculate_correlation_matrix(
    price_data: Dict[str, pd.Series],
    method: str = 'pearson',
    min_periods: int = 20
) -> pd.DataFrame:
    """
    Calculate correlation matrix between multiple assets

    Args:
        price_data: Dict of {token_address: price_series}
        method: Correlation method ('pearson', 'spearman', 'kendall')
        min_periods: Minimum periods required for correlation

    Returns:
        Correlation matrix as DataFrame
    """
    if len(price_data) < 2:
        return pd.DataFrame()

    # Convert to DataFrame with returns
    returns_data = {}
    for token, prices in price_data.items():
        if len(prices) >= min_periods:
            returns = prices.pct_change().dropna()
            if len(returns) >= min_periods:
                returns_data[token] = returns

    if len(returns_data) < 2:
        return pd.DataFrame()

    # Create DataFrame and calculate correlation
    returns_df = pd.DataFrame(returns_data)
    correlation_matrix = returns_df.corr(method=method, min_periods=min_periods)

    return correlation_matrix


def check_portfolio_concentration(
    positions: Dict[str, float],
    correlation_matrix: pd.DataFrame,
    max_correlation: float = 0.70,
    max_correlated_exposure: float = 0.40  # Max 40% in highly correlated assets
) -> Dict:
    """
    Check if portfolio is too concentrated in correlated assets

    Args:
        positions: Dict of {token: position_value_usd}
        correlation_matrix: Correlation matrix from calculate_correlation_matrix
        max_correlation: Correlation threshold for "high correlation"
        max_correlated_exposure: Max % of portfolio in correlated assets

    Returns:
        Dict with warnings and recommendations
    """
    results = {
        "warnings": [],
        "correlated_groups": [],
        "total_exposure": 0.0,
        "is_concentrated": False
    }

    if correlation_matrix.empty or len(positions) < 2:
        return results

    total_portfolio = sum(positions.values())
    if total_portfolio <= 0:
        return results

    # Find highly correlated pairs
    correlated_pairs = []
    tokens = list(correlation_matrix.columns)

    for i in range(len(tokens)):
        for j in range(i + 1, len(tokens)):
            token_a = tokens[i]
            token_b = tokens[j]

            if token_a in positions and token_b in positions:
                correlation = correlation_matrix.loc[token_a, token_b]

                if abs(correlation) >= max_correlation:
                    combined_exposure = (positions[token_a] + positions[token_b]) / total_portfolio
                    correlated_pairs.append({
                        "token_a": token_a,
                        "token_b": token_b,
                        "correlation": correlation,
                        "combined_exposure_pct": combined_exposure * 100
                    })

    # Group correlated assets
    if correlated_pairs:
        results["correlated_groups"] = correlated_pairs

        # Calculate total exposure to correlated assets
        correlated_tokens = set()
        for pair in correlated_pairs:
            correlated_tokens.add(pair["token_a"])
            correlated_tokens.add(pair["token_b"])

        correlated_exposure = sum(positions.get(token, 0) for token in correlated_tokens)
        results["total_exposure"] = correlated_exposure / total_portfolio

        # Check if concentrated
        if results["total_exposure"] > max_correlated_exposure:
            results["is_concentrated"] = True
            results["warnings"].append(
                f"⚠️ High concentration: {results['total_exposure']*100:.1f}% in correlated assets "
                f"(limit: {max_correlated_exposure*100:.0f}%)"
            )

    return results


# ============================================================================
# PORTFOLIO RISK METRICS
# ============================================================================

def calculate_portfolio_var(
    positions: Dict[str, float],
    returns_data: Dict[str, pd.Series],
    confidence_level: float = 0.95,
    time_horizon: int = 1  # 1-period VaR
) -> float:
    """
    Calculate Portfolio Value at Risk (VaR)

    Args:
        positions: Dict of {token: position_value_usd}
        returns_data: Dict of {token: returns_series}
        confidence_level: Confidence level (default: 95%)
        time_horizon: Time horizon in periods

    Returns:
        VaR in USD (positive number represents potential loss)
    """
    if not positions or not returns_data:
        return 0.0

    # Calculate portfolio returns
    portfolio_returns = []
    total_value = sum(positions.values())

    if total_value <= 0:
        return 0.0

    # Get common dates across all positions
    all_returns = pd.DataFrame(returns_data)
    common_dates = all_returns.dropna().index

    if len(common_dates) < 20:
        return 0.0

    # Calculate weighted portfolio returns
    for date in common_dates:
        portfolio_return = 0.0
        for token, value in positions.items():
            if token in returns_data:
                weight = value / total_value
                portfolio_return += weight * returns_data[token].loc[date]
        portfolio_returns.append(portfolio_return)

    # Calculate VaR
    portfolio_returns = pd.Series(portfolio_returns)
    var_percentile = np.percentile(portfolio_returns, (1 - confidence_level) * 100)

    # Scale by time horizon
    var_value = abs(var_percentile) * np.sqrt(time_horizon) * total_value

    return var_value


def calculate_portfolio_cvar(
    positions: Dict[str, float],
    returns_data: Dict[str, pd.Series],
    confidence_level: float = 0.95
) -> float:
    """
    Calculate Conditional Value at Risk (CVaR / Expected Shortfall)
    Average loss beyond VaR

    Args:
        positions: Dict of {token: position_value_usd}
        returns_data: Dict of {token: returns_series}
        confidence_level: Confidence level (default: 95%)

    Returns:
        CVaR in USD
    """
    if not positions or not returns_data:
        return 0.0

    # Calculate portfolio returns
    portfolio_returns = []
    total_value = sum(positions.values())

    if total_value <= 0:
        return 0.0

    all_returns = pd.DataFrame(returns_data)
    common_dates = all_returns.dropna().index

    if len(common_dates) < 20:
        return 0.0

    for date in common_dates:
        portfolio_return = 0.0
        for token, value in positions.items():
            if token in returns_data:
                weight = value / total_value
                portfolio_return += weight * returns_data[token].loc[date]
        portfolio_returns.append(portfolio_return)

    portfolio_returns = pd.Series(portfolio_returns)

    # Find VaR threshold
    var_threshold = np.percentile(portfolio_returns, (1 - confidence_level) * 100)

    # CVaR is average of returns below VaR
    tail_returns = portfolio_returns[portfolio_returns <= var_threshold]

    if len(tail_returns) == 0:
        return 0.0

    cvar_value = abs(tail_returns.mean()) * total_value

    return cvar_value


def calculate_sharpe_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.02,  # 2% annual
    periods_per_year: int = 35040
) -> float:
    """
    Calculate Sharpe Ratio

    Args:
        returns: Series of returns
        risk_free_rate: Annual risk-free rate
        periods_per_year: Periods per year for annualization

    Returns:
        Sharpe ratio
    """
    if len(returns) < 2:
        return 0.0

    # Calculate excess returns
    period_rf = risk_free_rate / periods_per_year
    excess_returns = returns - period_rf

    # Sharpe ratio
    if excess_returns.std() == 0:
        return 0.0

    sharpe = (excess_returns.mean() / excess_returns.std()) * np.sqrt(periods_per_year)

    return sharpe


def calculate_max_drawdown(prices: pd.Series) -> Tuple[float, int]:
    """
    Calculate maximum drawdown and duration

    Args:
        prices: Series of prices

    Returns:
        Tuple of (max_drawdown_pct, duration_periods)
    """
    if len(prices) < 2:
        return 0.0, 0

    # Calculate running maximum
    running_max = prices.expanding().max()

    # Calculate drawdown
    drawdown = (prices - running_max) / running_max

    max_dd = abs(drawdown.min())

    # Find duration
    dd_duration = 0
    current_duration = 0

    for dd in drawdown:
        if dd < 0:
            current_duration += 1
            dd_duration = max(dd_duration, current_duration)
        else:
            current_duration = 0

    return max_dd, dd_duration


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_position_score(
    volatility: float,
    correlation_with_portfolio: float,
    recent_performance: float,
    max_volatility: float = 1.0,  # 100% annual vol
    max_correlation: float = 0.80
) -> float:
    """
    Score a position for risk assessment (0-100)

    Higher score = higher risk

    Args:
        volatility: Asset volatility
        correlation_with_portfolio: Correlation with existing portfolio
        recent_performance: Recent return (positive or negative)
        max_volatility: Maximum acceptable volatility
        max_correlation: Maximum acceptable correlation

    Returns:
        Risk score (0-100, higher = riskier)
    """
    score = 0.0

    # Volatility component (40 points)
    vol_score = min((volatility / max_volatility) * 40, 40)
    score += vol_score

    # Correlation component (30 points)
    corr_score = min((abs(correlation_with_portfolio) / max_correlation) * 30, 30)
    score += corr_score

    # Recent performance component (30 points)
    # Negative recent performance = higher risk
    if recent_performance < 0:
        perf_score = min((abs(recent_performance) / 0.20) * 30, 30)  # -20% = max
    else:
        perf_score = 0  # No penalty for positive performance
    score += perf_score

    return min(score, 100)


if __name__ == "__main__":
    """
    Example usage and testing
    """
    print("🌙 Moon Dev's Risk Metrics Module")
    print("=" * 60)

    # Example: Volatility calculation
    example_prices = pd.Series([100, 102, 98, 103, 97, 105, 100, 108])
    vol = calculate_volatility(example_prices, window=5, annualize=False)
    print(f"\nExample Volatility: {vol*100:.2f}%")

    # Example: Position sizing
    portfolio_value = 10000
    asset_vol = 0.50  # 50% annual volatility
    position = volatility_based_position_size(portfolio_value, asset_volatility=asset_vol)
    print(f"\nVolatility-based position size: ${position:.2f}")
    print(f"Position as % of portfolio: {(position/portfolio_value)*100:.1f}%")

    # Example: Kelly Criterion
    kelly_position = kelly_criterion_position_size(
        win_rate=0.60,
        avg_win=0.05,
        avg_loss=0.03,
        portfolio_value=portfolio_value
    )
    print(f"\nKelly Criterion position size: ${kelly_position:.2f}")
    print(f"Position as % of portfolio: {(kelly_position/portfolio_value)*100:.1f}%")

    print("\n✅ Risk metrics module ready for use!")

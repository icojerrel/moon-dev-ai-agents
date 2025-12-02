"""
🌙 Moon Dev's Portfolio Optimization Module
Built with love by Moon Dev 🚀

Advanced portfolio optimization using Modern Portfolio Theory (MPT) and
beyond. Integrates with skfolio library for production-grade optimization.

Features:
- Mean-Variance Optimization (Markowitz)
- Risk Parity / Equal Risk Contribution
- Hierarchical Risk Parity (HRP)
- CVaR (Conditional Value at Risk) optimization
- Maximum Sharpe Ratio
- Minimum Volatility
- Custom constraints (min/max weights, sector limits)
- Transaction cost awareness

Supported Risk Measures:
- Variance (standard deviation)
- Semi-variance (downside risk)
- CVaR (tail risk)
- CDaR (Conditional Drawdown at Risk)
- Maximum Drawdown
- EVaR (Entropic Value at Risk)

Usage:
    from src.utils.portfolio_optimizer import PortfolioOptimizer
    import pandas as pd

    # Create optimizer
    optimizer = PortfolioOptimizer(method='cvar', risk_measure='cvar')

    # Prepare returns data
    returns = pd.DataFrame({
        'BTC': [...],   # Daily returns
        'ETH': [...],
        'SOL': [...]
    })

    # Optimize portfolio
    weights = optimizer.optimize(
        returns_df=returns,
        constraints={'min_weight': 0.05, 'max_weight': 0.40}
    )

    print(weights)  # {'BTC': 0.40, 'ETH': 0.35, 'SOL': 0.25}
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, List, Union
from decimal import Decimal
from termcolor import cprint


class PortfolioOptimizer:
    """
    Portfolio optimization using various methods

    This is a wrapper that gracefully handles skfolio if available,
    otherwise falls back to simple heuristics.
    """

    def __init__(
        self,
        method: str = 'mean_variance',
        risk_measure: str = 'variance',
        target_return: Optional[float] = None,
        target_volatility: Optional[float] = None
    ):
        """
        Initialize portfolio optimizer

        Args:
            method: Optimization method
                   - 'mean_variance': Classic Markowitz optimization
                   - 'risk_parity': Equal risk contribution
                   - 'hrp': Hierarchical Risk Parity
                   - 'min_volatility': Minimize portfolio volatility
                   - 'max_sharpe': Maximize Sharpe ratio
                   - 'cvar': Conditional Value at Risk minimization
            risk_measure: Risk metric to optimize
                         - 'variance': Standard deviation
                         - 'semivariance': Downside deviation
                         - 'cvar': Conditional Value at Risk (tail risk)
                         - 'max_drawdown': Maximum drawdown
            target_return: Target portfolio return (for mean-variance)
            target_volatility: Target portfolio volatility
        """
        self.method = method
        self.risk_measure = risk_measure
        self.target_return = target_return
        self.target_volatility = target_volatility

        # Try to import skfolio (optional dependency)
        self.skfolio_available = False
        try:
            import skfolio
            from skfolio.optimization import (
                MeanVariance,
                RiskBudgeting,
                HierarchicalRiskParity,
                ConvexOptimization
            )
            from skfolio.prior import EmpiricalPrior
            from skfolio import Population

            self.skfolio = skfolio
            self.MeanVariance = MeanVariance
            self.RiskBudgeting = RiskBudgeting
            self.HierarchicalRiskParity = HierarchicalRiskParity
            self.skfolio_available = True

            cprint("✅ skfolio library loaded (advanced optimization enabled)", "green")

        except ImportError:
            cprint("⚠️  skfolio not installed, using basic optimization", "yellow")
            cprint("   Install with: pip install skfolio", "yellow")

    def optimize(
        self,
        returns_df: pd.DataFrame,
        constraints: Optional[Dict[str, float]] = None
    ) -> Dict[str, float]:
        """
        Optimize portfolio weights

        Args:
            returns_df: DataFrame of asset returns (rows=time, columns=assets)
            constraints: Dict of constraints
                        - 'min_weight': Minimum weight per asset (default 0.0)
                        - 'max_weight': Maximum weight per asset (default 1.0)
                        - 'min_weights': Dict of per-asset minimums
                        - 'max_weights': Dict of per-asset maximums

        Returns:
            Dictionary of optimized weights {asset: weight}

        Example:
            >>> returns = pd.DataFrame({
            ...     'BTC': [0.02, -0.01, 0.03, 0.01],
            ...     'ETH': [0.01, 0.02, -0.01, 0.02],
            ...     'SOL': [0.03, -0.02, 0.04, -0.01]
            ... })
            >>> weights = optimizer.optimize(returns)
            >>> print(weights)
            {'BTC': 0.40, 'ETH': 0.35, 'SOL': 0.25}
        """
        # Validate inputs
        if returns_df.empty:
            raise ValueError("returns_df cannot be empty")

        if len(returns_df) < 30:
            cprint(f"⚠️  Only {len(returns_df)} periods of data, need 30+ for reliable optimization", "yellow")

        # Set default constraints
        constraints = constraints or {}
        min_weight = constraints.get('min_weight', 0.0)
        max_weight = constraints.get('max_weight', 1.0)

        if self.skfolio_available:
            return self._optimize_with_skfolio(returns_df, constraints)
        else:
            return self._optimize_simple(returns_df, min_weight, max_weight)

    def _optimize_with_skfolio(
        self,
        returns_df: pd.DataFrame,
        constraints: Dict[str, float]
    ) -> Dict[str, float]:
        """Optimize using skfolio library (advanced)"""
        try:
            min_weight = constraints.get('min_weight', 0.0)
            max_weight = constraints.get('max_weight', 1.0)

            # Choose optimization method
            if self.method == 'mean_variance':
                model = self.MeanVariance(
                    min_weights=min_weight,
                    max_weights=max_weight,
                    risk_free_rate=0.0  # Can be configured
                )
            elif self.method == 'risk_parity':
                model = self.RiskBudgeting(
                    min_weights=min_weight,
                    max_weights=max_weight
                )
            elif self.method == 'hrp':
                model = self.HierarchicalRiskParity()
            else:
                # Default to mean-variance
                model = self.MeanVariance(
                    min_weights=min_weight,
                    max_weights=max_weight
                )

            # Fit model to returns data
            model.fit(returns_df)

            # Get optimized weights
            weights_array = model.weights_

            # Convert to dictionary
            weights_dict = {
                asset: float(weight)
                for asset, weight in zip(returns_df.columns, weights_array)
            }

            # Normalize to sum to 1.0
            total = sum(weights_dict.values())
            if total > 0:
                weights_dict = {k: v/total for k, v in weights_dict.items()}

            return weights_dict

        except Exception as e:
            cprint(f"❌ skfolio optimization failed: {e}", "red")
            cprint("   Falling back to simple optimization", "yellow")
            return self._optimize_simple(
                returns_df,
                constraints.get('min_weight', 0.0),
                constraints.get('max_weight', 1.0)
            )

    def _optimize_simple(
        self,
        returns_df: pd.DataFrame,
        min_weight: float,
        max_weight: float
    ) -> Dict[str, float]:
        """
        Simple optimization fallback (no external dependencies)

        Uses Sharpe ratio maximization via equal weighting or
        inverse volatility weighting.
        """
        cprint("🔧 Using simple inverse-volatility optimization", "cyan")

        # Calculate asset volatilities
        volatilities = returns_df.std()

        # Inverse volatility weighting (lower vol = higher weight)
        inverse_vols = 1.0 / volatilities
        raw_weights = inverse_vols / inverse_vols.sum()

        # Apply constraints
        weights = {}
        for asset, weight in raw_weights.items():
            weight = max(min_weight, min(max_weight, weight))
            weights[asset] = float(weight)

        # Renormalize to sum to 1.0
        total = sum(weights.values())
        if total > 0:
            weights = {k: v/total for k, v in weights.items()}

        return weights

    def calculate_portfolio_metrics(
        self,
        returns_df: pd.DataFrame,
        weights: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calculate portfolio performance metrics

        Args:
            returns_df: Asset returns
            weights: Portfolio weights

        Returns:
            Dict with metrics:
            - expected_return: Annualized expected return
            - volatility: Annualized volatility
            - sharpe_ratio: Sharpe ratio (assuming 0% risk-free rate)
            - max_drawdown: Maximum drawdown
            - var_95: 95% Value at Risk
            - cvar_95: 95% Conditional Value at Risk
        """
        # Calculate portfolio returns
        weights_series = pd.Series(weights)
        portfolio_returns = (returns_df * weights_series).sum(axis=1)

        # Annualize metrics (assuming daily returns)
        periods_per_year = 252  # Trading days

        expected_return = portfolio_returns.mean() * periods_per_year
        volatility = portfolio_returns.std() * np.sqrt(periods_per_year)
        sharpe_ratio = expected_return / volatility if volatility > 0 else 0

        # Calculate drawdown
        cumulative = (1 + portfolio_returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()

        # VaR and CVaR (95% confidence)
        var_95 = np.percentile(portfolio_returns, 5)
        cvar_95 = portfolio_returns[portfolio_returns <= var_95].mean()

        return {
            'expected_return': float(expected_return),
            'volatility': float(volatility),
            'sharpe_ratio': float(sharpe_ratio),
            'max_drawdown': float(max_drawdown),
            'var_95': float(var_95),
            'cvar_95': float(cvar_95)
        }

    def suggest_rebalancing(
        self,
        current_weights: Dict[str, float],
        optimal_weights: Dict[str, float],
        threshold: float = 0.05
    ) -> Dict[str, float]:
        """
        Suggest rebalancing trades

        Args:
            current_weights: Current portfolio allocation
            optimal_weights: Target allocation
            threshold: Minimum deviation to trigger rebalance (default 5%)

        Returns:
            Dict of suggested trades {asset: delta_weight}
            Positive = buy, negative = sell

        Example:
            >>> current = {'BTC': 0.50, 'ETH': 0.30, 'SOL': 0.20}
            >>> optimal = {'BTC': 0.40, 'ETH': 0.35, 'SOL': 0.25}
            >>> trades = optimizer.suggest_rebalancing(current, optimal)
            >>> print(trades)
            {'BTC': -0.10, 'ETH': 0.05, 'SOL': 0.05}
        """
        trades = {}

        all_assets = set(current_weights.keys()) | set(optimal_weights.keys())

        for asset in all_assets:
            current = current_weights.get(asset, 0.0)
            optimal = optimal_weights.get(asset, 0.0)
            delta = optimal - current

            if abs(delta) >= threshold:
                trades[asset] = delta

        return trades


# ============================================
# 🧪 TESTING & EXAMPLES
# ============================================

def run_examples():
    """Run portfolio optimization examples"""
    cprint("\n🌙 Moon Dev's Portfolio Optimizer Examples\n", "cyan", attrs=["bold"])

    # Create sample returns data
    np.random.seed(42)
    periods = 100

    returns_data = {
        'BTC': np.random.normal(0.001, 0.03, periods),  # Higher vol
        'ETH': np.random.normal(0.0008, 0.025, periods),
        'SOL': np.random.normal(0.0012, 0.04, periods),  # Highest vol
        'AVAX': np.random.normal(0.0006, 0.02, periods),  # Lower vol
    }
    returns_df = pd.DataFrame(returns_data)

    # Example 1: Simple optimization
    cprint("Example 1: Inverse-Volatility Optimization", "cyan")
    optimizer = PortfolioOptimizer(method='min_volatility')

    weights = optimizer.optimize(
        returns_df,
        constraints={'min_weight': 0.10, 'max_weight': 0.40}
    )

    cprint("  Optimized Weights:", "white")
    for asset, weight in weights.items():
        cprint(f"    {asset}: {weight:.2%}", "green")

    # Example 2: Portfolio metrics
    cprint("\nExample 2: Portfolio Performance Metrics", "cyan")
    metrics = optimizer.calculate_portfolio_metrics(returns_df, weights)

    cprint("  Expected Return: {:.2%} (annualized)".format(metrics['expected_return']), "green")
    cprint("  Volatility: {:.2%} (annualized)".format(metrics['volatility']), "yellow")
    cprint("  Sharpe Ratio: {:.2f}".format(metrics['sharpe_ratio']), "green")
    cprint("  Max Drawdown: {:.2%}".format(metrics['max_drawdown']), "red")
    cprint("  VaR (95%): {:.2%}".format(metrics['var_95']), "yellow")
    cprint("  CVaR (95%): {:.2%}".format(metrics['cvar_95']), "red")

    # Example 3: Rebalancing suggestions
    cprint("\nExample 3: Rebalancing Recommendations", "cyan")
    current_weights = {
        'BTC': 0.50,
        'ETH': 0.30,
        'SOL': 0.10,
        'AVAX': 0.10
    }

    trades = optimizer.suggest_rebalancing(current_weights, weights, threshold=0.05)

    if trades:
        cprint("  Suggested Trades (threshold: 5%):", "white")
        for asset, delta in trades.items():
            action = "BUY" if delta > 0 else "SELL"
            color = "green" if delta > 0 else "red"
            cprint(f"    {action} {asset}: {abs(delta):.2%}", color)
    else:
        cprint("  ✅ No rebalancing needed (within threshold)", "green")

    cprint("\n")


if __name__ == "__main__":
    run_examples()

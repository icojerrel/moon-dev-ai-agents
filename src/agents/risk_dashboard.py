"""
🌙 Moon Dev's Risk Dashboard
Real-time risk monitoring and visualization

Features:
- Portfolio risk overview
- Correlation heat maps
- Position risk scores
- Real-time alerts
- Risk reports (CSV/JSON export)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
from termcolor import cprint, colored
import json
import os
from pathlib import Path


# ============================================================================
# RISK DASHBOARD CLASS
# ============================================================================

class RiskDashboard:
    """
    Real-time risk monitoring and reporting dashboard
    """

    def __init__(self, output_dir: str = 'src/data/risk_reports'):
        """Initialize risk dashboard"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.current_metrics = {}
        self.alerts = []

    def display_portfolio_overview(
        self,
        portfolio_value: float,
        positions: Dict[str, Dict],
        start_balance: float
    ):
        """
        Display comprehensive portfolio overview

        Args:
            portfolio_value: Current total portfolio value
            positions: Dict of {token: {value, volatility, etc.}}
            start_balance: Starting balance for PnL calculation
        """
        # Header
        cprint("\n" + "=" * 70, "cyan")
        cprint("🌙 MOON DEV'S RISK DASHBOARD 🛡️", "cyan", attrs=["bold"])
        cprint("=" * 70, "cyan")

        # Portfolio Summary
        pnl = portfolio_value - start_balance
        pnl_pct = (pnl / start_balance * 100) if start_balance > 0 else 0
        pnl_color = "green" if pnl >= 0 else "red"

        cprint("\n💼 PORTFOLIO SUMMARY", "white", attrs=["bold"])
        cprint("-" * 70, "cyan")
        print(f"  Total Value:        ${portfolio_value:,.2f}")
        print(f"  Start Balance:      ${start_balance:,.2f}")
        print(colored(f"  PnL:                ${pnl:,.2f} ({pnl_pct:+.2f}%)", pnl_color))
        print(f"  Positions:          {len(positions)}")

        # Position Breakdown
        if positions:
            cprint("\n📊 POSITIONS", "white", attrs=["bold"])
            cprint("-" * 70, "cyan")

            # Sort by value descending
            sorted_positions = sorted(
                positions.items(),
                key=lambda x: x[1].get('value', 0),
                reverse=True
            )

            for token, data in sorted_positions:
                value = data.get('value', 0)
                pct = (value / portfolio_value * 100) if portfolio_value > 0 else 0
                volatility = data.get('volatility', 0)
                risk_score = data.get('risk_score', 0)

                # Color code by risk score
                if risk_score >= 70:
                    risk_color = "red"
                elif risk_score >= 50:
                    risk_color = "yellow"
                else:
                    risk_color = "green"

                print(f"\n  {token[:12]}...")
                print(f"    Value:     ${value:,.2f} ({pct:.1f}%)")
                print(f"    Volatility: {volatility*100:.1f}%")
                print(colored(f"    Risk Score: {risk_score:.0f}/100", risk_color))

    def display_risk_metrics(
        self,
        portfolio_volatility: float,
        portfolio_var: float,
        portfolio_cvar: float,
        sharpe_ratio: float,
        max_drawdown: float
    ):
        """
        Display key risk metrics

        Args:
            portfolio_volatility: Portfolio volatility
            portfolio_var: Value at Risk
            portfolio_cvar: Conditional VaR
            sharpe_ratio: Sharpe ratio
            max_drawdown: Maximum drawdown
        """
        cprint("\n📈 RISK METRICS", "white", attrs=["bold"])
        cprint("-" * 70, "cyan")

        # Volatility
        vol_color = "red" if portfolio_volatility > 0.50 else "yellow" if portfolio_volatility > 0.30 else "green"
        print(colored(f"  Portfolio Volatility:  {portfolio_volatility*100:.1f}%", vol_color))

        # VaR
        print(f"  Value at Risk (95%):   ${portfolio_var:,.2f}")
        print(f"  CVaR (95%):            ${portfolio_cvar:,.2f}")

        # Sharpe Ratio
        sharpe_color = "green" if sharpe_ratio > 1.5 else "yellow" if sharpe_ratio > 1.0 else "red"
        print(colored(f"  Sharpe Ratio:          {sharpe_ratio:.2f}", sharpe_color))

        # Max Drawdown
        dd_color = "green" if max_drawdown < 0.10 else "yellow" if max_drawdown < 0.20 else "red"
        print(colored(f"  Max Drawdown:          {max_drawdown*100:.1f}%", dd_color))

    def display_correlation_heatmap(
        self,
        correlation_matrix: pd.DataFrame,
        positions: Dict[str, float]
    ):
        """
        Display correlation heat map (text-based)

        Args:
            correlation_matrix: Correlation matrix
            positions: Position values for sizing
        """
        if correlation_matrix.empty:
            return

        cprint("\n🔥 CORRELATION HEAT MAP", "white", attrs=["bold"])
        cprint("-" * 70, "cyan")

        # Truncate token names for display
        tokens = [t[:8] for t in correlation_matrix.columns]

        # Header
        print("        ", end="")
        for token in tokens:
            print(f"{token:>8}", end=" ")
        print()

        # Rows
        for i, token_a in enumerate(correlation_matrix.index):
            print(f"{tokens[i]:>8}", end=" ")

            for j, token_b in enumerate(correlation_matrix.columns):
                corr = correlation_matrix.loc[token_a, token_b]

                # Color code correlation
                if i == j:
                    # Diagonal (self-correlation)
                    corr_str = colored(f"{corr:>7.2f}", "white")
                elif abs(corr) >= 0.70:
                    # High correlation
                    corr_str = colored(f"{corr:>7.2f}", "red", attrs=["bold"])
                elif abs(corr) >= 0.40:
                    # Medium correlation
                    corr_str = colored(f"{corr:>7.2f}", "yellow")
                else:
                    # Low correlation
                    corr_str = colored(f"{corr:>7.2f}", "green")

                print(corr_str, end=" ")
            print()

        # Legend
        cprint("\n  Legend:", "cyan")
        print(colored("    High (>0.7)", "red", attrs=["bold"]))
        print(colored("    Medium (0.4-0.7)", "yellow"))
        print(colored("    Low (<0.4)", "green"))

    def display_concentration_warnings(
        self,
        concentration_results: Dict
    ):
        """
        Display portfolio concentration warnings

        Args:
            concentration_results: Results from check_portfolio_concentration
        """
        if not concentration_results.get("warnings"):
            cprint("\n✅ NO CONCENTRATION WARNINGS", "white", "on_green")
            return

        cprint("\n⚠️  CONCENTRATION WARNINGS", "white", "on_yellow")
        cprint("-" * 70, "cyan")

        for warning in concentration_results["warnings"]:
            print(colored(f"  {warning}", "yellow"))

        # Show correlated groups
        if concentration_results.get("correlated_groups"):
            cprint("\n  Correlated Asset Groups:", "yellow")
            for group in concentration_results["correlated_groups"]:
                token_a = group["token_a"][:12]
                token_b = group["token_b"][:12]
                corr = group["correlation"]
                exposure = group["combined_exposure_pct"]

                print(f"    • {token_a}... ↔ {token_b}...")
                print(f"      Correlation: {corr:.2f}")
                print(f"      Combined Exposure: {exposure:.1f}%")

    def display_alerts(self):
        """Display active risk alerts"""
        if not self.alerts:
            return

        cprint("\n🚨 ACTIVE ALERTS", "white", "on_red", attrs=["bold"])
        cprint("-" * 70, "cyan")

        for alert in self.alerts:
            severity = alert.get("severity", "medium")
            message = alert.get("message", "")

            if severity == "critical":
                print(colored(f"  🔴 CRITICAL: {message}", "red", attrs=["bold"]))
            elif severity == "high":
                print(colored(f"  🟠 HIGH: {message}", "yellow", attrs=["bold"]))
            else:
                print(colored(f"  🟡 MEDIUM: {message}", "yellow"))

    def add_alert(
        self,
        message: str,
        severity: str = "medium",
        alert_type: str = "general"
    ):
        """
        Add risk alert

        Args:
            message: Alert message
            severity: Alert severity (critical, high, medium, low)
            alert_type: Type of alert (volatility, correlation, concentration, etc.)
        """
        self.alerts.append({
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "severity": severity,
            "type": alert_type
        })

    def clear_alerts(self):
        """Clear all alerts"""
        self.alerts = []

    def export_risk_report(
        self,
        report_data: Dict,
        format: str = "json"
    ) -> str:
        """
        Export risk report to file

        Args:
            report_data: Risk report data
            format: Export format ('json' or 'csv')

        Returns:
            Path to exported file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if format == "json":
            filename = f"risk_report_{timestamp}.json"
            filepath = self.output_dir / filename

            with open(filepath, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)

        elif format == "csv":
            filename = f"risk_report_{timestamp}.csv"
            filepath = self.output_dir / filename

            # Flatten report data for CSV
            df = pd.DataFrame([report_data])
            df.to_csv(filepath, index=False)

        cprint(f"\n💾 Risk report exported: {filename}", "white", "on_green")
        return str(filepath)

    def generate_risk_report(
        self,
        portfolio_value: float,
        positions: Dict[str, Dict],
        metrics: Dict,
        concentration: Dict
    ) -> Dict:
        """
        Generate comprehensive risk report

        Args:
            portfolio_value: Total portfolio value
            positions: Position data
            metrics: Risk metrics
            concentration: Concentration analysis

        Returns:
            Risk report as dictionary
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "portfolio_summary": {
                "total_value": portfolio_value,
                "num_positions": len(positions),
                "largest_position_pct": max(
                    [(v.get('value', 0) / portfolio_value * 100) for v in positions.values()],
                    default=0
                )
            },
            "risk_metrics": {
                "portfolio_volatility": metrics.get("volatility", 0),
                "value_at_risk_95": metrics.get("var", 0),
                "cvar_95": metrics.get("cvar", 0),
                "sharpe_ratio": metrics.get("sharpe", 0),
                "max_drawdown": metrics.get("max_drawdown", 0)
            },
            "concentration": {
                "is_concentrated": concentration.get("is_concentrated", False),
                "total_correlated_exposure": concentration.get("total_exposure", 0),
                "num_correlated_groups": len(concentration.get("correlated_groups", []))
            },
            "alerts": self.alerts,
            "positions": []
        }

        # Add position details
        for token, data in positions.items():
            report["positions"].append({
                "token": token,
                "value": data.get("value", 0),
                "pct_of_portfolio": (data.get("value", 0) / portfolio_value * 100) if portfolio_value > 0 else 0,
                "volatility": data.get("volatility", 0),
                "risk_score": data.get("risk_score", 0)
            })

        return report


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def print_risk_summary(
    portfolio_value: float,
    var_95: float,
    max_position_size: float,
    num_positions: int
):
    """
    Quick risk summary for terminal display

    Args:
        portfolio_value: Total portfolio value
        var_95: Value at Risk (95%)
        max_position_size: Largest position size
        num_positions: Number of positions
    """
    cprint("\n🛡️  RISK SUMMARY", "white", "on_blue", attrs=["bold"])
    print(f"Portfolio Value:  ${portfolio_value:,.2f}")
    print(f"VaR (95%):        ${var_95:,.2f} ({(var_95/portfolio_value*100):.1f}%)")
    print(f"Largest Position: ${max_position_size:,.2f} ({(max_position_size/portfolio_value*100):.1f}%)")
    print(f"Total Positions:  {num_positions}")


def create_position_size_recommendation(
    token: str,
    current_size: float,
    recommended_size: float,
    reason: str
) -> Dict:
    """
    Create position size recommendation

    Args:
        token: Token address
        current_size: Current position size
        recommended_size: Recommended position size
        reason: Reason for recommendation

    Returns:
        Recommendation as dictionary
    """
    change_pct = ((recommended_size - current_size) / current_size * 100) if current_size > 0 else 0

    return {
        "token": token,
        "current_size": current_size,
        "recommended_size": recommended_size,
        "change_usd": recommended_size - current_size,
        "change_pct": change_pct,
        "reason": reason,
        "action": "INCREASE" if change_pct > 0 else "DECREASE" if change_pct < 0 else "HOLD"
    }


def display_position_recommendations(recommendations: List[Dict]):
    """
    Display position sizing recommendations

    Args:
        recommendations: List of recommendation dicts
    """
    if not recommendations:
        cprint("\n✅ No position adjustments recommended", "white", "on_green")
        return

    cprint("\n💡 POSITION RECOMMENDATIONS", "white", "on_cyan", attrs=["bold"])
    cprint("-" * 70, "cyan")

    for rec in recommendations:
        token = rec["token"][:12]
        action = rec["action"]
        change_pct = rec["change_pct"]
        reason = rec["reason"]

        # Color code by action
        if action == "INCREASE":
            action_color = "green"
            symbol = "⬆️"
        elif action == "DECREASE":
            action_color = "red"
            symbol = "⬇️"
        else:
            action_color = "white"
            symbol = "➡️"

        print(f"\n  {symbol} {token}...")
        print(colored(f"    Action: {action} ({change_pct:+.1f}%)", action_color))
        print(f"    Current: ${rec['current_size']:,.2f}")
        print(f"    Recommended: ${rec['recommended_size']:,.2f}")
        print(f"    Reason: {reason}")


# ============================================================================
# MAIN (EXAMPLE)
# ============================================================================

if __name__ == "__main__":
    """
    Example usage of risk dashboard
    """
    print("\n🌙 Moon Dev's Risk Dashboard - Example\n")

    # Create dashboard
    dashboard = RiskDashboard()

    # Example portfolio data
    portfolio_value = 10000
    start_balance = 9000

    positions = {
        "TokenA": {
            "value": 3000,
            "volatility": 0.45,
            "risk_score": 65
        },
        "TokenB": {
            "value": 2500,
            "volatility": 0.30,
            "risk_score": 45
        },
        "TokenC": {
            "value": 2000,
            "volatility": 0.60,
            "risk_score": 75
        }
    }

    # Display overview
    dashboard.display_portfolio_overview(portfolio_value, positions, start_balance)

    # Display risk metrics
    dashboard.display_risk_metrics(
        portfolio_volatility=0.40,
        portfolio_var=450,
        portfolio_cvar=600,
        sharpe_ratio=1.8,
        max_drawdown=0.12
    )

    # Add sample alerts
    dashboard.add_alert(
        "High volatility detected in TokenC",
        severity="high",
        alert_type="volatility"
    )

    dashboard.display_alerts()

    # Generate report
    report = dashboard.generate_risk_report(
        portfolio_value=portfolio_value,
        positions=positions,
        metrics={
            "volatility": 0.40,
            "var": 450,
            "cvar": 600,
            "sharpe": 1.8,
            "max_drawdown": 0.12
        },
        concentration={"is_concentrated": False, "total_exposure": 0.3}
    )

    # Export
    dashboard.export_risk_report(report, format="json")

    cprint("\n✅ Risk dashboard example complete!", "white", "on_green")

#!/usr/bin/env python3
"""
ADAPTIVE RISK MANAGER
=====================

Intelligent risk management that adapts to market conditions
No more fixed stop losses - dynamic portfolio protection
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
import numpy as np
from enum import Enum
import statistics

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class RiskLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class MarketRegime(Enum):
    BULL = "BULL"      # Rising market, low volatility
    BEAR = "BEAR"      # Falling market, high volatility
    SIDEWAYS = "SIDEWAYS"  # Range-bound market
    CHAOTIC = "CHAOTIC"    # High volatility, no clear trend

@dataclass
class Position:
    """Current trading position"""
    token: str
    size: float  # USD value
    side: str  # 'LONG' or 'SHORT'
    entry_price: float
    current_price: float
    unrealized_pnl: float
    strategy_type: str
    entry_time: datetime

@dataclass
class RiskMetrics:
    """Real-time portfolio risk metrics"""
    portfolio_value: float
    total_exposure: float
    unrealized_pnl: float
    daily_pnl: float
    max_drawdown: float
    var_95: float  # Value at Risk 95%
    beta_portfolio: float
    correlation_risk: float
    regime: MarketRegime
    risk_level: RiskLevel
    recommended_action: str

class AdaptiveRiskManager:
    """
    Intelligent risk management - protects portfolio from all risks
    """

    def __init__(self, initial_portfolio_value: float = 10000):
        self.initial_value = initial_portfolio_value
        self.current_value = initial_portfolio_value
        self.positions = []
        self.daily_high = initial_portfolio_value
        self.daily_low = initial_portfolio_value
        self.daily_start = initial_portfolio_value

        # Risk limits
        self.max_portfolio_risk = 0.15  # Max 15% portfolio risk
        self.max_position_size = 0.25   # Max 25% per position
        self.max_correlation = 0.7      # Max correlation between positions
        self.var_limit = 0.05           # Max 5% daily VaR

        # Risk tracking
        self.pnl_history = []
        self.drawdown_history = []
        self.regime_history = []

    def print_message(self, message, msg_type="info"):
        """Print without Unicode issues"""
        if msg_type == "success":
            print(f"[SUCCESS] {message}")
        elif msg_type == "warning":
            print(f"[WARNING] {message}")
        elif msg_type == "error":
            print(f"[ERROR] {message}")
        elif msg_type == "alert":
            print(f"[ALERT] {message}")
        else:
            print(f"[INFO] {message}")

    def detect_market_regime(self, market_data: Dict) -> MarketRegime:
        """
        Detect current market regime for risk adjustment
        """
        try:
            # Mock regime detection - replace with real analysis
            btc_change = market_data.get('btc_change_24h', 0.01)
            btc_volatility = market_data.get('btc_volatility', 0.025)

            fear_greed = market_data.get('fear_greed_index', 50)
            funding_pressure = market_data.get('avg_funding_rate', 0.001)

            # Regime detection logic
            if btc_change > 0.05 and btc_volatility < 0.03 and fear_greed > 60:
                return MarketRegime.BULL
            elif btc_change < -0.05 and btc_volatility > 0.04 and fear_greed < 40:
                return MarketRegime.BEAR
            elif btc_volatility > 0.06:
                return MarketRegime.CHAOTIC
            else:
                return MarketRegime.SIDEWAYS

        except Exception as e:
            self.print_message(f"Error detecting market regime: {e}", "error")
            return MarketRegime.SIDEWAYS

    def calculate_position_risk(self, position: Position, market_data: Dict) -> float:
        """
        Calculate risk contribution of individual position
        """
        try:
            # Get volatility for the token
            token_vol = market_data.get(f'{position.token}_volatility', 0.03)

            # Position risk = size * volatility * regime multiplier
            regime = self.detect_market_regime(market_data)
            regime_multiplier = {
                MarketRegime.BULL: 0.8,
                MarketRegime.SIDEWAYS: 1.0,
                MarketRegime.BEAR: 1.2,
                MarketRegime.CHAOTIC: 1.5
            }[regime]

            # Risk score
            risk_score = position.size * token_vol * regime_multiplier / self.current_value

            return risk_score

        except Exception as e:
            self.print_message(f"Error calculating position risk: {e}", "error")
            return 0.1  # Default high risk

    def calculate_portfolio_var(self, confidence: float = 0.95) -> float:
        """
        Calculate Portfolio Value at Risk
        """
        try:
            if len(self.pnl_history) < 20:
                return self.var_limit  # Use default if insufficient data

            # Calculate daily returns
            returns = [pnl / self.current_value for pnl in self.pnl_history[-252:]]  # Last year

            if not returns:
                return self.var_limit

            # Calculate VaR using historical method
            returns.sort()
            var_index = int((1 - confidence) * len(returns))
            var_95 = abs(returns[var_index]) if var_index < len(returns) else self.var_limit

            return var_95

        except Exception as e:
            self.print_message(f"Error calculating VaR: {e}", "error")
            return self.var_limit

    def calculate_correlation_risk(self) -> float:
        """
        Calculate correlation risk between positions
        """
        try:
            if len(self.positions) < 2:
                return 0.0

            # Simple correlation check based on strategy types
            strategy_risks = {
                'carry_trade': 0.3,      # Low correlation (market neutral)
                'liquidity_hunting': 0.8, # High correlation (market direction)
                'microstructure': 0.2,    # Very low correlation
                'volatility_normalization': 0.6,
                'correlation_arbitrage': 0.9  # High correlation (uses correlations)
            }

            # Calculate average correlation
            total_correlation = 0
            for pos in self.positions:
                total_correlation += strategy_risks.get(pos.strategy_type, 0.5)

            avg_correlation = total_correlation / len(self.positions) if self.positions else 0

            return min(avg_correlation, 1.0)

        except Exception as e:
            self.print_message(f"Error calculating correlation risk: {e}", "error")
            return 0.7

    def assess_risk_level(self, metrics: Dict) -> RiskLevel:
        """
        Determine overall portfolio risk level
        """
        risk_score = 0

        # Portfolio utilization risk
        utilization = metrics['total_exposure'] / self.current_value
        if utilization > 0.8:
            risk_score += 30
        elif utilization > 0.6:
            risk_score += 20
        elif utilization > 0.4:
            risk_score += 10

        # Drawdown risk
        if metrics['max_drawdown'] > 0.10:
            risk_score += 25
        elif metrics['max_drawdown'] > 0.05:
            risk_score += 15
        elif metrics['max_drawdown'] > 0.02:
            risk_score += 5

        # VaR risk
        if metrics['var_95'] > self.var_limit:
            risk_score += 20
        elif metrics['var_95'] > self.var_limit * 0.8:
            risk_score += 10

        # Correlation risk
        if metrics['correlation_risk'] > self.max_correlation:
            risk_score += 15
        elif metrics['correlation_risk'] > self.max_correlation * 0.8:
            risk_score += 8

        # Market regime risk
        regime = metrics['regime']
        if regime == MarketRegime.CHAOTIC:
            risk_score += 20
        elif regime == MarketRegime.BEAR:
            risk_score += 15
        elif regime == MarketRegime.BULL:
            risk_score += 5

        # Determine risk level
        if risk_score >= 70:
            return RiskLevel.CRITICAL
        elif risk_score >= 50:
            return RiskLevel.HIGH
        elif risk_score >= 30:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def generate_risk_recommendations(self, risk_level: RiskLevel, metrics: Dict) -> List[str]:
        """
        Generate actionable risk management recommendations
        """
        recommendations = []

        if risk_level == RiskLevel.CRITICAL:
            recommendations.extend([
                "IMMEDIATE ACTION REQUIRED",
                "Close 50% of all positions immediately",
                "Stop all new trading activity",
                "Review position sizing strategy",
                "Consider moving to cash"
            ])

        elif risk_level == RiskLevel.HIGH:
            if metrics['total_exposure'] / self.current_value > 0.7:
                recommendations.append("Reduce portfolio exposure to below 60%")

            if metrics['max_drawdown'] > 0.08:
                recommendations.append("Implement circuit breakers on losing positions")

            if metrics['correlation_risk'] > self.max_correlation:
                recommendations.append("Diversify across different strategy types")

            recommendations.append("Increase position stop losses by 50%")

        elif risk_level == RiskLevel.MEDIUM:
            if metrics['total_exposure'] / self.current_value > 0.5:
                recommendations.append("Consider reducing position sizes")

            if metrics['var_95'] > self.var_limit * 0.8:
                recommendations.append("Monitor daily losses closely")

            recommendations.append("Review risk limits weekly")

        else:  # LOW risk
            recommendations.extend([
                "Current risk level is acceptable",
                "Consider gradually increasing position sizes",
                "Monitor for regime changes"
            ])

        return recommendations

    def update_positions(self, new_positions: List[Dict]):
        """
        Update current positions
        """
        self.positions = []

        for pos_data in new_positions:
            position = Position(
                token=pos_data.get('token', 'UNKNOWN'),
                size=pos_data.get('size', 0),
                side=pos_data.get('side', 'LONG'),
                entry_price=pos_data.get('entry_price', 0),
                current_price=pos_data.get('current_price', 0),
                unrealized_pnl=pos_data.get('unrealized_pnl', 0),
                strategy_type=pos_data.get('strategy_type', 'unknown'),
                entry_time=pos_data.get('entry_time', datetime.now())
            )
            self.positions.append(position)

    def calculate_risk_metrics(self, market_data: Dict = None) -> RiskMetrics:
        """
        Calculate comprehensive risk metrics
        """
        try:
            if market_data is None:
                market_data = {}

            # Calculate total exposure and PnL
            total_exposure = sum(pos.size for pos in self.positions)
            unrealized_pnl = sum(pos.unrealized_pnl for pos in self.positions)

            # Calculate daily PnL (mock - would come from actual trading)
            daily_pnl = unrealized_pnl  # Simplified

            # Update portfolio value
            self.current_value = self.initial_value + daily_pnl

            # Calculate max drawdown
            current_drawdown = (self.daily_high - self.current_value) / self.daily_high
            self.drawdown_history.append(current_drawdown)
            max_drawdown = max(self.drawdown_history[-30:]) if self.drawdown_history else 0  # 30-day max

            # Calculate VaR
            var_95 = self.calculate_portfolio_var(0.95)

            # Calculate portfolio beta (mock)
            beta_portfolio = 1.2 if self.positions else 1.0

            # Calculate correlation risk
            correlation_risk = self.calculate_correlation_risk()

            # Detect market regime
            regime = self.detect_market_regime(market_data)

            # Assess overall risk level
            metrics = {
                'total_exposure': total_exposure,
                'max_drawdown': max_drawdown,
                'var_95': var_95,
                'correlation_risk': correlation_risk,
                'regime': regime
            }

            risk_level = self.assess_risk_level(metrics)

            # Generate recommendations
            recommendations = self.generate_risk_recommendations(risk_level, metrics)
            recommended_action = recommendations[0] if recommendations else "No action needed"

            return RiskMetrics(
                portfolio_value=self.current_value,
                total_exposure=total_exposure,
                unrealized_pnl=unrealized_pnl,
                daily_pnl=daily_pnl,
                max_drawdown=max_drawdown,
                var_95=var_95,
                beta_portfolio=beta_portfolio,
                correlation_risk=correlation_risk,
                regime=regime,
                risk_level=risk_level,
                recommended_action=recommended_action
            )

        except Exception as e:
            self.print_message(f"Error calculating risk metrics: {e}", "error")
            return RiskMetrics(
                portfolio_value=self.current_value,
                total_exposure=0,
                unrealized_pnl=0,
                daily_pnl=0,
                max_drawdown=0,
                var_95=self.var_limit,
                beta_portfolio=1.0,
                correlation_risk=0.5,
                regime=MarketRegime.SIDEWAYS,
                risk_level=RiskLevel.MEDIUM,
                recommended_action="Error calculating risk"
            )

    def print_risk_dashboard(self, risk_metrics: RiskMetrics):
        """
        Print comprehensive risk dashboard
        """
        print(f"\nRISK MANAGEMENT DASHBOARD")
        print("=" * 60)

        # Portfolio status
        print(f"Portfolio Value: ${risk_metrics.portfolio_value:,.2f}")
        print(f"Daily P&L: ${risk_metrics.daily_pnl:,.2f}")
        print(f"Total Exposure: ${risk_metrics.total_exposure:,.2f} ({risk_metrics.total_exposure/risk_metrics.portfolio_value:.1%})")

        # Risk metrics
        risk_color = {
            RiskLevel.LOW: "GREEN",
            RiskLevel.MEDIUM: "YELLOW",
            RiskLevel.HIGH: "ORANGE",
            RiskLevel.CRITICAL: "RED"
        }[risk_metrics.risk_level]

        print(f"\nRISK LEVEL: {risk_metrics.risk_level.value} [{risk_color}]")
        print(f"Max Drawdown: {risk_metrics.max_drawdown:.2%}")
        print(f"Value at Risk (95%): {risk_metrics.var_95:.2%}")
        print(f"Correlation Risk: {risk_metrics.correlation_risk:.2%}")
        print(f"Market Regime: {risk_metrics.regime.value}")

        # Recommendations
        print(f"\nRECOMMENDATION:")
        print(f"  {risk_metrics.recommended_action}")

        # Position breakdown
        if self.positions:
            print(f"\nPOSITION BREAKDOWN:")
            for pos in self.positions[:5]:  # Top 5 positions
                pnl_color = "GREEN" if pos.unrealized_pnl > 0 else "RED"
                print(f"  {pos.token}: ${pos.size:,.0f} {pos.side} | P&L: ${pos.unrealized_pnl:,.2f} [{pnl_color}]")

async def main():
    """Test the adaptive risk manager"""
    print("ADAPTIVE RISK MANAGER")
    print("=" * 40)
    print("Intelligent portfolio protection system")

    risk_manager = AdaptiveRiskManager(initial_portfolio_value=10000)

    try:
        # Mock current positions
        mock_positions = [
            {
                'token': 'BTC',
                'size': 2000,
                'side': 'LONG',
                'entry_price': 45000,
                'current_price': 46000,
                'unrealized_pnl': 44.44,  # (46000-45000)/45000 * 2000
                'strategy_type': 'liquidity_hunting',
                'entry_time': datetime.now() - timedelta(hours=2)
            },
            {
                'token': 'SOL',
                'size': 1500,
                'side': 'SHORT',
                'entry_price': 65,
                'current_price': 63,
                'unrealized_pnl': 46.15,  # (65-63)/65 * 1500
                'strategy_type': 'correlation_arbitrage',
                'entry_time': datetime.now() - timedelta(hours=1)
            },
            {
                'token': 'ETH',
                'size': 800,
                'side': 'LONG',
                'entry_price': 2400,
                'current_price': 2420,
                'unrealized_pnl': 6.67,
                'strategy_type': 'volatility_normalization',
                'entry_time': datetime.now() - timedelta(minutes=30)
            }
        ]

        # Update positions
        risk_manager.update_positions(mock_positions)

        # Mock market data
        market_data = {
            'btc_change_24h': 0.022,
            'btc_volatility': 0.025,
            'fear_greed_index': 58,
            'avg_funding_rate': 0.002
        }

        # Calculate risk metrics
        risk_metrics = risk_manager.calculate_risk_metrics(market_data)

        # Display dashboard
        risk_manager.print_risk_dashboard(risk_metrics)

        return risk_manager, risk_metrics

    except Exception as e:
        risk_manager.print_message(f"Risk management failed: {e}", "error")
        return risk_manager, None

if __name__ == "__main__":
    risk_manager, risk_metrics = asyncio.run(main())
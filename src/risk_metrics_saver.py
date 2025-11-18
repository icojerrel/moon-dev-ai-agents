#!/usr/bin/env python3
"""
Risk Metrics Saver
==================

Saves risk management metrics to JSON files
"""

import json
import datetime
import asyncio
import sys
import os

# Add src to path
sys.path.append('/app/src')

from adaptive_risk_manager import AdaptiveRiskManager

async def save_risk_metrics():
    """Calculate and save risk metrics"""

    # Create risk directory
    risk_dir = '/app/data/risk'
    os.makedirs(risk_dir, exist_ok=True)

    # Initialize risk manager
    risk_manager = AdaptiveRiskManager(initial_portfolio_value=10000)

    # Mock positions for demo
    mock_positions = [
        {
            'token': 'BTC',
            'size': 2000,
            'side': 'LONG',
            'entry_price': 45000,
            'current_price': 46000,
            'unrealized_pnl': 44.44,
            'strategy_type': 'liquidity_hunting',
            'entry_time': datetime.datetime.now() - datetime.timedelta(hours=2)
        }
    ]

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

    # Convert to JSON format
    risk_data = {
        'timestamp': datetime.datetime.now().isoformat(),
        'portfolio_value': risk_metrics.portfolio_value,
        'risk_level': risk_metrics.risk_level.value,
        'total_exposure': risk_metrics.total_exposure,
        'max_drawdown': risk_metrics.max_drawdown,
        'var_95': risk_metrics.var_95,
        'correlation_risk': risk_metrics.correlation_risk,
        'market_regime': risk_metrics.regime.value,
        'recommended_action': risk_metrics.recommended_action
    }

    # Save to file
    filename = f'{risk_dir}/risk_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json'

    with open(filename, 'w') as f:
        json.dump(risk_data, f, indent=2)

    print(f'[RISK] Saved risk metrics: {risk_metrics.risk_level.value} risk level to {filename}')

if __name__ == "__main__":
    asyncio.run(save_risk_metrics())
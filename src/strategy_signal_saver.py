#!/usr/bin/env python3
"""
Strategy Signal Saver
=====================

Saves generated signals to JSON files for the trading system
"""

import json
import datetime
import asyncio
import sys
import os

# Add src to path
sys.path.append('/app/src')

from robust_strategy_framework import RobustStrategyFramework

async def save_signals():
    """Generate and save strategy signals"""

    # Create signals directory
    signals_dir = '/app/data/signals'
    os.makedirs(signals_dir, exist_ok=True)

    # Generate signals
    framework = RobustStrategyFramework(portfolio_value=10000)
    signals = await framework.generate_all_signals()

    # Convert to JSON format
    signal_data = [{
        'timestamp': datetime.datetime.now().isoformat(),
        'strategy_type': s.strategy_type.value,
        'token': s.token,
        'action': s.action,
        'confidence': s.confidence,
        'position_size': s.position_size,
        'reasoning': s.reasoning,
        'metadata': s.metadata
    } for s in signals]

    # Save to file
    filename = f'{signals_dir}/signals_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json'

    with open(filename, 'w') as f:
        json.dump(signal_data, f, indent=2)

    print(f'[STRATEGY] Saved {len(signals)} signals to {filename}')

if __name__ == "__main__":
    asyncio.run(save_signals())
"""
📄 Paper Trading Script
=======================
Safe paper trading with REAL market data, SIMULATED trades

This script:
- Fetches real-time market data from BirdEye API
- Uses DeepSeek Director for trading decisions
- SIMULATES all trades (NO real money at risk)
- Tracks performance and logs all decisions
- Perfect for testing strategies safely

NO REAL TRADES ARE EXECUTED!
"""

import sys
import os
import time
import json
from pathlib import Path
from datetime import datetime, timedelta
from termcolor import cprint

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.config import *

# Try to import nice_funcs for market data
try:
    from src.nice_funcs import token_overview, token_price
    HAS_MARKET_DATA = True
except Exception as e:
    cprint(f"⚠️  Could not import market data functions: {str(e)}", "yellow")
    HAS_MARKET_DATA = False

# Try to import DeepSeek Director
try:
    from src.agents.deepseek_director_agent import DeepSeekTradingDirector
    HAS_DIRECTOR = True
except Exception as e:
    cprint(f"⚠️  Could not import DeepSeek Director: {str(e)}", "yellow")
    HAS_DIRECTOR = False


class PaperTradingSimulator:
    """
    Paper Trading Simulator with Real Market Data

    Simulates trading with:
    - Real market data from BirdEye
    - DeepSeek Director decisions
    - Simulated portfolio tracking
    - Performance metrics
    """

    def __init__(self, starting_balance: float = 1000):
        """
        Initialize paper trading simulator

        Args:
            starting_balance: Starting paper trading balance (default: $1000)
        """
        self.starting_balance = starting_balance
        self.current_balance = starting_balance
        self.positions = {}  # {token: {'amount': float, 'entry_price': float, 'pnl': float}}
        self.trade_history = []
        self.decision_history = []

        # Performance tracking
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_pnl = 0

        # Initialize DeepSeek Director if available
        if HAS_DIRECTOR:
            self.director = DeepSeekTradingDirector(config={
                'max_strategies': 1,  # Paper trading: start simple
                'risk_tolerance': 'low',
                'enable_trade_approval': True,
                'reasoning_temperature': 0.3
            })
        else:
            self.director = None

        # Create output directory
        self.output_dir = Path("src/data/paper_trading")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        cprint("\n📄 Paper Trading Simulator Initialized", "green", attrs=['bold'])
        cprint(f"💰 Starting Balance: ${starting_balance:,.2f}", "cyan")
        cprint(f"🎯 DeepSeek Director: {'✅ Active' if HAS_DIRECTOR else '❌ Not available'}", "cyan")
        cprint(f"📊 Market Data: {'✅ Active' if HAS_MARKET_DATA else '❌ Not available'}\n", "cyan")

    def fetch_market_data(self, tokens: list) -> dict:
        """
        Fetch real market data for tokens

        Args:
            tokens: List of token addresses

        Returns:
            Dict with market data per token
        """
        if not HAS_MARKET_DATA:
            cprint("⚠️  Market data not available - using simulated data", "yellow")
            return self._generate_simulated_data(tokens)

        market_data = {}

        for token in tokens:
            try:
                # Fetch token overview
                overview = token_overview(token)

                if overview:
                    market_data[token] = {
                        'symbol': overview.get('symbol', 'UNKNOWN'),
                        'price': overview.get('price', 0),
                        'volume_24h': overview.get('volume', 0),
                        'price_change_24h': overview.get('change_24h', 0),
                        'liquidity': overview.get('liquidity', 0)
                    }
                    cprint(f"  ✅ {market_data[token]['symbol']}: ${market_data[token]['price']:.6f}", "green")
                else:
                    cprint(f"  ⚠️  No data for token {token[:8]}...", "yellow")

            except Exception as e:
                cprint(f"  ❌ Error fetching {token[:8]}...: {str(e)}", "red")

        return market_data

    def _generate_simulated_data(self, tokens: list) -> dict:
        """Generate simulated market data for testing"""
        import random

        market_data = {}
        for token in tokens:
            market_data[token] = {
                'symbol': f'TOKEN{len(market_data)+1}',
                'price': random.uniform(0.001, 10.0),
                'volume_24h': random.uniform(10000, 1000000),
                'price_change_24h': random.uniform(-20, 20),
                'liquidity': random.uniform(50000, 500000)
            }

        return market_data

    def simulate_trade(self, action: str, token: str, amount: float, price: float, reasoning: str):
        """
        Simulate a trade (NO REAL EXECUTION)

        Args:
            action: 'BUY' or 'SELL'
            token: Token address
            amount: USD amount to trade
            price: Current price
            reasoning: Reason for trade
        """
        timestamp = datetime.now()

        if action == 'BUY':
            # Simulate buy
            if self.current_balance >= amount:
                token_amount = amount / price
                self.current_balance -= amount

                if token not in self.positions:
                    self.positions[token] = {
                        'amount': 0,
                        'avg_entry_price': 0,
                        'total_cost': 0
                    }

                # Update position
                old_amount = self.positions[token]['amount']
                old_cost = self.positions[token]['total_cost']
                new_cost = old_cost + amount

                self.positions[token]['amount'] = old_amount + token_amount
                self.positions[token]['total_cost'] = new_cost
                self.positions[token]['avg_entry_price'] = new_cost / self.positions[token]['amount']

                self.total_trades += 1

                cprint(f"\n✅ SIMULATED BUY", "green", attrs=['bold'])
                cprint(f"   Token: {token[:8]}...", "white")
                cprint(f"   Amount: ${amount:.2f}", "white")
                cprint(f"   Price: ${price:.6f}", "white")
                cprint(f"   Tokens: {token_amount:.2f}", "white")
                cprint(f"   Reason: {reasoning}", "cyan")

                # Log trade
                self.trade_history.append({
                    'timestamp': timestamp.isoformat(),
                    'action': 'BUY',
                    'token': token,
                    'amount_usd': amount,
                    'price': price,
                    'token_amount': token_amount,
                    'reasoning': reasoning
                })

            else:
                cprint(f"\n❌ Insufficient balance for BUY: ${self.current_balance:.2f} < ${amount:.2f}", "red")

        elif action == 'SELL':
            # Simulate sell
            if token in self.positions and self.positions[token]['amount'] > 0:
                token_amount = self.positions[token]['amount']
                sell_value = token_amount * price
                entry_price = self.positions[token]['avg_entry_price']
                pnl = (price - entry_price) * token_amount

                self.current_balance += sell_value
                self.total_pnl += pnl

                if pnl > 0:
                    self.winning_trades += 1
                else:
                    self.losing_trades += 1

                cprint(f"\n✅ SIMULATED SELL", "green" if pnl > 0 else "red", attrs=['bold'])
                cprint(f"   Token: {token[:8]}...", "white")
                cprint(f"   Amount: {token_amount:.2f} tokens", "white")
                cprint(f"   Value: ${sell_value:.2f}", "white")
                cprint(f"   Entry: ${entry_price:.6f}", "white")
                cprint(f"   Exit: ${price:.6f}", "white")
                cprint(f"   PnL: ${pnl:.2f} ({(pnl/self.positions[token]['total_cost'])*100:.2f}%)", "green" if pnl > 0 else "red", attrs=['bold'])
                cprint(f"   Reason: {reasoning}", "cyan")

                # Remove position
                del self.positions[token]
                self.total_trades += 1

                # Log trade
                self.trade_history.append({
                    'timestamp': timestamp.isoformat(),
                    'action': 'SELL',
                    'token': token,
                    'amount_usd': sell_value,
                    'price': price,
                    'token_amount': token_amount,
                    'pnl': pnl,
                    'pnl_pct': (pnl/self.positions[token]['total_cost'])*100 if self.positions[token]['total_cost'] > 0 else 0,
                    'reasoning': reasoning
                })

            else:
                cprint(f"\n❌ No position to sell for token {token[:8]}...", "red")

    def run_paper_trading_cycle(self):
        """Run one paper trading cycle"""

        cprint("\n" + "="*80, "cyan")
        cprint(f"📄 PAPER TRADING CYCLE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "cyan", attrs=['bold'])
        cprint("="*80, "cyan")

        # Step 1: Fetch market data
        cprint("\n[1/4] Fetching real market data...", "yellow", attrs=['bold'])
        tokens = MONITORED_TOKENS[:3]  # Start with 3 tokens for paper trading
        market_data = self.fetch_market_data(tokens)

        if not market_data:
            cprint("❌ No market data available - skipping cycle", "red")
            return

        # Step 2: Prepare data for Director
        cprint("\n[2/4] Preparing data for analysis...", "yellow", attrs=['bold'])
        director_input = {
            'tokens': [
                {
                    'address': token,
                    'symbol': data['symbol'],
                    'price': data['price'],
                    'volume_24h': data['volume_24h'],
                    'price_change_24h': data['price_change_24h']
                }
                for token, data in market_data.items()
            ],
            'balance': self.current_balance,
            'positions': [
                {
                    'token': token,
                    'amount': pos['amount'],
                    'value': pos['amount'] * market_data.get(token, {}).get('price', 0)
                }
                for token, pos in self.positions.items()
            ],
            'sentiment': 'neutral',  # Placeholder
            'whale_activity': 'normal'  # Placeholder
        }

        # Step 3: Get Director decision (if available)
        cprint("\n[3/4] Analyzing with DeepSeek Director...", "yellow", attrs=['bold'])

        if HAS_DIRECTOR and self.director:
            try:
                # Run director analysis
                regime_analysis = self.director.analyze_market_regime(director_input)

                # Get strategy recommendations
                strategies = self.director.select_strategies(
                    regime_analysis['regime'],
                    regime_analysis.get('recommended_risk_level', 'low')
                )

                # Simulate a trade proposal based on regime
                if regime_analysis['regime'] == 'trending_bullish' and len(market_data) > 0:
                    # Propose buy for best performing token
                    best_token = max(market_data.items(), key=lambda x: x[1]['price_change_24h'])
                    token_addr, token_data = best_token

                    trade_proposal = {
                        'action': 'BUY',
                        'token': token_addr,
                        'amount': min(usd_size, self.current_balance * 0.1),  # 10% of balance or usd_size
                        'strategy': 'paper_trading_momentum',
                        'reasoning': f"Bullish regime detected. {token_data['symbol']} up {token_data['price_change_24h']:.2f}% in 24h"
                    }

                    # Get approval
                    approved, approval_reasoning = self.director.approve_trade(trade_proposal)

                    if approved:
                        self.simulate_trade(
                            action='BUY',
                            token=token_addr,
                            amount=trade_proposal['amount'],
                            price=token_data['price'],
                            reasoning=approval_reasoning
                        )
                    else:
                        cprint(f"\n❌ Trade REJECTED by Director", "red")
                        cprint(f"   Reason: {approval_reasoning}", "yellow")

            except Exception as e:
                cprint(f"❌ Error in Director analysis: {str(e)}", "red")

        else:
            cprint("⚠️  DeepSeek Director not available - basic simulation only", "yellow")

        # Step 4: Display portfolio status
        self.display_portfolio()

        # Export state
        self.export_state()

    def display_portfolio(self):
        """Display current portfolio status"""

        cprint("\n" + "="*80, "green")
        cprint("💼 PORTFOLIO STATUS", "green", attrs=['bold'])
        cprint("="*80, "green")

        # Cash
        cprint(f"\n💵 Cash: ${self.current_balance:,.2f}", "cyan")

        # Positions
        if self.positions:
            cprint(f"\n📊 Open Positions ({len(self.positions)}):", "yellow", attrs=['bold'])
            for token, pos in self.positions.items():
                cprint(f"  • {token[:8]}...", "white")
                cprint(f"    Amount: {pos['amount']:.2f} tokens", "white")
                cprint(f"    Avg Entry: ${pos['avg_entry_price']:.6f}", "white")
                cprint(f"    Cost: ${pos['total_cost']:.2f}", "white")
        else:
            cprint(f"\n📊 No open positions", "yellow")

        # Performance
        total_value = self.current_balance + sum(
            pos['total_cost'] for pos in self.positions.values()
        )
        total_return = total_value - self.starting_balance
        total_return_pct = (total_return / self.starting_balance) * 100

        cprint(f"\n📈 Performance Summary:", "cyan", attrs=['bold'])
        cprint(f"  Starting Balance: ${self.starting_balance:,.2f}", "white")
        cprint(f"  Current Value:    ${total_value:,.2f}", "white")
        cprint(f"  Total Return:     ${total_return:,.2f} ({total_return_pct:+.2f}%)", "green" if total_return >= 0 else "red", attrs=['bold'])
        cprint(f"  Total Trades:     {self.total_trades}", "white")
        cprint(f"  Winning Trades:   {self.winning_trades}", "green")
        cprint(f"  Losing Trades:    {self.losing_trades}", "red")

        if self.total_trades > 0:
            win_rate = (self.winning_trades / self.total_trades) * 100
            cprint(f"  Win Rate:         {win_rate:.1f}%", "cyan")

        cprint("\n" + "="*80, "green")

    def export_state(self):
        """Export current state to JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        state_file = self.output_dir / f"paper_trading_state_{timestamp}.json"

        state = {
            'timestamp': datetime.now().isoformat(),
            'starting_balance': self.starting_balance,
            'current_balance': self.current_balance,
            'positions': self.positions,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'total_pnl': self.total_pnl,
            'trade_history': self.trade_history[-10:],  # Last 10 trades
        }

        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)

        cprint(f"\n📁 State exported: {state_file}", "green")


def main():
    """Main paper trading loop"""

    cprint("\n" + "="*80, "white", "on_blue")
    cprint("📄 PAPER TRADING MODE - Real Data, Simulated Trades", "white", "on_blue", attrs=['bold'])
    cprint("="*80, "white", "on_blue")

    cprint("\n⚠️  PAPER TRADING MODE", "yellow", attrs=['bold'])
    cprint("  • Real market data from BirdEye API", "white")
    cprint("  • DeepSeek Director AI decisions", "white")
    cprint("  • NO real trades executed", "white")
    cprint("  • NO real money at risk", "white")
    cprint("  • Safe testing environment\n", "white")

    # Initialize simulator
    simulator = PaperTradingSimulator(starting_balance=1000)

    try:
        cycle_count = 0
        while True:
            cycle_count += 1

            # Run one cycle
            simulator.run_paper_trading_cycle()

            # Sleep before next cycle
            cprint(f"\n😴 Sleeping {SLEEP_BETWEEN_RUNS_MINUTES} minutes until next cycle...", "cyan")
            cprint(f"   (Cycle {cycle_count} complete | Press Ctrl+C to stop)\n", "white")

            time.sleep(60 * SLEEP_BETWEEN_RUNS_MINUTES)

    except KeyboardInterrupt:
        cprint("\n\n👋 Paper trading stopped by user", "yellow")

        # Final portfolio display
        simulator.display_portfolio()

        cprint("\n📊 Paper trading session complete", "green")
        cprint(f"💾 Check results in: {simulator.output_dir}\n", "cyan")


if __name__ == "__main__":
    main()

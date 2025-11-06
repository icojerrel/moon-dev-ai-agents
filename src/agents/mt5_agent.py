#!/usr/bin/env python3
"""
🌙 Moon Dev's MT5 Trading Agent
Built with love by Moon Dev 🚀

AI-powered paper trading agent for MetaTrader 5 using qwen3-coder:30b
"""

import sys
from pathlib import Path
from termcolor import cprint
from datetime import datetime, timedelta
import time
import pandas as pd
from typing import Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.mt5.mt5_connection import MT5Connection
from src.models.model_factory import ModelFactory


class MT5TradingAgent:
    """AI-powered MT5 trading agent using qwen3-coder"""

    def __init__(self, paper_trading: bool = True, virtual_balance: float = 10000.0):
        """
        Initialize MT5 trading agent

        Args:
            paper_trading: Use paper trading mode (default: True)
            virtual_balance: Starting balance for paper trading
        """
        cprint("\n" + "="*70, "cyan", attrs=["bold"])
        cprint("  🌙 Moon Dev's MT5 Trading Agent", "cyan", attrs=["bold"])
        cprint("  Powered by Qwen3-Coder:30b", "cyan", attrs=["bold"])
        cprint("="*70 + "\n", "cyan")

        # Initialize MT5 connection
        self.mt5 = MT5Connection(paper_trading=paper_trading, virtual_balance=virtual_balance)

        # Initialize AI model
        cprint("🤖 Initializing AI model...", "yellow")
        self.factory = ModelFactory()

        if not self.factory.is_model_available("ollama"):
            cprint("❌ Ollama not available!", "red")
            cprint("   Make sure: ollama serve", "yellow")
            cprint("   And: ollama pull qwen3-coder:30b", "yellow")
            sys.exit(1)

        self.model = self.factory.get_model("ollama")
        cprint(f"✅ AI Model loaded: {self.model.model_name}\n", "green")

        # Trading parameters
        self.max_positions = 3
        self.risk_per_trade = 0.02  # 2% risk per trade
        self.symbols = ["EURUSD", "GBPUSD", "USDJPY"]  # Trading symbols

        # State
        self.running = False

    def connect_mt5(self) -> bool:
        """Connect to MT5"""
        return self.mt5.connect()

    def analyze_market(self, symbol: str, candles: pd.DataFrame) -> Dict:
        """
        Use AI to analyze market conditions

        Args:
            symbol: Trading symbol
            candles: Recent candlestick data

        Returns:
            Dict with analysis
        """
        cprint(f"\n🔍 Analyzing {symbol}...", "cyan")

        # Prepare market data summary
        last_candle = candles.iloc[-1]
        prev_candles = candles.tail(20)

        # Calculate simple metrics
        price_change = ((last_candle['Close'] - prev_candles['Close'].iloc[0]) /
                       prev_candles['Close'].iloc[0] * 100)

        high_20 = prev_candles['High'].max()
        low_20 = prev_candles['Low'].min()

        market_summary = f"""
Symbol: {symbol}
Current Price: {last_candle['Close']:.5f}
20-candle Change: {price_change:+.2f}%
20-candle High: {high_20:.5f}
20-candle Low: {low_20:.5f}

Recent 5 candles:
{candles[['datetime', 'Open', 'High', 'Low', 'Close']].tail(5).to_string()}
"""

        system_prompt = """You are a professional forex trading analyst.
Analyze the market data and provide a trading decision.

Your response MUST be in this EXACT format:

DECISION: BUY|SELL|HOLD
CONFIDENCE: 0-100
REASONING: [Your 2-3 sentence analysis]
STOP_LOSS: [Price level or NONE]
TAKE_PROFIT: [Price level or NONE]

Be conservative. Only recommend BUY or SELL if confidence > 70.
Use technical analysis principles."""

        user_content = f"""Analyze this market data and recommend a trade:

{market_summary}

Provide your analysis in the specified format."""

        cprint("🤔 AI is analyzing...", "yellow")
        start_time = time.time()

        response = self.model.generate_response(
            system_prompt=system_prompt,
            user_content=user_content,
            temperature=0.3,  # Lower temp for more consistent decisions
            max_tokens=500
        )

        elapsed = time.time() - start_time
        cprint(f"✅ Analysis complete in {elapsed:.1f}s", "green")

        # Parse AI response
        analysis = self._parse_ai_response(response.content)
        analysis['elapsed_time'] = elapsed

        return analysis

    def _parse_ai_response(self, response: str) -> Dict:
        """Parse AI response into structured format"""
        lines = response.strip().split('\n')

        analysis = {
            'decision': 'HOLD',
            'confidence': 0,
            'reasoning': '',
            'stop_loss': None,
            'take_profit': None,
            'raw_response': response
        }

        for line in lines:
            line = line.strip()
            if line.startswith('DECISION:'):
                decision = line.split(':', 1)[1].strip().upper()
                if decision in ['BUY', 'SELL', 'HOLD']:
                    analysis['decision'] = decision

            elif line.startswith('CONFIDENCE:'):
                try:
                    conf = line.split(':', 1)[1].strip()
                    analysis['confidence'] = int(conf.split()[0])  # Handle "75%" or "75"
                except:
                    pass

            elif line.startswith('REASONING:'):
                analysis['reasoning'] = line.split(':', 1)[1].strip()

            elif line.startswith('STOP_LOSS:'):
                sl_str = line.split(':', 1)[1].strip()
                if sl_str.upper() != 'NONE':
                    try:
                        analysis['stop_loss'] = float(sl_str)
                    except:
                        pass

            elif line.startswith('TAKE_PROFIT:'):
                tp_str = line.split(':', 1)[1].strip()
                if tp_str.upper() != 'NONE':
                    try:
                        analysis['take_profit'] = float(tp_str)
                    except:
                        pass

        return analysis

    def execute_trade(self, symbol: str, analysis: Dict) -> bool:
        """
        Execute trade based on AI analysis

        Args:
            symbol: Trading symbol
            analysis: AI analysis result

        Returns:
            True if trade executed
        """
        decision = analysis['decision']
        confidence = analysis['confidence']

        # Check if we should trade
        if decision == 'HOLD' or confidence < 70:
            cprint(f"⏸️  {decision} - Confidence too low ({confidence}%)", "yellow")
            return False

        # Check max positions
        positions = self.mt5.get_positions()
        if len(positions) >= self.max_positions:
            cprint(f"⏸️  Max positions reached ({self.max_positions})", "yellow")
            return False

        # Calculate position size based on risk
        account = self.mt5.get_account_info()
        risk_amount = account['balance'] * self.risk_per_trade

        # Get current price
        prices = self.mt5.get_price(symbol)
        if not prices:
            cprint("❌ Could not get price", "red")
            return False

        bid, ask = prices
        entry_price = ask if decision == "BUY" else bid

        # Calculate lot size (simplified)
        # In reality, you'd factor in stop loss distance
        lot_size = 0.01  # Start small for paper trading

        cprint(f"\n{'='*70}", "green")
        cprint(f"📊 TRADE SIGNAL", "green", attrs=["bold"])
        cprint(f"{'='*70}", "green")
        cprint(f"  Symbol: {symbol}", "white")
        cprint(f"  Decision: {decision}", "green", attrs=["bold"])
        cprint(f"  Confidence: {confidence}%", "white")
        cprint(f"  Reasoning: {analysis['reasoning']}", "white")
        cprint(f"  Entry Price: {entry_price:.5f}", "white")
        cprint(f"  Stop Loss: {analysis['stop_loss'] if analysis['stop_loss'] else 'None'}", "white")
        cprint(f"  Take Profit: {analysis['take_profit'] if analysis['take_profit'] else 'None'}", "white")
        cprint(f"  Lot Size: {lot_size}", "white")
        cprint(f"{'='*70}\n", "green")

        # Execute trade
        result = self.mt5.open_position(
            symbol=symbol,
            order_type=decision,
            volume=lot_size,
            sl=analysis['stop_loss'],
            tp=analysis['take_profit'],
            comment=f"AI Trade - {confidence}% conf"
        )

        if result['success']:
            cprint(f"✅ Trade executed! Ticket: {result['ticket']}", "green", attrs=["bold"])
            return True
        else:
            cprint(f"❌ Trade failed: {result.get('error', 'Unknown error')}", "red")
            return False

    def manage_positions(self):
        """Check and manage open positions"""
        positions = self.mt5.get_positions()

        if not positions:
            return

        cprint(f"\n📊 Managing {len(positions)} open position(s)...", "cyan")

        for pos in positions:
            cprint(f"\n  Position {pos['ticket']}:", "yellow")
            cprint(f"    Symbol: {pos['symbol']}", "white")
            cprint(f"    Type: {pos['type']}", "white")
            cprint(f"    Entry: {pos['entry_price']:.5f}", "white")
            cprint(f"    P/L: ${pos['profit']:,.2f}", "green" if pos['profit'] > 0 else "red")

            # Simple exit logic: Close if profit > $50 or loss > $20
            if pos['profit'] > 50:
                cprint("  ✅ Taking profit!", "green")
                self.mt5.close_position(pos['ticket'])
            elif pos['profit'] < -20:
                cprint("  🛑 Cutting loss!", "red")
                self.mt5.close_position(pos['ticket'])

    def run_trading_loop(self, interval_minutes: int = 60):
        """
        Run continuous trading loop

        Args:
            interval_minutes: Minutes between analysis cycles
        """
        if not self.mt5.connect():
            cprint("❌ Could not connect to MT5", "red")
            return

        self.running = True
        cycle = 0

        cprint("\n🚀 Starting trading loop...", "green", attrs=["bold"])
        cprint(f"  Interval: {interval_minutes} minutes", "white")
        cprint(f"  Symbols: {', '.join(self.symbols)}", "white")
        cprint(f"  Max Positions: {self.max_positions}", "white")
        cprint(f"  Risk per Trade: {self.risk_per_trade * 100}%", "white")
        cprint("\n  Press Ctrl+C to stop\n", "yellow")

        try:
            while self.running:
                cycle += 1
                cprint(f"\n{'█'*70}", "cyan")
                cprint(f"  CYCLE {cycle} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "cyan", attrs=["bold"])
                cprint(f"{'█'*70}\n", "cyan")

                # Show account status
                account = self.mt5.get_account_info()
                cprint(f"💰 Account Status:", "cyan", attrs=["bold"])
                cprint(f"  Balance: ${account['balance']:,.2f}", "white")
                cprint(f"  Equity: ${account['equity']:,.2f}", "white")
                cprint(f"  P/L: ${account['profit']:,.2f}", "green" if account['profit'] >= 0 else "red")

                # Manage existing positions
                self.manage_positions()

                # Analyze each symbol
                for symbol in self.symbols:
                    try:
                        # Get recent candles
                        candles = self.mt5.get_candles(symbol, timeframe="H1", count=50)

                        if candles is None:
                            cprint(f"⚠️  Could not get candles for {symbol}", "yellow")
                            continue

                        # AI analysis
                        analysis = self.analyze_market(symbol, candles)

                        cprint(f"\n📊 {symbol} Analysis:", "cyan")
                        cprint(f"  Decision: {analysis['decision']}", "white")
                        cprint(f"  Confidence: {analysis['confidence']}%", "white")
                        cprint(f"  Reasoning: {analysis['reasoning']}", "white")

                        # Execute if signal is strong
                        if analysis['decision'] in ['BUY', 'SELL'] and analysis['confidence'] >= 70:
                            self.execute_trade(symbol, analysis)

                    except Exception as e:
                        cprint(f"❌ Error analyzing {symbol}: {e}", "red")
                        continue

                # Wait for next cycle
                cprint(f"\n😴 Sleeping for {interval_minutes} minutes...", "yellow")
                time.sleep(interval_minutes * 60)

        except KeyboardInterrupt:
            cprint("\n\n⏸️  Trading loop stopped by user", "yellow")

        finally:
            self.running = False
            self.mt5.disconnect()

            # Show final stats
            account = self.mt5.get_account_info()
            cprint(f"\n{'='*70}", "cyan")
            cprint(f"📊 FINAL STATISTICS", "cyan", attrs=["bold"])
            cprint(f"{'='*70}", "cyan")
            cprint(f"  Final Balance: ${account['balance']:,.2f}", "white")
            cprint(f"  Final Equity: ${account['equity']:,.2f}", "white")
            cprint(f"  Total P/L: ${account['profit']:,.2f}", "green" if account['profit'] >= 0 else "red")

            if self.mt5.paper_trading:
                initial = self.mt5.initial_balance
                final = account['balance']
                pct_change = ((final - initial) / initial) * 100
                cprint(f"  Return: {pct_change:+.2f}%", "green" if pct_change >= 0 else "red")

            cprint(f"\n👋 Thanks for using Moon Dev's MT5 Agent! 🌙\n", "cyan")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Moon Dev MT5 Trading Agent')
    parser.add_argument('--live', action='store_true', help='Use live trading (default: paper)')
    parser.add_argument('--balance', type=float, default=10000, help='Starting balance for paper trading')
    parser.add_argument('--interval', type=int, default=60, help='Minutes between cycles (default: 60)')

    args = parser.parse_args()

    paper_trading = not args.live

    if not paper_trading:
        cprint("\n⚠️  WARNING: LIVE TRADING MODE!", "red", attrs=["bold"])
        cprint("This will execute REAL trades with REAL money!", "red")
        confirm = input("Type 'YES' to confirm: ")
        if confirm != 'YES':
            cprint("Cancelled.", "yellow")
            return

    # Initialize and run agent
    agent = MT5TradingAgent(
        paper_trading=paper_trading,
        virtual_balance=args.balance
    )

    agent.run_trading_loop(interval_minutes=args.interval)


if __name__ == "__main__":
    main()

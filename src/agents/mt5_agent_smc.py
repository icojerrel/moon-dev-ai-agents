#!/usr/bin/env python3
"""
🌙 Moon Dev's MT5 Trading Agent with SMC
Built with love by Moon Dev 🚀

AI-powered paper trading agent using Smart Money Concepts:
- IFVG (Imbalance Fair Value Gaps)
- Breaker Blocks
- Order Blocks
- Liquidity Zones
- Market Structure

Powered by qwen3-coder:30b
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
from src.mt5.smc_indicators import SMCIndicators
from src.models.model_factory import ModelFactory


class MT5TradingAgentSMC:
    """AI-powered MT5 trading agent with Smart Money Concepts"""

    def __init__(self, paper_trading: bool = True, virtual_balance: float = 10000.0):
        """
        Initialize MT5 SMC trading agent

        Args:
            paper_trading: Use paper trading mode (default: True)
            virtual_balance: Starting balance for paper trading
        """
        cprint("\n" + "="*70, "cyan", attrs=["bold"])
        cprint("  🌙 Moon Dev's MT5 SMC Trading Agent", "cyan", attrs=["bold"])
        cprint("  Smart Money Concepts + Qwen3-Coder:30b", "cyan", attrs=["bold"])
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

        # Trading parameters (SMC-optimized)
        self.max_positions = 3
        self.risk_per_trade = 0.01  # 1% risk (more conservative with SMC)
        self.symbols = ["EURUSD", "GBPUSD", "USDJPY"]

        # SMC-specific settings
        self.min_ifvg_size = 0.0010  # Minimum IFVG size to consider (10 pips)
        self.require_structure_confluence = True  # Only trade with market structure confluence

        # State
        self.running = False
        self.trade_log = []

    def connect_mt5(self) -> bool:
        """Connect to MT5"""
        return self.mt5.connect()

    def analyze_with_smc(self, symbol: str, candles: pd.DataFrame) -> Dict:
        """
        Comprehensive SMC analysis with AI decision

        Args:
            symbol: Trading symbol
            candles: Recent candlestick data

        Returns:
            Dict with SMC analysis and AI decision
        """
        cprint(f"\n🔍 SMC Analysis for {symbol}...", "cyan")

        # Get all SMC indicators
        ifvgs = SMCIndicators.detect_ifvg(candles)
        breakers = SMCIndicators.detect_breaker_blocks(candles)
        order_blocks = SMCIndicators.detect_order_blocks(candles)
        liquidity_zones = SMCIndicators.detect_liquidity_zones(candles)
        market_structure = SMCIndicators.get_market_structure(candles)

        # Current market state
        current_price = candles.iloc[-1]['Close']
        last_candle = candles.iloc[-1]

        # Format SMC summary for AI
        smc_summary = SMCIndicators.format_smc_summary(candles)

        # Print SMC analysis
        cprint(smc_summary, "white")

        # Enhanced AI prompt with SMC context
        system_prompt = """You are a professional Smart Money Concepts (SMC) trader.

Analyze the market using SMC principles:
1. IFVG (Imbalance Fair Value Gaps) - Price inefficiencies that get filled
2. Breaker Blocks - Former support/resistance that flipped
3. Order Blocks - Institutional order areas
4. Liquidity Zones - Stop loss clusters
5. Market Structure - Trend direction (HH/HL for bullish, LH/LL for bearish)

SMC TRADING RULES:
- Only trade WITH market structure (buy in uptrend, sell in downtrend)
- Look for price to react at IFVG, Order Blocks, or Breaker Blocks
- Consider liquidity grabs before trend continuation
- Require multiple confluences for high-confidence trades

Your response MUST be in this EXACT format:

DECISION: BUY|SELL|HOLD
CONFIDENCE: 0-100
REASONING: [2-3 sentences using SMC terminology]
STOP_LOSS: [Price level or NONE]
TAKE_PROFIT: [Price level or NONE]
SMC_CONFLUENCES: [List key confluences, e.g., "Bullish IFVG + Uptrend structure"]

Only recommend BUY/SELL if:
- Confidence > 75%
- At least 2 SMC confluences present
- Trade is WITH market structure"""

        user_content = f"""Symbol: {symbol}
Current Price: {current_price:.5f}

{smc_summary}

Recent Price Action:
- Last 5 candles show {"bullish" if candles.tail(5)['Close'].iloc[-1] > candles.tail(5)['Close'].iloc[0] else "bearish"} momentum
- Current candle: Open {last_candle['Open']:.5f}, Close {last_candle['Close']:.5f}

Provide SMC-based trading decision with reasoning:"""

        cprint("\n🤔 AI analyzing with SMC context...", "yellow")
        start_time = time.time()

        response = self.model.generate_response(
            system_prompt=system_prompt,
            user_content=user_content,
            temperature=0.2,  # Lower for more analytical decisions
            max_tokens=600
        )

        elapsed = time.time() - start_time
        cprint(f"✅ Analysis complete in {elapsed:.1f}s", "green")

        # Parse AI response
        analysis = self._parse_ai_response(response.content)
        analysis['elapsed_time'] = elapsed

        # Add SMC data to analysis
        analysis['smc'] = {
            'ifvgs': len([i for i in ifvgs if not i['filled']]),
            'breakers': len(breakers),
            'order_blocks': len(order_blocks),
            'liquidity_zones': len(liquidity_zones),
            'market_structure': market_structure['structure'],
            'structure_confidence': market_structure.get('confidence', 0)
        }

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
            'smc_confluences': '',
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
                    analysis['confidence'] = int(conf.split()[0])
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

            elif line.startswith('SMC_CONFLUENCES:'):
                analysis['smc_confluences'] = line.split(':', 1)[1].strip()

        return analysis

    def execute_trade(self, symbol: str, analysis: Dict) -> bool:
        """
        Execute trade based on SMC analysis

        Args:
            symbol: Trading symbol
            analysis: AI SMC analysis result

        Returns:
            True if trade executed
        """
        decision = analysis['decision']
        confidence = analysis['confidence']

        # SMC requirements: Higher confidence threshold
        if decision == 'HOLD' or confidence < 75:
            cprint(f"⏸️  {decision} - Confidence too low ({confidence}%, need 75%)", "yellow")
            return False

        # Check SMC confluences
        if not analysis.get('smc_confluences'):
            cprint("⏸️  No SMC confluences identified", "yellow")
            return False

        # Check max positions
        positions = self.mt5.get_positions()
        if len(positions) >= self.max_positions:
            cprint(f"⏸️  Max positions reached ({self.max_positions})", "yellow")
            return False

        # Calculate position size (conservative with SMC)
        account = self.mt5.get_account_info()
        risk_amount = account['balance'] * self.risk_per_trade

        # Get current price
        prices = self.mt5.get_price(symbol)
        if not prices:
            cprint("❌ Could not get price", "red")
            return False

        bid, ask = prices
        entry_price = ask if decision == "BUY" else bid

        # Position sizing: micro lot for SMC testing
        lot_size = 0.01

        cprint(f"\n{'='*70}", "green", attrs=["bold"])
        cprint(f"🎯 SMC TRADE SIGNAL", "green", attrs=["bold"])
        cprint(f"{'='*70}", "green")
        cprint(f"  Symbol: {symbol}", "white")
        cprint(f"  Decision: {decision}", "green", attrs=["bold"])
        cprint(f"  Confidence: {confidence}%", "white")
        cprint(f"  SMC Confluences: {analysis['smc_confluences']}", "cyan")
        cprint(f"  Reasoning: {analysis['reasoning']}", "white")
        cprint(f"\n  Market Structure: {analysis['smc']['market_structure']}", "cyan")
        cprint(f"  Active IFVGs: {analysis['smc']['ifvgs']}", "cyan")
        cprint(f"  Breaker Blocks: {analysis['smc']['breakers']}", "cyan")
        cprint(f"  Order Blocks: {analysis['smc']['order_blocks']}", "cyan")
        cprint(f"\n  Entry Price: {entry_price:.5f}", "white")
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
            comment=f"SMC {confidence}%"
        )

        if result['success']:
            cprint(f"✅ SMC Trade executed! Ticket: {result['ticket']}", "green", attrs=["bold"])

            # Log trade
            self.trade_log.append({
                'timestamp': datetime.now(),
                'symbol': symbol,
                'decision': decision,
                'confidence': confidence,
                'smc_confluences': analysis['smc_confluences'],
                'entry': entry_price,
                'ticket': result['ticket']
            })

            return True
        else:
            cprint(f"❌ Trade failed: {result.get('error', 'Unknown error')}", "red")
            return False

    def manage_positions(self):
        """Check and manage open positions with SMC logic"""
        positions = self.mt5.get_positions()

        if not positions:
            return

        cprint(f"\n📊 Managing {len(positions)} position(s)...", "cyan")

        for pos in positions:
            cprint(f"\n  Position {pos['ticket']}:", "yellow")
            cprint(f"    Symbol: {pos['symbol']}", "white")
            cprint(f"    Type: {pos['type']}", "white")
            cprint(f"    Entry: {pos['entry_price']:.5f}", "white")
            cprint(f"    P/L: ${pos['profit']:,.2f}", "green" if pos['profit'] > 0 else "red")

            # SMC-based exit logic: Wider targets, respect structure
            # Take profit if hit 2R (risk-reward ratio)
            if pos['profit'] > 100:
                cprint("  ✅ Taking profit at 2R!", "green")
                self.mt5.close_position(pos['ticket'])

            # Stop loss if hit 1R
            elif pos['profit'] < -50:
                cprint("  🛑 Stop loss hit!", "red")
                self.mt5.close_position(pos['ticket'])

    def run_trading_loop(self, interval_minutes: int = 15):
        """
        Run continuous SMC trading loop

        Args:
            interval_minutes: Minutes between cycles (default: 15 for more frequent monitoring)
        """
        if not self.mt5.connect():
            cprint("❌ Could not connect to MT5", "red")
            return

        self.running = True
        cycle = 0

        cprint("\n🚀 Starting SMC trading loop...", "green", attrs=["bold"])
        cprint(f"  Interval: {interval_minutes} minutes", "white")
        cprint(f"  Symbols: {', '.join(self.symbols)}", "white")
        cprint(f"  Max Positions: {self.max_positions}", "white")
        cprint(f"  Risk per Trade: {self.risk_per_trade * 100}%", "white")
        cprint(f"  Strategy: Smart Money Concepts", "cyan", attrs=["bold"])
        cprint("\n  Press Ctrl+C to stop\n", "yellow")

        try:
            while self.running:
                cycle += 1
                cprint(f"\n{'█'*70}", "cyan")
                cprint(f"  SMC CYCLE {cycle} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "cyan", attrs=["bold"])
                cprint(f"{'█'*70}\n", "cyan")

                # Show account status
                account = self.mt5.get_account_info()
                cprint(f"💰 Account Status:", "cyan", attrs=["bold"])
                cprint(f"  Balance: ${account['balance']:,.2f}", "white")
                cprint(f"  Equity: ${account['equity']:,.2f}", "white")
                cprint(f"  P/L: ${account['profit']:,.2f}", "green" if account['profit'] >= 0 else "red")

                # Manage existing positions
                self.manage_positions()

                # SMC analysis for each symbol
                for symbol in self.symbols:
                    try:
                        # Get more candles for better SMC analysis
                        candles = self.mt5.get_candles(symbol, timeframe="M15", count=100)

                        if candles is None:
                            cprint(f"⚠️  Could not get candles for {symbol}", "yellow")
                            continue

                        # SMC analysis with AI
                        analysis = self.analyze_with_smc(symbol, candles)

                        cprint(f"\n📊 {symbol} SMC Decision:", "cyan")
                        cprint(f"  Decision: {analysis['decision']}", "white")
                        cprint(f"  Confidence: {analysis['confidence']}%", "white")
                        cprint(f"  SMC Confluences: {analysis.get('smc_confluences', 'None')}", "cyan")

                        # Execute if SMC conditions met
                        if analysis['decision'] in ['BUY', 'SELL'] and analysis['confidence'] >= 75:
                            self.execute_trade(symbol, analysis)

                    except Exception as e:
                        cprint(f"❌ Error analyzing {symbol}: {e}", "red")
                        import traceback
                        traceback.print_exc()
                        continue

                # Wait for next cycle
                cprint(f"\n😴 Sleeping for {interval_minutes} minutes...", "yellow")
                time.sleep(interval_minutes * 60)

        except KeyboardInterrupt:
            cprint("\n\n⏸️  SMC trading loop stopped by user", "yellow")

        finally:
            self.running = False
            self.mt5.disconnect()

            # Show final stats
            account = self.mt5.get_account_info()
            cprint(f"\n{'='*70}", "cyan")
            cprint(f"📊 FINAL SMC STATISTICS", "cyan", attrs=["bold"])
            cprint(f"{'='*70}", "cyan")
            cprint(f"  Cycles Completed: {cycle}", "white")
            cprint(f"  Trades Executed: {len(self.trade_log)}", "white")
            cprint(f"  Final Balance: ${account['balance']:,.2f}", "white")
            cprint(f"  Final Equity: ${account['equity']:,.2f}", "white")
            cprint(f"  Total P/L: ${account['profit']:,.2f}", "green" if account['profit'] >= 0 else "red")

            if self.mt5.paper_trading:
                initial = self.mt5.initial_balance
                final = account['balance']
                pct_change = ((final - initial) / initial) * 100
                cprint(f"  Return: {pct_change:+.2f}%", "green" if pct_change >= 0 else "red")

            cprint(f"\n🌙 Thanks for using Moon Dev's SMC Agent! 🚀\n", "cyan")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Moon Dev MT5 SMC Trading Agent')
    parser.add_argument('--live', action='store_true', help='Use live trading (default: paper)')
    parser.add_argument('--balance', type=float, default=10000, help='Starting balance for paper trading')
    parser.add_argument('--interval', type=int, default=15, help='Minutes between cycles (default: 15)')

    args = parser.parse_args()

    paper_trading = not args.live

    if not paper_trading:
        cprint("\n⚠️  WARNING: LIVE TRADING MODE!", "red", attrs=["bold"])
        cprint("This will execute REAL trades with REAL money!", "red")
        confirm = input("Type 'YES' to confirm: ")
        if confirm != 'YES':
            cprint("Cancelled.", "yellow")
            return

    # Initialize and run SMC agent
    agent = MT5TradingAgentSMC(
        paper_trading=paper_trading,
        virtual_balance=args.balance
    )

    agent.run_trading_loop(interval_minutes=args.interval)


if __name__ == "__main__":
    main()

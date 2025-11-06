"""
🌙 Moon Dev's MT5 AI Trading Agent
AI-powered trading agent for MetaTrader 5
Windows-only (requires MT5)
"""

import os
import sys
from datetime import datetime
from termcolor import cprint
import pandas as pd
import pandas_ta as ta
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

# Import MT5 utils
from src.agents.mt5_utils import get_mt5_connection, MT5_AVAILABLE
from src.models.model_factory import ModelFactory
from src.models.fallback_model import create_openrouter_ollama_fallback

# Import config
from src.config import (
    MT5_ENABLED, MT5_SYMBOLS, MT5_TIMEFRAME, MT5_LOT_SIZE,
    MT5_MAX_POSITIONS, MT5_RISK_PERCENT,
    MT5_USE_STOP_LOSS, MT5_STOP_LOSS_POINTS,
    MT5_USE_TAKE_PROFIT, MT5_TAKE_PROFIT_POINTS,
    AI_MODEL, AI_MAX_TOKENS, AI_TEMPERATURE,
    AI_USE_FALLBACK, AI_PRIMARY_TYPE, AI_PRIMARY_MODEL,
    AI_FALLBACK_TYPE, AI_FALLBACK_MODEL,
)

# Trading prompt for AI
MT5_TRADING_PROMPT = """
You are Moon Dev's MT5 AI Trading Assistant 🌙

Analyze the provided market data and technical indicators to make a trading decision.

Market Data Analysis:
1. Price action relative to moving averages (MA20, MA50)
2. RSI levels (overbought >70, oversold <30)
3. MACD trend and momentum
4. Recent price movements and volatility
5. Support/resistance levels

Trading Rules:
- BUY signals: Bullish momentum, price above MAs, RSI recovering from oversold
- SELL signals: Bearish momentum, price below MAs, RSI declining from overbought
- NOTHING: Unclear signals, ranging market, conflicting indicators

Respond in this exact format:
Line 1: BUY, SELL, or NOTHING (in caps)
Line 2+: Explain your reasoning with technical analysis

Example:
BUY
Price broke above MA20 with strong volume. RSI at 45 showing bullish divergence. MACD histogram turning positive. Entry signal confirmed.
"""


class MT5TradingAgent:
    """AI-powered trading agent for MT5"""

    def __init__(self):
        """Initialize the MT5 trading agent"""
        self.mt5 = get_mt5_connection()
        self.model = None
        self.running = False

        # Statistics
        self.trades_today = 0
        self.wins = 0
        self.losses = 0

        cprint("\n🌙 Moon Dev's MT5 AI Trading Agent Initialized", "cyan")

    def connect(self) -> bool:
        """Connect to MT5"""
        if not MT5_AVAILABLE:
            cprint("❌ MT5 library not available (Windows only)", "red")
            cprint("Install with: pip install MetaTrader5", "yellow")
            return False

        if not MT5_ENABLED:
            cprint("❌ MT5 is disabled in config.py", "red")
            return False

        return self.mt5.connect()

    def initialize_model(self):
        """Initialize AI model with fallback support"""
        try:
            if AI_USE_FALLBACK and AI_PRIMARY_TYPE == 'openrouter':
                # Use OpenRouter → Ollama fallback
                cprint("\n🔄 Initializing OpenRouter with Ollama fallback...", "cyan")

                openrouter_key = os.getenv('OPENROUTER_API_KEY')
                if not openrouter_key:
                    cprint("⚠️ OPENROUTER_API_KEY not found, trying direct model init", "yellow")
                    raise ValueError("Missing OPENROUTER_API_KEY")

                self.model = create_openrouter_ollama_fallback(
                    openrouter_api_key=openrouter_key,
                    openrouter_model=AI_PRIMARY_MODEL,
                    ollama_model=AI_FALLBACK_MODEL
                )
                cprint(f"✅ Fallback Model initialized: {AI_PRIMARY_TYPE} → {AI_FALLBACK_TYPE}", "green")

            else:
                # Use single model (backwards compatible)
                self.model = ModelFactory.create_model(
                    model_type=AI_PRIMARY_TYPE,
                    model_name=AI_PRIMARY_MODEL
                )
                cprint(f"✅ AI Model initialized: {AI_PRIMARY_TYPE}", "green")

        except Exception as e:
            cprint(f"⚠️ Fallback initialization failed: {str(e)}", "yellow")
            cprint("🔄 Trying fallback model directly...", "cyan")

            try:
                # Last resort: try Ollama directly
                self.model = ModelFactory.create_model(
                    model_type=AI_FALLBACK_TYPE,
                    model_name=AI_FALLBACK_MODEL
                )
                cprint(f"✅ Fallback model initialized: {AI_FALLBACK_TYPE}", "green")
            except Exception as fallback_error:
                cprint(f"❌ Failed to initialize any AI model: {str(fallback_error)}", "red")
                raise

    def get_technical_indicators(self, df: pd.DataFrame) -> Dict:
        """Calculate technical indicators"""
        if df is None or len(df) < 50:
            return None

        # Calculate indicators
        df.ta.sma(length=20, append=True)
        df.ta.sma(length=50, append=True)
        df.ta.rsi(length=14, append=True)
        df.ta.macd(append=True)
        df.ta.bbands(append=True)

        # Get latest values
        latest = df.iloc[-1]
        prev = df.iloc[-2]

        indicators = {
            'price': latest['close'],
            'ma20': latest['SMA_20'],
            'ma50': latest['SMA_50'],
            'rsi': latest['RSI_14'],
            'macd': latest['MACD_12_26_9'],
            'macd_signal': latest['MACDs_12_26_9'],
            'macd_histogram': latest['MACDh_12_26_9'],
            'bb_upper': latest['BBU_5_2.0'],
            'bb_middle': latest['BBM_5_2.0'],
            'bb_lower': latest['BBL_5_2.0'],
            'volume': latest['tick_volume'],
            'high': latest['high'],
            'low': latest['low'],
            'prev_close': prev['close'],
            'price_change': ((latest['close'] - prev['close']) / prev['close']) * 100,
        }

        return indicators

    def format_market_data(self, symbol: str, indicators: Dict) -> str:
        """Format market data for AI analysis"""
        price = indicators['price']
        ma20 = indicators['ma20']
        ma50 = indicators['ma50']
        rsi = indicators['rsi']
        macd_hist = indicators['macd_histogram']
        price_change = indicators['price_change']

        # Price position
        price_vs_ma20 = ((price - ma20) / ma20) * 100
        price_vs_ma50 = ((price - ma50) / ma50) * 100

        # Trend analysis
        trend = "BULLISH" if price > ma20 > ma50 else "BEARISH" if price < ma20 < ma50 else "NEUTRAL"

        market_data = f"""
Symbol: {symbol}
Current Price: {price:.5f}
Price Change: {price_change:+.2f}%

Moving Averages:
- MA20: {ma20:.5f} (Price is {price_vs_ma20:+.2f}% vs MA20)
- MA50: {ma50:.5f} (Price is {price_vs_ma50:+.2f}% vs MA50)
- Trend: {trend}

Momentum Indicators:
- RSI(14): {rsi:.2f} {'(Overbought)' if rsi > 70 else '(Oversold)' if rsi < 30 else '(Neutral)'}
- MACD Histogram: {macd_hist:.5f} {'(Bullish)' if macd_hist > 0 else '(Bearish)'}

Volatility:
- Bollinger Upper: {indicators['bb_upper']:.5f}
- Bollinger Middle: {indicators['bb_middle']:.5f}
- Bollinger Lower: {indicators['bb_lower']:.5f}

Price Range:
- High: {indicators['high']:.5f}
- Low: {indicators['low']:.5f}
- Current: {price:.5f}
"""

        return market_data

    def get_ai_decision(self, symbol: str, market_data: str) -> tuple:
        """Get trading decision from AI"""
        try:
            response = self.model.generate_response(
                system_prompt=MT5_TRADING_PROMPT,
                user_content=market_data,
                temperature=AI_TEMPERATURE,
                max_tokens=AI_MAX_TOKENS
            )

            # Parse response
            lines = response.strip().split('\n')
            decision = lines[0].strip().upper()
            reasoning = '\n'.join(lines[1:]).strip()

            if decision not in ['BUY', 'SELL', 'NOTHING']:
                cprint(f"⚠️ Invalid AI decision: {decision}, defaulting to NOTHING", "yellow")
                decision = 'NOTHING'
                reasoning = "Invalid AI response format"

            return decision, reasoning

        except Exception as e:
            cprint(f"❌ Error getting AI decision: {str(e)}", "red")
            return 'NOTHING', f"Error: {str(e)}"

    def check_position_limits(self) -> bool:
        """Check if we can open new positions"""
        positions = self.mt5.get_positions()
        if len(positions) >= MT5_MAX_POSITIONS:
            cprint(f"⚠️ Maximum positions reached ({MT5_MAX_POSITIONS})", "yellow")
            return False
        return True

    def has_position(self, symbol: str) -> bool:
        """Check if we already have a position for this symbol"""
        positions = self.mt5.get_positions(symbol=symbol)
        return len(positions) > 0

    def calculate_sl_tp(self, symbol: str, is_buy: bool, entry_price: float) -> tuple:
        """Calculate stop loss and take profit prices"""
        symbol_info = self.mt5.get_symbol_info(symbol)
        if not symbol_info:
            return None, None

        point = symbol_info['point']

        sl = None
        tp = None

        if MT5_USE_STOP_LOSS:
            if is_buy:
                sl = entry_price - (MT5_STOP_LOSS_POINTS * point)
            else:
                sl = entry_price + (MT5_STOP_LOSS_POINTS * point)

        if MT5_USE_TAKE_PROFIT:
            if is_buy:
                tp = entry_price + (MT5_TAKE_PROFIT_POINTS * point)
            else:
                tp = entry_price - (MT5_TAKE_PROFIT_POINTS * point)

        return sl, tp

    def execute_trade(self, symbol: str, decision: str, reasoning: str):
        """Execute trade based on AI decision"""
        if decision == 'NOTHING':
            cprint(f"⏸️ {symbol}: No trade signal", "yellow")
            cprint(f"   Reasoning: {reasoning[:100]}...", "cyan")
            return

        # Check limits
        if not self.check_position_limits():
            return

        # Check existing position
        if self.has_position(symbol):
            cprint(f"⚠️ {symbol}: Already have a position", "yellow")
            return

        # Calculate lot size
        lot_size = self.mt5.calculate_lot_size(symbol, MT5_RISK_PERCENT, MT5_STOP_LOSS_POINTS)

        # Get current price
        symbol_info = self.mt5.get_symbol_info(symbol)
        if not symbol_info:
            return

        entry_price = symbol_info['ask'] if decision == 'BUY' else symbol_info['bid']

        # Calculate SL/TP
        sl, tp = self.calculate_sl_tp(symbol, decision == 'BUY', entry_price)

        # Display trade info
        cprint(f"\n{'🟢 BUY' if decision == 'BUY' else '🔴 SELL'} SIGNAL: {symbol}", "green" if decision == 'BUY' else "red")
        cprint(f"   Price: {entry_price:.5f}", "cyan")
        cprint(f"   Lot Size: {lot_size}", "cyan")
        cprint(f"   Stop Loss: {sl:.5f}" if sl else "   Stop Loss: None", "cyan")
        cprint(f"   Take Profit: {tp:.5f}" if tp else "   Take Profit: None", "cyan")
        cprint(f"   AI Reasoning: {reasoning[:150]}...", "yellow")

        # Execute order
        if decision == 'BUY':
            ticket = self.mt5.market_buy(symbol, lot_size, sl, tp, comment="Moon Dev AI Bot")
        else:
            ticket = self.mt5.market_sell(symbol, lot_size, sl, tp, comment="Moon Dev AI Bot")

        if ticket:
            self.trades_today += 1
            self.save_trade_log(symbol, decision, entry_price, lot_size, sl, tp, reasoning)

    def save_trade_log(self, symbol: str, decision: str, price: float,
                       lot_size: float, sl: float, tp: float, reasoning: str):
        """Save trade to log file"""
        log_dir = os.path.join(project_root, 'src', 'data', 'mt5_trading_agent')
        os.makedirs(log_dir, exist_ok=True)

        log_file = os.path.join(log_dir, f'trades_{datetime.now().strftime("%Y%m%d")}.csv')

        # Check if file exists
        file_exists = os.path.exists(log_file)

        with open(log_file, 'a') as f:
            if not file_exists:
                f.write('timestamp,symbol,action,price,lot_size,sl,tp,reasoning\n')

            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            reasoning_clean = reasoning.replace('\n', ' ').replace(',', ';')[:200]

            f.write(f'{timestamp},{symbol},{decision},{price:.5f},{lot_size},{sl or 0:.5f},{tp or 0:.5f},"{reasoning_clean}"\n')

    def analyze_symbol(self, symbol: str):
        """Analyze a symbol and make trading decision"""
        cprint(f"\n📊 Analyzing {symbol}...", "cyan")

        # Get OHLCV data
        df = self.mt5.get_ohlcv(symbol, MT5_TIMEFRAME, bars=100)
        if df is None:
            cprint(f"❌ Failed to get data for {symbol}", "red")
            return

        # Calculate indicators
        indicators = self.get_technical_indicators(df)
        if indicators is None:
            cprint(f"❌ Failed to calculate indicators for {symbol}", "red")
            return

        # Format market data
        market_data = self.format_market_data(symbol, indicators)

        # Get AI decision
        decision, reasoning = self.get_ai_decision(symbol, market_data)

        # Execute trade
        self.execute_trade(symbol, decision, reasoning)

    def manage_positions(self):
        """Monitor and manage open positions"""
        positions = self.mt5.get_positions()

        if len(positions) == 0:
            return

        cprint(f"\n📊 Managing {len(positions)} open positions...", "cyan")

        for pos in positions:
            symbol = pos['symbol']
            ticket = pos['ticket']
            profit = pos['profit']
            pos_type = pos['type']

            cprint(f"   Position #{ticket}: {pos_type} {symbol} | P&L: ${profit:.2f}", "yellow")

            # Check for manual close conditions (optional)
            # You can add custom exit logic here

    def show_statistics(self):
        """Show trading statistics"""
        account_info = self.mt5.get_account_info()
        if not account_info:
            return

        positions = self.mt5.get_positions()

        cprint("\n" + "="*60, "cyan")
        cprint("📊 TRADING STATISTICS", "cyan")
        cprint("="*60, "cyan")
        cprint(f"💰 Balance: ${account_info['balance']:.2f}", "green")
        cprint(f"💵 Equity: ${account_info['equity']:.2f}", "green")
        cprint(f"📈 Profit: ${account_info['profit']:.2f}", "green" if account_info['profit'] >= 0 else "red")
        cprint(f"📊 Margin Level: {account_info['margin_level']:.2f}%", "cyan")
        cprint(f"🎯 Open Positions: {len(positions)}", "cyan")
        cprint(f"📝 Trades Today: {self.trades_today}", "cyan")
        cprint("="*60, "cyan")

    def run_cycle(self):
        """Run one trading cycle"""
        cprint("\n" + "="*60, "cyan")
        cprint(f"🌙 Moon Dev MT5 Trading Cycle - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "cyan")
        cprint("="*60, "cyan")

        # Show account info
        self.show_statistics()

        # Manage existing positions
        self.manage_positions()

        # Analyze symbols
        for symbol in MT5_SYMBOLS:
            try:
                self.analyze_symbol(symbol)
            except Exception as e:
                cprint(f"❌ Error analyzing {symbol}: {str(e)}", "red")
                continue

        cprint(f"\n✅ Trading cycle completed", "green")

    def run(self):
        """Main run loop"""
        if not self.connect():
            return

        try:
            self.initialize_model()
        except Exception as e:
            cprint(f"❌ Failed to initialize AI model: {str(e)}", "red")
            self.mt5.disconnect()
            return

        self.running = True

        try:
            while self.running:
                self.run_cycle()

                # Sleep between cycles (configurable in config.py)
                from src.config import SLEEP_BETWEEN_RUNS_MINUTES
                import time

                cprint(f"\n😴 Sleeping for {SLEEP_BETWEEN_RUNS_MINUTES} minutes...", "yellow")
                time.sleep(SLEEP_BETWEEN_RUNS_MINUTES * 60)

        except KeyboardInterrupt:
            cprint("\n👋 Shutting down gracefully...", "yellow")
        except Exception as e:
            cprint(f"\n❌ Fatal error: {str(e)}", "red")
            raise
        finally:
            self.mt5.disconnect()


if __name__ == "__main__":
    """Run MT5 Trading Agent standalone"""
    agent = MT5TradingAgent()
    agent.run()

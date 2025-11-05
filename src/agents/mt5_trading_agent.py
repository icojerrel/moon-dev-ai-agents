"""
🌙 Moon Dev's MetaTrader 5 Trading Agent
Built with love by Moon Dev 🚀

This agent integrates with MetaTrader 5 for forex and CFD trading using AI analysis.
Follows the same pattern as other trading agents for consistency.
"""

import os
import sys
from datetime import datetime, timedelta
from termcolor import cprint
import pandas as pd
from typing import Dict, List, Optional

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from src.models.model_factory import model_factory
from src.nice_funcs_mt5 import (
    get_account_info,
    get_symbol_info,
    get_ohlcv_data,
    get_positions,
    market_buy,
    market_sell,
    close_position,
    close_all_positions,
    add_technical_indicators,
    ensure_connection
)
from src.config import (
    AI_MODEL,
    AI_MAX_TOKENS,
    AI_TEMPERATURE,
    MT5_SYMBOLS,
    MT5_MODEL_TYPE,
    MT5_MODEL_NAME,
    MT5_MIN_CONFIDENCE,
)
from src.utils.mt5_helpers import (
    detect_asset_class,
    get_asset_params,
    format_asset_name,
    get_market_context,
    calculate_position_size
)
from src.utils.trading_hours import (
    is_optimal_trading_time,
    get_current_session,
    get_session_info
)
import src.config as config


class MT5TradingAgent:
    """
    MetaTrader 5 Trading Agent

    Features:
    - AI-powered market analysis for forex/CFD pairs
    - Multi-symbol monitoring
    - Risk management integration
    - Position management
    - Technical indicator analysis
    """

    def __init__(
        self,
        symbols: List[str] = None,
        model_type: str = 'anthropic',
        model_name: str = None,
        max_position_size: float = 0.1,  # Max lots per position
        max_positions: int = 3,  # Max concurrent positions
    ):
        """
        Initialize MT5 Trading Agent

        Args:
            symbols: List of symbols to trade (e.g., ['EURUSD', 'GBPUSD'])
            model_type: AI model provider ('anthropic', 'openai', 'deepseek', 'groq', etc.)
            model_name: Specific model name (None = use default for provider)
            max_position_size: Maximum position size in lots
            max_positions: Maximum number of concurrent positions
        """
        self.symbols = symbols or ['EURUSD', 'GBPUSD', 'USDJPY']
        self.model_type = model_type
        self.model_name = model_name or MT5_MODEL_NAME  # Use MT5-specific model name from config
        self.max_position_size = max_position_size
        self.max_positions = max_positions

        # Initialize AI model with specific model name
        try:
            self.model = model_factory.get_model(model_type, model_name=self.model_name)
            if self.model:
                cprint(f"✅ Initialized MT5 agent with {model_type} ({self.model_name})", "green")
            else:
                raise Exception(f"Failed to get model {model_type}")
        except Exception as e:
            cprint(f"❌ Failed to initialize AI model: {str(e)}", "red")
            raise

        # Ensure MT5 connection
        if not ensure_connection():
            raise Exception("Failed to connect to MT5")

    def get_market_analysis(self, symbol: str, df: pd.DataFrame) -> Dict:
        """
        Get AI analysis for a symbol with asset class awareness

        Args:
            symbol: Trading symbol
            df: DataFrame with OHLCV and indicators

        Returns:
            Dict with analysis results
        """
        try:
            # Detect asset class and get parameters
            asset_class = detect_asset_class(symbol)
            asset_params = get_asset_params(symbol, config)
            market_context = get_market_context(symbol, asset_class)
            formatted_name, emoji = format_asset_name(symbol)

            # Prepare market data summary
            latest = df.iloc[-1]
            prev = df.iloc[-2]

            # Calculate key metrics
            price_change = ((latest['Close'] - prev['Close']) / prev['Close']) * 100

            # Build asset-specific analysis prompt
            system_prompt = f"""You are an expert multi-asset trading analyst specializing in {asset_class}.
Analyze the provided market data and technical indicators to make a trading decision.

{market_context}

Provide your analysis in the following JSON format:
{{
    "action": "BUY" | "SELL" | "HOLD",
    "confidence": 0-100,
    "reasoning": "Brief explanation of your decision (50-100 words)",
    "stop_loss_pips": number (suggested SL in pips from entry, {asset_params['min_stop_loss_pips']}-{asset_params['max_stop_loss_pips']}),
    "take_profit_pips": number (suggested TP in pips from entry, aim for {asset_params['default_tp_ratio']}:1 RR),
    "position_size": {asset_params['position_size']} (recommended for this asset class)
}}

Asset Class Specific Guidelines:
- This is a {asset_class} instrument
- Recommended position size: {asset_params['position_size']} lots
- Maximum spread: {asset_params['max_spread_pips']} pips
- Risk/Reward target: {asset_params['default_tp_ratio']}:1

Technical Analysis:
- Trend direction (SMAs 20/50/200)
- Momentum (RSI, MACD)
- Volatility (Bollinger Bands)
- Support/Resistance levels
- Volume confirmation

Be conservative. Only suggest trades with:
- Clear trend/momentum alignment
- Confidence > 75%
- Risk/Reward > 1.5:1
- Favorable technical setup"""

            user_content = f"""Symbol: {formatted_name} ({symbol}) {emoji}
Asset Class: {asset_class.upper()}

Current Market Data:
- Price: {latest['Close']:.5f}
- Price Change (1 bar): {price_change:.2f}%
- Volume: {latest['Volume']}
- Spread: {latest.get('Spread', 'N/A')}

Technical Indicators:
- SMA 20: {latest.get('SMA_20', 'N/A'):.5f}
- SMA 50: {latest.get('SMA_50', 'N/A'):.5f}
- SMA 200: {latest.get('SMA_200', 'N/A'):.5f}
- RSI: {latest.get('RSI', 'N/A'):.2f}
- MACD: {latest.get('MACD', 'N/A'):.5f}
- MACD Signal: {latest.get('MACD_Signal', 'N/A'):.5f}
- BB Upper: {latest.get('BB_Upper', 'N/A'):.5f}
- BB Middle: {latest.get('BB_Middle', 'N/A'):.5f}
- BB Lower: {latest.get('BB_Lower', 'N/A'):.5f}

Recent Price Action (last 5 bars):
{df[['Close', 'High', 'Low']].tail(5).to_string()}

Provide your trading recommendation."""

            # Get AI analysis
            response = self.model.generate_response(
                system_prompt=system_prompt,
                user_content=user_content,
                temperature=AI_TEMPERATURE,
                max_tokens=AI_MAX_TOKENS
            )

            # Parse response (assuming JSON format)
            import json

            # Try to extract JSON from response
            try:
                # Find JSON in response
                start = response.find('{')
                end = response.rfind('}') + 1
                if start != -1 and end > start:
                    json_str = response[start:end]
                    analysis = json.loads(json_str)
                else:
                    # Fallback if no JSON found
                    analysis = {
                        'action': 'HOLD',
                        'confidence': 0,
                        'reasoning': 'Failed to parse AI response',
                        'stop_loss_pips': 0,
                        'take_profit_pips': 0,
                        'position_size': 0
                    }
            except json.JSONDecodeError:
                cprint(f"⚠️  Failed to parse JSON from AI response", "yellow")
                analysis = {
                    'action': 'HOLD',
                    'confidence': 0,
                    'reasoning': response[:200],  # First 200 chars
                    'stop_loss_pips': 0,
                    'take_profit_pips': 0,
                    'position_size': 0
                }

            return analysis

        except Exception as e:
            cprint(f"❌ Error in market analysis: {str(e)}", "red")
            return {
                'action': 'HOLD',
                'confidence': 0,
                'reasoning': f'Error: {str(e)}',
                'stop_loss_pips': 0,
                'take_profit_pips': 0,
                'position_size': 0
            }

    def execute_trade(self, symbol: str, analysis: Dict) -> bool:
        """
        Execute trade based on analysis

        Args:
            symbol: Trading symbol
            analysis: Analysis dict from get_market_analysis

        Returns:
            True if trade executed, False otherwise
        """
        try:
            action = analysis.get('action', 'HOLD')
            confidence = analysis.get('confidence', 0)
            position_size = min(
                analysis.get('position_size', 0.01),
                self.max_position_size
            )

            if action == 'HOLD' or confidence < 70:
                cprint(f"⏸️  {symbol}: {action} (confidence: {confidence}%)", "yellow")
                return False

            # Check if we can open more positions
            positions = get_positions()
            if positions is not None and len(positions) >= self.max_positions:
                cprint(f"⚠️  Max positions ({self.max_positions}) reached, skipping trade", "yellow")
                return False

            # Get symbol info for SL/TP calculation
            symbol_info = get_symbol_info(symbol)
            if symbol_info is None:
                return False

            point = symbol_info['point']
            digits = symbol_info['digits']

            # Calculate SL/TP prices
            sl_pips = analysis.get('stop_loss_pips', 20)
            tp_pips = analysis.get('take_profit_pips', 40)

            if action == 'BUY':
                price = symbol_info['ask']
                sl = round(price - (sl_pips * point * 10), digits) if sl_pips > 0 else 0
                tp = round(price + (tp_pips * point * 10), digits) if tp_pips > 0 else 0

                cprint(f"\n🟢 BUYING {symbol}:", "green")
                cprint(f"  Size: {position_size} lots", "cyan")
                cprint(f"  Entry: {price:.5f}", "cyan")
                cprint(f"  SL: {sl:.5f} ({sl_pips} pips)", "cyan")
                cprint(f"  TP: {tp:.5f} ({tp_pips} pips)", "cyan")
                cprint(f"  Confidence: {confidence}%", "cyan")
                cprint(f"  Reason: {analysis.get('reasoning', '')}", "white")

                ticket = market_buy(
                    symbol=symbol,
                    volume=position_size,
                    sl=sl,
                    tp=tp,
                    comment=f"AI Buy {confidence}%"
                )

                return ticket is not None

            elif action == 'SELL':
                price = symbol_info['bid']
                sl = round(price + (sl_pips * point * 10), digits) if sl_pips > 0 else 0
                tp = round(price - (tp_pips * point * 10), digits) if tp_pips > 0 else 0

                cprint(f"\n🔴 SELLING {symbol}:", "red")
                cprint(f"  Size: {position_size} lots", "cyan")
                cprint(f"  Entry: {price:.5f}", "cyan")
                cprint(f"  SL: {sl:.5f} ({sl_pips} pips)", "cyan")
                cprint(f"  TP: {tp:.5f} ({tp_pips} pips)", "cyan")
                cprint(f"  Confidence: {confidence}%", "cyan")
                cprint(f"  Reason: {analysis.get('reasoning', '')}", "white")

                ticket = market_sell(
                    symbol=symbol,
                    volume=position_size,
                    sl=sl,
                    tp=tp,
                    comment=f"AI Sell {confidence}%"
                )

                return ticket is not None

            return False

        except Exception as e:
            cprint(f"❌ Error executing trade: {str(e)}", "red")
            return False

    def run_analysis_cycle(self):
        """Run one complete analysis cycle for all symbols"""
        try:
            cprint("\n" + "="*60, "cyan")
            cprint("🌙 MT5 Trading Agent - Analysis Cycle", "cyan")
            cprint("="*60 + "\n", "cyan")

            # Display current market session info
            if config.MT5_USE_TRADING_HOURS_FILTER:
                session_info = get_session_info()
                current_session = get_current_session()

                cprint(f"🕐 Market Session: {current_session.value}", "yellow")
                cprint(f"⏰ Time (UTC): {session_info['current_time_utc']}", "yellow")
                cprint(f"🇳🇱 Time (NL):  {session_info['current_time_nl']}", "yellow")
                cprint(f"📅 Day: {session_info['weekday']}", "yellow")

                if session_info['is_weekend']:
                    cprint("⚠️  Weekend - Markets closed or low liquidity", "red")
                    cprint("Skipping analysis cycle\n", "red")
                    return

                cprint("")  # Empty line

            # Check account
            account = get_account_info()
            if account is None:
                cprint("❌ Failed to get account info", "red")
                return

            cprint(f"💰 Account Balance: {account['balance']:.2f} {account['currency']}", "green")
            cprint(f"💵 Equity: {account['equity']:.2f} {account['currency']}", "green")
            cprint(f"📊 Margin Level: {account.get('margin_level', 0):.2f}%", "green")
            cprint(f"💸 Profit: {account['profit']:.2f} {account['currency']}\n", "green")

            # Check positions
            positions = get_positions()
            if positions is not None and len(positions) > 0:
                cprint(f"📈 Open Positions: {len(positions)}", "yellow")
                for _, pos in positions.iterrows():
                    cprint(f"  {pos['type']} {pos['symbol']} | "
                          f"Vol: {pos['volume']} | "
                          f"P/L: {pos['profit']:.2f}", "yellow")
                print()

            # Analyze each symbol
            for symbol in self.symbols:
                try:
                    cprint(f"\n🔍 Analyzing {symbol}...", "cyan")

                    # Check if optimal trading time for this asset class
                    if config.MT5_USE_TRADING_HOURS_FILTER:
                        asset_class = detect_asset_class(symbol)
                        is_optimal, reason = is_optimal_trading_time(
                            asset_class,
                            strict=config.MT5_STRICT_HOURS
                        )

                        if not is_optimal:
                            formatted_name, emoji = format_asset_name(symbol)
                            cprint(f"⏸️  {emoji} {formatted_name} ({asset_class}): {reason}", "yellow")
                            continue

                        # Show optimal status
                        formatted_name, emoji = format_asset_name(symbol)
                        cprint(f"✅ {emoji} {formatted_name} ({asset_class}): {reason}", "green")

                    # Get OHLCV data
                    df = get_ohlcv_data(symbol, timeframe='1H', bars=200)
                    if df is None:
                        cprint(f"⚠️  Failed to get data for {symbol}", "yellow")
                        continue

                    # Add indicators
                    df = add_technical_indicators(df)

                    # Get AI analysis
                    analysis = self.get_market_analysis(symbol, df)

                    # Execute trade if recommended
                    self.execute_trade(symbol, analysis)

                except Exception as e:
                    cprint(f"❌ Error analyzing {symbol}: {str(e)}", "red")
                    continue

            cprint("\n" + "="*60, "cyan")
            cprint("✅ Analysis cycle complete", "green")
            cprint("="*60 + "\n", "cyan")

        except Exception as e:
            cprint(f"❌ Error in analysis cycle: {str(e)}", "red")

    def run(self):
        """Run the agent continuously"""
        try:
            while True:
                self.run_analysis_cycle()

                # Sleep between cycles (15 minutes default)
                from src.config import SLEEP_BETWEEN_RUNS_MINUTES
                next_run = datetime.now() + timedelta(minutes=SLEEP_BETWEEN_RUNS_MINUTES)
                cprint(f"😴 Next run at {next_run.strftime('%H:%M:%S')}", "yellow")

                import time
                time.sleep(60 * SLEEP_BETWEEN_RUNS_MINUTES)

        except KeyboardInterrupt:
            cprint("\n👋 Shutting down MT5 agent...", "yellow")
        except Exception as e:
            cprint(f"\n❌ Fatal error: {str(e)}", "red")
            raise


if __name__ == "__main__":
    """Standalone execution"""
    cprint("\n🌙 Moon Dev MT5 Trading Agent\n", "white", "on_blue")

    # Configure symbols to trade
    SYMBOLS = [
        'EURUSD',  # Euro vs US Dollar
        'GBPUSD',  # British Pound vs US Dollar
        'USDJPY',  # US Dollar vs Japanese Yen
        # 'BTCUSD',  # Bitcoin (if available)
        # 'XAUUSD',  # Gold
    ]

    try:
        # Import config settings
        from src.config import MT5_MODEL_TYPE, MT5_MAX_POSITION_SIZE, MT5_MAX_POSITIONS

        agent = MT5TradingAgent(
            symbols=SYMBOLS,
            model_type=MT5_MODEL_TYPE,  # Uses config setting (openrouter, anthropic, etc.)
            max_position_size=MT5_MAX_POSITION_SIZE,  # From config
            max_positions=MT5_MAX_POSITIONS  # From config (currently 1)
        )

        # Run once for testing
        agent.run_analysis_cycle()

        # For continuous running, uncomment:
        # agent.run()

    except Exception as e:
        cprint(f"\n❌ Failed to start agent: {str(e)}", "red")

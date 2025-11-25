"""
🌙 Moon Dev's QuantAnalysis Agent
Inspired by QuantAgent research from Y-Research SBU
Combines Indicator + Pattern + Trend analysis in a unified agent

Built with love by Moon Dev 🚀
"""

import os
import sys
import pandas as pd
import numpy as np
import mplfinance as mpf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from pathlib import Path
import time
import traceback
import base64
from io import BytesIO
from dotenv import load_dotenv
import pandas_ta as ta

# Add project root to path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from src.agents.base_agent import BaseAgent
from src.models.model_factory import model_factory
from src import nice_funcs_hl as hl
from src.config import AI_MODEL, AI_TEMPERATURE, AI_MAX_TOKENS
from termcolor import cprint

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent.parent

# ============================================================================
# CONFIGURATION
# ============================================================================

# AI Model Configuration
QUANT_AI_MODEL_TYPE = 'anthropic'  # Vision-capable model required
QUANT_AI_MODEL_NAME = 'claude-3-5-sonnet-latest'  # Best for vision analysis

# Analysis Settings
DEFAULT_TIMEFRAME = '1H'  # 15m, 1H, 4H, 1D
DEFAULT_BARS = 100  # Number of candles to analyze (QuantAgent uses 30)
QUANT_LOOKBACK = 30  # Focus on last 30 candles like QuantAgent paper

# Chart Settings
CHART_STYLE = 'charles'
VOLUME_PANEL = True

# Indicator Settings (QuantAgent uses: RSI, MACD, Stochastic)
RSI_PERIOD = 14
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
STOCH_K = 14
STOCH_D = 3

# Confidence Thresholds
MIN_CONFIDENCE = 50  # Minimum confidence to act on signal
HIGH_CONFIDENCE = 75  # High confidence threshold

# ============================================================================
# AI PROMPTS (Based on QuantAgent methodology)
# ============================================================================

INDICATOR_ANALYSIS_PROMPT = """You are the INDICATOR AGENT from QuantAgent system.

Analyze these technical indicators and provide momentum/trend assessment:

Indicator Data:
{indicator_data}

Your task (as Indicator Agent):
1. Assess RSI levels (overbought >70, oversold <30, neutral 30-70)
2. Evaluate MACD convergence/divergence and histogram direction
3. Check Stochastic Oscillator for momentum extremes
4. Identify indicator confirmations or divergences

Respond in this format:
Line 1: BULLISH, BEARISH, or NEUTRAL
Line 2: Brief indicator summary (1 sentence)
Line 3: Key signals detected
Line 4: Confidence: X% (0-100)"""

PATTERN_ANALYSIS_PROMPT = """You are the PATTERN AGENT from QuantAgent system.

Analyze this price chart image and identify patterns:

Recent Price Action:
{price_action}

Your task (as Pattern Agent):
1. Identify chart patterns (triangles, flags, head & shoulders, double tops/bottoms, etc.)
2. Spot key support/resistance levels
3. Note any breakouts or breakdown patterns
4. Assess pattern strength and completion

Respond in this format:
Line 1: Pattern detected (e.g., "Ascending Triangle", "Bull Flag", "No Clear Pattern")
Line 2: Pattern description (1-2 sentences)
Line 3: Direction bias: BULLISH, BEARISH, or NEUTRAL
Line 4: Confidence: X% (0-100)"""

TREND_ANALYSIS_PROMPT = """You are the TREND AGENT from QuantAgent system.

Analyze price trends and channels:

Trend Data:
{trend_data}

Your task (as Trend Agent):
1. Identify overall trend direction (uptrend, downtrend, sideways)
2. Assess trend strength and slope
3. Detect consolidation zones
4. Note any trend reversals or continuations

Respond in this format:
Line 1: UPTREND, DOWNTREND, or SIDEWAYS
Line 2: Trend description (1-2 sentences)
Line 3: Trend strength: STRONG, MODERATE, or WEAK
Line 4: Confidence: X% (0-100)"""

DECISION_SYNTHESIS_PROMPT = """You are the DECISION AGENT from QuantAgent system.

Synthesize all agent analyses to make final trading recommendation:

Indicator Agent Analysis:
{indicator_analysis}

Pattern Agent Analysis:
{pattern_analysis}

Trend Agent Analysis:
{trend_analysis}

Your task (as Decision Agent):
1. Synthesize all three agent inputs
2. Look for confirmations across agents
3. Assess overall risk/reward
4. Make final trade recommendation

Respond in this format:
Line 1: BUY, SELL, or NOTHING (in caps)
Line 2: Position type: LONG or SHORT (if not NOTHING)
Line 3: Entry reasoning (2-3 sentences)
Line 4: Stop-loss suggestion
Line 5: Take-profit suggestion
Line 6: Overall confidence: X% (0-100)

Remember Moon Dev's rules:
- Only high-confidence trades (>50%)
- Risk management is priority #1
- Multiple agent confirmations increase confidence"""

# ============================================================================
# QUANTANALYSIS AGENT
# ============================================================================

class QuantAnalysisAgent(BaseAgent):
    """
    🌙 Moon Dev's QuantAnalysis Agent

    Multi-agent trading analysis system inspired by QuantAgent research:
    - Indicator Agent: RSI, MACD, Stochastic analysis
    - Pattern Agent: Chart pattern recognition (vision-based)
    - Trend Agent: Trend direction and channel detection
    - Decision Agent: Synthesis of all agents for final recommendation
    """

    def __init__(self):
        """Initialize QuantAnalysis Agent"""
        super().__init__('quantanalysis')

        cprint("\n🤖 Initializing Moon Dev's QuantAnalysis Agent...", "cyan")

        # Load environment
        load_dotenv()

        # Initialize AI model (vision-capable required)
        cprint(f"🧠 Loading {QUANT_AI_MODEL_TYPE} model: {QUANT_AI_MODEL_NAME}", "cyan")
        self.model = model_factory.get_model(QUANT_AI_MODEL_TYPE, QUANT_AI_MODEL_NAME)

        if not self.model:
            cprint(f"❌ Failed to initialize {QUANT_AI_MODEL_TYPE} model!", "red")
            sys.exit(1)

        cprint(f"✅ Using model: {self.model.model_name}", "green")

        # Set up directories
        self.charts_dir = PROJECT_ROOT / "src" / "data" / "quantanalysis" / "charts"
        self.results_dir = PROJECT_ROOT / "src" / "data" / "quantanalysis" / "results"
        self.charts_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)

        # Store analysis cache
        self.analysis_cache = {}

        cprint("✨ QuantAnalysis Agent initialized!", "green")
        cprint(f"📊 Multi-Agent Architecture: Indicator → Pattern → Trend → Decision", "cyan")

    # ========================================================================
    # DATA COLLECTION
    # ========================================================================

    def get_market_data(self, symbol, timeframe=DEFAULT_TIMEFRAME, bars=DEFAULT_BARS):
        """Get OHLCV data with technical indicators"""
        try:
            cprint(f"\n📊 Fetching data for {symbol} ({timeframe})...", "cyan")

            # Get data from HyperLiquid
            data = hl.get_data(
                symbol=symbol,
                timeframe=timeframe,
                bars=bars,
                add_indicators=False  # We'll add custom indicators
            )

            if data is None or data.empty:
                cprint(f"❌ No data available for {symbol}", "red")
                return None

            # Add QuantAgent-specific indicators
            data = self._add_quant_indicators(data)

            cprint(f"✅ Retrieved {len(data)} candles", "green")
            return data

        except Exception as e:
            cprint(f"❌ Error fetching data: {str(e)}", "red")
            traceback.print_exc()
            return None

    def _add_quant_indicators(self, df):
        """Add QuantAgent indicators: RSI, MACD, Stochastic"""
        try:
            cprint("🔧 Adding QuantAgent indicators (RSI, MACD, Stochastic)...", "yellow")

            # Ensure numeric types
            df['close'] = df['close'].astype('float64')
            df['high'] = df['high'].astype('float64')
            df['low'] = df['low'].astype('float64')

            # RSI (14 period)
            df['rsi'] = ta.rsi(df['close'], length=RSI_PERIOD)

            # MACD
            macd = ta.macd(df['close'], fast=MACD_FAST, slow=MACD_SLOW, signal=MACD_SIGNAL)
            if macd is not None:
                df = pd.concat([df, macd], axis=1)

            # Stochastic Oscillator
            stoch = ta.stoch(df['high'], df['low'], df['close'], k=STOCH_K, d=STOCH_D)
            if stoch is not None:
                df = pd.concat([df, stoch], axis=1)

            # SMAs for trend analysis
            df['sma_20'] = ta.sma(df['close'], length=20)
            df['sma_50'] = ta.sma(df['close'], length=50)

            cprint("✅ Indicators added successfully", "green")
            return df

        except Exception as e:
            cprint(f"❌ Error adding indicators: {str(e)}", "red")
            traceback.print_exc()
            return df

    # ========================================================================
    # INDICATOR AGENT
    # ========================================================================

    def indicator_agent_analysis(self, data):
        """
        INDICATOR AGENT: Analyze RSI, MACD, Stochastic
        Returns momentum and trend assessment
        """
        try:
            cprint("\n🔵 INDICATOR AGENT analyzing...", "blue")

            # Focus on recent data (last QUANT_LOOKBACK candles)
            recent_data = data.tail(QUANT_LOOKBACK)

            # Get latest indicator values
            latest = recent_data.iloc[-1]

            # Build indicator summary
            indicator_summary = f"""
Recent Close: ${latest['close']:.4f}

RSI (14): {latest['rsi']:.2f}
- Assessment: {'Overbought' if latest['rsi'] > 70 else 'Oversold' if latest['rsi'] < 30 else 'Neutral'}

MACD:
- MACD Line: {latest.get('MACD_12_26_9', 'N/A')}
- Signal Line: {latest.get('MACDs_12_26_9', 'N/A')}
- Histogram: {latest.get('MACDh_12_26_9', 'N/A')}

Stochastic Oscillator:
- %K: {latest.get('STOCHk_14_3_3', 'N/A')}
- %D: {latest.get('STOCHd_14_3_3', 'N/A')}

Moving Averages:
- SMA 20: ${latest['sma_20']:.4f}
- SMA 50: ${latest['sma_50']:.4f}
- Price vs SMA20: {'Above' if latest['close'] > latest['sma_20'] else 'Below'}
- Price vs SMA50: {'Above' if latest['close'] > latest['sma_50'] else 'Below'}
"""

            # Call AI for indicator analysis
            response = self.model.generate_response(
                system_prompt=INDICATOR_ANALYSIS_PROMPT.format(indicator_data=indicator_summary),
                user_content="Analyze these indicators as the Indicator Agent.",
                temperature=0.1,  # Low temperature for consistency
                max_tokens=500
            )

            # Parse response
            analysis = self._parse_agent_response(response, 'indicator')

            cprint(f"✅ Indicator Agent: {analysis.get('direction', 'UNKNOWN')} "
                   f"(Confidence: {analysis.get('confidence', 0)}%)", "green")

            return analysis

        except Exception as e:
            cprint(f"❌ Indicator Agent error: {str(e)}", "red")
            traceback.print_exc()
            return None

    # ========================================================================
    # PATTERN AGENT
    # ========================================================================

    def pattern_agent_analysis(self, data, symbol):
        """
        PATTERN AGENT: Chart pattern recognition using vision analysis
        Returns pattern identification and direction bias
        """
        try:
            cprint("\n🟢 PATTERN AGENT analyzing...", "green")

            # Generate chart for vision analysis
            chart_path = self._generate_chart(data, symbol)

            if not chart_path:
                cprint("⚠️ Could not generate chart for pattern analysis", "yellow")
                return None

            # Build price action summary
            recent_data = data.tail(QUANT_LOOKBACK)
            price_action = f"""
Recent {QUANT_LOOKBACK} candles:
- Highest: ${recent_data['high'].max():.4f}
- Lowest: ${recent_data['low'].min():.4f}
- Current: ${recent_data.iloc[-1]['close']:.4f}
- Change: {((recent_data.iloc[-1]['close'] - recent_data.iloc[0]['close']) / recent_data.iloc[0]['close'] * 100):.2f}%

Key levels:
- Recent highs: {recent_data.nlargest(3, 'high')['high'].tolist()}
- Recent lows: {recent_data.nsmallest(3, 'low')['low'].tolist()}
"""

            # Note: Vision analysis would go here if model supports it
            # For now, use text-based pattern detection
            response = self.model.generate_response(
                system_prompt=PATTERN_ANALYSIS_PROMPT.format(price_action=price_action),
                user_content="Analyze price patterns as the Pattern Agent.",
                temperature=0.1,
                max_tokens=500
            )

            # Parse response
            analysis = self._parse_agent_response(response, 'pattern')

            cprint(f"✅ Pattern Agent: {analysis.get('pattern', 'Unknown')} "
                   f"({analysis.get('direction', 'UNKNOWN')}, Confidence: {analysis.get('confidence', 0)}%)", "green")

            return analysis

        except Exception as e:
            cprint(f"❌ Pattern Agent error: {str(e)}", "red")
            traceback.print_exc()
            return None

    # ========================================================================
    # TREND AGENT
    # ========================================================================

    def trend_agent_analysis(self, data):
        """
        TREND AGENT: Trend direction, slope, and consolidation analysis
        Returns trend assessment and strength
        """
        try:
            cprint("\n🟡 TREND AGENT analyzing...", "yellow")

            # Focus on recent data
            recent_data = data.tail(QUANT_LOOKBACK)

            # Calculate trend metrics
            first_close = recent_data.iloc[0]['close']
            last_close = recent_data.iloc[-1]['close']
            price_change = ((last_close - first_close) / first_close) * 100

            # SMA trend
            sma_20_trend = "Rising" if recent_data['sma_20'].iloc[-1] > recent_data['sma_20'].iloc[-5] else "Falling"
            sma_50_trend = "Rising" if recent_data['sma_50'].iloc[-1] > recent_data['sma_50'].iloc[-10] else "Falling"

            # Price vs SMAs
            above_sma20 = last_close > recent_data['sma_20'].iloc[-1]
            above_sma50 = last_close > recent_data['sma_50'].iloc[-1]

            # Volatility (as proxy for consolidation)
            volatility = recent_data['close'].pct_change().std() * 100

            trend_summary = f"""
Timeframe: Last {QUANT_LOOKBACK} candles

Price Movement:
- Start: ${first_close:.4f}
- End: ${last_close:.4f}
- Change: {price_change:+.2f}%

Moving Average Analysis:
- SMA 20 trend: {sma_20_trend}
- SMA 50 trend: {sma_50_trend}
- Price position: {'Above' if above_sma20 else 'Below'} SMA20, {'Above' if above_sma50 else 'Below'} SMA50

Volatility: {volatility:.2f}% ({'Low - Consolidating' if volatility < 1 else 'High - Trending'})

Trend Strength Indicators:
- Price/SMA20 alignment: {'Bullish' if above_sma20 and sma_20_trend == 'Rising' else 'Bearish' if not above_sma20 and sma_20_trend == 'Falling' else 'Mixed'}
- Higher highs/lows: {'Yes' if price_change > 0 else 'No'}
"""

            # Call AI for trend analysis
            response = self.model.generate_response(
                system_prompt=TREND_ANALYSIS_PROMPT.format(trend_data=trend_summary),
                user_content="Analyze trend as the Trend Agent.",
                temperature=0.1,
                max_tokens=500
            )

            # Parse response
            analysis = self._parse_agent_response(response, 'trend')

            cprint(f"✅ Trend Agent: {analysis.get('direction', 'UNKNOWN')} "
                   f"(Strength: {analysis.get('strength', 'UNKNOWN')}, Confidence: {analysis.get('confidence', 0)}%)", "green")

            return analysis

        except Exception as e:
            cprint(f"❌ Trend Agent error: {str(e)}", "red")
            traceback.print_exc()
            return None

    # ========================================================================
    # DECISION AGENT
    # ========================================================================

    def decision_agent_synthesis(self, indicator_analysis, pattern_analysis, trend_analysis, symbol):
        """
        DECISION AGENT: Synthesize all agent outputs into final trading decision
        Returns: BUY, SELL, or NOTHING with reasoning and risk parameters
        """
        try:
            cprint("\n🔴 DECISION AGENT synthesizing...", "red")

            # Format all analyses
            indicator_text = f"""
Direction: {indicator_analysis.get('direction', 'UNKNOWN')}
Summary: {indicator_analysis.get('summary', 'N/A')}
Confidence: {indicator_analysis.get('confidence', 0)}%
"""

            pattern_text = f"""
Pattern: {pattern_analysis.get('pattern', 'Unknown')}
Direction: {pattern_analysis.get('direction', 'UNKNOWN')}
Description: {pattern_analysis.get('description', 'N/A')}
Confidence: {pattern_analysis.get('confidence', 0)}%
"""

            trend_text = f"""
Direction: {trend_analysis.get('direction', 'UNKNOWN')}
Strength: {trend_analysis.get('strength', 'UNKNOWN')}
Description: {trend_analysis.get('description', 'N/A')}
Confidence: {trend_analysis.get('confidence', 0)}%
"""

            # Call AI for final decision
            response = self.model.generate_response(
                system_prompt=DECISION_SYNTHESIS_PROMPT.format(
                    indicator_analysis=indicator_text,
                    pattern_analysis=pattern_text,
                    trend_analysis=trend_text
                ),
                user_content=f"Synthesize all analyses for {symbol} and make final trading recommendation.",
                temperature=0.2,  # Slightly higher for decision making
                max_tokens=1000
            )

            # Parse response
            decision = self._parse_decision_response(response)

            # Add component analyses for reference
            decision['component_analyses'] = {
                'indicator': indicator_analysis,
                'pattern': pattern_analysis,
                'trend': trend_analysis
            }

            action = decision.get('action', 'NOTHING')
            confidence = decision.get('confidence', 0)

            color = 'green' if action == 'BUY' else 'red' if action == 'SELL' else 'yellow'
            cprint(f"\n{'='*60}", color)
            cprint(f"🎯 FINAL DECISION for {symbol}: {action} (Confidence: {confidence}%)", color)
            cprint(f"{'='*60}", color)

            return decision

        except Exception as e:
            cprint(f"❌ Decision Agent error: {str(e)}", "red")
            traceback.print_exc()
            return None

    # ========================================================================
    # MAIN ANALYSIS PIPELINE
    # ========================================================================

    def analyze(self, symbol, timeframe=DEFAULT_TIMEFRAME, bars=DEFAULT_BARS):
        """
        Main analysis pipeline: Run all 4 agents and return final decision

        Returns:
            dict: {
                'symbol': str,
                'action': 'BUY'|'SELL'|'NOTHING',
                'confidence': int (0-100),
                'position_type': 'LONG'|'SHORT',
                'reasoning': str,
                'stop_loss': str,
                'take_profit': str,
                'component_analyses': dict
            }
        """
        try:
            cprint(f"\n{'='*60}", "cyan")
            cprint(f"🌙 QuantAnalysis Agent: Analyzing {symbol} ({timeframe})", "cyan")
            cprint(f"{'='*60}", "cyan")

            start_time = time.time()

            # 1. Get market data
            data = self.get_market_data(symbol, timeframe, bars)
            if data is None or data.empty:
                return None

            # 2. Run Indicator Agent
            indicator_analysis = self.indicator_agent_analysis(data)
            if not indicator_analysis:
                cprint("⚠️ Indicator Agent failed", "yellow")
                return None

            # 3. Run Pattern Agent
            pattern_analysis = self.pattern_agent_analysis(data, symbol)
            if not pattern_analysis:
                cprint("⚠️ Pattern Agent failed", "yellow")
                return None

            # 4. Run Trend Agent
            trend_analysis = self.trend_agent_analysis(data)
            if not trend_analysis:
                cprint("⚠️ Trend Agent failed", "yellow")
                return None

            # 5. Run Decision Agent (synthesis)
            final_decision = self.decision_agent_synthesis(
                indicator_analysis,
                pattern_analysis,
                trend_analysis,
                symbol
            )

            if not final_decision:
                cprint("⚠️ Decision Agent failed", "yellow")
                return None

            # Add metadata
            final_decision['symbol'] = symbol
            final_decision['timeframe'] = timeframe
            final_decision['timestamp'] = datetime.now().isoformat()
            final_decision['analysis_time_seconds'] = round(time.time() - start_time, 2)

            # Save results
            self._save_analysis(final_decision)

            elapsed = time.time() - start_time
            cprint(f"\n✨ Analysis complete in {elapsed:.2f} seconds", "green")

            return final_decision

        except Exception as e:
            cprint(f"❌ Analysis pipeline error: {str(e)}", "red")
            traceback.print_exc()
            return None

    # ========================================================================
    # HELPER FUNCTIONS
    # ========================================================================

    def _generate_chart(self, data, symbol):
        """Generate candlestick chart for visual analysis"""
        try:
            # Use recent data for chart
            chart_data = data.tail(QUANT_LOOKBACK).copy()
            chart_data.index = pd.to_datetime(chart_data['timestamp'])

            # Create chart
            filename = f"{symbol}_{int(time.time())}.png"
            chart_path = self.charts_dir / filename

            # Plot with SMAs
            apds = []
            if 'sma_20' in chart_data.columns:
                apds.append(mpf.make_addplot(chart_data['sma_20'], color='blue', width=1.5))
            if 'sma_50' in chart_data.columns:
                apds.append(mpf.make_addplot(chart_data['sma_50'], color='orange', width=1.5))

            mpf.plot(
                chart_data[['open', 'high', 'low', 'close', 'volume']],
                type='candle',
                style=CHART_STYLE,
                volume=VOLUME_PANEL,
                addplot=apds if apds else None,
                title=f"\n{symbol} - QuantAnalysis Chart",
                savefig=chart_path
            )

            return chart_path

        except Exception as e:
            cprint(f"❌ Chart generation error: {str(e)}", "red")
            return None

    def _parse_agent_response(self, response, agent_type):
        """Parse individual agent response"""
        try:
            # Handle response format
            if hasattr(response, 'content'):
                text = response.content
            else:
                text = str(response)

            # Clean up response
            if isinstance(text, list):
                text = text[0].text if hasattr(text[0], 'text') else str(text[0])

            lines = [line.strip() for line in text.split('\n') if line.strip()]

            result = {
                'raw_response': text,
                'agent_type': agent_type
            }

            # Extract direction
            if lines:
                result['direction'] = lines[0].strip().upper()

            # Extract confidence
            confidence = 50  # Default
            for line in lines:
                if 'confidence' in line.lower():
                    try:
                        confidence = int(''.join(filter(str.isdigit, line)))
                        break
                    except:
                        pass
            result['confidence'] = confidence

            # Agent-specific parsing
            if agent_type == 'indicator':
                result['summary'] = lines[1] if len(lines) > 1 else ""
                result['signals'] = lines[2] if len(lines) > 2 else ""

            elif agent_type == 'pattern':
                result['pattern'] = lines[0] if lines else "Unknown"
                result['description'] = lines[1] if len(lines) > 1 else ""
                if len(lines) > 2:
                    result['direction'] = lines[2].split(':')[-1].strip().upper()

            elif agent_type == 'trend':
                result['description'] = lines[1] if len(lines) > 1 else ""
                result['strength'] = lines[2].split(':')[-1].strip().upper() if len(lines) > 2 else "MODERATE"

            return result

        except Exception as e:
            cprint(f"⚠️ Error parsing {agent_type} response: {str(e)}", "yellow")
            return {'direction': 'UNKNOWN', 'confidence': 0, 'agent_type': agent_type}

    def _parse_decision_response(self, response):
        """Parse Decision Agent response"""
        try:
            # Handle response format
            if hasattr(response, 'content'):
                text = response.content
            else:
                text = str(response)

            # Clean up response
            if isinstance(text, list):
                text = text[0].text if hasattr(text[0], 'text') else str(text[0])

            lines = [line.strip() for line in text.split('\n') if line.strip()]

            result = {
                'action': 'NOTHING',
                'position_type': '',
                'reasoning': '',
                'stop_loss': '',
                'take_profit': '',
                'confidence': 50,
                'raw_response': text
            }

            # Parse action (line 1)
            if lines:
                action = lines[0].strip().upper()
                if action in ['BUY', 'SELL', 'NOTHING']:
                    result['action'] = action

            # Parse position type (line 2)
            if len(lines) > 1 and result['action'] != 'NOTHING':
                pos_line = lines[1].upper()
                if 'LONG' in pos_line:
                    result['position_type'] = 'LONG'
                elif 'SHORT' in pos_line:
                    result['position_type'] = 'SHORT'

            # Parse reasoning (line 3)
            if len(lines) > 2:
                result['reasoning'] = lines[2]

            # Parse stop-loss (line 4)
            if len(lines) > 3:
                result['stop_loss'] = lines[3]

            # Parse take-profit (line 5)
            if len(lines) > 4:
                result['take_profit'] = lines[4]

            # Parse confidence (line 6)
            if len(lines) > 5:
                try:
                    conf_line = lines[5]
                    result['confidence'] = int(''.join(filter(str.isdigit, conf_line)))
                except:
                    pass

            return result

        except Exception as e:
            cprint(f"⚠️ Error parsing decision response: {str(e)}", "yellow")
            return {'action': 'NOTHING', 'confidence': 0}

    def _save_analysis(self, analysis):
        """Save analysis results to JSON"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{analysis['symbol']}_{timestamp}.json"
            filepath = self.results_dir / filename

            import json
            with open(filepath, 'w') as f:
                json.dump(analysis, f, indent=2)

            cprint(f"💾 Analysis saved to: {filepath}", "cyan")

        except Exception as e:
            cprint(f"⚠️ Could not save analysis: {str(e)}", "yellow")

    def run(self):
        """Run continuous monitoring (can be called from main.py)"""
        cprint("\n🚀 QuantAnalysis Agent starting continuous monitoring...", "cyan")

        # Get active tokens
        tokens = self.get_active_tokens()

        while True:
            try:
                for symbol in tokens:
                    analysis = self.analyze(symbol)

                    if analysis and analysis['action'] != 'NOTHING':
                        cprint(f"\n🎯 Trading signal for {symbol}: {analysis['action']}", "green")
                        # Signal can be picked up by trading_agent.py

                    time.sleep(5)  # Small delay between symbols

                # Sleep before next cycle
                cprint(f"\n💤 Sleeping for {SLEEP_BETWEEN_RUNS_MINUTES} minutes...", "yellow")
                time.sleep(SLEEP_BETWEEN_RUNS_MINUTES * 60)

            except KeyboardInterrupt:
                cprint("\n👋 QuantAnalysis Agent shutting down gracefully...", "yellow")
                break
            except Exception as e:
                cprint(f"❌ Error in main loop: {str(e)}", "red")
                time.sleep(60)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    """
    Standalone execution example
    """
    cprint("\n" + "="*60, "cyan")
    cprint("🌙 Moon Dev's QuantAnalysis Agent", "cyan")
    cprint("Multi-Agent Trading Analysis System", "cyan")
    cprint("Inspired by QuantAgent Research (Y-Research SBU)", "cyan")
    cprint("="*60 + "\n", "cyan")

    # Initialize agent
    agent = QuantAnalysisAgent()

    # Example: Analyze single symbol
    symbol = "BTC"  # HyperLiquid symbol

    cprint(f"📊 Running single analysis for {symbol}...\n", "cyan")
    result = agent.analyze(symbol, timeframe='1H', bars=100)

    if result:
        cprint(f"\n{'='*60}", "green")
        cprint(f"📈 ANALYSIS RESULTS for {symbol}:", "green")
        cprint(f"{'='*60}", "green")
        cprint(f"Action: {result['action']}", "cyan")
        cprint(f"Confidence: {result['confidence']}%", "cyan")
        cprint(f"Position: {result.get('position_type', 'N/A')}", "cyan")
        cprint(f"Reasoning: {result['reasoning']}", "cyan")
        cprint(f"Stop-Loss: {result['stop_loss']}", "cyan")
        cprint(f"Take-Profit: {result['take_profit']}", "cyan")
        cprint(f"Analysis Time: {result['analysis_time_seconds']}s", "cyan")
        cprint(f"{'='*60}\n", "green")
    else:
        cprint("❌ Analysis failed", "red")

    # Uncomment to run continuous monitoring
    # agent.run()

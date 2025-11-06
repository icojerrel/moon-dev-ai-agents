"""
🌙 Moon Dev's AI Trading System
Main entry point for running trading agents
"""

import os
import sys
from termcolor import cprint
from dotenv import load_dotenv
import time
from datetime import datetime, timedelta
from src.config import (
    MONITORED_TOKENS,
    EXCLUDED_TOKENS,
    SLEEP_BETWEEN_RUNS_MINUTES,
)

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Import agents
from src.agents.trading_agent import TradingAgent
from src.agents.risk_agent import RiskAgent
from src.agents.strategy_agent import StrategyAgent
from src.agents.copybot_agent import CopyBotAgent
from src.agents.sentiment_agent import SentimentAgent

# Try importing MT5 agent (Windows only)
try:
    from src.agents.mt5_trading_agent import MT5TradingAgent
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    cprint("⚠️ MT5 Trading Agent not available (Windows only)", "yellow")

# Load environment variables
load_dotenv()

# Agent Configuration
ACTIVE_AGENTS = {
    'risk': False,      # Risk management agent
    'trading': False,   # LLM trading agent
    'strategy': False,  # Strategy-based trading agent
    'copybot': False,   # CopyBot agent
    'sentiment': False, # Run sentiment_agent.py directly instead
    'mt5': False,       # MT5 trading agent (Windows only)
    # whale_agent is run from whale_agent.py
    # Add more agents here as we build them:
    # 'portfolio': False,  # Future portfolio optimization agent
}

def run_agents():
    """Run all active agents in sequence"""
    try:
        # Initialize active agents
        trading_agent = TradingAgent() if ACTIVE_AGENTS['trading'] else None
        risk_agent = RiskAgent() if ACTIVE_AGENTS['risk'] else None
        strategy_agent = StrategyAgent() if ACTIVE_AGENTS['strategy'] else None
        copybot_agent = CopyBotAgent() if ACTIVE_AGENTS['copybot'] else None
        sentiment_agent = SentimentAgent() if ACTIVE_AGENTS['sentiment'] else None
        mt5_agent = None

        # Initialize MT5 agent if available and enabled
        if ACTIVE_AGENTS['mt5']:
            if MT5_AVAILABLE:
                mt5_agent = MT5TradingAgent()
                if not mt5_agent.connect():
                    cprint("❌ Failed to connect MT5 agent, disabling...", "red")
                    mt5_agent = None
                else:
                    mt5_agent.initialize_model()
            else:
                cprint("⚠️ MT5 agent enabled but not available (Windows only)", "yellow")

        while True:
            try:
                # Run Risk Management
                if risk_agent:
                    cprint("\n🛡️ Running Risk Management...", "cyan")
                    risk_agent.run()

                # Run Trading Analysis
                if trading_agent:
                    cprint("\n🤖 Running Trading Analysis...", "cyan")
                    trading_agent.run()

                # Run Strategy Analysis
                if strategy_agent:
                    cprint("\n📊 Running Strategy Analysis...", "cyan")
                    for token in MONITORED_TOKENS:
                        if token not in EXCLUDED_TOKENS:  # Skip USDC and other excluded tokens
                            cprint(f"\n🔍 Analyzing {token}...", "cyan")
                            strategy_agent.get_signals(token)

                # Run CopyBot Analysis
                if copybot_agent:
                    cprint("\n🤖 Running CopyBot Portfolio Analysis...", "cyan")
                    copybot_agent.run_analysis_cycle()

                # Run Sentiment Analysis
                if sentiment_agent:
                    cprint("\n🎭 Running Sentiment Analysis...", "cyan")
                    sentiment_agent.run()

                # Run MT5 Trading (if enabled and connected)
                if mt5_agent:
                    cprint("\n📊 Running MT5 Trading Agent...", "cyan")
                    mt5_agent.run_cycle()

                # Sleep until next cycle
                next_run = datetime.now() + timedelta(minutes=SLEEP_BETWEEN_RUNS_MINUTES)
                cprint(f"\n😴 Sleeping until {next_run.strftime('%H:%M:%S')}", "cyan")
                time.sleep(60 * SLEEP_BETWEEN_RUNS_MINUTES)

            except Exception as e:
                cprint(f"\n❌ Error running agents: {str(e)}", "red")
                cprint("🔄 Continuing to next cycle...", "yellow")
                time.sleep(60)  # Sleep for 1 minute on error before retrying

    except KeyboardInterrupt:
        cprint("\n👋 Gracefully shutting down...", "yellow")
    except Exception as e:
        cprint(f"\n❌ Fatal error in main loop: {str(e)}", "red")
        raise

if __name__ == "__main__":
    cprint("\n🌙 Moon Dev AI Agent Trading System Starting...", "white", "on_blue")
    cprint("\n📊 Active Agents:", "white", "on_blue")
    for agent, active in ACTIVE_AGENTS.items():
        status = "✅ ON" if active else "❌ OFF"
        cprint(f"  • {agent.title()}: {status}", "white", "on_blue")
    print("\n")

    run_agents()
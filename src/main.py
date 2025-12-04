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
from config import *

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Import agents
from src.agents.trading_agent import TradingAgent
from src.agents.risk_agent import RiskAgent
from src.agents.strategy_agent import StrategyAgent
from src.agents.copybot_agent import CopyBotAgent
from src.agents.sentiment_agent import SentimentAgent

# Import Prometheus metrics for production monitoring
from src.utils.prometheus_metrics import metrics

# Load environment variables
load_dotenv()

# Agent Configuration
ACTIVE_AGENTS = {
    'risk': False,      # Risk management agent
    'trading': False,   # LLM trading agent
    'strategy': False,  # Strategy-based trading agent
    'copybot': False,   # CopyBot agent
    'sentiment': False, # Run sentiment_agent.py directly instead
    # whale_agent is run from whale_agent.py
    # Add more agents here as we build them:
    # 'portfolio': False,  # Future portfolio optimization agent
}

@metrics.track_agent_run('main_loop')
def run_agents():
    """Run all active agents in sequence"""
    try:
        # Initialize active agents
        trading_agent = TradingAgent() if ACTIVE_AGENTS['trading'] else None
        risk_agent = RiskAgent() if ACTIVE_AGENTS['risk'] else None
        strategy_agent = StrategyAgent() if ACTIVE_AGENTS['strategy'] else None
        copybot_agent = CopyBotAgent() if ACTIVE_AGENTS['copybot'] else None
        sentiment_agent = SentimentAgent() if ACTIVE_AGENTS['sentiment'] else None

        while True:
            try:
                # Run Risk Management
                if risk_agent:
                    cprint("\n🛡️ Running Risk Management...", "cyan")
                    with metrics.track_agent_run('risk_agent'):
                        risk_agent.run()

                # Run Trading Analysis
                if trading_agent:
                    cprint("\n🤖 Running Trading Analysis...", "cyan")
                    with metrics.track_agent_run('trading_agent'):
                        trading_agent.run()

                # Run Strategy Analysis
                if strategy_agent:
                    cprint("\n📊 Running Strategy Analysis...", "cyan")
                    with metrics.track_agent_run('strategy_agent'):
                        for token in MONITORED_TOKENS:
                            if token not in EXCLUDED_TOKENS:  # Skip USDC and other excluded tokens
                                cprint(f"\n🔍 Analyzing {token}...", "cyan")
                                strategy_agent.get_signals(token)

                # Run CopyBot Analysis
                if copybot_agent:
                    cprint("\n🤖 Running CopyBot Portfolio Analysis...", "cyan")
                    with metrics.track_agent_run('copybot_agent'):
                        copybot_agent.run_analysis_cycle()

                # Run Sentiment Analysis
                if sentiment_agent:
                    cprint("\n🎭 Running Sentiment Analysis...", "cyan")
                    with metrics.track_agent_run('sentiment_agent'):
                        sentiment_agent.run()

                # Sleep until next cycle
                next_run = datetime.now() + timedelta(minutes=SLEEP_BETWEEN_RUNS_MINUTES)
                cprint(f"\n😴 Sleeping until {next_run.strftime('%H:%M:%S')}", "cyan")
                time.sleep(60 * SLEEP_BETWEEN_RUNS_MINUTES)

            except Exception as e:
                cprint(f"\n❌ Error running agents: {str(e)}", "red")
                cprint("🔄 Continuing to next cycle...", "yellow")
                metrics.system.errors_total.labels(error_type='agent_error').inc()
                time.sleep(60)  # Sleep for 1 minute on error before retrying

    except KeyboardInterrupt:
        cprint("\n👋 Gracefully shutting down...", "yellow")
    except Exception as e:
        cprint(f"\n❌ Fatal error in main loop: {str(e)}", "red")
        metrics.system.errors_total.labels(error_type='fatal_error').inc()
        raise

if __name__ == "__main__":
    cprint("\n🌙 Moon Dev AI Agent Trading System Starting...", "white", "on_blue")

    # Start Prometheus metrics server for production monitoring
    try:
        metrics.start_server(port=8000)
        cprint("\n📊 Prometheus Metrics Server Started", "green", attrs=['bold'])
        cprint("   🌐 Metrics available at: http://localhost:8000/metrics", "cyan")
        cprint("   📈 Use Prometheus + Grafana for visualization", "white")
    except OSError as e:
        if "Address already in use" in str(e):
            cprint("\n⚠️  Metrics server already running on port 8000", "yellow")
        else:
            cprint(f"\n⚠️  Could not start metrics server: {e}", "yellow")
            cprint("   Continuing without metrics...", "white")

    cprint("\n📊 Active Agents:", "white", "on_blue")
    for agent, active in ACTIVE_AGENTS.items():
        status = "✅ ON" if active else "❌ OFF"
        cprint(f"  • {agent.title()}: {status}", "white", "on_blue")
    print("\n")

    run_agents()
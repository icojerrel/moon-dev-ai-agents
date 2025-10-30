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

# Phase 3: Smart Scheduling - Different agents run at different intervals
# This optimizes costs by not running all agents every 15 minutes
AGENT_SCHEDULES = {
    'risk': 15,        # Every 15 min (critical - run frequently)
    'trading': 15,     # Every 15 min (time-sensitive)
    'sentiment': 30,   # Every 30 min (sentiment changes slower)
    'copybot': 30,     # Every 30 min (portfolio analysis)
    'strategy': 60,    # Every 60 min (long-term signals)
}

# Phase 3: Cost tracking
class CostTracker:
    """Simple cost tracker for monitoring API usage"""
    def __init__(self):
        self.api_calls = 0
        self.cache_hits = 0
        self.start_time = datetime.now()

    def track_cycle(self, agents_run):
        """Track a completed cycle"""
        self.api_calls += len(agents_run) * 3  # Estimate ~3 API calls per agent

    def get_stats(self):
        """Get current stats"""
        runtime = (datetime.now() - self.start_time).total_seconds() / 3600
        return {
            'runtime_hours': runtime,
            'api_calls': self.api_calls,
            'calls_per_hour': self.api_calls / runtime if runtime > 0 else 0
        }

cost_tracker = CostTracker()

def run_agents():
    """Phase 3: Run agents with smart scheduling and cost tracking"""
    try:
        # Initialize active agents
        agents = {}
        if ACTIVE_AGENTS['trading']:
            agents['trading'] = TradingAgent()
        if ACTIVE_AGENTS['risk']:
            agents['risk'] = RiskAgent()
        if ACTIVE_AGENTS['strategy']:
            agents['strategy'] = StrategyAgent()
        if ACTIVE_AGENTS['copybot']:
            agents['copybot'] = CopyBotAgent()
        if ACTIVE_AGENTS['sentiment']:
            agents['sentiment'] = SentimentAgent()

        # Track last run time for each agent
        last_run = {agent: datetime.min for agent in agents.keys()}
        cycle_count = 0

        cprint("\n✅ Phase 3 Optimizations Active:", "green")
        cprint("  • Smart scheduling (different intervals per agent)", "green")
        cprint("  • Cost tracking enabled", "green")
        cprint("  • BirdEye API caching (75% reduction)", "green")
        cprint("  • OpenRouter with free tier model\n", "green")

        while True:
            try:
                cycle_count += 1
                now = datetime.now()
                agents_to_run = []

                cprint(f"\n{'='*60}", "white", "on_blue")
                cprint(f"🔄 Cycle #{cycle_count} - {now.strftime('%H:%M:%S')}", "white", "on_blue")
                cprint(f"{'='*60}\n", "white", "on_blue")

                # Check which agents should run based on their schedule
                for agent_name, agent in agents.items():
                    interval = AGENT_SCHEDULES.get(agent_name, 15)
                    time_since_last = (now - last_run[agent_name]).total_seconds() / 60

                    if time_since_last >= interval:
                        agents_to_run.append(agent_name)
                        last_run[agent_name] = now

                        # Run the agent
                        try:
                            if agent_name == 'risk':
                                cprint("\n🛡️ Running Risk Management...", "cyan")
                                agent.run()
                            elif agent_name == 'trading':
                                cprint("\n🤖 Running Trading Analysis...", "cyan")
                                agent.run()
                            elif agent_name == 'strategy':
                                cprint("\n📊 Running Strategy Analysis...", "cyan")
                                for token in MONITORED_TOKENS:
                                    if token not in EXCLUDED_TOKENS:
                                        cprint(f"\n🔍 Analyzing {token}...", "cyan")
                                        agent.get_signals(token)
                            elif agent_name == 'copybot':
                                cprint("\n🤖 Running CopyBot Portfolio Analysis...", "cyan")
                                agent.run_analysis_cycle()
                            elif agent_name == 'sentiment':
                                cprint("\n🎭 Running Sentiment Analysis...", "cyan")
                                agent.run()

                            cprint(f"✅ {agent_name.title()} completed", "green")

                        except Exception as e:
                            cprint(f"❌ {agent_name.title()} error: {str(e)}", "red")

                # Track costs
                cost_tracker.track_cycle(agents_to_run)

                # Display stats
                if agents_to_run:
                    cprint(f"\n📊 This cycle: {len(agents_to_run)} agents ran", "yellow")
                else:
                    cprint("\n⏭️ No agents due this cycle", "yellow")

                # Show next run times
                cprint("\n⏰ Next scheduled runs:", "cyan")
                for agent_name in agents.keys():
                    interval = AGENT_SCHEDULES.get(agent_name, 15)
                    next_run = last_run[agent_name] + timedelta(minutes=interval)
                    minutes_until = (next_run - now).total_seconds() / 60
                    cprint(f"  • {agent_name.title()}: {next_run.strftime('%H:%M:%S')} ({minutes_until:.0f} min)", "cyan")

                # Show cost stats every 10 cycles
                if cycle_count % 10 == 0:
                    stats = cost_tracker.get_stats()
                    cprint(f"\n💰 Cost Stats (last {stats['runtime_hours']:.1f}h):", "yellow")
                    cprint(f"  • API calls: {stats['api_calls']}", "yellow")
                    cprint(f"  • Calls/hour: {stats['calls_per_hour']:.1f}", "yellow")

                # Sleep for 1 minute before next check
                time.sleep(60)

            except Exception as e:
                cprint(f"\n❌ Error in cycle: {str(e)}", "red")
                cprint("🔄 Continuing to next cycle...", "yellow")
                time.sleep(60)

    except KeyboardInterrupt:
        cprint("\n👋 Gracefully shutting down...", "yellow")
        stats = cost_tracker.get_stats()
        cprint(f"\n📊 Final Stats:", "cyan")
        cprint(f"  • Runtime: {stats['runtime_hours']:.2f} hours", "cyan")
        cprint(f"  • Total API calls: {stats['api_calls']}", "cyan")
        cprint(f"  • Average calls/hour: {stats['calls_per_hour']:.1f}", "cyan")
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
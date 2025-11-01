"""
🌙 Moon Dev's AI Trading System
Main entry point for running trading agents

Optimized with:
- Parallel execution for independent agents
- Retry logic with exponential backoff
- Real-time monitoring and health checks
- Performance profiling and metrics
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
from src.agents.orchestrator_monitor import OrchestratorMonitor

# Load environment variables
load_dotenv()

# Agent Configuration
ACTIVE_AGENTS = {
    'risk': False,      # Risk management agent (runs first, sequential)
    'trading': False,   # LLM trading agent (parallel)
    'strategy': False,  # Strategy-based trading agent (parallel)
    'copybot': False,   # CopyBot agent (parallel)
    'sentiment': False, # Sentiment analysis agent (parallel)
    # whale_agent is run from whale_agent.py
    # Add more agents here as we build them:
    # 'portfolio': False,  # Future portfolio optimization agent
}

# Orchestrator Configuration
ORCHESTRATOR_CONFIG = {
    'max_retries': 3,           # Max retries for failed agents
    'timeout_per_agent': 300,   # 5 minutes timeout per agent
    'backoff_multiplier': 2.0,  # Exponential backoff multiplier
    'max_workers': 4,           # Max parallel workers
    'enable_monitoring': True,  # Enable monitoring dashboard
    'enable_health_checks': True,  # Enable agent health checks
    'metrics_export_dir': 'src/data/orchestrator/',  # Metrics export directory
}

def run_agents():
    """
    Run all active agents with optimized orchestration

    Execution Strategy:
    1. Risk Agent runs first (sequential, with retry) - critical path
    2. Other agents run in parallel (trading, strategy, copybot, sentiment)
    3. Monitoring and health checks track performance
    4. Dashboard displays after each cycle
    """
    try:
        # Initialize orchestrator monitor
        monitor = OrchestratorMonitor(
            metrics_dir=ORCHESTRATOR_CONFIG['metrics_export_dir']
        )

        # Initialize active agents
        trading_agent = TradingAgent() if ACTIVE_AGENTS['trading'] else None
        risk_agent = RiskAgent() if ACTIVE_AGENTS['risk'] else None
        strategy_agent = StrategyAgent() if ACTIVE_AGENTS['strategy'] else None
        copybot_agent = CopyBotAgent() if ACTIVE_AGENTS['copybot'] else None
        sentiment_agent = SentimentAgent() if ACTIVE_AGENTS['sentiment'] else None

        # Main orchestration loop
        while True:
            try:
                # Start cycle tracking
                monitor.start_cycle()
                cprint(f"\n{'='*80}", "cyan")
                cprint(f"🌙 CYCLE START - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "cyan", attrs=['bold'])
                cprint(f"{'='*80}", "cyan")

                # Phase 1: Run Risk Management (CRITICAL - Sequential with retry)
                if risk_agent:
                    cprint("\n🛡️ Phase 1: Risk Management (Sequential)", "cyan", attrs=['bold'])

                    def run_risk_agent():
                        """Wrapper for risk agent execution"""
                        cprint("\n🛡️ Running Risk Management...", "cyan")
                        risk_agent.run()

                        # Enhanced metrics if available
                        if hasattr(risk_agent, 'calculate_enhanced_metrics'):
                            cprint("\n📊 Calculating Enhanced Risk Metrics...", "cyan")
                            risk_agent.calculate_enhanced_metrics(show_dashboard=True)

                    # Run with retry logic
                    monitor.run_agent_with_retry(
                        agent_name='risk',
                        agent_func=run_risk_agent,
                        max_retries=ORCHESTRATOR_CONFIG['max_retries'],
                        timeout_seconds=ORCHESTRATOR_CONFIG['timeout_per_agent'],
                        backoff_multiplier=ORCHESTRATOR_CONFIG['backoff_multiplier']
                    )

                # Phase 2: Run Independent Agents in Parallel
                parallel_agents = []

                if trading_agent:
                    def run_trading_agent():
                        cprint("\n🤖 Running Trading Analysis...", "cyan")
                        trading_agent.run()
                    parallel_agents.append(('trading', run_trading_agent))

                if strategy_agent:
                    def run_strategy_agent():
                        cprint("\n📊 Running Strategy Analysis...", "cyan")
                        for token in MONITORED_TOKENS:
                            if token not in EXCLUDED_TOKENS:
                                cprint(f"🔍 Analyzing {token}...", "cyan")
                                strategy_agent.get_signals(token)
                    parallel_agents.append(('strategy', run_strategy_agent))

                if copybot_agent:
                    def run_copybot_agent():
                        cprint("\n🤖 Running CopyBot Portfolio Analysis...", "cyan")
                        copybot_agent.run_analysis_cycle()
                    parallel_agents.append(('copybot', run_copybot_agent))

                if sentiment_agent:
                    def run_sentiment_agent():
                        cprint("\n🎭 Running Sentiment Analysis...", "cyan")
                        sentiment_agent.run()
                    parallel_agents.append(('sentiment', run_sentiment_agent))

                # Execute parallel agents if any are active
                if parallel_agents:
                    cprint(f"\n⚡ Phase 2: Running {len(parallel_agents)} agents in parallel", "cyan", attrs=['bold'])
                    monitor.run_agents_parallel(
                        agents=parallel_agents,
                        max_workers=ORCHESTRATOR_CONFIG['max_workers'],
                        timeout_per_agent=ORCHESTRATOR_CONFIG['timeout_per_agent']
                    )

                # End cycle tracking
                monitor.end_cycle()

                # Display monitoring dashboard
                if ORCHESTRATOR_CONFIG['enable_monitoring']:
                    cprint(f"\n{'='*80}", "yellow")
                    cprint("📊 CYCLE SUMMARY", "yellow", attrs=['bold'])
                    cprint(f"{'='*80}", "yellow")
                    monitor.display_dashboard()

                # Export metrics
                monitor.export_metrics(format='json')

                # Calculate sleep time
                next_run = datetime.now() + timedelta(minutes=SLEEP_BETWEEN_RUNS_MINUTES)
                cprint(f"\n{'='*80}", "green")
                cprint(f"😴 Sleeping until {next_run.strftime('%Y-%m-%d %H:%M:%S')}", "green", attrs=['bold'])
                cprint(f"{'='*80}\n", "green")
                time.sleep(60 * SLEEP_BETWEEN_RUNS_MINUTES)

            except KeyboardInterrupt:
                raise  # Re-raise to outer handler
            except Exception as e:
                cprint(f"\n❌ Error in orchestration cycle: {str(e)}", "red")
                cprint("🔄 Continuing to next cycle in 60 seconds...", "yellow")

                # Log error to monitor
                monitor.end_cycle()

                time.sleep(60)  # Sleep for 1 minute on error before retrying

    except KeyboardInterrupt:
        cprint("\n👋 Gracefully shutting down...", "yellow")

        # Display final metrics
        if ORCHESTRATOR_CONFIG['enable_monitoring']:
            cprint("\n📊 Final Metrics Summary:", "yellow")
            monitor.display_dashboard()
            monitor.export_metrics(format='json')

    except Exception as e:
        cprint(f"\n❌ Fatal error in main loop: {str(e)}", "red")

        # Export crash report
        if ORCHESTRATOR_CONFIG['enable_monitoring']:
            monitor.export_metrics(format='json')

        raise

if __name__ == "__main__":
    cprint("\n🌙 Moon Dev AI Agent Trading System Starting...", "white", "on_blue")
    cprint("\n📊 Active Agents:", "white", "on_blue")
    for agent, active in ACTIVE_AGENTS.items():
        status = "✅ ON" if active else "❌ OFF"
        cprint(f"  • {agent.title()}: {status}", "white", "on_blue")
    print("\n")

    run_agents()
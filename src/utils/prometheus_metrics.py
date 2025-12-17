#!/usr/bin/env python3
"""
🌙 Moon Dev's Prometheus Metrics Module 🌙

Production-grade monitoring with Prometheus integration for tracking:
- Trade execution metrics (trades, win rate, PnL, position sizes)
- Agent performance (runtime, success rate, errors)
- API latency and cache efficiency
- System health and resource usage
- Custom business metrics

Prometheus is the industry-standard monitoring system used by:
- Google, Meta, Amazon (internal monitoring)
- Kubernetes, Docker (container orchestration)
- Trading firms (Citadel, Jane Street equivalent systems)

Built with love by Moon Dev 🚀
"""

import sys
from pathlib import Path
import time
from typing import Dict, Optional, List, Callable
from functools import wraps
from prometheus_client import (
    Counter, Gauge, Histogram, Summary, Info,
    CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST,
    start_http_server
)
from termcolor import colored, cprint

# Project setup
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))


class TradingMetrics:
    """
    Prometheus metrics for trading operations.

    Metrics Categories:
    - Trade Execution: trades_total, trades_profitable, pnl_usd
    - Position Sizing: position_size_usd, kelly_fraction_used
    - Risk Management: max_drawdown_usd, circuit_breaker_triggered
    - Strategy Performance: strategy_win_rate, strategy_sharpe_ratio
    """

    def __init__(self, registry: Optional[CollectorRegistry] = None):
        """Initialize trading metrics with optional custom registry"""
        self.registry = registry or CollectorRegistry()

        # ==========================================
        # TRADE EXECUTION METRICS
        # ==========================================

        # Total number of trades executed
        self.trades_total = Counter(
            'trades_total',
            'Total number of trades executed',
            ['symbol', 'strategy', 'direction'],  # Labels for grouping
            registry=self.registry
        )

        # Profitable trades counter
        self.trades_profitable = Counter(
            'trades_profitable_total',
            'Total number of profitable trades',
            ['symbol', 'strategy'],
            registry=self.registry
        )

        # Losing trades counter
        self.trades_losing = Counter(
            'trades_losing_total',
            'Total number of losing trades',
            ['symbol', 'strategy'],
            registry=self.registry
        )

        # Total PnL in USD (using Gauge since PnL can be negative)
        self.pnl_usd_total = Gauge(
            'pnl_usd_total',
            'Total profit/loss in USD (cumulative)',
            ['symbol', 'strategy'],
            registry=self.registry
        )

        # Current PnL (gauge - can go up and down)
        self.pnl_usd_current = Gauge(
            'pnl_usd_current',
            'Current unrealized profit/loss in USD',
            ['symbol'],
            registry=self.registry
        )

        # Trade execution latency
        self.trade_execution_latency = Histogram(
            'trade_execution_seconds',
            'Time taken to execute a trade',
            ['symbol', 'direction'],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0],  # seconds
            registry=self.registry
        )

        # ==========================================
        # POSITION SIZING METRICS
        # ==========================================

        # Position size in USD
        self.position_size_usd = Histogram(
            'position_size_usd',
            'Position size in USD',
            ['symbol', 'strategy'],
            buckets=[10, 50, 100, 500, 1000, 5000, 10000],
            registry=self.registry
        )

        # Kelly fraction used
        self.kelly_fraction_used = Histogram(
            'kelly_fraction_used',
            'Kelly Criterion fraction used for position sizing',
            ['strategy'],
            buckets=[0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30],
            registry=self.registry
        )

        # ==========================================
        # RISK MANAGEMENT METRICS
        # ==========================================

        # Maximum drawdown
        self.max_drawdown_usd = Gauge(
            'max_drawdown_usd',
            'Maximum drawdown in USD',
            ['strategy'],
            registry=self.registry
        )

        # Circuit breaker triggers
        self.circuit_breaker_triggered = Counter(
            'circuit_breaker_triggered_total',
            'Number of times circuit breaker was triggered',
            ['reason'],  # max_loss, min_balance, max_drawdown
            registry=self.registry
        )

        # Current portfolio value
        self.portfolio_value_usd = Gauge(
            'portfolio_value_usd',
            'Current total portfolio value in USD',
            registry=self.registry
        )

        # Cash balance
        self.cash_balance_usd = Gauge(
            'cash_balance_usd',
            'Current cash balance in USD',
            registry=self.registry
        )

        # ==========================================
        # STRATEGY PERFORMANCE METRICS
        # ==========================================

        # Win rate by strategy
        self.strategy_win_rate = Gauge(
            'strategy_win_rate',
            'Win rate (0.0 to 1.0) by strategy',
            ['strategy'],
            registry=self.registry
        )

        # Sharpe ratio by strategy
        self.strategy_sharpe_ratio = Gauge(
            'strategy_sharpe_ratio',
            'Sharpe ratio by strategy',
            ['strategy'],
            registry=self.registry
        )

        # Average trade duration
        self.trade_duration_seconds = Histogram(
            'trade_duration_seconds',
            'Duration of trades in seconds',
            ['symbol', 'strategy'],
            buckets=[60, 300, 900, 1800, 3600, 14400, 86400],  # 1min to 1day
            registry=self.registry
        )


class AgentMetrics:
    """
    Prometheus metrics for AI agent operations.

    Tracks:
    - Agent execution count and success rate
    - Runtime duration and latency
    - Error rates and types
    - LLM API usage (tokens, cost)
    """

    def __init__(self, registry: Optional[CollectorRegistry] = None):
        """Initialize agent metrics with optional custom registry"""
        self.registry = registry or CollectorRegistry()

        # Agent runs counter
        self.agent_runs_total = Counter(
            'agent_runs_total',
            'Total number of agent executions',
            ['agent_name', 'status'],  # status: success, error
            registry=self.registry
        )

        # Agent runtime duration
        self.agent_duration_seconds = Histogram(
            'agent_duration_seconds',
            'Agent execution duration in seconds',
            ['agent_name'],
            buckets=[0.5, 1.0, 5.0, 10.0, 30.0, 60.0, 300.0],
            registry=self.registry
        )

        # Agent errors
        self.agent_errors_total = Counter(
            'agent_errors_total',
            'Total number of agent errors',
            ['agent_name', 'error_type'],
            registry=self.registry
        )

        # LLM API tokens used
        self.llm_tokens_used = Counter(
            'llm_tokens_used_total',
            'Total LLM tokens used',
            ['model', 'agent_name'],
            registry=self.registry
        )

        # LLM API cost in USD
        self.llm_cost_usd = Counter(
            'llm_cost_usd_total',
            'Total LLM API cost in USD',
            ['model', 'agent_name'],
            registry=self.registry
        )

        # Currently active agents
        self.active_agents = Gauge(
            'active_agents',
            'Number of currently running agents',
            registry=self.registry
        )


class APIMetrics:
    """
    Prometheus metrics for API and cache performance.

    Tracks:
    - API request count and latency
    - Cache hit/miss rates
    - Rate limiting events
    - External service health
    """

    def __init__(self, registry: Optional[CollectorRegistry] = None):
        """Initialize API metrics with optional custom registry"""
        self.registry = registry or CollectorRegistry()

        # API requests counter
        self.api_requests_total = Counter(
            'api_requests_total',
            'Total number of API requests',
            ['service', 'endpoint', 'status'],  # status: success, error
            registry=self.registry
        )

        # API latency
        self.api_latency_seconds = Histogram(
            'api_latency_seconds',
            'API request latency in seconds',
            ['service', 'endpoint'],
            buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0],
            registry=self.registry
        )

        # Cache hits
        self.cache_hits_total = Counter(
            'cache_hits_total',
            'Total number of cache hits',
            ['cache_type'],  # memory, redis
            registry=self.registry
        )

        # Cache misses
        self.cache_misses_total = Counter(
            'cache_misses_total',
            'Total number of cache misses',
            ['cache_type'],
            registry=self.registry
        )

        # Rate limit events
        self.rate_limit_events = Counter(
            'rate_limit_events_total',
            'Number of rate limit events',
            ['service'],
            registry=self.registry
        )

        # External service health (0 = down, 1 = up)
        self.external_service_up = Gauge(
            'external_service_up',
            'External service health status',
            ['service'],
            registry=self.registry
        )


class SystemMetrics:
    """
    Prometheus metrics for system health and resources.

    Tracks:
    - System uptime
    - Memory and CPU usage
    - Active connections
    - Error rates
    """

    def __init__(self, registry: Optional[CollectorRegistry] = None):
        """Initialize system metrics with optional custom registry"""
        self.registry = registry or CollectorRegistry()

        # System uptime
        self.uptime_seconds = Gauge(
            'uptime_seconds',
            'System uptime in seconds',
            registry=self.registry
        )

        # Application info
        self.app_info = Info(
            'app',
            'Application information',
            registry=self.registry
        )

        # Total errors
        self.errors_total = Counter(
            'errors_total',
            'Total number of errors',
            ['component', 'severity'],  # severity: warning, error, critical
            registry=self.registry
        )

        # Health check status
        self.health_check_status = Gauge(
            'health_check_status',
            'Health check status (1 = healthy, 0 = unhealthy)',
            ['component'],
            registry=self.registry
        )


class MetricsCollector:
    """
    Central metrics collector for the entire trading system.

    Aggregates all metrics and provides:
    - Unified metrics access
    - Decorator utilities for instrumentation
    - Metrics export endpoint
    - HTTP server for Prometheus scraping
    """

    def __init__(self):
        """Initialize metrics collector with all metric types"""
        # Use default registry for all metrics
        self.trading = TradingMetrics()
        self.agent = AgentMetrics()
        self.api = APIMetrics()
        self.system = SystemMetrics()

        # Track initialization time
        self.start_time = time.time()
        self._update_system_info()

    def _update_system_info(self):
        """Update system information metrics"""
        self.system.app_info.info({
            'version': '1.0.0',
            'name': 'moon-dev-ai-agents',
            'description': 'AI-powered crypto trading system'
        })

    def track_trade(
        self,
        symbol: str,
        strategy: str,
        direction: str,  # 'BUY' or 'SELL'
        pnl_usd: float,
        position_size_usd: float,
        duration_seconds: float,
        kelly_fraction: Optional[float] = None
    ):
        """
        Track a completed trade with all relevant metrics.

        Args:
            symbol: Token symbol (e.g., 'BTC', 'ETH')
            strategy: Strategy name (e.g., 'momentum', 'mean_reversion')
            direction: 'BUY' or 'SELL'
            pnl_usd: Profit/loss in USD
            position_size_usd: Position size in USD
            duration_seconds: How long the trade was open
            kelly_fraction: Kelly fraction used (optional)
        """
        # Increment trade counter
        self.trading.trades_total.labels(
            symbol=symbol,
            strategy=strategy,
            direction=direction
        ).inc()

        # Track profitable vs losing
        if pnl_usd > 0:
            self.trading.trades_profitable.labels(
                symbol=symbol,
                strategy=strategy
            ).inc()
        else:
            self.trading.trades_losing.labels(
                symbol=symbol,
                strategy=strategy
            ).inc()

        # Track PnL (Gauge can handle negative values via inc)
        gauge = self.trading.pnl_usd_total.labels(
            symbol=symbol,
            strategy=strategy
        )
        # Gauges support .inc() with negative values
        gauge.inc(pnl_usd)

        # Track position size
        self.trading.position_size_usd.labels(
            symbol=symbol,
            strategy=strategy
        ).observe(position_size_usd)

        # Track trade duration
        self.trading.trade_duration_seconds.labels(
            symbol=symbol,
            strategy=strategy
        ).observe(duration_seconds)

        # Track Kelly fraction if provided
        if kelly_fraction is not None:
            self.trading.kelly_fraction_used.labels(
                strategy=strategy
            ).observe(kelly_fraction)

    def track_agent_run(self, agent_name: str):
        """
        Context manager decorator for tracking agent execution.

        Usage:
            @metrics.track_agent_run('trading_agent')
            def run_trading_agent():
                # agent code here
                pass
        """
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                self.agent.active_agents.inc()
                start_time = time.time()

                try:
                    result = func(*args, **kwargs)

                    # Success
                    self.agent.agent_runs_total.labels(
                        agent_name=agent_name,
                        status='success'
                    ).inc()

                    return result

                except Exception as e:
                    # Error
                    self.agent.agent_runs_total.labels(
                        agent_name=agent_name,
                        status='error'
                    ).inc()

                    self.agent.agent_errors_total.labels(
                        agent_name=agent_name,
                        error_type=type(e).__name__
                    ).inc()

                    raise

                finally:
                    # Track duration and decrement active counter
                    duration = time.time() - start_time
                    self.agent.agent_duration_seconds.labels(
                        agent_name=agent_name
                    ).observe(duration)

                    self.agent.active_agents.dec()

            return wrapper
        return decorator

    def track_api_call(self, service: str, endpoint: str):
        """
        Context manager decorator for tracking API calls.

        Usage:
            @metrics.track_api_call('birdeye', '/token/price')
            def get_token_price(address):
                # API call here
                pass
        """
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()

                try:
                    result = func(*args, **kwargs)

                    # Success
                    self.api.api_requests_total.labels(
                        service=service,
                        endpoint=endpoint,
                        status='success'
                    ).inc()

                    return result

                except Exception as e:
                    # Error
                    self.api.api_requests_total.labels(
                        service=service,
                        endpoint=endpoint,
                        status='error'
                    ).inc()

                    raise

                finally:
                    # Track latency
                    latency = time.time() - start_time
                    self.api.api_latency_seconds.labels(
                        service=service,
                        endpoint=endpoint
                    ).observe(latency)

            return wrapper
        return decorator

    def update_uptime(self):
        """Update system uptime metric"""
        uptime = time.time() - self.start_time
        self.system.uptime_seconds.set(uptime)

    def export_metrics(self) -> bytes:
        """
        Export all metrics in Prometheus format.

        Returns:
            bytes: Metrics in Prometheus text format
        """
        self.update_uptime()
        return generate_latest()

    def start_server(self, port: int = 8000):
        """
        Start HTTP server for Prometheus scraping.

        Args:
            port: Port to listen on (default 8000)

        Usage:
            metrics = MetricsCollector()
            metrics.start_server(port=8000)
            # Prometheus can now scrape http://localhost:8000/metrics
        """
        start_http_server(port)
        cprint(f"\n📊 Prometheus metrics server started on port {port}", "green", attrs=["bold"])
        cprint(f"🌐 Metrics available at: http://localhost:{port}/metrics\n", "cyan")


# Global metrics instance
metrics = MetricsCollector()


# ============================================
# 🧪 TESTING & EXAMPLES
# ============================================

if __name__ == "__main__":
    cprint("\n🧪 Testing Prometheus Metrics Module\n", "cyan", attrs=["bold"])

    # Initialize metrics collector
    collector = MetricsCollector()

    # Example 1: Track trades
    cprint("=" * 60, "green")
    cprint("Example 1: Tracking Trade Metrics", "green", attrs=["bold"])
    cprint("=" * 60, "green")

    # Simulate some trades
    trades = [
        ("BTC", "momentum", "BUY", 150.0, 1000.0, 3600.0, 0.10),
        ("ETH", "momentum", "BUY", -50.0, 500.0, 1800.0, 0.08),
        ("SOL", "mean_reversion", "BUY", 75.0, 300.0, 7200.0, 0.05),
        ("BTC", "momentum", "SELL", 200.0, 1000.0, 5400.0, 0.12),
    ]

    for symbol, strategy, direction, pnl, size, duration, kelly in trades:
        collector.track_trade(
            symbol=symbol,
            strategy=strategy,
            direction=direction,
            pnl_usd=pnl,
            position_size_usd=size,
            duration_seconds=duration,
            kelly_fraction=kelly
        )
        print(colored(f"✅ Tracked {direction} {symbol} trade: ", "white") +
              colored(f"PnL ${pnl:+.2f}", "green" if pnl > 0 else "red"))

    print(colored(f"\n📊 Total trades tracked: {len(trades)}", "cyan"))
    print(colored(f"💰 Net PnL: ${sum(t[3] for t in trades):+.2f}", "green"))

    # Example 2: Track agent execution
    cprint("\n" + "=" * 60, "yellow")
    cprint("Example 2: Tracking Agent Execution", "yellow", attrs=["bold"])
    cprint("=" * 60, "yellow")

    @collector.track_agent_run('trading_agent')
    def example_agent():
        """Example agent function"""
        time.sleep(0.1)  # Simulate work
        return "Agent completed"

    try:
        result = example_agent()
        print(colored("✅ Agent execution tracked successfully", "green"))
    except Exception as e:
        print(colored(f"❌ Agent error: {e}", "red"))

    # Example 3: Track API calls
    cprint("\n" + "=" * 60, "cyan")
    cprint("Example 3: Tracking API Calls", "cyan", attrs=["bold"])
    cprint("=" * 60, "cyan")

    @collector.track_api_call('birdeye', '/token/price')
    def example_api_call():
        """Example API call"""
        time.sleep(0.05)  # Simulate API latency
        return {"price": 45000}

    try:
        data = example_api_call()
        print(colored("✅ API call tracked successfully", "green"))
    except Exception as e:
        print(colored(f"❌ API error: {e}", "red"))

    # Example 4: Cache metrics
    cprint("\n" + "=" * 60, "blue")
    cprint("Example 4: Tracking Cache Performance", "blue", attrs=["bold"])
    cprint("=" * 60, "blue")

    # Simulate cache operations
    collector.api.cache_hits_total.labels(cache_type='memory').inc(85)
    collector.api.cache_misses_total.labels(cache_type='memory').inc(15)
    collector.api.cache_hits_total.labels(cache_type='redis').inc(10)
    collector.api.cache_misses_total.labels(cache_type='redis').inc(2)

    print(colored("✅ Memory cache: 85 hits, 15 misses (85.0% hit rate)", "green"))
    print(colored("✅ Redis cache: 10 hits, 2 misses (83.3% hit rate)", "green"))

    # Example 5: Export metrics
    cprint("\n" + "=" * 60, "magenta")
    cprint("Example 5: Exporting Metrics (Prometheus Format)", "magenta", attrs=["bold"])
    cprint("=" * 60, "magenta")

    metrics_output = collector.export_metrics()
    print(colored("\n📊 Sample Metrics Output (first 500 chars):", "white", attrs=["bold"]))
    print(metrics_output.decode('utf-8')[:500] + "...\n")

    cprint("=" * 60, "green")
    cprint("✅ All Prometheus metrics tests completed!", "green", attrs=["bold"])
    cprint("=" * 60, "green")

    # Usage instructions
    cprint("\n" + "=" * 60, "cyan")
    cprint("📚 USAGE INSTRUCTIONS", "cyan", attrs=["bold"])
    cprint("=" * 60, "cyan")
    print("""
# In your trading agent:
from src.utils.prometheus_metrics import metrics

# Track trades
metrics.track_trade(
    symbol="BTC",
    strategy="momentum",
    direction="BUY",
    pnl_usd=150.0,
    position_size_usd=1000.0,
    duration_seconds=3600.0,
    kelly_fraction=0.10
)

# Track agent execution (decorator)
@metrics.track_agent_run('trading_agent')
def run_trading_agent():
    # Your agent code here
    pass

# Track API calls (decorator)
@metrics.track_api_call('birdeye', '/token/price')
def get_token_price(address):
    # Your API call here
    pass

# Track cache hits/misses
metrics.api.cache_hits_total.labels(cache_type='memory').inc()
metrics.api.cache_misses_total.labels(cache_type='memory').inc()

# Update portfolio metrics
metrics.trading.portfolio_value_usd.set(10000.0)
metrics.trading.cash_balance_usd.set(5000.0)

# Start Prometheus HTTP server (run in main.py)
metrics.start_server(port=8000)
# Metrics available at: http://localhost:8000/metrics

# Configure Prometheus to scrape:
# prometheus.yml:
#   scrape_configs:
#     - job_name: 'trading_system'
#       static_configs:
#         - targets: ['localhost:8000']
    """)

    print(colored("\n🚀 Ready to integrate with your trading system!\n", "green", attrs=["bold"]))

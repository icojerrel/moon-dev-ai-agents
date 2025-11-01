"""
🌙 Moon Dev's Orchestrator Monitor
Real-time monitoring, profiling, and health checks for agent orchestration

Features:
- Agent execution time profiling
- Success/failure rate tracking
- Health check system
- Performance metrics export
- Real-time monitoring dashboard
- Retry logic with exponential backoff
"""

import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from pathlib import Path
from termcolor import cprint, colored
import traceback
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
import threading


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class AgentMetrics:
    """Metrics for a single agent execution"""
    agent_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    success: bool = False
    error_message: Optional[str] = None
    retry_count: int = 0


@dataclass
class AgentHealth:
    """Health status for an agent"""
    agent_name: str
    status: str  # 'healthy', 'degraded', 'unhealthy', 'unknown'
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    consecutive_failures: int = 0
    success_rate: float = 0.0
    avg_execution_time: float = 0.0


# ============================================================================
# ORCHESTRATOR MONITOR CLASS
# ============================================================================

class OrchestratorMonitor:
    """
    Monitor and profile agent orchestration
    """

    def __init__(self, output_dir: str = 'src/data/orchestrator_metrics'):
        """Initialize orchestrator monitor"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Execution history
        self.execution_history: List[AgentMetrics] = []
        self.current_cycle_metrics: List[AgentMetrics] = []

        # Agent health tracking
        self.agent_health: Dict[str, AgentHealth] = {}

        # Cycle tracking
        self.cycle_count = 0
        self.cycle_start_time: Optional[datetime] = None
        self.total_cycles_completed = 0

        # Lock for thread-safe operations
        self.lock = threading.Lock()

        cprint("📊 Orchestrator Monitor initialized", "white", "on_blue")

    def start_cycle(self):
        """Mark the start of a new orchestration cycle"""
        with self.lock:
            self.cycle_count += 1
            self.cycle_start_time = datetime.now()
            self.current_cycle_metrics = []

            cprint(f"\n{'='*70}", "cyan")
            cprint(f"🔄 Orchestration Cycle #{self.cycle_count} Starting", "cyan", attrs=["bold"])
            cprint(f"⏰ Time: {self.cycle_start_time.strftime('%Y-%m-%d %H:%M:%S')}", "cyan")
            cprint(f"{'='*70}", "cyan")

    def end_cycle(self):
        """Mark the end of an orchestration cycle"""
        with self.lock:
            if self.cycle_start_time is None:
                return

            cycle_duration = (datetime.now() - self.cycle_start_time).total_seconds()
            self.total_cycles_completed += 1

            # Update health for all agents in this cycle
            self._update_agent_health()

            # Display cycle summary
            self._display_cycle_summary(cycle_duration)

            # Export metrics
            self._export_cycle_metrics()

    def start_agent(self, agent_name: str) -> AgentMetrics:
        """
        Start tracking an agent execution

        Args:
            agent_name: Name of the agent

        Returns:
            AgentMetrics object for this execution
        """
        metrics = AgentMetrics(
            agent_name=agent_name,
            start_time=datetime.now()
        )

        cprint(f"\n🚀 Starting: {agent_name}", "white", "on_cyan")

        return metrics

    def end_agent(
        self,
        metrics: AgentMetrics,
        success: bool = True,
        error: Optional[Exception] = None
    ):
        """
        End tracking an agent execution

        Args:
            metrics: AgentMetrics object from start_agent
            success: Whether execution was successful
            error: Exception if execution failed
        """
        with self.lock:
            metrics.end_time = datetime.now()
            metrics.duration_seconds = (metrics.end_time - metrics.start_time).total_seconds()
            metrics.success = success

            if error:
                metrics.error_message = str(error)

            # Add to history
            self.execution_history.append(metrics)
            self.current_cycle_metrics.append(metrics)

            # Display result
            if success:
                cprint(
                    f"✅ Completed: {metrics.agent_name} ({metrics.duration_seconds:.2f}s)",
                    "green"
                )
            else:
                cprint(
                    f"❌ Failed: {metrics.agent_name} ({metrics.duration_seconds:.2f}s)",
                    "red"
                )
                if error:
                    cprint(f"   Error: {metrics.error_message}", "red")

    def run_agent_with_retry(
        self,
        agent_name: str,
        agent_func: Callable,
        max_retries: int = 3,
        timeout_seconds: int = 300,
        backoff_multiplier: float = 2.0
    ) -> bool:
        """
        Run an agent with retry logic and timeout

        Args:
            agent_name: Name of the agent
            agent_func: Function to execute
            max_retries: Maximum retry attempts (default: 3)
            timeout_seconds: Timeout per attempt (default: 300s)
            backoff_multiplier: Exponential backoff multiplier (default: 2.0)

        Returns:
            True if successful, False otherwise
        """
        metrics = self.start_agent(agent_name)
        last_error = None

        for attempt in range(max_retries + 1):
            try:
                # Calculate timeout with backoff
                current_timeout = timeout_seconds * (backoff_multiplier ** attempt)

                if attempt > 0:
                    cprint(
                        f"🔄 Retry attempt {attempt}/{max_retries} for {agent_name}",
                        "yellow"
                    )
                    # Exponential backoff delay
                    backoff_delay = 2 ** attempt
                    time.sleep(backoff_delay)

                # Run agent with timeout
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(agent_func)
                    future.result(timeout=current_timeout)

                # Success!
                metrics.retry_count = attempt
                self.end_agent(metrics, success=True)
                return True

            except TimeoutError:
                last_error = TimeoutError(f"Agent timed out after {current_timeout}s")
                cprint(f"⏱️  Timeout for {agent_name} (attempt {attempt + 1})", "yellow")

            except Exception as e:
                last_error = e
                cprint(f"❌ Error in {agent_name} (attempt {attempt + 1}): {str(e)}", "red")

        # All retries failed
        metrics.retry_count = max_retries
        self.end_agent(metrics, success=False, error=last_error)
        return False

    def run_agents_parallel(
        self,
        agents: List[tuple],  # List of (name, func) tuples
        max_workers: int = 5,
        timeout_per_agent: int = 300
    ) -> Dict[str, bool]:
        """
        Run multiple agents in parallel

        Args:
            agents: List of (agent_name, agent_func) tuples
            max_workers: Maximum parallel workers (default: 5)
            timeout_per_agent: Timeout per agent (default: 300s)

        Returns:
            Dict of {agent_name: success}
        """
        results = {}

        cprint(f"\n⚡ Running {len(agents)} agents in parallel...", "cyan", attrs=["bold"])

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all agents
            future_to_agent = {}
            for agent_name, agent_func in agents:
                metrics = self.start_agent(agent_name)
                future = executor.submit(agent_func)
                future_to_agent[future] = (agent_name, metrics)

            # Collect results as they complete
            for future in as_completed(future_to_agent.keys(), timeout=timeout_per_agent):
                agent_name, metrics = future_to_agent[future]

                try:
                    future.result(timeout=5)  # Small timeout for result retrieval
                    self.end_agent(metrics, success=True)
                    results[agent_name] = True

                except Exception as e:
                    self.end_agent(metrics, success=False, error=e)
                    results[agent_name] = False

        return results

    def get_agent_health(self, agent_name: str) -> Optional[AgentHealth]:
        """Get health status for an agent"""
        return self.agent_health.get(agent_name)

    def get_all_agent_health(self) -> Dict[str, AgentHealth]:
        """Get health status for all agents"""
        return self.agent_health.copy()

    def display_dashboard(self):
        """Display real-time monitoring dashboard"""
        cprint("\n" + "=" * 70, "cyan")
        cprint("📊 ORCHESTRATOR DASHBOARD", "cyan", attrs=["bold"])
        cprint("=" * 70, "cyan")

        # Cycle Info
        cprint("\n🔄 CYCLE INFORMATION", "white", attrs=["bold"])
        cprint(f"  Current Cycle: #{self.cycle_count}", "white")
        cprint(f"  Total Cycles Completed: {self.total_cycles_completed}", "white")

        if self.cycle_start_time:
            uptime = (datetime.now() - self.cycle_start_time).total_seconds()
            cprint(f"  Current Cycle Uptime: {uptime:.0f}s", "white")

        # Agent Health
        if self.agent_health:
            cprint("\n🏥 AGENT HEALTH STATUS", "white", attrs=["bold"])
            cprint("-" * 70, "cyan")

            for agent_name, health in self.agent_health.items():
                # Color code by health status
                if health.status == 'healthy':
                    status_color = "green"
                    symbol = "✅"
                elif health.status == 'degraded':
                    status_color = "yellow"
                    symbol = "⚠️"
                elif health.status == 'unhealthy':
                    status_color = "red"
                    symbol = "❌"
                else:
                    status_color = "white"
                    symbol = "❓"

                print(f"\n  {symbol} {agent_name}")
                print(colored(f"    Status: {health.status.upper()}", status_color))
                print(f"    Success Rate: {health.success_rate*100:.1f}%")
                print(f"    Avg Execution Time: {health.avg_execution_time:.2f}s")
                print(f"    Consecutive Failures: {health.consecutive_failures}")

                if health.last_success:
                    print(f"    Last Success: {health.last_success.strftime('%H:%M:%S')}")
                if health.last_failure:
                    print(f"    Last Failure: {health.last_failure.strftime('%H:%M:%S')}")

        # Recent Executions
        if self.current_cycle_metrics:
            cprint("\n📈 CURRENT CYCLE EXECUTIONS", "white", attrs=["bold"])
            cprint("-" * 70, "cyan")

            for metrics in self.current_cycle_metrics:
                status_symbol = "✅" if metrics.success else "❌"
                print(f"  {status_symbol} {metrics.agent_name}: {metrics.duration_seconds:.2f}s")
                if metrics.retry_count > 0:
                    print(f"     (Retried {metrics.retry_count} times)")

    def _update_agent_health(self):
        """Update health status for all agents based on execution history"""
        # Get recent history (last 10 executions per agent)
        agent_history: Dict[str, List[AgentMetrics]] = {}

        for metrics in reversed(self.execution_history[-100:]):  # Last 100 executions
            if metrics.agent_name not in agent_history:
                agent_history[metrics.agent_name] = []

            if len(agent_history[metrics.agent_name]) < 10:
                agent_history[metrics.agent_name].append(metrics)

        # Calculate health for each agent
        for agent_name, history in agent_history.items():
            if not history:
                continue

            # Calculate metrics
            successes = sum(1 for m in history if m.success)
            failures = len(history) - successes
            success_rate = successes / len(history)

            # Calculate consecutive failures
            consecutive_failures = 0
            for metrics in reversed(self.execution_history):
                if metrics.agent_name != agent_name:
                    continue
                if not metrics.success:
                    consecutive_failures += 1
                else:
                    break

            # Calculate average execution time
            successful_executions = [m for m in history if m.success]
            avg_time = (
                sum(m.duration_seconds for m in successful_executions) / len(successful_executions)
                if successful_executions else 0.0
            )

            # Determine health status
            if consecutive_failures >= 3:
                status = 'unhealthy'
            elif consecutive_failures > 0 or success_rate < 0.8:
                status = 'degraded'
            else:
                status = 'healthy'

            # Find last success/failure
            last_success = None
            last_failure = None
            for metrics in reversed(self.execution_history):
                if metrics.agent_name != agent_name:
                    continue
                if metrics.success and last_success is None:
                    last_success = metrics.end_time
                if not metrics.success and last_failure is None:
                    last_failure = metrics.end_time
                if last_success and last_failure:
                    break

            # Update health
            self.agent_health[agent_name] = AgentHealth(
                agent_name=agent_name,
                status=status,
                last_success=last_success,
                last_failure=last_failure,
                consecutive_failures=consecutive_failures,
                success_rate=success_rate,
                avg_execution_time=avg_time
            )

    def _display_cycle_summary(self, cycle_duration: float):
        """Display summary of completed cycle"""
        cprint("\n" + "=" * 70, "cyan")
        cprint(f"✅ Cycle #{self.cycle_count} Completed", "green", attrs=["bold"])
        cprint("=" * 70, "cyan")

        # Count successes/failures
        successes = sum(1 for m in self.current_cycle_metrics if m.success)
        failures = len(self.current_cycle_metrics) - successes

        print(f"\n  Total Duration: {cycle_duration:.2f}s")
        print(f"  Agents Run: {len(self.current_cycle_metrics)}")
        print(colored(f"  Successes: {successes}", "green"))
        if failures > 0:
            print(colored(f"  Failures: {failures}", "red"))

        # Show slowest agents
        if self.current_cycle_metrics:
            slowest = sorted(
                self.current_cycle_metrics,
                key=lambda m: m.duration_seconds,
                reverse=True
            )[:3]

            print("\n  Slowest Agents:")
            for metrics in slowest:
                print(f"    • {metrics.agent_name}: {metrics.duration_seconds:.2f}s")

    def _export_cycle_metrics(self):
        """Export cycle metrics to file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cycle_{self.cycle_count}_{timestamp}.json"
            filepath = self.output_dir / filename

            data = {
                "cycle_number": self.cycle_count,
                "timestamp": datetime.now().isoformat(),
                "metrics": [
                    {
                        "agent_name": m.agent_name,
                        "duration_seconds": m.duration_seconds,
                        "success": m.success,
                        "retry_count": m.retry_count,
                        "error_message": m.error_message
                    }
                    for m in self.current_cycle_metrics
                ],
                "agent_health": {
                    name: {
                        "status": health.status,
                        "success_rate": health.success_rate,
                        "avg_execution_time": health.avg_execution_time,
                        "consecutive_failures": health.consecutive_failures
                    }
                    for name, health in self.agent_health.items()
                }
            }

            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            cprint(f"⚠️  Could not export metrics: {str(e)}", "yellow")


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def create_agent_wrapper(agent_instance, method_name: str = 'run'):
    """
    Create a wrapper function for an agent

    Args:
        agent_instance: Agent instance
        method_name: Method to call (default: 'run')

    Returns:
        Callable function
    """
    def wrapper():
        method = getattr(agent_instance, method_name)
        return method()

    return wrapper


# ============================================================================
# MAIN (EXAMPLE)
# ============================================================================

if __name__ == "__main__":
    """
    Example usage of orchestrator monitor
    """
    print("\n🌙 Moon Dev's Orchestrator Monitor - Example\n")

    # Create monitor
    monitor = OrchestratorMonitor()

    # Start cycle
    monitor.start_cycle()

    # Example: Run agents with retry
    def example_agent():
        time.sleep(1)
        return True

    monitor.run_agent_with_retry("ExampleAgent", example_agent)

    # Display dashboard
    monitor.display_dashboard()

    # End cycle
    monitor.end_cycle()

    cprint("\n✅ Orchestrator monitor example complete!", "white", "on_green")

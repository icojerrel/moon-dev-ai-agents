"""
🌙 Moon Dev's Cost Tracker
Track and monitor API costs across all agents
Built with love by Moon Dev 🚀
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from termcolor import cprint

class CostTracker:
    """Track and log API costs per agent and model"""

    def __init__(self, log_dir: str = "src/data/cost_tracking"):
        """Initialize cost tracker

        Args:
            log_dir: Directory to store cost logs
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "cost_log.json"

    def log_request(self, agent: str, model: str, tokens_used: dict, cost: float,
                   task_type: str = "general", metadata: Optional[dict] = None):
        """Log a single API request

        Args:
            agent: Name of the agent making the request
            model: Model ID used
            tokens_used: Dictionary with prompt_tokens, completion_tokens, total_tokens
            cost: Calculated cost in USD
            task_type: Type of task performed
            metadata: Additional metadata (optional)
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "model": model,
            "tokens": tokens_used,
            "cost": cost,
            "task_type": task_type,
            "metadata": metadata or {}
        }

        # Append to log
        logs = self._load_logs()
        logs.append(entry)
        self._save_logs(logs)

        cprint(f"💰 Logged: {agent} - ${cost:.6f} ({tokens_used.get('total_tokens', 0)} tokens)", "cyan")

    def get_daily_cost(self, date: Optional[datetime] = None) -> float:
        """Get total cost for a specific day

        Args:
            date: Date to check (defaults to today)

        Returns:
            Total cost in USD
        """
        if date is None:
            date = datetime.now()

        logs = self._load_logs()
        target_date = date.date()

        daily_cost = sum(
            log['cost'] for log in logs
            if datetime.fromisoformat(log['timestamp']).date() == target_date
        )

        return daily_cost

    def get_weekly_cost(self) -> float:
        """Get total cost for the past 7 days

        Returns:
            Total cost in USD
        """
        logs = self._load_logs()
        week_ago = datetime.now() - timedelta(days=7)

        weekly_cost = sum(
            log['cost'] for log in logs
            if datetime.fromisoformat(log['timestamp']) >= week_ago
        )

        return weekly_cost

    def get_monthly_cost(self) -> float:
        """Get total cost for the past 30 days

        Returns:
            Total cost in USD
        """
        logs = self._load_logs()
        month_ago = datetime.now() - timedelta(days=30)

        monthly_cost = sum(
            log['cost'] for log in logs
            if datetime.fromisoformat(log['timestamp']) >= month_ago
        )

        return monthly_cost

    def get_agent_costs(self, days: int = 30) -> Dict[str, float]:
        """Get costs per agent for the specified time period

        Args:
            days: Number of days to look back

        Returns:
            Dictionary mapping agent name to total cost
        """
        logs = self._load_logs()
        cutoff_date = datetime.now() - timedelta(days=days)

        agent_costs = {}
        for log in logs:
            if datetime.fromisoformat(log['timestamp']) >= cutoff_date:
                agent = log['agent']
                agent_costs[agent] = agent_costs.get(agent, 0) + log['cost']

        return agent_costs

    def get_model_costs(self, days: int = 30) -> Dict[str, float]:
        """Get costs per model for the specified time period

        Args:
            days: Number of days to look back

        Returns:
            Dictionary mapping model to total cost
        """
        logs = self._load_logs()
        cutoff_date = datetime.now() - timedelta(days=days)

        model_costs = {}
        for log in logs:
            if datetime.fromisoformat(log['timestamp']) >= cutoff_date:
                model = log['model']
                model_costs[model] = model_costs.get(model, 0) + log['cost']

        return model_costs

    def get_token_usage(self, days: int = 30) -> Dict[str, int]:
        """Get total token usage for the specified time period

        Args:
            days: Number of days to look back

        Returns:
            Dictionary with prompt_tokens, completion_tokens, total_tokens
        """
        logs = self._load_logs()
        cutoff_date = datetime.now() - timedelta(days=days)

        total_tokens = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }

        for log in logs:
            if datetime.fromisoformat(log['timestamp']) >= cutoff_date:
                tokens = log.get('tokens', {})
                total_tokens['prompt_tokens'] += tokens.get('prompt_tokens', 0)
                total_tokens['completion_tokens'] += tokens.get('completion_tokens', 0)
                total_tokens['total_tokens'] += tokens.get('total_tokens', 0)

        return total_tokens

    def print_summary(self, days: int = 7):
        """Print a formatted cost summary

        Args:
            days: Number of days to summarize
        """
        cprint(f"\n{'='*60}", "cyan")
        cprint(f"💰 COST SUMMARY - Last {days} Days", "cyan", attrs=['bold'])
        cprint(f"{'='*60}", "cyan")

        # Overall costs
        if days == 1:
            total_cost = self.get_daily_cost()
            period = "Today"
        elif days == 7:
            total_cost = self.get_weekly_cost()
            period = "This Week"
        elif days == 30:
            total_cost = self.get_monthly_cost()
            period = "This Month"
        else:
            # Custom period
            total_cost = sum(
                log['cost'] for log in self._load_logs()
                if datetime.fromisoformat(log['timestamp']) >= datetime.now() - timedelta(days=days)
            )
            period = f"Last {days} Days"

        cprint(f"\n📊 {period} Total: ${total_cost:.2f}", "yellow", attrs=['bold'])

        # Per-agent costs
        agent_costs = self.get_agent_costs(days)
        if agent_costs:
            cprint(f"\n🤖 Costs by Agent:", "cyan")
            for agent, cost in sorted(agent_costs.items(), key=lambda x: x[1], reverse=True):
                percentage = (cost / total_cost * 100) if total_cost > 0 else 0
                cprint(f"  ├─ {agent}: ${cost:.4f} ({percentage:.1f}%)", "green")

        # Per-model costs
        model_costs = self.get_model_costs(days)
        if model_costs:
            cprint(f"\n🎯 Costs by Model:", "cyan")
            for model, cost in sorted(model_costs.items(), key=lambda x: x[1], reverse=True):
                percentage = (cost / total_cost * 100) if total_cost > 0 else 0
                cprint(f"  ├─ {model}: ${cost:.4f} ({percentage:.1f}%)", "green")

        # Token usage
        tokens = self.get_token_usage(days)
        cprint(f"\n📈 Token Usage:", "cyan")
        cprint(f"  ├─ Input: {tokens['prompt_tokens']:,} tokens", "green")
        cprint(f"  ├─ Output: {tokens['completion_tokens']:,} tokens", "green")
        cprint(f"  └─ Total: {tokens['total_tokens']:,} tokens", "green")

        # Daily average
        daily_avg = total_cost / days if days > 0 else 0
        monthly_projection = daily_avg * 30
        cprint(f"\n📅 Projections:", "cyan")
        cprint(f"  ├─ Daily Average: ${daily_avg:.2f}", "yellow")
        cprint(f"  └─ Monthly Projection: ${monthly_projection:.2f}", "yellow")

        cprint(f"\n{'='*60}\n", "cyan")

    def check_budget_limit(self, daily_limit: float = 10.0, monthly_limit: float = 300.0) -> Dict[str, bool]:
        """Check if costs are within budget limits

        Args:
            daily_limit: Maximum daily cost in USD
            monthly_limit: Maximum monthly cost in USD

        Returns:
            Dictionary with limit check results
        """
        daily_cost = self.get_daily_cost()
        monthly_cost = self.get_monthly_cost()

        results = {
            "daily_ok": daily_cost <= daily_limit,
            "monthly_ok": monthly_cost <= monthly_limit,
            "daily_cost": daily_cost,
            "monthly_cost": monthly_cost,
            "daily_limit": daily_limit,
            "monthly_limit": monthly_limit
        }

        # Print warnings if limits exceeded
        if not results["daily_ok"]:
            cprint(f"\n⚠️ DAILY BUDGET EXCEEDED!", "red", attrs=['bold'])
            cprint(f"   Current: ${daily_cost:.2f} / Limit: ${daily_limit:.2f}", "red")

        if not results["monthly_ok"]:
            cprint(f"\n⚠️ MONTHLY BUDGET EXCEEDED!", "red", attrs=['bold'])
            cprint(f"   Current: ${monthly_cost:.2f} / Limit: ${monthly_limit:.2f}", "red")

        return results

    def export_to_csv(self, output_file: str = "cost_report.csv"):
        """Export cost log to CSV format

        Args:
            output_file: Output CSV file path
        """
        import csv

        logs = self._load_logs()
        output_path = self.log_dir / output_file

        with open(output_path, 'w', newline='') as f:
            if logs:
                fieldnames = ['timestamp', 'agent', 'model', 'task_type', 'cost',
                            'prompt_tokens', 'completion_tokens', 'total_tokens']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for log in logs:
                    tokens = log.get('tokens', {})
                    writer.writerow({
                        'timestamp': log['timestamp'],
                        'agent': log['agent'],
                        'model': log['model'],
                        'task_type': log.get('task_type', 'general'),
                        'cost': log['cost'],
                        'prompt_tokens': tokens.get('prompt_tokens', 0),
                        'completion_tokens': tokens.get('completion_tokens', 0),
                        'total_tokens': tokens.get('total_tokens', 0)
                    })

        cprint(f"✅ Cost report exported to: {output_path}", "green")

    def _load_logs(self) -> List[dict]:
        """Load logs from file

        Returns:
            List of log entries
        """
        if self.log_file.exists():
            try:
                return json.loads(self.log_file.read_text())
            except json.JSONDecodeError:
                cprint("⚠️ Error reading cost log, starting fresh", "yellow")
                return []
        return []

    def _save_logs(self, logs: List[dict]):
        """Save logs to file

        Args:
            logs: List of log entries to save
        """
        self.log_file.write_text(json.dumps(logs, indent=2))

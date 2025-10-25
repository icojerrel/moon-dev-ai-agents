"""
🌙 Moon Dev's Cost Optimizer
Automatically select the cheapest model for each task type
Built with love by Moon Dev 🚀
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass
from termcolor import cprint

@dataclass
class ModelPricing:
    """Model pricing information"""
    model: str
    input_cost: float  # Per 1M tokens
    output_cost: float  # Per 1M tokens
    speed: str  # "fast", "medium", "slow"
    quality: str  # "high", "medium", "low"
    context_window: int  # Context window size

class CostOptimizer:
    """Select optimal model based on task requirements and budget"""

    # OpenRouter pricing (as of January 2025)
    OPENROUTER_PRICING = {
        # Ultra cheap options (BEST VALUE)
        "deepseek/deepseek-chat": ModelPricing(
            model="deepseek/deepseek-chat",
            input_cost=0.14, output_cost=0.28,
            speed="fast", quality="high",
            context_window=64000
        ),
        "anthropic/claude-3-haiku": ModelPricing(
            model="anthropic/claude-3-haiku",
            input_cost=0.25, output_cost=1.25,
            speed="fast", quality="high",
            context_window=200000
        ),
        "openai/gpt-3.5-turbo": ModelPricing(
            model="openai/gpt-3.5-turbo",
            input_cost=0.50, output_cost=1.50,
            speed="fast", quality="medium",
            context_window=16000
        ),
        "mistralai/mixtral-8x7b-instruct": ModelPricing(
            model="mistralai/mixtral-8x7b-instruct",
            input_cost=0.24, output_cost=0.24,
            speed="fast", quality="high",
            context_window=32000
        ),

        # Reasoning models
        "deepseek/deepseek-r1": ModelPricing(
            model="deepseek/deepseek-r1",
            input_cost=0.55, output_cost=2.19,
            speed="medium", quality="high",
            context_window=64000
        ),

        # Balanced options
        "anthropic/claude-3.5-sonnet": ModelPricing(
            model="anthropic/claude-3.5-sonnet",
            input_cost=3.00, output_cost=15.00,
            speed="medium", quality="high",
            context_window=200000
        ),
        "openai/gpt-4o": ModelPricing(
            model="openai/gpt-4o",
            input_cost=2.50, output_cost=10.00,
            speed="medium", quality="high",
            context_window=128000
        ),

        # Premium options (use sparingly!)
        "anthropic/claude-3-opus": ModelPricing(
            model="anthropic/claude-3-opus",
            input_cost=15.00, output_cost=75.00,
            speed="slow", quality="high",
            context_window=200000
        ),
        "openai/gpt-4-turbo": ModelPricing(
            model="openai/gpt-4-turbo",
            input_cost=10.00, output_cost=30.00,
            speed="slow", quality="high",
            context_window=128000
        ),
    }

    @staticmethod
    def get_optimal_model(task_type: str = "general", budget: str = "cheap") -> str:
        """Get optimal model for task type and budget

        Args:
            task_type: Type of task ("general", "research", "complex_reasoning",
                      "code_generation", "strategy_backtest", "simple_chat")
            budget: Budget level ("ultra_cheap", "cheap", "balanced", "premium")

        Returns:
            Model ID for OpenRouter
        """

        # Task-specific recommendations by budget level
        recommendations = {
            # Simple tasks - use cheapest models
            "simple_chat": {
                "ultra_cheap": "deepseek/deepseek-chat",  # $0.14/1M
                "cheap": "deepseek/deepseek-chat",  # $0.14/1M
                "balanced": "anthropic/claude-3-haiku",  # $0.25/1M
                "premium": "openai/gpt-4o",  # $2.50/1M
            },

            # Research - need good quality but can be cheap
            "research": {
                "ultra_cheap": "deepseek/deepseek-chat",  # $0.14/1M
                "cheap": "anthropic/claude-3-haiku",  # $0.25/1M
                "balanced": "anthropic/claude-3.5-sonnet",  # $3.00/1M
                "premium": "anthropic/claude-3-opus",  # $15.00/1M
            },

            # Complex reasoning - need reasoning capabilities
            "complex_reasoning": {
                "ultra_cheap": "deepseek/deepseek-r1",  # $0.55/1M (shows thinking!)
                "cheap": "deepseek/deepseek-r1",  # $0.55/1M
                "balanced": "anthropic/claude-3.5-sonnet",  # $3.00/1M
                "premium": "anthropic/claude-3-opus",  # $15.00/1M
            },

            # Code generation - cheap is fine
            "code_generation": {
                "ultra_cheap": "deepseek/deepseek-chat",  # $0.14/1M (great at code!)
                "cheap": "deepseek/deepseek-chat",  # $0.14/1M
                "balanced": "openai/gpt-4o",  # $2.50/1M
                "premium": "anthropic/claude-3.5-sonnet",  # $3.00/1M
            },

            # Strategy backtesting - needs reasoning
            "strategy_backtest": {
                "ultra_cheap": "deepseek/deepseek-r1",  # $0.55/1M (shows reasoning process!)
                "cheap": "deepseek/deepseek-r1",  # $0.55/1M
                "balanced": "anthropic/claude-3.5-sonnet",  # $3.00/1M
                "premium": "anthropic/claude-3-opus",  # $15.00/1M
            },

            # General purpose
            "general": {
                "ultra_cheap": "deepseek/deepseek-chat",  # $0.14/1M
                "cheap": "anthropic/claude-3-haiku",  # $0.25/1M
                "balanced": "anthropic/claude-3.5-sonnet",  # $3.00/1M
                "premium": "openai/gpt-4o",  # $2.50/1M
            },

            # Trading analysis - needs good reasoning
            "trading_analysis": {
                "ultra_cheap": "deepseek/deepseek-chat",  # $0.14/1M
                "cheap": "anthropic/claude-3-haiku",  # $0.25/1M
                "balanced": "anthropic/claude-3.5-sonnet",  # $3.00/1M
                "premium": "anthropic/claude-3-opus",  # $15.00/1M
            },
        }

        # Get recommendation
        task_recommendations = recommendations.get(task_type, recommendations["general"])
        model = task_recommendations.get(budget, task_recommendations["cheap"])

        cprint(f"\n💡 Optimal model for '{task_type}' (budget: {budget}): {model}", "cyan")

        return model

    @staticmethod
    def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for a request

        Args:
            model: Model ID
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Estimated cost in USD
        """
        pricing = CostOptimizer.OPENROUTER_PRICING.get(model)
        if not pricing:
            cprint(f"⚠️ No pricing info for {model}, assuming $0", "yellow")
            return 0.0

        # Calculate costs (pricing is per 1M tokens)
        input_cost = (input_tokens / 1_000_000) * pricing.input_cost
        output_cost = (output_tokens / 1_000_000) * pricing.output_cost
        total_cost = input_cost + output_cost

        return total_cost

    @staticmethod
    def compare_costs(models: List[str], input_tokens: int, output_tokens: int) -> List[Tuple[str, float]]:
        """Compare costs across multiple models

        Args:
            models: List of model IDs to compare
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            List of (model, cost) tuples sorted by cost (cheapest first)
        """
        costs = []
        for model in models:
            cost = CostOptimizer.estimate_cost(model, input_tokens, output_tokens)
            costs.append((model, cost))

        # Sort by cost
        costs.sort(key=lambda x: x[1])

        cprint("\n💰 Cost Comparison:", "cyan")
        for model, cost in costs:
            cprint(f"  ├─ {model}: ${cost:.6f}", "green" if cost == costs[0][1] else "yellow")

        return costs

    @staticmethod
    def get_cheapest_models(limit: int = 5) -> List[Tuple[str, str]]:
        """Get the cheapest models available

        Args:
            limit: Number of models to return

        Returns:
            List of (model, price_description) tuples
        """
        # Calculate average cost per model (assuming 50/50 input/output split)
        model_costs = []
        for model_id, pricing in CostOptimizer.OPENROUTER_PRICING.items():
            avg_cost = (pricing.input_cost + pricing.output_cost) / 2
            price_str = f"${pricing.input_cost:.2f} in / ${pricing.output_cost:.2f} out per 1M"
            model_costs.append((model_id, price_str, avg_cost))

        # Sort by average cost
        model_costs.sort(key=lambda x: x[2])

        cprint("\n💰 Cheapest Models Available:", "cyan")
        for i, (model, price, _) in enumerate(model_costs[:limit]):
            cprint(f"  {i+1}. {model}", "green")
            cprint(f"     {price}", "cyan")

        return [(model, price) for model, price, _ in model_costs[:limit]]

    @staticmethod
    def calculate_monthly_cost(daily_requests: int, avg_input_tokens: int,
                               avg_output_tokens: int, model: str) -> float:
        """Calculate estimated monthly cost

        Args:
            daily_requests: Number of requests per day
            avg_input_tokens: Average input tokens per request
            avg_output_tokens: Average output tokens per request
            model: Model ID

        Returns:
            Estimated monthly cost in USD
        """
        daily_cost = daily_requests * CostOptimizer.estimate_cost(
            model, avg_input_tokens, avg_output_tokens
        )
        monthly_cost = daily_cost * 30

        cprint(f"\n📊 Cost Projection for {model}:", "cyan")
        cprint(f"  ├─ Daily cost: ${daily_cost:.2f}", "yellow")
        cprint(f"  └─ Monthly cost: ${monthly_cost:.2f}", "yellow")

        return monthly_cost

    @staticmethod
    def get_best_value_models() -> Dict[str, str]:
        """Get recommended models for best value

        Returns:
            Dictionary of use_case: model_id
        """
        return {
            "best_overall": "deepseek/deepseek-chat",  # Unbeatable value
            "best_reasoning": "deepseek/deepseek-r1",  # Shows thinking, cheap
            "best_quality_cheap": "anthropic/claude-3-haiku",  # Great quality, still cheap
            "best_balanced": "anthropic/claude-3.5-sonnet",  # High quality, reasonable price
            "best_premium": "anthropic/claude-3-opus",  # Top quality, expensive
        }

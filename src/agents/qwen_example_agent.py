#!/usr/bin/env python3
"""
🌙 Moon Dev's Qwen3-Coder Example Agent
Built with love by Moon Dev 🚀

This agent demonstrates how to use the local qwen3-coder:30b model
for trading strategy analysis and code generation.

Usage:
    python src/agents/qwen_example_agent.py
"""

import sys
from pathlib import Path
from termcolor import cprint
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.models.model_factory import ModelFactory


class QwenExampleAgent:
    """Example agent using qwen3-coder:30b for trading tasks"""

    def __init__(self):
        """Initialize the agent with qwen3-coder model"""
        cprint("\n" + "="*60, "cyan")
        cprint("🤖 Qwen3-Coder Example Agent", "cyan", attrs=["bold"])
        cprint("="*60 + "\n", "cyan")

        # Initialize model factory
        cprint("📦 Initializing ModelFactory...", "yellow")
        self.factory = ModelFactory()

        # Get Ollama model (should be qwen3-coder:30b by default)
        if not self.factory.is_model_available("ollama"):
            cprint("❌ Ollama not available. Make sure:", "red")
            cprint("   1. Ollama is installed", "yellow")
            cprint("   2. Server is running: ollama serve", "yellow")
            cprint("   3. Model is pulled: ollama pull qwen3-coder:30b", "yellow")
            sys.exit(1)

        self.model = self.factory.get_model("ollama")
        cprint(f"✅ Model loaded: {self.model.model_name}\n", "green")

    def analyze_strategy(self, strategy_description: str) -> str:
        """Analyze a trading strategy using qwen3-coder"""
        cprint("🔍 Analyzing trading strategy...\n", "cyan")

        system_prompt = """You are an expert quantitative trading strategist with deep knowledge of:
- Technical analysis and indicators (RSI, MACD, Bollinger Bands, etc.)
- Market structure and price action
- Risk management and position sizing
- Backtesting and strategy validation

Provide clear, actionable analysis with specific recommendations."""

        user_content = f"""Analyze this trading strategy:

{strategy_description}

Provide:
1. Strengths of the strategy
2. Potential weaknesses and risks
3. Specific improvement suggestions
4. Recommended indicators to combine with it
5. Risk management considerations"""

        response = self.model.generate_response(
            system_prompt=system_prompt,
            user_content=user_content,
            temperature=0.4,  # Lower for more focused analysis
            max_tokens=1500
        )

        return response.content

    def generate_indicator_code(self, indicator_name: str, description: str = "") -> str:
        """Generate Python code for a trading indicator"""
        cprint(f"💻 Generating code for {indicator_name}...\n", "cyan")

        system_prompt = """You are an expert Python developer specializing in trading algorithms.
Generate clean, efficient, well-documented code using pandas and numpy.
Include type hints and docstrings."""

        user_content = f"""Write a Python function to calculate the {indicator_name} indicator.

{description}

Requirements:
- Use pandas Series/DataFrame for input
- Include proper error handling
- Add clear docstring with parameters and return value
- Use numpy for calculations where appropriate
- Make it compatible with backtesting.py library

Return ONLY the Python code, no explanations."""

        response = self.model.generate_response(
            system_prompt=system_prompt,
            user_content=user_content,
            temperature=0.2,  # Very low for precise code generation
            max_tokens=1000
        )

        return response.content

    def suggest_strategy_improvements(self, current_strategy: str,
                                     backtest_results: dict = None) -> str:
        """Suggest improvements for an existing strategy"""
        cprint("💡 Generating strategy improvements...\n", "cyan")

        system_prompt = """You are a quantitative trading expert specialized in strategy optimization.
Focus on practical, implementable improvements that can increase win rate and reduce drawdown."""

        user_content = f"""Current strategy:
{current_strategy}
"""

        if backtest_results:
            user_content += f"""
Backtest results:
- Win Rate: {backtest_results.get('win_rate', 'N/A')}%
- Max Drawdown: {backtest_results.get('max_drawdown', 'N/A')}%
- Sharpe Ratio: {backtest_results.get('sharpe_ratio', 'N/A')}
- Total Return: {backtest_results.get('total_return', 'N/A')}%
"""

        user_content += """
Suggest 5 specific, actionable improvements to:
1. Increase win rate
2. Reduce drawdown
3. Improve risk-adjusted returns
4. Add better entry/exit conditions
5. Implement stronger risk management

Be specific with parameter ranges and conditions."""

        response = self.model.generate_response(
            system_prompt=system_prompt,
            user_content=user_content,
            temperature=0.5,
            max_tokens=1500
        )

        return response.content

    def explain_market_pattern(self, pattern_description: str) -> str:
        """Explain a market pattern and how to trade it"""
        cprint("📊 Analyzing market pattern...\n", "cyan")

        system_prompt = """You are a professional trader and educator specialized in chart patterns
and market structure. Explain concepts clearly and provide actionable trading plans."""

        user_content = f"""Explain this market pattern/setup:

{pattern_description}

Provide:
1. What this pattern means
2. Psychology behind the pattern
3. How to identify it reliably
4. Entry conditions and timing
5. Stop loss placement
6. Profit targets
7. Common mistakes to avoid"""

        response = self.model.generate_response(
            system_prompt=system_prompt,
            user_content=user_content,
            temperature=0.5,
            max_tokens=1200
        )

        return response.content


def run_examples():
    """Run example demonstrations"""

    # Initialize agent
    agent = QwenExampleAgent()

    # Example 1: Analyze a simple RSI strategy
    cprint("="*60, "cyan")
    cprint("Example 1: Strategy Analysis", "cyan", attrs=["bold"])
    cprint("="*60 + "\n", "cyan")

    strategy = """
    RSI Mean Reversion Strategy:
    - Timeframe: 1 hour
    - Entry: Buy when RSI(14) crosses below 30
    - Exit: Sell when RSI(14) crosses above 70
    - Stop Loss: 2% below entry
    - Position Size: 100% of available capital
    """

    analysis = agent.analyze_strategy(strategy)
    cprint("📋 Analysis:", "green")
    print(analysis)
    print()

    # Example 2: Generate indicator code
    cprint("\n" + "="*60, "cyan")
    cprint("Example 2: Code Generation", "cyan", attrs=["bold"])
    cprint("="*60 + "\n", "cyan")

    code = agent.generate_indicator_code(
        "Bollinger Bands",
        "Calculate upper band, middle band (SMA), and lower band using standard deviation"
    )
    cprint("💻 Generated Code:", "green")
    print(code)
    print()

    # Example 3: Strategy improvements
    cprint("\n" + "="*60, "cyan")
    cprint("Example 3: Strategy Improvements", "cyan", attrs=["bold"])
    cprint("="*60 + "\n", "cyan")

    backtest_results = {
        'win_rate': 45.2,
        'max_drawdown': 18.5,
        'sharpe_ratio': 0.8,
        'total_return': 12.3
    }

    improvements = agent.suggest_strategy_improvements(strategy, backtest_results)
    cprint("💡 Improvement Suggestions:", "green")
    print(improvements)
    print()

    # Example 4: Pattern explanation
    cprint("\n" + "="*60, "cyan")
    cprint("Example 4: Market Pattern Analysis", "cyan", attrs=["bold"])
    cprint("="*60 + "\n", "cyan")

    pattern = "Bull flag pattern after a strong uptrend on the 15-minute chart"

    explanation = agent.explain_market_pattern(pattern)
    cprint("📊 Pattern Explanation:", "green")
    print(explanation)
    print()

    # Done
    cprint("\n" + "="*60, "green")
    cprint("✅ All Examples Completed Successfully!", "green", attrs=["bold"])
    cprint("="*60 + "\n", "green")

    cprint("🚀 qwen3-coder:30b is perfect for:", "cyan")
    cprint("  • Trading strategy analysis", "white")
    cprint("  • Code generation for indicators", "white")
    cprint("  • Strategy optimization suggestions", "white")
    cprint("  • Market pattern explanation", "white")
    cprint("  • Backtesting code creation", "white")
    cprint("\nAll running 100% local, free, and private! 🔒\n", "green")


if __name__ == "__main__":
    try:
        run_examples()
    except KeyboardInterrupt:
        cprint("\n\n⏸️  Agent stopped by user", "yellow")
        sys.exit(0)
    except Exception as e:
        cprint(f"\n❌ Error: {e}", "red")
        import traceback
        traceback.print_exc()
        sys.exit(1)

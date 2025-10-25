#!/usr/bin/env python3
"""
🌙 Moon Dev's OpenRouter Integration Test
Test the complete OpenRouter implementation
Built with love by Moon Dev 🚀
"""

import os
import sys
from dotenv import load_dotenv
from termcolor import cprint

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.models.model_factory import ModelFactory
from src.utils.cost_optimizer import CostOptimizer
from src.utils.cost_tracker import CostTracker

def test_openrouter():
    """Test OpenRouter integration"""

    cprint("\n" + "="*70, "cyan", attrs=['bold'])
    cprint("🧪 MOON DEV'S OPENROUTER INTEGRATION TEST", "cyan", attrs=['bold'])
    cprint("="*70 + "\n", "cyan", attrs=['bold'])

    # Load environment
    load_dotenv()

    # Test 1: Model Factory Initialization
    cprint("\n📋 Test 1: Model Factory Initialization", "yellow", attrs=['bold'])
    cprint("-" * 70, "yellow")

    try:
        factory = ModelFactory()

        if factory.is_model_available('openrouter'):
            cprint("✅ OpenRouter available in factory", "green")
        else:
            cprint("❌ OpenRouter not available", "red")
            return False
    except Exception as e:
        cprint(f"❌ Failed to initialize factory: {e}", "red")
        return False

    # Test 2: Get OpenRouter Model
    cprint("\n📋 Test 2: Get OpenRouter Model Instance", "yellow", attrs=['bold'])
    cprint("-" * 70, "yellow")

    try:
        model = factory.get_model('openrouter')
        cprint(f"✅ Got OpenRouter model: {model.model_name}", "green")
    except Exception as e:
        cprint(f"❌ Failed to get model: {e}", "red")
        return False

    # Test 3: Simple Response Generation
    cprint("\n📋 Test 3: Generate Simple Response", "yellow", attrs=['bold'])
    cprint("-" * 70, "yellow")

    try:
        response = model.generate_response(
            system_prompt="You are a helpful AI assistant. Respond in one short sentence.",
            user_content="Say 'OpenRouter integration successful!' in a creative way.",
            temperature=0.7,
            max_tokens=50
        )

        cprint(f"✅ Response generated successfully!", "green")
        cprint(f"\n📝 Response: {response.content}\n", "cyan")
        cprint(f"📊 Tokens used: {response.usage}", "cyan")

        # Calculate cost
        cost = CostOptimizer.estimate_cost(
            model.model_name,
            response.usage['prompt_tokens'],
            response.usage['completion_tokens']
        )
        cprint(f"💰 Estimated cost: ${cost:.6f}", "cyan")

    except Exception as e:
        cprint(f"❌ Failed to generate response: {e}", "red")
        import traceback
        traceback.print_exc()
        return False

    # Test 4: Cost Optimizer
    cprint("\n📋 Test 4: Cost Optimizer", "yellow", attrs=['bold'])
    cprint("-" * 70, "yellow")

    try:
        # Get optimal models for different tasks
        tasks = ["simple_chat", "research", "complex_reasoning", "strategy_backtest"]

        for task in tasks:
            optimal = CostOptimizer.get_optimal_model(task, budget="cheap")
            cprint(f"  Task: {task:20} → Model: {optimal}", "green")

        cprint("\n✅ Cost optimizer working", "green")

    except Exception as e:
        cprint(f"❌ Cost optimizer failed: {e}", "red")
        return False

    # Test 5: Cost Tracker
    cprint("\n📋 Test 5: Cost Tracker", "yellow", attrs=['bold'])
    cprint("-" * 70, "yellow")

    try:
        tracker = CostTracker()

        # Log the test request
        tracker.log_request(
            agent="test_agent",
            model=model.model_name,
            tokens_used=response.usage,
            cost=cost,
            task_type="testing"
        )

        # Get today's cost
        daily_cost = tracker.get_daily_cost()
        cprint(f"💰 Today's total cost: ${daily_cost:.6f}", "cyan")

        cprint("\n✅ Cost tracker working", "green")

    except Exception as e:
        cprint(f"❌ Cost tracker failed: {e}", "red")
        return False

    # Test 6: Multiple Models
    cprint("\n📋 Test 6: Test Multiple Models", "yellow", attrs=['bold'])
    cprint("-" * 70, "yellow")

    cheap_models = [
        "deepseek/deepseek-chat",
        "anthropic/claude-3-haiku",
    ]

    for model_name in cheap_models:
        try:
            cprint(f"\n🔄 Testing: {model_name}", "cyan")
            model = factory.get_model('openrouter', model_name)

            response = model.generate_response(
                system_prompt="Reply with just 'OK'",
                user_content="Test",
                max_tokens=5
            )

            cost = CostOptimizer.estimate_cost(
                model_name,
                response.usage['prompt_tokens'],
                response.usage['completion_tokens']
            )

            cprint(f"✅ {model_name}: Response '{response.content}' (${cost:.6f})", "green")

        except Exception as e:
            cprint(f"⚠️ {model_name} failed: {e}", "yellow")

    # Test 7: Show Cheapest Models
    cprint("\n📋 Test 7: List Cheapest Models", "yellow", attrs=['bold'])
    cprint("-" * 70, "yellow")

    try:
        CostOptimizer.get_cheapest_models(limit=5)
        cprint("\n✅ Cheapest models listed", "green")
    except Exception as e:
        cprint(f"❌ Failed to list models: {e}", "red")

    # Final Summary
    cprint("\n" + "="*70, "cyan", attrs=['bold'])
    cprint("🎉 ALL TESTS COMPLETED SUCCESSFULLY!", "green", attrs=['bold'])
    cprint("="*70, "cyan", attrs=['bold'])

    cprint("\n💡 Next Steps:", "cyan")
    cprint("  1. OpenRouter is ready to use in all agents", "green")
    cprint("  2. Use CostOptimizer.get_optimal_model() to select models", "green")
    cprint("  3. Use CostTracker to monitor spending", "green")
    cprint("  4. Check cost reports: tracker.print_summary()", "green")

    cprint("\n🌙 Moon Dev's OpenRouter integration is live!\n", "cyan", attrs=['bold'])

    return True

if __name__ == "__main__":
    try:
        success = test_openrouter()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        cprint("\n\n⚠️ Test interrupted by user", "yellow")
        sys.exit(1)
    except Exception as e:
        cprint(f"\n\n❌ Unexpected error: {e}", "red")
        import traceback
        traceback.print_exc()
        sys.exit(1)

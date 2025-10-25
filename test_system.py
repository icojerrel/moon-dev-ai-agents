#!/usr/bin/env python3
"""
🌙 Moon Dev's System Test - No API Keys Required
Test everything we can without valid API keys
Built with love by Moon Dev 🚀
"""

import os
import sys
from dotenv import load_dotenv
from termcolor import cprint

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported"""
    cprint("\n📋 Test 1: Import Tests", "yellow", attrs=['bold'])
    cprint("-" * 70, "yellow")

    tests = [
        ("Model Factory", "from src.models.model_factory import ModelFactory"),
        ("OpenRouter Model", "from src.models.openrouter_model import OpenRouterModel"),
        ("Cost Optimizer", "from src.utils.cost_optimizer import CostOptimizer"),
        ("Cost Tracker", "from src.utils.cost_tracker import CostTracker"),
        ("Config", "from src.config import MONITORED_TOKENS"),
    ]

    for name, import_stmt in tests:
        try:
            exec(import_stmt)
            cprint(f"  ✅ {name}", "green")
        except Exception as e:
            cprint(f"  ❌ {name}: {e}", "red")
            return False

    return True

def test_cost_optimizer():
    """Test Cost Optimizer (no API key needed)"""
    cprint("\n📋 Test 2: Cost Optimizer", "yellow", attrs=['bold'])
    cprint("-" * 70, "yellow")

    try:
        from src.utils.cost_optimizer import CostOptimizer

        # Test 2.1: Get optimal models
        cprint("\n  🔍 Test 2.1: Task-based model selection", "cyan")
        tasks = ["simple_chat", "research", "complex_reasoning", "strategy_backtest"]
        budgets = ["ultra_cheap", "cheap", "balanced"]

        for task in tasks:
            for budget in budgets:
                model = CostOptimizer.get_optimal_model(task, budget)
                cprint(f"    {task:20} ({budget:12}): {model}", "green")

        # Test 2.2: Cost estimation
        cprint("\n  🔍 Test 2.2: Cost estimation", "cyan")
        test_models = [
            "deepseek/deepseek-chat",
            "anthropic/claude-3-haiku",
            "anthropic/claude-3.5-sonnet"
        ]

        for model in test_models:
            cost = CostOptimizer.estimate_cost(model, 1000, 2000)
            cprint(f"    {model:40} 1K in + 2K out = ${cost:.6f}", "green")

        # Test 2.3: Cost comparison
        cprint("\n  🔍 Test 2.3: Cost comparison", "cyan")
        CostOptimizer.compare_costs(test_models, 10000, 20000)

        # Test 2.4: Cheapest models
        cprint("\n  🔍 Test 2.4: Cheapest models", "cyan")
        CostOptimizer.get_cheapest_models(limit=5)

        # Test 2.5: Monthly projections
        cprint("\n  🔍 Test 2.5: Monthly cost projection", "cyan")
        monthly = CostOptimizer.calculate_monthly_cost(
            daily_requests=100,
            avg_input_tokens=1000,
            avg_output_tokens=2000,
            model="deepseek/deepseek-chat"
        )

        # Test 2.6: Best value models
        cprint("\n  🔍 Test 2.6: Best value recommendations", "cyan")
        best = CostOptimizer.get_best_value_models()
        for use_case, model in best.items():
            cprint(f"    {use_case:25}: {model}", "green")

        cprint("\n  ✅ Cost Optimizer: All tests passed!", "green", attrs=['bold'])
        return True

    except Exception as e:
        cprint(f"  ❌ Cost Optimizer failed: {e}", "red")
        import traceback
        traceback.print_exc()
        return False

def test_cost_tracker():
    """Test Cost Tracker (no API key needed)"""
    cprint("\n📋 Test 3: Cost Tracker", "yellow", attrs=['bold'])
    cprint("-" * 70, "yellow")

    try:
        from src.utils.cost_tracker import CostTracker

        # Test 3.1: Initialize tracker
        cprint("\n  🔍 Test 3.1: Initialize tracker", "cyan")
        tracker = CostTracker(log_dir="src/data/test_cost_tracking")
        cprint("    ✅ Tracker initialized", "green")

        # Test 3.2: Log some requests
        cprint("\n  🔍 Test 3.2: Log test requests", "cyan")
        test_logs = [
            ("rbi_agent", "deepseek/deepseek-chat", {"prompt_tokens": 1000, "completion_tokens": 2000, "total_tokens": 3000}, 0.0042, "strategy_backtest"),
            ("trading_agent", "anthropic/claude-3-haiku", {"prompt_tokens": 500, "completion_tokens": 1000, "total_tokens": 1500}, 0.0014, "trading_analysis"),
            ("research_agent", "deepseek/deepseek-r1", {"prompt_tokens": 2000, "completion_tokens": 4000, "total_tokens": 6000}, 0.0098, "research"),
        ]

        for agent, model, tokens, cost, task in test_logs:
            tracker.log_request(agent, model, tokens, cost, task)

        cprint("    ✅ Logged 3 test requests", "green")

        # Test 3.3: Get daily cost
        cprint("\n  🔍 Test 3.3: Get daily cost", "cyan")
        daily = tracker.get_daily_cost()
        cprint(f"    Today's total: ${daily:.6f}", "green")

        # Test 3.4: Get agent costs
        cprint("\n  🔍 Test 3.4: Get costs per agent", "cyan")
        agent_costs = tracker.get_agent_costs(days=1)
        for agent, cost in agent_costs.items():
            cprint(f"    {agent:20}: ${cost:.6f}", "green")

        # Test 3.5: Get model costs
        cprint("\n  🔍 Test 3.5: Get costs per model", "cyan")
        model_costs = tracker.get_model_costs(days=1)
        for model, cost in model_costs.items():
            cprint(f"    {model:40}: ${cost:.6f}", "green")

        # Test 3.6: Print summary
        cprint("\n  🔍 Test 3.6: Print summary", "cyan")
        tracker.print_summary(days=1)

        # Test 3.7: Budget check
        cprint("\n  🔍 Test 3.7: Budget limit check", "cyan")
        budget_check = tracker.check_budget_limit(daily_limit=1.0, monthly_limit=30.0)
        cprint(f"    Daily OK: {budget_check['daily_ok']}", "green" if budget_check['daily_ok'] else "red")
        cprint(f"    Monthly OK: {budget_check['monthly_ok']}", "green" if budget_check['monthly_ok'] else "red")

        cprint("\n  ✅ Cost Tracker: All tests passed!", "green", attrs=['bold'])
        return True

    except Exception as e:
        cprint(f"  ❌ Cost Tracker failed: {e}", "red")
        import traceback
        traceback.print_exc()
        return False

def test_model_factory():
    """Test Model Factory initialization"""
    cprint("\n📋 Test 4: Model Factory", "yellow", attrs=['bold'])
    cprint("-" * 70, "yellow")

    try:
        from src.models.model_factory import ModelFactory

        cprint("\n  🔍 Initializing Model Factory...", "cyan")
        factory = ModelFactory()

        # Check which models are available
        cprint("\n  📊 Available Providers:", "cyan")
        available = []
        for provider in ["claude", "openai", "deepseek", "groq", "xai", "openrouter", "ollama"]:
            is_available = factory.is_model_available(provider)
            status = "✅" if is_available else "❌"
            color = "green" if is_available else "red"
            cprint(f"    {status} {provider}", color)
            if is_available:
                available.append(provider)

        if available:
            cprint(f"\n  ✅ {len(available)} provider(s) available: {', '.join(available)}", "green")
        else:
            cprint("\n  ⚠️ No providers available (need valid API keys)", "yellow")

        return True

    except Exception as e:
        cprint(f"  ❌ Model Factory failed: {e}", "red")
        import traceback
        traceback.print_exc()
        return False

def test_openrouter_integration():
    """Test OpenRouter specific features"""
    cprint("\n📋 Test 5: OpenRouter Integration", "yellow", attrs=['bold'])
    cprint("-" * 70, "yellow")

    try:
        from src.models.openrouter_model import OpenRouterModel

        # Test 5.1: Check available models
        cprint("\n  🔍 Test 5.1: OpenRouter available models", "cyan")
        cprint(f"    Total models defined: {len(OpenRouterModel.AVAILABLE_MODELS)}", "green")

        cprint("\n  Popular models:", "cyan")
        popular = [
            "deepseek-chat",
            "claude-haiku",
            "claude-3.5-sonnet",
            "gpt-4o",
            "deepseek-r1"
        ]

        for key in popular:
            if key in OpenRouterModel.AVAILABLE_MODELS:
                info = OpenRouterModel.AVAILABLE_MODELS[key]
                cprint(f"    ✅ {key:25} - {info.get('description', 'N/A')}", "green")
                cprint(f"       Price: {info.get('input_price')} in / {info.get('output_price')} out", "cyan")

        cprint("\n  ✅ OpenRouter model definitions loaded", "green", attrs=['bold'])
        return True

    except Exception as e:
        cprint(f"  ❌ OpenRouter test failed: {e}", "red")
        return False

def main():
    """Run all tests"""

    cprint("\n" + "="*70, "cyan", attrs=['bold'])
    cprint("🧪 MOON DEV'S COMPREHENSIVE SYSTEM TEST", "cyan", attrs=['bold'])
    cprint("="*70 + "\n", "cyan", attrs=['bold'])

    # Load environment
    load_dotenv()

    results = []

    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Cost Optimizer", test_cost_optimizer()))
    results.append(("Cost Tracker", test_cost_tracker()))
    results.append(("Model Factory", test_model_factory()))
    results.append(("OpenRouter Integration", test_openrouter_integration()))

    # Summary
    cprint("\n" + "="*70, "cyan", attrs=['bold'])
    cprint("📊 TEST SUMMARY", "cyan", attrs=['bold'])
    cprint("="*70 + "\n", "cyan", attrs=['bold'])

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        color = "green" if result else "red"
        cprint(f"  {status:10} - {name}", color, attrs=['bold'])

    cprint(f"\n  Total: {passed}/{total} tests passed", "cyan", attrs=['bold'])

    # Next steps
    if passed == total:
        cprint("\n🎉 ALL TESTS PASSED!", "green", attrs=['bold'])
        cprint("\n💡 System is ready!", "cyan")
        cprint("   - Cost Optimizer: ✅ Working", "green")
        cprint("   - Cost Tracker: ✅ Working", "green")
        cprint("   - OpenRouter: ✅ Integrated (needs valid API key to use)", "yellow")
    else:
        cprint("\n⚠️ Some tests failed", "yellow", attrs=['bold'])

    cprint("\n📋 To use OpenRouter:", "cyan")
    cprint("   1. Get API key from https://openrouter.ai", "yellow")
    cprint("   2. Add $5+ credits to account", "yellow")
    cprint("   3. Update .env with key", "yellow")
    cprint("   4. Run: python test_openrouter.py", "yellow")

    cprint("\n🌙 Moon Dev's System Test Complete!\n", "cyan", attrs=['bold'])

    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        cprint("\n\n⚠️ Test interrupted by user", "yellow")
        sys.exit(1)
    except Exception as e:
        cprint(f"\n\n❌ Unexpected error: {e}", "red")
        import traceback
        traceback.print_exc()
        sys.exit(1)

#!/usr/bin/env python3
"""
Test script for qwen3-coder:30b local model integration
Run this after starting Ollama: ollama serve
"""

from termcolor import cprint
from src.models.model_factory import ModelFactory

def test_qwen_model():
    """Test the qwen3-coder:30b model integration"""

    cprint("\n" + "="*60, "cyan")
    cprint("🧪 Testing Qwen3-Coder:30B Integration", "cyan", attrs=["bold"])
    cprint("="*60 + "\n", "cyan")

    # Initialize model factory
    cprint("📦 Initializing ModelFactory...", "yellow")
    try:
        factory = ModelFactory()
        cprint("✅ ModelFactory initialized\n", "green")
    except Exception as e:
        cprint(f"❌ Failed to initialize ModelFactory: {e}", "red")
        return False

    # Check if Ollama is available
    if not factory.is_model_available("ollama"):
        cprint("❌ Ollama not available. Make sure:", "red")
        cprint("   1. Ollama is installed: curl https://ollama.ai/install.sh | sh", "yellow")
        cprint("   2. Server is running: ollama serve", "yellow")
        cprint("   3. Model is pulled: ollama pull qwen3-coder:30b", "yellow")
        return False

    cprint("✅ Ollama is available\n", "green")

    # Get the model
    cprint("🤖 Getting qwen3-coder:30b model...", "yellow")
    try:
        model = factory.get_model("ollama")  # Should use qwen3-coder:30b by default
        cprint(f"✅ Model loaded: {model.model_name}\n", "green")

        if model.model_name != "qwen3-coder:30b":
            cprint(f"⚠️ Warning: Expected qwen3-coder:30b but got {model.model_name}", "yellow")
    except Exception as e:
        cprint(f"❌ Failed to get model: {e}", "red")
        return False

    # Test 1: Simple code generation
    cprint("="*60, "cyan")
    cprint("Test 1: Simple Python Function Generation", "cyan", attrs=["bold"])
    cprint("="*60, "cyan")

    test_prompt_1 = """Write a Python function that calculates the RSI (Relative Strength Index)
for a given price series. The function should take a pandas Series and period (default 14) as parameters."""

    cprint("\n📝 Prompt:", "yellow")
    cprint(test_prompt_1, "white")
    cprint("\n🤔 Generating response...\n", "yellow")

    try:
        response = model.generate_response(
            system_prompt="You are an expert Python developer specializing in trading algorithms.",
            user_content=test_prompt_1,
            temperature=0.3,
            max_tokens=1000
        )

        cprint("✅ Response received:", "green")
        cprint("-"*60, "white")
        cprint(response.content, "white")
        cprint("-"*60 + "\n", "white")

    except Exception as e:
        cprint(f"❌ Test 1 failed: {e}", "red")
        return False

    # Test 2: Trading strategy analysis
    cprint("="*60, "cyan")
    cprint("Test 2: Trading Strategy Analysis", "cyan", attrs=["bold"])
    cprint("="*60, "cyan")

    test_prompt_2 = """Analyze this simple trading strategy and suggest improvements:

Strategy:
- Buy when RSI < 30
- Sell when RSI > 70
- Use 14-period RSI on 1-hour timeframe

What are potential weaknesses and how can we improve it?"""

    cprint("\n📝 Prompt:", "yellow")
    cprint(test_prompt_2, "white")
    cprint("\n🤔 Generating response...\n", "yellow")

    try:
        response = model.generate_response(
            system_prompt="You are a quantitative trading strategist with expertise in technical analysis.",
            user_content=test_prompt_2,
            temperature=0.5,
            max_tokens=800
        )

        cprint("✅ Response received:", "green")
        cprint("-"*60, "white")
        cprint(response.content, "white")
        cprint("-"*60 + "\n", "white")

    except Exception as e:
        cprint(f"❌ Test 2 failed: {e}", "red")
        return False

    # Test 3: Quick response test
    cprint("="*60, "cyan")
    cprint("Test 3: Quick Response Test", "cyan", attrs=["bold"])
    cprint("="*60, "cyan")

    test_prompt_3 = "What is the current price of Bitcoin in a single sentence?"

    cprint("\n📝 Prompt:", "yellow")
    cprint(test_prompt_3, "white")
    cprint("\n🤔 Generating response...\n", "yellow")

    try:
        response = model.generate_response(
            system_prompt="You are a helpful AI assistant.",
            user_content=test_prompt_3,
            temperature=0.7,
            max_tokens=100
        )

        cprint("✅ Response received:", "green")
        cprint("-"*60, "white")
        cprint(response.content, "white")
        cprint("-"*60 + "\n", "white")

    except Exception as e:
        cprint(f"❌ Test 3 failed: {e}", "red")
        return False

    # All tests passed
    cprint("\n" + "="*60, "green")
    cprint("🎉 ALL TESTS PASSED!", "green", attrs=["bold"])
    cprint("="*60, "green")
    cprint(f"\nqwen3-coder:30b is working correctly! 🚀", "green")
    cprint("The model is ready to use in agents.\n", "green")

    return True


if __name__ == "__main__":
    import sys

    # Make sure we're in the right directory
    import os
    from pathlib import Path

    # Get the project root (where this script is located)
    project_root = Path(__file__).parent
    os.chdir(project_root)

    # Run the tests
    success = test_qwen_model()

    # Exit with appropriate code
    sys.exit(0 if success else 1)

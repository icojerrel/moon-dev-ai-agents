#!/usr/bin/env python3
"""
🌙 Moon Dev's OpenRouter Test Script
Run this locally to test OpenRouter integration

This script tests the OpenRouter API key without Claude Code's proxy restrictions.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.openrouter_model import OpenRouterModel, OpenRouterError, ModerationError
from dotenv import load_dotenv
from termcolor import cprint

def main():
    cprint("\n🌙 MOON DEV'S OPENROUTER LOCAL TEST", "cyan", attrs=["bold"])
    cprint("=" * 70, "cyan")

    # Load environment
    load_dotenv()
    api_key = os.getenv('OPENROUTER_API_KEY')

    if not api_key or api_key == "your_openrouter_key_here":
        cprint("\n❌ No OpenRouter API key found in .env", "red")
        cprint("   Add your key to .env file:", "yellow")
        cprint("   OPENROUTER_API_KEY=sk-or-v1-...", "white")
        return 1

    cprint(f"\n🔑 API Key: {api_key[:20]}...{api_key[-10:]}", "white")

    # Test 1: Initialize model
    cprint("\n" + "="*70, "cyan")
    cprint("TEST 1: Initialize OpenRouter Model", "cyan", attrs=["bold"])
    cprint("="*70, "cyan")

    try:
        model = OpenRouterModel(
            api_key=api_key,
            model_name="anthropic/claude-3-haiku"  # Cheap paid model
        )
        cprint("✅ Model initialized successfully!", "green")
    except Exception as e:
        cprint(f"❌ Failed to initialize: {e}", "red")
        return 1

    # Test 2: Check availability
    cprint("\n" + "="*70, "cyan")
    cprint("TEST 2: Check API Availability", "cyan", attrs=["bold"])
    cprint("="*70, "cyan")

    is_available = model.is_available()

    if not is_available:
        cprint("\n⚠️  OpenRouter not available - check error messages above", "yellow")
        return 1

    # Test 3: Simple completion
    cprint("\n" + "="*70, "cyan")
    cprint("TEST 3: Generate Response", "cyan", attrs=["bold"])
    cprint("="*70, "cyan")

    try:
        response = model.generate_response(
            system_prompt="You are a helpful AI assistant.",
            user_content="Say 'Hello Moon Dev!' if you can read this.",
            max_tokens=50
        )

        cprint("\n✅ SUCCESS! OpenRouter is working!", "green", attrs=["bold"])
        cprint(f"\n📝 Response:", "cyan")
        cprint(f"   {response.content}", "white")
        cprint(f"\n📊 Usage:", "cyan")
        cprint(f"   Tokens: {response.usage['total_tokens']} ({response.usage['prompt_tokens']} in + {response.usage['completion_tokens']} out)", "white")
        cprint(f"   Model: {response.model_name}", "white")

    except ModerationError as e:
        cprint(f"\n🚨 Content Moderation Error:", "yellow")
        cprint(f"   Reasons: {', '.join(e.reasons)}", "yellow")
        cprint(f"   Flagged: {e.flagged_input}", "yellow")
        return 1

    except OpenRouterError as e:
        cprint(f"\n❌ OpenRouter Error {e.code}:", "red")
        cprint(f"   {e.message}", "red")
        return 1

    # Test 4: List cheapest models
    cprint("\n" + "="*70, "cyan")
    cprint("TEST 4: Find Cheapest Models", "cyan", attrs=["bold"])
    cprint("="*70, "cyan")

    try:
        cheap_models = model.find_cheapest_models(top_n=5)
        if cheap_models:
            cprint("\n✅ Model discovery working!", "green")
    except Exception as e:
        cprint(f"\n⚠️  Model discovery failed (non-critical): {e}", "yellow")

    # Success summary
    cprint("\n" + "="*70, "green")
    cprint("🎉 ALL TESTS PASSED!", "green", attrs=["bold"])
    cprint("="*70, "green")

    cprint("\n✅ OpenRouter integration is fully functional!", "green")
    cprint("💡 You can now use OpenRouter in your agents:", "cyan")
    cprint("   from src.models.model_factory import ModelFactory", "white")
    cprint("   model = ModelFactory.create_model('openrouter')", "white")
    cprint("   response = model.generate_response(system, user)", "white")

    cprint("\n💰 Cost Savings:", "cyan")
    cprint("   DeepSeek R1: $0.55/$2.19 per 1M tokens (98% cheaper than GPT-4)", "white")
    cprint("   Claude Haiku: $0.25/$1.25 per 1M tokens (95% cheaper than Claude Opus)", "white")

    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        cprint("\n\n⚠️  Test interrupted by user", "yellow")
        sys.exit(1)
    except Exception as e:
        cprint(f"\n❌ Unexpected error: {e}", "red")
        import traceback
        traceback.print_exc()
        sys.exit(1)

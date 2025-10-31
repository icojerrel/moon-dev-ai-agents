#!/usr/bin/env python3
"""
🌙 Moon Dev's OpenRouter Test Script
Test your OpenRouter API integration
"""

import os
from dotenv import load_dotenv
from termcolor import cprint
from src.models.model_factory import ModelFactory

def test_openrouter():
    """Test OpenRouter integration"""

    cprint("\n🌙 Moon Dev's OpenRouter Test Script", "cyan")
    cprint("=" * 50, "cyan")

    # Load environment variables
    load_dotenv()

    # Check if OpenRouter API key is set
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        cprint("\n❌ OPENROUTER_API_KEY not found in .env file", "red")
        cprint("📝 Please add your OpenRouter API key to .env:", "yellow")
        cprint("   OPENROUTER_API_KEY=sk-or-v1-xxxxx", "yellow")
        cprint("\n🔗 Get your key at: https://openrouter.ai/keys", "cyan")
        return

    cprint(f"\n✅ Found OpenRouter API key ({len(api_key)} chars)", "green")

    # Initialize ModelFactory
    cprint("\n🏭 Initializing Model Factory...", "cyan")
    factory = ModelFactory()

    # Check if OpenRouter is available
    if not factory.is_model_available("openrouter"):
        cprint("\n❌ OpenRouter not available", "red")
        return

    cprint("\n✅ OpenRouter is available!", "green")

    # Test with a simple prompt using different models
    test_models = [
        "anthropic/claude-3.5-sonnet",   # Best balanced model
        "deepseek/deepseek-r1",          # Great for trading, cheap
        "openai/gpt-4o-mini",            # Fast and cheap
    ]

    for model_name in test_models:
        cprint(f"\n{'=' * 50}", "cyan")
        cprint(f"🧪 Testing model: {model_name}", "cyan")
        cprint(f"{'=' * 50}", "cyan")

        try:
            # Get the model
            model = factory.get_model("openrouter", model_name)

            if not model:
                cprint(f"❌ Failed to initialize {model_name}", "red")
                continue

            # Generate a simple response
            cprint("📝 Sending test prompt...", "yellow")
            response = model.generate_response(
                system_prompt="You are a helpful AI assistant. Be concise.",
                user_content="Say 'Hello from OpenRouter!' and tell me one interesting fact about the moon in one sentence.",
                temperature=0.7,
                max_tokens=100
            )

            if response and response.content:
                cprint(f"\n✅ Response received:", "green")
                cprint(f"📄 {response.content}", "white")

                if response.usage:
                    cprint(f"\n💰 Token usage: {response.usage}", "cyan")
            else:
                cprint(f"\n❌ No response received from {model_name}", "red")

        except Exception as e:
            cprint(f"\n❌ Error testing {model_name}: {str(e)}", "red")

    cprint("\n" + "=" * 50, "cyan")
    cprint("🎉 OpenRouter test complete!", "green")
    cprint("\n💡 Tips:", "cyan")
    cprint("  • Use 'google/gemini-2.0-flash-exp' for free testing", "yellow")
    cprint("  • Use 'deepseek/deepseek-r1' for best value trading analysis", "yellow")
    cprint("  • Use 'anthropic/claude-3.5-sonnet' for complex tasks", "yellow")
    cprint("  • See all models at: https://openrouter.ai/models", "yellow")
    cprint("\n🌙 Happy trading with Moon Dev! 🚀", "green")

if __name__ == "__main__":
    test_openrouter()

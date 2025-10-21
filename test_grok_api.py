"""
🌙 Grok API Test Script with Smart Fallback Data
Tests the Grok integration with semi-realistic market data
"""

import sys
import os
from pathlib import Path
from termcolor import cprint
import json

# Add the src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from models.model_factory import ModelFactory

def get_smart_fallback_data():
    """
    Returns semi-realistic market data for testing
    Simulates what CoinGecko would return
    """
    return {
        "bitcoin": {
            "price": 67234.56,
            "market_cap": 1316789234567,
            "volume_24h": 28456789123,
            "price_change_24h": 2.34,
            "price_change_7d": -1.23,
            "circulating_supply": 19589234,
            "total_supply": 21000000,
            "market_cap_rank": 1
        },
        "ethereum": {
            "price": 2456.78,
            "market_cap": 295123456789,
            "volume_24h": 12345678901,
            "price_change_24h": 1.89,
            "price_change_7d": -2.45,
            "circulating_supply": 120123456,
            "market_cap_rank": 2
        },
        "solana": {
            "price": 145.67,
            "market_cap": 67890123456,
            "volume_24h": 2345678901,
            "price_change_24h": 5.67,
            "price_change_7d": 8.34,
            "circulating_supply": 466234567,
            "market_cap_rank": 5
        },
        "cardano": {
            "price": 0.456,
            "market_cap": 16234567890,
            "volume_24h": 456789012,
            "price_change_24h": -0.89,
            "price_change_7d": -3.21,
            "circulating_supply": 35567890123,
            "market_cap_rank": 8
        },
        "polkadot": {
            "price": 6.78,
            "market_cap": 9876543210,
            "volume_24h": 234567890,
            "price_change_24h": 3.45,
            "price_change_7d": 1.23,
            "circulating_supply": 1456789012,
            "market_cap_rank": 12
        }
    }

def test_grok_with_market_data():
    """
    Test Grok API with semi-realistic market data
    """
    cprint("\n" + "="*60, "cyan")
    cprint("🚀 Grok API Test with Smart Fallback Data", "cyan", attrs=["bold"])
    cprint("="*60 + "\n", "cyan")

    # Initialize Model Factory
    cprint("📦 Initializing Model Factory...", "yellow")
    factory = ModelFactory()

    # Check if xAI/Grok is available
    if not factory.is_model_available("xai"):
        cprint("\n❌ Grok/xAI model not available!", "red")
        cprint("💡 Make sure GROK_API_KEY is set in your .env file", "yellow")
        return False

    cprint("✅ Grok model is available!\n", "green")

    # Get the model
    cprint("🔍 Getting Grok model instance...", "yellow")
    grok_model = factory.get_model("xai", "grok-4-fast-reasoning")

    if not grok_model:
        cprint("\n❌ Failed to get Grok model instance!", "red")
        return False

    cprint("✅ Got Grok model instance!\n", "green")

    # Get smart fallback data
    cprint("📊 Loading market data (fallback mode for sandbox)...", "yellow")
    market_data = get_smart_fallback_data()

    # Format data for the prompt
    data_str = json.dumps(market_data, indent=2)
    cprint("✅ Market data loaded!\n", "green")

    # Print sample of data
    cprint("📈 Sample Market Data:", "cyan")
    cprint(f"  • Bitcoin: ${market_data['bitcoin']['price']:,.2f} ({market_data['bitcoin']['price_change_24h']:+.2f}%)", "white")
    cprint(f"  • Ethereum: ${market_data['ethereum']['price']:,.2f} ({market_data['ethereum']['price_change_24h']:+.2f}%)", "white")
    cprint(f"  • Solana: ${market_data['solana']['price']:,.2f} ({market_data['solana']['price_change_24h']:+.2f}%)\n", "white")

    # Create prompts
    system_prompt = """You are an expert cryptocurrency market analyst.
Analyze the provided market data and give a brief market overview with:
1. Overall market sentiment
2. Top performing coin (by 24h change)
3. Any notable trends
4. Brief trading recommendation

Keep your response concise and actionable."""

    user_prompt = f"""Analyze this cryptocurrency market data:

{data_str}

Provide your market analysis."""

    # Test Grok API
    cprint("🤖 Calling Grok API...", "yellow")
    cprint("⏳ This may take a few seconds...\n", "yellow")

    try:
        response = grok_model.generate_response(
            system_prompt=system_prompt,
            user_content=user_prompt,
            temperature=0.7,
            max_tokens=500
        )

        if response and response.content:
            cprint("\n" + "="*60, "green")
            cprint("✅ GROK API TEST SUCCESSFUL!", "green", attrs=["bold"])
            cprint("="*60 + "\n", "green")

            cprint("📝 Grok's Market Analysis:", "cyan", attrs=["bold"])
            cprint("-"*60, "cyan")
            cprint(response.content, "white")
            cprint("-"*60 + "\n", "cyan")

            # Show usage stats if available
            if response.usage:
                cprint("📊 API Usage Statistics:", "cyan")
                cprint(f"  • Prompt tokens: {response.usage.get('prompt_tokens', 'N/A')}", "white")
                cprint(f"  • Completion tokens: {response.usage.get('completion_tokens', 'N/A')}", "white")
                cprint(f"  • Total tokens: {response.usage.get('total_tokens', 'N/A')}\n", "white")

            return True
        else:
            cprint("\n❌ No response received from Grok!", "red")
            return False

    except Exception as e:
        cprint(f"\n❌ Error during Grok API call: {str(e)}", "red")
        cprint(f"Error type: {type(e).__name__}", "yellow")
        return False

def test_different_grok_models():
    """
    Test different Grok models to compare performance
    """
    cprint("\n" + "="*60, "cyan")
    cprint("🔄 Testing Different Grok Models", "cyan", attrs=["bold"])
    cprint("="*60 + "\n", "cyan")

    factory = ModelFactory()

    # Models to test
    models_to_test = [
        "grok-4-fast-reasoning",
        "grok-4-fast-non-reasoning",
        "grok-code-fast-1"
    ]

    test_prompt = "Explain in one sentence why Solana is gaining popularity in 2025."

    for model_name in models_to_test:
        cprint(f"\n🧪 Testing {model_name}...", "yellow")

        try:
            model = factory.get_model("xai", model_name)

            if not model:
                cprint(f"  ❌ Could not get model {model_name}", "red")
                continue

            response = model.generate_response(
                system_prompt="You are a helpful assistant. Be brief.",
                user_content=test_prompt,
                temperature=0.7,
                max_tokens=100
            )

            if response:
                cprint(f"  ✅ {model_name} response:", "green")
                cprint(f"     {response.content[:150]}...", "white")
            else:
                cprint(f"  ❌ No response from {model_name}", "red")

        except Exception as e:
            cprint(f"  ❌ Error with {model_name}: {str(e)}", "red")

def main():
    """
    Main test runner
    """
    cprint("\n🌙 Moon Dev's Grok API Test Suite 🌙\n", "magenta", attrs=["bold"])

    # Test 1: Market Data Analysis
    test_result = test_grok_with_market_data()

    if test_result:
        cprint("\n✅ PRIMARY TEST PASSED!", "green", attrs=["bold"])

        # Test 2: Different Models (optional)
        cprint("\n" + "="*60, "cyan")
        response = input("Would you like to test different Grok models? (y/n): ")
        if response.lower() == 'y':
            test_different_grok_models()
    else:
        cprint("\n❌ PRIMARY TEST FAILED!", "red", attrs=["bold"])
        cprint("\n💡 Troubleshooting tips:", "yellow")
        cprint("  1. Check that GROK_API_KEY is set in .env", "white")
        cprint("  2. Verify your API key is valid", "white")
        cprint("  3. Check your internet connection", "white")
        cprint("  4. Make sure you have API credits remaining\n", "white")

    cprint("\n" + "="*60, "cyan")
    cprint("🎉 Test Suite Complete!", "cyan", attrs=["bold"])
    cprint("="*60 + "\n", "cyan")

if __name__ == "__main__":
    main()

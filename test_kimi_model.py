#!/usr/bin/env python3
"""
🌙 Test Moonshot AI Kimi K2-0905 Model via OpenRouter
"""

import os
from openai import OpenAI
from dotenv import load_dotenv
from termcolor import cprint

# Load environment
load_dotenv()

def test_kimi_model():
    """Test Kimi K2-0905 model through OpenRouter"""

    cprint("\n" + "="*60, "cyan")
    cprint("🌙 TESTING MOONSHOT AI KIMI K2-0905 🌙", "white", "on_blue")
    cprint("="*60, "cyan")

    # Get API key
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        cprint("\n❌ OPENROUTER_API_KEY not found in .env", "red")
        return False

    cprint(f"\n✅ API Key found ({len(api_key)} chars)", "green")

    # Model info
    cprint("\n📊 MODEL SPECS:", "cyan")
    cprint("  ├─ Name: Kimi K2-0905", "yellow")
    cprint("  ├─ Developer: Moonshot AI", "yellow")
    cprint("  ├─ Parameters: 1 Trillion (MoE)", "yellow")
    cprint("  ├─ Active Params: 32 Billion", "yellow")
    cprint("  ├─ Context Window: 256k tokens", "yellow")
    cprint("  ├─ Pricing: $1/$3 per 1M tokens", "yellow")
    cprint("  └─ Best for: Coding, reasoning, tool use", "yellow")

    # Initialize OpenRouter client
    cprint("\n🔌 Connecting to OpenRouter...", "cyan")

    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )

    cprint("✅ Client initialized", "green")

    # Test prompts
    test_cases = [
        {
            "name": "Simple Greeting",
            "system": "You are a helpful AI assistant.",
            "prompt": "Say hello and tell me one interesting fact about AI in one sentence.",
            "max_tokens": 100
        },
        {
            "name": "Trading Strategy Question",
            "system": "You are a trading strategy expert.",
            "prompt": "What is the most important factor when backtesting a momentum trading strategy?",
            "max_tokens": 200
        },
        {
            "name": "Code Generation",
            "system": "You are a Python coding expert.",
            "prompt": "Write a Python function to calculate RSI (Relative Strength Index) for a price series.",
            "max_tokens": 300
        }
    ]

    results = []

    for i, test in enumerate(test_cases, 1):
        cprint(f"\n{'='*60}", "cyan")
        cprint(f"TEST {i}/{len(test_cases)}: {test['name']}", "white", "on_magenta")
        cprint(f"{'='*60}", "cyan")

        cprint(f"\n📝 Prompt: {test['prompt'][:80]}...", "yellow")
        cprint(f"⚙️  Max Tokens: {test['max_tokens']}", "yellow")

        try:
            cprint("\n⏳ Sending request to Kimi K2-0905...", "cyan")

            response = client.chat.completions.create(
                model="moonshotai/kimi-k2-0905",
                messages=[
                    {"role": "system", "content": test['system']},
                    {"role": "user", "content": test['prompt']}
                ],
                max_tokens=test['max_tokens'],
                temperature=0.7
            )

            content = response.choices[0].message.content
            usage = response.usage

            cprint(f"\n✅ Response received!", "green")
            cprint(f"\n📄 OUTPUT:", "cyan")
            cprint("-"*60, "white")
            cprint(content, "white")
            cprint("-"*60, "white")

            cprint(f"\n💰 TOKEN USAGE:", "yellow")
            cprint(f"  ├─ Input: {usage.prompt_tokens} tokens", "yellow")
            cprint(f"  ├─ Output: {usage.completion_tokens} tokens", "yellow")
            cprint(f"  └─ Total: {usage.total_tokens} tokens", "yellow")

            # Calculate cost
            input_cost = (usage.prompt_tokens / 1_000_000) * 1.00  # $1 per 1M
            output_cost = (usage.completion_tokens / 1_000_000) * 3.00  # $3 per 1M
            total_cost = input_cost + output_cost

            cprint(f"\n💵 ESTIMATED COST:", "green")
            cprint(f"  └─ ${total_cost:.6f} USD", "green")

            results.append({
                "test": test['name'],
                "success": True,
                "tokens": usage.total_tokens,
                "cost": total_cost
            })

        except Exception as e:
            cprint(f"\n❌ ERROR: {str(e)}", "red")

            # Check for specific errors
            if "402" in str(e) or "insufficient" in str(e).lower():
                cprint("💳 Insufficient credits - add credits at https://openrouter.ai/credits", "yellow")
            elif "401" in str(e):
                cprint("🔑 Invalid API key - check your OPENROUTER_API_KEY", "yellow")
            elif "404" in str(e):
                cprint("🤔 Model not found - check model name", "yellow")

            results.append({
                "test": test['name'],
                "success": False,
                "error": str(e)
            })

    # Summary
    cprint(f"\n{'='*60}", "cyan")
    cprint("📊 TEST SUMMARY", "white", "on_green")
    cprint(f"{'='*60}", "cyan")

    successful = sum(1 for r in results if r.get('success'))
    failed = len(results) - successful

    cprint(f"\n✅ Successful: {successful}/{len(results)}", "green")
    cprint(f"❌ Failed: {failed}/{len(results)}", "red" if failed > 0 else "green")

    if successful > 0:
        total_tokens = sum(r.get('tokens', 0) for r in results if r.get('success'))
        total_cost = sum(r.get('cost', 0) for r in results if r.get('success'))

        cprint(f"\n💰 Total Tokens Used: {total_tokens}", "yellow")
        cprint(f"💵 Total Cost: ${total_cost:.6f} USD", "green")

        cprint(f"\n🎉 KIMI K2-0905 IS WORKING VIA OPENROUTER! 🎉", "white", "on_green")
        cprint("\n💡 Model Performance:", "cyan")
        cprint("  ├─ Fast response times", "yellow")
        cprint("  ├─ 256k context window (excellent for long documents)", "yellow")
        cprint("  ├─ Good for coding tasks", "yellow")
        cprint("  └─ Competitive pricing: $1/$3 per 1M tokens", "yellow")

        return True
    else:
        cprint(f"\n⚠️ All tests failed - check API key and credits", "yellow")
        return False

if __name__ == "__main__":
    test_kimi_model()

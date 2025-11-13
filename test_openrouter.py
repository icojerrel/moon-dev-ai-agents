#!/usr/bin/env python3
"""
🌙 Moon Dev's OpenRouter Test Script
Tests OpenRouter API connection with multiple models
"""

import os
import sys
from pathlib import Path
from termcolor import cprint
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Load environment variables
load_dotenv()

# Import model factory
from src.models.model_factory import ModelFactory

def test_openrouter():
    """Test OpenRouter with different models"""

    cprint("\n" + "="*60, "cyan", attrs=['bold'])
    cprint("🌙 Moon Dev's OpenRouter Connection Test", "cyan", attrs=['bold'])
    cprint("="*60 + "\n", "cyan", attrs=['bold'])

    # Check if API key is set
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        cprint("❌ OPENROUTER_API_KEY not found in .env!", "red", attrs=['bold'])
        return False

    cprint(f"✅ API Key found: {api_key[:20]}...", "green")

    # Test models (from cheap to expensive)
    test_models = [
        ("google/gemini-2.5-flash", "Gemini 2.5 Flash - Fast & Cheap"),
        ("qwen/qwen3-vl-32b-instruct", "Qwen 3 VL 32B - Vision & Language"),
        ("anthropic/claude-3-5-haiku", "Claude 3.5 Haiku - Fast Anthropic")
    ]

    test_prompt = "What is 2+2? Answer in one short sentence."

    results = []

    for model_name, description in test_models:
        cprint(f"\n{'='*60}", "yellow")
        cprint(f"🧪 Testing: {description}", "yellow", attrs=['bold'])
        cprint(f"📝 Model: {model_name}", "cyan")
        cprint(f"{'='*60}", "yellow")

        try:
            # Create model instance
            model = ModelFactory.create_model(
                'openrouter',
                model_name=model_name
            )

            if not model:
                cprint(f"❌ Failed to create model instance", "red")
                results.append((model_name, False, "Failed to create instance"))
                continue

            # Test simple query
            cprint(f"💬 Sending test query...", "cyan")
            response = model.generate_response(
                system_prompt="You are a helpful assistant.",
                user_content=test_prompt,
                temperature=0.7,
                max_tokens=100
            )

            if response and response.content:
                cprint(f"\n✅ SUCCESS!", "green", attrs=['bold'])
                cprint(f"📨 Response: {response.content}", "white")

                # Show usage if available
                if hasattr(response, 'usage') and response.usage:
                    usage = response.usage
                    if isinstance(usage, dict):
                        total_tokens = usage.get('total_tokens', 'N/A')
                    else:
                        total_tokens = getattr(usage, 'total_tokens', 'N/A')
                    cprint(f"📊 Tokens used: {total_tokens}", "cyan")

                results.append((model_name, True, response.content[:100]))
            else:
                cprint(f"❌ Empty response received", "red")
                results.append((model_name, False, "Empty response"))

        except Exception as e:
            cprint(f"\n❌ ERROR: {str(e)}", "red", attrs=['bold'])
            results.append((model_name, False, str(e)[:100]))

    # Print summary
    cprint(f"\n{'='*60}", "cyan", attrs=['bold'])
    cprint("📊 TEST SUMMARY", "cyan", attrs=['bold'])
    cprint(f"{'='*60}", "cyan", attrs=['bold'])

    success_count = sum(1 for _, success, _ in results if success)
    total_count = len(results)

    for model_name, success, info in results:
        status = "✅ PASS" if success else "❌ FAIL"
        color = "green" if success else "red"
        cprint(f"{status} - {model_name}", color)

    cprint(f"\n🎯 Results: {success_count}/{total_count} models working",
           "green" if success_count == total_count else "yellow", attrs=['bold'])

    if success_count == total_count:
        cprint(f"\n🎉 All OpenRouter models tested successfully!", "green", attrs=['bold'])
        cprint(f"💡 You now have access to 200+ models with one API key!", "cyan")
        return True
    elif success_count > 0:
        cprint(f"\n⚠️ Some models working, check errors above", "yellow", attrs=['bold'])
        return True
    else:
        cprint(f"\n❌ No models working - check API key and credits", "red", attrs=['bold'])
        return False

if __name__ == "__main__":
    try:
        success = test_openrouter()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        cprint("\n\n👋 Test interrupted by user", "yellow")
        sys.exit(1)
    except Exception as e:
        cprint(f"\n❌ Fatal error: {str(e)}", "red", attrs=['bold'])
        import traceback
        traceback.print_exc()
        sys.exit(1)

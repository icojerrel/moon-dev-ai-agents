#!/usr/bin/env python3
"""
🌙 Simple OpenRouter Test
Direct test without model factory dependencies
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

# Load .env
load_dotenv()

def test_openrouter_direct():
    """Direct test of OpenRouter API"""

    print("\n" + "="*60)
    print("🌙 Moon Dev's OpenRouter Connection Test")
    print("="*60 + "\n")

    # Get API key
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("❌ OPENROUTER_API_KEY not found in .env!")
        return False

    print(f"✅ API Key found: {api_key[:20]}...")

    # Test models
    test_models = [
        ("google/gemini-2.5-flash", "Gemini 2.5 Flash"),
        ("qwen/qwen3-vl-32b-instruct", "Qwen 3 VL 32B"),
        ("anthropic/claude-3-5-haiku", "Claude 3.5 Haiku")
    ]

    results = []

    for model_name, description in test_models:
        print(f"\n{'='*60}")
        print(f"🧪 Testing: {description}")
        print(f"📝 Model: {model_name}")
        print(f"{'='*60}")

        try:
            # Create OpenAI client with OpenRouter
            client = OpenAI(
                api_key=api_key,
                base_url="https://openrouter.ai/api/v1",
                default_headers={
                    "HTTP-Referer": "https://moon.dev",
                    "X-Title": "Moon Dev Trading Bot"
                }
            )

            print("💬 Sending test query...")

            # Make request
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "What is 2+2? Answer in one short sentence."}
                ],
                max_tokens=100,
                temperature=0.7
            )

            if response and response.choices:
                answer = response.choices[0].message.content
                print(f"\n✅ SUCCESS!")
                print(f"📨 Response: {answer}")

                # Show usage
                if hasattr(response, 'usage'):
                    print(f"📊 Tokens used: {response.usage.total_tokens}")

                results.append((model_name, True, answer[:100]))
            else:
                print("❌ Empty response")
                results.append((model_name, False, "Empty response"))

        except Exception as e:
            error_msg = str(e)
            print(f"\n❌ ERROR: {error_msg}")
            results.append((model_name, False, error_msg[:100]))

    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")

    success_count = sum(1 for _, success, _ in results if success)
    total_count = len(results)

    for model_name, success, info in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {model_name}")
        if not success:
            print(f"   Error: {info}")

    print(f"\n🎯 Results: {success_count}/{total_count} models working")

    if success_count == total_count:
        print("\n🎉 All OpenRouter models tested successfully!")
        print("💡 You now have access to 200+ models with one API key!")
        return True
    elif success_count > 0:
        print("\n⚠️ Some models working")
        return True
    else:
        print("\n❌ No models working - check API key and credits")
        print("💡 Get your key at: https://openrouter.ai/keys")
        print("💡 Add credits at: https://openrouter.ai/credits")
        return False

if __name__ == "__main__":
    try:
        success = test_openrouter_direct()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted")
        exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)

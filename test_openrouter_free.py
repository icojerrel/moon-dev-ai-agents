#!/usr/bin/env python3
"""
🌙 OpenRouter Free Model Test
Test with free models to check if it's a credit issue
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def test_free_models():
    """Test with free/cheap models"""

    print("\n" + "="*60)
    print("🌙 Testing OpenRouter with Free Models")
    print("="*60 + "\n")

    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("❌ No API key found")
        return False

    print(f"✅ API Key: {api_key[:25]}...\n")

    # Test with auto-routing (OpenRouter picks best available)
    test_models = [
        ("openrouter/auto", "Auto-route (OpenRouter picks best available)")
    ]

    for model_name, description in test_models:
        print(f"🧪 Testing: {description}")
        print(f"📝 Model: {model_name}\n")

        try:
            client = OpenAI(
                api_key=api_key,
                base_url="https://openrouter.ai/api/v1",
                default_headers={
                    "HTTP-Referer": "https://moon.dev",
                    "X-Title": "Moon Dev Trading Bot"
                }
            )

            print("💬 Sending request...")

            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "user", "content": "Hi, just testing. Reply with 'OK'."}
                ],
                max_tokens=50
            )

            if response and response.choices:
                answer = response.choices[0].message.content
                print(f"✅ SUCCESS!")
                print(f"📨 Response: {answer}\n")

                # Check what model was actually used
                if hasattr(response, 'model'):
                    print(f"🤖 Model used: {response.model}")

                if hasattr(response, 'usage'):
                    print(f"📊 Tokens: {response.usage.total_tokens}")

                return True

        except Exception as e:
            error_msg = str(e)
            print(f"❌ ERROR: {error_msg}\n")

            # Check for specific error types
            if "insufficient" in error_msg.lower() or "credit" in error_msg.lower():
                print("💡 This appears to be a credits/billing issue")
                print("   Add credits at: https://openrouter.ai/credits")
            elif "access denied" in error_msg.lower() or "401" in error_msg:
                print("💡 This appears to be an authentication issue")
                print("   Check your API key at: https://openrouter.ai/keys")
                print(f"   Current key format: {api_key[:10]}...{api_key[-10:]}")
            elif "403" in error_msg:
                print("💡 This appears to be a permissions issue")
                print("   Your key might not have access to these models")

            return False

    return False

if __name__ == "__main__":
    success = test_free_models()

    if not success:
        print("\n" + "="*60)
        print("📋 TROUBLESHOOTING STEPS")
        print("="*60)
        print("\n1. Check API key is correct:")
        print("   Visit: https://openrouter.ai/keys")
        print("\n2. Check credits balance:")
        print("   Visit: https://openrouter.ai/credits")
        print("\n3. Verify API key permissions:")
        print("   Some keys may have model restrictions")
        print("\n4. Test in OpenRouter playground:")
        print("   Visit: https://openrouter.ai/playground")

    exit(0 if success else 1)

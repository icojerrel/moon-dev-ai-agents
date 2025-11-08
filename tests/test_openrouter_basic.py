"""
🧪 Basic OpenRouter Connection Test
Test if OpenRouter API works with DeepSeek V3
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from dotenv import load_dotenv
from openai import OpenAI

def test_openrouter_basic():
    """Test basic OpenRouter connection"""

    print("🧪 Testing OpenRouter Basic Connection...\n")

    # Step 1: Load environment
    print("1. Loading environment...")
    load_dotenv(project_root / '.env')

    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("   ❌ OPENROUTER_API_KEY not found in .env")
        return False

    print(f"   ✅ OPENROUTER_API_KEY found ({len(api_key)} chars)")
    print()

    # Step 2: Test OpenRouter
    print("2. Testing OpenRouter with DeepSeek V3...")
    print("   📡 Sending request...")

    try:
        client = OpenAI(
            api_key=api_key,
            base_url='https://openrouter.ai/api/v1',
            default_headers={
                'HTTP-Referer': 'https://moon.dev',
                'X-Title': 'Moon Dev Trading Bot'
            }
        )

        response = client.chat.completions.create(
            model='deepseek/deepseek-chat-v3-0324',
            messages=[
                {
                    'role': 'system',
                    'content': 'You are a helpful trading assistant.'
                },
                {
                    'role': 'user',
                    'content': 'Say a friendly hello in one sentence.'
                }
            ],
            max_tokens=50
        )

        print("   ✅ Response received!")
        print()

        content = response.choices[0].message.content
        model = response.model
        tokens = response.usage.total_tokens if hasattr(response, 'usage') else 'N/A'

        print(f"   AI said: \"{content}\"")
        print()
        print(f"   Model: {model}")
        print(f"   Tokens used: ~{tokens}")
        print()

        print("🎉 SUCCESS! OpenRouter + DeepSeek V3 works perfectly!")
        return True

    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        print()
        print("Troubleshooting:")
        print("  1. Check .env - is OPENROUTER_API_KEY correct?")
        print("  2. Check https://openrouter.ai/credits - credits available?")
        print("  3. Check https://openrouter.ai/keys - key active?")
        print()
        return False

if __name__ == "__main__":
    success = test_openrouter_basic()
    sys.exit(0 if success else 1)

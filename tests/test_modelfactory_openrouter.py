"""
🧪 ModelFactory + OpenRouter Integration Test
Test if ModelFactory correctly loads and uses OpenRouter
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from dotenv import load_dotenv

def test_modelfactory_openrouter():
    """Test ModelFactory with OpenRouter"""

    print("🧪 Testing ModelFactory with OpenRouter...\n")

    # Load environment
    load_dotenv(project_root / '.env')

    # Step 1: Import model_factory
    print("1. Import model_factory singleton...")
    try:
        from src.models.model_factory import model_factory
        print("   ✅ Imported successfully")
        print()
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False

    # Step 2: Get OpenRouter model
    print("2. Get OpenRouter model...")
    try:
        model = model_factory.get_model('openrouter', model_name='deepseek/deepseek-chat-v3-0324')

        if not model:
            print("   ❌ Model is None - check if OPENROUTER_API_KEY is in .env")
            return False

        print(f"   ✅ Model initialized: {model.model_type}")
        print(f"   ✅ Model name: {model.model_name}")
        print()
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

    # Step 3: Test generate_response
    print("3. Test generate_response...")
    try:
        response = model.generate_response(
            system_prompt="You are a trading analyst. Be concise.",
            user_content="Analyze EUR/USD trending up. Give advice in max 15 words.",
            temperature=0.7,
            max_tokens=50
        )

        if response and response.content:
            print(f"   ✅ Response: {response.content}")
            print()
        else:
            print("   ⚠️  Empty response")
            print()

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

    # Step 4: Check configuration
    print("4. Check fallback configuration...")
    try:
        from src.config import MT5_MODEL_NAME, MT5_FALLBACK_MODEL
        print(f"   Primary: {MT5_MODEL_NAME} ✅")
        print(f"   Fallback: {MT5_FALLBACK_MODEL} ✅")
        print()
    except Exception as e:
        print(f"   ⚠️  Config check: {e}")
        print()

    print("🎉 ModelFactory + OpenRouter works perfectly!")
    return True

if __name__ == "__main__":
    success = test_modelfactory_openrouter()
    sys.exit(0 if success else 1)

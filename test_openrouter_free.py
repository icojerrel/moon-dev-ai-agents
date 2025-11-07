#!/usr/bin/env python
"""
Test OpenRouter with a free model
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.models.model_factory import ModelFactory
from dotenv import load_dotenv

# Load environment
load_dotenv()

print("\n" + "="*80)
print("OpenRouter Free Model Test")
print("="*80 + "\n")

# Test idea
test_idea = "Explain the concept of trend following in 2 sentences."

print("Test Prompt:", test_idea)
print("\n" + "="*80)

# Initialize model factory
print("\n🔧 Initializing Model Factory...")
factory = ModelFactory()

# Try different free models on OpenRouter
free_models = [
    "meta-llama/llama-3.2-3b-instruct:free",
    "google/gemma-2-9b-it:free",
    "qwen/qwen-2-7b-instruct:free",
    "mistralai/mistral-7b-instruct:free"
]

for model_name in free_models:
    print(f"\n{'='*80}")
    print(f"Testing: {model_name}")
    print("="*80)

    try:
        # Get OpenAI model (which will use OpenRouter via base_url)
        model = factory.get_model("openai", model_name)

        if not model:
            print(f"❌ Failed to get model!")
            continue

        print(f"✅ Model obtained: {model.model_name}")

        # Test generation
        print("\n🤖 Testing response generation...")
        response = model.generate_response(
            system_prompt="You are a helpful assistant.",
            user_content=test_idea,
            temperature=0.7,
            max_tokens=100
        )

        print("\n" + "="*80)
        print("Response:")
        print("="*80)
        if hasattr(response, 'content'):
            print(response.content)
        else:
            print(response)
        print("="*80)
        print(f"\n✅ SUCCESS with {model_name}!")
        break

    except Exception as e:
        print(f"\n❌ FAILED with {model_name}: {str(e)}")
        continue

else:
    print("\n❌ All models failed. API key might be invalid.")
    print("\n💡 Troubleshooting:")
    print("  1. Check if API key is valid on OpenRouter dashboard")
    print("  2. Verify API key has credits/permissions")
    print("  3. Try visiting https://openrouter.ai/keys to check key status")

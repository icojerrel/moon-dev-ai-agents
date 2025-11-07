#!/usr/bin/env python
"""
Quick test of OpenRouter integration
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
print("OpenRouter Integration Test")
print("="*80 + "\n")

# Test idea
test_idea = """
NQ 9am Hour Continuation Strategy: Trade in direction of 9am hour close (9:30am-10:30am EST).
If 9am hour closes green, go long with 67% probability entire session closes green.
"""

print("Test Idea:")
print(test_idea)
print("\n" + "="*80)

# Initialize model factory
print("\n🔧 Initializing Model Factory...")
factory = ModelFactory()

# Get OpenAI model (which will use OpenRouter via base_url)
print("\n🔧 Getting OpenAI model...")
model = factory.get_model("openai", "qwen/qwen-2.5-coder-32b-instruct")

if not model:
    print("❌ Failed to get model!")
    sys.exit(1)

print(f"✅ Model obtained: {model.model_name}")

# Test generation
print("\n🤖 Testing response generation...")
system_prompt = "You are a trading strategy analyzer. Summarize the given strategy in 2-3 sentences."
user_content = f"Strategy: {test_idea}"

try:
    response = model.generate_response(
        system_prompt=system_prompt,
        user_content=user_content,
        temperature=0.7,
        max_tokens=200
    )

    print("\n" + "="*80)
    print("Response:")
    print("="*80)
    if hasattr(response, 'content'):
        print(response.content)
    else:
        print(response)
    print("="*80)
    print("\n✅ OpenRouter integration test PASSED!")

except Exception as e:
    print(f"\n❌ Test FAILED: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

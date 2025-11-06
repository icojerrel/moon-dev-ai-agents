#!/usr/bin/env python3
"""Simple OpenRouter test without full dependencies"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    print("❌ No OpenRouter key found")
    exit(1)

print(f"✅ Found key: {api_key[:20]}...")

client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1"
)

print("🧪 Testing deepseek/deepseek-r1...")

response = client.chat.completions.create(
    model="deepseek/deepseek-r1",
    messages=[
        {"role": "system", "content": "You are a helpful assistant. Be concise."},
        {"role": "user", "content": "Say 'OpenRouter works!' and tell me one fact about trading in one sentence."}
    ],
    temperature=0.7,
    max_tokens=100
)

print(f"✅ Response: {response.choices[0].message.content}")
print(f"💰 Tokens: {response.usage}")
print("\n🎉 OpenRouter integration works!")

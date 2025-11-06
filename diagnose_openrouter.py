#!/usr/bin/env python3
"""
🔍 OpenRouter API Key Diagnostic Tool

Tests if your OpenRouter account is properly configured.
"""

import os
import requests
import json
from termcolor import cprint
from dotenv import load_dotenv

load_dotenv()

def diagnose_openrouter():
    """Comprehensive OpenRouter diagnostics"""

    cprint("\n" + "="*70, "cyan")
    cprint("🔍 OPENROUTER API KEY DIAGNOSTICS", "white", "on_blue")
    cprint("="*70, "cyan")

    # Get API key
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        cprint("\n❌ OPENROUTER_API_KEY not found in .env", "red")
        return False

    cprint(f"\n✅ API Key found", "green")
    cprint(f"   Length: {len(api_key)} chars", "cyan")
    cprint(f"   Format: {api_key[:10]}...{api_key[-10:]}", "cyan")

    # Test 1: Check auth endpoint
    cprint("\n" + "-"*70, "yellow")
    cprint("TEST 1: Checking API Key Status", "yellow")
    cprint("-"*70, "yellow")

    try:
        response = requests.get(
            "https://openrouter.ai/api/v1/auth/key",
            headers={"Authorization": f"Bearer {api_key}"}
        )

        cprint(f"Status Code: {response.status_code}", "cyan")

        if response.status_code == 200:
            cprint("✅ API key is valid!", "green")
            data = response.json()
            cprint(f"Response: {json.dumps(data, indent=2)}", "cyan")
        elif response.status_code == 403:
            cprint("❌ 403 FORBIDDEN - Account has restrictions", "red")
            cprint("\n🔧 FIXES NEEDED:", "yellow")
            cprint("  1. Verify email op openrouter.ai", "yellow")
            cprint("  2. Add payment method (Settings > Billing)", "yellow")
            cprint("  3. Check account status (Settings)", "yellow")
            cprint("  4. Check API key permissions (Keys page)", "yellow")
        elif response.status_code == 401:
            cprint("❌ 401 UNAUTHORIZED - Invalid API key", "red")
            cprint("  Get new key at: https://openrouter.ai/keys", "yellow")
        else:
            cprint(f"⚠️  Unexpected status: {response.status_code}", "yellow")
            cprint(f"Response: {response.text}", "cyan")

    except Exception as e:
        cprint(f"❌ Error: {str(e)}", "red")

    # Test 2: Try cheapest model
    cprint("\n" + "-"*70, "yellow")
    cprint("TEST 2: Testing with GPT-4o Mini (cheapest)", "yellow")
    cprint("-"*70, "yellow")

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/moondevonyt/moon-dev-ai-agents",
                "X-Title": "Moon Dev AI Agents"
            },
            data=json.dumps({
                "model": "openai/gpt-4o-mini",
                "messages": [{"role": "user", "content": "Say 'OK'"}],
                "max_tokens": 5
            })
        )

        cprint(f"Status Code: {response.status_code}", "cyan")

        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            cprint(f"✅ SUCCESS! Response: {content}", "green")

            usage = result.get('usage', {})
            cprint(f"\n💰 Usage:", "yellow")
            cprint(f"   Input tokens: {usage.get('prompt_tokens', 0)}", "yellow")
            cprint(f"   Output tokens: {usage.get('completion_tokens', 0)}", "yellow")
            cprint(f"   Total: {usage.get('total_tokens', 0)}", "yellow")

            return True

        elif response.status_code == 403:
            cprint("❌ 403 FORBIDDEN", "red")
            cprint(f"Response: {response.text}", "red")
            cprint("\n⚠️  Account needs configuration - zie CHECK_OPENROUTER_ACCOUNT.md", "yellow")

        elif response.status_code == 402:
            cprint("❌ 402 PAYMENT REQUIRED - Insufficient credits", "red")
            cprint("   Add credits at: https://openrouter.ai/credits", "yellow")

        else:
            cprint(f"⚠️  Status: {response.status_code}", "yellow")
            cprint(f"Response: {response.text}", "cyan")

    except Exception as e:
        cprint(f"❌ Error: {str(e)}", "red")

    # Test 3: Try another cheap model
    cprint("\n" + "-"*70, "yellow")
    cprint("TEST 3: Testing with DeepSeek Chat (also cheap)", "yellow")
    cprint("-"*70, "yellow")

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/moondevonyt/moon-dev-ai-agents",
                "X-Title": "Moon Dev AI Agents"
            },
            data=json.dumps({
                "model": "deepseek/deepseek-chat",
                "messages": [{"role": "user", "content": "Say 'OK'"}],
                "max_tokens": 5
            })
        )

        cprint(f"Status Code: {response.status_code}", "cyan")

        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            cprint(f"✅ SUCCESS! Response: {content}", "green")
            return True
        else:
            cprint(f"Status: {response.status_code}", "yellow")
            cprint(f"Response: {response.text[:100]}", "cyan")

    except Exception as e:
        cprint(f"❌ Error: {str(e)}", "red")

    # Summary
    cprint("\n" + "="*70, "cyan")
    cprint("📋 SUMMARY", "white", "on_red")
    cprint("="*70, "cyan")

    cprint("\n❌ All tests failed with 403 Forbidden", "red")
    cprint("\n🔧 ACTION REQUIRED:", "yellow")
    cprint("   1. Open: https://openrouter.ai/settings", "white")
    cprint("   2. Verify email address", "white")
    cprint("   3. Add payment method (even with credits)", "white")
    cprint("   4. Check API key permissions: https://openrouter.ai/keys", "white")
    cprint("   5. Verify credits: https://openrouter.ai/credits", "white")

    cprint("\n📖 Detailed guide: CHECK_OPENROUTER_ACCOUNT.md", "cyan")

    return False

if __name__ == "__main__":
    success = diagnose_openrouter()

    if success:
        cprint("\n🎉 OpenRouter is working! Run test scripts:", "green")
        cprint("   python3 test_openrouter_simple.py", "cyan")
        cprint("   python3 test_kimi_model.py", "cyan")
    else:
        cprint("\n⚠️  Fix account issues first, then run this again", "yellow")

#!/usr/bin/env python3
"""
🌙 Moon Dev API Connectivity Tester with Smart Retry Logic
Tests API connections to verify keys and connectivity
Enhanced with automatic retry for transient failures
"""

import os
import sys
from pathlib import Path
import time

# Try to import colored output
try:
    from termcolor import cprint
except ImportError:
    def cprint(text, color=None, on_color=None, attrs=None):
        print(text)

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

# Load environment
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    cprint("⚠️  python-dotenv not installed", "yellow")

# Try to import our error handling utilities
try:
    from utils.error_handling import retry_on_error, RetryConfig
    RETRY_AVAILABLE = True
    cprint("✨ Enhanced with smart retry logic", "green")
except ImportError:
    RETRY_AVAILABLE = False
    # Fallback: simple retry decorator
    def retry_on_error(max_retries=3, delay_seconds=2, backoff=2, exceptions=(Exception,), on_retry=None):
        """Fallback retry decorator if utils not available"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                last_exception = None
                for attempt in range(max_retries):
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        last_exception = e
                        if attempt < max_retries - 1:
                            wait_time = delay_seconds * (backoff ** attempt)
                            cprint(f"  ⚠️  Attempt {attempt + 1} failed, retrying in {wait_time}s...", "yellow")
                            time.sleep(wait_time)
                        else:
                            raise
                if last_exception:
                    raise last_exception
            return wrapper
        return decorator


@retry_on_error(max_retries=3, delay_seconds=2, backoff=1.5)
def test_anthropic():
    """Test Anthropic (Claude) API with automatic retry"""
    cprint("\n🔍 Testing Anthropic API...", "cyan")

    api_key = os.getenv('ANTHROPIC_KEY')
    if not api_key:
        cprint("  ⏭️  ANTHROPIC_KEY not configured - skipping", "yellow")
        return None

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)

        # Simple test message
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=10,
            messages=[{"role": "user", "content": "Say OK"}]
        )

        cprint("  ✅ Anthropic API working", "green")
        cprint(f"  Response: {response.content[0].text}", "white")
        return True

    except ImportError:
        cprint("  ❌ anthropic package not installed", "red")
        return False
    except Exception as e:
        cprint(f"  ❌ Error: {str(e)}", "red")
        return False


@retry_on_error(max_retries=3, delay_seconds=2, backoff=1.5)
def test_openai():
    """Test OpenAI API with automatic retry"""
    cprint("\n🔍 Testing OpenAI API...", "cyan")

    api_key = os.getenv('OPENAI_KEY')
    if not api_key:
        cprint("  ⏭️  OPENAI_KEY not configured - skipping", "yellow")
        return None

    try:
        import openai
        client = openai.OpenAI(api_key=api_key)

        # Simple test
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            max_tokens=10,
            messages=[{"role": "user", "content": "Say OK"}]
        )

        cprint("  ✅ OpenAI API working", "green")
        cprint(f"  Response: {response.choices[0].message.content}", "white")
        return True

    except ImportError:
        cprint("  ❌ openai package not installed", "red")
        return False
    except Exception as e:
        cprint(f"  ❌ Error: {str(e)}", "red")
        return False


@retry_on_error(max_retries=3, delay_seconds=2, backoff=1.5)
def test_groq():
    """Test Groq API with automatic retry"""
    cprint("\n🔍 Testing Groq API...", "cyan")

    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        cprint("  ⏭️  GROQ_API_KEY not configured - skipping", "yellow")
        return None

    try:
        from groq import Groq
        client = Groq(api_key=api_key)

        # Simple test
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=10,
            messages=[{"role": "user", "content": "Say OK"}]
        )

        cprint("  ✅ Groq API working", "green")
        cprint(f"  Response: {response.choices[0].message.content}", "white")
        return True

    except ImportError:
        cprint("  ❌ groq package not installed", "red")
        return False
    except Exception as e:
        cprint(f"  ❌ Error: {str(e)}", "red")
        return False


@retry_on_error(max_retries=3, delay_seconds=2, backoff=1.5)
def test_birdeye():
    """Test BirdEye API with automatic retry"""
    cprint("\n🔍 Testing BirdEye API...", "cyan")

    api_key = os.getenv('BIRDEYE_API_KEY')
    if not api_key:
        cprint("  ⏭️  BIRDEYE_API_KEY not configured - skipping", "yellow")
        return None

    try:
        import requests

        # Test with simple token list request
        url = "https://public-api.birdeye.so/public/tokenlist"
        headers = {"X-API-KEY": api_key}

        response = requests.get(url, headers=headers, params={"sort_by": "v24hUSD", "sort_type": "desc", "offset": 0, "limit": 1})

        if response.status_code == 200:
            cprint("  ✅ BirdEye API working", "green")
            data = response.json()
            if data.get('data') and len(data['data']) > 0:
                token = data['data'][0]
                cprint(f"  Sample token: {token.get('symbol', 'N/A')}", "white")
            return True
        else:
            cprint(f"  ❌ Error: HTTP {response.status_code}", "red")
            return False

    except ImportError:
        cprint("  ❌ requests package not installed", "red")
        return False
    except Exception as e:
        cprint(f"  ❌ Error: {str(e)}", "red")
        return False


@retry_on_error(max_retries=3, delay_seconds=2, backoff=1.5)
def test_rpc():
    """Test Solana RPC endpoint with automatic retry"""
    cprint("\n🔍 Testing Solana RPC...", "cyan")

    rpc_endpoint = os.getenv('RPC_ENDPOINT')
    if not rpc_endpoint:
        cprint("  ⏭️  RPC_ENDPOINT not configured - skipping", "yellow")
        return None

    try:
        import requests

        # Test health endpoint
        response = requests.post(
            rpc_endpoint,
            json={"jsonrpc": "2.0", "id": 1, "method": "getHealth"},
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data.get('result') == 'ok' or 'error' not in data:
                cprint("  ✅ Solana RPC working", "green")
                return True
            else:
                cprint(f"  ❌ RPC returned error: {data.get('error')}", "red")
                return False
        else:
            cprint(f"  ❌ Error: HTTP {response.status_code}", "red")
            return False

    except ImportError:
        cprint("  ❌ requests package not installed", "red")
        return False
    except Exception as e:
        cprint(f"  ❌ Error: {str(e)}", "red")
        return False


@retry_on_error(max_retries=3, delay_seconds=2, backoff=1.5)
def test_coingecko():
    """Test CoinGecko API with automatic retry"""
    cprint("\n🔍 Testing CoinGecko API...", "cyan")

    api_key = os.getenv('COINGECKO_API_KEY')

    try:
        import requests

        # Test with simple ping (works without API key)
        url = "https://api.coingecko.com/api/v3/ping"
        headers = {}
        if api_key:
            headers['x-cg-api-key'] = api_key

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            cprint("  ✅ CoinGecko API working", "green")
            if not api_key:
                cprint("  ℹ️  Using public API (rate limited)", "white")
            return True
        else:
            cprint(f"  ❌ Error: HTTP {response.status_code}", "red")
            return False

    except ImportError:
        cprint("  ❌ requests package not installed", "red")
        return False
    except Exception as e:
        cprint(f"  ❌ Error: {str(e)}", "red")
        return False


def main():
    """Run all API tests"""
    cprint("\n" + "="*60, "cyan")
    cprint("🌙 Moon Dev API Connectivity Tester", "cyan", attrs=['bold'])
    cprint("="*60 + "\n", "cyan")

    results = {
        'Anthropic (Claude)': test_anthropic(),
        'OpenAI': test_openai(),
        'Groq': test_groq(),
        'BirdEye': test_birdeye(),
        'Solana RPC': test_rpc(),
        'CoinGecko': test_coingecko(),
    }

    # Summary
    cprint("\n" + "="*60, "cyan")
    cprint("📊 Test Summary", "cyan", attrs=['bold'])
    cprint("="*60, "cyan")

    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)

    for service, result in results.items():
        if result is True:
            status = "✅ PASS"
            color = "green"
        elif result is False:
            status = "❌ FAIL"
            color = "red"
        else:
            status = "⏭️  SKIP"
            color = "yellow"

        cprint(f"  {service}: {status}", color)

    cprint("\n" + "="*60, "cyan")
    cprint(f"Passed: {passed} | Failed: {failed} | Skipped: {skipped}", "white")
    cprint("="*60 + "\n", "cyan")

    if failed > 0:
        cprint("⚠️  Some API tests failed. Check API keys and connectivity.", "yellow")
        cprint("💡 See TROUBLESHOOTING.md for help", "cyan")
        return 1
    elif passed == 0:
        cprint("⚠️  No APIs configured. Add API keys to .env file.", "yellow")
        cprint("💡 See SETUP.md for configuration instructions", "cyan")
        return 1
    else:
        cprint("✅ All configured APIs are working!", "green")
        return 0


if __name__ == "__main__":
    sys.exit(main())

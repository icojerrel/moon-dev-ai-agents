"""
🌙 Moon Dev's MT5 Setup Tester
Test your complete setup without actually trading
"""

import os
import sys
from termcolor import cprint
from dotenv import load_dotenv

# Load environment
load_dotenv()

def print_section(title):
    """Print section header"""
    cprint(f"\n{'='*60}", "cyan")
    cprint(f"  {title}", "cyan", attrs=["bold"])
    cprint(f"{'='*60}", "cyan")

def check_env_var(var_name, required=True):
    """Check if environment variable is set"""
    value = os.getenv(var_name)
    if value and len(value.strip()) > 0:
        cprint(f"✅ {var_name}: Found ({len(value)} chars)", "green")
        return True
    else:
        if required:
            cprint(f"❌ {var_name}: Not found or empty", "red")
        else:
            cprint(f"⚠️ {var_name}: Not found (optional)", "yellow")
        return False

def test_mt5_library():
    """Test if MT5 library can be imported"""
    print_section("1. Testing MetaTrader5 Library")

    try:
        import MetaTrader5 as mt5
        cprint(f"✅ MetaTrader5 library installed (v{mt5.__version__})", "green")
        return True
    except ImportError:
        cprint("❌ MetaTrader5 library not installed", "red")
        cprint("   Install: pip install MetaTrader5", "yellow")
        cprint("   Note: Only works on Windows!", "yellow")
        return False

def test_dependencies():
    """Test if required dependencies are installed"""
    print_section("2. Testing Dependencies")

    required = {
        'pandas': 'pandas',
        'pandas_ta': 'pandas-ta',
        'termcolor': 'termcolor',
        'dotenv': 'python-dotenv',
    }

    all_ok = True
    for module_name, package_name in required.items():
        try:
            __import__(module_name.replace('_', '.') if '_' in module_name else module_name)
            cprint(f"✅ {package_name}: Installed", "green")
        except ImportError:
            cprint(f"❌ {package_name}: Not installed", "red")
            cprint(f"   Install: pip install {package_name}", "yellow")
            all_ok = False

    return all_ok

def test_env_config():
    """Test environment configuration"""
    print_section("3. Testing Environment Configuration")

    cprint("\nMT5 Credentials:", "cyan")
    mt5_ok = True
    mt5_ok &= check_env_var("MT5_LOGIN")
    mt5_ok &= check_env_var("MT5_PASSWORD")
    mt5_ok &= check_env_var("MT5_SERVER")
    check_env_var("MT5_PATH", required=False)

    cprint("\nAI API Keys:", "cyan")
    openrouter_ok = check_env_var("OPENROUTER_API_KEY")

    cprint("\nOptional AI Keys:", "cyan")
    check_env_var("GROK_API_KEY", required=False)
    check_env_var("GROQ_API_KEY", required=False)
    check_env_var("OPENAI_KEY", required=False)
    check_env_var("ANTHROPIC_KEY", required=False)

    return mt5_ok and openrouter_ok

def test_openrouter():
    """Test OpenRouter connection"""
    print_section("4. Testing OpenRouter Connection")

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        cprint("❌ OPENROUTER_API_KEY not set, skipping test", "red")
        return False

    try:
        cprint("🔄 Testing OpenRouter API...", "cyan")

        # Add project root to path
        project_root = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, project_root)

        from src.models.openrouter_model import OpenRouterModel

        model = OpenRouterModel(
            api_key=api_key,
            model_name="anthropic/claude-3-haiku"  # Cheapest for testing
        )

        if not model.is_available():
            cprint("❌ OpenRouter model not available", "red")
            return False

        cprint("✅ OpenRouter client initialized", "green")

        # Test with a simple request
        cprint("🔄 Testing API request...", "cyan")
        response = model.generate_response(
            system_prompt="You are a helpful assistant.",
            user_content="Say 'Hello Moon Dev' in one sentence.",
            max_tokens=50
        )

        if response and response.content:
            cprint(f"✅ OpenRouter API works!", "green")
            cprint(f"   Response: {response.content[:100]}...", "yellow")
            return True
        else:
            cprint("❌ OpenRouter returned empty response", "red")
            return False

    except Exception as e:
        cprint(f"❌ OpenRouter test failed: {str(e)}", "red")

        error_str = str(e).lower()
        if "insufficient credits" in error_str or "quota" in error_str:
            cprint("💳 Add credits at: https://openrouter.ai/credits", "yellow")
        elif "unauthorized" in error_str or "authentication" in error_str:
            cprint("🔑 Check your API key at: https://openrouter.ai/keys", "yellow")

        return False

def test_ollama():
    """Test Ollama connection"""
    print_section("5. Testing Ollama (Local Fallback)")

    try:
        cprint("🔄 Testing Ollama connection...", "cyan")

        # Add project root to path
        project_root = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, project_root)

        from src.models.ollama_model import OllamaModel

        model = OllamaModel(
            api_key="not-needed",
            model_name="llama3.2"
        )

        if not model.is_available():
            cprint("❌ Ollama not available", "red")
            cprint("   Make sure Ollama is running:", "yellow")
            cprint("   - Windows: Check system tray for Ollama", "yellow")
            cprint("   - Or run: ollama serve", "yellow")
            return False

        cprint("✅ Ollama server is running", "green")

        # Test with a simple request
        cprint("🔄 Testing Ollama model...", "cyan")
        response = model.generate_response(
            system_prompt="You are a helpful assistant.",
            user_content="Say 'Hello Moon Dev' in one sentence.",
            max_tokens=50
        )

        if response and response.content:
            cprint(f"✅ Ollama works!", "green")
            cprint(f"   Model: llama3.2", "yellow")
            cprint(f"   Response: {response.content[:100]}...", "yellow")
            return True
        else:
            cprint("❌ Ollama returned empty response", "red")
            cprint("   Make sure model is pulled: ollama pull llama3.2", "yellow")
            return False

    except Exception as e:
        cprint(f"❌ Ollama test failed: {str(e)}", "red")
        cprint("   Install Ollama: https://ollama.com/download", "yellow")
        cprint("   Then run: ollama pull llama3.2", "yellow")
        return False

def test_fallback():
    """Test fallback system"""
    print_section("6. Testing OpenRouter → Ollama Fallback")

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        cprint("⚠️ OPENROUTER_API_KEY not set, skipping fallback test", "yellow")
        return False

    try:
        cprint("🔄 Creating fallback model...", "cyan")

        # Add project root to path
        project_root = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, project_root)

        from src.models.fallback_model import create_openrouter_ollama_fallback

        model = create_openrouter_ollama_fallback(
            openrouter_api_key=api_key,
            openrouter_model="anthropic/claude-3-haiku",
            ollama_model="llama3.2"
        )

        cprint("✅ Fallback model created", "green")

        # Test request
        cprint("🔄 Testing fallback request...", "cyan")
        response = model.generate_response(
            system_prompt="You are a trading assistant.",
            user_content="What is RSI? One sentence.",
            max_tokens=50
        )

        if response and response.content:
            cprint(f"✅ Fallback system works!", "green")
            cprint(f"   Used model: {response.model_name}", "yellow")

            # Print statistics
            model.print_statistics()
            return True
        else:
            cprint("❌ Fallback returned empty response", "red")
            return False

    except Exception as e:
        cprint(f"❌ Fallback test failed: {str(e)}", "red")
        return False

def test_config():
    """Test configuration"""
    print_section("7. Testing Configuration")

    try:
        project_root = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, project_root)

        from src.config import (
            AI_USE_FALLBACK, AI_PRIMARY_TYPE, AI_PRIMARY_MODEL,
            AI_FALLBACK_TYPE, AI_FALLBACK_MODEL,
            MT5_ENABLED, MT5_SYMBOLS, MT5_LOT_SIZE
        )

        cprint(f"✅ Configuration loaded", "green")
        cprint(f"\nAI Configuration:", "cyan")
        cprint(f"   Fallback Enabled: {AI_USE_FALLBACK}", "yellow")
        cprint(f"   Primary: {AI_PRIMARY_TYPE} ({AI_PRIMARY_MODEL})", "yellow")
        cprint(f"   Fallback: {AI_FALLBACK_TYPE} ({AI_FALLBACK_MODEL})", "yellow")

        cprint(f"\nMT5 Configuration:", "cyan")
        cprint(f"   Enabled: {MT5_ENABLED}", "yellow")
        cprint(f"   Symbols: {', '.join(MT5_SYMBOLS[:3])}...", "yellow")
        cprint(f"   Lot Size: {MT5_LOT_SIZE}", "yellow")

        return True

    except Exception as e:
        cprint(f"❌ Config test failed: {str(e)}", "red")
        return False

def main():
    """Run all tests"""
    cprint("\n" + "="*60, "cyan", attrs=["bold"])
    cprint("  🌙 Moon Dev's MT5 Setup Tester", "cyan", attrs=["bold"])
    cprint("="*60 + "\n", "cyan", attrs=["bold"])

    results = {}

    # Run tests
    results['MT5 Library'] = test_mt5_library()
    results['Dependencies'] = test_dependencies()
    results['Environment'] = test_env_config()
    results['Configuration'] = test_config()
    results['OpenRouter'] = test_openrouter()
    results['Ollama'] = test_ollama()
    results['Fallback'] = test_fallback()

    # Summary
    print_section("TEST SUMMARY")

    total = len(results)
    passed = sum(1 for v in results.values() if v)

    for test_name, result in results.items():
        if result:
            cprint(f"✅ {test_name}", "green")
        else:
            cprint(f"❌ {test_name}", "red")

    cprint(f"\n{'='*60}", "cyan")
    cprint(f"  Results: {passed}/{total} tests passed", "cyan", attrs=["bold"])
    cprint(f"{'='*60}\n", "cyan")

    if passed == total:
        cprint("🎉 ALL TESTS PASSED! Ready to trade! 🚀", "green", attrs=["bold"])
        cprint("\nNext step:", "cyan")
        cprint("  start_mt5_trading.bat", "yellow", attrs=["bold"])
    elif passed >= total - 2:
        cprint("⚠️ MOSTLY READY - Fix remaining issues and you're good to go!", "yellow", attrs=["bold"])
    else:
        cprint("❌ SETUP INCOMPLETE - Please fix the issues above", "red", attrs=["bold"])
        cprint("\nQuick fixes:", "cyan")

        if not results['Environment']:
            cprint("  1. Run: create_env_file.bat", "yellow")
            cprint("  2. Add your OPENROUTER_API_KEY", "yellow")

        if not results['Ollama']:
            cprint("  1. Download: https://ollama.com/download", "yellow")
            cprint("  2. Run: ollama pull llama3.2", "yellow")

        if not results['MT5 Library']:
            cprint("  1. Windows only! Run: pip install MetaTrader5", "yellow")

    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        cprint("\n\n👋 Test cancelled by user", "yellow")
        sys.exit(1)
    except Exception as e:
        cprint(f"\n\n❌ Unexpected error: {str(e)}", "red")
        import traceback
        traceback.print_exc()
        sys.exit(1)

#!/usr/bin/env python3
"""
🌙 Moon Dev Configuration Validator
Validates config.py settings and environment variables before running agents
"""

import os
import sys
from pathlib import Path

# Try to import termcolor, fallback to regular print
try:
    from termcolor import cprint
except ImportError:
    def cprint(text, color=None, on_color=None, attrs=None):
        """Fallback if termcolor not installed"""
        print(text)

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

def validate_environment_variables():
    """Check for required environment variables"""
    cprint("\n🔍 Checking Environment Variables...", "cyan")

    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        cprint("\n⚠️  python-dotenv not installed - skipping .env file loading", "yellow")
        cprint("   Install with: pip install python-dotenv", "yellow")

    # Critical keys
    critical = {
        'ANTHROPIC_KEY': 'Claude AI (or use another AI provider)',
        'BIRDEYE_API_KEY': 'Solana market data',
        'RPC_ENDPOINT': 'Solana blockchain access',
    }

    # Optional but important
    optional = {
        'OPENAI_KEY': 'OpenAI GPT models',
        'DEEPSEEK_KEY': 'DeepSeek models (cost-effective)',
        'GROQ_API_KEY': 'Groq fast inference',
        'GEMINI_KEY': 'Google Gemini (currently disabled)',
        'MOONDEV_API_KEY': 'Moon Dev custom API',
        'COINGECKO_API_KEY': 'Token metadata',
        'SOLANA_PRIVATE_KEY': '⚠️  Trading wallet (required for live trading)',
    }

    missing_critical = []
    missing_optional = []
    found = []

    # Check critical
    for key, purpose in critical.items():
        value = os.getenv(key)
        if value:
            found.append(f"  ✅ {key}: {purpose}")
        else:
            missing_critical.append(f"  ❌ {key}: {purpose}")

    # Check optional
    for key, purpose in optional.items():
        value = os.getenv(key)
        if value:
            found.append(f"  ✅ {key}: {purpose}")
        else:
            missing_optional.append(f"  ⚠️  {key}: {purpose}")

    # Display results
    if found:
        cprint("\n✅ Found Environment Variables:", "green")
        for item in found:
            cprint(item, "green")

    if missing_critical:
        cprint("\n❌ Missing CRITICAL Variables:", "red")
        for item in missing_critical:
            cprint(item, "red")
        cprint("\n💡 At least ONE AI provider key is required (Anthropic, OpenAI, DeepSeek, or Groq)", "yellow")

    if missing_optional:
        cprint("\n⚠️  Missing OPTIONAL Variables:", "yellow")
        for item in missing_optional:
            cprint(item, "yellow")

    # Check if at least one AI provider exists
    ai_providers = ['ANTHROPIC_KEY', 'OPENAI_KEY', 'DEEPSEEK_KEY', 'GROQ_API_KEY']
    has_ai = any(os.getenv(key) for key in ai_providers)

    if not has_ai:
        cprint("\n🚨 ERROR: No AI provider configured!", "red")
        cprint("   Add at least one of: ANTHROPIC_KEY, OPENAI_KEY, DEEPSEEK_KEY, GROQ_API_KEY", "red")
        return False

    cprint(f"\n✅ Environment variables check: {'PASS' if not missing_critical else 'WARNING'}", "green" if not missing_critical else "yellow")
    return True


def validate_config():
    """Validate config.py settings"""
    cprint("\n🔍 Checking Configuration Settings...", "cyan")

    try:
        import config

        issues = []
        warnings = []

        # Check for negative balances that should be negative
        if config.MAX_LOSS_USD > 0:
            warnings.append("⚠️  MAX_LOSS_USD should typically be negative (e.g., -25)")

        # Check percentage ranges
        if not (0 <= config.CASH_PERCENTAGE <= 100):
            issues.append("❌ CASH_PERCENTAGE must be between 0-100")

        if not (0 <= config.MAX_POSITION_PERCENTAGE <= 100):
            issues.append("❌ MAX_POSITION_PERCENTAGE must be between 0-100")

        # Check reasonable position sizing
        if config.usd_size > 1000:
            warnings.append(f"⚠️  usd_size is ${config.usd_size} - consider starting smaller for testing")

        if config.max_usd_order_size > config.usd_size:
            warnings.append(f"⚠️  max_usd_order_size (${config.max_usd_order_size}) is greater than usd_size (${config.usd_size})")

        # Check AI settings
        if not (0 <= config.AI_TEMPERATURE <= 1):
            issues.append("❌ AI_TEMPERATURE must be between 0-1")

        if config.AI_MAX_TOKENS < 100:
            warnings.append(f"⚠️  AI_MAX_TOKENS ({config.AI_MAX_TOKENS}) seems very low")

        # Check sleep settings
        if config.SLEEP_BETWEEN_RUNS_MINUTES < 1:
            warnings.append("⚠️  SLEEP_BETWEEN_RUNS_MINUTES < 1 may cause rate limiting")

        # Check monitored tokens
        if len(config.MONITORED_TOKENS) == 0:
            warnings.append("⚠️  No tokens in MONITORED_TOKENS list")

        if len(config.MONITORED_TOKENS) > 20:
            warnings.append(f"⚠️  {len(config.MONITORED_TOKENS)} tokens monitored - may be slow")

        # Display results
        if issues:
            cprint("\n❌ Configuration Issues:", "red")
            for issue in issues:
                cprint(f"  {issue}", "red")

        if warnings:
            cprint("\n⚠️  Configuration Warnings:", "yellow")
            for warning in warnings:
                cprint(f"  {warning}", "yellow")

        if not issues and not warnings:
            cprint("\n✅ Configuration looks good!", "green")

        # Display key settings
        cprint("\n📊 Current Configuration:", "cyan")
        cprint(f"  Position Size: ${config.usd_size}", "white")
        cprint(f"  Max Order Size: ${config.max_usd_order_size}", "white")
        cprint(f"  Monitored Tokens: {len(config.MONITORED_TOKENS)}", "white")
        cprint(f"  AI Model: {config.AI_MODEL}", "white")
        cprint(f"  Sleep Between Runs: {config.SLEEP_BETWEEN_RUNS_MINUTES} min", "white")
        cprint(f"  Max Loss: ${config.MAX_LOSS_USD}", "white")
        cprint(f"  Max Gain: ${config.MAX_GAIN_USD}", "white")

        cprint(f"\n✅ Config validation: {'PASS' if not issues else 'FAILED'}", "green" if not issues else "red")
        return len(issues) == 0

    except Exception as e:
        cprint(f"\n❌ Error loading config: {str(e)}", "red")
        return False


def validate_dependencies():
    """Check if required Python packages are installed"""
    cprint("\n🔍 Checking Python Dependencies...", "cyan")

    required = {
        'anthropic': 'Claude AI',
        'openai': 'OpenAI GPT',
        'pandas': 'Data handling',
        'numpy': 'Numerical operations',
        'requests': 'API calls',
        'termcolor': 'Colored output',
        'dotenv': 'Environment variables',
    }

    optional = {
        'groq': 'Groq fast inference',
        # 'google.generativeai': 'Gemini (disabled)',
        'cv2': 'OpenCV for video',
        'whisper': 'Audio transcription',
    }

    missing_required = []
    missing_optional = []
    found = []

    # Check required
    for package, purpose in required.items():
        try:
            if package == 'dotenv':
                __import__('dotenv')
            else:
                __import__(package)
            found.append(f"  ✅ {package}: {purpose}")
        except ImportError:
            missing_required.append(f"  ❌ {package}: {purpose}")

    # Check optional
    for package, purpose in optional.items():
        try:
            __import__(package)
            found.append(f"  ✅ {package}: {purpose}")
        except ImportError:
            missing_optional.append(f"  ⚠️  {package}: {purpose}")

    # Display results
    if found:
        cprint("\n✅ Installed Packages:", "green")
        for item in found[:10]:  # Show first 10
            cprint(item, "green")
        if len(found) > 10:
            cprint(f"  ... and {len(found) - 10} more", "green")

    if missing_required:
        cprint("\n❌ Missing REQUIRED Packages:", "red")
        for item in missing_required:
            cprint(item, "red")
        cprint("\n💡 Install with: pip install -r requirements.txt", "yellow")

    if missing_optional:
        cprint("\n⚠️  Missing OPTIONAL Packages:", "yellow")
        for item in missing_optional:
            cprint(item, "yellow")

    cprint(f"\n✅ Dependencies check: {'PASS' if not missing_required else 'FAILED'}", "green" if not missing_required else "red")
    return len(missing_required) == 0


def validate_file_structure():
    """Check if required files and directories exist"""
    cprint("\n🔍 Checking File Structure...", "cyan")

    required_files = [
        'src/config.py',
        'src/main.py',
        'src/nice_funcs.py',
        '.env_example',
        'requirements.txt',
    ]

    required_dirs = [
        'src/agents',
        'src/models',
        'src/strategies',
        'src/data',
    ]

    missing_files = []
    missing_dirs = []
    found = []

    # Check files
    for filepath in required_files:
        path = project_root / filepath
        if path.exists():
            found.append(f"  ✅ {filepath}")
        else:
            missing_files.append(f"  ❌ {filepath}")

    # Check directories
    for dirpath in required_dirs:
        path = project_root / dirpath
        if path.exists():
            found.append(f"  ✅ {dirpath}/")
        else:
            missing_dirs.append(f"  ❌ {dirpath}/")

    # Display results
    if found:
        cprint("\n✅ Found Files/Directories:", "green")
        for item in found:
            cprint(item, "green")

    if missing_files or missing_dirs:
        cprint("\n❌ Missing Files/Directories:", "red")
        for item in missing_files + missing_dirs:
            cprint(item, "red")

    # Check .env
    env_file = project_root / '.env'
    if env_file.exists():
        cprint("\n✅ .env file exists", "green")
    else:
        cprint("\n⚠️  .env file NOT found", "yellow")
        cprint("   Copy .env_example to .env and add your API keys", "yellow")

    cprint(f"\n✅ File structure check: {'PASS' if not (missing_files or missing_dirs) else 'FAILED'}",
           "green" if not (missing_files or missing_dirs) else "red")
    return len(missing_files) == 0 and len(missing_dirs) == 0


def validate_performance():
    """Check performance utilities and cache system"""
    cprint("\n🚀 Checking Performance Infrastructure...", "cyan")

    checks_passed = True

    # Check if cache utilities are available
    try:
        from utils.cache_manager import (
            market_data_cache,
            token_metadata_cache,
            ohlcv_cache,
            wallet_cache,
            print_all_cache_stats
        )
        cprint("  ✅ Cache system available", "green")

        # Show cache configurations
        caches = {
            'Market Data': market_data_cache,
            'Token Metadata': token_metadata_cache,
            'OHLCV Data': ohlcv_cache,
            'Wallet/Position': wallet_cache
        }

        cprint("\n  📊 Cache Configurations:", "cyan")
        for name, cache in caches.items():
            stats = cache.get_stats()
            ttl = int(stats['ttl_minutes']) if hasattr(cache, 'default_ttl') else 'N/A'
            cprint(f"    • {name}: TTL={cache.default_ttl.total_seconds()/60:.0f}min, Entries={stats['entries']}, Hit Rate={stats['hit_rate']}", "white")

    except ImportError as e:
        cprint(f"  ⚠️  Cache utilities not available: {e}", "yellow")
        cprint("    Cache system is optional but recommended for performance", "yellow")

    # Check if error handling utilities are available
    try:
        from utils.error_handling import (
            retry_on_error,
            safe_api_call,
            RetryConfig
        )
        cprint("  ✅ Error handling utilities available", "green")
        cprint("    • Retry decorators: Available", "white")
        cprint("    • Safe API calls: Available", "white")
        cprint("    • Pre-configured profiles: Available", "white")

    except ImportError:
        cprint("  ⚠️  Error handling utilities not available", "yellow")
        cprint("    These utilities are optional but improve reliability", "yellow")

    # Performance utilities are optional, so we always pass
    cprint("\n✅ Performance infrastructure check complete", "green")
    cprint("   (Note: Performance utilities are optional enhancements)", "cyan")
    return True


def main():
    """Run all validations"""
    cprint("\n" + "="*60, "cyan")
    cprint("🌙 Moon Dev Configuration Validator", "cyan", attrs=['bold'])
    cprint("="*60 + "\n", "cyan")

    results = {
        'File Structure': validate_file_structure(),
        'Dependencies': validate_dependencies(),
        'Environment Variables': validate_environment_variables(),
        'Configuration': validate_config(),
        'Performance Infrastructure': validate_performance(),
    }

    # Summary
    cprint("\n" + "="*60, "cyan")
    cprint("📊 Validation Summary", "cyan", attrs=['bold'])
    cprint("="*60, "cyan")

    all_passed = True
    for check, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        color = "green" if passed else "red"
        cprint(f"  {check}: {status}", color)
        if not passed:
            all_passed = False

    cprint("\n" + "="*60, "cyan")

    if all_passed:
        cprint("✅ All checks passed! Ready to run agents.", "green", attrs=['bold'])
        cprint("\n💡 Start with: python src/main.py", "cyan")
        return 0
    else:
        cprint("⚠️  Some checks failed. Please review above.", "yellow", attrs=['bold'])
        cprint("\n💡 See SETUP.md and TROUBLESHOOTING.md for help", "cyan")
        return 1


if __name__ == "__main__":
    sys.exit(main())

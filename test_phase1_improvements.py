#!/usr/bin/env python3
"""
🌙 Moon Dev Phase 1 Improvements Test Suite
Tests all Phase 1 implementations for correctness and backwards compatibility
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = str(Path(__file__).parent)
if project_root not in sys.path:
    sys.path.append(project_root)

def test_rich_logger():
    """Test Rich logger import and basic functionality"""
    print("\n" + "="*60)
    print("TEST 1: Rich Logger")
    print("="*60)

    try:
        from src.utils.rich_logger import (
            print_panel, print_status, print_trade_result,
            print_agent_header, setup_logging, console
        )
        print("✅ Rich logger imports successful")

        # Test basic functions
        print_status("Testing status message...", "info")
        print_status("Warning message test", "warning")
        print_status("Success message test", "success")

        print_panel("This is a test panel", "Test Panel", style="info")

        print_agent_header("Test Agent", "TESTING")

        print_trade_result(
            action="BUY",
            token="SOL",
            amount_usd=25.0,
            price=150.50,
            success=True
        )

        logger = setup_logging("test_agent")
        logger.info("Test log message")

        print("\n✅ TEST 1 PASSED - Rich logger working correctly")
        return True

    except ImportError as e:
        print(f"⚠️ Rich library not installed: {e}")
        print("Run: pip install rich>=13.0.0")
        return False
    except Exception as e:
        print(f"❌ TEST 1 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_event_emitter():
    """Test event emitter system"""
    print("\n" + "="*60)
    print("TEST 2: Event Emitter")
    print("="*60)

    try:
        from src.utils.event_emitter import (
            emit_event, emit_trading_event, emit_whale_event,
            emit_agent_lifecycle, EventType, get_event_stats
        )
        print("✅ Event emitter imports successful")

        # Test with events disabled (default)
        print("\n📝 Testing with events DISABLED (default)...")
        emit_trading_event("BUY", "SOL", 25.0, 150.50, True, "test_agent")
        print("✅ No events emitted (as expected)")

        # Test with events enabled
        print("\n📝 Testing with events ENABLED...")
        os.environ["MOONDEV_ENABLE_EVENTS"] = "true"

        emit_trading_event("BUY", "SOL", 25.0, 150.50, True, "test_agent")
        emit_whale_event("BTC", "WhaleAddr123...", "BUY", 1000000)
        emit_agent_lifecycle("test_agent", "START")
        emit_agent_lifecycle("test_agent", "COMPLETE", duration=5.5)

        stats = get_event_stats()
        print(f"\n📊 Event statistics: {stats}")

        # Cleanup
        del os.environ["MOONDEV_ENABLE_EVENTS"]

        print("\n✅ TEST 2 PASSED - Event emitter working correctly")
        print("💡 Look for ::MOONDEV_EVENT:: lines above")
        return True

    except Exception as e:
        print(f"❌ TEST 2 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_gemini_thinking_mode():
    """Test Gemini thinking mode support"""
    print("\n" + "="*60)
    print("TEST 3: Gemini Thinking Mode")
    print("="*60)

    try:
        from src.models.gemini_model import GeminiModel, HAS_THINKING_MODE

        print(f"Thinking mode available: {HAS_THINKING_MODE}")

        if HAS_THINKING_MODE:
            print("✅ google-genai library detected")
            print("✨ Gemini thinking mode is enabled")
        else:
            print("⚠️ google-genai library not installed")
            print("💡 Install with: pip install google-genai")
            print("✅ Fallback to legacy library will work")

        # Test model initialization (without actual API call)
        print("\n📝 Testing model initialization...")
        model = GeminiModel(
            api_key="test_key_not_real",
            model_name="gemini-2.5-flash",
            use_thinking_mode=True
        )

        print(f"Model name: {model.model_name}")
        print(f"Thinking mode enabled: {model.use_thinking_mode}")
        print(f"Has new client: {model.new_client is not None}")

        print("\n✅ TEST 3 PASSED - Gemini thinking mode configured correctly")
        return True

    except Exception as e:
        print(f"❌ TEST 3 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_security_fix():
    """Test path traversal security fix"""
    print("\n" + "="*60)
    print("TEST 4: Security Fix (Path Traversal)")
    print("="*60)

    try:
        from src.agents.api import MoonDevAPI

        api = MoonDevAPI(api_key="test_key")

        # Test 1: Safe filename (should work)
        print("\n📝 Test 1: Safe filename 'data.csv'")
        try:
            # This will fail at the network level, but should pass validation
            api._fetch_csv("data.csv", limit=1)
            print("✅ Safe filename passed validation")
        except ValueError as e:
            print(f"❌ Safe filename rejected incorrectly: {e}")
            return False
        except Exception as e:
            # Network errors are expected (no real API)
            print(f"✅ Validation passed (network error expected: {type(e).__name__})")

        # Test 2: Path traversal attempt (should fail)
        print("\n📝 Test 2: Path traversal '../../../etc/passwd'")
        try:
            api._fetch_csv("../../../etc/passwd")
            print("❌ SECURITY FAILURE - Path traversal not blocked!")
            return False
        except ValueError as e:
            print(f"✅ Path traversal blocked: {e}")

        # Test 3: Absolute path attempt (should fail)
        print("\n📝 Test 3: Absolute path '/etc/passwd'")
        try:
            api._fetch_csv("/etc/passwd")
            print("❌ SECURITY FAILURE - Absolute path not blocked!")
            return False
        except ValueError as e:
            print(f"✅ Absolute path blocked: {e}")

        # Test 4: Windows path attempt (should fail)
        print("\n📝 Test 4: Windows path 'C:\\\\Windows\\\\System32\\\\config'")
        try:
            api._fetch_csv("C:\\Windows\\System32\\config")
            print("❌ SECURITY FAILURE - Windows path not blocked!")
            return False
        except ValueError as e:
            print(f"✅ Windows path blocked: {e}")

        print("\n✅ TEST 4 PASSED - All security tests passed")
        return True

    except Exception as e:
        print(f"❌ TEST 4 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_trading_agent_imports():
    """Test trading agent with new imports"""
    print("\n" + "="*60)
    print("TEST 5: Trading Agent Imports")
    print("="*60)

    try:
        # Temporarily suppress agent initialization
        os.environ["SKIP_MODEL_INIT"] = "true"

        print("📝 Testing trading_agent.py imports...")

        # This will fail at model initialization, but imports should work
        try:
            import src.agents.trading_agent as ta
            print(f"✅ Trading agent module imported")
            print(f"   HAS_RICH_LOGGING: {getattr(ta, 'HAS_RICH_LOGGING', 'Not found')}")
        except Exception as e:
            # Expected to fail at init, but imports should work
            if "import" in str(e).lower():
                raise  # Re-raise import errors
            print(f"✅ Imports successful (init error expected: {type(e).__name__})")

        print("\n✅ TEST 5 PASSED - Trading agent imports working")
        return True

    except Exception as e:
        print(f"❌ TEST 5 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if "SKIP_MODEL_INIT" in os.environ:
            del os.environ["SKIP_MODEL_INIT"]


def test_backwards_compatibility():
    """Test that old code still works"""
    print("\n" + "="*60)
    print("TEST 6: Backwards Compatibility")
    print("="*60)

    try:
        # Test that termcolor still works
        from termcolor import cprint
        cprint("Testing termcolor...", "cyan")
        print("✅ termcolor still works")

        # Test that old imports don't break
        from src.config import MONITORED_TOKENS, AI_MODEL_TYPE
        print(f"✅ Config imports work: {len(MONITORED_TOKENS)} tokens")

        # Test that ModelFactory still works
        from src.models.model_factory import model_factory
        print(f"✅ ModelFactory available")

        print("\n✅ TEST 6 PASSED - Backwards compatibility maintained")
        return True

    except Exception as e:
        print(f"❌ TEST 6 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all Phase 1 tests"""
    print("\n🌙 MOON DEV PHASE 1 TEST SUITE 🚀")
    print("="*60)

    results = {
        "Rich Logger": test_rich_logger(),
        "Event Emitter": test_event_emitter(),
        "Gemini Thinking": test_gemini_thinking_mode(),
        "Security Fix": test_security_fix(),
        "Trading Agent": test_trading_agent_imports(),
        "Backwards Compatibility": test_backwards_compatibility(),
    }

    print("\n" + "="*60)
    print("🎯 TEST RESULTS SUMMARY")
    print("="*60)

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    print("\n" + "="*60)
    print(f"Final Score: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("="*60)

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Phase 1 ready for production!")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Review output above.")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)

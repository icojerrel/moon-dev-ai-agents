#!/usr/bin/env python3
"""
🧪 Test MT5 Integration
Quick test to verify MT5 paper trading setup
"""

import sys
from pathlib import Path
from termcolor import cprint

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_imports():
    """Test that all imports work"""
    cprint("\n📦 Testing imports...", "cyan")

    try:
        from src.mt5.mt5_connection import MT5Connection
        cprint("  ✅ MT5Connection imported", "green")
    except Exception as e:
        cprint(f"  ❌ MT5Connection import failed: {e}", "red")
        return False

    try:
        from src.models.model_factory import ModelFactory
        cprint("  ✅ ModelFactory imported", "green")
    except Exception as e:
        cprint(f"  ❌ ModelFactory import failed: {e}", "red")
        return False

    return True


def test_mt5_connection():
    """Test MT5 connection in paper trading mode"""
    cprint("\n🔌 Testing MT5 connection...", "cyan")

    try:
        from src.mt5.mt5_connection import MT5Connection

        # Create paper trading connection
        mt5 = MT5Connection(paper_trading=True, virtual_balance=10000)
        cprint("  ✅ MT5Connection created", "green")

        # Connect
        if not mt5.connect():
            cprint("  ❌ Connection failed", "red")
            return False
        cprint("  ✅ Connected (paper mode)", "green")

        # Get account info
        account = mt5.get_account_info()
        cprint(f"  ✅ Account balance: ${account['balance']:,.2f}", "green")

        # Get symbol info
        symbol_info = mt5.get_symbol_info("EURUSD")
        if symbol_info:
            cprint(f"  ✅ Symbol info retrieved: {symbol_info['symbol']}", "green")

        # Test opening position
        result = mt5.open_position(
            symbol="EURUSD",
            order_type="BUY",
            volume=0.01,
            comment="Test trade"
        )

        if result['success']:
            cprint(f"  ✅ Paper position opened: Ticket {result['ticket']}", "green")

            # Get positions
            positions = mt5.get_positions()
            cprint(f"  ✅ Open positions: {len(positions)}", "green")

            # Close position
            close_result = mt5.close_position(result['ticket'])
            if close_result['success']:
                cprint(f"  ✅ Position closed: P/L ${close_result['profit']:,.2f}", "green")
        else:
            cprint(f"  ❌ Failed to open position: {result.get('error')}", "red")
            return False

        mt5.disconnect()
        cprint("  ✅ Disconnected", "green")

        return True

    except Exception as e:
        cprint(f"  ❌ Test failed: {e}", "red")
        import traceback
        traceback.print_exc()
        return False


def test_model_factory():
    """Test ModelFactory with Ollama"""
    cprint("\n🤖 Testing ModelFactory...", "cyan")

    try:
        from src.models.model_factory import ModelFactory

        factory = ModelFactory()
        cprint("  ✅ ModelFactory initialized", "green")

        if factory.is_model_available("ollama"):
            cprint("  ✅ Ollama is available", "green")

            model = factory.get_model("ollama")
            cprint(f"  ✅ Model loaded: {model.model_name}", "green")

            # Quick test
            response = model.generate_response(
                system_prompt="You are a helpful assistant.",
                user_content="Say 'Hello from MT5 test!' in one line.",
                temperature=0.5,
                max_tokens=50
            )

            if response:
                cprint(f"  ✅ Model response: {response.content[:50]}...", "green")
                return True
        else:
            cprint("  ⚠️  Ollama not available (run 'ollama serve')", "yellow")
            cprint("     MT5 agent will not work without Ollama", "yellow")
            return False

    except Exception as e:
        cprint(f"  ❌ Test failed: {e}", "red")
        return False


def test_full_workflow():
    """Test complete workflow (without running full agent)"""
    cprint("\n🔄 Testing full workflow...", "cyan")

    try:
        from src.mt5.mt5_connection import MT5Connection
        from src.models.model_factory import ModelFactory
        import pandas as pd
        from datetime import datetime, timedelta

        # Initialize
        mt5 = MT5Connection(paper_trading=True, virtual_balance=10000)
        factory = ModelFactory()

        if not mt5.connect():
            cprint("  ❌ MT5 connection failed", "red")
            return False

        if not factory.is_model_available("ollama"):
            cprint("  ⚠️  Ollama not available - skipping AI test", "yellow")
            mt5.disconnect()
            return False

        model = factory.get_model("ollama")

        # Create mock candlestick data
        dates = pd.date_range(end=datetime.now(), periods=20, freq='H')
        mock_data = pd.DataFrame({
            'datetime': dates,
            'Open': [1.0840 + (i * 0.0001) for i in range(20)],
            'High': [1.0850 + (i * 0.0001) for i in range(20)],
            'Low': [1.0830 + (i * 0.0001) for i in range(20)],
            'Close': [1.0845 + (i * 0.0001) for i in range(20)],
            'Volume': [100] * 20
        })

        cprint("  ✅ Mock market data created", "green")

        # Prepare prompt (simplified version of what agent does)
        system_prompt = """You are a forex trading analyst.
Analyze the data and provide decision in this format:

DECISION: BUY|SELL|HOLD
CONFIDENCE: 0-100
REASONING: [Brief explanation]
"""

        user_content = f"""Symbol: EURUSD
Current Price: 1.08450

Recent candles show upward trend.

Provide trading decision:"""

        cprint("  ⏱️  Asking AI for trading decision...", "yellow")

        response = model.generate_response(
            system_prompt=system_prompt,
            user_content=user_content,
            temperature=0.3,
            max_tokens=200
        )

        cprint(f"  ✅ AI response received:", "green")
        cprint(f"     {response.content[:100]}...", "white")

        # Test trade execution (paper mode)
        result = mt5.open_position(
            symbol="EURUSD",
            order_type="BUY",
            volume=0.01,
            sl=1.0820,
            tp=1.0880,
            comment="AI test trade"
        )

        if result['success']:
            cprint(f"  ✅ Test trade executed: Ticket {result['ticket']}", "green")
            mt5.close_position(result['ticket'])
            cprint("  ✅ Test trade closed", "green")

        mt5.disconnect()

        return True

    except Exception as e:
        cprint(f"  ❌ Workflow test failed: {e}", "red")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    cprint("\n" + "="*70, "cyan", attrs=["bold"])
    cprint("  🧪 MT5 Integration Test Suite", "cyan", attrs=["bold"])
    cprint("="*70 + "\n", "cyan")

    results = []

    # Test 1: Imports
    results.append(("Imports", test_imports()))

    # Test 2: MT5 Connection
    results.append(("MT5 Connection", test_mt5_connection()))

    # Test 3: Model Factory
    results.append(("Model Factory", test_model_factory()))

    # Test 4: Full Workflow
    results.append(("Full Workflow", test_full_workflow()))

    # Summary
    cprint("\n" + "="*70, "cyan")
    cprint("  📊 Test Results", "cyan", attrs=["bold"])
    cprint("="*70 + "\n", "cyan")

    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        color = "green" if passed else "red"
        cprint(f"  {name:20} {status}", color)

    all_passed = all(result[1] for result in results)

    cprint("\n" + "="*70, "cyan")
    if all_passed:
        cprint("  🎉 ALL TESTS PASSED!", "green", attrs=["bold"])
        cprint("  Ready to run: python src/agents/mt5_agent.py", "green")
    else:
        cprint("  ⚠️  SOME TESTS FAILED", "yellow", attrs=["bold"])
        cprint("  Check errors above and fix before running MT5 agent", "yellow")
    cprint("="*70 + "\n", "cyan")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        cprint("\n\n⏸️  Tests stopped by user", "yellow")
        sys.exit(0)
    except Exception as e:
        cprint(f"\n❌ Fatal error: {e}", "red")
        import traceback
        traceback.print_exc()
        sys.exit(1)

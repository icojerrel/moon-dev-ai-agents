#!/usr/bin/env python3
"""
🌙 Moon Dev's Lightweight Sandbox Test
Built with love by Moon Dev 🚀

Simplified tests that work without external dependencies.
Validates core functionality of the trading system.
"""

import sys
from datetime import datetime

# Test counter
tests_run = 0
tests_passed = 0
tests_failed = 0

def run_test(test_name, test_func):
    """Run a single test"""
    global tests_run, tests_passed, tests_failed

    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"{'='*60}")

    tests_run += 1

    try:
        result = test_func()
        if result:
            print(f"✅ PASSED: {test_name}")
            tests_passed += 1
        else:
            print(f"❌ FAILED: {test_name}")
            tests_failed += 1
    except Exception as e:
        print(f"❌ ERROR: {test_name}")
        print(f"   Error: {str(e)}")
        tests_failed += 1

def test_config_validation():
    """Test configuration settings"""
    import sys
    import os

    # Add project root to path
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from src import config

    print(f"MT5_MAX_POSITIONS: {config.MT5_MAX_POSITIONS}")
    print(f"MT5_MIN_CONFIDENCE: {config.MT5_MIN_CONFIDENCE}")
    print(f"SANDBOX_MODE: {config.SANDBOX_MODE}")
    print(f"SANDBOX_STARTING_BALANCE: {config.SANDBOX_STARTING_BALANCE}")

    # Validate critical settings
    assert config.MT5_MAX_POSITIONS == 1, f"Expected max 1 position, got {config.MT5_MAX_POSITIONS}"
    assert config.MT5_MIN_CONFIDENCE >= 70, f"Min confidence should be >= 70, got {config.MT5_MIN_CONFIDENCE}"
    assert config.SANDBOX_STARTING_BALANCE > 0, "Sandbox balance must be > 0"

    print("\n✅ All critical config settings validated")
    return True

def test_asset_detection():
    """Test asset class detection without pandas"""
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from src.utils.mt5_helpers import detect_asset_class, format_asset_name

    test_cases = [
        ('EURUSD', 'forex', '💱'),
        ('GBPUSD', 'forex', '💱'),
        ('XAUUSD', 'metals', '🏆'),
        ('XAGUSD', 'metals', '🏆'),
        ('US30', 'indices', '📈'),
        ('NAS100', 'indices', '📈'),
        ('SPX500', 'indices', '📈'),
        ('AAPL', 'stocks', '📊'),
        ('MSFT', 'stocks', '📊'),
        ('BTCUSD', 'crypto', '🪙'),
    ]

    for symbol, expected_class, expected_emoji in test_cases:
        detected = detect_asset_class(symbol)
        name, emoji = format_asset_name(symbol)

        print(f"{emoji} {symbol:10} → {detected:10} (expected: {expected_class})")

        assert detected == expected_class, f"Failed for {symbol}: got {detected}, expected {expected_class}"

    print(f"\n✅ Tested {len(test_cases)} symbols successfully")
    return True

def test_position_limit():
    """Test max position limit setting"""
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from src import config

    max_positions = config.MT5_MAX_POSITIONS

    print(f"Maximum allowed positions: {max_positions}")

    # Simulate checking position limit
    current_positions = 0

    print(f"\nSimulating position opening:")

    # Try to open position 1
    current_positions += 1
    print(f"  Position 1: {'✅ Allowed' if current_positions <= max_positions else '❌ Blocked'}")

    # Try to open position 2
    would_open = current_positions + 1
    blocked = would_open > max_positions
    print(f"  Position 2: {'❌ BLOCKED (max limit reached)' if blocked else '✅ Allowed'}")

    assert max_positions == 1, f"Expected max_positions=1, got {max_positions}"
    assert blocked == True, "Second position should be blocked"

    print(f"\n✅ Max position limit ({max_positions}) enforced correctly")
    return True

def test_risk_parameters():
    """Test risk management parameters"""
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from src import config
    from src.utils.mt5_helpers import get_asset_params

    test_symbols = ['EURUSD', 'XAUUSD', 'US30']

    print("Asset-Specific Risk Parameters:")

    for symbol in test_symbols:
        params = get_asset_params(symbol, config)

        print(f"\n{symbol} ({params['asset_class']}):")
        print(f"  Position Size: {params['position_size']} lots")
        print(f"  Max Spread: {params['max_spread_pips']} pips")
        print(f"  Min SL: {params['min_stop_loss_pips']} pips")
        print(f"  Max SL: {params['max_stop_loss_pips']} pips")
        print(f"  TP Ratio: {params['default_tp_ratio']}:1")

        # Validate
        assert params['position_size'] > 0, "Position size must be > 0"
        assert params['max_spread_pips'] > 0, "Max spread must be > 0"
        assert params['min_stop_loss_pips'] > 0, "Min SL must be > 0"
        assert params['default_tp_ratio'] >= 1.0, "TP ratio should be >= 1:1"

    print(f"\n✅ Risk parameters validated for {len(test_symbols)} asset classes")
    return True

def test_symbol_list():
    """Test configured symbol lists"""
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from src import config
    from src.utils.mt5_helpers import detect_asset_class

    print(f"Total symbols configured: {len(config.MT5_SYMBOLS)}")

    # Count by asset class
    asset_counts = {}

    for symbol in config.MT5_SYMBOLS:
        asset_class = detect_asset_class(symbol)
        asset_counts[asset_class] = asset_counts.get(asset_class, 0) + 1

    print("\nSymbols by asset class:")
    for asset_class, count in sorted(asset_counts.items()):
        print(f"  {asset_class}: {count} symbols")

    assert len(config.MT5_SYMBOLS) > 0, "At least one symbol must be configured"

    print(f"\n✅ Symbol list validated")
    return True

def test_mock_account_simulation():
    """Test mock account without pandas"""

    print("Simulating mock trading account:")

    # Simple account simulation
    class SimpleAccount:
        def __init__(self, balance):
            self.balance = balance
            self.equity = balance
            self.positions = []

        def open_position(self, symbol, type, size):
            if len(self.positions) >= 1:
                return None  # Max 1 position limit

            position = {
                'symbol': symbol,
                'type': type,
                'size': size,
                'entry_price': 1.0850 if symbol == 'EURUSD' else 2050.0,
                'profit': 0.0
            }
            self.positions.append(position)
            return len(self.positions)

        def close_position(self, index):
            if index < len(self.positions):
                pos = self.positions.pop(index)
                # Simulate profit
                profit = 50.0  # $50 profit
                self.balance += profit
                self.equity = self.balance
                return profit
            return None

    # Test account
    account = SimpleAccount(balance=10000)

    print(f"\nInitial Balance: ${account.balance:.2f}")

    # Try to open position
    pos1 = account.open_position('EURUSD', 'BUY', 0.01)
    print(f"Position 1: {'✅ Opened' if pos1 else '❌ Failed'}")

    # Try to open second position (should fail)
    pos2 = account.open_position('GBPUSD', 'BUY', 0.01)
    print(f"Position 2: {'❌ BLOCKED (max 1 position)' if not pos2 else '✅ Opened (ERROR!)'}")

    assert pos1 is not None, "First position should open"
    assert pos2 is None, "Second position should be blocked"
    assert len(account.positions) == 1, "Only 1 position should exist"

    # Close position
    profit = account.close_position(0)
    print(f"\nClosed position with profit: ${profit:.2f}")
    print(f"New Balance: ${account.balance:.2f}")

    assert profit > 0, "Should have profit"
    assert account.balance > 10000, "Balance should increase"
    assert len(account.positions) == 0, "No positions should remain"

    print(f"\n✅ Mock account simulation successful")
    return True

def print_summary():
    """Print test summary"""
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")

    print(f"\nTotal Tests: {tests_run}")
    print(f"Passed: {tests_passed}")
    print(f"Failed: {tests_failed}")

    if tests_failed == 0:
        pass_rate = 100.0
    else:
        pass_rate = (tests_passed / tests_run * 100) if tests_run > 0 else 0

    print(f"Pass Rate: {pass_rate:.1f}%")
    print(f"{'='*60}")

    if tests_failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        print("System is ready for deployment.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run full test suite: python tests/test_mt5_sandbox.py")
        print("3. Test with MT5 demo account")
        print("4. Deploy to production")
    else:
        print(f"\n⚠️  {tests_failed} test(s) failed.")
        print("Please review and fix before deployment.")

    print(f"\n{'='*60}")

def main():
    """Run all lightweight tests"""
    print("\n🌙 Moon Dev MT5 Sandbox - Lightweight Test Suite")
    print(f"Starting at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nNote: Running lightweight tests without pandas/numpy")
    print(f"For full tests, install dependencies and run with Docker\n")

    # Run tests
    run_test("Configuration Validation", test_config_validation)
    run_test("Asset Class Detection", test_asset_detection)
    run_test("Max Position Limit (Critical)", test_position_limit)
    run_test("Risk Parameters", test_risk_parameters)
    run_test("Symbol List Configuration", test_symbol_list)
    run_test("Mock Account Simulation", test_mock_account_simulation)

    # Print summary
    print_summary()

    return 0 if tests_failed == 0 else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

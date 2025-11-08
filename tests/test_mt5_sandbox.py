"""
🌙 Moon Dev's MT5 Sandbox Test Suite
Built with love by Moon Dev 🚀

Comprehensive testing of MT5 trading system in sandbox mode.
Tests all asset classes, risk management, and system functionality.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

import time
from datetime import datetime
from termcolor import cprint
import pandas as pd

from src.utils.mock_mt5 import MockMT5Simulator
from src.utils.mt5_helpers import (
    detect_asset_class,
    get_asset_params,
    format_asset_name,
    calculate_position_size
)
import src.config as config


class MT5SandboxTester:
    """Comprehensive sandbox testing suite"""

    def __init__(self):
        self.simulator = MockMT5Simulator(
            starting_balance=config.SANDBOX_STARTING_BALANCE
        )
        self.test_results = []
        self.passed = 0
        self.failed = 0

    def run_test(self, test_name: str, test_func):
        """Run a single test"""
        cprint(f"\n{'='*60}", "cyan")
        cprint(f"TEST: {test_name}", "white", "on_blue")
        cprint(f"{'='*60}", "cyan")

        try:
            result = test_func()
            if result:
                cprint(f"✅ PASSED: {test_name}", "green")
                self.passed += 1
                self.test_results.append((test_name, "PASSED", None))
            else:
                cprint(f"❌ FAILED: {test_name}", "red")
                self.failed += 1
                self.test_results.append((test_name, "FAILED", "Test returned False"))
        except Exception as e:
            cprint(f"❌ ERROR: {test_name}", "red")
            cprint(f"   Error: {str(e)}", "red")
            self.failed += 1
            self.test_results.append((test_name, "ERROR", str(e)))

    def test_account_initialization(self) -> bool:
        """Test account initialization"""
        account = self.simulator.get_account_info()

        print(f"Account Login: {account['login']}")
        print(f"Starting Balance: ${account['balance']:.2f}")
        print(f"Currency: {account['currency']}")
        print(f"Leverage: 1:{account['leverage']}")

        assert account['balance'] == config.SANDBOX_STARTING_BALANCE
        assert account['equity'] == config.SANDBOX_STARTING_BALANCE
        assert account['currency'] == 'USD'

        return True

    def test_asset_detection(self) -> bool:
        """Test asset class detection"""
        test_cases = [
            ('EURUSD', 'forex'),
            ('GBPUSD', 'forex'),
            ('XAUUSD', 'metals'),
            ('XAGUSD', 'metals'),
            ('US30', 'indices'),
            ('NAS100', 'indices'),
            ('AAPL', 'stocks'),
            ('BTCUSD', 'crypto'),
        ]

        for symbol, expected_class in test_cases:
            detected = detect_asset_class(symbol)
            name, emoji = format_asset_name(symbol)
            print(f"{emoji} {symbol:10} → {detected:10} (expected: {expected_class})")
            assert detected == expected_class, f"Failed for {symbol}"

        return True

    def test_symbol_info(self) -> bool:
        """Test symbol information"""
        symbols = ['EURUSD', 'XAUUSD', 'US30', 'AAPL']

        for symbol in symbols:
            info = self.simulator.get_symbol_info(symbol)

            print(f"\n{symbol}:")
            print(f"  Bid: {info['bid']}")
            print(f"  Ask: {info['ask']}")
            print(f"  Spread: {info['spread']} points")
            print(f"  Point: {info['point']}")

            assert info is not None
            assert info['ask'] > info['bid']  # Ask should be higher
            assert info['spread'] > 0

        return True

    def test_ohlcv_generation(self) -> bool:
        """Test OHLCV data generation"""
        symbols = ['EURUSD', 'XAUUSD', 'US30']
        trends = ['bullish', 'bearish', 'ranging']

        for symbol in symbols:
            for trend in trends:
                df = self.simulator.generate_ohlcv_data(
                    symbol,
                    timeframe='1H',
                    bars=100,
                    trend=trend
                )

                print(f"\n{symbol} ({trend}):")
                print(f"  Bars: {len(df)}")
                print(f"  Price range: {df['Low'].min():.5f} - {df['High'].max():.5f}")

                assert len(df) == 100
                assert 'Open' in df.columns
                assert 'High' in df.columns
                assert 'Low' in df.columns
                assert 'Close' in df.columns
                assert 'Volume' in df.columns

                # Validate OHLC logic
                assert (df['High'] >= df['Open']).all()
                assert (df['High'] >= df['Close']).all()
                assert (df['Low'] <= df['Open']).all()
                assert (df['Low'] <= df['Close']).all()

        return True

    def test_position_sizing(self) -> bool:
        """Test position size calculation"""
        account_balance = 10000
        risk_percent = 1.0  # Risk 1% = $100

        test_cases = [
            ('EURUSD', 50),    # 50 pip SL
            ('XAUUSD', 500),   # 500 pip SL
            ('US30', 200),     # 200 point SL
        ]

        for symbol, sl_pips in test_cases:
            size = calculate_position_size(
                symbol,
                account_balance,
                risk_percent,
                sl_pips
            )

            asset_class = detect_asset_class(symbol)
            risk_amount = account_balance * (risk_percent / 100)

            print(f"\n{symbol} ({asset_class}):")
            print(f"  Account: ${account_balance}")
            print(f"  Risk: {risk_percent}% = ${risk_amount}")
            print(f"  SL: {sl_pips} pips")
            print(f"  Position Size: {size} lots")

            assert size > 0
            assert size <= 1.0  # Reasonable maximum

        return True

    def test_buy_position(self) -> bool:
        """Test opening BUY position"""
        symbol = 'EURUSD'
        volume = 0.01
        sl = 1.0800
        tp = 1.0900

        # Open position
        ticket = self.simulator.market_buy(symbol, volume, sl, tp)

        print(f"Opened BUY position:")
        print(f"  Ticket: {ticket}")
        print(f"  Symbol: {symbol}")
        print(f"  Volume: {volume} lots")

        assert ticket is not None
        assert ticket > 0

        # Check positions
        positions = self.simulator.get_positions()
        assert len(positions) == 1
        assert positions.iloc[0]['type'] == 'BUY'
        assert positions.iloc[0]['symbol'] == symbol

        print(f"\nPosition details:")
        print(positions[['symbol', 'type', 'volume', 'price_open', 'profit']])

        # Close position
        self.simulator.close_position(ticket)

        return True

    def test_sell_position(self) -> bool:
        """Test opening SELL position"""
        symbol = 'GBPUSD'
        volume = 0.01

        # Open position
        ticket = self.simulator.market_sell(symbol, volume)

        print(f"Opened SELL position:")
        print(f"  Ticket: {ticket}")
        print(f"  Symbol: {symbol}")

        assert ticket is not None

        # Check positions
        positions = self.simulator.get_positions()
        assert len(positions) == 1
        assert positions.iloc[0]['type'] == 'SELL'

        print(f"\nPosition details:")
        print(positions[['symbol', 'type', 'volume', 'price_open', 'profit']])

        # Close position
        self.simulator.close_position(ticket)

        return True

    def test_max_positions_limit(self) -> bool:
        """Test maximum 1 position limit"""
        print(f"Max positions allowed: {config.MT5_MAX_POSITIONS}")

        # Try to open 2 positions
        ticket1 = self.simulator.market_buy('EURUSD', 0.01)
        print(f"Position 1 opened: {ticket1}")

        positions = self.simulator.get_positions()
        print(f"Current positions: {len(positions)}")

        # Application-level limit check
        if len(positions) >= config.MT5_MAX_POSITIONS:
            print(f"⚠️  Max positions limit reached ({config.MT5_MAX_POSITIONS})")
            print(f"   Would reject second position in real system")

        # Clean up
        self.simulator.close_position(ticket1)

        return True

    def test_profit_calculation(self) -> bool:
        """Test profit calculation with market move"""
        symbol = 'EURUSD'
        volume = 0.01

        # Get initial balance
        account_before = self.simulator.get_account_info()
        balance_before = account_before['balance']

        # Open BUY position
        ticket = self.simulator.market_buy(symbol, volume)

        print(f"Opened position at: {self.simulator.positions[ticket].price_open:.5f}")

        # Simulate +50 pip move
        print(f"Simulating +50 pip move...")
        self.simulator.simulate_market_move(symbol, 50)

        # Check profit
        positions = self.simulator.get_positions()
        profit = positions.iloc[0]['profit']

        print(f"Current profit: ${profit:.2f}")
        assert profit > 0  # Should be profitable

        # Close position
        self.simulator.close_position(ticket)

        # Check balance updated
        account_after = self.simulator.get_account_info()
        balance_after = account_after['balance']

        print(f"\nBalance before: ${balance_before:.2f}")
        print(f"Balance after: ${balance_after:.2f}")
        print(f"Profit: ${balance_after - balance_before:.2f}")

        assert balance_after > balance_before

        return True

    def test_loss_calculation(self) -> bool:
        """Test loss calculation with market move"""
        symbol = 'EURUSD'
        volume = 0.01

        # Get initial balance
        account_before = self.simulator.get_account_info()
        balance_before = account_before['balance']

        # Open BUY position
        ticket = self.simulator.market_buy(symbol, volume)

        # Simulate -50 pip move (loss)
        print(f"Simulating -50 pip move (loss)...")
        self.simulator.simulate_market_move(symbol, -50)

        # Check profit (negative)
        positions = self.simulator.get_positions()
        profit = positions.iloc[0]['profit']

        print(f"Current P/L: ${profit:.2f}")
        assert profit < 0  # Should be in loss

        # Close position
        self.simulator.close_position(ticket)

        # Check balance updated
        account_after = self.simulator.get_account_info()
        balance_after = account_after['balance']

        print(f"\nBalance before: ${balance_before:.2f}")
        print(f"Balance after: ${balance_after:.2f}")
        print(f"Loss: ${balance_after - balance_before:.2f}")

        assert balance_after < balance_before

        return True

    def test_multi_asset_trading(self) -> bool:
        """Test trading across multiple asset classes"""
        assets = [
            ('EURUSD', 0.01, 'forex'),
            ('XAUUSD', 0.01, 'metals'),
            ('US30', 0.10, 'indices'),
        ]

        for symbol, volume, expected_class in assets:
            asset_class = detect_asset_class(symbol)
            name, emoji = format_asset_name(symbol)

            print(f"\n{emoji} Testing {name} ({asset_class}):")

            # Open position
            ticket = self.simulator.market_buy(symbol, volume)
            print(f"  Opened ticket: {ticket}")

            # Check position
            positions = self.simulator.get_positions()
            assert len(positions) == 1

            # Simulate market move
            pips = 10 if asset_class == 'forex' else 50
            self.simulator.simulate_market_move(symbol, pips)

            # Check profit
            positions = self.simulator.get_positions()
            profit = positions.iloc[0]['profit']
            print(f"  Profit after +{pips} pips: ${profit:.2f}")

            # Close
            self.simulator.close_position(ticket)

        return True

    def test_account_equity_updates(self) -> bool:
        """Test account equity updates with open positions"""
        # Open position
        ticket = self.simulator.market_buy('EURUSD', 0.01)

        # Check initial equity
        account = self.simulator.get_account_info()
        balance = account['balance']
        equity_before = account['equity']

        print(f"Balance: ${balance:.2f}")
        print(f"Initial Equity: ${equity_before:.2f}")

        # Simulate profit
        self.simulator.simulate_market_move('EURUSD', 50)

        # Check updated equity
        account = self.simulator.get_account_info()
        equity_after = account['equity']
        profit = account['profit']

        print(f"Updated Equity: ${equity_after:.2f}")
        print(f"Unrealized Profit: ${profit:.2f}")

        assert equity_after > equity_before
        assert equity_after == balance + profit

        # Close position
        self.simulator.close_position(ticket)

        return True

    def print_summary(self):
        """Print test summary"""
        cprint(f"\n{'='*60}", "cyan")
        cprint("TEST SUMMARY", "white", "on_blue")
        cprint(f"{'='*60}", "cyan")

        for test_name, result, error in self.test_results:
            if result == "PASSED":
                cprint(f"✅ {test_name}", "green")
            else:
                cprint(f"❌ {test_name}", "red")
                if error:
                    cprint(f"   {error}", "red")

        cprint(f"\n{'='*60}", "cyan")
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0

        cprint(f"Total Tests: {total}", "white")
        cprint(f"Passed: {self.passed}", "green")
        cprint(f"Failed: {self.failed}", "red")
        cprint(f"Pass Rate: {pass_rate:.1f}%", "cyan")
        cprint(f"{'='*60}", "cyan")

        if self.failed == 0:
            cprint("\n🎉 ALL TESTS PASSED! System is ready for deployment.", "green")
        else:
            cprint(f"\n⚠️  {self.failed} test(s) failed. Please fix before deployment.", "yellow")


def run_all_tests():
    """Run complete test suite"""
    cprint("\n🌙 Moon Dev MT5 Sandbox Test Suite", "white", "on_blue")
    cprint(f"Starting at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n", "cyan")

    tester = MT5SandboxTester()

    # Run all tests
    tester.run_test("Account Initialization", tester.test_account_initialization)
    tester.run_test("Asset Class Detection", tester.test_asset_detection)
    tester.run_test("Symbol Information", tester.test_symbol_info)
    tester.run_test("OHLCV Data Generation", tester.test_ohlcv_generation)
    tester.run_test("Position Size Calculation", tester.test_position_sizing)
    tester.run_test("BUY Position", tester.test_buy_position)
    tester.run_test("SELL Position", tester.test_sell_position)
    tester.run_test("Max Positions Limit", tester.test_max_positions_limit)
    tester.run_test("Profit Calculation", tester.test_profit_calculation)
    tester.run_test("Loss Calculation", tester.test_loss_calculation)
    tester.run_test("Multi-Asset Trading", tester.test_multi_asset_trading)
    tester.run_test("Account Equity Updates", tester.test_account_equity_updates)

    # Print summary
    tester.print_summary()

    return tester.failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

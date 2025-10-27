#!/usr/bin/env python3
"""
🌙 Moon Dev AI Trading System - Test Suite
End-to-end system validation and health checks

Usage:
    # Run all tests
    python scripts/test_system.py

    # Run specific test category
    python scripts/test_system.py --category api
    python scripts/test_system.py --category agents
    python scripts/test_system.py --category performance

    # Quick health check
    python scripts/test_system.py --quick
"""

import sys
import asyncio
import time
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from termcolor import colored, cprint
from dotenv import load_dotenv
import argparse

# Add project root to path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

# Load environment
load_dotenv()


class SystemTest:
    """Comprehensive system test suite"""

    def __init__(self):
        self.results: Dict[str, Dict] = {}
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.warnings = 0

    def test_result(self, test_name: str, passed: bool, message: str = "", warning: bool = False):
        """
        Record test result

        Args:
            test_name: Name of the test
            passed: Whether test passed
            message: Additional information
            warning: Whether this is a warning (not critical failure)
        """
        self.total_tests += 1

        if passed:
            self.passed_tests += 1
            cprint(f"✅ {test_name}", "green")
        elif warning:
            self.warnings += 1
            cprint(f"⚠️  {test_name}: {message}", "yellow")
        else:
            self.failed_tests += 1
            cprint(f"❌ {test_name}: {message}", "red")

        if message and passed:
            print(f"   {message}")

        self.results[test_name] = {
            "passed": passed,
            "message": message,
            "warning": warning
        }

    async def test_api_keys(self):
        """Test API key configuration"""
        cprint("\n📋 Testing API Keys...", "cyan", attrs=['bold'])

        # Required keys
        anthropic_key = os.getenv('ANTHROPIC_KEY')
        self.test_result(
            "ANTHROPIC_KEY configured",
            anthropic_key is not None and len(anthropic_key) > 0,
            f"Found: {anthropic_key[:10]}..." if anthropic_key else "Not set"
        )

        # Optional but recommended keys
        birdeye_key = os.getenv('BIRDEYE_API_KEY')
        self.test_result(
            "BIRDEYE_API_KEY configured",
            birdeye_key is not None and len(birdeye_key) > 0,
            "Required for Solana token data" if not birdeye_key else "OK",
            warning=not birdeye_key
        )

        solana_key = os.getenv('SOLANA_PRIVATE_KEY')
        self.test_result(
            "SOLANA_PRIVATE_KEY configured",
            solana_key is not None and len(solana_key) > 0,
            "Required for trading" if not solana_key else "OK",
            warning=not solana_key
        )

        # Optional AI keys
        openai_key = os.getenv('OPENAI_KEY')
        self.test_result(
            "OPENAI_KEY configured (optional)",
            True,  # Always pass, it's optional
            "Configured" if openai_key else "Not set (Swarm will use fewer models)",
            warning=not openai_key
        )

    async def test_python_imports(self):
        """Test critical Python imports"""
        cprint("\n🐍 Testing Python Imports...", "cyan", attrs=['bold'])

        # Core imports
        try:
            from src import config
            self.test_result("config module", True)
        except ImportError as e:
            self.test_result("config module", False, str(e))

        try:
            from src.nice_funcs import token_price
            self.test_result("nice_funcs module", True)
        except ImportError as e:
            self.test_result("nice_funcs module", False, str(e))

        # Agent imports
        try:
            from src.agents.risk_agent import RiskAgent
            self.test_result("RiskAgent", True)
        except ImportError as e:
            self.test_result("RiskAgent", False, str(e))

        try:
            from src.agents.trading_agent import TradingAgent
            self.test_result("TradingAgent", True)
        except ImportError as e:
            self.test_result("TradingAgent", False, str(e))

        try:
            from src.agents.sentiment_agent import SentimentAgent
            self.test_result("SentimentAgent", True)
        except ImportError as e:
            self.test_result("SentimentAgent", False, str(e))

        # Async orchestrator
        try:
            from src.agents.async_orchestrator import AsyncOrchestrator
            self.test_result("AsyncOrchestrator", True)
        except ImportError as e:
            self.test_result("AsyncOrchestrator", False, str(e))

        # Optional imports
        try:
            from src.agents.swarm_agent import SwarmAgent
            self.test_result("SwarmAgent (optional)", True, "Multi-model consensus available")
        except ImportError:
            self.test_result("SwarmAgent (optional)", True, "Not available (use upstream version)", warning=True)

        try:
            from src.services.realtime_price_feed import RealtimePriceFeed
            self.test_result("RealtimePriceFeed", True, "Real-time WebSocket support")
        except ImportError:
            self.test_result("RealtimePriceFeed", True, "Not available (fallback to polling)", warning=True)

        # Rust core (optional)
        try:
            import moon_rust_core
            version = moon_rust_core.version()
            self.test_result("Rust core (optional)", True, f"v{version} - Ultra-fast mode enabled")
        except ImportError:
            self.test_result("Rust core (optional)", True, "Not available (build with: cd rust_core && maturin develop)", warning=True)

    async def test_model_factory(self):
        """Test model factory initialization"""
        cprint("\n🤖 Testing Model Factory...", "cyan", attrs=['bold'])

        try:
            from src.models.model_factory import model_factory

            # Test Claude
            if os.getenv('ANTHROPIC_KEY'):
                claude_model = model_factory.get_model('claude')
                self.test_result(
                    "Claude model initialization",
                    claude_model is not None,
                    "Ready for AI inference"
                )
            else:
                self.test_result(
                    "Claude model initialization",
                    False,
                    "ANTHROPIC_KEY not set"
                )

            # Test other models (if keys available)
            if os.getenv('OPENAI_KEY'):
                openai_model = model_factory.get_model('openai')
                self.test_result("OpenAI model", openai_model is not None)

            if os.getenv('DEEPSEEK_KEY'):
                deepseek_model = model_factory.get_model('deepseek')
                self.test_result("DeepSeek model", deepseek_model is not None)

        except Exception as e:
            self.test_result("Model factory", False, str(e))

    async def test_price_fetching(self):
        """Test price data fetching"""
        cprint("\n💹 Testing Price Fetching...", "cyan", attrs=['bold'])

        try:
            from src.nice_funcs import token_price

            # Test SOL price
            start = time.time()
            sol_price = token_price('SOL')
            elapsed_ms = (time.time() - start) * 1000

            if sol_price and sol_price > 0:
                self.test_result(
                    "SOL price fetch",
                    True,
                    f"${sol_price:.2f} (fetched in {elapsed_ms:.0f}ms)"
                )
            else:
                self.test_result(
                    "SOL price fetch",
                    False,
                    "Price returned None or invalid"
                )

            # Test BTC price
            btc_price = token_price('BTC')
            self.test_result(
                "BTC price fetch (optional)",
                True,
                f"${btc_price:.2f}" if btc_price else "Not available",
                warning=not btc_price
            )

        except Exception as e:
            self.test_result("Price fetching", False, str(e))

    async def test_real_time_feed(self):
        """Test real-time price feed (if available)"""
        cprint("\n🌊 Testing Real-Time Price Feed...", "cyan", attrs=['bold'])

        try:
            from src.services.realtime_price_feed import RealtimePriceFeed

            feed = RealtimePriceFeed()
            connected = await feed.connect()

            self.test_result(
                "Real-time feed connection",
                connected,
                "WebSocket connected" if connected else "Connection failed"
            )

            if connected:
                # Subscribe to test token
                feed.subscribe(['SOL'])

                # Wait briefly for price update
                await asyncio.sleep(2)

                price = feed.get_price('SOL')
                self.test_result(
                    "Real-time price retrieval",
                    price is not None,
                    f"SOL: ${price:.2f}" if price else "No price received yet"
                )

                await feed.disconnect()

        except ImportError:
            self.test_result(
                "Real-time feed",
                True,
                "Module not available (using fallback)",
                warning=True
            )
        except Exception as e:
            self.test_result("Real-time feed", False, str(e))

    async def test_agent_initialization(self):
        """Test agent initialization"""
        cprint("\n🤖 Testing Agent Initialization...", "cyan", attrs=['bold'])

        # Risk Agent
        try:
            from src.agents.risk_agent import RiskAgent
            risk_agent = RiskAgent()
            self.test_result("Risk Agent initialization", True)
        except Exception as e:
            self.test_result("Risk Agent initialization", False, str(e))

        # Trading Agent
        try:
            from src.agents.trading_agent import TradingAgent
            trading_agent = TradingAgent()
            self.test_result("Trading Agent initialization", True)
        except Exception as e:
            self.test_result("Trading Agent initialization", False, str(e))

        # Sentiment Agent
        try:
            from src.agents.sentiment_agent import SentimentAgent
            sentiment_agent = SentimentAgent()
            self.test_result("Sentiment Agent initialization", True)
        except Exception as e:
            self.test_result("Sentiment Agent initialization", False, str(e))

    async def test_async_orchestrator(self):
        """Test async orchestrator setup"""
        cprint("\n⚡ Testing Async Orchestrator...", "cyan", attrs=['bold'])

        try:
            from src.agents.async_orchestrator import AsyncOrchestrator

            orchestrator = AsyncOrchestrator()
            self.test_result("Orchestrator initialization", True)

            orchestrator.initialize_agents()
            agent_count = len(orchestrator.agents)

            self.test_result(
                "Agent auto-initialization",
                agent_count > 0,
                f"{agent_count} agents initialized"
            )

        except Exception as e:
            self.test_result("Async orchestrator", False, str(e))

    async def test_configuration(self):
        """Test system configuration"""
        cprint("\n⚙️  Testing Configuration...", "cyan", attrs=['bold'])

        try:
            from src import config

            # Check critical config values
            monitored_tokens = getattr(config, 'MONITORED_TOKENS', [])
            self.test_result(
                "MONITORED_TOKENS configured",
                len(monitored_tokens) > 0,
                f"{len(monitored_tokens)} tokens: {', '.join(monitored_tokens[:3])}"
            )

            max_loss = getattr(config, 'MAX_LOSS_USD', None)
            self.test_result(
                "MAX_LOSS_USD configured",
                max_loss is not None,
                f"${max_loss:.2f}"
            )

            min_balance = getattr(config, 'MINIMUM_BALANCE_USD', None)
            self.test_result(
                "MINIMUM_BALANCE_USD configured",
                min_balance is not None,
                f"${min_balance:.2f}"
            )

        except Exception as e:
            self.test_result("Configuration", False, str(e))

    async def test_directory_structure(self):
        """Test directory structure"""
        cprint("\n📁 Testing Directory Structure...", "cyan", attrs=['bold'])

        required_dirs = [
            'src/agents',
            'src/data',
            'src/models',
            'src/services',
            'rust_core/src',
            'scripts'
        ]

        for dir_path in required_dirs:
            full_path = Path(project_root) / dir_path
            self.test_result(
                f"Directory: {dir_path}",
                full_path.exists(),
                "Exists" if full_path.exists() else "Missing"
            )

    async def quick_health_check(self):
        """Quick health check (essential tests only)"""
        cprint("\n🏥 Running Quick Health Check...", "cyan", attrs=['bold'])

        await self.test_api_keys()
        await self.test_python_imports()
        await self.test_price_fetching()

    async def run_full_test_suite(self):
        """Run complete test suite"""
        cprint("\n" + "="*70, "green")
        cprint("🌙 Moon Dev System Test Suite 🌙", "green", attrs=['bold'])
        cprint("="*70 + "\n", "green")

        await self.test_directory_structure()
        await self.test_api_keys()
        await self.test_python_imports()
        await self.test_model_factory()
        await self.test_price_fetching()
        await self.test_real_time_feed()
        await self.test_agent_initialization()
        await self.test_async_orchestrator()
        await self.test_configuration()

    def print_summary(self):
        """Print test summary"""
        cprint("\n" + "="*70, "cyan")
        cprint("📊 Test Summary", "cyan", attrs=['bold'])
        cprint("="*70, "cyan")

        print(f"\nTotal Tests:   {self.total_tests}")
        cprint(f"Passed:        {self.passed_tests}", "green")

        if self.warnings > 0:
            cprint(f"Warnings:      {self.warnings}", "yellow")

        if self.failed_tests > 0:
            cprint(f"Failed:        {self.failed_tests}", "red")
        else:
            cprint("\n✨ All tests passed! System is healthy.", "green", attrs=['bold'])

        # Calculate success rate
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0

        if success_rate == 100:
            cprint(f"\n🎉 Success Rate: {success_rate:.0f}%", "green", attrs=['bold'])
        elif success_rate >= 80:
            cprint(f"\n⚠️  Success Rate: {success_rate:.0f}%", "yellow", attrs=['bold'])
        else:
            cprint(f"\n❌ Success Rate: {success_rate:.0f}%", "red", attrs=['bold'])

        # Recommendations
        if self.failed_tests > 0:
            cprint("\n📝 Recommendations:", "yellow")
            print("  - Check API keys in .env file")
            print("  - Run: pip install -r requirements.txt")
            print("  - Review error messages above")

        if self.warnings > 0:
            cprint("\n💡 Optional Improvements:", "cyan")
            print("  - Build Rust core for maximum performance")
            print("  - Configure additional AI model APIs")
            print("  - Setup real-time WebSocket feeds")

        print()


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Moon Dev System Test Suite")
    parser.add_argument('--quick', action='store_true', help="Quick health check only")
    parser.add_argument('--category', choices=['api', 'agents', 'performance', 'all'],
                       help="Test specific category")
    args = parser.parse_args()

    tester = SystemTest()

    if args.quick:
        await tester.quick_health_check()
    elif args.category:
        if args.category == 'api':
            await tester.test_api_keys()
            await tester.test_price_fetching()
            await tester.test_real_time_feed()
        elif args.category == 'agents':
            await tester.test_python_imports()
            await tester.test_agent_initialization()
            await tester.test_async_orchestrator()
        elif args.category == 'performance':
            await tester.test_price_fetching()
            await tester.test_real_time_feed()
        else:
            await tester.run_full_test_suite()
    else:
        await tester.run_full_test_suite()

    tester.print_summary()

    # Exit with error code if tests failed
    sys.exit(1 if tester.failed_tests > 0 else 0)


if __name__ == "__main__":
    asyncio.run(main())

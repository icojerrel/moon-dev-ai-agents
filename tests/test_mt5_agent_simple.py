"""
🧪 MT5 Agent Simple Test
Test MT5 Agent initialization and AI integration
"""

import os
import sys
from pathlib import Path
import argparse

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from dotenv import load_dotenv

def test_mt5_agent(skip_mt5=False):
    """Test MT5 Agent"""

    print("🧪 Testing MT5 Agent with OpenRouter...\n")

    # Load environment
    load_dotenv(project_root / '.env')

    # Step 1: MT5 Connection (Windows only)
    if not skip_mt5:
        print("1. MT5 Connection...")
        try:
            import MetaTrader5 as mt5

            if mt5.initialize():
                print("   ✅ MT5 initialized")

                login = int(os.getenv('MT5_LOGIN'))
                password = os.getenv('MT5_PASSWORD')
                server = os.getenv('MT5_SERVER')

                if mt5.login(login, password, server):
                    account = mt5.account_info()
                    print(f"   ✅ Logged in: {account.login}")
                    print(f"   💰 Balance: {account.balance} {account.currency}")
                    print()
                else:
                    print("   ❌ Login failed")
                    mt5.shutdown()
                    return False

                mt5.shutdown()
            else:
                print("   ❌ MT5 initialize failed")
                print("   (Make sure MT5 is installed)")
                return False

        except ImportError:
            print("   ⚠️  MetaTrader5 not available (needs Windows)")
            print("   Continuing with AI test only...\n")
            skip_mt5 = True
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    else:
        print("⚠️  Skipping MT5 connection (--skip-mt5 flag)\n")

    # Step 2: Agent Initialization
    print("2. Agent Initialization...")
    try:
        from src.agents.mt5_trading_agent import MT5TradingAgent
        from src.config import MT5_MODEL_TYPE, MT5_MAX_POSITIONS

        # Note: This will fail if MT5 is not available
        # But we can still test the model loading part
        if skip_mt5:
            print("   Testing model loading only (without MT5)...")
            from src.models.model_factory import model_factory
            from src.config import MT5_MODEL_NAME

            model = model_factory.get_model(MT5_MODEL_TYPE, model_name=MT5_MODEL_NAME)
            if model:
                print(f"   ✅ OpenRouter model loaded")
                print(f"   ✅ Model: {model.model_name}")
                print()
            else:
                print("   ❌ Model loading failed")
                return False
        else:
            agent = MT5TradingAgent(
                symbols=['EURUSD'],
                model_type=MT5_MODEL_TYPE,
                max_positions=MT5_MAX_POSITIONS
            )
            print(f"   ✅ Agent initialized")
            print(f"   ✅ Model type: {agent.model_type}")
            print(f"   ✅ Model name: {agent.model_name}")
            print(f"   ✅ Max positions: {agent.max_positions}")
            print()

    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Step 3: Trading Hours Check
    print("3. Trading Hours Check...")
    try:
        from src.utils.trading_hours import get_current_session, is_optimal_trading_time

        session = get_current_session()
        is_optimal, reason = is_optimal_trading_time('forex')

        print(f"   🕐 Current session: {session.value}")
        print(f"   {'✅' if is_optimal else '⏸️'} EURUSD: {reason}")
        print()
    except Exception as e:
        print(f"   ⚠️  Trading hours check: {e}")
        print()

    # Step 4: AI Analysis Test
    print("4. AI Analysis Test...")
    try:
        from src.models.model_factory import model_factory
        from src.config import MT5_MODEL_TYPE, MT5_MODEL_NAME

        model = model_factory.get_model(MT5_MODEL_TYPE, model_name=MT5_MODEL_NAME)

        if model:
            response = model.generate_response(
                system_prompt="You are a forex trading analyst. Be very concise.",
                user_content="EUR/USD at 1.0850, trending up. Trade recommendation in max 20 words?",
                temperature=0.7,
                max_tokens=80
            )

            if response and response.content:
                print(f"   ✅ Got AI analysis!")
                print(f"   Response: {response.content}")
                print()
            else:
                print("   ⚠️  Empty AI response")
                print()
        else:
            print("   ❌ Model not available")
            return False

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

    if skip_mt5:
        print("🎉 OpenRouter AI works! (MT5 needs Windows)")
    else:
        print("🎉 MT5 Agent + OpenRouter works perfectly!")

    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test MT5 Agent')
    parser.add_argument('--skip-mt5', action='store_true',
                       help='Skip MT5 connection test (for Mac/Linux)')
    args = parser.parse_args()

    success = test_mt5_agent(skip_mt5=args.skip_mt5)
    sys.exit(0 if success else 1)

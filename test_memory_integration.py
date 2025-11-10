#!/usr/bin/env python3
"""
Quick validation test for memory layer integration
Tests basic functionality without requiring API keys or actual trading
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_memory_imports():
    """Test that memory module imports correctly"""
    print("🧪 Testing memory module imports...")
    try:
        from src.memory import AgentMemory, MemoryScope, MemoryConfig
        print("✅ Memory module imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_memory_scopes():
    """Test that all memory scopes are defined"""
    print("\n🧪 Testing memory scopes...")
    try:
        from src.memory import MemoryScope

        expected_scopes = [
            'RISK', 'TRADING', 'MARKET_ANALYSIS', 'STRATEGY',
            'SENTIMENT', 'WHALE', 'FUNDING', 'LIQUIDATION',
            'COPYBOT', 'GLOBAL', 'ALERTS', 'CACHE'
        ]

        for scope_name in expected_scopes:
            scope = getattr(MemoryScope, scope_name)
            print(f"  ✓ {scope_name}: {scope.value}")

        print("✅ All memory scopes defined")
        return True
    except Exception as e:
        print(f"❌ Scope test failed: {e}")
        return False

def test_memory_config():
    """Test memory configuration"""
    print("\n🧪 Testing memory configuration...")
    try:
        from src.memory import MemoryConfig
        from src import config

        # Check config values
        assert hasattr(config, 'ENABLE_MEMORY'), "ENABLE_MEMORY not in config"
        assert hasattr(config, 'MEMORY_DB_PATH'), "MEMORY_DB_PATH not in config"

        print(f"  ✓ ENABLE_MEMORY: {config.ENABLE_MEMORY}")
        print(f"  ✓ MEMORY_DB_PATH: {config.MEMORY_DB_PATH}")

        # Check retention policies exist
        assert hasattr(MemoryConfig, 'RETENTION_POLICIES'), "No retention policies"
        print(f"  ✓ Retention policies: {len(MemoryConfig.RETENTION_POLICIES)} scopes configured")

        print("✅ Memory configuration valid")
        return True
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False

def test_agent_memory_initialization():
    """Test AgentMemory class initialization"""
    print("\n🧪 Testing AgentMemory initialization...")
    try:
        from src.memory import AgentMemory

        # Test initialization (should work even if database doesn't exist yet)
        memory = AgentMemory(agent_name="test_agent")

        print(f"  ✓ AgentMemory instance created")
        print(f"  ✓ Agent name: {memory.agent_name}")
        print(f"  ✓ Enabled: {memory.enabled}")

        # Test methods exist
        assert hasattr(memory, 'store'), "Missing store method"
        assert hasattr(memory, 'get_recent'), "Missing get_recent method"
        assert hasattr(memory, 'broadcast'), "Missing broadcast method"
        assert hasattr(memory, 'cache_api_response'), "Missing cache_api_response method"
        assert hasattr(memory, 'handoff'), "Missing handoff method"

        print("  ✓ All required methods present")
        print("✅ AgentMemory initialization successful")
        return True
    except Exception as e:
        print(f"❌ Initialization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_agent_integrations():
    """Test that agents have memory integration"""
    print("\n🧪 Testing agent integrations...")

    agents_to_test = [
        'risk_agent',
        'trading_agent',
        'sentiment_agent',
        'whale_agent',
        'strategy_agent'
    ]

    results = []
    for agent_name in agents_to_test:
        try:
            # Import agent module
            agent_module = __import__(f'src.agents.{agent_name}', fromlist=[''])

            # Check for memory imports in source
            agent_file = project_root / 'src' / 'agents' / f'{agent_name}.py'
            with open(agent_file, 'r') as f:
                source = f.read()
                has_memory_import = 'from src.memory import' in source
                has_memory_init = 'AgentMemory(' in source

            if has_memory_import and has_memory_init:
                print(f"  ✓ {agent_name}: Memory integrated")
                results.append(True)
            else:
                print(f"  ⚠ {agent_name}: Memory not fully integrated")
                results.append(False)

        except Exception as e:
            print(f"  ❌ {agent_name}: Error - {e}")
            results.append(False)

    if all(results):
        print("✅ All target agents have memory integration")
        return True
    else:
        print(f"⚠️ {sum(results)}/{len(results)} agents successfully integrated")
        return False

def main():
    """Run all validation tests"""
    print("=" * 60)
    print("🌙 Moon Dev AI Agents - Memory Layer Validation")
    print("=" * 60)

    tests = [
        test_memory_imports,
        test_memory_scopes,
        test_memory_config,
        test_agent_memory_initialization,
        test_agent_integrations,
    ]

    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)

    print("\n" + "=" * 60)
    print("📊 Test Results")
    print("=" * 60)
    print(f"Passed: {sum(results)}/{len(results)}")

    if all(results):
        print("✅ All validation tests passed!")
        return 0
    else:
        print("⚠️ Some tests failed. Review output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

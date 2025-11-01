"""
Test suite for Model Factory
Tests all LLM provider integrations

Run with: python -m pytest tests/test_model_factory.py -v
Or directly: python tests/test_model_factory.py
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.model_factory import ModelFactory
from dotenv import load_dotenv
import time
from termcolor import cprint

# Load environment
load_dotenv()

class ModelFactoryTester:
    """Comprehensive Model Factory test suite"""

    def __init__(self):
        self.results = {}
        self.factory = None

    def test_factory_initialization(self):
        """Test if ModelFactory initializes correctly"""
        cprint("\n" + "="*70, "cyan")
        cprint("TEST 1: Model Factory Initialization", "cyan", attrs=["bold"])
        cprint("="*70, "cyan")

        try:
            self.factory = ModelFactory()
            self.results["factory_init"] = {
                "status": "PASS",
                "message": "ModelFactory initialized successfully"
            }
            cprint("✅ PASS: Factory initialized", "green")
            return True
        except Exception as e:
            self.results["factory_init"] = {
                "status": "FAIL",
                "message": f"Factory initialization failed: {str(e)}"
            }
            cprint(f"❌ FAIL: {str(e)}", "red")
            return False

    def test_available_models(self):
        """Test which models are available"""
        cprint("\n" + "="*70, "cyan")
        cprint("TEST 2: Available Models Check", "cyan", attrs=["bold"])
        cprint("="*70, "cyan")

        if not self.factory:
            cprint("❌ SKIP: Factory not initialized", "yellow")
            return

        expected_models = ["claude", "openai", "deepseek", "groq", "ollama", "xai"]
        available = list(self.factory._models.keys())

        cprint(f"\n📊 Expected models: {len(expected_models)}", "cyan")
        cprint(f"📊 Available models: {len(available)}", "cyan")

        self.results["available_models"] = {
            "expected": expected_models,
            "available": available,
            "status": "INFO"
        }

        for model in expected_models:
            if model in available:
                cprint(f"  ✅ {model}: Available", "green")
            else:
                cprint(f"  ❌ {model}: Not available (check API key)", "yellow")

        cprint(f"\n✨ {len(available)}/{len(expected_models)} models available", "cyan")

    def test_model_retrieval(self):
        """Test getting specific models"""
        cprint("\n" + "="*70, "cyan")
        cprint("TEST 3: Model Retrieval", "cyan", attrs=["bold"])
        cprint("="*70, "cyan")

        if not self.factory:
            cprint("❌ SKIP: Factory not initialized", "yellow")
            return

        test_results = {}

        for model_type in self.factory._models.keys():
            try:
                model = self.factory.get_model(model_type)
                if model:
                    test_results[model_type] = "PASS"
                    cprint(f"  ✅ {model_type}: Retrieved successfully", "green")
                    cprint(f"     Model name: {model.model_name}", "cyan")
                else:
                    test_results[model_type] = "FAIL"
                    cprint(f"  ❌ {model_type}: Retrieval failed", "red")
            except Exception as e:
                test_results[model_type] = f"ERROR: {str(e)}"
                cprint(f"  ❌ {model_type}: Error - {str(e)}", "red")

        self.results["model_retrieval"] = test_results

    def test_model_interface(self):
        """Test if models implement required interface"""
        cprint("\n" + "="*70, "cyan")
        cprint("TEST 4: Model Interface Compliance", "cyan", attrs=["bold"])
        cprint("="*70, "cyan")

        if not self.factory:
            cprint("❌ SKIP: Factory not initialized", "yellow")
            return

        required_methods = ["is_available", "generate_response", "model_type"]
        test_results = {}

        for model_type, model in self.factory._models.items():
            missing_methods = []
            for method in required_methods:
                if not hasattr(model, method):
                    missing_methods.append(method)

            if missing_methods:
                test_results[model_type] = f"FAIL: Missing {missing_methods}"
                cprint(f"  ❌ {model_type}: Missing methods {missing_methods}", "red")
            else:
                test_results[model_type] = "PASS"
                cprint(f"  ✅ {model_type}: All required methods present", "green")

        self.results["interface_compliance"] = test_results

    def test_simple_generation(self, test_models=None):
        """Test simple text generation (if API keys available)"""
        cprint("\n" + "="*70, "cyan")
        cprint("TEST 5: Simple Text Generation", "cyan", attrs=["bold"])
        cprint("="*70, "cyan")

        if not self.factory:
            cprint("❌ SKIP: Factory not initialized", "yellow")
            return

        # Simple test prompt
        system_prompt = "You are a helpful assistant. Respond concisely."
        user_prompt = "Say 'Hello' in exactly one word."

        test_results = {}

        # Test only available models or specified models
        models_to_test = test_models if test_models else list(self.factory._models.keys())

        for model_type in models_to_test:
            if model_type not in self.factory._models:
                cprint(f"  ⚠️  {model_type}: Skipped (not available)", "yellow")
                continue

            cprint(f"\n  Testing {model_type}...", "cyan")

            try:
                model = self.factory.get_model(model_type)
                if not model:
                    test_results[model_type] = "SKIP: Model not available"
                    cprint(f"  ⚠️  {model_type}: Model retrieval failed", "yellow")
                    continue

                start_time = time.time()
                response = model.generate_response(
                    system_prompt=system_prompt,
                    user_content=user_prompt,
                    temperature=0.1,
                    max_tokens=10
                )
                elapsed = time.time() - start_time

                if response:
                    response_text = response.content if hasattr(response, 'content') else str(response)
                    test_results[model_type] = {
                        "status": "PASS",
                        "response": response_text[:100],
                        "time": f"{elapsed:.2f}s"
                    }
                    cprint(f"  ✅ {model_type}: Generated response in {elapsed:.2f}s", "green")
                    cprint(f"     Response: {response_text[:80]}...", "cyan")
                else:
                    test_results[model_type] = "FAIL: No response"
                    cprint(f"  ❌ {model_type}: No response received", "red")

            except Exception as e:
                test_results[model_type] = f"ERROR: {str(e)}"
                cprint(f"  ❌ {model_type}: Error - {str(e)}", "red")

        self.results["generation_test"] = test_results

    def generate_cost_comparison(self):
        """Generate cost comparison for different providers"""
        cprint("\n" + "="*70, "cyan")
        cprint("Cost Comparison Analysis", "cyan", attrs=["bold"])
        cprint("="*70, "cyan")

        # Based on typical pricing (as of Nov 2024/Jan 2025)
        cost_data = {
            "claude": {
                "model": "claude-3-5-haiku-latest",
                "input": 0.25,  # per 1M tokens
                "output": 1.25,
                "speed": "Fast",
                "context": "200K",
                "best_for": "Cost-effective, general purpose"
            },
            "openai": {
                "model": "gpt-4o",
                "input": 2.50,
                "output": 10.00,
                "speed": "Medium",
                "context": "128K",
                "best_for": "High quality, latest features"
            },
            "deepseek": {
                "model": "deepseek-reasoner",
                "input": 0.14,  # R1 model
                "output": 0.28,
                "speed": "Medium",
                "context": "64K",
                "best_for": "Reasoning tasks, very cheap"
            },
            "groq": {
                "model": "mixtral-8x7b-32768",
                "input": 0.24,
                "output": 0.24,
                "speed": "Very Fast",
                "context": "32K",
                "best_for": "Speed, real-time applications"
            },
            "ollama": {
                "model": "llama3.2",
                "input": 0.00,  # Local/free
                "output": 0.00,
                "speed": "Variable",
                "context": "128K",
                "best_for": "Free, private, offline"
            },
            "xai": {
                "model": "grok-4-fast-reasoning",
                "input": 0.10,
                "output": 0.10,
                "speed": "Fast",
                "context": "2M",
                "best_for": "Huge context, cheap, reasoning"
            }
        }

        cprint("\n💰 Pricing (per 1M tokens):", "cyan")
        cprint("-" * 70, "cyan")
        cprint(f"{'Provider':<12} {'Model':<30} {'Input':<8} {'Output':<8} {'Context'}", "cyan", attrs=["bold"])
        cprint("-" * 70, "cyan")

        for provider, data in cost_data.items():
            input_cost = f"${data['input']:.2f}" if data['input'] > 0 else "Free"
            output_cost = f"${data['output']:.2f}" if data['output'] > 0 else "Free"
            cprint(f"{provider:<12} {data['model']:<30} {input_cost:<8} {output_cost:<8} {data['context']}", "white")

        cprint("\n🎯 Use Case Recommendations:", "cyan")
        cprint("-" * 70, "cyan")

        for provider, data in cost_data.items():
            available = " ✅" if provider in self.factory._models else " ❌"
            cprint(f"{provider:<12}{available} - {data['best_for']}", "white")

        self.results["cost_comparison"] = cost_data

    def generate_report(self):
        """Generate comprehensive test report"""
        cprint("\n" + "="*70, "cyan")
        cprint("📋 TEST REPORT SUMMARY", "cyan", attrs=["bold"])
        cprint("="*70, "cyan")

        # Count results
        total_tests = len(self.results)
        passed = sum(1 for r in self.results.values() if isinstance(r, dict) and r.get("status") == "PASS")

        cprint(f"\n📊 Total Tests: {total_tests}", "cyan")
        cprint(f"✅ Passed: {passed}", "green")

        # Model availability summary
        if "available_models" in self.results:
            available = self.results["available_models"]["available"]
            expected = self.results["available_models"]["expected"]
            cprint(f"\n🤖 Models Available: {len(available)}/{len(expected)}", "cyan")
            cprint(f"   Available: {', '.join(available) if available else 'None'}", "white")
            missing = set(expected) - set(available)
            if missing:
                cprint(f"   Missing: {', '.join(missing)}", "yellow")

        cprint("\n" + "="*70, "cyan")

        return self.results

    def run_all_tests(self, test_generation=False):
        """Run complete test suite"""
        cprint("\n" + "="*70, "magenta")
        cprint("🧪 MODEL FACTORY COMPREHENSIVE TEST SUITE", "magenta", attrs=["bold"])
        cprint("="*70, "magenta")
        cprint("Testing all LLM provider integrations...\n", "white")

        start_time = time.time()

        # Run tests in order
        self.test_factory_initialization()
        self.test_available_models()
        self.test_model_retrieval()
        self.test_model_interface()

        # Only test generation if explicitly requested (requires API keys)
        if test_generation:
            self.test_simple_generation()
        else:
            cprint("\n⚠️  Skipping generation tests (requires API keys)", "yellow")
            cprint("   Run with test_generation=True to enable", "yellow")

        self.generate_cost_comparison()

        elapsed = time.time() - start_time

        cprint(f"\n⏱️  Total test time: {elapsed:.2f}s", "cyan")

        return self.generate_report()


def main():
    """Run tests"""
    tester = ModelFactoryTester()

    # Check if we should test generation (requires API keys)
    test_gen = os.getenv("TEST_GENERATION", "false").lower() == "true"

    results = tester.run_all_tests(test_generation=test_gen)

    # Exit code based on factory initialization
    if results.get("factory_init", {}).get("status") == "PASS":
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()

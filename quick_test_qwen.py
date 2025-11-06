#!/usr/bin/env python3
"""Quick test for qwen3-coder:30b - run this on your local machine"""

from termcolor import cprint

# Quick check
cprint("\n🔍 Quick Ollama + Qwen Test\n", "cyan", attrs=["bold"])

try:
    from src.models.model_factory import ModelFactory

    factory = ModelFactory()

    # Check default model name
    cprint(f"Default Ollama model: {factory.DEFAULT_MODELS['ollama']}", "yellow")

    if factory.is_model_available("ollama"):
        model = factory.get_model("ollama")
        cprint(f"✅ Ollama active! Model: {model.model_name}", "green")

        # Quick test
        cprint("\n🧪 Testing response...", "cyan")
        response = model.generate_response(
            system_prompt="You are a helpful assistant.",
            user_content="Say 'Hello from qwen3-coder:30b!' in one line.",
            temperature=0.5,
            max_tokens=50
        )

        cprint(f"\n💬 Response: {response.content}\n", "green")
        cprint("🎉 Success! qwen3-coder:30b is working!\n", "green", attrs=["bold"])

    else:
        cprint("❌ Ollama not available. Run: ollama serve", "red")

except Exception as e:
    cprint(f"❌ Error: {e}", "red")
    import traceback
    traceback.print_exc()

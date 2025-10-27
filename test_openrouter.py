"""
🌙 Moon Dev's OpenRouter Test Script
Quick test to verify OpenRouter integration
"""

import os
from dotenv import load_dotenv
from src.models.model_factory import model_factory
from termcolor import cprint

def test_openrouter():
    """Test OpenRouter model"""
    cprint("\n" + "="*60, "cyan")
    cprint("🧪 Testing OpenRouter Integration", "cyan")
    cprint("="*60, "cyan")

    # Check if OpenRouter is available
    if not model_factory.is_model_available("openrouter"):
        cprint("\n❌ OpenRouter not available", "red")
        cprint("💡 Make sure OPENROUTER_API_KEY is set in .env", "yellow")
        return False

    # Get OpenRouter model
    model = model_factory.get_model("openrouter")
    if not model:
        cprint("\n❌ Failed to get OpenRouter model", "red")
        return False

    cprint(f"\n✅ OpenRouter model loaded: {model.model_name}", "green")

    # Test generation
    try:
        cprint("\n📝 Testing response generation...", "cyan")

        system_prompt = "You are a helpful AI assistant built by Moon Dev."
        user_content = "Say 'Hello from OpenRouter!' and confirm you're working."

        response = model.generate_response(
            system_prompt=system_prompt,
            user_content=user_content,
            temperature=0.7,
            max_tokens=100
        )

        if response and response.content:
            cprint("\n✅ Response received!", "green")
            cprint(f"\n💬 Response: {response.content}", "cyan")

            if response.usage:
                cprint(f"\n📊 Token usage:", "yellow")
                cprint(f"  - Prompt tokens: {response.usage.get('prompt_tokens', 0)}", "yellow")
                cprint(f"  - Completion tokens: {response.usage.get('completion_tokens', 0)}", "yellow")
                cprint(f"  - Total tokens: {response.usage.get('total_tokens', 0)}", "yellow")

            cprint("\n" + "="*60, "green")
            cprint("✅ OpenRouter integration test PASSED!", "green")
            cprint("="*60, "green")
            return True
        else:
            cprint("\n❌ Empty response received", "red")
            return False

    except Exception as e:
        cprint(f"\n❌ Test failed with error: {str(e)}", "red")
        import traceback
        cprint(f"\n{traceback.format_exc()}", "yellow")
        return False

if __name__ == "__main__":
    # Load environment
    load_dotenv()

    # Run test
    success = test_openrouter()

    if success:
        cprint("\n🎉 You can now use OpenRouter in your agents!", "green")
        cprint("\n📖 Example usage:", "cyan")
        cprint("```python", "yellow")
        cprint("from src.models.model_factory import model_factory", "yellow")
        cprint("", "yellow")
        cprint("# Get OpenRouter model", "yellow")
        cprint("model = model_factory.get_model('openrouter')", "yellow")
        cprint("", "yellow")
        cprint("# Or use a specific model via OpenRouter", "yellow")
        cprint("model = model_factory.get_model('openrouter', model_name='anthropic/claude-3.5-sonnet')", "yellow")
        cprint("", "yellow")
        cprint("# Generate response", "yellow")
        cprint("response = model.generate_response(", "yellow")
        cprint("    system_prompt='You are a helpful assistant',", "yellow")
        cprint("    user_content='Hello!'", "yellow")
        cprint(")", "yellow")
        cprint("print(response.content)", "yellow")
        cprint("```", "yellow")
    else:
        cprint("\n⚠️  Test failed. Please check your OpenRouter API key.", "yellow")
        cprint("\n📝 To fix:", "cyan")
        cprint("  1. Get your API key from https://openrouter.ai/keys", "cyan")
        cprint("  2. Add to .env: OPENROUTER_API_KEY=your_key_here", "cyan")
        cprint("  3. Run this test again: python test_openrouter.py", "cyan")

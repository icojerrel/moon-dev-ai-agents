"""
🌙 Moon Dev's Fallback Model Wrapper
Built with love by Moon Dev 🚀

Provides automatic fallback between multiple AI providers
"""

from typing import Optional, List
from termcolor import cprint
from .base_model import BaseModel, ModelResponse


class FallbackModel:
    """
    Wrapper that tries multiple models in sequence until one succeeds

    Usage:
        fallback = FallbackModel(
            primary=openrouter_model,
            fallback=ollama_model
        )

        response = fallback.generate_response(system_prompt, user_content)
    """

    def __init__(self, primary: BaseModel, fallback: BaseModel, name: str = "Fallback"):
        """
        Initialize fallback model

        Args:
            primary: Primary model to try first
            fallback: Fallback model to use if primary fails
            name: Name for this fallback configuration
        """
        self.primary = primary
        self.fallback = fallback
        self.name = name

        self.primary_attempts = 0
        self.fallback_attempts = 0
        self.primary_successes = 0
        self.fallback_successes = 0

        cprint(f"\n🔄 {self.name} Fallback Model Initialized", "cyan")
        cprint(f"   Primary: {primary.model_type} ({primary.model_name})", "green")
        cprint(f"   Fallback: {fallback.model_type} ({fallback.model_name})", "yellow")

    def generate_response(self, system_prompt: str, user_content: str,
                         temperature: float = 0.7, max_tokens: int = None,
                         **kwargs) -> Optional[ModelResponse]:
        """
        Generate response with automatic fallback

        Tries primary model first, falls back to secondary if it fails

        Args:
            system_prompt: System instructions
            user_content: User message
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters

        Returns:
            ModelResponse from successful model, or None if all fail
        """

        # Try primary model first
        if self.primary.is_available():
            try:
                cprint(f"🎯 Trying primary: {self.primary.model_type}", "cyan")
                self.primary_attempts += 1

                response = self.primary.generate_response(
                    system_prompt=system_prompt,
                    user_content=user_content,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )

                if response and response.content:
                    self.primary_successes += 1
                    cprint(f"✅ Primary model succeeded ({self.primary.model_type})", "green")
                    return response

            except Exception as e:
                cprint(f"⚠️ Primary model failed: {str(e)}", "yellow")
                cprint(f"🔄 Falling back to: {self.fallback.model_type}", "cyan")
        else:
            cprint(f"⚠️ Primary model not available: {self.primary.model_type}", "yellow")
            cprint(f"🔄 Using fallback: {self.fallback.model_type}", "cyan")

        # Try fallback model
        if self.fallback.is_available():
            try:
                cprint(f"🎯 Trying fallback: {self.fallback.model_type}", "cyan")
                self.fallback_attempts += 1

                response = self.fallback.generate_response(
                    system_prompt=system_prompt,
                    user_content=user_content,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )

                if response and response.content:
                    self.fallback_successes += 1
                    cprint(f"✅ Fallback model succeeded ({self.fallback.model_type})", "green")
                    return response

            except Exception as e:
                cprint(f"❌ Fallback model also failed: {str(e)}", "red")
                cprint("💡 Check your API keys and model availability", "yellow")
        else:
            cprint(f"❌ Fallback model not available: {self.fallback.model_type}", "red")

        # Both models failed
        cprint(f"❌ All models failed for {self.name}", "red")
        return None

    def get_statistics(self):
        """Get usage statistics"""
        total_attempts = self.primary_attempts + self.fallback_attempts

        stats = {
            "total_attempts": total_attempts,
            "primary": {
                "attempts": self.primary_attempts,
                "successes": self.primary_successes,
                "success_rate": f"{(self.primary_successes / self.primary_attempts * 100):.1f}%" if self.primary_attempts > 0 else "0%"
            },
            "fallback": {
                "attempts": self.fallback_attempts,
                "successes": self.fallback_successes,
                "success_rate": f"{(self.fallback_successes / self.fallback_attempts * 100):.1f}%" if self.fallback_attempts > 0 else "0%"
            }
        }

        return stats

    def print_statistics(self):
        """Print usage statistics"""
        stats = self.get_statistics()

        cprint(f"\n📊 {self.name} Statistics", "cyan")
        cprint("=" * 50, "cyan")
        cprint(f"Total Requests: {stats['total_attempts']}", "white")
        cprint(f"\nPrimary ({self.primary.model_type}):", "green")
        cprint(f"  Attempts: {stats['primary']['attempts']}", "yellow")
        cprint(f"  Successes: {stats['primary']['successes']}", "yellow")
        cprint(f"  Success Rate: {stats['primary']['success_rate']}", "yellow")
        cprint(f"\nFallback ({self.fallback.model_type}):", "magenta")
        cprint(f"  Attempts: {stats['fallback']['attempts']}", "yellow")
        cprint(f"  Successes: {stats['fallback']['successes']}", "yellow")
        cprint(f"  Success Rate: {stats['fallback']['success_rate']}", "yellow")
        cprint("=" * 50, "cyan")

    def is_available(self) -> bool:
        """Check if at least one model is available"""
        return self.primary.is_available() or self.fallback.is_available()

    @property
    def model_type(self) -> str:
        """Return combined model type"""
        return f"{self.primary.model_type}→{self.fallback.model_type}"

    @property
    def model_name(self) -> str:
        """Return combined model names"""
        return f"{self.primary.model_name}→{self.fallback.model_name}"


def create_openrouter_ollama_fallback(openrouter_api_key: str,
                                      openrouter_model: str = "anthropic/claude-3.5-sonnet",
                                      ollama_model: str = "llama3.2") -> FallbackModel:
    """
    Create OpenRouter → Ollama fallback configuration

    Args:
        openrouter_api_key: OpenRouter API key
        openrouter_model: OpenRouter model to use
        ollama_model: Ollama model to use as fallback

    Returns:
        FallbackModel instance
    """
    from .openrouter_model import OpenRouterModel
    from .ollama_model import OllamaModel

    cprint("\n🔧 Creating OpenRouter → Ollama Fallback", "cyan")

    # Initialize primary (OpenRouter)
    primary = OpenRouterModel(
        api_key=openrouter_api_key,
        model_name=openrouter_model
    )

    # Initialize fallback (Ollama)
    fallback = OllamaModel(
        api_key="not-needed",  # Ollama doesn't need key
        model_name=ollama_model
    )

    # Create fallback wrapper
    return FallbackModel(
        primary=primary,
        fallback=fallback,
        name="OpenRouter→Ollama"
    )


if __name__ == "__main__":
    """Test fallback model"""
    import os
    from dotenv import load_dotenv

    load_dotenv()

    openrouter_key = os.getenv("OPENROUTER_API_KEY")

    if not openrouter_key:
        cprint("❌ OPENROUTER_API_KEY not found", "red")
        cprint("Get one at: https://openrouter.ai/keys", "yellow")
        exit(1)

    # Create fallback model
    model = create_openrouter_ollama_fallback(
        openrouter_api_key=openrouter_key,
        openrouter_model="anthropic/claude-3-haiku",  # Cheap for testing
        ollama_model="llama3.2"
    )

    # Test
    cprint("\n🧪 Testing Fallback Model", "cyan")

    response = model.generate_response(
        system_prompt="You are a helpful trading assistant.",
        user_content="What are 3 key forex indicators? Be brief.",
        max_tokens=150
    )

    if response:
        cprint(f"\n📝 Response ({response.model_name}):", "cyan")
        cprint(response.content, "white")

    # Print stats
    model.print_statistics()

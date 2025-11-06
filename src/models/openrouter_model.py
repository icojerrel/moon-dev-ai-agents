"""
🌙 Moon Dev's OpenRouter Model Implementation
Built with love by Moon Dev 🚀

OpenRouter provides access to multiple AI models through a unified API
"""

from openai import OpenAI
from termcolor import cprint
from .base_model import BaseModel, ModelResponse

class OpenRouterModel(BaseModel):
    """Implementation for OpenRouter's unified AI API"""

    # Popular models available on OpenRouter
    POPULAR_MODELS = {
        # Anthropic Claude
        "anthropic/claude-3.5-sonnet": "Claude 3.5 Sonnet - Best balanced model",
        "anthropic/claude-3-opus": "Claude 3 Opus - Most intelligent",
        "anthropic/claude-3-haiku": "Claude 3 Haiku - Fastest Claude",

        # OpenAI
        "openai/gpt-4-turbo": "GPT-4 Turbo - Latest OpenAI",
        "openai/gpt-4": "GPT-4 - Flagship model",
        "openai/gpt-3.5-turbo": "GPT-3.5 Turbo - Fast & cheap",

        # Google
        "google/gemini-pro-1.5": "Gemini 1.5 Pro - Latest Google",
        "google/gemini-pro": "Gemini Pro - Production ready",

        # Meta
        "meta-llama/llama-3.1-70b-instruct": "Llama 3.1 70B - Open source",
        "meta-llama/llama-3.1-8b-instruct": "Llama 3.1 8B - Fast",

        # Mistral
        "mistralai/mistral-large": "Mistral Large - Flagship",
        "mistralai/mixtral-8x7b-instruct": "Mixtral 8x7B - Fast MoE",

        # DeepSeek
        "deepseek/deepseek-r1": "DeepSeek R1 - Reasoning model",
        "deepseek/deepseek-chat": "DeepSeek Chat - General purpose",

        # Qwen
        "qwen/qwen-2.5-72b-instruct": "Qwen 2.5 72B - Chinese model",

        # Others
        "perplexity/llama-3.1-sonar-large-128k-online": "Perplexity Sonar - With internet",
        "x-ai/grok-2": "Grok 2 - xAI's model",
    }

    def __init__(self, api_key: str, model_name: str = "anthropic/claude-3.5-sonnet", **kwargs):
        """
        Initialize OpenRouter model

        Args:
            api_key: OpenRouter API key
            model_name: Model identifier (e.g., "anthropic/claude-3.5-sonnet")
            **kwargs: Additional parameters
        """
        self.model_name = model_name
        self.max_tokens = kwargs.get('max_tokens', 2048)
        super().__init__(api_key, **kwargs)

    def initialize_client(self, **kwargs) -> None:
        """Initialize the OpenRouter client using OpenAI SDK"""
        try:
            # OpenRouter uses OpenAI-compatible API
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.api_key,
            )

            model_desc = self.POPULAR_MODELS.get(self.model_name, "Custom model")
            cprint(f"✨ Moon Dev's OpenRouter initialized: {self.model_name}", "green")
            cprint(f"   {model_desc}", "cyan")

        except Exception as e:
            cprint(f"❌ Failed to initialize OpenRouter: {str(e)}", "red")
            self.client = None

    def generate_response(self, system_prompt: str, user_content: str,
                         temperature: float = 0.7, max_tokens: int = None, **kwargs):
        """
        Generate a response using OpenRouter

        Args:
            system_prompt: System instructions
            user_content: User message
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters

        Returns:
            ModelResponse object
        """
        try:
            messages = [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_content
                }
            ]

            cprint(f"🤔 OpenRouter {self.model_name} is thinking...", "yellow")

            # Make request
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens or self.max_tokens,
                **kwargs
            )

            # Extract content
            content = response.choices[0].message.content

            if not content or not content.strip():
                cprint("⚠️ OpenRouter returned empty content", "yellow")
                content = ""

            cprint(f"✅ OpenRouter response received ({len(content)} chars)", "green")

            return ModelResponse(
                content=content.strip() if content else "",
                raw_response=response,
                model_name=self.model_name,
                usage=response.usage.model_dump() if hasattr(response, 'usage') else None
            )

        except Exception as e:
            cprint(f"❌ OpenRouter error: {str(e)}", "red")

            # Check for common errors
            error_str = str(e).lower()
            if "insufficient credits" in error_str or "quota" in error_str:
                cprint("💳 Insufficient OpenRouter credits!", "red")
            elif "unauthorized" in error_str or "authentication" in error_str:
                cprint("🔑 OpenRouter API key invalid or missing", "red")
            elif "model not found" in error_str:
                cprint(f"❌ Model '{self.model_name}' not found on OpenRouter", "red")
                cprint(f"💡 Try one of: {', '.join(list(self.POPULAR_MODELS.keys())[:5])}", "yellow")

            raise

    def is_available(self) -> bool:
        """Check if OpenRouter is available"""
        return self.client is not None

    @property
    def model_type(self) -> str:
        """Return model type"""
        return "openrouter"

    @classmethod
    def list_popular_models(cls):
        """Print list of popular OpenRouter models"""
        cprint("\n🌟 Popular OpenRouter Models:", "cyan")
        cprint("=" * 60, "cyan")

        for model_id, description in cls.POPULAR_MODELS.items():
            cprint(f"  {model_id}", "green")
            cprint(f"    └─ {description}", "yellow")

        cprint("\n💡 More models at: https://openrouter.ai/models", "cyan")
        cprint("=" * 60, "cyan")


if __name__ == "__main__":
    """Test OpenRouter model"""
    import os
    from dotenv import load_dotenv

    load_dotenv()

    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        cprint("❌ OPENROUTER_API_KEY not found in .env", "red")
        cprint("Get your key at: https://openrouter.ai/keys", "yellow")
        exit(1)

    # List available models
    OpenRouterModel.list_popular_models()

    # Test the model
    cprint("\n🧪 Testing OpenRouter...", "cyan")

    model = OpenRouterModel(
        api_key=api_key,
        model_name="anthropic/claude-3-haiku"  # Fast & cheap for testing
    )

    if model.is_available():
        response = model.generate_response(
            system_prompt="You are a helpful trading assistant.",
            user_content="What are the key indicators for forex trading?",
            max_tokens=200
        )

        cprint(f"\n📝 Response:", "cyan")
        cprint(response.content, "white")

        if response.usage:
            cprint(f"\n📊 Token Usage: {response.usage}", "yellow")
    else:
        cprint("❌ OpenRouter not available", "red")

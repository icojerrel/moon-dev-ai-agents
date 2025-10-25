"""
🌙 Moon Dev's OpenRouter Model Implementation
Access to 100+ AI models through one unified API
Built with love by Moon Dev 🚀
"""

from openai import OpenAI
from termcolor import cprint
from .base_model import BaseModel, ModelResponse
from typing import Optional
import os

class OpenRouterModel(BaseModel):
    """Implementation for OpenRouter - unified access to 100+ AI models"""

    AVAILABLE_MODELS = {
        # Top performing models
        "claude-3.5-sonnet": {
            "id": "anthropic/claude-3.5-sonnet",
            "description": "Anthropic's most intelligent model",
            "input_price": "$3.00/1M tokens",
            "output_price": "$15.00/1M tokens",
            "context": "200k"
        },
        "claude-3-opus": {
            "id": "anthropic/claude-3-opus",
            "description": "Powerful Claude model for complex tasks",
            "input_price": "$15.00/1M tokens",
            "output_price": "$75.00/1M tokens",
            "context": "200k"
        },
        "gpt-4-turbo": {
            "id": "openai/gpt-4-turbo",
            "description": "OpenAI's advanced GPT-4 Turbo",
            "input_price": "$10.00/1M tokens",
            "output_price": "$30.00/1M tokens",
            "context": "128k"
        },
        "gpt-4o": {
            "id": "openai/gpt-4o",
            "description": "OpenAI's GPT-4 Optimized model",
            "input_price": "$2.50/1M tokens",
            "output_price": "$10.00/1M tokens",
            "context": "128k"
        },

        # Cost-effective options (RECOMMENDED)
        "claude-haiku": {
            "id": "anthropic/claude-3-haiku",
            "description": "Fast and efficient Claude model",
            "input_price": "$0.25/1M tokens",
            "output_price": "$1.25/1M tokens",
            "context": "200k"
        },
        "deepseek-chat": {
            "id": "deepseek/deepseek-chat",
            "description": "Very cheap, high-quality model",
            "input_price": "$0.14/1M tokens",
            "output_price": "$0.28/1M tokens",
            "context": "64k"
        },
        "deepseek-r1": {
            "id": "deepseek/deepseek-r1",
            "description": "DeepSeek's reasoning model with thinking process",
            "input_price": "$0.55/1M tokens",
            "output_price": "$2.19/1M tokens",
            "context": "64k"
        },
        "gpt-3.5-turbo": {
            "id": "openai/gpt-3.5-turbo",
            "description": "Fast and cheap OpenAI model",
            "input_price": "$0.50/1M tokens",
            "output_price": "$1.50/1M tokens",
            "context": "16k"
        },

        # Open source models
        "llama-3.1-70b": {
            "id": "meta-llama/llama-3.1-70b-instruct",
            "description": "Meta's large Llama model",
            "input_price": "$0.35/1M tokens",
            "output_price": "$0.40/1M tokens",
            "context": "128k"
        },
        "mixtral-8x7b": {
            "id": "mistralai/mixtral-8x7b-instruct",
            "description": "Mixtral mixture of experts model",
            "input_price": "$0.24/1M tokens",
            "output_price": "$0.24/1M tokens",
            "context": "32k"
        },

        # Specialized models
        "gemini-pro": {
            "id": "google/gemini-pro",
            "description": "Google's Gemini Pro model",
            "input_price": "$0.125/1M tokens",
            "output_price": "$0.375/1M tokens",
            "context": "32k"
        },
        "command-r-plus": {
            "id": "cohere/command-r-plus",
            "description": "Cohere's large instruction-following model",
            "input_price": "$2.50/1M tokens",
            "output_price": "$10.00/1M tokens",
            "context": "128k"
        },
    }

    def __init__(self, api_key: str, model_name: str = "anthropic/claude-3-haiku", **kwargs):
        """Initialize OpenRouter model

        Args:
            api_key: OpenRouter API key
            model_name: Model ID to use (e.g., 'anthropic/claude-3-haiku')
            **kwargs: Additional configuration options
        """
        self.model_name = model_name
        self.max_tokens = kwargs.get('max_tokens', 4096)
        self.app_name = kwargs.get('app_name', os.getenv('OPENROUTER_APP_NAME', 'Moon Dev AI Trading'))
        self.app_url = kwargs.get('app_url', os.getenv('OPENROUTER_APP_URL', 'https://github.com/moon-dev-ai-agents'))
        super().__init__(api_key, **kwargs)

        cprint(f"✨ Moon Dev's OpenRouter initialized: {model_name} 🌙", "green")
        cprint(f"🌍 Access to 100+ models via unified API", "cyan")
        cprint(f"💰 Cost-optimized routing enabled", "cyan")

    def initialize_client(self, **kwargs) -> None:
        """Initialize OpenRouter client (OpenAI-compatible)"""
        try:
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.api_key,
                default_headers={
                    "HTTP-Referer": self.app_url,
                    "X-Title": self.app_name,
                }
            )
            cprint("✅ OpenRouter client initialized successfully", "green")
            cprint(f"📱 App: {self.app_name}", "cyan")
            cprint(f"🔗 URL: {self.app_url}", "cyan")
        except Exception as e:
            cprint(f"❌ Failed to initialize OpenRouter: {str(e)}", "red")
            raise

    def generate_response(self, system_prompt: str, user_content: str,
                         temperature: float = 0.7, max_tokens: Optional[int] = None) -> ModelResponse:
        """Generate response via OpenRouter

        Args:
            system_prompt: System message to set context
            user_content: User's input message
            temperature: Randomness (0.0-1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            ModelResponse with content and usage info
        """
        try:
            cprint(f"\n🤖 Generating response with {self.model_name}...", "cyan")

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=temperature,
                max_tokens=max_tokens or self.max_tokens
            )

            # Extract content
            content = response.choices[0].message.content

            # Calculate usage
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }

            cprint(f"✅ Response generated successfully", "green")
            cprint(f"📊 Tokens: {usage['total_tokens']} total ({usage['prompt_tokens']} in + {usage['completion_tokens']} out)", "cyan")

            return ModelResponse(
                content=content,
                raw_response=response,
                model_name=self.model_name,
                usage=usage
            )

        except Exception as e:
            cprint(f"❌ OpenRouter error: {str(e)}", "red")
            raise

    def is_available(self) -> bool:
        """Check if OpenRouter is available and working"""
        try:
            # Test with a minimal completion
            cprint("🔍 Testing OpenRouter availability...", "cyan")
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            cprint("✅ OpenRouter is available and working!", "green")
            return True
        except Exception as e:
            cprint(f"⚠️ OpenRouter not available: {str(e)}", "yellow")
            return False

    @property
    def model_type(self) -> str:
        """Return the model type"""
        return "openrouter"

    def get_model_info(self, model_key: str) -> dict:
        """Get information about a specific model

        Args:
            model_key: Short model key (e.g., 'claude-haiku')

        Returns:
            Dictionary with model information
        """
        return self.AVAILABLE_MODELS.get(model_key, {})

    def list_cheap_models(self) -> list:
        """List the most cost-effective models

        Returns:
            List of model keys sorted by cost (cheapest first)
        """
        cheap_models = [
            ("deepseek-chat", "$0.14/1M in, $0.28/1M out"),
            ("claude-haiku", "$0.25/1M in, $1.25/1M out"),
            ("gpt-3.5-turbo", "$0.50/1M in, $1.50/1M out"),
            ("mixtral-8x7b", "$0.24/1M tokens"),
        ]

        cprint("\n💰 Most Cost-Effective Models:", "cyan")
        for model, price in cheap_models:
            cprint(f"  ├─ {model}: {price}", "green")

        return [model for model, _ in cheap_models]

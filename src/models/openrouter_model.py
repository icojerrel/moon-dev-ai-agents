"""
🌙 Moon Dev's OpenRouter Model Implementation
Built with love by Moon Dev 🚀

OpenRouter provides unified access to ALL AI models through a single API.
No need for multiple API keys - just one OpenRouter key for everything!
"""

from openai import OpenAI
from termcolor import cprint
from .base_model import BaseModel, ModelResponse

class OpenRouterModel(BaseModel):
    """Implementation for OpenRouter - unified access to all AI models"""

    # Popular models available through OpenRouter
    # Full list at: https://openrouter.ai/models
    AVAILABLE_MODELS = {
        # OpenAI Models
        "openai/gpt-4o": {
            "description": "Latest GPT-4 Optimized model",
            "input_price": "$2.50/1M tokens",
            "output_price": "$10.00/1M tokens",
            "context": "128k tokens"
        },
        "openai/gpt-4o-mini": {
            "description": "Efficient GPT-4 Optimized mini model",
            "input_price": "$0.15/1M tokens",
            "output_price": "$0.60/1M tokens",
            "context": "128k tokens"
        },
        "openai/o1": {
            "description": "Latest O1 reasoning model",
            "input_price": "$15.00/1M tokens",
            "output_price": "$60.00/1M tokens",
            "context": "200k tokens"
        },
        "openai/o1-mini": {
            "description": "Smaller O1 reasoning model",
            "input_price": "$3.00/1M tokens",
            "output_price": "$12.00/1M tokens",
            "context": "128k tokens"
        },

        # Anthropic Claude Models
        "anthropic/claude-3.5-sonnet": {
            "description": "Latest Claude 3.5 Sonnet - Best for complex tasks",
            "input_price": "$3.00/1M tokens",
            "output_price": "$15.00/1M tokens",
            "context": "200k tokens"
        },
        "anthropic/claude-3-opus": {
            "description": "Most powerful Claude model",
            "input_price": "$15.00/1M tokens",
            "output_price": "$75.00/1M tokens",
            "context": "200k tokens"
        },
        "anthropic/claude-3-haiku": {
            "description": "Fast, efficient Claude model",
            "input_price": "$0.25/1M tokens",
            "output_price": "$1.25/1M tokens",
            "context": "200k tokens"
        },

        # Google Gemini Models
        "google/gemini-2.0-flash-exp": {
            "description": "Next-gen multimodal Gemini model",
            "input_price": "FREE",
            "output_price": "FREE",
            "context": "1M tokens"
        },
        "google/gemini-pro-1.5": {
            "description": "Complex reasoning Gemini model",
            "input_price": "$1.25/1M tokens",
            "output_price": "$5.00/1M tokens",
            "context": "2M tokens"
        },

        # DeepSeek Models
        "deepseek/deepseek-chat": {
            "description": "Fast DeepSeek chat model",
            "input_price": "$0.14/1M tokens",
            "output_price": "$0.28/1M tokens",
            "context": "64k tokens"
        },
        "deepseek/deepseek-r1": {
            "description": "DeepSeek R1 reasoning model - EXCELLENT for trading",
            "input_price": "$0.55/1M tokens",
            "output_price": "$2.19/1M tokens",
            "context": "64k tokens"
        },

        # Meta Llama Models
        "meta-llama/llama-3.3-70b-instruct": {
            "description": "Latest Llama 3.3 70B model",
            "input_price": "$0.35/1M tokens",
            "output_price": "$0.40/1M tokens",
            "context": "128k tokens"
        },
        "meta-llama/llama-3.1-405b-instruct": {
            "description": "Massive Llama 3.1 405B model",
            "input_price": "$2.70/1M tokens",
            "output_price": "$2.70/1M tokens",
            "context": "128k tokens"
        },

        # xAI Grok Models
        "x-ai/grok-2": {
            "description": "xAI's Grok 2 model",
            "input_price": "$2.00/1M tokens",
            "output_price": "$10.00/1M tokens",
            "context": "131k tokens"
        },
        "x-ai/grok-beta": {
            "description": "Latest Grok beta with enhanced capabilities",
            "input_price": "$5.00/1M tokens",
            "output_price": "$15.00/1M tokens",
            "context": "131k tokens"
        },

        # Mistral Models
        "mistralai/mistral-large": {
            "description": "Mistral's largest model",
            "input_price": "$2.00/1M tokens",
            "output_price": "$6.00/1M tokens",
            "context": "128k tokens"
        },

        # Cohere Models
        "cohere/command-r-plus": {
            "description": "Cohere's command model with RAG",
            "input_price": "$2.50/1M tokens",
            "output_price": "$10.00/1M tokens",
            "context": "128k tokens"
        }
    }

    def __init__(self, api_key: str, model_name: str = "anthropic/claude-3.5-sonnet", **kwargs):
        """
        Initialize OpenRouter model

        Args:
            api_key: Your OpenRouter API key from https://openrouter.ai/keys
            model_name: Model to use (format: provider/model-name)
        """
        self.model_name = model_name
        self.max_tokens = 4096  # Default max tokens
        super().__init__(api_key, **kwargs)

    def initialize_client(self, **kwargs) -> None:
        """Initialize the OpenRouter client using OpenAI SDK with custom base URL"""
        try:
            # OpenRouter is compatible with OpenAI's API format
            # Just point to their endpoint
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://openrouter.ai/api/v1"
            )
            cprint(f"✨ Moon Dev's magic initialized OpenRouter model: {self.model_name} 🌟", "green")

            model_info = self.AVAILABLE_MODELS.get(self.model_name, {})
            if model_info:
                cprint(f"💰 Pricing: {model_info.get('input_price', 'N/A')} in / {model_info.get('output_price', 'N/A')} out", "cyan")
                cprint(f"📊 Context: {model_info.get('context', 'N/A')}", "cyan")
        except Exception as e:
            cprint(f"❌ Failed to initialize OpenRouter model: {str(e)}", "red")
            self.client = None

    def generate_response(self, system_prompt, user_content, temperature=0.7, max_tokens=None, **kwargs):
        """Generate a response using OpenRouter"""
        try:
            # Prepare messages in OpenAI format
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

            cprint(f"🤔 Moon Dev's {self.model_name} is thinking via OpenRouter...", "yellow")

            # Use max_tokens if provided, otherwise use default
            token_limit = max_tokens if max_tokens else self.max_tokens

            # Create completion using OpenAI SDK format
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=token_limit,
                **kwargs
            )

            # Extract content
            content = response.choices[0].message.content

            # Return standardized response
            return ModelResponse(
                content=content,
                raw_response=response,
                model_name=self.model_name,
                usage=response.usage.model_dump() if hasattr(response, 'usage') else None
            )

        except Exception as e:
            cprint(f"❌ OpenRouter generation error: {str(e)}", "red")
            cprint(f"🔍 Model attempted: {self.model_name}", "yellow")
            cprint(f"💡 Tip: Check https://openrouter.ai/models for valid model names", "cyan")
            raise

    def is_available(self) -> bool:
        """Check if OpenRouter is available"""
        return self.client is not None

    @property
    def model_type(self) -> str:
        return "openrouter"

"""
🌙 Moon Dev's OpenRouter Model Implementation
Built with love by Moon Dev 🚀

OpenRouter provides unified access to 200+ AI models through a single API.
Perfect for accessing Claude, GPT-4, Gemini, and more with one key!
"""

from openai import OpenAI
from termcolor import cprint
from .base_model import BaseModel, ModelResponse

class OpenRouterModel(BaseModel):
    """Implementation for OpenRouter's unified API"""

    # Popular models available through OpenRouter
    AVAILABLE_MODELS = {
        # Claude models (Anthropic)
        "anthropic/claude-3.5-sonnet": {
            "description": "Claude 3.5 Sonnet - Best for complex tasks",
            "input_price": "$3.00/1M tokens",
            "output_price": "$15.00/1M tokens",
            "context": "200K"
        },
        "anthropic/claude-3-5-haiku": {
            "description": "Claude 3.5 Haiku - Fast and affordable",
            "input_price": "$0.80/1M tokens",
            "output_price": "$4.00/1M tokens",
            "context": "200K"
        },
        "anthropic/claude-3-opus": {
            "description": "Claude 3 Opus - Most powerful Claude",
            "input_price": "$15.00/1M tokens",
            "output_price": "$75.00/1M tokens",
            "context": "200K"
        },

        # OpenAI models
        "openai/gpt-4o": {
            "description": "GPT-4 Optimized - Latest OpenAI model",
            "input_price": "$2.50/1M tokens",
            "output_price": "$10.00/1M tokens",
            "context": "128K"
        },
        "openai/gpt-4o-mini": {
            "description": "GPT-4o Mini - Fast and affordable",
            "input_price": "$0.15/1M tokens",
            "output_price": "$0.60/1M tokens",
            "context": "128K"
        },
        "openai/o1-mini": {
            "description": "O1 Mini - Reasoning model",
            "input_price": "$3.00/1M tokens",
            "output_price": "$12.00/1M tokens",
            "context": "128K"
        },

        # Google models
        "google/gemini-pro-1.5": {
            "description": "Gemini 1.5 Pro - Google's latest",
            "input_price": "$1.25/1M tokens",
            "output_price": "$5.00/1M tokens",
            "context": "2M"
        },
        "google/gemini-flash-1.5": {
            "description": "Gemini 1.5 Flash - Fast inference",
            "input_price": "$0.075/1M tokens",
            "output_price": "$0.30/1M tokens",
            "context": "1M"
        },

        # Meta models
        "meta-llama/llama-3.3-70b-instruct": {
            "description": "Llama 3.3 70B - Latest Meta model",
            "input_price": "$0.35/1M tokens",
            "output_price": "$0.40/1M tokens",
            "context": "128K"
        },

        # DeepSeek
        "deepseek/deepseek-r1": {
            "description": "DeepSeek R1 - Reasoning model",
            "input_price": "$0.55/1M tokens",
            "output_price": "$2.19/1M tokens",
            "context": "64K"
        },

        # Mistral
        "mistralai/mistral-large": {
            "description": "Mistral Large - Latest Mistral model",
            "input_price": "$2.00/1M tokens",
            "output_price": "$6.00/1M tokens",
            "context": "128K"
        },

        # Default/Auto (OpenRouter picks best model)
        "openrouter/auto": {
            "description": "Auto-select best available model",
            "input_price": "Variable",
            "output_price": "Variable",
            "context": "Variable"
        }
    }

    def __init__(self, api_key: str, model_name: str = "anthropic/claude-3-5-haiku", **kwargs):
        """
        Initialize OpenRouter model

        Args:
            api_key: OpenRouter API key
            model_name: Model identifier (e.g., "anthropic/claude-3.5-sonnet")
        """
        self.model_name = model_name
        super().__init__(api_key, **kwargs)

    def initialize_client(self, **kwargs) -> None:
        """Initialize the OpenRouter client with custom base URL and headers"""
        try:
            # OpenRouter uses OpenAI-compatible API with required headers
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://openrouter.ai/api/v1",
                default_headers={
                    "HTTP-Referer": "https://moon.dev",  # Optional: for rankings
                    "X-Title": "Moon Dev Trading Bot"    # Optional: show in rankings
                }
            )
            cprint(f"✨ Moon Dev's magic initialized OpenRouter with model: {self.model_name} 🌟", "green")
            cprint(f"🔗 Using OpenRouter unified API (200+ models available)", "cyan")
        except Exception as e:
            cprint(f"❌ Failed to initialize OpenRouter: {str(e)}", "red")
            self.client = None

    def generate_response(self, system_prompt, user_content, **kwargs):
        """Generate a response using OpenRouter"""
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

            cprint(f"🤔 OpenRouter ({self.model_name}) is thinking...", "yellow")

            # Prepare kwargs
            model_kwargs = kwargs.copy()

            # Create completion
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                **model_kwargs
            )

            # Extract content
            choice = response.choices[0]
            message = choice.message
            content_text = message.content.strip() if isinstance(message.content, str) else ""

            if not content_text:
                cprint("⚠️ OpenRouter returned empty content", "yellow")

            return ModelResponse(
                content=content_text or "",
                raw_response=response,
                model_name=self.model_name,
                usage=response.usage.model_dump() if hasattr(response, 'usage') else None
            )

        except Exception as e:
            cprint(f"❌ OpenRouter generation error: {str(e)}", "red")
            try:
                if hasattr(e, 'status_code'):
                    cprint(f"🔎 Status code: {e.status_code}", "yellow")
                if hasattr(e, 'response'):
                    cprint(f"🔎 Response: {e.response}", "yellow")
            except Exception:
                pass
            raise

    def is_available(self) -> bool:
        """Check if OpenRouter is available"""
        return self.client is not None

    @property
    def model_type(self) -> str:
        return "openrouter"

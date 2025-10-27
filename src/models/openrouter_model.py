"""
🌙 Moon Dev's OpenRouter Model Implementation
Built with love by Moon Dev 🚀

OpenRouter provides access to 100+ AI models through a single API.
Compatible with OpenAI API format.
"""

from openai import OpenAI
from termcolor import cprint
from .base_model import BaseModel, ModelResponse

class OpenRouterModel(BaseModel):
    """Implementation for OpenRouter's unified model access"""

    # Popular models available via OpenRouter
    AVAILABLE_MODELS = {
        # Claude Models
        "anthropic/claude-3.5-sonnet": {
            "description": "Claude 3.5 Sonnet - Most intelligent model",
            "context": "200K tokens",
            "price": "$3/$15 per 1M tokens"
        },
        "anthropic/claude-3.5-haiku": {
            "description": "Claude 3.5 Haiku - Fast and efficient",
            "context": "200K tokens",
            "price": "$1/$5 per 1M tokens"
        },
        "anthropic/claude-3-opus": {
            "description": "Claude 3 Opus - Powerful reasoning",
            "context": "200K tokens",
            "price": "$15/$75 per 1M tokens"
        },

        # OpenAI Models
        "openai/gpt-4-turbo": {
            "description": "GPT-4 Turbo - Latest GPT-4",
            "context": "128K tokens",
            "price": "$10/$30 per 1M tokens"
        },
        "openai/gpt-4o": {
            "description": "GPT-4o - Optimized for speed",
            "context": "128K tokens",
            "price": "$5/$15 per 1M tokens"
        },
        "openai/gpt-4o-mini": {
            "description": "GPT-4o Mini - Fast and cheap",
            "context": "128K tokens",
            "price": "$0.15/$0.60 per 1M tokens"
        },
        "openai/o1-mini": {
            "description": "O1 Mini - Reasoning model",
            "context": "128K tokens",
            "price": "$3/$12 per 1M tokens"
        },

        # Google Models
        "google/gemini-2.0-flash-exp": {
            "description": "Gemini 2.0 Flash - Latest Google model",
            "context": "1M tokens",
            "price": "Free (experimental)"
        },
        "google/gemini-pro-1.5": {
            "description": "Gemini Pro 1.5 - Production ready",
            "context": "2M tokens",
            "price": "$1.25/$5 per 1M tokens"
        },

        # Meta Models
        "meta-llama/llama-3.3-70b-instruct": {
            "description": "Llama 3.3 70B - Open source powerhouse",
            "context": "128K tokens",
            "price": "$0.59/$0.79 per 1M tokens"
        },
        "meta-llama/llama-3.1-405b-instruct": {
            "description": "Llama 3.1 405B - Largest open model",
            "context": "128K tokens",
            "price": "$2.70/$2.70 per 1M tokens"
        },

        # DeepSeek Models
        "deepseek/deepseek-chat": {
            "description": "DeepSeek Chat - Cost effective",
            "context": "64K tokens",
            "price": "$0.14/$0.28 per 1M tokens"
        },
        "deepseek/deepseek-r1": {
            "description": "DeepSeek R1 - Advanced reasoning",
            "context": "64K tokens",
            "price": "$0.55/$2.19 per 1M tokens"
        },

        # Mistral Models
        "mistralai/mistral-large": {
            "description": "Mistral Large - Flagship model",
            "context": "128K tokens",
            "price": "$2/$6 per 1M tokens"
        },
        "mistralai/mixtral-8x22b-instruct": {
            "description": "Mixtral 8x22B - MoE architecture",
            "context": "64K tokens",
            "price": "$0.65/$0.65 per 1M tokens"
        },

        # Qwen Models
        "qwen/qwen-2.5-72b-instruct": {
            "description": "Qwen 2.5 72B - Multilingual",
            "context": "32K tokens",
            "price": "$0.35/$0.40 per 1M tokens"
        },

        # Auto-routing (OpenRouter selects best model)
        "openrouter/auto": {
            "description": "Auto - OpenRouter picks the best model for your request",
            "context": "Varies",
            "price": "Varies by selected model"
        }
    }

    def __init__(self, api_key: str, model_name: str = "anthropic/claude-3.5-haiku", **kwargs):
        """
        Initialize OpenRouter model

        Args:
            api_key: OpenRouter API key
            model_name: Model identifier (e.g., "anthropic/claude-3.5-haiku")
            **kwargs: Additional parameters
        """
        self.model_name = model_name
        self.max_tokens = kwargs.get('max_tokens', 4096)
        super().__init__(api_key, **kwargs)

    def initialize_client(self, **kwargs) -> None:
        """Initialize the OpenRouter client using OpenAI SDK"""
        try:
            # OpenRouter uses OpenAI-compatible API with custom base URL
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://openrouter.ai/api/v1"
            )
            cprint(f"✨ Moon Dev's magic initialized OpenRouter with model: {self.model_name} 🌟", "green")

            # Show model info if available
            if self.model_name in self.AVAILABLE_MODELS:
                info = self.AVAILABLE_MODELS[self.model_name]
                cprint(f"📊 {info['description']}", "cyan")
                cprint(f"📏 Context: {info['context']}", "cyan")
                cprint(f"💰 Pricing: {info['price']}", "cyan")

        except Exception as e:
            cprint(f"❌ Failed to initialize OpenRouter model: {str(e)}", "red")
            self.client = None

    def generate_response(self, system_prompt, user_content, temperature=0.7, max_tokens=None, **kwargs):
        """
        Generate a response using OpenRouter

        Args:
            system_prompt: System instructions
            user_content: User message
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters

        Returns:
            ModelResponse object with content and metadata
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

            cprint(f"🤔 Moon Dev's OpenRouter ({self.model_name}) is thinking...", "yellow")

            # Prepare request parameters
            request_params = {
                "model": self.model_name,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens if max_tokens else self.max_tokens
            }

            # Add optional parameters
            if 'top_p' in kwargs:
                request_params['top_p'] = kwargs['top_p']
            if 'frequency_penalty' in kwargs:
                request_params['frequency_penalty'] = kwargs['frequency_penalty']
            if 'presence_penalty' in kwargs:
                request_params['presence_penalty'] = kwargs['presence_penalty']

            # Create completion
            response = self.client.chat.completions.create(**request_params)

            # Extract content
            choice = response.choices[0]
            message = choice.message
            content_text = getattr(message, 'content', '')

            if isinstance(content_text, str):
                content_text = content_text.strip()
            else:
                content_text = str(content_text).strip()

            if not content_text:
                cprint("⚠️ OpenRouter returned empty content", "yellow")
                content_text = ""

            # Get usage stats if available
            usage = None
            if hasattr(response, 'usage'):
                usage = {
                    'prompt_tokens': getattr(response.usage, 'prompt_tokens', 0),
                    'completion_tokens': getattr(response.usage, 'completion_tokens', 0),
                    'total_tokens': getattr(response.usage, 'total_tokens', 0)
                }

            cprint(f"✅ Response received from {self.model_name}", "green")
            if usage:
                cprint(f"📊 Tokens used: {usage['total_tokens']} (prompt: {usage['prompt_tokens']}, completion: {usage['completion_tokens']})", "cyan")

            return ModelResponse(
                content=content_text,
                raw_response=response,
                model_name=self.model_name,
                usage=usage
            )

        except Exception as e:
            cprint(f"❌ OpenRouter generation error: {repr(e)}", "red")

            # Print detailed error info
            try:
                if hasattr(e, 'status_code'):
                    cprint(f"🔎 Status code: {e.status_code}", "yellow")
                if hasattr(e, 'response'):
                    cprint(f"🔎 Response: {e.response}", "yellow")
            except:
                pass

            raise

    def is_available(self) -> bool:
        """Check if OpenRouter client is available"""
        return self.client is not None

    @property
    def model_type(self) -> str:
        """Return model type identifier"""
        return "openrouter"

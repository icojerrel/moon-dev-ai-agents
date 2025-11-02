"""
🌙 Moon Dev's OpenRouter Model Implementation
Built with love by Moon Dev 🚀

OpenRouter provides access to ALL AI models through a single API key:
- OpenAI (GPT-4, GPT-4o, O1, etc.)
- Anthropic (Claude 3.5 Haiku, Sonnet, Opus)
- DeepSeek (Reasoner, Chat)
- Google (Gemini)
- xAI (Grok)
- Meta (Llama)
- And many more!

Benefits:
- Single API key for all models
- Cost tracking across providers
- Automatic fallbacks
- Rate limit handling
"""

from openai import OpenAI
from termcolor import cprint
from .base_model import BaseModel, ModelResponse

class OpenRouterModel(BaseModel):
    """Implementation for OpenRouter's unified AI model access"""

    # Popular models available through OpenRouter
    # Format: "provider/model-name"
    AVAILABLE_MODELS = {
        # OpenAI Models
        "openai/gpt-4o": {
            "description": "GPT-4 Optimized - Fast and capable",
            "context": "128K tokens",
            "pricing": "Competitive"
        },
        "openai/o1-mini": {
            "description": "O1 Mini - Reasoning model",
            "context": "128K tokens",
            "pricing": "Budget-friendly"
        },
        "openai/gpt-4o-mini": {
            "description": "GPT-4o Mini - Efficient",
            "context": "128K tokens",
            "pricing": "Very cheap"
        },

        # Anthropic Models
        "anthropic/claude-3.5-haiku": {
            "description": "Claude 3.5 Haiku - Fast and smart",
            "context": "200K tokens",
            "pricing": "Affordable"
        },
        "anthropic/claude-3-5-haiku-latest": {
            "description": "Claude 3.5 Haiku Latest",
            "context": "200K tokens",
            "pricing": "Affordable"
        },
        "anthropic/claude-3.5-sonnet": {
            "description": "Claude 3.5 Sonnet - Balanced",
            "context": "200K tokens",
            "pricing": "Mid-range"
        },
        "anthropic/claude-3-opus": {
            "description": "Claude 3 Opus - Most capable",
            "context": "200K tokens",
            "pricing": "Premium"
        },

        # DeepSeek Models
        "deepseek/deepseek-chat": {
            "description": "DeepSeek Chat - Fast and cheap",
            "context": "64K tokens",
            "pricing": "Very cheap"
        },
        "deepseek/deepseek-reasoner": {
            "description": "DeepSeek R1 - Reasoning model",
            "context": "64K tokens",
            "pricing": "Cheap"
        },

        # Google Models
        "google/gemini-2.0-flash-exp": {
            "description": "Gemini 2.0 Flash - Latest",
            "context": "1M tokens",
            "pricing": "Free tier available"
        },
        "google/gemini-flash-1.5": {
            "description": "Gemini 1.5 Flash",
            "context": "1M tokens",
            "pricing": "Affordable"
        },

        # xAI Models
        "x-ai/grok-beta": {
            "description": "Grok Beta - xAI's model",
            "context": "128K tokens",
            "pricing": "Premium"
        },

        # Meta Models
        "meta-llama/llama-3.3-70b-instruct": {
            "description": "Llama 3.3 70B - Open source",
            "context": "128K tokens",
            "pricing": "Very cheap"
        },
    }

    # Default model (fast and cheap)
    DEFAULT_MODEL = "anthropic/claude-3.5-haiku"

    def __init__(self, api_key: str, model_name: str = None, **kwargs):
        """
        Initialize OpenRouter model

        Args:
            api_key: OpenRouter API key (from OPENROUTER_KEY env var)
            model_name: Model to use (e.g., "anthropic/claude-3.5-haiku")
            **kwargs: Additional arguments
        """
        self.model_name = model_name or self.DEFAULT_MODEL
        super().__init__(api_key, **kwargs)

    def initialize_client(self, **kwargs) -> None:
        """Initialize the OpenRouter client (OpenAI-compatible)"""
        try:
            # OpenRouter uses OpenAI-compatible API
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://openrouter.ai/api/v1"
            )
            cprint(f"✨ Moon Dev's OpenRouter initialized: {self.model_name} 🌟", "green")
            cprint(f"🌐 Access to ALL AI models through one API key!", "cyan")
        except Exception as e:
            cprint(f"❌ Failed to initialize OpenRouter: {str(e)}", "red")
            self.client = None

    def generate_response(self, system_prompt, user_content, **kwargs):
        """
        Generate a response using OpenRouter

        Args:
            system_prompt: System instructions
            user_content: User message/query
            **kwargs: Additional parameters (temperature, max_tokens, etc.)

        Returns:
            ModelResponse with content and metadata
        """
        try:
            # Prepare messages
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

            # Prepare kwargs for API call
            api_kwargs = {}

            # Add temperature if specified
            if 'temperature' in kwargs:
                api_kwargs['temperature'] = kwargs['temperature']

            # Add max_tokens if specified
            if 'max_tokens' in kwargs:
                api_kwargs['max_tokens'] = kwargs['max_tokens']

            # OpenRouter-specific headers for tracking
            extra_headers = {
                "HTTP-Referer": "https://github.com/moondev",  # Replace with your URL
                "X-Title": "Moon Dev AI Agents"
            }

            # Create completion
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                extra_headers=extra_headers,
                **api_kwargs
            )

            # Extract content
            choice = response.choices[0]
            message = choice.message
            content_text = ""

            if hasattr(message, 'content'):
                if isinstance(message.content, str):
                    content_text = message.content.strip()
                elif isinstance(message.content, list):
                    # Handle structured content
                    parts = []
                    for part in message.content:
                        if isinstance(part, dict):
                            text_val = part.get('text') or part.get('content')
                            if isinstance(text_val, str):
                                parts.append(text_val)
                        elif isinstance(part, str):
                            parts.append(part)
                        else:
                            text_val = getattr(part, 'text', None)
                            if isinstance(text_val, str):
                                parts.append(text_val)
                    content_text = "".join(parts).strip()

            if not content_text:
                cprint("⚠️ OpenRouter returned empty content", "yellow")

            # Get usage stats if available
            usage = None
            if hasattr(response, 'usage'):
                usage = response.usage.model_dump() if hasattr(response.usage, 'model_dump') else None

            return ModelResponse(
                content=content_text or "",
                raw_response=response,
                model_name=self.model_name,
                usage=usage
            )

        except Exception as e:
            cprint(f"❌ OpenRouter generation error: {repr(e)}", "red")
            try:
                if hasattr(e, 'status_code'):
                    cprint(f"🔎 Status code: {getattr(e, 'status_code', None)}", "yellow")
                if hasattr(e, 'code'):
                    cprint(f"🔎 Error code: {getattr(e, 'code', None)}", "yellow")
            except:
                pass
            raise

    def is_available(self) -> bool:
        """Check if OpenRouter is available"""
        return self.client is not None

    @property
    def model_type(self) -> str:
        return "openrouter"

    @classmethod
    def list_models(cls):
        """List all available models through OpenRouter"""
        cprint("\n🌐 Available Models through OpenRouter:", "cyan")
        cprint("=" * 60, "cyan")

        for model_id, info in cls.AVAILABLE_MODELS.items():
            cprint(f"\n📦 {model_id}", "green")
            cprint(f"   Description: {info['description']}", "white")
            cprint(f"   Context: {info['context']}", "yellow")
            cprint(f"   Pricing: {info['pricing']}", "cyan")

        cprint(f"\n💡 Default model: {cls.DEFAULT_MODEL}", "green")
        cprint("=" * 60, "cyan")

"""
🌙 Moon Dev's OpenRouter Model Implementation
Built with love by Moon Dev 🚀

OpenRouter provides unified access to ALL AI models through a single API.
No need for multiple API keys - just one OpenRouter key for everything!
"""

from openai import OpenAI
from termcolor import cprint
from .base_model import BaseModel, ModelResponse
import time
import re

class OpenRouterModel(BaseModel):
    """Implementation for OpenRouter - unified access to all AI models"""

    # Popular models available through OpenRouter
    # Full list at: https://openrouter.ai/models
    AVAILABLE_MODELS = {
        # Qwen Models (Chinese AI - Vision & Language)
        "qwen/qwen3-vl-32b-instruct": {
            "description": "Qwen 3 VL 32B - Vision & Language - 32k context",
            "input_price": "$0.25/1M tokens",
            "output_price": "$0.25/1M tokens"
        },
        "qwen/qwen3-max": {
            "description": "Qwen 3 Max - Flagship model - 32k context",
            "input_price": "$1.00/1M tokens",
            "output_price": "$1.00/1M tokens"
        },

        # Google Gemini Models (Updated to 2.5)
        "google/gemini-2.5-pro": {
            "description": "Gemini 2.5 Pro - Advanced reasoning - 128k context",
            "input_price": "$1.25/1M tokens",
            "output_price": "$5.00/1M tokens"
        },
        "google/gemini-2.5-flash": {
            "description": "Gemini 2.5 Flash - Fast multimodal - 1M context",
            "input_price": "$0.10/1M tokens",
            "output_price": "$0.40/1M tokens"
        },

        # Zhipu AI GLM Models
        "z-ai/glm-4.6": {
            "description": "GLM 4.6 - Zhipu AI - 128k context",
            "input_price": "$0.50/1M tokens",
            "output_price": "$0.50/1M tokens"
        },

        # DeepSeek Models (EXCELLENT for trading!)
        "deepseek/deepseek-r1-0528": {
            "description": "DeepSeek R1 - Advanced reasoning - 64k context",
            "input_price": "$0.55/1M tokens",
            "output_price": "$2.19/1M tokens"
        },
        "deepseek/deepseek-r1": {
            "description": "DeepSeek R1 - Reasoning model - EXCELLENT for trading",
            "input_price": "$0.55/1M tokens",
            "output_price": "$2.19/1M tokens"
        },
        "deepseek/deepseek-chat": {
            "description": "DeepSeek Chat - Fast chat model",
            "input_price": "$0.14/1M tokens",
            "output_price": "$0.28/1M tokens"
        },

        # OpenAI GPT-5 Models (Latest!)
        "openai/gpt-5": {
            "description": "GPT-5 - Next-gen OpenAI model - 200k context",
            "input_price": "See openrouter.ai/docs",
            "output_price": "See openrouter.ai/docs"
        },
        "openai/gpt-5-mini": {
            "description": "GPT-5 Mini - Fast & efficient - 128k context",
            "input_price": "See openrouter.ai/docs",
            "output_price": "See openrouter.ai/docs"
        },
        "openai/gpt-5-nano": {
            "description": "GPT-5 Nano - Ultra-fast & cheap - 64k context",
            "input_price": "See openrouter.ai/docs",
            "output_price": "See openrouter.ai/docs"
        },
        "openai/gpt-4.5-preview": {
            "description": "GPT-4.5 Preview - Latest OpenAI flagship - 128k context",
            "input_price": "See openrouter.ai/docs",
            "output_price": "See openrouter.ai/docs"
        },

        # OpenAI GPT-4 Models
        "openai/gpt-4o": {
            "description": "Latest GPT-4 Optimized model",
            "input_price": "$2.50/1M tokens",
            "output_price": "$10.00/1M tokens"
        },
        "openai/gpt-4o-mini": {
            "description": "Efficient GPT-4 Optimized mini model",
            "input_price": "$0.15/1M tokens",
            "output_price": "$0.60/1M tokens"
        },
        "openai/o1": {
            "description": "Latest O1 reasoning model",
            "input_price": "$15.00/1M tokens",
            "output_price": "$60.00/1M tokens"
        },
        "openai/o1-mini": {
            "description": "Smaller O1 reasoning model",
            "input_price": "$3.00/1M tokens",
            "output_price": "$12.00/1M tokens"
        },

        # Anthropic Claude 4.5 Models (Latest!)
        "anthropic/claude-sonnet-4.5": {
            "description": "Claude Sonnet 4.5 - Balanced performance - 200k context",
            "input_price": "See openrouter.ai/docs",
            "output_price": "See openrouter.ai/docs"
        },
        "anthropic/claude-haiku-4.5": {
            "description": "Claude Haiku 4.5 - Fast & efficient - 200k context",
            "input_price": "See openrouter.ai/docs",
            "output_price": "See openrouter.ai/docs"
        },
        "anthropic/claude-opus-4.1": {
            "description": "Claude Opus 4.1 - Most powerful - 200k context",
            "input_price": "See openrouter.ai/docs",
            "output_price": "See openrouter.ai/docs"
        },

        # Anthropic Claude 3.5 Models
        "anthropic/claude-3.5-sonnet": {
            "description": "Claude 3.5 Sonnet - Best for complex tasks",
            "input_price": "$3.00/1M tokens",
            "output_price": "$15.00/1M tokens"
        },
        "anthropic/claude-3-opus": {
            "description": "Most powerful Claude 3 model",
            "input_price": "$15.00/1M tokens",
            "output_price": "$75.00/1M tokens"
        },
        "anthropic/claude-3-haiku": {
            "description": "Fast, efficient Claude 3 model",
            "input_price": "$0.25/1M tokens",
            "output_price": "$1.25/1M tokens"
        },

        # Meta Llama Models
        "meta-llama/llama-3.3-70b-instruct": {
            "description": "Latest Llama 3.3 70B model",
            "input_price": "$0.35/1M tokens",
            "output_price": "$0.40/1M tokens"
        },
        "meta-llama/llama-3.1-405b-instruct": {
            "description": "Massive Llama 3.1 405B model",
            "input_price": "$2.70/1M tokens",
            "output_price": "$2.70/1M tokens"
        },

        # xAI Grok Models
        "x-ai/grok-2": {
            "description": "xAI's Grok 2 model",
            "input_price": "$2.00/1M tokens",
            "output_price": "$10.00/1M tokens"
        },
        "x-ai/grok-beta": {
            "description": "Latest Grok beta with enhanced capabilities",
            "input_price": "$5.00/1M tokens",
            "output_price": "$15.00/1M tokens"
        },

        # Mistral Models
        "mistralai/mistral-large": {
            "description": "Mistral's largest model",
            "input_price": "$2.00/1M tokens",
            "output_price": "$6.00/1M tokens"
        },

        # Cohere Models
        "cohere/command-r-plus": {
            "description": "Cohere's command model with RAG",
            "input_price": "$2.50/1M tokens",
            "output_price": "$10.00/1M tokens"
        },

        # Moonshot AI Models
        "moonshotai/kimi-k2-0905": {
            "description": "Kimi K2 0905 - 1T params MoE, 256k context - Excellent for coding",
            "input_price": "$1.00/1M tokens",
            "output_price": "$3.00/1M tokens"
        }
    }

    def __init__(self, api_key: str, model_name: str = "google/gemini-2.5-flash", **kwargs):
        """
        Initialize OpenRouter model

        Args:
            api_key: Your OpenRouter API key from https://openrouter.ai/keys
            model_name: Model to use (format: provider/model-name)
        """
        try:
            cprint(f"\n🌙 Moon Dev's OpenRouter Model Initialization", "cyan")

            # Validate API key
            if not api_key or len(api_key.strip()) == 0:
                raise ValueError("API key is empty or None")

            cprint(f"🔑 API Key validation:", "cyan")
            cprint(f"  ├─ Length: {len(api_key)} chars", "cyan")
            cprint(f"  ├─ Contains whitespace: {'yes' if any(c.isspace() for c in api_key) else 'no'}", "cyan")
            cprint(f"  └─ Starts with 'sk-or-': {'yes' if api_key.startswith('sk-or-') else 'no'}", "cyan")

            # Validate model name
            cprint(f"\n📝 Model validation:", "cyan")
            cprint(f"  ├─ Requested: {model_name}", "cyan")
            if model_name not in self.AVAILABLE_MODELS:
                cprint(f"  └─ ⚠️ Model not in predefined list (will still try to use it)", "yellow")
                cprint(f"  💡 OpenRouter supports 200+ models - see https://openrouter.ai/docs", "cyan")
            else:
                cprint(f"  └─ ✅ Model name recognized", "green")

            self.model_name = model_name
            self.max_tokens = 4096  # Default max tokens

            cprint(f"\n📡 Parent class initialization...", "cyan")
            super().__init__(api_key, **kwargs)
            cprint(f"✅ Parent class initialized", "green")

        except Exception as e:
            cprint(f"\n❌ Error in OpenRouter model initialization", "red")
            cprint(f"  ├─ Error type: {type(e).__name__}", "red")
            cprint(f"  ├─ Error message: {str(e)}", "red")
            if "api_key" in str(e).lower():
                cprint(f"  ├─ 🔑 This appears to be an API key issue", "red")
                cprint(f"  └─ Please check your OPENROUTER_API_KEY in .env", "red")
            elif "model" in str(e).lower():
                cprint(f"  ├─ 🤖 This appears to be a model name issue", "red")
                cprint(f"  └─ See all models at: https://openrouter.ai/docs", "red")
            raise

    def initialize_client(self, **kwargs) -> None:
        """Initialize the OpenRouter client using OpenAI SDK with custom base URL"""
        try:
            cprint(f"\n🔌 Initializing OpenRouter client...", "cyan")
            cprint(f"  ├─ API Key length: {len(self.api_key)} chars", "cyan")
            cprint(f"  ├─ Model name: {self.model_name}", "cyan")

            cprint(f"\n  ├─ Creating OpenRouter client (via OpenAI SDK)...", "cyan")
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://openrouter.ai/api/v1"
            )
            cprint(f"  ├─ ✅ OpenRouter client created", "green")

            # Test connection with a simple request
            cprint(f"  ├─ Testing connection with model: {self.model_name}", "cyan")
            test_response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            cprint(f"  ├─ ✅ Test response received", "green")
            cprint(f"  ├─ Response content: {test_response.choices[0].message.content}", "cyan")

            # Show model info
            model_info = self.AVAILABLE_MODELS.get(self.model_name, {
                "description": "Custom model via OpenRouter",
                "input_price": "See openrouter.ai/docs",
                "output_price": "See openrouter.ai/docs"
            })
            cprint(f"  ├─ ✨ OpenRouter model initialized: {self.model_name}", "green")
            cprint(f"  ├─ Model info: {model_info.get('description', '')}", "cyan")
            cprint(f"  └─ Pricing: Input {model_info.get('input_price', '')} | Output {model_info.get('output_price', '')}", "yellow")

        except Exception as e:
            cprint(f"\n❌ Failed to initialize OpenRouter client", "red")
            cprint(f"  ├─ Error type: {type(e).__name__}", "red")
            cprint(f"  ├─ Error message: {str(e)}", "red")

            if "api_key" in str(e).lower() or "401" in str(e):
                cprint(f"  ├─ 🔑 This appears to be an API key issue", "red")
                cprint(f"  ├─ Make sure your OPENROUTER_API_KEY is correct", "red")
                cprint(f"  ├─ Get your key at: https://openrouter.ai/keys", "red")
                cprint(f"  └─ Key length: {len(self.api_key)} chars", "red")
            elif "model" in str(e).lower():
                cprint(f"  ├─ 🤖 This appears to be a model name issue", "red")
                cprint(f"  ├─ Requested model: {self.model_name}", "red")
                cprint(f"  └─ See all models at: https://openrouter.ai/docs", "red")

            if hasattr(e, 'response'):
                cprint(f"  ├─ Response status: {e.response.status_code}", "red")
                cprint(f"  └─ Response body: {e.response.text}", "red")

            if hasattr(e, '__traceback__'):
                import traceback
                cprint(f"\n📋 Full traceback:", "red")
                cprint(traceback.format_exc(), "red")

            self.client = None
            raise

    def generate_response(self, system_prompt, user_content, temperature=0.7, max_tokens=None, **kwargs):
        """Generate a response using OpenRouter with anti-caching and <think> tag filtering"""
        try:
            # Add millisecond timestamp to prevent caching
            timestamp = int(time.time() * 1000)

            # Create completion using OpenAI SDK format
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"{user_content}_{timestamp}"}
                ],
                temperature=temperature,
                max_tokens=max_tokens if max_tokens else self.max_tokens,
                stream=False,
                **kwargs
            )

            # Extract content
            raw_content = response.choices[0].message.content

            # Filter out <think> tags from reasoning models (DeepSeek R1, etc.)
            filtered_content = re.sub(r'<think>.*?</think>', '', raw_content, flags=re.DOTALL).strip()

            # Also handle cases where </think> is missing
            if '<think>' in filtered_content:
                filtered_content = filtered_content.split('<think>')[0].strip()

            # Use filtered content if available, otherwise use raw
            final_content = filtered_content if filtered_content else raw_content

            # Return standardized response
            return ModelResponse(
                content=final_content,
                raw_response=response,
                model_name=self.model_name,
                usage=response.usage
            )

        except Exception as e:
            error_str = str(e)

            # Handle rate limiting gracefully
            if "429" in error_str or "rate_limit" in error_str:
                cprint(f"⚠️  OpenRouter rate limit exceeded", "yellow")
                cprint(f"   Model: {self.model_name}", "yellow")
                cprint(f"   💡 Skipping this model for this request...", "cyan")
                return None

            # Handle insufficient credits
            if "402" in error_str or "insufficient" in error_str:
                cprint(f"⚠️  OpenRouter credits insufficient", "yellow")
                cprint(f"   Model: {self.model_name}", "yellow")
                cprint(f"   💡 Add credits at: https://openrouter.ai/credits", "cyan")
                return None

            # Re-raise 503 for retry logic
            if "503" in error_str:
                raise e

            # Other errors
            cprint(f"❌ OpenRouter error: {error_str}", "red")
            return None

    def is_available(self) -> bool:
        """Check if OpenRouter is available"""
        return self.client is not None

    @property
    def model_type(self) -> str:
        return "openrouter"

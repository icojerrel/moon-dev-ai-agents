"""
🌙 Moon Dev's OpenRouter Model Implementation
Built with love by Moon Dev 🚀

OpenRouter provides unified access to multiple LLM providers with one API key.
More info: https://openrouter.ai
"""

from openai import OpenAI
from termcolor import cprint
from .base_model import BaseModel, ModelResponse

class OpenRouterModel(BaseModel):
    """Implementation for OpenRouter's unified LLM API"""

    # OpenRouter provides access to all these models and more!
    AVAILABLE_MODELS = {
        # DeepSeek (Recommended - Best value)
        "deepseek/deepseek-chat": "DeepSeek Chat - Fast, cheap, high quality",
        "deepseek/deepseek-reasoner": "DeepSeek Reasoner - Enhanced reasoning",
        "deepseek/deepseek-r1": "DeepSeek R1 - Latest reasoning model",

        # Anthropic Claude (Premium)
        "anthropic/claude-3.5-sonnet": "Claude 3.5 Sonnet - Best overall",
        "anthropic/claude-3-haiku": "Claude 3 Haiku - Fast and cheap",
        "anthropic/claude-3-opus": "Claude 3 Opus - Most capable",

        # OpenAI GPT (Popular)
        "openai/gpt-4o": "GPT-4 Optimized - Latest and fastest",
        "openai/gpt-4-turbo": "GPT-4 Turbo - Fast GPT-4",
        "openai/gpt-3.5-turbo": "GPT-3.5 Turbo - Cheap and fast",

        # Google Gemini
        "google/gemini-2.0-flash-exp": "Gemini 2.0 Flash - Latest fast model",
        "google/gemini-pro-1.5": "Gemini Pro 1.5 - Balanced",

        # Meta Llama (Open source)
        "meta-llama/llama-3.2-90b-instruct": "Llama 3.2 90B - Large open model",
        "meta-llama/llama-3.1-70b-instruct": "Llama 3.1 70B - Balanced open model",
        "meta-llama/llama-3.1-8b-instruct": "Llama 3.1 8B - Fast open model",

        # Mistral
        "mistralai/mistral-large": "Mistral Large - Most capable",
        "mistralai/mistral-medium": "Mistral Medium - Balanced",
        "mistralai/mixtral-8x7b-instruct": "Mixtral 8x7B - MoE model",

        # xAI Grok
        "x-ai/grok-2": "Grok 2 - xAI's latest model",

        # Cohere
        "cohere/command-r-plus": "Command R+ - Good for RAG",

        # Qwen (Alibaba)
        "qwen/qwen-2.5-72b-instruct": "Qwen 2.5 72B - Chinese + English",
    }

    def __init__(self, api_key: str, model_name: str = "deepseek/deepseek-chat", base_url: str = "https://openrouter.ai/api/v1", **kwargs):
        self.model_name = model_name
        self.base_url = base_url
        # OpenRouter requires these headers
        self.extra_headers = {
            "HTTP-Referer": "https://github.com/moon-dev-ai",  # Your site URL
            "X-Title": "Moon Dev AI Trading System"  # Your app name
        }
        super().__init__(api_key, **kwargs)

    def initialize_client(self, **kwargs) -> None:
        """Initialize the OpenRouter client"""
        try:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                default_headers=self.extra_headers
            )
            cprint(f"✨ Initialized OpenRouter model: {self.model_name}", "green")
            cprint(f"   Base URL: {self.base_url}", "cyan")
        except Exception as e:
            cprint(f"❌ Failed to initialize OpenRouter model: {str(e)}", "red")
            self.client = None

    def generate_response(self,
        system_prompt: str,
        user_content: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs
    ) -> ModelResponse:
        """Generate a response using OpenRouter"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False
            )

            return ModelResponse(
                content=response.choices[0].message.content.strip(),
                raw_response=response,
                model_name=self.model_name,
                usage=response.usage.model_dump() if hasattr(response, 'usage') else None
            )

        except Exception as e:
            cprint(f"❌ OpenRouter generation error: {str(e)}", "red")
            cprint(f"   Model: {self.model_name}", "yellow")
            cprint(f"   Check: https://openrouter.ai/models for available models", "yellow")
            raise

    def is_available(self) -> bool:
        """Check if OpenRouter is available"""
        return self.client is not None

    @property
    def model_type(self) -> str:
        return "openrouter"

    def get_cost_info(self) -> dict:
        """
        Get pricing information for current model
        OpenRouter shows real-time pricing at: https://openrouter.ai/models
        """
        # This is a placeholder - actual costs are shown on OpenRouter dashboard
        return {
            "model": self.model_name,
            "pricing_url": f"https://openrouter.ai/models/{self.model_name}",
            "note": "Check OpenRouter dashboard for real-time pricing"
        }

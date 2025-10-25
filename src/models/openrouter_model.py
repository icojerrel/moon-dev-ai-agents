"""
🌙 Moon Dev's OpenRouter Model Implementation
Access to 100+ AI models through one unified API
Built with love by Moon Dev 🚀
"""

from openai import OpenAI
from termcolor import cprint
from .base_model import BaseModel, ModelResponse
from typing import Optional, Dict, Any, List
import os
import json


class OpenRouterError(Exception):
    """Base exception for OpenRouter errors"""
    def __init__(self, code: int, message: str, metadata: Optional[Dict[str, Any]] = None):
        self.code = code
        self.message = message
        self.metadata = metadata or {}
        super().__init__(f"OpenRouter Error {code}: {message}")


class ModerationError(OpenRouterError):
    """Exception for content moderation errors (403)"""
    def __init__(self, message: str, metadata: Dict[str, Any]):
        super().__init__(403, message, metadata)
        self.reasons = metadata.get('reasons', [])
        self.flagged_input = metadata.get('flagged_input', '')
        self.provider_name = metadata.get('provider_name', '')
        self.model_slug = metadata.get('model_slug', '')


class ProviderError(OpenRouterError):
    """Exception for provider-level errors"""
    def __init__(self, code: int, message: str, metadata: Dict[str, Any]):
        super().__init__(code, message, metadata)
        self.provider_name = metadata.get('provider_name', '')
        self.raw_error = metadata.get('raw')


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

    def _parse_error(self, error: Exception) -> OpenRouterError:
        """Parse error from OpenRouter API

        Error Codes:
        - 400: Bad Request (invalid or missing params, CORS)
        - 401: Invalid credentials (OAuth expired, disabled/invalid API key)
        - 402: Insufficient credits
        - 403: Moderation flagged
        - 408: Request timeout
        - 429: Rate limited
        - 502: Bad Gateway (model down or invalid response)
        - 503: Service Unavailable (no provider meets routing requirements)

        Args:
            error: Exception from OpenAI client

        Returns:
            OpenRouterError with parsed details
        """
        error_str = str(error)

        # Try to extract error code and parse response
        try:
            # Check if it's an OpenAI API error with response
            if hasattr(error, 'response') and error.response:
                try:
                    error_data = error.response.json()
                    if 'error' in error_data:
                        err = error_data['error']
                        code = err.get('code', 500)
                        message = err.get('message', str(error))
                        metadata = err.get('metadata', {})

                        # 403 with moderation metadata
                        if code == 403 and metadata:
                            return ModerationError(message, metadata)

                        # Provider error with metadata
                        if metadata and 'provider_name' in metadata:
                            return ProviderError(code, message, metadata)

                        return OpenRouterError(code, message, metadata)
                except:
                    pass

            # Parse from error string if possible
            if "401" in error_str or "Invalid credentials" in error_str:
                return OpenRouterError(401, "Invalid API key or OAuth session expired")
            elif "402" in error_str or "insufficient credits" in error_str.lower():
                return OpenRouterError(402, "Insufficient credits. Add more credits and retry.")
            elif "403" in error_str or "Access denied" in error_str:
                return OpenRouterError(403, "Access denied. Check your OpenRouter account settings:\n"
                                           "  1. Privacy Settings → Enable 'Model Training'\n"
                                           "  2. Provider Settings → Unblock ALL providers\n"
                                           "  3. Verify API key is active\n"
                                           "  4. Check payment method is added")
            elif "408" in error_str or "timeout" in error_str.lower():
                return OpenRouterError(408, "Request timed out")
            elif "429" in error_str or "rate limit" in error_str.lower():
                return OpenRouterError(429, "Rate limited. Wait and retry.")
            elif "502" in error_str:
                return OpenRouterError(502, "Model is down or returned invalid response")
            elif "503" in error_str:
                return OpenRouterError(503, "No available provider meets routing requirements")

        except Exception as parse_err:
            cprint(f"⚠️  Error parsing OpenRouter error: {parse_err}", "yellow")

        # Fallback
        return OpenRouterError(500, str(error))

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

        Raises:
            OpenRouterError: For API errors with detailed error info
            ModerationError: When content is flagged (403 with moderation metadata)
            ProviderError: When provider encounters an error
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
            # Parse and re-raise as OpenRouter-specific error
            parsed_error = self._parse_error(e)

            # Print detailed error info
            cprint(f"❌ OpenRouter Error {parsed_error.code}: {parsed_error.message}", "red")

            if isinstance(parsed_error, ModerationError):
                cprint(f"🚨 Content Moderation:", "yellow")
                cprint(f"   Reasons: {', '.join(parsed_error.reasons)}", "yellow")
                cprint(f"   Flagged: {parsed_error.flagged_input}", "yellow")
                cprint(f"   Provider: {parsed_error.provider_name}", "yellow")
            elif isinstance(parsed_error, ProviderError):
                cprint(f"⚠️  Provider: {parsed_error.provider_name}", "yellow")
                if parsed_error.raw_error:
                    cprint(f"   Raw error: {parsed_error.raw_error}", "yellow")

            raise parsed_error

    def is_available(self) -> bool:
        """Check if OpenRouter is available and working

        Returns:
            bool: True if OpenRouter API is accessible and working
        """
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
            parsed_error = self._parse_error(e)
            cprint(f"⚠️ OpenRouter not available: {parsed_error.message}", "yellow")

            # Show actionable steps for common errors
            if parsed_error.code == 403:
                cprint("\n🔧 Troubleshooting Steps:", "cyan")
                cprint("   1. Visit: https://openrouter.ai/settings/privacy", "white")
                cprint("      → Enable 'Model Training'", "white")
                cprint("   2. Visit: https://openrouter.ai/settings/providers", "white")
                cprint("      → Unblock ALL 'Ignored Providers'", "white")
                cprint("      → Clear 'Allowed Providers' (leave empty)", "white")
                cprint("      → Click 'Save'", "white")
                cprint("   3. Visit: https://openrouter.ai/settings/keys", "white")
                cprint("      → Verify API key is ACTIVE (green)", "white")
                cprint("   4. Visit: https://openrouter.ai/settings/credits", "white")
                cprint("      → Add payment method if needed\n", "white")
            elif parsed_error.code == 402:
                cprint("\n💳 Add credits: https://openrouter.ai/settings/credits\n", "cyan")
            elif parsed_error.code == 401:
                cprint("\n🔑 Check API key: https://openrouter.ai/settings/keys\n", "cyan")

            return False

    def list_available_models(self) -> List[Dict[str, Any]]:
        """Fetch list of all available models from OpenRouter API

        Returns:
            List of model dictionaries with pricing, capabilities, etc.

        Raises:
            OpenRouterError: If API request fails
        """
        try:
            import requests

            cprint("🔍 Fetching available models from OpenRouter...", "cyan")

            response = requests.get(
                "https://openrouter.ai/api/v1/models",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )

            if response.status_code != 200:
                raise OpenRouterError(response.status_code, response.text)

            data = response.json()
            models = data.get('data', [])

            cprint(f"✅ Found {len(models)} available models", "green")
            return models

        except Exception as e:
            parsed_error = self._parse_error(e)
            cprint(f"❌ Failed to fetch models: {parsed_error.message}", "red")
            raise parsed_error

    def find_cheapest_models(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """Find the cheapest available models

        Args:
            top_n: Number of cheapest models to return

        Returns:
            List of cheapest models sorted by total cost (input + output)
        """
        try:
            models = self.list_available_models()

            # Calculate total cost per million tokens (avg of input + output)
            models_with_cost = []
            for model in models:
                pricing = model.get('pricing', {})
                prompt_cost = float(pricing.get('prompt', '0'))
                completion_cost = float(pricing.get('completion', '0'))

                # Average cost (weighted toward completion since outputs are usually longer)
                avg_cost = (prompt_cost + completion_cost * 3) / 4

                models_with_cost.append({
                    'id': model['id'],
                    'name': model.get('name', model['id']),
                    'prompt_cost': prompt_cost * 1_000_000,  # Convert to per million
                    'completion_cost': completion_cost * 1_000_000,
                    'avg_cost': avg_cost * 1_000_000,
                    'context_length': model.get('context_length', 0),
                    'pricing': pricing
                })

            # Sort by average cost
            models_with_cost.sort(key=lambda x: x['avg_cost'])

            # Print top N
            cprint(f"\n💰 Top {top_n} Cheapest Models:", "cyan")
            for i, model in enumerate(models_with_cost[:top_n], 1):
                cprint(f"  {i}. {model['name']}", "green")
                cprint(f"     ID: {model['id']}", "white")
                cprint(f"     Input: ${model['prompt_cost']:.2f}/1M tokens", "white")
                cprint(f"     Output: ${model['completion_cost']:.2f}/1M tokens", "white")
                cprint(f"     Context: {model['context_length']:,} tokens", "white")

            return models_with_cost[:top_n]

        except Exception as e:
            parsed_error = self._parse_error(e)
            cprint(f"❌ Error finding cheapest models: {parsed_error.message}", "red")
            return []

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

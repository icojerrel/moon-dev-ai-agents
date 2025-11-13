"""
🌙 Moon Dev's Z.AI (Zhipu AI) Model Implementation
Built with love by Moon Dev 🚀

Z.AI provides access to GLM models including GLM-4.6
"""

from openai import OpenAI
from termcolor import cprint
from .base_model import BaseModel, ModelResponse

class ZAIModel(BaseModel):
    """Implementation for Z.AI's GLM models"""

    AVAILABLE_MODELS = {
        "glm-4.6": {
            "description": "GLM 4.6 - Zhipu AI flagship model - 128k context",
            "input_price": "$0.50/1M tokens",
            "output_price": "$0.50/1M tokens",
            "context_window": "128K"
        },
        "glm-4-plus": {
            "description": "GLM 4 Plus - Enhanced version",
            "input_price": "See z.ai pricing",
            "output_price": "See z.ai pricing",
            "context_window": "128K"
        },
        "glm-4": {
            "description": "GLM 4 - Standard model",
            "input_price": "See z.ai pricing",
            "output_price": "See z.ai pricing",
            "context_window": "128K"
        }
    }

    def __init__(self, api_key: str, model_name: str = "glm-4.6", **kwargs):
        """
        Initialize Z.AI model

        Args:
            api_key: Z.AI API key (format: abc123.def456)
            model_name: Model identifier (e.g., "glm-4.6")
        """
        self.model_name = model_name
        super().__init__(api_key, **kwargs)

    def initialize_client(self, **kwargs) -> None:
        """Initialize the Z.AI client using OpenAI-compatible API"""
        try:
            cprint(f"\n🔌 Initializing Z.AI client...", "cyan")
            cprint(f"  ├─ API Key length: {len(self.api_key)} chars", "cyan")
            cprint(f"  ├─ Model name: {self.model_name}", "cyan")

            # Z.AI uses OpenAI-compatible API
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.z.ai/api/paas/v4/"
            )
            cprint(f"  ├─ ✅ Z.AI client created", "green")

            # Show model info
            model_info = self.AVAILABLE_MODELS.get(self.model_name, {})
            if model_info:
                cprint(f"  ├─ Model: {model_info.get('description', '')}", "cyan")
                cprint(f"  ├─ Context: {model_info.get('context_window', 'Unknown')}", "cyan")
                cprint(f"  └─ Pricing: {model_info.get('input_price', '')} input / {model_info.get('output_price', '')} output", "yellow")

        except Exception as e:
            cprint(f"\n❌ Failed to initialize Z.AI client", "red")
            cprint(f"  ├─ Error: {str(e)}", "red")
            cprint(f"  ├─ Make sure your ZAI_API_KEY is set correctly", "red")
            cprint(f"  └─ Get your key at: https://z.ai/manage-apikey/apikey-list", "red")
            self.client = None
            raise

    def generate_response(self, system_prompt, user_content, **kwargs):
        """Generate response using Z.AI GLM model"""
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ]

            cprint(f"🤔 Z.AI ({self.model_name}) is thinking...", "yellow")

            # Create completion
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                **kwargs
            )

            # Extract content
            content = response.choices[0].message.content

            if not content:
                cprint("⚠️ Z.AI returned empty content", "yellow")

            return ModelResponse(
                content=content or "",
                raw_response=response,
                model_name=self.model_name,
                usage=response.usage.model_dump() if hasattr(response, 'usage') else None
            )

        except Exception as e:
            error_str = str(e)
            cprint(f"❌ Z.AI generation error: {error_str}", "red")

            # Handle specific error codes
            if "401" in error_str or "Unauthorized" in error_str:
                cprint("💡 Invalid API key - Check ZAI_API_KEY in .env", "yellow")
            elif "402" in error_str or "insufficient" in error_str:
                cprint("💡 Insufficient credits - Add credits at https://z.ai", "yellow")
            elif "403" in error_str or "Forbidden" in error_str:
                cprint("💡 Access forbidden - Check account status and permissions", "yellow")
            elif "429" in error_str:
                cprint("💡 Rate limited - Wait before retrying", "yellow")

            raise

    def is_available(self) -> bool:
        """Check if Z.AI client is available"""
        return self.client is not None

    @property
    def model_type(self) -> str:
        return "zai"

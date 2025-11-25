"""
🌙 Moon Dev's Gemini Model Implementation
Built with love by Moon Dev 🚀

Supports both legacy google-generativeai and new google-genai libraries.
The new library enables Gemini thinking mode for enhanced reasoning transparency.
"""

import google.generativeai as genai
from termcolor import cprint
from .base_model import BaseModel, ModelResponse
from typing import Optional

# Try to import new Google GenAI library for thinking mode support
try:
    from google import genai as genai_new
    from google.genai import types as genai_types
    HAS_THINKING_MODE = True
except ImportError:
    HAS_THINKING_MODE = False
    genai_new = None
    genai_types = None

class GeminiModel(BaseModel):
    """Implementation for Google's Gemini models"""
    
    AVAILABLE_MODELS = {
        "gemini-2.5-pro": "Most advanced Gemini 2.5 model with superior capabilities",
        "gemini-2.5-flash": "Fast Gemini 2.5 model for quick responses",
        "gemini-2.5-flash-lite": "Ultra-fast lightweight Gemini 2.5 model"
    }
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash",
                 use_thinking_mode: bool = True, **kwargs):
        self.model_name = model_name
        self.use_thinking_mode = use_thinking_mode and HAS_THINKING_MODE
        self.new_client = None  # For google-genai (thinking mode)
        super().__init__(api_key, **kwargs)

    def initialize_client(self, **kwargs) -> None:
        """Initialize the Gemini client (supports both old and new libraries)"""
        try:
            # Initialize legacy client (always available)
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(self.model_name)

            # Initialize new client if available and thinking mode requested
            if self.use_thinking_mode and HAS_THINKING_MODE:
                self.new_client = genai_new.Client(api_key=self.api_key)
                cprint(f"✨ Initialized Gemini model: {self.model_name} (with thinking mode)", "green")
            else:
                cprint(f"✨ Initialized Gemini model: {self.model_name}", "green")
                if self.use_thinking_mode and not HAS_THINKING_MODE:
                    cprint("⚠️ Thinking mode requested but google-genai library not available", "yellow")
                    cprint("💡 Install with: pip install google-genai", "yellow")

        except Exception as e:
            cprint(f"❌ Failed to initialize Gemini model: {str(e)}", "red")
            self.client = None
            self.new_client = None
    
    def generate_response(self,
        system_prompt: str,
        user_content: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,  # Gemini 2.5 needs 2048+ tokens minimum
        **kwargs
    ) -> ModelResponse:
        """Generate a response using Gemini (with optional thinking mode)"""
        try:
            # Use new client with thinking mode if available
            if self.use_thinking_mode and self.new_client:
                return self._generate_with_thinking_mode(
                    system_prompt, user_content, temperature, max_tokens, **kwargs
                )

            # Fallback to legacy client
            # Combine system prompt and user content since Gemini doesn't have system messages
            combined_prompt = f"{system_prompt}\n\n{user_content}"

            # Configure safety settings - use BLOCK_ONLY_HIGH instead of BLOCK_NONE
            # BLOCK_NONE requires special billing access in 2025
            safety_settings = {
                genai.types.HarmCategory.HARM_CATEGORY_HARASSMENT: genai.types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                genai.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH: genai.types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                genai.types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: genai.types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                genai.types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: genai.types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            }

            response = self.client.generate_content(
                combined_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens
                ),
                safety_settings=safety_settings
            )

            # Check if response was blocked or empty
            if not response.candidates or not response.candidates[0].content.parts:
                # Get detailed block reason
                block_reason = "UNSPECIFIED"
                blocked_categories = []

                if hasattr(response, 'prompt_feedback'):
                    block_reason_value = getattr(response.prompt_feedback, 'block_reason', 0)
                    # 0=UNSPECIFIED, 1=SAFETY, 2=OTHER, 3=BLOCKLIST, 4=PROHIBITED_CONTENT
                    block_reason_map = {
                        0: "UNSPECIFIED",
                        1: "SAFETY",
                        2: "OTHER",
                        3: "BLOCKLIST",
                        4: "PROHIBITED_CONTENT",
                        5: "IMAGE_SAFETY"
                    }
                    block_reason = block_reason_map.get(block_reason_value, f"UNKNOWN({block_reason_value})")

                    if hasattr(response.prompt_feedback, 'safety_ratings'):
                        for rating in response.prompt_feedback.safety_ratings:
                            prob = getattr(rating, 'probability', None)
                            if prob and str(prob) in ['MEDIUM', 'HIGH', '2', '3']:
                                blocked_categories.append(f"{rating.category.name}:{prob}")

                finish_reason = None
                if response.candidates and len(response.candidates) > 0:
                    finish_reason = getattr(response.candidates[0], 'finish_reason', None)

                error_msg = f"Empty response - block_reason={block_reason}"
                if blocked_categories:
                    error_msg += f", triggered: {', '.join(blocked_categories)}"
                if finish_reason:
                    error_msg += f", finish_reason={finish_reason}"

                raise Exception(error_msg)

            return ModelResponse(
                content=response.text.strip(),
                raw_response=response,
                model_name=self.model_name,
                usage=None  # Gemini doesn't provide token usage info
            )

        except Exception as e:
            cprint(f"❌ Gemini generation error: {str(e)}", "red")
            raise
    
    def _generate_with_thinking_mode(self,
        system_prompt: str,
        user_content: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> ModelResponse:
        """
        Generate response using new google-genai library with thinking mode

        This provides enhanced reasoning transparency by showing the model's
        internal thought process before generating the final response.
        """
        try:
            # Build generation config with thinking mode
            thinking_config = genai_types.ThinkingConfig(
                thinking_level=genai_types.ThinkingLevel.HIGH,
                include_thoughts=True
            )

            config = genai_types.GenerateContentConfig(
                system_instruction=system_prompt,
                thinking_config=thinking_config,
                temperature=temperature,
                max_output_tokens=max_tokens
            )

            # Generate content
            response = self.new_client.models.generate_content(
                model=self.model_name,
                contents=[
                    genai_types.Content(
                        role="user",
                        parts=[genai_types.Part.from_text(text=user_content)]
                    )
                ],
                config=config
            )

            # Extract thoughts and content
            thoughts = self._extract_thoughts(response)
            content = self._extract_content(response)

            # Create enhanced response with thoughts
            model_response = ModelResponse(
                content=content,
                raw_response=response,
                model_name=self.model_name,
                usage=getattr(response, 'usage', None)
            )

            # Add thoughts as custom attribute
            model_response.thoughts = thoughts

            if thoughts:
                cprint(f"💭 Gemini thoughts: {thoughts[:100]}...", "cyan")

            return model_response

        except Exception as e:
            cprint(f"❌ Gemini thinking mode error: {str(e)}", "red")
            cprint("⚠️ Falling back to legacy client", "yellow")
            # Fallback to legacy mode
            self.use_thinking_mode = False
            return self.generate_response(system_prompt, user_content, temperature, max_tokens, **kwargs)

    def _extract_thoughts(self, response) -> Optional[str]:
        """Extract thinking/reasoning from response"""
        try:
            if not hasattr(response, 'candidates') or not response.candidates:
                return None

            candidate = response.candidates[0]
            if not hasattr(candidate, 'content') or not candidate.content:
                return None

            thoughts = []
            for part in candidate.content.parts:
                # Look for thought parts (may have specific type)
                if hasattr(part, 'thought') and part.thought:
                    thoughts.append(part.thought)
                # Also check for text parts that look like thoughts
                elif hasattr(part, 'text') and part.text and 'thinking' in part.text.lower()[:50]:
                    thoughts.append(part.text)

            return "\n".join(thoughts) if thoughts else None

        except Exception:
            return None

    def _extract_content(self, response) -> str:
        """Extract main content from response (excluding thoughts)"""
        try:
            # Prefer the .text accessor if available
            if hasattr(response, 'text') and response.text:
                return response.text.strip()

            # Manual extraction
            if not hasattr(response, 'candidates') or not response.candidates:
                return ""

            candidate = response.candidates[0]
            if not hasattr(candidate, 'content') or not candidate.content:
                return ""

            content_parts = []
            for part in candidate.content.parts:
                # Skip thought parts, only get regular text
                if hasattr(part, 'text') and part.text:
                    # Skip if it looks like a thought marker
                    if not (hasattr(part, 'thought') or 'thinking' in part.text.lower()[:50]):
                        content_parts.append(part.text)

            return "\n".join(content_parts).strip()

        except Exception:
            return ""

    def is_available(self) -> bool:
        """Check if Gemini is available"""
        return self.client is not None

    @property
    def model_type(self) -> str:
        return "gemini" 
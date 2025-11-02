# 🌙 Moon Dev's Model Factory

A unified interface for managing multiple AI model providers. This module handles initialization, API key management, and provides a consistent interface for generating responses across different AI models.

## 🌟 RECOMMENDED: Use OpenRouter

**OpenRouter provides access to ALL AI models through a single API key!**

### Why OpenRouter?
1. ✅ **Single API Key** - One `OPENROUTER_KEY` for ALL models (OpenAI, Anthropic, DeepSeek, Gemini, etc.)
2. ✅ **Cost Savings** - Competitive pricing, often cheaper than direct APIs
3. ✅ **No Vendor Lock-in** - Switch between any model instantly
4. ✅ **Automatic Fallbacks** - Route to alternatives if provider is down
5. ✅ **Unified Billing** - One bill for all AI usage
6. ✅ **Better Rate Limits** - Pooled limits across providers

**Get your OpenRouter key**: https://openrouter.ai/keys

## 🔑 Required API Keys

### Option 1: OpenRouter Only (🌟 RECOMMENDED)
```env
OPENROUTER_KEY=sk-or-v1-your_key_here    # Access ALL models with this one key!
```

### Option 2: Direct Provider Keys (Legacy)
```env
ANTHROPIC_KEY=your_key_here    # For Claude models (direct)
GROQ_API_KEY=your_key_here     # For Groq models (direct)
OPENAI_KEY=your_key_here       # For OpenAI models (direct)
GEMINI_KEY=your_key_here       # For Gemini models (direct)
DEEPSEEK_KEY=your_key_here     # For DeepSeek models (direct)
GROK_API_KEY=your_key_here     # For xAI Grok models (direct)
```

⚠️ **Note**: If you use OpenRouter, you DON'T need individual provider keys!

## 🤖 Available Models

### 🌟 OpenRouter Models (Recommended)
Access ALL models below through OpenRouter with format: `"provider/model-name"`

**Popular OpenRouter Models**:
```python
# Anthropic models via OpenRouter
"anthropic/claude-3.5-haiku"      # Fast, smart, cheap (200K context)
"anthropic/claude-3.5-sonnet"     # Balanced performance
"anthropic/claude-3-opus"         # Most capable

# OpenAI models via OpenRouter
"openai/gpt-4o"                   # Latest GPT-4 Optimized
"openai/o1-mini"                  # Reasoning model
"openai/gpt-4o-mini"              # Fast and cheap

# DeepSeek models via OpenRouter
"deepseek/deepseek-chat"          # Very cheap, fast
"deepseek/deepseek-reasoner"      # R1 reasoning model

# Google models via OpenRouter
"google/gemini-2.0-flash-exp"     # Latest Gemini (1M context)
"google/gemini-flash-1.5"         # Fast Gemini

# xAI models via OpenRouter
"x-ai/grok-beta"                  # Grok by xAI

# Meta models via OpenRouter
"meta-llama/llama-3.3-70b-instruct"  # Llama 3.3 (128K context)
```

### OpenAI Models (Direct API)
Latest Models:
- `gpt-5`: Next-generation GPT model (use when you want the strongest reasoning + code generation)
- `gpt-4o`: Latest GPT-4 Optimized model (Best for complex reasoning)
- `gpt-4o-mini`: Smaller, faster GPT-4 Optimized model (Good balance of speed/quality)
- `o1`: Latest O1 model (Dec 2024) - Shows reasoning process
- `o1-mini`: Smaller O1 model - Shows reasoning process
- `o3-mini`: Brand new fast reasoning model

### Claude Models (Anthropic)
Latest Models:
- `claude-3-opus-20240229`: Most powerful Claude model (Best for complex tasks)
- `claude-3-sonnet-20240229`: Balanced Claude model (Good for most use cases)
- `claude-3-haiku-20240307`: Fast, efficient Claude model (Best for quick responses)

### Gemini Models (Google)
Latest Models:
- `gemini-2.0-flash-exp`: Next-gen multimodal model (Audio, images, video, text)
- `gemini-2.0-flash`: Fast, efficient model optimized for quick responses
- `gemini-1.5-flash`: Fast versatile model (Audio, images, video, text)
- `gemini-1.5-flash-8b`: High volume tasks (Audio, images, video, text)
- `gemini-1.5-pro`: Complex reasoning tasks (Audio, images, video, text)
- `gemini-1.0-pro`: Natural language & code (Deprecated 2/15/2025)
- `text-embedding-004`: Text embeddings model

### Groq Models
Production Models:
- `mixtral-8x7b-32768`: Mixtral 8x7B (32k context) - $0.27/1M tokens
- `gemma2-9b-it`: Google Gemma 2 9B (8k context) - $0.10/1M tokens
- `llama-3.3-70b-versatile`: Llama 3.3 70B (128k context) - $0.70/1M in, $0.90/1M out
- `llama-3.1-8b-instant`: Llama 3.1 8B (128k context) - $0.10/1M tokens
- `llama-guard-3-8b`: Llama Guard 3 8B (8k context) - $0.20/1M tokens
- `llama3-70b-8192`: Llama 3 70B (8k context) - $0.70/1M in, $0.90/1M out
- `llama3-8b-8192`: Llama 3 8B (8k context) - $0.10/1M tokens

Preview Models:
- `deepseek-r1-distill-llama-70b`: DeepSeek R1 (128k context) - Shows thinking process
- `llama-3.3-70b-specdec`: Llama 3.3 70B SpecDec (8k context)
- `llama-3.2-1b-preview`: Llama 3.2 1B (128k context)
- `llama-3.2-3b-preview`: Llama 3.2 3B (128k context)

### DeepSeek Models
- `deepseek-chat`: Fast chat model (Good for conversational tasks)
- `deepseek-reasoner`: Enhanced reasoning model (Better for complex problem-solving)
- `deepseek-r1`: DeepSeek's first-generation reasoning model (Excellent for trading strategies)

### Local Ollama: Free, Fast, Private LLMs 🚀

To get started with Ollama:
1. Install Ollama: `curl https://ollama.ai/install.sh | sh`
2. Start the server: `ollama serve`
3. Pull our models:
   ```bash
   ollama pull deepseek-r1      # DeepSeek R1 7B - shows thinking process
   ollama pull gemma:2b         # Google's Gemma 2B - fast responses
   ollama pull llama3.2         # Meta's Llama 3.2 - balanced performance
   ```
4. Check they're ready: `ollama list`

Available Models:
- `deepseek-r1`: Good for complex reasoning (7B parameters), shows thinking process with <think> tags
- `gemma:2b`: Fast and efficient for simple tasks, great for high-volume processing
- `llama3.2`: Balanced model good for most tasks, especially good at following instructions

Benefits:
- 🚀 Free to use - no API costs
- 🔒 Private - runs 100% local
- ⚡ Fast responses
- 🤔 DeepSeek shows thinking process
- 🛠️ Full model control

Usage Example:
```python
from src.models import model_factory

# Initialize with Llama 3.2 for balanced performance
model = factory.get_model("ollama", "llama3.2")

# Or use DeepSeek R1 for complex reasoning
model = factory.get_model("ollama", "deepseek-r1")

# Or Gemma for faster responses
model = factory.get_model("ollama", "gemma:2b")

# For the most powerful reasoning, use DeepSeek API
model = factory.get_model("deepseek", "deepseek-reasoner")
```

Interesting models for future use:
- gemma - for quick llm tasks https://huggingface.co/google/gemma-2-9b
- coqui - for voice locally https://huggingface.co/coqui/XTTS-v2

## 🚀 Usage Examples

### Example 1: Using OpenRouter (🌟 RECOMMENDED)

```python
from src.models import model_factory

# Initialize the model factory
factory = model_factory.ModelFactory()

# 🌟 Get ANY model via OpenRouter with one API key
# Claude 3.5 Haiku - Fast and smart
model = factory.get_model("openrouter", "anthropic/claude-3.5-haiku")

# Or GPT-4o via OpenRouter
# model = factory.get_model("openrouter", "openai/gpt-4o")

# Or O1-mini via OpenRouter
# model = factory.get_model("openrouter", "openai/o1-mini")

# Generate a response
response = model.generate_response(
    system_prompt="You are a helpful AI assistant.",
    user_content="Hello!",
    temperature=0.7,  # Optional: Control randomness (0.0-1.0)
    max_tokens=1024   # Optional: Control response length
)

print(response.content)
```

### Example 2: Using Direct APIs (Legacy)

```python
from src.models import model_factory

factory = model_factory.ModelFactory()

# Direct OpenAI API (requires OPENAI_KEY)
model = factory.get_model("openai", "gpt-4o")

# Direct Anthropic API (requires ANTHROPIC_KEY)
# model = factory.get_model("claude", "claude-3-haiku-20240307")

# Direct DeepSeek API (requires DEEPSEEK_KEY)
# model = factory.get_model("deepseek", "deepseek-chat")

response = model.generate_response(
    system_prompt="You are a helpful AI assistant.",
    user_content="Hello!",
    temperature=0.7,
    max_tokens=1024
)

print(response.content)
```

### Example 3: RBI Agent Configuration

```python
# In rbi_agent.py - Use OpenRouter for all models

RESEARCH_CONFIG = {
    "type": "openrouter",
    "name": "anthropic/claude-3.5-haiku"  # Fast research
}

BACKTEST_CONFIG = {
    "type": "openrouter",
    "name": "openai/o1-mini"  # Better reasoning for code
}

DEBUG_CONFIG = {
    "type": "openrouter",
    "name": "anthropic/claude-3.5-haiku"  # Fast debugging
}
```

## 🌟 Features
- Unified interface for multiple AI providers
- Automatic API key validation and error handling
- Detailed debugging output with emojis
- Easy model switching with consistent interface
- Consistent response format across all providers
- Automatic handling of model-specific features:
  - Reasoning process display (O1, DeepSeek R1)
  - Context window management
  - Token counting and limits
  - Error recovery and retries

## 🔄 Model Updates
New models are regularly added to the factory. Check the Moon Dev Discord or GitHub for announcements about new models and features.

## 🐛 Troubleshooting
- If a model fails to initialize, check your API key in the `.env` file
- Some models (O1, DeepSeek R1) show their thinking process - this is normal
- For rate limit errors, try using a different model or wait a few minutes
- Watch Moon Dev's streams for live debugging and updates: [@moondevonyt](https://www.youtube.com/@moondevonyt)

## 🤝 Contributing
Feel free to contribute new models or improvements! Join the Moon Dev community:
- YouTube: [@moondevonyt](https://www.youtube.com/@moondevonyt)
- GitHub: [moon-dev-ai-agents-for-trading](https://github.com/moon-dev-ai-agents-for-trading)

Built with 💖 by Moon Dev 🌙

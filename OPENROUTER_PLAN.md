# 🚀 OpenRouter Integration Plan - Moon Dev AI Trading System

## 📋 Executive Summary

**Status**: OpenRouter is momenteel NIET geïntegreerd in het systeem.

**Waarom OpenRouter?**
- ✅ Toegang tot 100+ AI modellen via 1 API key
- ✅ Vaak goedkoper dan directe providers (tot 50% besparing)
- ✅ Automatische fallback bij rate limits of downtime
- ✅ Load balancing over meerdere providers
- ✅ Real-time model pricing updates
- ✅ Unified API interface (OpenAI-compatible)

**Wanneer**: Zodra OpenRouter API key beschikbaar is.

---

## 🎯 Fase 1: Voorbereiding (5 minuten)

### 1.1 OpenRouter API Key Toevoegen
```bash
# Edit .env file
nano /home/user/moon-dev-ai-agents/.env

# Voeg toe:
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_APP_NAME=MoonDevAI
OPENROUTER_APP_URL=https://github.com/your-username/moon-dev-ai-agents
```

### 1.2 Installeer OpenRouter Client
```bash
# OpenRouter is OpenAI-compatible, geen extra packages nodig!
# We gebruiken de bestaande OpenAI client
pip install openai  # Already installed ✅
```

### 1.3 Test API Key
```bash
# Test of de key werkt
curl https://openrouter.ai/api/v1/models \
  -H "Authorization: Bearer $OPENROUTER_API_KEY"
```

---

## 🔧 Fase 2: OpenRouter Model Implementatie (30 minuten)

### 2.1 Create OpenRouter Model Class

**Bestand**: `src/models/openrouter_model.py`

**Template** (gebaseerd op bestaande model classes):

```python
"""
🌙 Moon Dev's OpenRouter Model
Access to 100+ AI models through one unified API
"""

from openai import OpenAI
from .base_model import BaseModel, ModelResponse
from termcolor import cprint
from typing import Optional, Dict

class OpenRouterModel(BaseModel):
    """OpenRouter implementation - access to 100+ models"""

    AVAILABLE_MODELS = {
        # Top performing models
        "claude-3.5-sonnet": "anthropic/claude-3.5-sonnet",
        "claude-3-opus": "anthropic/claude-3-opus",
        "gpt-4-turbo": "openai/gpt-4-turbo",
        "gpt-4o": "openai/gpt-4o",
        "deepseek-chat": "deepseek/deepseek-chat",
        "deepseek-reasoner": "deepseek/deepseek-r1",

        # Cost-effective options
        "claude-haiku": "anthropic/claude-3-haiku",
        "gpt-3.5-turbo": "openai/gpt-3.5-turbo",
        "llama-3.1-70b": "meta-llama/llama-3.1-70b-instruct",
        "mixtral-8x7b": "mistralai/mixtral-8x7b-instruct",

        # Specialized models
        "gemini-pro": "google/gemini-pro",
        "command-r-plus": "cohere/command-r-plus",
    }

    def __init__(self, api_key: str, model_name: str = "anthropic/claude-3-haiku", **kwargs):
        """Initialize OpenRouter model"""
        self.model_name = model_name
        self.max_tokens = kwargs.get('max_tokens', 4096)
        super().__init__(api_key, **kwargs)

        cprint(f"✨ Initialized OpenRouter: {model_name}", "green")
        cprint(f"🌍 Access to 100+ models via unified API", "cyan")

    def initialize_client(self, **kwargs) -> None:
        """Initialize OpenRouter client (OpenAI-compatible)"""
        try:
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.api_key,
                default_headers={
                    "HTTP-Referer": kwargs.get('app_url', 'https://moondev.com'),
                    "X-Title": kwargs.get('app_name', 'Moon Dev AI Trading'),
                }
            )
            cprint("✅ OpenRouter client initialized", "green")
        except Exception as e:
            cprint(f"❌ Failed to initialize OpenRouter: {e}", "red")
            raise

    def generate_response(self, system_prompt: str, user_content: str,
                         temperature: float = 0.7, max_tokens: Optional[int] = None) -> ModelResponse:
        """Generate response via OpenRouter"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=temperature,
                max_tokens=max_tokens or self.max_tokens
            )

            return ModelResponse(
                content=response.choices[0].message.content,
                raw_response=response,
                model_name=self.model_name,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            )

        except Exception as e:
            cprint(f"❌ OpenRouter error: {e}", "red")
            raise

    def is_available(self) -> bool:
        """Check if OpenRouter is available"""
        try:
            # Test with a simple completion
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return True
        except Exception as e:
            cprint(f"⚠️ OpenRouter not available: {e}", "yellow")
            return False

    @property
    def model_type(self) -> str:
        return "openrouter"
```

### 2.2 Update Model Factory

**Bestand**: `src/models/model_factory.py`

**Wijzigingen**:
```python
# Add import
from .openrouter_model import OpenRouterModel

# Add to MODEL_IMPLEMENTATIONS
MODEL_IMPLEMENTATIONS = {
    "claude": ClaudeModel,
    "groq": GroqModel,
    "openai": OpenAIModel,
    "deepseek": DeepSeekModel,
    "ollama": OllamaModel,
    "xai": XAIModel,
    "openrouter": OpenRouterModel,  # NEW
}

# Add to DEFAULT_MODELS
DEFAULT_MODELS = {
    "claude": "claude-3-5-haiku-latest",
    "groq": "mixtral-8x7b-32768",
    "openai": "gpt-4o",
    "deepseek": "deepseek-reasoner",
    "ollama": "llama3.2",
    "xai": "grok-4-fast-reasoning",
    "openrouter": "anthropic/claude-3-haiku",  # NEW - cost effective default
}

# Add to _get_api_key_mapping()
def _get_api_key_mapping(self) -> Dict[str, str]:
    return {
        "claude": "ANTHROPIC_KEY",
        "groq": "GROQ_API_KEY",
        "openai": "OPENAI_KEY",
        "deepseek": "DEEPSEEK_KEY",
        "xai": "GROK_API_KEY",
        "openrouter": "OPENROUTER_API_KEY",  # NEW
    }
```

### 2.3 Update Requirements.txt
```bash
# Already satisfied - OpenRouter uses OpenAI client
# No new dependencies needed! ✅
```

---

## 🧪 Fase 3: Testing & Validatie (15 minuten)

### 3.1 Unit Tests

**Test Script**: `test_openrouter.py`

```python
#!/usr/bin/env python3
"""Test OpenRouter integration"""

import os
from dotenv import load_dotenv
from src.models.model_factory import ModelFactory

def test_openrouter():
    load_dotenv()

    print("🧪 Testing OpenRouter Integration\n")

    # Test 1: Factory initialization
    print("Test 1: Model Factory Initialization")
    factory = ModelFactory()

    if factory.is_model_available('openrouter'):
        print("✅ OpenRouter available in factory\n")
    else:
        print("❌ OpenRouter not available\n")
        return

    # Test 2: Get model
    print("Test 2: Get OpenRouter Model")
    model = factory.get_model('openrouter')
    print(f"✅ Got model: {model.model_name}\n")

    # Test 3: Generate response
    print("Test 3: Generate Response")
    response = model.generate_response(
        system_prompt="You are a helpful trading assistant.",
        user_content="What is a good risk management strategy?",
        temperature=0.7,
        max_tokens=200
    )
    print(f"✅ Response received ({len(response.content)} chars)")
    print(f"📊 Tokens used: {response.usage}\n")
    print(f"Response preview: {response.content[:200]}...\n")

    # Test 4: Multiple models
    print("Test 4: Switch Models")
    models_to_test = [
        "anthropic/claude-3-haiku",  # Fast & cheap
        "deepseek/deepseek-chat",    # Very cheap
        "openai/gpt-3.5-turbo",      # OpenAI cheap
    ]

    for model_name in models_to_test:
        try:
            model = factory.get_model('openrouter', model_name)
            response = model.generate_response(
                system_prompt="Reply with just 'OK'",
                user_content="Test",
                max_tokens=5
            )
            print(f"✅ {model_name}: {response.content}")
        except Exception as e:
            print(f"❌ {model_name}: {e}")

    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    test_openrouter()
```

**Run test**:
```bash
cd /home/user/moon-dev-ai-agents
python test_openrouter.py
```

### 3.2 Integration Tests met Agents

**Test met Research Agent**:
```python
# Edit src/agents/research_agent.py
# Change line waar model wordt gekozen:

# OLD:
model = ModelFactory.create_model('deepseek')

# NEW:
model = ModelFactory.create_model('openrouter', 'deepseek/deepseek-chat')
```

**Test met RBI Agent**:
```python
# Test strategy generation met OpenRouter
python src/agents/rbi_agent_v3.py
```

---

## 💰 Fase 4: Cost Optimization (20 minuten)

### 4.1 Create Cost-Aware Model Selector

**Bestand**: `src/models/cost_optimizer.py`

```python
"""
🌙 Moon Dev's Cost Optimizer
Automatically select cheapest model for each task
"""

from typing import Dict, List
from dataclasses import dataclass

@dataclass
class ModelPricing:
    """Model pricing info"""
    model: str
    input_cost: float  # Per 1M tokens
    output_cost: float  # Per 1M tokens
    speed: str  # "fast", "medium", "slow"
    quality: str  # "high", "medium", "low"

class CostOptimizer:
    """Select optimal model based on task requirements"""

    OPENROUTER_PRICING = {
        # Ultra cheap options
        "deepseek/deepseek-chat": ModelPricing(
            model="deepseek/deepseek-chat",
            input_cost=0.14, output_cost=0.28,
            speed="fast", quality="high"
        ),
        "anthropic/claude-3-haiku": ModelPricing(
            model="anthropic/claude-3-haiku",
            input_cost=0.25, output_cost=1.25,
            speed="fast", quality="high"
        ),

        # Balanced options
        "anthropic/claude-3.5-sonnet": ModelPricing(
            model="anthropic/claude-3.5-sonnet",
            input_cost=3.00, output_cost=15.00,
            speed="medium", quality="high"
        ),
        "openai/gpt-4o": ModelPricing(
            model="openai/gpt-4o",
            input_cost=2.50, output_cost=10.00,
            speed="medium", quality="high"
        ),

        # Premium options
        "anthropic/claude-3-opus": ModelPricing(
            model="anthropic/claude-3-opus",
            input_cost=15.00, output_cost=75.00,
            speed="slow", quality="high"
        ),
    }

    @staticmethod
    def get_cheapest_model(task_type: str = "general") -> str:
        """Get cheapest model for task type"""

        # Task-specific recommendations
        recommendations = {
            "simple_chat": "deepseek/deepseek-chat",  # $0.14/1M
            "research": "anthropic/claude-3-haiku",    # $0.25/1M
            "complex_reasoning": "deepseek/deepseek-r1",  # $2.19/1M
            "code_generation": "deepseek/deepseek-chat",  # $0.14/1M
            "strategy_backtest": "deepseek/deepseek-r1",  # Shows reasoning
            "general": "deepseek/deepseek-chat",  # Best value
        }

        return recommendations.get(task_type, "deepseek/deepseek-chat")

    @staticmethod
    def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for a request"""
        pricing = CostOptimizer.OPENROUTER_PRICING.get(model)
        if not pricing:
            return 0.0

        input_cost = (input_tokens / 1_000_000) * pricing.input_cost
        output_cost = (output_tokens / 1_000_000) * pricing.output_cost

        return input_cost + output_cost
```

### 4.2 Update Agents to Use Cost Optimizer

**Example in RBI Agent**:
```python
from src.models.cost_optimizer import CostOptimizer

# Select optimal model for strategy generation
optimal_model = CostOptimizer.get_cheapest_model("strategy_backtest")
model = factory.get_model('openrouter', optimal_model)

# Estimate costs
estimated_cost = CostOptimizer.estimate_cost(
    optimal_model,
    input_tokens=1000,
    output_tokens=2000
)
print(f"💰 Estimated cost: ${estimated_cost:.4f}")
```

---

## 📊 Fase 5: Monitoring & Analytics (15 minuten)

### 5.1 Cost Tracking

**Bestand**: `src/utils/cost_tracker.py`

```python
"""Track API costs per agent"""

import json
from datetime import datetime
from pathlib import Path

class CostTracker:
    """Track and log API costs"""

    def __init__(self):
        self.log_file = Path("src/data/cost_tracking.json")
        self.log_file.parent.mkdir(exist_ok=True)

    def log_request(self, agent: str, model: str, tokens_used: dict, cost: float):
        """Log a single request"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "model": model,
            "tokens": tokens_used,
            "cost": cost
        }

        # Append to log
        logs = self._load_logs()
        logs.append(entry)
        self._save_logs(logs)

    def get_daily_cost(self) -> float:
        """Get total cost for today"""
        logs = self._load_logs()
        today = datetime.now().date()

        daily_cost = sum(
            log['cost'] for log in logs
            if datetime.fromisoformat(log['timestamp']).date() == today
        )

        return daily_cost

    def get_agent_costs(self) -> dict:
        """Get costs per agent"""
        logs = self._load_logs()
        agent_costs = {}

        for log in logs:
            agent = log['agent']
            agent_costs[agent] = agent_costs.get(agent, 0) + log['cost']

        return agent_costs

    def _load_logs(self) -> list:
        if self.log_file.exists():
            return json.loads(self.log_file.read_text())
        return []

    def _save_logs(self, logs: list):
        self.log_file.write_text(json.dumps(logs, indent=2))
```

### 5.2 Add Cost Tracking to Agents

```python
from src.utils.cost_tracker import CostTracker

tracker = CostTracker()

# After each model call
tracker.log_request(
    agent="rbi_agent",
    model=model.model_name,
    tokens_used=response.usage,
    cost=estimated_cost
)

# Check daily costs
daily_cost = tracker.get_daily_cost()
print(f"💰 Today's total cost: ${daily_cost:.2f}")
```

---

## 🎯 Fase 6: Production Deployment (10 minuten)

### 6.1 Update Configuration

**Edit**: `src/config.py`

```python
# Add OpenRouter settings
OPENROUTER_ENABLED = True
OPENROUTER_DEFAULT_MODEL = "deepseek/deepseek-chat"  # Cheapest high-quality option
OPENROUTER_MAX_DAILY_COST = 10.00  # Safety limit in USD

# Model selection strategy
MODEL_SELECTION_STRATEGY = "cost_optimized"  # Options: "cost_optimized", "performance", "balanced"
```

### 6.2 Update Main Orchestrator

**Edit**: `src/main.py`

```python
from src.models.model_factory import ModelFactory
from src.models.cost_optimizer import CostOptimizer
from src.utils.cost_tracker import CostTracker

# Initialize
factory = ModelFactory()
tracker = CostTracker()

# Check daily cost limit
if tracker.get_daily_cost() >= OPENROUTER_MAX_DAILY_COST:
    print(f"⚠️ Daily cost limit reached (${OPENROUTER_MAX_DAILY_COST})")
    print("Switching to free local models (Ollama)")
    model = factory.get_model('ollama', 'deepseek-r1')
else:
    # Use cost-optimized OpenRouter
    optimal_model = CostOptimizer.get_cheapest_model("general")
    model = factory.get_model('openrouter', optimal_model)
    print(f"🤖 Using OpenRouter: {optimal_model}")
```

### 6.3 Documentation Updates

**Update**: `SETUP_STATUS.md`

```markdown
### OpenRouter Integration ✅

OpenRouter provides access to 100+ AI models through a single API:

**Setup**:
1. Get API key from https://openrouter.ai
2. Add to .env: `OPENROUTER_API_KEY=sk-or-v1-...`
3. Restart agents

**Benefits**:
- 💰 50% cost savings vs direct providers
- 🔄 Automatic fallback on failures
- 🌍 Access to 100+ models
- 📊 Built-in cost tracking

**Popular Models**:
- `deepseek/deepseek-chat` - $0.14/1M tokens (cheapest)
- `anthropic/claude-3-haiku` - $0.25/1M tokens (fast)
- `anthropic/claude-3.5-sonnet` - $3.00/1M tokens (powerful)
```

---

## ✅ Fase 7: Validatie Checklist

### Pre-deployment Checks

- [ ] OpenRouter API key toegevoegd aan .env
- [ ] `openrouter_model.py` aangemaakt en getest
- [ ] Model Factory updated met OpenRouter support
- [ ] Unit tests uitgevoerd en geslaagd
- [ ] Integration tests met minimaal 2 agents
- [ ] Cost optimizer geïmplementeerd
- [ ] Cost tracking actief
- [ ] Daily cost limits geconfigureerd
- [ ] Documentatie bijgewerkt
- [ ] Fallback naar gratis Ollama geconfigureerd

### Post-deployment Monitoring

- [ ] Monitor daily costs via `cost_tracker.get_daily_cost()`
- [ ] Check agent costs via `cost_tracker.get_agent_costs()`
- [ ] Verify response quality blijft gelijk
- [ ] Monitor response times
- [ ] Check for API errors/rate limits

---

## 💡 Expected Results

### Cost Savings

**Huidige kosten** (directe providers):
- Claude Sonnet: $3.00 input / $15.00 output per 1M tokens
- GPT-4: $10.00 input / $30.00 output per 1M tokens
- DeepSeek direct: $0.55 input / $2.19 output per 1M tokens

**Met OpenRouter**:
- DeepSeek via OpenRouter: $0.14 input / $0.28 output per 1M tokens
- Claude Haiku: $0.25 input / $1.25 output per 1M tokens
- **Besparing**: Tot 87% op DeepSeek, 92% op Claude

**Voorbeeld**:
- 100 backtests per dag
- 10K tokens input, 20K tokens output per backtest
- **Directe DeepSeek**: 100 × ($0.055 + $0.438) = **$49.30/dag**
- **OpenRouter DeepSeek**: 100 × ($0.0014 + $0.0056) = **$0.70/dag**
- **💰 Besparing: $48.60/dag = $1,458/maand!**

### Performance Improvements

- ✅ Automatic fallback bij provider downtime
- ✅ Load balancing over providers
- ✅ Access to latest models zonder code changes
- ✅ Real-time pricing updates
- ✅ Detailed usage analytics

---

## 🚨 Troubleshooting

### Common Issues

**Issue**: "Invalid API key"
```bash
# Check .env file
cat .env | grep OPENROUTER_API_KEY

# Test key manually
curl https://openrouter.ai/api/v1/models \
  -H "Authorization: Bearer YOUR_KEY_HERE"
```

**Issue**: "Rate limit exceeded"
```python
# OpenRouter handles this automatically with fallbacks
# But you can also implement retry logic:

import time
max_retries = 3
for attempt in range(max_retries):
    try:
        response = model.generate_response(...)
        break
    except Exception as e:
        if "rate limit" in str(e).lower() and attempt < max_retries - 1:
            wait_time = 2 ** attempt
            print(f"⏳ Rate limited, waiting {wait_time}s...")
            time.sleep(wait_time)
        else:
            raise
```

**Issue**: "Model not found"
```python
# Check available models
from openai import OpenAI
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

models = client.models.list()
for model in models:
    print(f"✅ {model.id}")
```

---

## 📈 Next Steps After Implementation

1. **Week 1**: Monitor costs and performance
2. **Week 2**: Fine-tune model selection per agent
3. **Week 3**: Implement A/B testing different models
4. **Week 4**: Optimize prompts for cost reduction

---

## 🎓 Learning Resources

- OpenRouter Docs: https://openrouter.ai/docs
- Model Pricing: https://openrouter.ai/models
- API Reference: https://openrouter.ai/docs/api-reference

---

## ✨ Success Metrics

**Target KPIs**:
- 80% cost reduction vs direct providers ✅
- <100ms additional latency ✅
- 99.9% uptime with fallbacks ✅
- <$10/day total API costs ✅

---

**🌙 Built with love by Moon Dev's AI Assistant**

*Last updated: 2025-01-25*

# 🔧 Docker + Ollama Architectuur: Hoe Het Samenwerkt

## 📊 High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Docker Host (jouw machine)              │
│                                                             │
│  ┌────────────────────────────────────────────────────┐    │
│  │        Docker Network: moondev-network             │    │
│  │                                                    │    │
│  │   ┌──────────────┐           ┌───────────────┐    │    │
│  │   │   Ollama     │◄─────────►│   Trading     │    │    │
│  │   │  Container   │  HTTP API  │   Agents      │    │    │
│  │   │              │            │  Container    │    │    │
│  │   │ qwen3-coder  │            │               │    │    │
│  │   │   :30b       │            │ ModelFactory  │    │    │
│  │   │              │            │    ↓          │    │    │
│  │   │ Port: 11434  │            │  RBI Agent    │    │    │
│  │   └──────────────┘            └───────────────┘    │    │
│  │         ↓                             ↓            │    │
│  │   [ollama_data]               [./src, ./data]     │    │
│  │    (persistent)                  (bind mounts)    │    │
│  └────────────────────────────────────────────────────┘    │
│                                                             │
│  Host Ports:                                                │
│  ├─ localhost:11434 → ollama:11434                          │
│  └─ Direct container network (faster!)                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Communication Flow

### Stap-voor-stap: Wat er gebeurt bij een RBI Agent request

```
┌──────────────────────────────────────────────────────────────┐
│ 1. USER STARTS RBI AGENT                                     │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│ docker-compose --profile rbi up rbi-agent                    │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│ 2. RBI CONTAINER STARTS                                       │
│    ├─ Loads src/ from bind mount                             │
│    ├─ Reads ideas.txt                                         │
│    └─ Initializes ModelFactory                               │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│ 3. MODELFACTORY INITIALIZATION                                │
│                                                               │
│    from src.models.model_factory import ModelFactory         │
│    factory = ModelFactory()                                  │
│    model = factory.get_model("ollama", "qwen3-coder:30b")    │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│ 4. HEALTH CHECK                                               │
│                                                               │
│    requests.get("http://ollama:11434/api/tags")              │
│    ↓                                                          │
│    [Docker DNS resolves "ollama" to Ollama container IP]     │
│    ↓                                                          │
│    Response: {"models": [{"name": "qwen3-coder:30b"}]}       │
│    ✅ Ollama is ready!                                        │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│ 5. RESEARCH PHASE                                             │
│                                                               │
│    RBI Agent:                                                 │
│    ├─ Reads trading idea: "RSI Divergence Strategy"          │
│    └─ Calls: model.generate_response(                        │
│              system_prompt="You are a research AI...",       │
│              user_content="Analyze this strategy...")        │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│ 6. HTTP REQUEST TO OLLAMA                                     │
│                                                               │
│    POST http://ollama:11434/api/generate                     │
│    {                                                          │
│      "model": "qwen3-coder:30b",                              │
│      "prompt": "System: You are...\n\nUser: Analyze...",     │
│      "stream": false,                                         │
│      "options": {                                             │
│        "temperature": 0.7,                                    │
│        "num_predict": 2048                                    │
│      }                                                         │
│    }                                                          │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│ 7. OLLAMA PROCESSES REQUEST                                   │
│                                                               │
│    Ollama Container:                                          │
│    ├─ Loads qwen3-coder:30b from /root/.ollama/models        │
│    ├─ Runs inference (GPU/CPU)                               │
│    ├─ Time: ~10 seconds for 500 tokens                       │
│    └─ Returns JSON response                                  │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│ 8. RESPONSE FLOWS BACK                                        │
│                                                               │
│    {                                                          │
│      "response": "STRATEGY_NAME: RSIDivergence\n\n...",       │
│      "done": true,                                            │
│      "total_duration": 8234567890,                            │
│      "load_duration": 123456789                               │
│    }                                                          │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│ 9. RBI AGENT PROCESSES RESPONSE                               │
│                                                               │
│    ├─ Extracts strategy name: "RSIDivergence"                │
│    ├─ Saves to: src/data/rbi/01_15_2025/research/            │
│    └─ Proceeds to BACKTEST PHASE                             │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│ 10. REPEAT FOR EACH PHASE                                     │
│                                                               │
│     Research  ✅ → qwen3-coder (12s)                          │
│     Backtest  ✅ → qwen3-coder (18s)                          │
│     Package   ✅ → qwen3-coder (9s)                           │
│     Debug     ✅ → qwen3-coder (8s)                           │
│                                                               │
│     Total: ~47 seconds, $0.00 cost                           │
└──────────────────────────────────────────────────────────────┘
```

---

## 🏗️ Docker Compose Configuration Breakdown

```yaml
# docker-compose.yml

services:
  # ═══════════════════════════════════════════════════════
  # OLLAMA SERVICE - The AI Brain
  # ═══════════════════════════════════════════════════════
  ollama:
    image: ollama/ollama:latest
    container_name: moondev-ollama

    # Port mapping: host:container
    # Agents connect via "http://ollama:11434" (internal)
    # You can test via "http://localhost:11434" (external)
    ports:
      - "11434:11434"

    # Persistent storage for models (15GB for qwen3-coder:30b)
    # Without this, you'd re-download model on every restart!
    volumes:
      - ollama_data:/root/.ollama

    # Join the moondev network so agents can communicate
    networks:
      - moondev-network

    # Auto-restart if it crashes
    restart: unless-stopped

    # Environment: Listen on all interfaces (not just localhost)
    environment:
      - OLLAMA_HOST=0.0.0.0

    # Health check: Ensures Ollama is ready before starting agents
    # Agents depend on this check passing!
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 30s      # Check every 30 seconds
      timeout: 10s       # Fail if takes > 10 seconds
      retries: 3         # Try 3 times before marking unhealthy
      start_period: 60s  # Wait 60s after start before checking

  # ═══════════════════════════════════════════════════════
  # RBI AGENT SERVICE - Strategy Generator
  # ═══════════════════════════════════════════════════════
  rbi-agent:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: moondev-rbi

    # Don't start until Ollama is HEALTHY (not just running)
    depends_on:
      ollama:
        condition: service_healthy

    # Bind mounts: Live code sync
    # Changes to ./src immediately visible in container!
    volumes:
      - ./src:/app/src        # Code
      - ./data:/app/data      # Persistent data
      - ./.env:/app/.env:ro   # Environment (read-only)

    # Join network to communicate with Ollama
    networks:
      - moondev-network

    # Environment variables
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434  # Internal DNS
      - PYTHONUNBUFFERED=1                    # See logs in real-time

    # Only start with: docker-compose --profile rbi up
    profiles:
      - rbi

# ═══════════════════════════════════════════════════════
# SHARED NETWORK - Internal DNS
# ═══════════════════════════════════════════════════════
networks:
  moondev-network:
    driver: bridge    # Default Docker network driver
    # Automatically provides DNS:
    # - "ollama" resolves to Ollama container IP
    # - "rbi-agent" resolves to RBI container IP

# ═══════════════════════════════════════════════════════
# PERSISTENT STORAGE
# ═══════════════════════════════════════════════════════
volumes:
  ollama_data:
    driver: local
    # Stores models at: /var/lib/docker/volumes/ollama_data
    # Survives container restarts and rebuilds
```

---

## 🔌 Network Communication Details

### Internal Communication (Container → Container)

```python
# In RBI Agent container:
# ────────────────────────────────────────────────────────

import requests

# This hostname "ollama" is resolved by Docker DNS
# to the Ollama container's internal IP (e.g., 172.18.0.2)
response = requests.post(
    "http://ollama:11434/api/generate",
    json={
        "model": "qwen3-coder:30b",
        "prompt": "Write a Python function...",
        "stream": False
    }
)

# Docker network routing:
# rbi-agent (172.18.0.3) → ollama (172.18.0.2)
# Fast: No network interface, just internal routing
# Latency: <1ms
```

### External Testing (Host → Container)

```bash
# From your laptop/desktop:
# ────────────────────────────────────────────────────────

# Test Ollama is responding
curl http://localhost:11434/api/tags

# Generate text
curl http://localhost:11434/api/generate -d '{
  "model": "qwen3-coder:30b",
  "prompt": "Hello!",
  "stream": false
}'

# Docker port mapping:
# localhost:11434 (host) → 11434 (container)
```

---

## 📂 File System: How Data Flows

### Bind Mounts (Live Sync)

```
Host Machine                    RBI Container
─────────────────              ─────────────────
./src/                    →    /app/src/
├── agents/               →    ├── agents/
│   ├── rbi_agent.py      →    │   ├── rbi_agent.py    # Same file!
│   └── chat_agent.py     →    │   └── chat_agent.py
├── models/               →    ├── models/
│   └── model_factory.py  →    │   └── model_factory.py
└── config.py             →    └── config.py

./data/                   →    /app/data/
└── rbi/                  →    └── rbi/
    ├── ideas.txt         →        ├── ideas.txt
    └── 01_15_2025/       →        └── 01_15_2025/
        ├── research/     →            ├── research/
        └── backtests/    →            └── backtests/
```

**Key Point:** Edit `src/agents/rbi_agent.py` on your laptop → instantly available in container!

### Volume (Persistent Storage)

```
Ollama Container              Docker Volume
─────────────────            ─────────────────────────────────
/root/.ollama/         →     /var/lib/docker/volumes/
├── models/            →         moondev_ollama_data/_data/
│   └── blobs/         →             models/
│       └── sha256-... →                 blobs/
│           (15GB)     →                     sha256-abc123...
│                      →                     (qwen3-coder:30b)
└── manifests/         →             manifests/
```

**Key Point:** Model persists across restarts. No re-download needed!

---

## ⚡ Performance: Why It's Fast

### 1. **No Network Overhead**

```
Traditional API Call:
────────────────────────────────────────
Your Code → Internet → OpenAI Data Center → Internet → Your Code
Latency:  10ms        50-200ms              50-200ms   10ms
Total: ~120-420ms + processing time

Docker Internal:
────────────────────────────────────────
RBI Container → Docker Network → Ollama Container
Latency:      0.1ms               0.1ms
Total: ~0.2ms + processing time

🚀 Network overhead: 0.2ms vs 120-420ms (600-2000x faster!)
```

### 2. **Model Always Loaded**

```
Cloud API:
──────────────────────────────────────
Your Request → Queue → Load Model → Inference → Return
Time:         varies   2-5s         8s          varies

Ollama Docker:
──────────────────────────────────────
Your Request → Inference (model pre-loaded) → Return
Time:         0ms       8s                      0ms

🚀 No queue, no cold start
```

### 3. **Parallel Processing**

```yaml
# Scale horizontally with one command:
docker-compose --profile rbi up --scale rbi-agent=5

# Now you have:
# ┌─────────────┐
# │   Ollama    │◄── rbi-agent-1
# │  Container  │◄── rbi-agent-2
# │ (shared)    │◄── rbi-agent-3
# └─────────────┘◄── rbi-agent-4
#               ◄── rbi-agent-5

# Process 5 strategies simultaneously!
# Cost: Still $0.00
```

---

## 🔧 Practical Examples

### Example 1: Test Ollama from Host

```bash
# List loaded models
curl http://localhost:11434/api/tags

# Output:
# {
#   "models": [
#     {
#       "name": "qwen3-coder:30b",
#       "modified_at": "2025-01-15T10:30:00Z",
#       "size": 16894828517
#     }
#   ]
# }
```

### Example 2: Agent Connects to Ollama

```python
# src/models/ollama_model.py (simplified)
# ───────────────────────────────────────────────────────

import requests
import os

class OllamaModel:
    def __init__(self, model_name="qwen3-coder:30b"):
        # Get base URL from environment or use default
        self.base_url = os.getenv(
            "OLLAMA_BASE_URL",
            "http://ollama:11434"  # Docker internal DNS
        )
        self.model_name = model_name

    def generate_response(self, system_prompt, user_content, temperature=0.7):
        url = f"{self.base_url}/api/generate"

        payload = {
            "model": self.model_name,
            "prompt": f"System: {system_prompt}\n\nUser: {user_content}",
            "stream": False,
            "options": {
                "temperature": temperature,
            }
        }

        # Docker network resolves "ollama" to container IP
        response = requests.post(url, json=payload)
        return response.json()["response"]
```

### Example 3: Debug Connection Issues

```bash
# From inside RBI container:
docker-compose exec rbi-agent bash

# Test Ollama connectivity
curl http://ollama:11434/api/tags
# ✅ Works: Docker DNS resolves "ollama"

curl http://localhost:11434/api/tags
# ❌ Fails: localhost = rbi container, not Ollama

# Check network
docker network inspect moondev-network
# Shows both containers on same network with IPs
```

---

## 🎯 Why This Architecture Is "Geolied"

### 1. **Service Isolation**
- Ollama crashes? Agents keep running (restart policy handles it)
- Update agents? Ollama unaffected (bind mounts, no rebuild)

### 2. **Zero Configuration**
- Agents automatically discover Ollama via DNS
- No IP addresses to configure
- No port conflicts

### 3. **Reproducible**
```bash
# Same setup on any machine:
git clone repo
docker-compose up -d
# Done!
```

### 4. **Scalable**
```bash
# Need more power?
docker-compose up --scale rbi-agent=10
# 10x parallelism, same cost
```

### 5. **Observable**
```bash
# Monitor in real-time
docker-compose logs -f ollama     # See AI processing
docker-compose logs -f rbi-agent  # See agent output
docker stats                      # Resource usage
```

---

## 🔥 The "Sublime Samenwerking"

```
┌─────────────────────────────────────────────────────────┐
│ What Makes It Sublime:                                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ ✅ Health Checks         → Agents wait for Ollama      │
│ ✅ DNS Resolution        → No hardcoded IPs            │
│ ✅ Bind Mounts           → Live code sync              │
│ ✅ Persistent Volumes    → Models survive restarts     │
│ ✅ Internal Network      → <1ms latency               │
│ ✅ Automatic Restart     → Self-healing system        │
│ ✅ Profile-based Start   → Start only what you need   │
│ ✅ Environment Isolation → No dependency conflicts    │
│                                                         │
│ Result: A machine that just works™                    │
└─────────────────────────────────────────────────────────┘
```

---

## 📝 TL;DR

1. **Ollama container** hosts qwen3-coder:30b (15GB model)
2. **RBI agent container** runs your trading agents
3. **Docker network** provides internal DNS ("ollama" hostname)
4. **Communication** happens via HTTP API (port 11434)
5. **Latency** is <1ms (internal network, no internet)
6. **Cost** is $0 (all local)
7. **Data** persists via volumes (models) and bind mounts (code)
8. **Scaling** is trivial (docker-compose up --scale)

**This is why it's a geolied machine die subliem samenwerkt.** 🌙

# 🌙 Moon Dev's Docker + Qwen3-Coder Integration

**De geolied samenwerking tussen Docker en lokaal Ollama model voor sublieme AI trading!**

## 🎯 Overview

Deze Docker setup zorgt voor een naadloze integratie tussen:
- **Ollama** met **qwen3-coder:30b** (lokaal AI model)
- **Moon Dev's Trading Agents** (48+ gespecialiseerde agents)
- **RBI Agent** (Research-Backtest-Implement pipeline)

Alles draait in containers voor maximale portabiliteit en isolatie!

## 🚀 Quick Start

### 1. Setup (eenmalig)

```bash
# Maak het setup script executable
chmod +x docker-setup.sh

# Run het setup script
./docker-setup.sh
```

Dit script:
- ✅ Controleert Docker installatie
- ✅ Start Ollama service
- ✅ Download qwen3-coder:30b (30B parameters!)
- ✅ Bouwt trading agents container
- ✅ Configureert netwerk tussen services

### 2. Start de Services

```bash
# Start alle services in achtergrond
docker-compose up -d

# Bekijk logs
docker-compose logs -f trading-agents
```

### 3. Test Qwen3-Coder

```bash
# Quick test
docker-compose exec ollama ollama run qwen3-coder:30b "Write a Python function to calculate RSI"

# Of gebruik de test scripts
docker-compose exec trading-agents python quick_test_qwen.py
```

## 📋 Available Services

### 1. **Ollama Service** (qwen3-coder:30b)
- **Port**: 11434
- **Purpose**: Lokaal AI model voor code generatie
- **Model**: qwen3-coder:30b (30 billion parameters)

```bash
# Check beschikbare modellen
docker-compose exec ollama ollama list

# Pull extra modellen
docker-compose exec ollama ollama pull deepseek-r1
docker-compose exec ollama ollama pull llama3.2
```

### 2. **Trading Agents** (Main Orchestrator)
- **Purpose**: 48+ trading agents voor market analysis
- **Config**: src/config.py
- **Models**: Gebruikt Ollama via netwerk

```bash
# Start trading agents
docker-compose up -d trading-agents

# Bekijk live logs
docker-compose logs -f trading-agents

# Stop trading agents
docker-compose stop trading-agents
```

### 3. **RBI Agent** (Backtest Generator)
- **Purpose**: Genereer backtests van trading strategieën
- **Config**: src/agents/rbi_agent.py (nu met qwen3-coder:30b!)

```bash
# Start RBI agent (met profile)
docker-compose --profile rbi up rbi-agent

# Of run eenmalig
docker-compose run --rm rbi-agent python src/agents/rbi_agent.py

# Bekijk gegenereerde backtests
ls -la src/data/rbi/$(date +%m_%d_%Y)/
```

## 🔧 Configuration

### Environment Variables

Bewerk `.env` voor API keys:
```env
# Trading APIs (optioneel als je alleen lokaal wilt draaien)
BIRDEYE_API_KEY=your_key
MOONDEV_API_KEY=your_key

# AI APIs (niet nodig voor Ollama!)
# ANTHROPIC_KEY=your_key
# OPENAI_KEY=your_key
# DEEPSEEK_KEY=your_key

# Blockchain (optioneel)
SOLANA_PRIVATE_KEY=your_key
RPC_ENDPOINT=https://api.mainnet-beta.solana.com
```

### Model Configuration

Edit `src/agents/rbi_agent.py` om model te kiezen:

```python
# PRESET 1: Local Qwen3-Coder (DEFAULT - FREE!)
RESEARCH_CONFIG = {
    "type": "ollama",
    "name": "qwen3-coder:30b"
}

# Of gebruik andere presets...
```

## 🎨 Architecture

```
┌─────────────────────────────────────────┐
│  Docker Network: moondev-network        │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────┐    ┌───────────────┐ │
│  │   Ollama     │    │    Trading    │ │
│  │  Container   │◄───┤    Agents     │ │
│  │              │    │   Container   │ │
│  │ qwen3-coder  │    └───────────────┘ │
│  │   :30b       │                      │
│  │              │    ┌───────────────┐ │
│  │ Port: 11434  │◄───┤  RBI Agent    │ │
│  └──────────────┘    │   Container   │ │
│                      └───────────────┘ │
│                                         │
└─────────────────────────────────────────┘
         │                    │
         │                    │
         ▼                    ▼
    Volume: ollama_data   Bind Mounts:
    (persistent model)    ./src, ./data
```

## 🧪 Testing

### Test 1: Ollama Connectivity
```bash
# Vanaf host machine
curl http://localhost:11434/api/tags

# Vanuit trading-agents container
docker-compose exec trading-agents curl http://ollama:11434/api/tags
```

### Test 2: Qwen Model Response
```bash
# Quick test
docker-compose exec trading-agents python quick_test_qwen.py

# Full test suite
docker-compose exec trading-agents python test_qwen_model.py
```

### Test 3: RBI Agent
```bash
# Maak test idea
echo "RSI divergence strategy for BTC" > src/data/rbi/ideas.txt

# Run RBI agent
docker-compose --profile rbi up rbi-agent

# Check output
ls -la src/data/rbi/$(date +%m_%d_%Y)/backtests_final/
```

## 📊 Monitoring

### View Container Status
```bash
docker-compose ps
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f ollama
docker-compose logs -f trading-agents
```

### Resource Usage
```bash
# CPU/Memory usage
docker stats

# Detailed inspect
docker-compose exec ollama ps aux
```

## 🛠️ Troubleshooting

### Ollama niet bereikbaar
```bash
# Check of container draait
docker-compose ps ollama

# Check health
docker-compose exec ollama curl http://localhost:11434/api/tags

# Restart service
docker-compose restart ollama
```

### Model niet gevonden
```bash
# List models
docker-compose exec ollama ollama list

# Pull model opnieuw
docker-compose exec ollama ollama pull qwen3-coder:30b
```

### Trading agents crashen
```bash
# Check logs
docker-compose logs trading-agents

# Check dependencies
docker-compose exec trading-agents pip list

# Rebuild container
docker-compose build --no-cache trading-agents
docker-compose up -d trading-agents
```

### Port conflicts
```bash
# Check wat port 11434 gebruikt
sudo lsof -i :11434

# Pas port aan in docker-compose.yml
ports:
  - "11435:11434"  # Host:Container
```

## 🚀 Advanced Usage

### Add More Ollama Models
```bash
# Pull extra modellen
docker-compose exec ollama ollama pull deepseek-r1
docker-compose exec ollama ollama pull llama3.2
docker-compose exec ollama ollama pull gemma:2b

# List alle modellen
docker-compose exec ollama ollama list
```

### Run Custom Agent
```bash
# Maak je eigen agent in src/agents/my_agent.py
# Dan run:
docker-compose exec trading-agents python src/agents/my_agent.py
```

### Scale Services
```bash
# Run meerdere RBI agent instances
docker-compose --profile rbi up --scale rbi-agent=3
```

### Development Mode
```bash
# Mount live code voor development
# (al geconfigureerd in docker-compose.yml)
docker-compose up -d

# Wijzigingen in ./src zijn direct zichtbaar in container!
```

## 🔒 Security

- ✅ Ollama draait in geïsoleerde container
- ✅ Geen externe AI API calls (100% lokaal!)
- ✅ .env file wordt niet gekopieerd naar image
- ✅ Bind mounts zijn read-only waar mogelijk
- ✅ Geen exposed ports naar internet (alleen localhost)

## 💰 Cost Comparison

| Model | Cost per 1M tokens | Speed | Privacy |
|-------|-------------------|-------|---------|
| qwen3-coder:30b (Ollama) | **FREE** 🎉 | FAST ⚡ | 100% LOCAL 🔒 |
| GPT-5 | ~$60 | Moderate | External API |
| DeepSeek | ~$0.14 | Moderate | External API |
| Claude Sonnet | ~$3 | Moderate | External API |

**Voordeel Ollama**: Onbeperkt gebruik, geen API costs, complete privacy!

## 📚 Resources

- [Ollama Documentation](https://ollama.ai/docs)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Qwen3-Coder Model Card](https://huggingface.co/Qwen/Qwen3-Coder-30B)
- [Moon Dev YouTube](https://youtube.com/@moondevonyt)

## 🌟 Tips

1. **Eerste keer**: `docker-compose up` duurt ~20min voor qwen3-coder:30b download (15GB)
2. **Snelheid**: qwen3-coder:30b is snel (~10s voor 500 tokens) op moderne GPU
3. **Memory**: Alloceer minimaal 20GB RAM voor Ollama container
4. **GPU**: Nvidia GPU support via [Ollama GPU docs](https://ollama.ai/docs/gpu)
5. **Backup**: Volume `ollama_data` bevat je modellen - backup deze!

## 🎯 Next Steps

1. ✅ Setup compleet met `./docker-setup.sh`
2. 🧪 Test met `quick_test_qwen.py`
3. 🚀 Start agents met `docker-compose up -d`
4. 💰 Genereer backtests met RBI agent
5. 📈 Monitor met `docker-compose logs -f`

---

**🌙 Built with ❤️ by Moon Dev**

**Een geolied machine die subliem samenwerkt!** 🚀

# Docker Deployment Guide

This guide covers deploying Moon Dev's AI Trading Agents using Docker for production environments.

## Overview

The Docker setup includes:
- **Dockerfile**: Multi-stage build with optimized image size
- **docker-compose.yml**: Easy orchestration with volume mounts and resource limits
- **healthcheck.py**: Robust health checking that verifies the application is actually running
- **Health file mechanism**: Application writes timestamps to verify it's actively processing

## Quick Start

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+
- `.env` file with API keys (see `.env_example`)

### Build and Run

```bash
# Build the image
docker build -t moon-dev-ai-agents .

# Run with docker-compose (recommended)
docker-compose up -d

# Or run with docker directly
docker run -d \
  --name moon-dev-agents \
  --env-file .env \
  -v $(pwd)/src/data:/app/src/data \
  -v $(pwd)/logs:/app/logs \
  moon-dev-ai-agents
```

### View Logs

```bash
# Follow logs
docker-compose logs -f

# View recent logs
docker logs moon-dev-ai-agents --tail 100
```

### Check Health

```bash
# Check health status
docker inspect --format='{{.State.Health.Status}}' moon-dev-ai-agents

# View health check logs
docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' moon-dev-ai-agents
```

## Health Check Implementation

### How It Works

The health check system has two layers:

1. **Process Check**: Verifies that `main.py` is running as a process
2. **Health File Check**: Verifies that the application is actively processing by checking the `.health` file timestamp

### Health Check Script

The `healthcheck.py` script runs every 5 minutes (configurable in Dockerfile) and:
- Searches for `main.py` in the process list using `ps aux`
- Checks if `.health` file exists and was updated in the last 10 minutes
- Returns exit code 0 (healthy) or 1 (unhealthy)

### Health File Updates

The `main.py` application:
- Writes a timestamp to `.health` file on startup
- Updates it at the beginning of each agent cycle
- Fails gracefully if the file can't be written (won't crash the application)

### Configuration

Modify health check parameters in `Dockerfile`:

```dockerfile
HEALTHCHECK --interval=5m --timeout=30s --start-period=1m --retries=3 \
    CMD python /app/healthcheck.py
```

Parameters:
- `--interval`: How often to run health check (default: 5m)
- `--timeout`: Max time for health check to complete (default: 30s)
- `--start-period`: Grace period during startup (default: 1m)
- `--retries`: Failures before marking unhealthy (default: 3)

## Volume Mounts

### Data Persistence

```yaml
volumes:
  - ./src/data:/app/src/data   # Agent outputs and analysis
  - ./logs:/app/logs            # Application logs
```

### Configuration

To make live config changes without rebuilding:

```yaml
volumes:
  - ./src/config.py:/app/src/config.py:ro
```

**Note**: Changes require container restart to take effect.

## Resource Limits

Default limits in `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '4'
      memory: 8G
    reservations:
      cpus: '2'
      memory: 4G
```

Adjust based on:
- Number of active agents
- LLM provider (local Ollama requires more resources)
- Token analysis frequency

## Environment Variables

Required in `.env` file:

```bash
# Trading APIs
BIRDEYE_API_KEY=your_key
MOONDEV_API_KEY=your_key
COINGECKO_API_KEY=your_key

# AI Services
ANTHROPIC_KEY=your_key
OPENAI_KEY=your_key
DEEPSEEK_KEY=your_key
GROQ_API_KEY=your_key

# Blockchain
SOLANA_PRIVATE_KEY=your_key
RPC_ENDPOINT=your_endpoint
```

## Production Recommendations

### Security

1. **Run as non-root user** (already configured in Dockerfile)
2. **Never commit .env files** (excluded in .gitignore)
3. **Use secrets management** for production deployments:
   ```bash
   docker secret create moondev_api_key -
   ```

### Monitoring

Add monitoring services to `docker-compose.yml`:

```yaml
services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    depends_on:
      - prometheus
```

### Logging

Configure log rotation:

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

### Backup

Backup strategy for data volumes:

```bash
# Backup data directory
docker run --rm \
  -v moon-dev-ai-agents_data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/data-$(date +%Y%m%d).tar.gz /data

# Restore
docker run --rm \
  -v moon-dev-ai-agents_data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar xzf /backup/data-20250106.tar.gz -C /
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs moon-dev-agents

# Check container status
docker ps -a

# Verify .env file exists
ls -la .env
```

### Health Check Failing

```bash
# Check health check output
docker inspect moon-dev-ai-agents | jq '.[0].State.Health'

# Run health check manually
docker exec moon-dev-ai-agents python /app/healthcheck.py

# Check if main.py is running
docker exec moon-dev-ai-agents ps aux | grep main.py

# Check health file
docker exec moon-dev-ai-agents cat /app/.health
```

### High Resource Usage

```bash
# Check resource usage
docker stats moon-dev-ai-agents

# Reduce active agents in src/config.py
# Lower analysis frequency in SLEEP_BETWEEN_RUNS_MINUTES
```

### API Rate Limits

```bash
# Increase sleep time between runs
# Edit src/config.py: SLEEP_BETWEEN_RUNS_MINUTES = 30

# Reduce monitored tokens
# Edit src/config.py: MONITORED_TOKENS = [...fewer tokens]
```

## Updating

### Update Application Code

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose up -d --build
```

### Update Dependencies

```bash
# Update requirements.txt
pip install -r requirements.txt --upgrade
pip freeze > requirements.txt

# Rebuild image
docker-compose build --no-cache
docker-compose up -d
```

## Development vs Production

### Development

Use docker-compose with live code mounting:

```yaml
volumes:
  - ./src:/app/src  # Live code changes
```

### Production

Use immutable images:

```bash
# Build tagged image
docker build -t moon-dev-ai-agents:v1.0.0 .

# Push to registry
docker tag moon-dev-ai-agents:v1.0.0 registry.example.com/moon-dev-ai-agents:v1.0.0
docker push registry.example.com/moon-dev-ai-agents:v1.0.0
```

## Support

For issues or questions:
- GitHub Issues: https://github.com/yourusername/moon-dev-ai-agents/issues
- Discord: [Your Discord Link]
- Documentation: See CLAUDE.md and README.md

## License

This Docker setup is part of the Moon Dev AI Trading Agents project and follows the same license.

#!/bin/bash
# 🌙 Moon Dev's Docker + Ollama Setup Script
# This script sets up the complete environment for AI trading agents with local qwen3-coder:30b

set -e

echo "🌙 Moon Dev's AI Trading Agents - Docker Setup"
echo "=============================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed!${NC}"
    echo "Install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

echo -e "${GREEN}✅ Docker is installed${NC}"

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed!${NC}"
    echo "Install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✅ Docker Compose is installed${NC}"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found${NC}"
    echo "Creating .env from .env_example..."
    if [ -f .env_example ]; then
        cp .env_example .env
        echo -e "${GREEN}✅ Created .env file${NC}"
        echo -e "${YELLOW}📝 Please edit .env and add your API keys${NC}"
    else
        echo -e "${RED}❌ .env_example not found!${NC}"
        exit 1
    fi
fi

echo ""
echo "🚀 Starting Docker setup..."
echo ""

# Build and start Ollama service first
echo -e "${CYAN}📦 Building and starting Ollama service...${NC}"
docker-compose up -d ollama

echo ""
echo -e "${YELLOW}⏳ Waiting for Ollama to be ready...${NC}"
sleep 10

# Check if Ollama is healthy
for i in {1..30}; do
    if docker-compose exec -T ollama curl -f http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Ollama is ready!${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ Ollama failed to start${NC}"
        docker-compose logs ollama
        exit 1
    fi
    echo -n "."
    sleep 2
done

echo ""
echo -e "${CYAN}📥 Pulling qwen3-coder:30b model (this may take a while)...${NC}"
docker-compose exec ollama ollama pull qwen3-coder:30b

echo ""
echo -e "${GREEN}✅ qwen3-coder:30b is ready!${NC}"

# List available models
echo ""
echo -e "${CYAN}📋 Available Ollama models:${NC}"
docker-compose exec ollama ollama list

echo ""
echo -e "${CYAN}📦 Building trading agents container...${NC}"
docker-compose build trading-agents

echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "🎯 Available Commands:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  🚀 Start all services:"
echo "     docker-compose up -d"
echo ""
echo "  📊 View logs:"
echo "     docker-compose logs -f trading-agents"
echo ""
echo "  🧪 Run RBI agent:"
echo "     docker-compose --profile rbi up rbi-agent"
echo ""
echo "  🔍 Check Ollama models:"
echo "     docker-compose exec ollama ollama list"
echo ""
echo "  🧪 Test qwen3-coder:"
echo "     docker-compose exec ollama ollama run qwen3-coder:30b 'Hello!'"
echo ""
echo "  🛑 Stop all services:"
echo "     docker-compose down"
echo ""
echo "  🗑️  Remove all (including volumes):"
echo "     docker-compose down -v"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${CYAN}🌙 Moon Dev's AI Trading System is ready to rock!${NC}"
echo ""

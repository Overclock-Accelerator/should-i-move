#!/bin/bash

# Quick start script for AgentOS
# This script sets up and runs AgentOS for the "Should I Move?" application

set -e  # Exit on error

echo "=============================================================================="
echo "🚀 AgentOS Quick Start for 'Should I Move?' Application"
echo "=============================================================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo -e "${RED}❌ Python is not installed. Please install Python 3.11 or higher.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python found: $(python --version)${NC}"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from template...${NC}"
    cat > .env << 'EOF'
# OpenAI API Key (required)
OPENAI_API_KEY=your_openai_key_here

# Firecrawl API Key (for web scraping)
FIRECRAWL_API_KEY=your_firecrawl_key_here

# Brave Search API Key (for Reddit search)
BRAVE_API_KEY=your_brave_key_here

# AgentOS Database Configuration
AGENTOS_DB_URL=postgresql+psycopg://agno:agno@localhost:5532/agno
EOF
    echo -e "${YELLOW}📝 Please edit .env file and add your API keys${NC}"
    echo -e "${YELLOW}   Then run this script again.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ .env file found${NC}"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker not found. Please install Docker to run PostgreSQL.${NC}"
    echo -e "${YELLOW}   Or update AGENTOS_DB_URL in .env to use an existing PostgreSQL instance.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker found: $(docker --version)${NC}"
echo ""

# Check if PostgreSQL container is running
if [ "$(docker ps -q -f name=agentos-postgres)" ]; then
    echo -e "${GREEN}✅ PostgreSQL container already running${NC}"
else
    echo -e "${BLUE}🐘 Starting PostgreSQL with pgvector...${NC}"
    docker run -d \
      --name agentos-postgres \
      -e POSTGRES_USER=agno \
      -e POSTGRES_PASSWORD=agno \
      -e POSTGRES_DB=agno \
      -p 5532:5432 \
      pgvector/pgvector:pg16
    
    echo -e "${GREEN}✅ PostgreSQL container started${NC}"
    echo -e "${YELLOW}⏳ Waiting 5 seconds for PostgreSQL to initialize...${NC}"
    sleep 5
fi

echo ""

# Check if virtual environment exists
if [ -d ".venv" ]; then
    VENV_DIR=".venv"
elif [ -d "venv" ]; then
    VENV_DIR="venv"
else
    echo -e "${BLUE}📦 Creating virtual environment...${NC}"
    python -m venv .venv
    VENV_DIR=".venv"
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi

# Activate virtual environment
echo -e "${BLUE}🔧 Activating virtual environment...${NC}"
source "$VENV_DIR/bin/activate" 2>/dev/null || source "$VENV_DIR/Scripts/activate" 2>/dev/null

# Install dependencies
echo -e "${BLUE}📥 Installing dependencies...${NC}"
pip install -q --upgrade pip
pip install -q -r requirements-agentos.txt

echo -e "${GREEN}✅ Dependencies installed${NC}"
echo ""

# Check if city database exists
if [ ! -f "data/nerdwallet_cities_comprehensive.json" ]; then
    echo -e "${YELLOW}⚠️  City database not found. Creating it now...${NC}"
    python nerdwallet-tools/create_city_database.py
    echo -e "${GREEN}✅ City database created${NC}"
fi

echo ""
echo "=============================================================================="
echo -e "${GREEN}🎉 Setup Complete! Starting AgentOS...${NC}"
echo "=============================================================================="
echo ""
echo -e "${BLUE}📋 Available Resources:${NC}"
echo "   - Agents: Cost Analyst, Sentiment Analyst, Migration Researcher"
echo "   - Team: City Move Decision Team"
echo "   - Knowledge Base: City Relocation Data"
echo ""
echo -e "${BLUE}🌐 Server Information:${NC}"
echo "   - Local URL: http://localhost:7777"
echo "   - API Docs: http://localhost:7777/docs"
echo ""
echo -e "${BLUE}🔗 Next Steps:${NC}"
echo "   1. Visit https://app.agno.com to access the Control Plane"
echo "   2. Click 'Connect AgentOS' and enter: http://localhost:7777"
echo "   3. Start chatting with your agents through the web interface!"
echo ""
echo "=============================================================================="
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""

# Start AgentOS
python 04-agno-agentos.py


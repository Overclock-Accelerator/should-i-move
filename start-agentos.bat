@echo off
REM Quick start script for AgentOS on Windows
REM This script sets up and runs AgentOS for the "Should I Move?" application

setlocal enabledelayedexpansion

echo ==============================================================================
echo 🚀 AgentOS Quick Start for 'Should I Move?' Application
echo ==============================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.11 or higher.
    exit /b 1
)

echo ✅ Python found
python --version
echo.

REM Check if .env file exists
if not exist .env (
    echo ⚠️  .env file not found. Creating from template...
    (
        echo # OpenAI API Key ^(required^)
        echo OPENAI_API_KEY=your_openai_key_here
        echo.
        echo # Firecrawl API Key ^(for web scraping^)
        echo FIRECRAWL_API_KEY=your_firecrawl_key_here
        echo.
        echo # Brave Search API Key ^(for Reddit search^)
        echo BRAVE_API_KEY=your_brave_key_here
        echo.
        echo # AgentOS Database Configuration
        echo AGENTOS_DB_URL=postgresql+psycopg://agno:agno@localhost:5532/agno
    ) > .env
    echo 📝 Please edit .env file and add your API keys
    echo    Then run this script again.
    exit /b 1
)

echo ✅ .env file found
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Docker not found. Please install Docker to run PostgreSQL.
    echo    Or update AGENTOS_DB_URL in .env to use an existing PostgreSQL instance.
    exit /b 1
)

echo ✅ Docker found
docker --version
echo.

REM Check if PostgreSQL container is running
docker ps -q -f name=agentos-postgres >nul 2>&1
if errorlevel 1 (
    echo 🐘 Starting PostgreSQL with pgvector...
    docker run -d --name agentos-postgres -e POSTGRES_USER=agno -e POSTGRES_PASSWORD=agno -e POSTGRES_DB=agno -p 5532:5432 pgvector/pgvector:pg16
    echo ✅ PostgreSQL container started
    echo ⏳ Waiting 5 seconds for PostgreSQL to initialize...
    timeout /t 5 /nobreak >nul
) else (
    echo ✅ PostgreSQL container already running
)

echo.

REM Check if virtual environment exists
if not exist venv (
    echo 📦 Creating virtual environment...
    python -m venv venv
    echo ✅ Virtual environment created
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
python -m pip install -q --upgrade pip
python -m pip install -q -r requirements-agentos.txt

echo ✅ Dependencies installed
echo.

REM Check if city database exists
if not exist data\nerdwallet_cities_comprehensive.json (
    echo ⚠️  City database not found. Creating it now...
    python nerdwallet-tools\create_city_database.py
    echo ✅ City database created
)

echo.
echo ==============================================================================
echo 🎉 Setup Complete! Starting AgentOS...
echo ==============================================================================
echo.
echo 📋 Available Resources:
echo    - Agents: Cost Analyst, Sentiment Analyst, Migration Researcher
echo    - Team: City Move Decision Team
echo    - Knowledge Base: City Relocation Data
echo.
echo 🌐 Server Information:
echo    - Local URL: http://localhost:7777
echo    - API Docs: http://localhost:7777/docs
echo.
echo 🔗 Next Steps:
echo    1. Visit https://app.agno.com to access the Control Plane
echo    2. Click 'Connect AgentOS' and enter: http://localhost:7777
echo    3. Start chatting with your agents through the web interface!
echo.
echo ==============================================================================
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start AgentOS
python 04-agno-agentos.py


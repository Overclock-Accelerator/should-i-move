# AgentOS Integration - Complete Guide

Complete guide for integrating your "Should I Move?" Agno application with AgentOS and the AgentOS Control Plane.

## Table of Contents
1. [What is AgentOS?](#what-is-agentos)
2. [Quick Start](#quick-start)
3. [Detailed Setup](#detailed-setup)
4. [Using AgentOS](#using-agentos)
5. [CLI vs AgentOS Comparison](#cli-vs-agentos-comparison)
6. [API Reference](#api-reference)
7. [Troubleshooting](#troubleshooting)

---

## What is AgentOS?

**AgentOS** is Agno's production-ready runtime that provides:

- **FastAPI Runtime**: Pre-built REST API for serving your agents
- **Control Plane**: Beautiful web interface at https://app.agno.com
- **Session Management**: Track conversation history across interactions
- **Memory Persistence**: Store and retrieve memories for personalized interactions
- **Knowledge Management**: Upload and manage documents for your agents
- **Private by Design**: Runs entirely in your infrastructure - no data leaves your environment

### Architecture Overview

```
Browser → Control Plane (app.agno.com)
              ↓
         FastAPI Server (localhost:7777)
              ↓
    ┌─────────┴─────────┐
    ↓                   ↓
PostgreSQL          Agents/Teams
(sessions,          (Cost, Sentiment,
 memory,             Migration)
 knowledge)
```

---

## Quick Start

### Prerequisites Checklist

**System Requirements:**
- [ ] Python 3.11 or higher
- [ ] Docker (for PostgreSQL) OR existing PostgreSQL server
- [ ] API Keys: OpenAI, Firecrawl, Brave Search

**Get API Keys:**
- OpenAI: https://platform.openai.com/api-keys
- Firecrawl: https://firecrawl.dev/
- Brave Search: https://brave.com/search/api/ (free: 2,000 queries/month)

### Option A: Automated Setup (Recommended)

**Linux/Mac:**
```bash
bash start-agentos.sh
```

**Windows:**
```bash
start-agentos.bat
```

The script will automatically:
1. Check Python installation
2. Verify/create `.env` file
3. Start PostgreSQL in Docker
4. Create virtual environment
5. Install dependencies
6. Start AgentOS server

### Option B: Manual Setup

#### 1. Configure Environment

Create `.env` file:
```bash
# Required API Keys
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
FIRECRAWL_API_KEY=fc-xxxxxxxxxxxxx
BRAVE_API_KEY=BSxxxxxxxxxxxxx

# Database (required for AgentOS)
AGENTOS_DB_URL=postgresql+psycopg://agno:agno@localhost:5532/agno
```

#### 2. Start PostgreSQL

**Using Docker:**
```bash
docker run -d \
  --name agentos-postgres \
  -e POSTGRES_USER=agno \
  -e POSTGRES_PASSWORD=agno \
  -e POSTGRES_DB=agno \
  -p 5532:5432 \
  pgvector/pgvector:pg16
```

**Using Existing PostgreSQL:**
- Enable pgvector extension: `CREATE EXTENSION vector;`
- Update `AGENTOS_DB_URL` in `.env` with your connection string

#### 3. Install Dependencies

```bash
# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Install AgentOS packages
pip install -r requirements-agentos.txt
```

#### 4. Start AgentOS Server

```bash
python agentos_integration.py
```

You should see:
```
🚀 Starting AgentOS for 'Should I Move?' Application
🌐 Server Information:
   - Local URL: http://localhost:7777
   - API Docs: http://localhost:7777/docs
```

#### 5. Connect to Control Plane

1. Visit **https://app.agno.com**
2. Sign in (free account)
3. Click **"Connect AgentOS"**
4. Enter: `http://localhost:7777`
5. Click **"Connect"**

---

## Detailed Setup

### PostgreSQL Options

#### Option 1: Docker (Recommended)
Best for development and testing.

```bash
docker run -d \
  --name agentos-postgres \
  -e POSTGRES_USER=agno \
  -e POSTGRES_PASSWORD=agno \
  -e POSTGRES_DB=agno \
  -p 5532:5432 \
  pgvector/pgvector:pg16
```

#### Option 2: Local PostgreSQL
If you have PostgreSQL installed locally:

```sql
CREATE DATABASE agno;
\c agno
CREATE EXTENSION vector;
```

Update `.env`:
```bash
AGENTOS_DB_URL=postgresql+psycopg://your_user:your_pass@localhost:5432/agno
```

#### Option 3: Skip AgentOS (Use CLI)
If you don't want to set up PostgreSQL:

```bash
# Just use the CLI versions
python 01-agno-coordination.py
python 02-agno-router.py
python 03-agno-cooperation.py
```

CLI mode doesn't require PostgreSQL - works with just API keys!

---

## Using AgentOS

### Web Interface

Once connected to the Control Plane:

**Chat with Agents:**
1. Select an agent or team from sidebar
2. Type your question: "Should I move from Seattle to Austin?"
3. Watch agents work in real-time
4. Get comprehensive recommendations

**Manage Knowledge:**
1. Navigate to "Knowledge" tab
2. Upload city guides, cost reports, etc.
3. Agents automatically use this knowledge

**View Sessions:**
1. Navigate to "Sessions" tab
2. See all conversation history
3. Resume previous conversations

**Browse Memory:**
1. Navigate to "Memory" tab
2. See what agents remember about users
3. Edit or delete memories

### API Usage

**Chat with Team:**
```bash
curl -X POST "http://localhost:7777/teams/move-decision-team/runs" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Should I move from NYC to Austin?"
  }'
```

**Create Session:**
```bash
curl -X POST "http://localhost:7777/sessions" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "cost-analyst",
    "user_id": "user123"
  }'
```

**Continue Session:**
```bash
curl -X POST "http://localhost:7777/agents/cost-analyst/runs" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What about taxes?",
    "session_id": "session_abc123"
  }'
```

**Full API Docs:** http://localhost:7777/docs

---

## CLI vs AgentOS Comparison

### Feature Comparison

| Feature | CLI Mode | AgentOS Mode |
|---------|----------|--------------|
| **Interface** | Terminal | Web UI |
| **Setup** | Simple | Requires PostgreSQL |
| **Sessions** | One-time | Persistent |
| **Memory** | None | PostgreSQL |
| **Knowledge** | Static files | Dynamic upload |
| **Multi-user** | No | Yes |
| **API Access** | No | REST API |
| **Monitoring** | Console logs | Dashboard |
| **Deployment** | Local script | Production server |

### When to Use What?

**Use CLI Mode When:**
- ✅ Quick one-off analyses
- ✅ Testing and development
- ✅ Prefer terminal interfaces
- ✅ Don't need persistence
- ✅ Minimal setup desired

**Use AgentOS When:**
- ✅ Web interface needed
- ✅ Multiple users
- ✅ Session persistence required
- ✅ Building a product/service
- ✅ Need monitoring/analytics
- ✅ API integrations needed

### Commands

**CLI Mode:**
```bash
python 01-agno-coordination.py  # Sequential analysis
python 02-agno-router.py        # Single specialist
python 03-agno-cooperation.py   # Collaborative debate
```

**AgentOS Mode:**
```bash
bash start-agentos.sh           # Linux/Mac
start-agentos.bat               # Windows
# Or manually:
python agentos_integration.py
```

---

## API Reference

### Endpoints

**Run Agent:**
```http
POST /agents/{agent_id}/runs
Content-Type: application/json

{
  "message": "Compare Seattle vs Portland",
  "session_id": "optional-session-id",
  "stream": false
}
```

**Run Team:**
```http
POST /teams/{team_id}/runs
Content-Type: application/json

{
  "message": "Should I move to Austin?",
  "session_id": "optional-session-id",
  "stream": false
}
```

**Manage Sessions:**
```http
POST /sessions              # Create session
GET /sessions/{session_id}  # Get session
PUT /sessions/{session_id}  # Update session
DELETE /sessions/{id}       # Delete session
```

**Manage Knowledge:**
```http
POST /knowledge/upload      # Upload document
GET /knowledge              # List knowledge
DELETE /knowledge/{id}      # Delete document
```

**Manage Memory:**
```http
GET /memory                 # List memories
POST /memory                # Create memory
DELETE /memory/{id}         # Delete memory
```

### Available Resources

**Agents:**
- `cost-analyst` - Financial analysis specialist
- `sentiment-analyst` - City culture specialist
- `migration-researcher` - Reddit insights specialist

**Teams:**
- `move-decision-team` - Complete analysis team

---

## Troubleshooting

### Common Issues

#### Docker Not Found

**Error:** `Docker not found. Please install Docker...`

**Solutions:**
1. **Install Docker:** https://www.docker.com/products/docker-desktop/
2. **Use existing PostgreSQL:** Update `AGENTOS_DB_URL` in `.env`
3. **Skip AgentOS:** Use CLI mode instead (`python 01-agno-coordination.py`)

#### PostgreSQL Connection Failed

**Error:** `could not connect to server...`

**Check:**
```bash
# Is PostgreSQL running?
docker ps | grep agentos-postgres

# Restart if needed
docker restart agentos-postgres

# Or start fresh
docker rm agentos-postgres
docker run -d --name agentos-postgres \
  -e POSTGRES_USER=agno -e POSTGRES_PASSWORD=agno \
  -e POSTGRES_DB=agno -p 5532:5432 pgvector/pgvector:pg16
```

#### Can't Connect to Control Plane

**Error:** Connection refused or timeout

**Check:**
```bash
# Is server running?
curl http://localhost:7777/health

# Should return: {"status": "ok"}
```

**Verify:**
- Server is running on port 7777
- Using `http://` not `https://` for localhost
- Firewall not blocking port 7777

#### Import Errors

**Error:** `ModuleNotFoundError: No module named 'agno'`

**Fix:**
```bash
# Activate virtual environment
source .venv/bin/activate  # or .venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements-agentos.txt
```

#### API Key Errors

**Error:** `OPENAI_API_KEY not set`

**Fix:**
```bash
# Check .env file exists
cat .env

# Verify keys are set
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('OpenAI:', os.getenv('OPENAI_API_KEY')[:10])"
```

#### Port Already in Use

**Error:** `Address already in use: 7777`

**Fix:**
```bash
# Find what's using port 7777
# Linux/Mac:
lsof -i :7777

# Windows:
netstat -ano | findstr :7777

# Kill the process or use different port
# Edit agentos_integration.py, change port 7777 to something else
```

### Database Issues

**Reset PostgreSQL:**
```bash
# Stop and remove container
docker stop agentos-postgres
docker rm agentos-postgres

# Start fresh
docker run -d --name agentos-postgres \
  -e POSTGRES_USER=agno -e POSTGRES_PASSWORD=agno \
  -e POSTGRES_DB=agno -p 5532:5432 pgvector/pgvector:pg16
```

**View PostgreSQL Logs:**
```bash
docker logs agentos-postgres
```

### Agent Failures

**Cost Analyst Fails:**
- Check Firecrawl API key is valid
- Verify internet connection
- Check city names are spelled correctly

**Migration Researcher Fails:**
- Check Brave API key is valid
- Verify API quota (2,000/month free)
- Check internet connection

**General Agent Issues:**
- Check OpenAI API key is valid
- Verify API quota not exceeded
- Review server logs for errors

---

## Production Deployment

### Security

**Add API Key Authentication:**
```bash
# In .env
AGENTOS_API_KEY=your_secure_key_here
```

**Update agentos_integration.py:**
```python
app = create_agentos_app(
    agents=[...],
    teams=[...],
    api_key=os.getenv("AGENTOS_API_KEY"),
)
```

### Docker Deployment

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements-agentos.txt .
RUN pip install -r requirements-agentos.txt

COPY . .
CMD ["python", "agentos_integration.py"]
```

**Build and Run:**
```bash
docker build -t should-i-move-agentos .
docker run -p 7777:7777 --env-file .env should-i-move-agentos
```

### Production Database

Use managed PostgreSQL:
- AWS RDS
- Google Cloud SQL
- Azure Database for PostgreSQL
- Supabase
- Neon

Update `.env` with production connection string.

---

## Next Steps

1. **Try CLI First (5 min):** `python 01-agno-coordination.py`
2. **Set Up AgentOS (10 min):** `bash start-agentos.sh`
3. **Explore Control Plane:** https://app.agno.com
4. **Test API:** http://localhost:7777/docs
5. **Deploy to Production:** Follow deployment guide above

## Resources

- **Agno Documentation:** https://docs.agno.com
- **AgentOS Guide:** https://docs.agno.com/agent-os/introduction
- **Control Plane:** https://app.agno.com
- **API Reference:** https://docs.agno.com/reference-api/overview
- **Discord Support:** https://discord.gg/agno

---

**You now have production-ready agents with both CLI and web interfaces! 🚀**


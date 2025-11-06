# 04 - AgentOS Production Deployment Pattern

## Overview

This pattern demonstrates how to transform a multi-agent system into a **production-ready application** using AgentOS. It takes the coordination pattern and adds enterprise features like session management, memory persistence, knowledge bases, and web-based deployment.

Think of this as "multi-agent system meets production infrastructure" - your agents become persistent, stateful services accessible via API and web interface.

## Key Characteristics

- **FastAPI Server**: Agents served via REST API endpoints
- **Session Management**: Persistent conversations across interactions
- **Memory Persistence**: Agents remember previous discussions
- **Knowledge Base**: Vector-embedded documentation and data
- **Control Plane**: Web-based management interface
- **PostgreSQL Backend**: Database for sessions, memory, and vectors

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│           AgentOS Control Plane (Web UI)                │
│         https://app.agno.com                            │
│  - Chat interface with agents                           │
│  - Session history and management                       │
│  - Agent monitoring and metrics                         │
└─────────────────────────────────────────────────────────┘
                          │
                          │ HTTP/WebSocket
                          │
┌─────────────────────────────────────────────────────────┐
│        FastAPI Server (localhost:7777)                  │
│  - REST API endpoints                                   │
│  - Session management                                   │
│  - Request routing                                      │
└─────────────────────────────────────────────────────────┘
                          │
                ┌─────────┴─────────┐
                │                   │
┌───────────────▼─────┐   ┌─────────▼──────────┐
│  PostgreSQL DB      │   │  Vector DB         │
│  (PgVector)         │   │  (Embeddings)      │
│                     │   │                    │
│  - agent_sessions   │   │  - agent_knowledge │
│  - agent_memory     │   │  - embeddings      │
└─────────────────────┘   └────────────────────┘
                          │
                ┌─────────┴─────────┐
                │                   │
                ▼                   ▼
┌───────────────────────┐   ┌──────────────────┐
│  City Move Decision   │   │  Knowledge Base  │
│       Team            │   │                  │
│                       │   │  - System docs   │
│  Members:             │   │  - City data     │
│  - Cost Analyst       │   │  - Reports       │
│  - Sentiment Analyst  │   │  - Capabilities  │
│  - Migration Researcher│  └──────────────────┘
└───────────────────────┘
```

## What AgentOS Adds

### 1. **Persistence Layer**

**Before (Stateless):**
```python
# Each run is independent
team = Team(name="Move Team", members=[...])
team.print_response("Should I move?")
# No memory of previous conversations
```

**After (Stateful with AgentOS):**
```python
# Sessions persist across interactions
team = Team(
    name="Move Team",
    db=db,  # PostgreSQL for sessions & memory
    knowledge=knowledge_base,  # Shared knowledge
)
# Agents remember previous conversations
# Context is maintained across messages
```

### 2. **Web-Based Interface**

Instead of terminal-only interaction, users can:
- Chat via web browser at https://app.agno.com
- View conversation history
- Switch between agents
- Monitor agent status
- Access from any device

### 3. **Knowledge Base Integration**

```python
relocation_knowledge = Knowledge(
    vector_db=PgVector(embedder=OpenAIEmbedder())
)

# Add system documentation
relocation_knowledge.add_text(SYSTEM_DOCS)

# Add data files
relocation_knowledge.add_directory(path="data", glob="*.json")

# Agents can now query this knowledge
agent = Agent(
    knowledge=relocation_knowledge,  # ← Agents have RAG access
    # ...
)
```

**What this enables:**
- Agents can recall team capabilities
- Access to historical reports
- City data lookup
- Consistent system knowledge across all agents

### 4. **Session Management**

Each conversation gets a unique session ID:
- Users can pause and resume conversations
- Context is maintained across messages
- Multiple users can have independent sessions
- Session history is queryable

### 5. **API-First Architecture**

The system exposes REST endpoints:
- `POST /v1/agents/{agent_id}/runs` - Run an agent
- `POST /v1/teams/{team_id}/runs` - Run a team
- `GET /v1/sessions/{session_id}` - Get session details
- `GET /health` - Health check
- Full OpenAPI docs at `/docs`

## Database Configuration

### PostgreSQL with PgVector

```python
DB_URL = "postgresql+psycopg://agno:agno@localhost:5532/agno"

# Session and memory storage
db = PostgresDb(
    db_url=DB_URL,
    session_table="agent_sessions",
    memory_table="agent_memory",
)

# Vector database for knowledge embeddings
vector_db = PgVector(
    table_name="agent_knowledge",
    db_url=DB_URL,
    embedder=OpenAIEmbedder(id="text-embedding-3-small"),
)
```

### Tables Created:
- `agent_sessions` - Conversation sessions
- `agent_memory` - Agent memory storage
- `agent_knowledge` - Vector embeddings for RAG

## Enhanced Agent Configuration

Each agent gets additional capabilities:

```python
cost_analyst = Agent(
    name="Cost Analyst",
    id="cost-analyst",  # ← Unique ID for routing
    db=db,              # ← Enable session storage
    knowledge=relocation_knowledge,  # ← Access to knowledge base
    # ... rest of configuration
)
```

**New capabilities per agent:**
- **Memory**: Recall facts from earlier in conversation
- **Knowledge Access**: Query embedded documents via RAG
- **Session Context**: Understand conversation history
- **Unique ID**: Addressable via API

## AgentOS Instance

```python
from agno.os import AgentOS

agent_os = AgentOS(
    id="should-i-move-os",
    description="City Relocation Analysis System",
    agents=[cost_analyst, sentiment_analyst, migration_researcher],
    teams=[move_decision_team],
    knowledge=[relocation_knowledge],
)

# Get FastAPI app
app = agent_os.get_app()

# Serve with uvicorn
agent_os.serve(
    app="04-agno-agentos:app",
    host="0.0.0.0",
    port=7777,
    reload=True,
)
```

## Setup and Installation

### Prerequisites

1. **Docker** (for PostgreSQL with PgVector)
2. **Python 3.10+**
3. **Required API Keys**:
   - OpenAI API key
   - Firecrawl API key
   - Brave Search API key

### Step 1: Environment Variables

Create `.env` file:

```bash
# OpenAI
OPENAI_API_KEY=your_openai_key_here

# Data sources
FIRECRAWL_API_KEY=your_firecrawl_key_here
BRAVE_API_KEY=your_brave_search_key_here

# Database (or use default)
AGENTOS_DB_URL=postgresql+psycopg://agno:agno@localhost:5532/agno
```

### Step 2: Start PostgreSQL Database

**Using Docker:**

```bash
docker run -d \
  --name pgvector-db \
  -e POSTGRES_USER=agno \
  -e POSTGRES_PASSWORD=agno \
  -e POSTGRES_DB=agno \
  -p 5532:5432 \
  pgvector/pgvector:pg16
```

**Verify connection:**

```bash
docker exec -it pgvector-db psql -U agno -d agno -c "SELECT version();"
```

### Step 3: Install Dependencies

```bash
# Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install AgentOS requirements
pip install -r requirements-agentos.txt
```

**Key packages:**
- `agno[agentos]` - AgentOS framework
- `psycopg[binary]` - PostgreSQL driver
- `pgvector` - Vector extension for PostgreSQL

### Step 4: Setup City Database

```bash
cd nerdwallet-tools
python create_city_database.py
cd ..
```

### Step 5: Start AgentOS Server

**Windows:**
```bash
start-agentos.bat
```

**Linux/Mac:**
```bash
chmod +x start-agentos.sh
./start-agentos.sh
```

**Or directly:**
```bash
python 04-agno-agentos.py
```

You should see:

```
🚀 Starting AgentOS for 'Should I Move?' Application
================================================================================

📋 Available Resources:
   - 👥 Agents: Cost Analyst, Sentiment Analyst, Migration Researcher
   - 🤝 Team: City Move Decision Team (coordinator)
   - 🧠 Knowledge Base: System docs, team capabilities, city data

🌐 Server Information:
   - Local URL: http://localhost:7777
   - API Docs: http://localhost:7777/docs
   - Health Check: http://localhost:7777/health

🔗 Next Steps:
   1. Visit https://app.agno.com to access the Control Plane
   2. Click 'Connect AgentOS' and enter: http://localhost:7777
   3. Start chatting with your agents through the web interface!
```

### Step 6: Connect to Control Plane

1. **Open browser** → https://app.agno.com
2. **Click "Connect AgentOS"**
3. **Enter URL**: `http://localhost:7777`
4. **Start chatting** with your agents!

## Usage

### Via Control Plane (Web UI)

1. Navigate to https://app.agno.com
2. Select "City Move Decision Team" from the agent list
3. Start a conversation:
   ```
   You: Should I move from Austin to Seattle?
   
   Team: I'd be happy to help you analyze that move! To provide a 
         comprehensive recommendation, I'll need to understand your 
         situation better. Can you share:
         
         1. What's driving your interest in Seattle?
         2. What's your approximate household income and monthly budget?
         3. What do you value most in a city?
   
   You: [Continue conversation...]
   ```

**Features:**
- Natural multi-turn conversations
- Team remembers context from earlier messages
- Can ask clarifying questions at any point
- Real-time delegation to specialized agents visible
- Final report is saved and accessible

### Via API (cURL Example)

```bash
curl -X POST "http://localhost:7777/v1/teams/move-decision-team/runs" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Should I move from Austin to Seattle? I make $150k/year and value outdoor activities."
  }'
```

### Via Python SDK

```python
import requests

response = requests.post(
    "http://localhost:7777/v1/teams/move-decision-team/runs",
    json={
        "message": "Should I move from Austin to Seattle?",
        "session_id": "user-123"  # Optional: for session continuity
    }
)

result = response.json()
print(result["content"])
```

## Conversation Flow with Memory

### First Message:
```
User: I'm thinking about moving to Miami

Team: Great! Let me help you analyze that move. Where are you 
      currently living?

[Session ID created: sess_abc123]
[Memory stored: User considering Miami move]
```

### Second Message (Same Session):
```
User: I'm in Boston

Team: Got it - Boston to Miami! That's quite a change. Since 
      I remember you're interested in Miami, can you share what's 
      driving this consideration?

[Memory retrieved: Previous context about Miami]
[Memory stored: Current city = Boston, Desired = Miami]
```

### Third Message:
```
User: I'm tired of the cold winters

Team: That makes sense - Miami certainly offers a warm climate! 
      Let me gather some more details about your financial situation...

[Memory retrieved: Boston → Miami, reason = cold winters]
[Continues conversation with full context]
```

## Knowledge Base Features

### What's in the Knowledge Base?

1. **System Documentation** (embedded at startup):
   - Team structure and roles
   - Agent capabilities
   - Tool descriptions
   - Conversation flow
   
2. **City Data** (from `data/` directory):
   - NerdWallet city database
   - Historical comparison data

3. **Dynamic Content**:
   - Previous analysis reports (can be added)
   - User feedback and insights

### How Agents Use It

Agents can query the knowledge base during conversations:

```python
# Agent instruction example:
"If asked about your capabilities, reference the knowledge base 
 for team member details"

# At runtime:
User: What can the Cost Analyst do?

Agent: [Queries knowledge base]
       The Cost Analyst specializes in financial analysis using 
       real-time NerdWallet data, covering housing costs, 
       transportation, food prices, and tax implications...
```

### Benefits:
- Consistent answers about system capabilities
- Access to historical data
- Reduced hallucinations about team structure
- Can cite specific documentation

## Enhanced Instructions

All agents have production-grade instructions:

### Team Leader Example:
```python
instructions=[
    "🤝 YOUR ROLE:",
    "- Engage in natural, helpful conversations",
    "- Ask clarifying questions when needed",
    "- Coordinate specialists to provide analysis",
    
    "💬 CONVERSATIONAL APPROACH:",
    "- Be warm and empathetic",
    "- Remember context from earlier messages",  # ← Memory!
    "- Explain what your team will do",
    
    "🧠 REMEMBER:",
    "- You have access to a knowledge base",      # ← RAG!
    "- You maintain conversation memory",         # ← Sessions!
]
```

## Monitoring and Observability

### Health Check

```bash
curl http://localhost:7777/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-06T21:30:00Z",
  "agents": ["cost-analyst", "sentiment-analyst", "migration-researcher"],
  "teams": ["move-decision-team"]
}
```

### API Documentation

Visit http://localhost:7777/docs for:
- Interactive API testing
- Schema documentation
- Example requests/responses
- Authentication details (if configured)

### Database Inspection

```bash
# Check sessions
docker exec -it pgvector-db psql -U agno -d agno \
  -c "SELECT id, created_at FROM agent_sessions ORDER BY created_at DESC LIMIT 5;"

# Check memory entries
docker exec -it pgvector-db psql -U agno -d agno \
  -c "SELECT session_id, created_at FROM agent_memory ORDER BY created_at DESC LIMIT 5;"

# Check knowledge embeddings
docker exec -it pgvector-db psql -U agno -d agno \
  -c "SELECT COUNT(*) FROM agent_knowledge;"
```

## Generated Reports

Reports are still saved to `reports/` folder as markdown files:

**Filename format:** `{current_city}_to_{desired_city}_{timestamp}_analysis.md`

**Enhanced with:**
- Session ID for traceability
- Conversation history context
- Knowledge base references (if used)
- Memory snapshots

## Comparison: Terminal vs AgentOS

| Feature | Terminal (01-03) | AgentOS (04) |
|---------|-----------------|--------------|
| **Interface** | Command line only | Web UI + API |
| **State** | Stateless | Session-based |
| **Memory** | None | Persistent |
| **Knowledge** | None | Vector RAG |
| **Multi-user** | No | Yes |
| **API Access** | No | REST API |
| **Deployment** | Local script | Server/production |
| **Monitoring** | Console logs | Metrics + logs |
| **Database** | None | PostgreSQL |

## When to Use AgentOS Pattern

**Use AgentOS when:**
- Building production applications
- Need multi-user support
- Want persistent conversations
- Require API access
- Building web applications
- Need monitoring and observability
- Want session management
- Need knowledge base integration

**Use Terminal patterns when:**
- Quick prototyping
- Single-user local tool
- No persistence needed
- Simplicity is priority
- No server infrastructure

## Deployment Options

### Local Development
```bash
python 04-agno-agentos.py
# Runs on localhost:7777
```

### Production Deployment

**1. Docker Compose:**
```yaml
version: '3.8'
services:
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_USER: agno
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: agno
    volumes:
      - pgdata:/var/lib/postgresql/data
    
  agentos:
    build: .
    environment:
      AGENTOS_DB_URL: postgresql+psycopg://agno:${DB_PASSWORD}@postgres:5432/agno
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    ports:
      - "7777:7777"
    depends_on:
      - postgres
```

**2. Cloud Deployment (e.g., AWS/GCP/Azure):**
- Deploy PostgreSQL as managed service (RDS, Cloud SQL)
- Deploy FastAPI app to container service (ECS, Cloud Run, AKS)
- Configure environment variables
- Set up load balancer for API endpoints
- Enable SSL/TLS for production

**3. Kubernetes:**
- Deploy as StatefulSet (for database)
- Deploy FastAPI as Deployment
- Use ConfigMaps for configuration
- Use Secrets for API keys
- Add HPA for auto-scaling

## Troubleshooting

### Database Connection Issues

```bash
# Test database connection
docker exec -it pgvector-db psql -U agno -d agno -c "SELECT 1;"

# Check if PgVector extension is enabled
docker exec -it pgvector-db psql -U agno -d agno -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Verify tables exist
docker exec -it pgvector-db psql -U agno -d agno -c "\dt"
```

### Server Won't Start

```bash
# Check if port 7777 is already in use
netstat -ano | findstr :7777  # Windows
lsof -i :7777                  # Linux/Mac

# Check environment variables
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('AGENTOS_DB_URL'))"
```

### Knowledge Base Not Loading

```bash
# Verify data directory exists
ls -la data/

# Check file permissions
chmod 644 data/*.json

# Test manual knowledge loading
python -c "
from agno.knowledge.knowledge import Knowledge
from agno.vectordb.pgvector import PgVector
kb = Knowledge(vector_db=PgVector(...))
kb.add_directory('data', glob='*.json')
"
```

## Advanced Features

### Custom Knowledge Sources

```python
# Add web content to knowledge base
relocation_knowledge.add_url(
    url="https://example.com/city-guide",
    title="City Moving Guide"
)

# Add PDF documents
relocation_knowledge.add_pdf(
    path="docs/relocation-handbook.pdf",
    title="Relocation Handbook"
)
```

### Session Management

```python
# Get session history
from agno.db.postgres import PostgresDb

db = PostgresDb(db_url=DB_URL)
sessions = db.get_sessions(agent_id="move-decision-team")

for session in sessions:
    print(f"Session {session.id}: {session.created_at}")
    messages = db.get_memory(session_id=session.id)
    for msg in messages:
        print(f"  {msg.role}: {msg.content[:50]}...")
```

### Agent Metrics

```python
# Track agent performance
@app.middleware("http")
async def track_metrics(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    # Log metrics
    print(f"Request to {request.url.path} took {duration:.2f}s")
    
    return response
```

## Project Files

**Main Script:** `04-agno-agentos.py`

**Configuration:**
- `.env` - Environment variables
- `requirements-agentos.txt` - Python dependencies
- `start-agentos.sh` / `start-agentos.bat` - Launch scripts

**Documentation:**
- `agentos-reference/README.md` - AgentOS overview
- `agentos-reference/ARCHITECTURE.md` - Detailed architecture
- `agentos-reference/GETTING_STARTED.md` - Setup guide

## Future Enhancements

### Potential Additions:
- 🔄 Authentication and authorization (JWT, OAuth)
- 🔄 Rate limiting and quotas per user
- 🔄 WebSocket support for streaming responses
- 🔄 Advanced analytics dashboard
- 🔄 A/B testing for agent instructions
- 🔄 Feedback collection and learning
- 🔄 Multi-language support
- 🔄 Export conversation transcripts
- 🔄 Admin panel for knowledge base management

## Key Takeaways

**AgentOS transforms your agents into:**
1. **Stateful Services** - Remember conversations and context
2. **API-First** - Accessible via REST endpoints
3. **Production-Ready** - With monitoring, persistence, and scalability
4. **Knowledge-Enabled** - With RAG access to documentation
5. **Web-Accessible** - Through the Control Plane UI
6. **Multi-User** - Supporting concurrent sessions

**Bottom line:** If you need to deploy agents as a service, AgentOS provides the infrastructure layer you need.

---

**Related Files:**
- `04-agno-agentos.py` - This AgentOS implementation
- `01-agno-coordination.py` - Terminal coordination pattern (stateless)
- `03-agno-cooperation.py` - Terminal cooperation pattern (stateless)
- `agentos-reference/` - Full AgentOS documentation

**External Resources:**
- AgentOS Control Plane: https://app.agno.com
- Agno Documentation: https://docs.agno.com
- PgVector: https://github.com/pgvector/pgvector



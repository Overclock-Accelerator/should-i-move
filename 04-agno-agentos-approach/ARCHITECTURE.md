# AgentOS Architecture Reference

Visual diagrams and technical details of the AgentOS integration.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER'S BROWSER                          │
│                   https://app.agno.com                          │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTPS + WebSocket
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                  AGENTOS CONTROL PLANE                          │
│                   (Hosted by Agno)                              │
│                                                                 │
│  • Chat UI  • Knowledge Manager  • Session Browser             │
│  • Memory Browser  • Performance Metrics                        │
│  🔒 NO DATA STORED - Direct browser connection                  │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP/WebSocket (from browser)
                         │
┌────────────────────────▼────────────────────────────────────────┐
│               YOUR AGENTOS SERVER                               │
│           (Your Infrastructure - Port 7777)                     │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                    REST API                              │  │
│  │  /agents/{id}/runs  /teams/{id}/runs  /sessions        │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              AGENTS & TEAMS                              │  │
│  │  Cost Analyst  │  Sentiment  │  Migration Researcher    │  │
│  │                    Team Coordinator                      │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                 CUSTOM TOOLS                             │  │
│  │  NerdWallet Scraper  │  Brave Reddit Search             │  │
│  └─────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                    POSTGRESQL + pgvector                        │
│  agent_sessions  │  agent_memory  │  agent_knowledge            │
└─────────────────────────────────────────────────────────────────┘
```

## Request Flow

```
USER TYPES: "Should I move from Seattle to Austin?"
    ↓
Browser → Control Plane (app.agno.com)
    ↓
Control Plane → Your Server (localhost:7777)
    POST /teams/move-decision-team/runs
    ↓
AgentOS Server:
    ├─ Load session from PostgreSQL (if exists)
    ├─ Load user memories
    └─ Delegate to Team Coordinator
    ↓
Team Coordinator delegates to agents:
    ├─ Cost Analyst → scrapes NerdWallet
    ├─ Sentiment Analyst → analyzes city culture  
    └─ Migration Researcher → searches Reddit via Brave
    ↓
Agents return analyses → Team synthesizes
    ↓
Save to PostgreSQL:
    ├─ Conversation → agent_sessions
    ├─ Memories → agent_memory
    └─ Knowledge vectors → agent_knowledge
    ↓
Response streams back through Control Plane → Browser
    ↓
USER SEES: Complete recommendation with all analyses
```

## Database Schema

```sql
-- Session Management
CREATE TABLE agent_sessions (
    session_id VARCHAR PRIMARY KEY,
    agent_id VARCHAR NOT NULL,
    user_id VARCHAR,
    messages JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Memory Storage
CREATE TABLE agent_memory (
    memory_id SERIAL PRIMARY KEY,
    agent_id VARCHAR NOT NULL,
    user_id VARCHAR NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Knowledge Base (with pgvector)
CREATE TABLE agent_knowledge (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding VECTOR(1536),  -- OpenAI embedding dimension
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX ON agent_knowledge USING ivfflat (embedding vector_cosine_ops);
```

## Component Interactions

### Agent Tool Execution

```
Agent: "I need cost data"
    ↓
Call: get_cost_of_living_comparison("Seattle", "Austin")
    ↓
    ├─ find_best_city_match("Seattle")
    │  └─ Returns: "seattle-wa"
    │
    ├─ find_best_city_match("Austin")
    │  └─ Returns: "austin-tx"
    │
    └─ Build URL: nerdwallet.com/...compare/seattle-wa-vs-austin-tx
       ↓
       Firecrawl scrapes page
       ↓
       Returns: Structured cost data
       ↓
       Agent analyzes → CostAnalysis model
```

### Session Persistence

```
FIRST MESSAGE:
User: "Tell me about Austin"
    ↓
Create session_id = "abc123"
Save to agent_sessions table
    ↓
Response sent

SECOND MESSAGE:
User: "What about cost of living?"
    ↓
Load session "abc123" from database
    ↓
Agent has full context from previous message
    ↓
Process with conversation history
    ↓
Update session in database
```

### Memory System

```
DURING CONVERSATION:
Agent observes: "User prefers walkable cities"
    ↓
Extract as memory
    ↓
INSERT INTO agent_memory (
    user_id: "user123",
    agent_id: "sentiment-analyst",
    content: "User prefers walkable cities",
    metadata: {"category": "preference"}
)

NEXT CONVERSATION:
Agent loads memories for user123
    ↓
"I remember you prefer walkable cities..."
    ↓
Personalized recommendation
```

## Deployment Architectures

### Local Development

```
┌────────────────┐
│  Your Laptop   │
│  ┌──────────┐  │
│  │ Browser  │  │
│  └────┬─────┘  │
│       │        │
│  ┌────▼──────┐ │
│  │ AgentOS  │ │  Port 7777
│  │ FastAPI  │ │
│  └────┬──────┘ │
│       │        │
│  ┌────▼──────┐ │
│  │PostgreSQL│ │  Port 5532 (Docker)
│  └──────────┘ │
└────────────────┘
         ↑
         │ Connect to: http://localhost:7777
         │
    Control Plane
    app.agno.com
```

### Production Deployment

```
┌─────────────────── CLOUD PROVIDER ─────────────────────┐
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │          Load Balancer (HTTPS)                  │  │
│  └────────────────┬────────────────────────────────┘  │
│                   │                                    │
│  ┌────────────────▼───────────────────────────────┐  │
│  │     AgentOS Instances (Auto-scaling)           │  │
│  │   ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐     │  │
│  │   │ Pod1 │  │ Pod2 │  │ Pod3 │  │ PodN │     │  │
│  └───┬──────┴──┬──────┴──┬──────┴──┬──────┴─────┘  │
│      │         │         │         │                 │
│  ┌───▼─────────▼─────────▼─────────▼─────────────┐  │
│  │    Managed PostgreSQL (RDS/Cloud SQL)         │  │
│  │    - Automatic backups                        │  │
│  │    - High availability                        │  │
│  │    - Read replicas                            │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
                      ↑
                      │ HTTPS
                      │
            ┌─────────┴──────────┐
            │   Control Plane    │
            │   app.agno.com     │
            │                    │
            │   Users connect    │
            │   from anywhere    │
            └────────────────────┘
```

## Security Layers

```
┌──────────────────────────────────────────────────┐
│               SECURITY LAYERS                     │
├──────────────────────────────────────────────────┤
│ 1. HTTPS/TLS                                     │
│    └─ All traffic encrypted                      │
│                                                   │
│ 2. Bearer Token Auth                             │
│    └─ AGENTOS_API_KEY                           │
│                                                   │
│ 3. Database Credentials                          │
│    └─ PostgreSQL auth                            │
│                                                   │
│ 4. Network Isolation                             │
│    └─ DB not publicly accessible                 │
│                                                   │
│ 5. Private Deployment                            │
│    └─ All data in your infrastructure            │
│    └─ Control Plane never stores data            │
└──────────────────────────────────────────────────┘
```

## Comparison: CLI vs AgentOS

### CLI Architecture

```
Terminal
   ↓
Python Script (*.py)
   ↓
Agents
   ├─ Cost Analyst
   ├─ Sentiment Analyst
   └─ Migration Researcher
   ↓
Tools → External APIs
   ├─ Firecrawl (NerdWallet)
   └─ Brave Search (Reddit)
   ↓
Console Output
   └─ Markdown Report (reports/*.md)
```

**Characteristics:**
- ✅ Simple: No database, no server
- ✅ Fast: Direct execution
- ❌ No persistence: One-time run
- ❌ Single user only
- ❌ No API access

### AgentOS Architecture

```
Browser → Control Plane → FastAPI Server
                              ↓
                         PostgreSQL
                              ↓
                           Agents
                              ↓
                       Tools → APIs
                              ↓
                    Web UI + API Response
```

**Characteristics:**
- ✅ Multi-user: Concurrent sessions
- ✅ Persistent: Sessions + memory
- ✅ API: REST endpoints
- ✅ Monitoring: Dashboard + metrics
- ❌ Complex: Requires database
- ❌ Setup: More dependencies

## Technology Stack

### AgentOS Stack

```
┌─────────────────────────────────────────┐
│         Frontend (Browser)              │
│  • Control Plane UI (app.agno.com)     │
│  • WebSocket for real-time updates     │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         Backend (Your Server)           │
│  • Python 3.11+                        │
│  • FastAPI (REST API framework)        │
│  • Uvicorn (ASGI server)               │
│  • Agno (agent framework)              │
│  • SQLAlchemy (ORM)                    │
│  • psycopg (PostgreSQL driver)         │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         Database                        │
│  • PostgreSQL 16                       │
│  • pgvector extension                  │
│  • Vector similarity search            │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│         External APIs                   │
│  • OpenAI (GPT-4o-mini, embeddings)    │
│  • Firecrawl (web scraping)            │
│  • Brave Search (Reddit data)          │
└─────────────────────────────────────────┘
```

## Data Flow Patterns

### Pattern 1: Stateless Request (No Session)

```
Request → AgentOS → Process → Response
             ↓
        No persistence
        Fresh context
```

### Pattern 2: Stateful Session

```
Request → Load Session → Add to History → Process → Save Session → Response
             ↓              ↓                           ↓
        PostgreSQL    Conversation          agent_sessions table
                        Context
```

### Pattern 3: Memory-Enhanced

```
Request → Load Session + Memories → Process with Context → Save Updates
             ↓              ↓                                    ↓
        agent_sessions  agent_memory                 Both tables updated
        
Agent knows:
- Previous conversations (session)
- User preferences (memories)
- Historical patterns (memories)
```

## Scaling Considerations

### Vertical Scaling
- Increase server CPU/RAM
- Larger PostgreSQL instance
- More agent workers

### Horizontal Scaling
```
┌─────────────────────────────────┐
│       Load Balancer             │
└──┬───────┬───────┬──────────┬──┘
   │       │       │          │
┌──▼──┐ ┌──▼──┐ ┌──▼──┐  ┌──▼──┐
│ Pod1│ │ Pod2│ │ Pod3│  │ PodN│
└──┬──┘ └──┬──┘ └──┬──┘  └──┬──┘
   └───────┴───────┴─────────┘
              │
    ┌─────────▼──────────┐
    │  Shared PostgreSQL │
    │  (or read replicas)│
    └────────────────────┘
```

### Performance Optimization
- Connection pooling
- Query optimization
- Vector index tuning (pgvector)
- Caching layer (Redis)
- Async processing

## Key Design Decisions

1. **Private by Design**
   - Control Plane doesn't store data
   - All data in your PostgreSQL
   - Direct browser ↔ server connection

2. **Agent Reusability**
   - Same agents work in CLI and AgentOS
   - No code duplication
   - Easy maintenance

3. **Session-First**
   - Every conversation can be a session
   - Optional: anonymous sessions
   - User-scoped memories

4. **Tool Flexibility**
   - Custom tools (Brave, NerdWallet)
   - Easy to add new tools
   - Tools work in both modes

5. **Standard Tech Stack**
   - FastAPI (industry standard)
   - PostgreSQL (proven, reliable)
   - OpenAI (standardized models)

---

**For implementation details, see:** `agentos_integration.py`

**For usage instructions, see:** `GETTING_STARTED.md`




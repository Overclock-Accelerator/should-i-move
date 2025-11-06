# Should I Move? 🏙️ → 🌆

AI-powered city relocation decision assistant using multi-agent systems to analyze cost of living, city culture, and real migration experiences from Reddit.

## Features

✅ **Real Cost of Living Data** - Scrapes NerdWallet for actual cost comparisons  
✅ **City Vibe Analysis** - Analyzes culture, livability, and lifestyle fit  
✅ **Reddit Migration Insights** - Searches Reddit for real experiences from people who made similar moves  
✅ **Comprehensive Recommendations** - Synthesizes all data into actionable advice  
✅ **Multiple Analysis Modes** - Choose between coordination or cooperation strategies  

## Quick Start

### Option 1: CLI Mode (Interactive Terminal) 💻

**Run directly in your terminal:**

#### 1. Setup Environment

```bash
# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: source .venv/Scripts/activate

# Install dependencies
pip install agno openai python-dotenv requests
```

#### 2. Configure API Keys

Create a `.env` file in the project root:

```bash
# Required API Keys
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
FIRECRAWL_API_KEY=fc-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
BRAVE_API_KEY=BSxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Get your API keys:**
- OpenAI: https://platform.openai.com/api-keys
- Firecrawl: https://firecrawl.dev/
- Brave Search: https://brave.com/search/api/ (free tier: 2,000 queries/month)

#### 3. Run the App

**Choose your analysis mode:**

**Coordination Mode (Sequential Analysis)**
```bash
python 01-agno-coordination.py
```
Agents work independently, then results are synthesized.

**Cooperation Mode (Collaborative Debate)**
```bash
python 03-agno-cooperation.py
```
Agents debate together and reach consensus, prioritizing your most important factor.

**Both modes will:**
1. Ask about your current and desired cities
2. Gather your financial situation and preferences
3. Ask what matters MOST to you (cooperation mode)
4. Analyze cost of living, city culture, and Reddit discussions
5. Provide a comprehensive recommendation

---

### Option 2: AgentOS (Production-Ready Web Interface) 🚀

**Run as a production server with beautiful web UI:**

```bash
# Linux/Mac
bash start-agentos.sh

# Windows
start-agentos.bat
```

Then visit **https://app.agno.com** and connect to `http://localhost:7777`

**Features:**
- 🌐 Beautiful web interface for chatting with agents
- 💾 Session persistence across conversations
- 🧠 Memory management for personalized interactions
- 📚 Knowledge base management
- 📊 Performance monitoring
- 🔌 REST API for integrations

See [agentos-reference/GETTING_STARTED.md](agentos-reference/GETTING_STARTED.md) for detailed setup instructions.

## Project Structure

```
should-i-move/
├── agentos_integration.py            # 🚀 AgentOS server (production)
├── start-agentos.sh                  # Quick start script (Linux/Mac)
├── start-agentos.bat                 # Quick start script (Windows)
├── requirements-agentos.txt          # AgentOS dependencies
├── 01-agno-coordination.py           # CLI: Coordination mode
├── 02-agno-router.py                 # CLI: Router mode
├── 03-agno-cooperation.py            # CLI: Cooperation mode
├── .env                              # API keys (create this)
├── README.md                         # This file
├── agentos-reference/                # 📚 AgentOS documentation
│   ├── README.md                     # Documentation guide
│   ├── GETTING_STARTED.md            # Complete setup guide
│   └── ARCHITECTURE.md               # Technical architecture
├── 02-agno-coordination-approach/    # Coordination strategy docs
│   └── README.md
├── 03-agno-cooperation-approach/     # Cooperation strategy docs
│   └── README.md
├── brave_tools/                      # Reddit search via Brave API
│   ├── brave_search_tool.py         # Custom search tool
│   ├── test_brave_integration.py    # Tests
│   └── README.md                     # Tool documentation
├── data/                             # NerdWallet city database
│   └── nerdwallet_cities_comprehensive.json
├── nerdwallet-tools/                 # Cost of living utilities
│   ├── city_matcher.py
│   ├── create_city_database.py
│   └── validate_cities.py
├── reports/                          # Generated analysis reports
│   └── {city}_to_{city}_analysis.md
└── docs/                             # Documentation
    └── archive/                      # Setup guides & debug files
```

## How It Works

### Two Analysis Modes

#### 🎯 Coordination Mode (`01-agno-coordination.py`)
**Sequential, Independent Analysis**

- Team leader delegates tasks one-by-one to each specialist
- Agents work independently with their specialized tools
- Results are synthesized at the end by the coordinator
- Best for: Straightforward decisions, when expert opinions don't conflict

```
Coordinator → Cost Analyst → [waits] → Sentiment Analyst → [waits] → Migration Researcher
                    ↓                           ↓                              ↓
                Analysis 1                 Analysis 2                    Analysis 3
                                              ↓
                                    Final Synthesis
```

#### 🤝 Cooperation Mode (`03-agno-cooperation.py`)
**Collaborative Debate & Consensus**

- All agents receive the task simultaneously
- Agents discuss findings and debate perspectives
- Team focuses on user's **most important factor**
- Agents defer to user priorities even if data suggests otherwise
- Consensus reached through collaborative discussion
- Best for: Complex decisions, when priorities matter, when expert opinions might conflict

```
                        Coordinator
                             ↓
        ┌────────────────────┼────────────────────┐
        ↓                    ↓                    ↓
   Cost Analyst      Sentiment Analyst    Migration Researcher
        ↓                    ↓                    ↓
        └────────────────────┼────────────────────┘
                             ↓
                    Collaborative Debate
                  (focused on user priority)
                             ↓
                     Consensus Reached
```

### Agent Architecture

Both modes use the same **Team of Specialized Agents**:

1. **Cost Analyst** 💰
   - Fetches real cost data from NerdWallet
   - Compares housing, food, transportation, taxes
   - Provides financial impact summary
   - (Cooperation mode: Adjusts weight based on user priority)

2. **Sentiment Analyst** 🎭
   - Analyzes city vibe and culture
   - Assesses livability based on user preferences
   - Identifies pros and cons
   - (Cooperation mode: Defers to user's most important factor)

3. **Migration Researcher** 🔍
   - Searches Reddit for real migration stories
   - Extracts common reasons, challenges, outcomes
   - Highlights what Redditors are saying
   - (Cooperation mode: Filters insights by user priority)

4. **Team Coordinator** 🎯
   - (Coordination mode: Synthesizes independent analyses)
   - (Cooperation mode: Moderates debate, ensures consensus)
   - Provides final recommendation
   - Suggests next steps

### Reddit Search (Custom Brave Tool)

Instead of using Reddit's API (which has authentication issues), we use **Brave Search** with `site:reddit.com` queries to find discussions:

```
site:reddit.com should I move from Seattle to New York
site:reddit.com moved from Seattle to New York
site:reddit.com Seattle to New York relocation
```

This approach:
- ✅ Avoids Reddit API auth complexity
- ✅ Gets comprehensive search results
- ✅ Works reliably in all environments
- ✅ No dependency issues

## Testing

### Test Brave Search Integration
```bash
python brave_tools/test_brave_integration.py
```

Expected output:
```
🎉 All tests passed! Custom Brave Search integration is working!
✅ No dependency issues!
✅ Works in your .venv environment!
```

## Example Output

```json
{
  "recommendation": "Recommend moving with careful financial planning",
  "confidence_level": "Medium-High",
  "key_supporting_factors": [
    "Strong career growth opportunities in NYC tech scene",
    "Better alignment with preference for urban density and culture",
    "Public transit eliminates car expenses"
  ],
  "key_concerns": [
    "19% higher cost of living overall",
    "Housing costs 45% more expensive",
    "Smaller living spaces require adjustment"
  ],
  "reddit_insights": "Based on 12 Reddit discussions, Redditors commonly mention the cost increase is real but career opportunities offset it..."
}
```

## API Usage & Limits

| Service | Free Tier | Usage Per Analysis |
|---------|-----------|-------------------|
| OpenAI | Pay-per-use | ~$0.01-0.05 |
| Firecrawl | Varies | 1 scrape |
| Brave Search | 2,000/month | 4 searches |

**Estimated capacity:** ~500 city pair analyses per month on free tiers

## Troubleshooting

### "BRAVE_API_KEY not set"
- Create `.env` file in project root
- Add: `BRAVE_API_KEY=BSxxxxx`
- Restart terminal/IDE

### "City not found in database"
- Run: `python nerdwallet-tools/validate_cities.py`
- Check city name spelling
- Try "City, State" format (e.g., "Seattle, WA")

### "No Reddit discussions found"
- Normal for uncommon city pairs
- Agent falls back to general knowledge
- Not an error

## Development

### City Database
The app includes a comprehensive database of ~200 US cities with NerdWallet URL formats. To update:

```bash
python nerdwallet-tools/create_city_database.py
```

### Adding New Tools
Custom tools can be added to agents. See `brave-tools/brave_search_tool.py` for an example.

## Documentation

### AgentOS Documentation (Production Mode)
- **[Getting Started Guide](agentos-reference/GETTING_STARTED.md)** - Complete setup, usage, and troubleshooting
- **[Architecture Reference](agentos-reference/ARCHITECTURE.md)** - System diagrams and technical details

### Legacy Documentation
Historical setup guides and troubleshooting docs are in `docs/archive/`:
- Brave Search setup
- Migration researcher updates
- venv troubleshooting
- Alternative approaches attempted

## License

MIT

## Contributing

Feel free to submit issues or PRs for:
- Additional data sources
- New analysis agents
- City database improvements
- UI enhancements


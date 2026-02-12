# Should I Move? 🏙️ → 🌆

AI-powered city relocation decision assistant using multi-agent systems to analyze cost of living, city culture, and real migration experiences from Reddit.

## Features

✅ **Real Cost of Living Data** - Scrapes NerdWallet for actual cost comparisons  
✅ **City Vibe Analysis** - Analyzes culture, livability, and lifestyle fit  
✅ **Reddit Migration Insights** - Searches Reddit for real experiences from people who made similar moves  
✅ **Comprehensive Recommendations** - Synthesizes all data into actionable advice  

## Requirements

- Python 3.11+
- Virtual environment (recommended)
- Dependencies: `pip install -r requirements.txt`
- API Keys: OpenAI, Firecrawl, Brave Search (see Configuration section)

## Quick Start

### CLI Mode (Interactive)

#### 1. Setup Environment

```bash
# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: source .venv/Scripts/activate

# Install dependencies
pip install -r requirements.txt
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

```bash
python agno_coordinator.py
```

**The app will:**
1. Ask about your current and desired cities
2. Gather your financial situation and preferences
3. Analyze cost of living, city culture, and Reddit discussions
4. Provide a comprehensive recommendation

### API Mode (FastAPI Server)

For integration with web apps or other services, run the FastAPI server:

#### 1. Start the Server

```bash
python api.py
```

Or using uvicorn:
```bash
uvicorn api:app --reload --port 8000
```

#### 2. Test the API

Visit http://localhost:8000/docs for interactive API documentation.

Submit an analysis request:
```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "current_city": "New York City",
    "desired_city": "Austin",
    "annual_income": 85000,
    "monthly_expenses": 3500,
    "city_preferences": ["good weather", "tech industry"],
    "current_city_likes": ["public transit"],
    "current_city_dislikes": ["high cost"]
  }'
```

Check analysis status:
```bash
curl "http://localhost:8000/analysis/{analysis_id}"
```

#### 3. Deploy to Railway

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

**Quick deploy:**
1. Push code to GitHub
2. Connect Railway to your repository
3. Add environment variables in Railway dashboard
4. Deploy automatically

## Project Structure

```
should-i-move/
├── agno_coordinator.py               # Main CLI Application
├── api.py                            # FastAPI Server
├── test_api.py                       # API Test Script
├── sub_agents/                       # Specialized Agents
│   ├── cost_analyst/                 # Cost of living analysis
│   │   ├── agent.py
│   │   └── tools.py
│   ├── sentiment_analyst/            # City vibe analysis
│   │   └── agent.py
│   ├── migration_researcher/         # Reddit migration stories
│   │   ├── agent.py
│   │   └── tools.py
│   └── schemas.py                    # Shared data models
├── .env                              # API keys (create this)
├── .env.example                      # Environment template
├── requirements.txt                  # Dependencies
├── railway.toml                      # Railway deployment config
├── README.md                         # This file
├── API_GUIDE.md                      # API usage guide
├── DEPLOYMENT.md                     # Deployment instructions
├── data/                             # NerdWallet city database
│   ├── nerd-wallet-data-generator/   # Scripts to generate city data
│   │   ├── create_city_database.py
│   │   └── ...
│   └── nerdwallet_cities_comprehensive.json
└── reports/                          # Generated analysis reports
    └── README.md
```

## How It Works

### Coordination Mode (`agno_coordinator.py`)
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

### Agent Architecture

The system uses a **Team of Specialized Agents**:

1. **Cost Analyst** 💰
   - Fetches real cost data from NerdWallet
   - Compares housing, food, transportation, taxes
   - Provides financial impact summary

2. **Sentiment Analyst** 🎭
   - Analyzes city vibe and culture
   - Assesses livability based on user preferences
   - Identifies pros and cons

3. **Migration Researcher** 🔍
   - Searches Reddit for real migration stories
   - Extracts common reasons, challenges, outcomes
   - Highlights what Redditors are saying

4. **Team Coordinator** 🎯
   - Synthesizes independent analyses
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
You can test the migration researcher's tool directly:
```bash
# Create a test script or run in python shell
python -c "from sub_agents.migration_researcher.tools import search_reddit_discussions; print(search_reddit_discussions('Seattle', 'New York'))"
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
- Run: `python data/nerd-wallet-data-generator/validate_cities.py`
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
python data/nerd-wallet-data-generator/create_city_database.py
```

### Adding New Tools
Custom tools can be added to agents in their respective `tools.py` files.

## License

MIT

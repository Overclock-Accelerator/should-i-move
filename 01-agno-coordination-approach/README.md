# 01 - Agno Coordination Pattern

## Overview

This is the **foundational multi-agent pattern** that demonstrates sequential task coordination. A team leader delegates tasks to specialized agents one by one, gathers their reports, and synthesizes a comprehensive recommendation.

This is the most straightforward multi-agent pattern - think of it like a manager who delegates tasks to team members sequentially and compiles their individual reports.

## Key Characteristics

- **Sequential Delegation**: Leader delegates to one agent at a time
- **Independent Work**: Each agent works without knowledge of other agents' results
- **Centralized Synthesis**: Team leader combines all reports at the end
- **No Inter-Agent Discussion**: Agents don't debate or influence each other

## Architecture

```
┌─────────────────────────────────────────────────────┐
│              Team Leader (Coordinator)               │
│  - Validates user has provided all info             │
│  - Delegates tasks sequentially                     │
│  - Synthesizes final recommendation                 │
│  - Generates comprehensive report                   │
└─────────────────────────────────────────────────────┘
                          │
                          │ Sequential delegation
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Cost Analyst │  │  Sentiment   │  │  Migration   │
│              │  │   Analyst    │  │  Researcher  │
│ ✓ Real data  │  │ ✓ General    │  │ ✓ Reddit via │
│   NerdWallet │  │   knowledge  │  │   Brave API  │
└──────────────┘  └──────────────┘  └──────────────┘
        │                 │                 │
        └─────────────────┼─────────────────┘
                          │
                          ▼
              Individual Reports Generated
                          │
                          ▼
            Team Leader Synthesizes Results
                          │
                          ▼
              Final Recommendation + Report
```

## Specialized Agents

### 1. **Cost Analyst**
- **Role**: Analyzes cost of living differences
- **Data Source**: Real-time scraping from NerdWallet Cost of Living Calculator
- **Tool**: `get_cost_of_living_comparison()` - Uses Firecrawl to scrape actual data
- **Output**: `CostAnalysis` (housing, transportation, food, taxes, key insights)
- **Features**:
  - City database matching (200+ US cities)
  - Fuzzy matching for city names (handles "NYC" → "New York (Manhattan), NY")
  - URL formatting for NerdWallet comparisons
  - Real percentage differences and dollar amounts

### 2. **Sentiment Analyst**
- **Role**: Researches city vibe, culture, and livability
- **Data Source**: General knowledge about cities
- **Output**: `SentimentAnalysis` (vibe, livability score, pros/cons)
- **Considers**: User's stated preferences and values

### 3. **Migration Researcher**
- **Role**: Finds real-world experiences from people who made similar moves
- **Data Source**: Reddit discussions via Brave Search API
- **Tool**: `search_reddit_discussions()` - Custom integration
- **Output**: `MigrationInsights` (common reasons, challenges, outcomes, warnings)
- **Features**:
  - Multiple query variations for comprehensive search
  - Real Reddit thread analysis
  - Direct quotes and themes from Redditors

## Real Data Integration

### ✅ Implemented: NerdWallet Cost Data
```python
# Automatically fetches and parses real cost comparison
get_cost_of_living_comparison(current_city="Austin", desired_city="Seattle")

# Output includes:
# - Overall cost difference percentage
# - Housing costs (rent, utilities)
# - Transportation costs (transit, gas, car ownership)
# - Food and grocery costs
# - Entertainment costs
# - Healthcare costs
# - Tax implications
```

Console output shows the scraping process:
```
🔍 [COST TOOL] Fetching real cost of living data...
   Current City: Austin
   ├─ Matched to: Austin, TX
   └─ URL format: austin-tx
   Desired City: Seattle
   ├─ Matched to: Seattle, WA
   └─ URL format: seattle-wa
   URL: https://www.nerdwallet.com/cost-of-living-calculator/compare/austin-tx-vs-seattle-wa
   ⏳ Scraping data with Firecrawl...

✅ [COST TOOL] Successfully retrieved cost of living data!
```

### ✅ Implemented: Reddit Search via Brave
```python
# Searches Reddit for migration experiences
search_reddit_discussions(current_city="Austin", desired_city="Seattle")

# Automatically tries multiple query patterns:
# - "moving from Austin to Seattle reddit"
# - "relocated Austin to Seattle experience"
# - "moved from Austin to Seattle"
```

Returns formatted results with:
- Thread titles
- Subreddits
- Descriptions/snippets
- Direct URLs

## Information Gathering Flow

The application uses a conversational agent to gather comprehensive user information:

1. **Initial Freeform Input**: User describes their situation naturally
2. **Intelligent Follow-up**: Agent asks targeted questions for missing info
3. **Priority Order**:
   - Specific city names (handles boroughs, metro areas)
   - Financial information (income + expenses)
   - Preferences and current city opinions
4. **Validation**: Ensures cities are specific before proceeding

### Example Interaction
```
Tell me about your move consideration: I'm thinking about moving from New York to Miami

▰▰▰▱▱▱▱ Analyzing your response...

Great! Let me ask you a few questions to understand your situation better.

When you say New York, do you mean New York City? If so, which borough (Manhattan, Brooklyn, etc.)?

You: Manhattan

Can you share your household income and typical monthly expenses?

You: I make about $120k/year and spend around $4,500/month

What do you value most in a city, and what do you like/dislike about where you live now?

You: I value good weather and outdoor activities. I love the culture here but hate the cold winters and high taxes.

▰▰▰▰▰▰▰ Finalizing your profile...
```

## Pydantic Data Models

The application uses strongly-typed Pydantic models for all data:

### Core Models
- **`UserProfile`**: Financial info, preferences, city opinions
- **`CostAnalysis`**: Structured cost comparison data
- **`SentimentAnalysis`**: City vibe and livability metrics
- **`MigrationInsights`**: Real migration experiences
- **`FinalRecommendation`**: Comprehensive decision with justification

All agents use `output_schema` to ensure consistent, structured responses.

## Usage

### Prerequisites

1. **Python Environment**:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. **Install Dependencies**:
```bash
pip install agno openai python-dotenv firecrawl-py pydantic
```

3. **Environment Variables** (`.env` file):
```bash
OPENAI_API_KEY=your_openai_key_here
FIRECRAWL_API_KEY=your_firecrawl_key_here
BRAVE_API_KEY=your_brave_search_key_here
```

### Setup: City Database (First Time)

Generate the city database for accurate URL matching:

```bash
cd nerdwallet-tools
python create_city_database.py
cd ..
```

This creates `data/nerdwallet_cities_comprehensive.json` with 200+ US cities.

### Run the Application

```bash
# Normal mode
python 01-agno-coordination.py

# Debug mode (shows detailed agent communication)
python 01-agno-coordination.py --debug
```

Press `Ctrl+C` to exit at any time.

### Test Components

Test the cost scraper independently:
```bash
cd nerdwallet-tools
python test_cost_scraper.py
cd ..
```

Test city matching:
```bash
cd nerdwallet-tools
python city_matcher.py
cd ..
```

## Generated Report

The system automatically saves a comprehensive markdown report to the `reports/` folder:

### Filename Format
```
{current_city}_to_{desired_city}_{timestamp}_analysis.md
```

Example: `new_york_city_to_miami_20251106_143022_analysis.md`

### Report Structure
```markdown
# Should You Move from [Current] to [Desired]?

## Report Generated
- Date: [timestamp]
- Analysis Type: Comprehensive Multi-Agent Analysis (Coordination Pattern)

## Executive Summary
[High-level recommendation with confidence level]

## Financial Analysis
[Cost Analyst's detailed breakdown with real NerdWallet data]

## Lifestyle & Culture Analysis
[Sentiment Analyst's assessment of city vibe and livability]

## Migration Insights
[Migration Researcher's findings from Reddit discussions]

## Final Recommendation
[Detailed justification synthesizing all inputs]

## Key Supporting Factors
- [Bulleted list of reasons to move]

## Key Concerns
- [Bulleted list of potential risks]

## Next Steps
- [Actionable recommendations]

## Report Metadata
- Analysis Pattern: Coordination (Sequential Multi-Agent)
- Specialists Consulted: Cost Analyst, Sentiment Analyst, Migration Researcher
```

## Key Features

### 1. **Animated UI**
- Loading animations during processing
- Clear visual feedback for each step
- Colorful ASCII art banner
- Emoji indicators for tool usage

### 2. **Intelligent City Matching**
- Handles aliases (NYC → New York City)
- Borough-specific matching (Manhattan, Brooklyn, etc.)
- Fuzzy matching for typos
- Fallback to basic formatting if city not in database

### 3. **Comprehensive Validation**
- Ensures all required info before proceeding
- Asks targeted follow-up questions
- Validates city specificity
- Checks for financial context

### 4. **Real-Time Tool Logging**
```
🔍 [COST TOOL] Fetching real cost of living data...
✅ [COST TOOL] Successfully retrieved cost of living data!
```

### 5. **Graceful Error Handling**
- Falls back to general knowledge if tools fail
- Notes tool failures in analysis
- Continues with available data

## When to Use Coordination Pattern

**Use Coordination Mode when:**
- Tasks are independent and don't require discussion
- You want clear, separate analyses from each expert
- Sequential processing is acceptable
- Synthesis happens at the end without debate
- Transparency into individual agent work is valuable

**Consider Cooperation Mode when:**
- Decision requires balancing conflicting perspectives
- User has a clear priority that should influence all analyses
- Debate between agents would add value
- Consensus-building is important

## Technical Implementation

### Key Code Pattern

```python
# Sequential coordination team
move_decision_team = Team(
    name="City Move Decision Team",
    model=OpenAIChat("gpt-4o-mini"),
    members=[cost_analyst, sentiment_analyst, migration_researcher],
    delegate_task_to_all_members=False,  # ← COORDINATION MODE (default)
    show_members_responses=True,          # ← Show individual work
    add_member_tools_to_context=False,    # ← Isolate agent tools
    output_schema=FinalRecommendation,
    # ... instructions for delegation flow
)
```

### Team Leader Instructions (Simplified)

```python
instructions=[
    "Step 1 - Validate user has ALL required information (cities, financials, preferences)",
    "Step 2 - Delegate sequentially: Cost → Sentiment → Migration",
    "Step 3 - Synthesize all reports into final recommendation",
    "Step 4 - Save comprehensive markdown report to reports/ folder",
]
```

## Dependencies

**Core:**
- `agno` - Multi-agent orchestration framework
- `pydantic` - Data validation and type safety
- `python-dotenv` - Environment variable management

**AI Services:**
- `openai` - GPT models via OpenAI API

**Data Tools:**
- `firecrawl-py` - Web scraping for NerdWallet data
- Custom `brave_tools` - Reddit search integration

**Utilities:**
- `difflib` - Fuzzy city name matching
- `json` - City database management
- `threading` - Animated UI

## Project Files

**Main Script:** `01-agno-coordination.py`

**Supporting Tools:**
- `brave_tools/brave_search_tool.py` - Reddit search
- `nerdwallet-tools/create_city_database.py` - City database generator
- `nerdwallet-tools/city_matcher.py` - Test city matching
- `nerdwallet-tools/test_cost_scraper.py` - Test NerdWallet scraping

**Data:**
- `data/nerdwallet_cities_comprehensive.json` - City database (200+ cities)

**Reports:**
- `reports/` - Auto-generated analysis reports

## Future Enhancements

### Potential Improvements
- ✅ ~~Real-time cost data~~ (COMPLETED)
- ✅ ~~Reddit migration stories~~ (COMPLETED)
- 🔄 Sentiment analysis from actual reviews/articles
- 🔄 Job market data integration (LinkedIn, Indeed)
- 🔄 School ratings and education data
- 🔄 Crime statistics and safety metrics
- 🔄 Weather and climate data
- 🔄 Interactive report format (HTML/dashboard)

## Comparison with Other Patterns

| Feature | Coordination (01) | Router (02) | Cooperation (03) |
|---------|------------------|-------------|------------------|
| **Delegation** | Sequential | Single routing | Simultaneous |
| **Agent Interaction** | None | None | Discussion/debate |
| **Best For** | Independent tasks | Task classification | Conflicting views |
| **Processing** | Linear | Selective | Parallel |
| **Synthesis** | End-stage | N/A (single agent) | Consensus |

---

**Related Files:**
- `01-agno-coordination.py` - This coordination implementation
- `02-agno-router.py` - Router pattern (single-agent selection)
- `03-agno-cooperation.py` - Cooperation pattern (debate/consensus)
- `04-agno-agentos.py` - AgentOS pattern (workflow automation)

**Documentation:**
- `COMPARISON.md` - Detailed pattern comparison
- `README.md` - Project overview
- `agentos-reference/` - AgentOS documentation


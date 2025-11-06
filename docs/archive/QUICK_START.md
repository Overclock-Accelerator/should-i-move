# Quick Start Guide - Should I Move?

## Current Status ✅

Your "Should I Move?" app now uses **Brave Search** to find Reddit discussions about city relocations. This avoids all the Reddit API authentication issues!

## What You Need

### Required API Keys (3 total)

1. **OpenAI API** - For the AI agents
2. **Firecrawl API** - For cost of living data from NerdWallet
3. **Brave Search API** - For Reddit migration research

## Setup (5 minutes)

### 1. Get Brave API Key

- Go to: https://brave.com/search/api/
- Sign up (free tier: 2,000 searches/month)
- Copy your API key

### 2. Update .env File

Your `.env` file should have:

```bash
OPENAI_API_KEY=sk-proj-xxxxx
FIRECRAWL_API_KEY=fc-xxxxx
BRAVE_API_KEY=BSxxxxxxxxxxxxxx
```

**Note:** You NO LONGER need Reddit API credentials!

### 3. Install Package

```bash
pip install brave-search tenacity
```

### 4. Test It

```bash
python test_brave_integration.py
```

Expected output:
```
🎉 All tests passed! Brave Search integration is working!
```

### 5. Run Your App

```bash
python 02-agno-coordination.py
```

## How It Works Now

### Migration Researcher Agent

**Old way (Reddit API):**
- Required Reddit app creation
- OAuth authentication
- 401 errors from wrong app type
- Complex setup

**New way (Brave Search):**
- Searches: `site:reddit.com should I move from Seattle to New York`
- Gets Reddit post titles, snippets, and URLs
- Extracts insights from search results
- Much simpler and more reliable!

### Example Flow

1. User: "Should I move from Seattle to New York?"

2. **Cost Analyst** fetches NerdWallet data
   - Shows exact cost comparisons
   - Housing, food, transportation, etc.

3. **Sentiment Analyst** analyzes NYC vibe
   - Culture, livability, preferences match

4. **Migration Researcher** (NEW!)
   - Searches: `site:reddit.com moved from Seattle to New York`
   - Finds: 8+ Reddit discussions
   - Extracts: What Redditors are saying
   - Summarizes: Common experiences, warnings, outcomes

5. **Team Coordinator** synthesizes all insights
   - Final recommendation
   - Confidence level
   - Next steps

## Testing Your Setup

### Quick Test (30 seconds)
```bash
python test_brave_integration.py
```

### Full Diagnostic
```bash
python debug_brave_search.py
```

### Run the App
```bash
python 02-agno-coordination.py
```

## Expected Output from Migration Researcher

```json
{
  "number_of_sources": 8,
  "reddit_insights_included": true,
  "redditor_perspectives": "Based on 8 Reddit discussions found via Brave Search, Redditors who moved from Seattle to New York commonly mention: 1) The significant cost increase is real, especially housing (averaging $1000+/month more); 2) Missing Seattle's outdoor access and milder weather; 3) NYC's transit system is a major plus - no car needed; 4) Smaller living spaces (400-600 sq ft typical) take adjustment; 5) Career opportunities and networking in NYC often offset higher costs; 6) Social life is easier to build quickly; 7) Winter is colder and summers more humid than expected.",
  "common_reasons_for_moving": [
    "Career advancement in tech/finance/media",
    "Desire for faster pace and cultural amenities",
    "Better public transit and walkability"
  ],
  "common_challenges": [
    "Housing search complexity and broker fees",
    "Much higher cost of living",
    "Smaller living spaces",
    "Weather adjustment"
  ],
  "common_positive_outcomes": [
    "Career growth and networking",
    "Cultural variety and food scene",
    "No car needed",
    "Easier to meet people"
  ],
  "regrets_or_warnings": [
    "Don't rush the apartment search",
    "Budget more than you think for move-in costs",
    "Winter gear is essential"
  ]
}
```

## Files Created

### Setup & Testing
- `BRAVE_SEARCH_SETUP.md` - Detailed Brave API setup
- `debug_brave_search.py` - Diagnostic tool
- `test_brave_integration.py` - Quick integration test

### Documentation
- `MIGRATION_RESEARCHER_UPDATE.md` - Technical details of the update
- `QUICK_START.md` - This file
- `REDDIT_SETUP.md` - Old Reddit setup (no longer needed)

### Debug Files (from Reddit attempt)
- `debug_reddit_tools.py` - Old Reddit diagnostic
- `quick_fix_reddit.md` - Old Reddit fixes

You can delete the old Reddit files if you want!

## Troubleshooting

### "brave-search not installed"
```bash
pip install brave-search tenacity
```

### "BRAVE_API_KEY not set"
- Check your `.env` file
- Make sure it's in the project root
- No quotes around the value

### "Invalid API key"
- Get a new key from https://brave.com/search/api/
- Copy the full key
- Update `.env` file

### "Rate limit exceeded"
- Free tier: 2,000 queries/month
- Each analysis uses ~3-5 queries
- Wait until next month or upgrade

## Success Indicators

When everything is working, you'll see:

1. ✅ Cost Analyst fetches NerdWallet data
2. ✅ Sentiment Analyst provides city vibe analysis
3. ✅ Migration Researcher shows:
   - `reddit_insights_included: true`
   - `number_of_sources: 5-10`
   - Detailed `redditor_perspectives` summary
4. ✅ Final recommendation with all insights

## Getting Help

Run diagnostics:
```bash
python debug_brave_search.py
```

This will tell you exactly what's wrong:
- ✅ or ❌ for each component
- Specific error messages
- Step-by-step fixes

## Ready to Go!

1. Add `BRAVE_API_KEY` to `.env`
2. Run `python test_brave_integration.py`
3. See success message
4. Run `python 02-agno-coordination.py`
5. Get comprehensive city relocation recommendations! 🎉

---

**Note:** The old Reddit API approach is no longer needed. Brave Search provides better results with simpler setup!


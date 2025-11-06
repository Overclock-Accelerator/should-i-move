# Brave Search API Setup Guide

## Overview
The Migration Researcher now uses Brave Search API to find Reddit discussions about city relocations. This approach searches Reddit via `site:reddit.com` queries, avoiding Reddit API authentication issues.

## Setup Steps

### Step 1: Get a Brave Search API Key

1. Go to https://brave.com/search/api/
2. Click **"Get Started"** or **"Sign Up"**
3. Create an account or sign in
4. Choose a plan:
   - **Free Tier**: 2,000 queries per month (plenty for this app)
   - **Paid Tiers**: Higher limits if needed
5. After signing up, go to your dashboard
6. Copy your **API Key**

### Step 2: Add API Key to .env File

Add this line to your `.env` file:

```bash
# Brave Search API Key (for migration research via Reddit)
BRAVE_API_KEY=your_brave_api_key_here

# Your existing credentials
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
FIRECRAWL_API_KEY=fc-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Step 3: Install Required Package

```bash
pip install brave-search
```

### Step 4: Test Your Setup

Run the debug script:

```bash
python debug_brave_search.py
```

This will verify:
1. ✅ Environment variable is set
2. ✅ brave-search library is installed
3. ✅ API key is valid
4. ✅ Can search Reddit via Brave
5. ✅ Agno BraveSearchTools works

### Step 5: Run Your App

```bash
python 02-agno-coordination.py
```

## How It Works

The Migration Researcher agent will:

1. **Search Reddit via Brave Search** using queries like:
   - `site:reddit.com should I move from Seattle to New York`
   - `site:reddit.com moved from Seattle to New York`
   - `site:reddit.com Seattle to New York relocation`

2. **Extract insights** from the search results (titles, snippets, URLs)

3. **Summarize** what Redditors are saying in the `redditor_perspectives` field

4. **Signal** that Reddit data was used via `reddit_insights_included: true`

## Benefits Over Direct Reddit API

✅ **No authentication issues** - Just need a Brave API key
✅ **Better search** - Brave's search is often more comprehensive than Reddit's
✅ **Easier setup** - One API key vs. Reddit app creation
✅ **More reliable** - No OAuth complications
✅ **Same insights** - Still getting real Reddit discussions

## API Limits

- **Free Tier**: 2,000 queries/month
- **Usage per analysis**: ~3-5 searches per city pair
- **Estimates**: Can analyze ~400-600 city pairs per month on free tier

## Troubleshooting

### "brave-search library not installed"
```bash
pip install brave-search
```

### "BRAVE_API_KEY not set"
- Check your `.env` file exists in project root
- Ensure the key is on a line like: `BRAVE_API_KEY=BSxxxxxxxxxx`
- No quotes needed around the value
- Restart your terminal/IDE after editing

### "Invalid API key"
- Verify you copied the full API key from Brave dashboard
- Check for extra spaces or characters
- Make sure your Brave account is active

### "Rate limit exceeded"
- Free tier: 2,000 queries/month
- Wait until next month or upgrade your plan
- The app only uses 3-5 searches per analysis

## Example Output

When working correctly, the Migration Researcher will output:

```json
{
  "number_of_sources": 8,
  "reddit_insights_included": true,
  "redditor_perspectives": "Based on 8 Reddit discussions found via Brave Search, Redditors who moved from Seattle to New York commonly mention: 1) The significant cost increase is real but career opportunities offset it, 2) Missing Seattle's outdoor access and milder weather...",
  "common_reasons_for_moving": [...],
  ...
}
```

## Getting Your API Key

Direct link: https://api.search.brave.com/register

1. Sign up for free account
2. Verify email
3. Go to dashboard
4. Copy API key
5. Add to `.env` file
6. Done! 🎉

## Complete .env File Example

Your `.env` file should look like this:

```bash
# OpenAI API Key (required)
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Firecrawl API Key (required for cost analysis)
FIRECRAWL_API_KEY=fc-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Brave Search API Key (required for migration research)
BRAVE_API_KEY=BSxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Note:** You NO LONGER need Reddit API credentials (REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT)


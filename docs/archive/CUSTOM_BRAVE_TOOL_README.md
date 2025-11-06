# Custom Brave Search Tool - No Dependency Issues! 🎉

## Problem Solved

The `brave-search` package has dependency issues on Windows (requires compiling numpy from source, needs C compiler). 

**Solution:** Created a custom tool that uses the Brave Search API directly via simple HTTP requests. No problematic dependencies!

## What Was Created

### 1. `brave_search_tool.py`
A lightweight custom tool that:
- ✅ Uses Brave Search API directly (just `requests` library)
- ✅ Searches Reddit with multiple query variations
- ✅ Returns formatted results for the agent
- ✅ Works in your `.venv` without issues
- ✅ No numpy, no compilation, no problems!

### 2. Updated `02-agno-coordination.py`
- Imports the custom `search_reddit_discussions` function
- Migration Researcher agent now uses this custom tool
- Same output schema, same functionality
- Just cleaner and more reliable!

### 3. Updated `test_brave_integration.py`
- Tests the custom tool directly
- Tests it with an Agno agent
- Verifies everything works in your environment

## How It Works

### The Custom Tool

```python
from brave_search_tool import search_reddit_discussions

# Call it with city names
result = search_reddit_discussions(
    current_city="Seattle",
    desired_city="New York",
    max_results=10
)
```

### What It Does

1. **Searches Reddit via Brave** with multiple query variations:
   - `site:reddit.com should I move from Seattle to New York`
   - `site:reddit.com moved from Seattle to New York`
   - `site:reddit.com Seattle to New York relocation`
   - `site:reddit.com New York vs Seattle`

2. **Collects results** - titles, URLs, descriptions

3. **Deduplicates** - removes duplicate URLs

4. **Formats** for the agent with:
   - Number of discussions found
   - List of results with titles and previews
   - Instructions for analysis

### API Usage

The tool uses the Brave Search API directly:
```python
GET https://api.search.brave.com/res/v1/web/search
Headers:
  X-Subscription-Token: YOUR_BRAVE_API_KEY
Params:
  q: site:reddit.com should I move from X to Y
  count: 10
```

## Setup (Super Simple!)

### 1. Ensure BRAVE_API_KEY is in .env

```bash
BRAVE_API_KEY=BSxxxxxxxxxxxxxxxxxx
```

### 2. That's it!

No `pip install brave-search` needed!  
The custom tool only uses `requests` (already installed).

## Testing

### Quick Test
```bash
python test_brave_integration.py
```

Expected output:
```
🎉 All tests passed! Custom Brave Search integration is working!
✅ No dependency issues!
✅ Works in your .venv environment!
```

### Direct Tool Test
```bash
python brave_search_tool.py
```

This will search for "Seattle to New York" discussions and show you the results.

## Usage in Your App

Just run your app normally:
```bash
python 02-agno-coordination.py
```

The Migration Researcher will:
1. Call `search_reddit_discussions(current_city, desired_city)`
2. Receive formatted Reddit discussion results
3. Analyze what Redditors are saying
4. Populate the output with insights

## Example Output

When working correctly, you'll see console output like:

```
🔍 [REDDIT SEARCH] Searching for Reddit discussions about moving from Seattle to New York...
   📡 Query: site:reddit.com should I move from Seattle to New York
   ✅ Found 10 results
   📡 Query: site:reddit.com moved from Seattle to New York
   ✅ Found 8 results

✅ [REDDIT SEARCH] Collected 15 unique Reddit discussions
```

And the agent will output:

```json
{
  "number_of_sources": 15,
  "reddit_insights_included": true,
  "redditor_perspectives": "Based on 15 Reddit discussions, Redditors who moved from Seattle to NYC commonly mention: 1) The cost increase is significant but career opportunities offset it; 2) Missing Seattle's outdoor access; 3) NYC's transit is superior; 4) Smaller apartments take adjustment; 5) Social life is easier to build in NYC...",
  ...
}
```

## Benefits Over Package-Based Approach

| Aspect | brave-search package | Custom Tool |
|--------|---------------------|-------------|
| **Dependencies** | numpy, httpx, tenacity, pytest-asyncio | just `requests` |
| **Installation** | Fails on Windows (needs compiler) | Works everywhere |
| **Complexity** | Heavy package | Simple HTTP calls |
| **Reliability** | Version conflicts | Just works |
| **Maintenance** | Depends on package updates | Full control |
| **Setup Time** | 15+ minutes (if it works) | 0 minutes |

## Files Created/Modified

### New Files
- `brave_search_tool.py` - Custom search tool
- `CUSTOM_BRAVE_TOOL_README.md` - This file

### Modified Files
- `02-agno-coordination.py` - Uses custom tool instead of BraveSearchTools
- `test_brave_integration.py` - Tests custom tool

### Old Files (No Longer Needed)
You can delete these if you want:
- `debug_reddit_tools.py` - Old Reddit diagnostic
- `quick_fix_reddit.md` - Old Reddit fixes
- `REDDIT_SETUP.md` - Reddit setup (no longer needed)

## Troubleshooting

### "BRAVE_API_KEY not set"
- Add it to your `.env` file
- No quotes around the value
- Restart terminal/IDE after editing

### "Invalid API key" (HTTP 401)
- Get new key from https://brave.com/search/api/
- Update `.env` file

### "Rate limit exceeded" (HTTP 429)
- Free tier: 2,000 queries/month
- Each city pair uses ~4 queries
- Wait until next month or upgrade plan

### No results found
- Some city pairs may not have Reddit discussions
- Agent will fall back to general knowledge
- `reddit_insights_included` will be False

## Code Structure

### brave_search_tool.py

```python
def search_reddit_discussions(
    current_city: str,
    desired_city: str,
    max_results: int = 10
) -> str:
    # 1. Get BRAVE_API_KEY from environment
    # 2. Build search queries
    # 3. Call Brave Search API for each query
    # 4. Collect and deduplicate results
    # 5. Format for agent consumption
    # 6. Return formatted string
```

### Integration

```python
# In 02-agno-coordination.py

from brave_search_tool import search_reddit_discussions

migration_researcher = Agent(
    tools=[search_reddit_discussions],
    instructions=[
        "Use search_reddit_discussions function",
        "Analyze the results",
        "Populate output schema"
    ],
    output_schema=MigrationInsights
)
```

## Success Indicators

✅ `test_brave_integration.py` passes all tests  
✅ Console shows "Collected X unique Reddit discussions"  
✅ Agent output has `reddit_insights_included: true`  
✅ `redditor_perspectives` field is populated  
✅ No import errors, no dependency issues  

## Next Steps

1. Run test: `python test_brave_integration.py`
2. If passes: Run app: `python 02-agno-coordination.py`
3. Enjoy Reddit insights without dependency headaches! 🎉

---

**Note:** This custom tool is simpler, more reliable, and more maintainable than using the `brave-search` package. It's the recommended approach for this project!


# Brave Search Tools

Custom Brave Search integration for finding Reddit discussions about city relocations.

## Why Custom Tool?

The `brave-search` package has dependency issues on Windows (requires numpy compilation, C compiler). This custom tool uses the Brave Search API directly via simple HTTP requests - no problematic dependencies!

## Setup

1. **Get Brave API Key**: https://brave.com/search/api/ (free tier: 2,000 queries/month)

2. **Add to .env**:
   ```bash
   BRAVE_API_KEY=BSxxxxxxxxxxxxxxxxxx
   ```

3. **That's it!** No additional packages needed (uses `requests` library).

## Usage

```python
from brave_tools.brave_search_tool import search_reddit_discussions

# Search for Reddit discussions about a city move
result = search_reddit_discussions(
    current_city="Seattle",
    desired_city="New York",
    max_results=10
)
```

## How It Works

1. **Searches Reddit via Brave** with multiple query variations:
   - `site:reddit.com should I move from [current] to [desired]`
   - `site:reddit.com moved from [current] to [desired]`
   - `site:reddit.com [current] to [desired] relocation`
   - `site:reddit.com [desired] vs [current]`

2. **Collects unique results** (titles, URLs, descriptions)

3. **Returns formatted string** ready for agent analysis

## Testing

```bash
# Run the test suite
python brave_tools/test_brave_integration.py
```

Expected output:
```
🎉 All tests passed! Custom Brave Search integration is working!
✅ No dependency issues!
✅ Works in your .venv environment!
```

## Integration

The tool is used by the Migration Researcher agent in `02-agno-coordination.py`:

```python
from brave_tools.brave_search_tool import search_reddit_discussions

migration_researcher = Agent(
    name="Migration Researcher",
    tools=[search_reddit_discussions],
    # ... agent configuration
)
```

## Files

- `brave_search_tool.py` - Custom Brave Search tool implementation
- `test_brave_integration.py` - Test suite
- `README.md` - This file

## Benefits

✅ Simple HTTP requests (no complex dependencies)  
✅ Works everywhere (Windows, Mac, Linux)  
✅ No compilation required  
✅ Full control over search logic  
✅ Easy to maintain and debug  

## API Limits

- **Free tier**: 2,000 queries/month
- **Per analysis**: ~4 queries (one per query variation)
- **Capacity**: ~500 city pair analyses per month

## Troubleshooting

**"BRAVE_API_KEY not set"**
- Add it to your `.env` file in project root
- Format: `BRAVE_API_KEY=BSxxxxx` (no quotes)

**"HTTP 401 Invalid API key"**
- Get new key from https://brave.com/search/api/
- Verify you copied the full key

**"No results found"**
- Normal for uncommon city pairs
- Agent falls back to general knowledge
- Not an error


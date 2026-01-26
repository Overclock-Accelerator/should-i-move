import os
import time
import requests
from typing import List, Optional
from pydantic import BaseModel, Field


class BraveSearchResult(BaseModel):
    """A single search result from Brave Search"""
    title: str
    url: str
    description: str


def search_reddit_discussions(
    current_city: str,
    desired_city: str,
    max_results: int = 10
) -> str:
    """
    Search Reddit for discussions about moving between two cities using Brave Search API.
    
    Args:
        current_city: The city the user is moving from
        desired_city: The city the user is moving to
        max_results: Maximum number of results to return per query (default: 10)
        
    Returns:
        Formatted string with search results from Reddit discussions
    """
    api_key = os.getenv('BRAVE_API_KEY')
    
    if not api_key:
        return "ERROR: BRAVE_API_KEY not set in environment variables. Please add it to your .env file."
    
    # Search queries to try
    queries = [
        f"site:reddit.com should I move from {current_city} to {desired_city}",
        f"site:reddit.com moved from {current_city} to {desired_city}",
        f"site:reddit.com {current_city} to {desired_city} relocation",
        f"site:reddit.com {desired_city} vs {current_city}",
    ]
    
    all_results = []
    seen_urls = set()
    
    print(f"\n🔍 [REDDIT SEARCH] Searching for Reddit discussions about moving from {current_city} to {desired_city}...")
    
    for query in queries:
        print(f"   📡 Query: {query}")
        
        try:
            # Make request to Brave Search API
            response = requests.get(
                "https://api.search.brave.com/res/v1/web/search",
                params={
                    "q": query,
                    "count": max_results
                },
                headers={
                    "Accept": "application/json",
                    "Accept-Encoding": "gzip",
                    "X-Subscription-Token": api_key
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract web results
                if "web" in data and "results" in data["web"]:
                    results = data["web"]["results"]
                    print(f"   ✅ Found {len(results)} results")
                    
                    for result in results:
                        url = result.get("url", "")
                        
                        # Avoid duplicates
                        if url and url not in seen_urls:
                            seen_urls.add(url)
                            all_results.append({
                                "title": result.get("title", ""),
                                "url": url,
                                "description": result.get("description", "")
                            })
                else:
                    print(f"   ⚠️  No results found")
            
            elif response.status_code == 401:
                return "ERROR: Invalid Brave API key. Please check your BRAVE_API_KEY in .env file."
            elif response.status_code == 429:
                print(f"   ⚠️  Rate limit reached, using results collected so far")
                break
            else:
                print(f"   ⚠️  API returned status {response.status_code}")
        
        except requests.exceptions.Timeout:
            print(f"   ⚠️  Request timed out")
        except Exception as e:
            print(f"   ⚠️  Error: {e}")
        
        # Respect rate limits (1 request per second for free tier)
        time.sleep(1.1)
    
    print(f"\n✅ [REDDIT SEARCH] Collected {len(all_results)} unique Reddit discussions\n")
    
    # Format results for the agent
    if not all_results:
        return f"""
No Reddit discussions found about moving from {current_city} to {desired_city}.

This could mean:
1. This is a less common migration path
2. The search queries didn't match existing discussions
3. There may be API issues

Please provide insights based on general knowledge about these two cities.
"""
    
    formatted_results = f"""
Reddit Search Results: Moving from {current_city} to {desired_city}
Found {len(all_results)} Reddit discussions

"""
    
    for i, result in enumerate(all_results[:20], 1):  # Limit to top 20
        formatted_results += f"""
{i}. {result['title']}
   URL: {result['url']}
   Preview: {result['description'][:200]}...

"""
    
    formatted_results += f"""

INSTRUCTIONS FOR ANALYSIS:
Based on these {len(all_results)} Reddit discussions, extract:
1. What Redditors are saying about this move (for 'redditor_perspectives' field)
2. Specific quotes and their source URLs (for 'featured_quotes' field) - use the 'Preview' text as the quote if relevant
3. Common reasons people gave for moving
4. Common challenges mentioned
5. Common positive outcomes reported
6. Any warnings or regrets shared

Set 'reddit_insights_included' to True since we found Reddit data.
Set 'number_of_sources' to {len(all_results)}.
"""
    
    return formatted_results

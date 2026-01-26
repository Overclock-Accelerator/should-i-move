import json
import re
from typing import Optional
from difflib import get_close_matches
from agno.tools.firecrawl import FirecrawlTools

# Load city database for URL formatting
CITY_DATABASE = {}
try:
    with open("data/nerdwallet_cities_comprehensive.json", "r", encoding="utf-8") as f:
        CITY_DATABASE = json.load(f)
    print(f"✅ Loaded {len(CITY_DATABASE)} cities from database")
except FileNotFoundError:
    print("⚠️  City database not found. Run 'python data/nerd-wallet-data-generator/create_city_database.py' first.")
    print("   Falling back to basic URL formatting.")

def find_best_city_match(city_name: str, cutoff: float = 0.6) -> Optional[dict]:
    """
    Find the best matching city from the database using fuzzy matching.
    
    Args:
        city_name: User's city input
        cutoff: Minimum similarity score (0-1)
    
    Returns:
        Dictionary with city data if found, None otherwise
    """
    if not CITY_DATABASE:
        return None
    
    # Normalize input
    city_name = city_name.strip()
    
    # Try exact match first (case-insensitive)
    for city_key, city_data in CITY_DATABASE.items():
        if city_key.lower() == city_name.lower():
            return city_data
        if city_data['city'].lower() == city_name.lower():
            return city_data
        if city_data.get('display_name', '').lower() == city_name.lower():
            return city_data
    
    # Check if this is an alias
    city_lower = city_name.lower()
    alias_map = {
        "nyc": "New York (Manhattan), NY",
        "new york city": "New York (Manhattan), NY",
        "brooklyn": "New York (Brooklyn), NY",
        "manhattan": "New York (Manhattan), NY",
        "queens": "New York (Queens), NY",
        "bronx": "New York (Bronx), NY",
        "staten island": "New York (Staten Island), NY",
        "la": "Los Angeles, CA",
        "sf": "San Francisco, CA",
        "san fran": "San Francisco, CA",
        "philly": "Philadelphia, PA",
        "vegas": "Las Vegas, NV",
    }
    
    if city_lower in alias_map:
        alias_key = alias_map[city_lower]
        if alias_key in CITY_DATABASE:
            return CITY_DATABASE[alias_key]
    
    # Try fuzzy matching on display names
    display_names = [city_data.get('display_name', key) for key, city_data in CITY_DATABASE.items()]
    matches = get_close_matches(city_name, display_names, n=1, cutoff=cutoff)
    
    if matches:
        # Find the city data for this match
        for city_key, city_data in CITY_DATABASE.items():
            if city_data.get('display_name', city_key) == matches[0]:
                return city_data
    
    return None


def format_city_for_url(city_name: str) -> str:
    """
    Format city name for NerdWallet URL using the city database.
    Falls back to basic formatting if city not found in database.
    
    Args:
        city_name: The city name to format
        
    Returns:
        URL-formatted city string (e.g., "dallas-tx" or "new-york-brooklyn-ny")
    """
    # Try to find city in database
    city_match = find_best_city_match(city_name)
    
    if city_match:
        return city_match['url_format']
    
    # Fallback to basic formatting if not in database
    print(f"   ⚠️  City '{city_name}' not found in database, using basic formatting")
    
    # Remove common state abbreviations and full state names
    city_clean = re.sub(r',?\s*(AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|VA|WA|WV|WI|WY)\s*$', '', city_name, flags=re.IGNORECASE)
    city_clean = re.sub(r',?\s*(Alabama|Alaska|Arizona|Arkansas|California|Colorado|Connecticut|Delaware|Florida|Georgia|Hawaii|Idaho|Illinois|Indiana|Iowa|Kansas|Kentucky|Louisiana|Maine|Maryland|Massachusetts|Michigan|Minnesota|Mississippi|Missouri|Montana|Nebraska|Nevada|New Hampshire|New Jersey|New Mexico|New York|North Carolina|North Dakota|Ohio|Oklahoma|Oregon|Pennsylvania|Rhode Island|South Carolina|South Dakota|Tennessee|Texas|Utah|Vermont|Virginia|Washington|West Virginia|Wisconsin|Wyoming)\s*$', '', city_clean, flags=re.IGNORECASE)
    
    # Convert to lowercase and replace spaces with dashes
    city_formatted = city_clean.strip().lower().replace(' ', '-')
    
    # Remove any special characters except dashes
    city_formatted = re.sub(r'[^a-z0-9-]', '', city_formatted)
    
    return city_formatted


def get_cost_of_living_comparison(current_city: str, desired_city: str) -> str:
    """
    Get cost of living comparison between two cities from NerdWallet.
    
    Args:
        current_city: The user's current city
        desired_city: The city the user is considering moving to
        
    Returns:
        Extracted cost of living data including housing, transportation, food, entertainment, and healthcare
    """
    # Find best matching cities in database
    current_match = find_best_city_match(current_city)
    desired_match = find_best_city_match(desired_city)
    
    # Format cities for URL
    current_formatted = format_city_for_url(current_city)
    desired_formatted = format_city_for_url(desired_city)
    
    # Build NerdWallet URL
    url = f"https://www.nerdwallet.com/cost-of-living-calculator/compare/{current_formatted}-vs-{desired_formatted}"
    
    # Console log
    print(f"\n🔍 [COST TOOL] Fetching real cost of living data...")
    print(f"   Current City: {current_city}")
    if current_match:
        print(f"   ├─ Matched to: {current_match['display_name']}")
    print(f"   └─ URL format: {current_formatted}")
    print(f"   Desired City: {desired_city}")
    if desired_match:
        print(f"   ├─ Matched to: {desired_match['display_name']}")
    print(f"   └─ URL format: {desired_formatted}")
    print(f"   URL: {url}")
    print(f"   ⏳ Scraping data with Firecrawl...\n")
    
    try:
        # Use Firecrawl to scrape the page
        firecrawl = FirecrawlTools()
        result = firecrawl.scrape_website(url)
        
        print(f"✅ [COST TOOL] Successfully retrieved cost of living data!\n")
        
        # Return the scraped content
        return f"""
Cost of Living Comparison Data from NerdWallet:
URL: {url}

{result}

Please extract and analyze the following from the above data:
1. Overall cost of living percentage difference
2. Housing costs comparison
3. Transportation costs comparison
4. Food costs comparison
5. Entertainment costs comparison
6. Healthcare costs comparison (if available)
7. Any other relevant financial metrics

Use these real-world data points in your analysis.
"""
    except Exception as e:
        print(f"⚠️ [COST TOOL] Error fetching data: {e}")
        print(f"   Falling back to general knowledge analysis\n")
        return f"""
Unable to fetch real-time cost of living data from NerdWallet.
URL attempted: {url}
Error: {e}

Please provide analysis based on your general knowledge of {current_city} and {desired_city}.
"""

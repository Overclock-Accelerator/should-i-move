"""
Scrape the list of available cities from NerdWallet's cost of living calculator.
This creates a mapping file that can be used to match user input to valid NerdWallet cities.
"""

import os
import json
import re
from dotenv import load_dotenv
from agno.tools.firecrawl import FirecrawlTools

# Load environment variables
load_dotenv()

def scrape_nerdwallet_cities():
    """
    Scrape the NerdWallet cost of living calculator to get the list of available cities.
    """
    print("="*80)
    print("SCRAPING NERDWALLET CITY LIST")
    print("="*80)
    
    # The main calculator page should have the city dropdown/autocomplete data
    url = "https://www.nerdwallet.com/cost-of-living-calculator"
    
    print(f"\nTarget URL: {url}")
    print(f"🔍 Scraping page...\n")
    
    try:
        firecrawl = FirecrawlTools()
        result = firecrawl.scrape_website(url)
        
        print(f"✅ Page scraped successfully!")
        print(f"   Data length: {len(str(result))} characters\n")
        
        # Save raw HTML for inspection
        with open("../data/nerdwallet_raw_scrape.txt", "w", encoding="utf-8") as f:
            f.write(str(result))
        print(f"✅ Raw scrape saved to: data/nerdwallet_raw_scrape.txt")
        
        # Try to extract city patterns
        # Looking for patterns like "Dallas, TX" or similar city, state combinations
        result_str = str(result)
        
        # Pattern 1: City, ST format (e.g., "Dallas, TX")
        city_state_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z]{2})\b'
        matches = re.findall(city_state_pattern, result_str)
        
        # Deduplicate
        cities = {}
        for city, state in matches:
            # Skip common false positives
            if city in ["By", "In", "The", "For", "All", "New", "Best", "Get", "See", "Read"]:
                continue
            
            city_name = f"{city}, {state}"
            # Format for URL (lowercase, spaces to dashes)
            url_format = f"{city.lower().replace(' ', '-')}-{state.lower()}"
            
            cities[city_name] = {
                "display_name": city_name,
                "url_format": url_format,
                "city": city,
                "state": state,
                "state_abbr": state
            }
        
        print(f"\n📊 Found {len(cities)} unique cities")
        
        if len(cities) > 0:
            # Save to JSON
            with open("../data/nerdwallet_cities.json", "w", encoding="utf-8") as f:
                json.dump(cities, f, indent=2, sort_keys=True)
            
            print(f"✅ City list saved to: data/nerdwallet_cities.json")
            
            # Show sample
            print(f"\n📋 Sample cities (first 20):")
            for i, (key, value) in enumerate(sorted(cities.items())[:20]):
                print(f"   {value['display_name']:30} → {value['url_format']}")
        else:
            print(f"\n⚠️  No cities found using pattern matching.")
            print(f"   The page structure may have changed or require JavaScript rendering.")
            print(f"   Check nerdwallet_raw_scrape.txt to inspect the raw data.")
        
        return cities
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return {}


def try_extract_from_comparison_page():
    """
    Alternative approach: Scrape a comparison page and extract city options from dropdown data.
    """
    print("\n" + "="*80)
    print("ALTERNATIVE: SCRAPING FROM COMPARISON PAGE")
    print("="*80)
    
    # Use a known comparison to get the page with dropdowns
    url = "https://www.nerdwallet.com/cost-of-living-calculator/compare/dallas-tx-vs-san-francisco-ca"
    
    print(f"\nTarget URL: {url}")
    print(f"🔍 Scraping page...\n")
    
    try:
        firecrawl = FirecrawlTools()
        result = firecrawl.scrape_website(url)
        
        print(f"✅ Page scraped successfully!")
        print(f"   Data length: {len(str(result))} characters\n")
        
        # Save raw HTML for inspection
        with open("../data/nerdwallet_comparison_raw.txt", "w", encoding="utf-8") as f:
            f.write(str(result))
        print(f"✅ Raw scrape saved to: data/nerdwallet_comparison_raw.txt")
        
        # Look for city patterns
        result_str = str(result)
        
        # Pattern: Cities in format "City, ST"
        city_state_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z]{2})\b'
        matches = re.findall(city_state_pattern, result_str)
        
        cities = {}
        for city, state in matches:
            # Skip common false positives
            if city in ["By", "In", "The", "For", "All", "New", "Best", "Get", "See", "Read", "How", "What"]:
                continue
            
            city_name = f"{city}, {state}"
            url_format = f"{city.lower().replace(' ', '-')}-{state.lower()}"
            
            cities[city_name] = {
                "display_name": city_name,
                "url_format": url_format,
                "city": city,
                "state": state,
                "state_abbr": state
            }
        
        print(f"\n📊 Found {len(cities)} unique cities from comparison page")
        
        if len(cities) > 0:
            # Show sample
            print(f"\n📋 Sample cities (first 20):")
            for i, (key, value) in enumerate(sorted(cities.items())[:20]):
                print(f"   {value['display_name']:30} → {value['url_format']}")
        
        return cities
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return {}


def main():
    """
    Main execution function.
    """
    print("\n🏙️  NERDWALLET CITY LIST SCRAPER")
    print("="*80)
    print("\nThis script will attempt to extract the list of available cities")
    print("from NerdWallet's cost of living calculator.")
    print("\nNote: Since NerdWallet likely uses JavaScript to load city data,")
    print("we may need to inspect the raw HTML to find embedded JSON data.\n")
    
    # Try main page first
    cities_main = scrape_nerdwallet_cities()
    
    # Try comparison page as alternative
    cities_comparison = try_extract_from_comparison_page()
    
    # Merge results
    all_cities = {**cities_main, **cities_comparison}
    
    if len(all_cities) > 0:
        # Save merged list
        with open("../data/nerdwallet_cities_merged.json", "w", encoding="utf-8") as f:
            json.dump(all_cities, f, indent=2, sort_keys=True)
        
        print("\n" + "="*80)
        print("FINAL RESULTS")
        print("="*80)
        print(f"\n✅ Total unique cities found: {len(all_cities)}")
        print(f"✅ Saved to: data/nerdwallet_cities_merged.json")
        
        # Show statistics by state
        states = {}
        for city_data in all_cities.values():
            state = city_data['state_abbr']
            states[state] = states.get(state, 0) + 1
        
        print(f"\n📊 Cities by state:")
        for state, count in sorted(states.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   {state}: {count} cities")
    else:
        print("\n⚠️  No cities could be extracted automatically.")
        print("\nNext steps:")
        print("1. Check the raw scrape files to see what data was captured")
        print("2. The city data may be loaded via JavaScript/API")
        print("3. We may need to manually create the city list or use a different approach")
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()


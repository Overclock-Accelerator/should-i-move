"""
City matching utility for converting user input to NerdWallet city format.
Uses fuzzy matching to handle variations in city names.
"""

import json
import os
from typing import Optional, Dict, Tuple
from difflib import get_close_matches


class CityMatcher:
    """
    Matches user-provided city names to NerdWallet's city format.
    """
    
    def __init__(self, cities_file: str = "../data/nerdwallet_cities_comprehensive.json"):
        """
        Initialize the city matcher with a JSON file of cities.
        
        Args:
            cities_file: Path to JSON file containing city data
        """
        self.cities = {}
        self.cities_file = cities_file
        
        if os.path.exists(cities_file):
            with open(cities_file, 'r', encoding='utf-8') as f:
                self.cities = json.load(f)
            print(f"✅ Loaded {len(self.cities)} cities from {cities_file}")
        else:
            print(f"⚠️  City list file not found: {cities_file}")
            print(f"   Run 'python scrape_city_list.py' first to generate the city list.")
    
    def find_city(self, user_input: str, cutoff: float = 0.6) -> Optional[Dict]:
        """
        Find the best matching city for user input.
        
        Args:
            user_input: User's city input (e.g., "New York City", "NYC", "New York, NY")
            cutoff: Minimum similarity score (0-1)
        
        Returns:
            Dictionary with city data if found, None otherwise
        """
        if not self.cities:
            return None
        
        # Normalize input
        user_input = user_input.strip()
        
        # Try exact match first (case-insensitive)
        for city_key, city_data in self.cities.items():
            if city_key.lower() == user_input.lower():
                return city_data
            if city_data['city'].lower() == user_input.lower():
                return city_data
            if city_data.get('display_name', '').lower() == user_input.lower():
                return city_data
        
        # Try fuzzy matching on display names
        display_names = [city_data.get('display_name', key) for key, city_data in self.cities.items()]
        matches = get_close_matches(user_input, display_names, n=1, cutoff=cutoff)
        
        if matches:
            # Find the city data for this match
            for city_key, city_data in self.cities.items():
                if city_data.get('display_name', city_key) == matches[0]:
                    return city_data
        
        return None
    
    def format_for_url(self, city_data: Dict) -> str:
        """
        Get the URL-formatted version of a city.
        
        Args:
            city_data: City data dictionary
        
        Returns:
            URL-formatted city string (e.g., "new-york-city-ny")
        """
        return city_data.get('url_format', '')
    
    def search_cities(self, query: str, limit: int = 5) -> list:
        """
        Search for cities matching a query.
        
        Args:
            query: Search query
            limit: Maximum number of results
        
        Returns:
            List of matching city data dictionaries
        """
        if not self.cities:
            return []
        
        query_lower = query.lower()
        results = []
        
        for city_key, city_data in self.cities.items():
            display_name = city_data.get('display_name', city_key)
            if query_lower in display_name.lower():
                results.append(city_data)
                if len(results) >= limit:
                    break
        
        return results


def test_city_matcher():
    """
    Test the city matcher with various inputs.
    """
    print("\n" + "="*80)
    print("TESTING CITY MATCHER")
    print("="*80)
    
    matcher = CityMatcher()
    
    if not matcher.cities:
        print("\n⚠️  No cities loaded. Run 'python scrape_city_list.py' first.")
        return
    
    test_cases = [
        "Dallas",
        "Dallas, TX",
        "San Francisco",
        "New York City",
        "NYC",
        "Los Angeles",
        "Miami",
        "Austin, Texas",
    ]
    
    print(f"\nTesting city matching:")
    print("-"*80)
    
    for test_input in test_cases:
        result = matcher.find_city(test_input)
        if result:
            print(f"✅ '{test_input}' → '{result['display_name']}' → {result['url_format']}")
        else:
            print(f"❌ '{test_input}' → No match found")
    
    # Test search
    print(f"\n\nTesting city search:")
    print("-"*80)
    search_query = "San"
    results = matcher.search_cities(search_query, limit=5)
    print(f"\nSearching for '{search_query}':")
    for result in results:
        print(f"   • {result['display_name']} → {result['url_format']}")
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    test_city_matcher()


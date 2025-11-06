"""
Validate city URLs against NerdWallet to ensure they actually exist.
This script tests URLs and identifies which ones work vs which need correction.
"""

import json
import time
from agno.tools.firecrawl import FirecrawlTools
from dotenv import load_dotenv

load_dotenv()

def test_city_url(city1_url: str, city2_url: str = "dallas-tx") -> tuple:
    """
    Test if a city URL is valid by attempting to scrape a comparison page.
    
    Args:
        city1_url: The city URL format to test
        city2_url: A known working city to compare against (default: dallas-tx)
    
    Returns:
        (is_valid, status_code, error_message)
    """
    url = f"https://www.nerdwallet.com/cost-of-living-calculator/compare/{city1_url}-vs-{city2_url}"
    
    try:
        firecrawl = FirecrawlTools()
        result = firecrawl.scrape_website(url)
        
        # Check if we got actual cost data (not an error page)
        result_str = str(result).lower()
        
        if "housing costs" in result_str or "cost of living" in result_str:
            return (True, 200, None)
        elif "not found" in result_str or "404" in result_str:
            return (False, 404, "City not found")
        else:
            return (False, 0, "Unknown response")
            
    except Exception as e:
        return (False, 0, str(e))


def validate_city_database(cities_file: str = "../data/nerdwallet_cities_comprehensive.json", 
                          sample_size: int = 20,
                          delay: float = 2.0):
    """
    Validate a sample of cities from the database.
    
    Args:
        cities_file: Path to city database JSON
        sample_size: Number of cities to test
        delay: Delay between requests (seconds) to avoid rate limiting
    """
    print("="*80)
    print("CITY DATABASE VALIDATION")
    print("="*80)
    
    # Load cities
    with open(cities_file, 'r', encoding='utf-8') as f:
        cities = json.load(f)
    
    print(f"\n📚 Loaded {len(cities)} cities from database")
    print(f"🧪 Testing sample of {sample_size} cities...")
    print(f"⏱️  Delay between requests: {delay} seconds\n")
    
    # Sample cities to test
    import random
    city_items = list(cities.items())
    random.shuffle(city_items)
    sample = city_items[:sample_size]
    
    results = {
        "valid": [],
        "invalid": [],
        "errors": []
    }
    
    print("Testing cities:")
    print("-"*80)
    
    for i, (city_key, city_data) in enumerate(sample, 1):
        url_format = city_data['url_format']
        display_name = city_data['display_name']
        
        print(f"{i:2d}. Testing: {display_name:30} ({url_format})...", end=" ", flush=True)
        
        is_valid, status, error = test_city_url(url_format)
        
        if is_valid:
            print("✅ VALID")
            results["valid"].append({
                "display_name": display_name,
                "url_format": url_format
            })
        elif status == 404:
            print("❌ NOT FOUND")
            results["invalid"].append({
                "display_name": display_name,
                "url_format": url_format,
                "error": error
            })
        else:
            print(f"⚠️  ERROR: {error}")
            results["errors"].append({
                "display_name": display_name,
                "url_format": url_format,
                "error": error
            })
        
        # Delay to avoid rate limiting
        if i < len(sample):
            time.sleep(delay)
    
    # Print summary
    print("\n" + "="*80)
    print("VALIDATION SUMMARY")
    print("="*80)
    
    total = len(sample)
    valid_count = len(results["valid"])
    invalid_count = len(results["invalid"])
    error_count = len(results["errors"])
    
    print(f"\n✅ Valid:     {valid_count:3d} / {total} ({valid_count/total*100:.1f}%)")
    print(f"❌ Invalid:   {invalid_count:3d} / {total} ({invalid_count/total*100:.1f}%)")
    print(f"⚠️  Errors:    {error_count:3d} / {total} ({error_count/total*100:.1f}%)")
    
    if results["invalid"]:
        print(f"\n🔍 Invalid Cities (need URL format correction):")
        for item in results["invalid"][:10]:
            print(f"   • {item['display_name']:30} → {item['url_format']}")
        if len(results["invalid"]) > 10:
            print(f"   ... and {len(results['invalid']) - 10} more")
    
    # Save results
    with open("../data/validation_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Full results saved to: data/validation_results.json")
    print("="*80 + "\n")
    
    return results


def check_specific_cities():
    """
    Check specific known cities to understand NerdWallet's format.
    """
    print("\n" + "="*80)
    print("CHECKING SPECIFIC KNOWN CITIES")
    print("="*80)
    
    # Test known variations
    test_cases = [
        ("New York City", "new-york-city-ny"),
        ("NYC (Brooklyn)", "new-york-brooklyn-ny"),
        ("NYC (Manhattan)", "new-york-manhattan-ny"),
        ("NYC (Queens)", "new-york-queens-ny"),
        ("San Francisco", "san-francisco-ca"),
        ("Los Angeles", "los-angeles-ca"),
        ("Chicago", "chicago-il"),
    ]
    
    print("\nTesting specific URLs:")
    print("-"*80)
    
    for name, url_format in test_cases:
        print(f"Testing: {name:25} ({url_format})...", end=" ", flush=True)
        is_valid, status, error = test_city_url(url_format)
        
        if is_valid:
            print("✅ WORKS")
        else:
            print(f"❌ FAILS ({status})")
        
        time.sleep(1.5)
    
    print("\n" + "="*80)


def main():
    """
    Main validation function.
    """
    print("\n🔍 NERDWALLET CITY URL VALIDATOR")
    print("="*80)
    print("\nThis script validates city URLs against NerdWallet to ensure they work.")
    print("It will test a sample of cities and identify which ones need correction.\n")
    
    # First check specific known cities
    check_specific_cities()
    
    # Then validate a sample from the database
    print("\n" + "="*80)
    choice = input("Validate the comprehensive database? (y/n): ").strip().lower()
    
    if choice == 'y':
        sample_size = input("How many cities to test? (default 20): ").strip()
        sample_size = int(sample_size) if sample_size else 20
        
        validate_city_database(sample_size=sample_size)
    else:
        print("\nSkipping database validation.\n")
    
    print("💡 TIP: Based on validation results, you may need to:")
    print("   1. Update city URL formats to match NerdWallet's actual identifiers")
    print("   2. Add borough-specific entries for NYC (Brooklyn, Manhattan, Queens, etc.)")
    print("   3. Remove cities that NerdWallet doesn't support")
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()


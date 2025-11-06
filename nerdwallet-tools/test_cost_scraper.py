"""
Standalone test script for the NerdWallet cost of living scraper.
This script tests the scraping functionality independently.
"""

import os
import re
from dotenv import load_dotenv
from agno.tools.firecrawl import FirecrawlTools

# Load environment variables
load_dotenv()

# Check if API key is present
firecrawl_key = os.getenv("FIRECRAWL_API_KEY")
if not firecrawl_key:
    print("❌ ERROR: FIRECRAWL_API_KEY not found in .env file")
    print("   Please add FIRECRAWL_API_KEY to your .env file")
    exit(1)
else:
    print(f"✅ FIRECRAWL_API_KEY found: {firecrawl_key[:8]}...")


def format_city_for_url(city_name: str) -> str:
    """Format city name for NerdWallet URL (lowercase, spaces to dashes, remove state if present)"""
    # Remove common state abbreviations and full state names
    city_clean = re.sub(r',?\s*(AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|VA|WA|WV|WI|WY)\s*$', '', city_name, flags=re.IGNORECASE)
    city_clean = re.sub(r',?\s*(Alabama|Alaska|Arizona|Arkansas|California|Colorado|Connecticut|Delaware|Florida|Georgia|Hawaii|Idaho|Illinois|Indiana|Iowa|Kansas|Kentucky|Louisiana|Maine|Maryland|Massachusetts|Michigan|Minnesota|Mississippi|Missouri|Montana|Nebraska|Nevada|New Hampshire|New Jersey|New Mexico|New York|North Carolina|North Dakota|Ohio|Oklahoma|Oregon|Pennsylvania|Rhode Island|South Carolina|South Dakota|Tennessee|Texas|Utah|Vermont|Virginia|Washington|West Virginia|Wisconsin|Wyoming)\s*$', '', city_clean, flags=re.IGNORECASE)
    
    # Convert to lowercase and replace spaces with dashes
    city_formatted = city_clean.strip().lower().replace(' ', '-')
    
    # Remove any special characters except dashes
    city_formatted = re.sub(r'[^a-z0-9-]', '', city_formatted)
    
    return city_formatted


def test_city_formatting():
    """Test the city name formatting function"""
    print("\n" + "="*80)
    print("TESTING CITY NAME FORMATTING")
    print("="*80)
    
    test_cases = [
        ("New York City", "new-york-city"),
        ("New York City, NY", "new-york-city"),
        ("Fort Worth, Texas", "fort-worth"),
        ("Miami, FL", "miami"),
        ("San Francisco", "san-francisco"),
        ("Los Angeles, California", "los-angeles"),
    ]
    
    all_passed = True
    for input_city, expected_output in test_cases:
        result = format_city_for_url(input_city)
        status = "✅" if result == expected_output else "❌"
        print(f"{status} '{input_city}' → '{result}' (expected: '{expected_output}')")
        if result != expected_output:
            all_passed = False
    
    return all_passed


def test_scraper(current_city: str, desired_city: str):
    """Test the actual scraping functionality"""
    print("\n" + "="*80)
    print("TESTING FIRECRAWL SCRAPER")
    print("="*80)
    
    # Format cities
    current_formatted = format_city_for_url(current_city)
    desired_formatted = format_city_for_url(desired_city)
    
    # Build URL
    url = f"https://www.nerdwallet.com/cost-of-living-calculator/compare/{current_formatted}-vs-{desired_formatted}"
    
    print(f"\nTest Cities:")
    print(f"  Current: {current_city} → {current_formatted}")
    print(f"  Desired: {desired_city} → {desired_formatted}")
    print(f"\nGenerated URL:")
    print(f"  {url}")
    
    print(f"\n🔍 Attempting to scrape...")
    
    try:
        # Initialize Firecrawl
        firecrawl = FirecrawlTools()
        print(f"✅ FirecrawlTools initialized successfully")
        
        # Attempt to scrape
        print(f"⏳ Scraping URL (this may take 10-30 seconds)...")
        result = firecrawl.scrape_website(url)
        
        print(f"✅ Scraping completed!")
        print(f"\n{'='*80}")
        print("SCRAPED DATA")
        print("="*80)
        
        # Show first 2000 characters of result
        if isinstance(result, str):
            print(f"\nData type: string")
            print(f"Length: {len(result)} characters")
            print(f"\nFirst 2000 characters:")
            print("-"*80)
            print(result[:2000])
            if len(result) > 2000:
                print(f"\n... ({len(result) - 2000} more characters)")
        else:
            print(f"\nData type: {type(result)}")
            print(f"\nFull result:")
            print("-"*80)
            print(result)
        
        # Check for key indicators of successful scrape
        print(f"\n{'='*80}")
        print("DATA VALIDATION")
        print("="*80)
        
        result_str = str(result).lower()
        checks = [
            ("Contains 'cost of living'", "cost of living" in result_str),
            ("Contains 'housing'", "housing" in result_str),
            ("Contains 'transportation'", "transportation" in result_str),
            ("Contains percentage or dollar signs", ("%" in result_str or "$" in result_str)),
        ]
        
        for check_name, passed in checks:
            status = "✅" if passed else "❌"
            print(f"{status} {check_name}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR during scraping:")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {e}")
        
        # Print full traceback for debugging
        import traceback
        print(f"\nFull traceback:")
        print("-"*80)
        traceback.print_exc()
        
        return False


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("🧪 NERDWALLET COST SCRAPER TEST SUITE")
    print("="*80)
    
    # Test 1: City formatting
    formatting_passed = test_city_formatting()
    
    # Test 2: Scraping
    print("\n")
    print("Which cities would you like to test?")
    print("Examples: 'New York City' and 'Fort Worth'")
    print("          'San Francisco' and 'Austin'")
    print("          'Miami' and 'Seattle'")
    
    current = input("\nEnter current city (or press Enter for 'New York City'): ").strip()
    if not current:
        current = "New York City"
    
    desired = input("Enter desired city (or press Enter for 'Miami'): ").strip()
    if not desired:
        desired = "Miami"
    
    scraping_passed = test_scraper(current, desired)
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"City Formatting: {'✅ PASSED' if formatting_passed else '❌ FAILED'}")
    print(f"Web Scraping:    {'✅ PASSED' if scraping_passed else '❌ FAILED'}")
    
    if formatting_passed and scraping_passed:
        print("\n🎉 All tests passed! The scraper is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
    
    print("="*80 + "\n")


if __name__ == "__main__":
    main()


"""
Debug script for Brave Search API integration
Tests Brave Search credentials and BraveSearchTools functionality
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80)

def print_step(number, text):
    """Print a step indicator"""
    print(f"\n[{number}] {text}")

def print_success(text):
    """Print success message"""
    print(f"  ✅ {text}")

def print_error(text):
    """Print error message"""
    print(f"  ❌ {text}")

def print_warning(text):
    """Print warning message"""
    print(f"  ⚠️  {text}")

def check_environment_variables():
    """Check if Brave API key is set"""
    print_step(1, "Checking Environment Variables")
    
    api_key = os.getenv('BRAVE_API_KEY')
    
    if api_key:
        # Show partial value for security
        display_value = api_key[:8] + "..." if len(api_key) > 8 else "***"
        print_success(f"BRAVE_API_KEY = {display_value}")
        return True
    else:
        print_error("BRAVE_API_KEY is NOT SET")
        print_warning("Missing environment variable!")
        print("\n  To fix this, set the following in your .env file:")
        print("\n  BRAVE_API_KEY=your-brave-api-key-here")
        print("\n  Get your API key from: https://brave.com/search/api/")
        return False

def test_brave_search_import():
    """Test if brave-search library is installed"""
    print_step(2, "Testing brave-search Library Import")
    
    try:
        import brave
        print_success(f"brave-search library installed")
        return True
    except ImportError as e:
        print_error(f"brave-search library not installed: {e}")
        print_warning("Install with: pip install brave-search")
        return False

def test_brave_api_connection():
    """Test basic Brave Search API connection"""
    print_step(3, "Testing Brave Search API Connection")
    
    try:
        from brave import Brave
        
        api_key = os.getenv('BRAVE_API_KEY')
        brave_client = Brave(api_key=api_key)
        
        # Test with a simple search
        print("  Running test search...")
        search_results = brave_client.search(q="test", count=1)
        
        if search_results and hasattr(search_results, 'web'):
            print_success("Connected to Brave Search API")
            print_success(f"API is working correctly")
            return True
        else:
            print_error("API returned unexpected response")
            return False
            
    except Exception as e:
        error_msg = str(e)
        print_error(f"Failed to connect to Brave Search API: {error_msg}")
        
        if "401" in error_msg or "Unauthorized" in error_msg:
            print_warning("Your API key appears to be invalid")
            print_warning("Get a new key from: https://brave.com/search/api/")
        elif "403" in error_msg or "Forbidden" in error_msg:
            print_warning("Access forbidden - check your API key and account status")
        elif "429" in error_msg or "rate limit" in error_msg.lower():
            print_warning("Rate limit exceeded - wait a bit or upgrade your plan")
        
        return False

def test_reddit_site_search():
    """Test searching Reddit via Brave Search"""
    print_step(4, "Testing Reddit Site Search")
    
    try:
        from brave import Brave
        
        api_key = os.getenv('BRAVE_API_KEY')
        brave_client = Brave(api_key=api_key)
        
        # Test Reddit-specific search
        query = "site:reddit.com should I move to New York"
        print(f"  Searching for: '{query}'")
        
        search_results = brave_client.search(q=query, count=5)
        
        if search_results and hasattr(search_results, 'web') and search_results.web.results:
            results = search_results.web.results
            print_success(f"Found {len(results)} Reddit results")
            
            for i, result in enumerate(results[:3], 1):
                title = result.title[:60] + "..." if len(result.title) > 60 else result.title
                print(f"    {i}. {title}")
                if hasattr(result, 'url'):
                    print(f"       {result.url[:70]}...")
        else:
            print_warning("Search returned no results (but API is working)")
        
        return True
    except Exception as e:
        print_error(f"Reddit search failed: {e}")
        return False

def test_agno_brave_tools():
    """Test Agno's BraveSearchTools"""
    print_step(5, "Testing Agno BraveSearchTools")
    
    try:
        from agno.tools.bravesearch import BraveSearchTools
        
        brave_tools = BraveSearchTools()
        print_success("BraveSearchTools instantiated successfully")
        
        # Check what methods are available
        methods = [m for m in dir(brave_tools) if not m.startswith('_') and callable(getattr(brave_tools, m))]
        print(f"  Available methods: {', '.join(methods[:5])}...")
        
        return True
    except ImportError as e:
        print_error(f"Failed to import BraveSearchTools: {e}")
        print_warning("Make sure agno is installed with: pip install -U agno")
        return False
    except Exception as e:
        print_error(f"Failed to instantiate BraveSearchTools: {e}")
        return False

def test_agno_agent_with_brave():
    """Test Agno Agent with BraveSearchTools"""
    print_step(6, "Testing Agno Agent with BraveSearchTools")
    
    try:
        from agno.agent import Agent
        from agno.models.openai import OpenAIChat
        from agno.tools.bravesearch import BraveSearchTools
        
        # Check OpenAI API key
        if not os.getenv('OPENAI_API_KEY'):
            print_error("OPENAI_API_KEY not set")
            print_warning("Set it in your .env file to test the agent")
            return False
        
        print("  Creating test agent...")
        agent = Agent(
            name="Brave Search Test Agent",
            model=OpenAIChat("gpt-4o-mini"),
            tools=[BraveSearchTools()],
            instructions=[
                "You are a search assistant that helps find Reddit discussions",
                "Always include 'site:reddit.com' in your searches to limit to Reddit"
            ],
            markdown=True,
        )
        print_success("Agent created successfully with BraveSearchTools")
        
        print("\n  Running test query...")
        print("  (This may take a moment...)")
        
        response = agent.run(
            "Search for Reddit discussions about moving to Seattle. Use site:reddit.com and show me just the top 2 results.",
            stream=False
        )
        
        print_success("Agent executed successfully!")
        print("\n  Agent response preview:")
        print("  " + "-"*76)
        response_text = str(response.content)[:500]
        for line in response_text.split('\n')[:10]:
            print(f"  {line}")
        print("  " + "-"*76)
        
        return True
    except ImportError as e:
        print_error(f"Import error: {e}")
        return False
    except Exception as e:
        print_error(f"Agent test failed: {e}")
        import traceback
        print("\n  Full error:")
        traceback.print_exc()
        return False

def main():
    """Run all diagnostic tests"""
    print_header("Brave Search API Integration Diagnostic Tool")
    print("This script will test your Brave Search setup for the Should I Move? app")
    
    results = []
    
    # Run tests
    results.append(("Environment Variables", check_environment_variables()))
    results.append(("brave-search Library", test_brave_search_import()))
    
    # Only continue if basics are working
    if results[-1][1] and results[0][1]:
        results.append(("Brave API Connection", test_brave_api_connection()))
        
        if results[-1][1]:
            results.append(("Reddit Site Search", test_reddit_site_search()))
    
    results.append(("Agno BraveSearchTools", test_agno_brave_tools()))
    
    # Test agent if everything else works
    if all(r[1] for r in results):
        results.append(("Agno Agent Integration", test_agno_agent_with_brave()))
    
    # Summary
    print_header("Test Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}  {test_name}")
    
    print(f"\n  Results: {passed}/{total} tests passed")
    
    if passed == total:
        print_success("\n🎉 All tests passed! Brave Search integration is working correctly.")
        print_success("Your Migration Researcher agent will now use Brave Search to find Reddit discussions.")
    else:
        print_error("\nSome tests failed. Please fix the issues above.")
        print_warning("\nCommon fixes:")
        print("  1. Get Brave API key from: https://brave.com/search/api/")
        print("  2. Add BRAVE_API_KEY to your .env file")
        print("  3. Install missing packages: pip install brave-search agno openai")
    
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()


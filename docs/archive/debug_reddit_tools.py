"""
Debug script for Reddit API integration
Tests Reddit credentials and RedditTools functionality
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
    """Check if Reddit credentials are set"""
    print_step(1, "Checking Environment Variables")
    
    required_vars = [
        'REDDIT_CLIENT_ID',
        'REDDIT_CLIENT_SECRET',
        'REDDIT_USER_AGENT'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Show partial value for security
            display_value = value[:8] + "..." if len(value) > 8 else "***"
            print_success(f"{var} = {display_value}")
        else:
            print_error(f"{var} is NOT SET")
            missing_vars.append(var)
    
    if missing_vars:
        print_warning("Missing environment variables!")
        print("\n  To fix this, set the following in your .env file:")
        print("\n  REDDIT_CLIENT_ID=your-client-id")
        print("  REDDIT_CLIENT_SECRET=your-client-secret")
        print("  REDDIT_USER_AGENT=YourApp/1.0")
        print("\n  Get credentials from: https://www.reddit.com/prefs/apps")
        return False
    
    return True

def test_praw_import():
    """Test if praw library is installed"""
    print_step(2, "Testing PRAW Library Import")
    
    try:
        import praw
        print_success(f"praw library installed (version: {praw.__version__})")
        return True
    except ImportError as e:
        print_error(f"praw library not installed: {e}")
        print_warning("Install with: pip install praw")
        return False

def test_reddit_connection():
    """Test basic Reddit API connection"""
    print_step(3, "Testing Reddit API Connection")
    
    try:
        import praw
        
        reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent=os.getenv('REDDIT_USER_AGENT')
        )
        
        # Test read-only access
        reddit.read_only = True
        
        # Try to authenticate
        print("  Attempting to authenticate...")
        try:
            # This will trigger authentication
            user = reddit.user.me()
            if user is None:
                print_success("Authenticated (read-only mode)")
            else:
                print_success(f"Authenticated as: {user.name}")
        except Exception as auth_error:
            print_warning(f"Auth check returned: {auth_error}")
            print_warning("This is expected for script-type apps in read-only mode")
        
        # Try to get a subreddit
        subreddit = reddit.subreddit('moving')
        print_success(f"Connected to Reddit API")
        print_success(f"Test subreddit access: r/{subreddit.display_name}")
        
        return True
    except Exception as e:
        print_error(f"Failed to connect to Reddit API: {e}")
        print_warning("Check your credentials and internet connection")
        return False

def test_reddit_search():
    """Test Reddit search functionality"""
    print_step(4, "Testing Reddit Search")
    
    try:
        import praw
        from prawcore.exceptions import ResponseException, OAuthException
        
        reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent=os.getenv('REDDIT_USER_AGENT')
        )
        reddit.read_only = True
        
        # Try a simple search
        query = "should I move"
        print(f"  Searching for: '{query}'")
        
        try:
            results = list(reddit.subreddit('moving').search(query, limit=3))
            
            if results:
                print_success(f"Found {len(results)} results")
                for i, post in enumerate(results, 1):
                    print(f"    {i}. {post.title[:60]}...")
            else:
                print_warning("Search returned no results (but API is working)")
            
            return True
        except ResponseException as e:
            if e.response.status_code == 401:
                print_error(f"Search failed: received 401 HTTP response")
                print("\n  🔍 DIAGNOSIS: Authentication Issue")
                print("  This means your Reddit app credentials are invalid or the app type is wrong.")
                print("\n  💡 SOLUTION:")
                print("  1. Go to https://www.reddit.com/prefs/apps")
                print("  2. Find your app in the list")
                print("  3. Check if it says 'personal use script' (CORRECT) or 'web app' (WRONG)")
                print("  4. If it's a 'web app', DELETE it and create a NEW app")
                print("  5. When creating, select 'script' as the app type")
                print("  6. Copy the NEW client_id (under 'personal use script') and secret")
                print("  7. Update your .env file with the new credentials")
                return False
            else:
                print_error(f"Search failed with HTTP {e.response.status_code}: {e}")
                return False
        except OAuthException as e:
            print_error(f"OAuth error: {e}")
            print_warning("Your credentials may be incorrect or expired")
            return False
            
    except Exception as e:
        print_error(f"Search failed: {e}")
        import traceback
        print("\n  Full error trace:")
        traceback.print_exc()
        return False

def test_agno_reddit_tools():
    """Test Agno's RedditTools"""
    print_step(5, "Testing Agno RedditTools")
    
    try:
        from agno.tools.reddit import RedditTools
        
        reddit_tools = RedditTools()
        print_success("RedditTools instantiated successfully")
        
        # Check what methods are available
        methods = [m for m in dir(reddit_tools) if not m.startswith('_')]
        print(f"  Available methods: {', '.join(methods[:5])}...")
        
        return True
    except ImportError as e:
        print_error(f"Failed to import RedditTools: {e}")
        print_warning("Make sure agno is installed with: pip install -U agno")
        return False
    except Exception as e:
        print_error(f"Failed to instantiate RedditTools: {e}")
        return False

def test_agno_agent_with_reddit():
    """Test Agno Agent with RedditTools"""
    print_step(6, "Testing Agno Agent with RedditTools")
    
    try:
        from agno.agent import Agent
        from agno.models.openai import OpenAIChat
        from agno.tools.reddit import RedditTools
        
        # Check OpenAI API key
        if not os.getenv('OPENAI_API_KEY'):
            print_error("OPENAI_API_KEY not set")
            print_warning("Set it in your .env file to test the agent")
            return False
        
        print("  Creating test agent...")
        agent = Agent(
            name="Reddit Test Agent",
            model=OpenAIChat("gpt-4o-mini"),
            tools=[RedditTools()],
            instructions=["You are a Reddit search assistant"],
            markdown=True,
        )
        print_success("Agent created successfully with RedditTools")
        
        print("\n  Running test query...")
        print("  (This may take a moment...)")
        
        response = agent.run(
            "Search Reddit for posts about moving to New York. Show me just the top 2 results.",
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
    print_header("Reddit API Integration Diagnostic Tool")
    print("This script will test your Reddit API setup for the Should I Move? app")
    
    results = []
    
    # Run tests
    results.append(("Environment Variables", check_environment_variables()))
    results.append(("PRAW Library", test_praw_import()))
    
    # Only continue if basics are working
    if results[-1][1]:
        results.append(("Reddit Connection", test_reddit_connection()))
        
        if results[-1][1]:
            results.append(("Reddit Search", test_reddit_search()))
    
    results.append(("Agno RedditTools", test_agno_reddit_tools()))
    
    # Test agent if everything else works
    if all(r[1] for r in results):
        results.append(("Agno Agent Integration", test_agno_agent_with_reddit()))
    
    # Summary
    print_header("Test Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}  {test_name}")
    
    print(f"\n  Results: {passed}/{total} tests passed")
    
    if passed == total:
        print_success("\nAll tests passed! Reddit integration is working correctly.")
    else:
        print_error("\nSome tests failed. Please fix the issues above.")
        
        # Check for specific 401 error
        failed_tests = [name for name, result in results if not result]
        if "Reddit Search" in failed_tests and "Reddit Connection" in [name for name, result in results if result]:
            print("\n" + "!"*80)
            print("  🚨 LIKELY ISSUE: Wrong Reddit App Type")
            print("!"*80)
            print("\n  Your Reddit app is probably a 'web app' but should be a 'script' app.")
            print("\n  Quick Fix:")
            print("  1. Go to: https://www.reddit.com/prefs/apps")
            print("  2. Delete your current app")
            print("  3. Click 'create another app' or 'create app'")
            print("  4. Name: anything you want")
            print("  5. Type: Select 'script' (NOT 'web app')")
            print("  6. Redirect URI: http://localhost:8080")
            print("  7. Click 'create app'")
            print("  8. Copy the client_id (under 'personal use script')")
            print("  9. Copy the secret")
            print("  10. Update your .env file with these new credentials")
            print("\n" + "!"*80)
        else:
            print_warning("\nCommon fixes:")
            print("  1. Create Reddit app at: https://www.reddit.com/prefs/apps")
            print("  2. Add credentials to .env file")
            print("  3. Install missing packages: pip install praw agno openai")
    
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()


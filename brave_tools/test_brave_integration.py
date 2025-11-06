"""
Quick test of Brave Search integration with custom tool
"""

import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 80)
print("Testing Custom Brave Search Integration")
print("=" * 80)

# Test 1: Environment variable
print("\n[1] Checking BRAVE_API_KEY...")
api_key = os.getenv('BRAVE_API_KEY')
if api_key:
    print(f"✅ BRAVE_API_KEY is set ({api_key[:8]}...)")
else:
    print("❌ BRAVE_API_KEY not set!")
    exit(1)

# Test 2: Import custom tool
print("\n[2] Importing custom search_reddit_discussions tool...")
try:
    # Add parent directory to path to import from brave_tools
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from brave_tools.brave_search_tool import search_reddit_discussions
    print("✅ Custom tool imported successfully")
except ImportError as e:
    print(f"❌ Failed to import: {e}")
    exit(1)

# Test 3: Test the tool directly
print("\n[3] Testing tool directly...")
print("   Searching for: Seattle to Austin discussions")
print("   (This will take a moment...)\n")

try:
    result = search_reddit_discussions("Seattle", "Austin", max_results=5)
    
    if "ERROR" in result:
        print(f"❌ Tool returned error: {result}")
        exit(1)
    
    print("✅ Tool executed successfully!")
    print("\n" + "-" * 80)
    print("Sample Results:")
    print("-" * 80)
    # Show first 500 chars of result
    print(result[:500] + "...")
    print("-" * 80)
    
except Exception as e:
    print(f"❌ Tool failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 4: Test with Agent
print("\n[4] Creating agent with custom tool...")
try:
    from agno.agent import Agent
    from agno.models.openai import OpenAIChat
    
    agent = Agent(
        name="Reddit Search Agent",
        model=OpenAIChat("gpt-4o-mini"),
        tools=[search_reddit_discussions],
        instructions=[
            "You are a Reddit migration research specialist",
            "Use the search_reddit_discussions function to find discussions",
            "Summarize what you find"
        ],
        markdown=True,
    )
    print("✅ Agent created successfully")
except Exception as e:
    print(f"❌ Failed to create agent: {e}")
    exit(1)

# Test 5: Run agent
print("\n[5] Running agent with custom tool...")
print("   Query: Analyze discussions about moving from Denver to Portland")
print("   (This will take a moment...)\n")

try:
    response = agent.run(
        "Use search_reddit_discussions to find discussions about moving from Denver to Portland. "
        "Show me what Redditors are saying (top 3 insights).",
        stream=False
    )
    
    print("✅ Agent executed successfully!")
    print("\n" + "-" * 80)
    print("Agent Response:")
    print("-" * 80)
    print(response.content)
    print("-" * 80)
    
    print("\n" + "=" * 80)
    print("🎉 All tests passed! Custom Brave Search integration is working!")
    print("=" * 80)
    print("\nYour Migration Researcher agent will now use the custom Brave Search tool")
    print("to find Reddit discussions about city relocations.")
    print("\n✅ No dependency issues!")
    print("✅ Works in your .venv environment!")
    print("\nRun: python 02-agno-coordination.py")
    print("=" * 80)
    
except Exception as e:
    print(f"❌ Agent execution failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)


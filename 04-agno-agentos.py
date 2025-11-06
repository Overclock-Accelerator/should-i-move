"""
AgentOS Integration for Should I Move? Application

This module demonstrates how to integrate the existing Agno agents with AgentOS
and the AgentOS Control Plane for production deployment, monitoring, and management.

Key Features:
- FastAPI runtime for serving agents via API
- Session management for conversation tracking
- Knowledge base integration
- Memory persistence
- Control Plane connectivity for web-based management

Usage:
    python agentos_integration.py

Then connect to the AgentOS Control Plane at https://app.agno.com
"""

from typing import List, Optional
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from difflib import get_close_matches

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.team.team import Team
from agno.tools.firecrawl import FirecrawlTools
from agno.tools.local_file_system import LocalFileSystemTools
from agno.storage.agent.postgres import PgAgentStorage
from agno.knowledge.text import TextKnowledgeBase
from agno.memory.db.postgres import PgMemoryDb
from agno.vectordb.pgvector import PgVector
from pydantic import BaseModel, Field

# Import custom Brave Search tool
from brave_tools.brave_search_tool import search_reddit_discussions

# Load environment variables
load_dotenv()

# ============================================================================
# Database Configuration for AgentOS
# ============================================================================

# PostgreSQL connection string for session storage, memory, and knowledge
# Format: postgresql+psycopg://user:password@host:port/database
DB_URL = os.getenv("AGENTOS_DB_URL", "postgresql+psycopg://agno:agno@localhost:5532/agno")

# Configure storage for session management
agent_storage = PgAgentStorage(
    table_name="agent_sessions",
    db_url=DB_URL,
)

# Configure memory database for persistent memory across sessions
memory_db = PgMemoryDb(
    table_name="agent_memory",
    db_url=DB_URL,
)

# Configure vector database for knowledge base
vector_db = PgVector(
    table_name="agent_knowledge",
    db_url=DB_URL,
    embedder=OpenAIChat(model="text-embedding-3-small"),
)

# ============================================================================
# Knowledge Base Setup
# ============================================================================

# Create a knowledge base with city relocation information
relocation_knowledge = TextKnowledgeBase(
    path="data",  # Load from data directory
    vector_db=vector_db,
    reader=None,  # Will auto-detect file types
)

# ============================================================================
# Load City Database
# ============================================================================

CITY_DATABASE = {}
try:
    with open("data/nerdwallet_cities_comprehensive.json", "r", encoding="utf-8") as f:
        CITY_DATABASE = json.load(f)
    print(f"✅ Loaded {len(CITY_DATABASE)} cities from database")
except FileNotFoundError:
    print("⚠️  City database not found. Falling back to basic URL formatting.")


# ============================================================================
# Pydantic Models (Reused from existing apps)
# ============================================================================

class UserProfile(BaseModel):
    """Captures user's financial info and preferences"""
    current_city: str = Field(..., description="The city the user currently lives in")
    desired_city: str = Field(..., description="The city the user is considering moving to")
    annual_income: Optional[float] = Field(None, description="User's annual income")
    monthly_expenses: Optional[float] = Field(None, description="User's monthly expenses")
    city_preferences: List[str] = Field(
        default_factory=list,
        description="What the user values in a city"
    )


class CostAnalysis(BaseModel):
    """Cost of living comparison between cities"""
    overall_cost_difference: str
    housing_comparison: str
    food_comparison: str
    transportation_comparison: str
    taxes_comparison: str
    key_insights: List[str]


class SentimentAnalysis(BaseModel):
    """City vibe and livability analysis"""
    overall_sentiment: str
    vibe_description: str
    livability_score: str
    notable_pros: List[str]
    notable_cons: List[str]


class MigrationInsights(BaseModel):
    """Insights from people who made similar moves"""
    number_of_sources: int
    reddit_insights_included: bool
    redditor_perspectives: str
    common_reasons_for_moving: List[str]
    common_challenges: List[str]
    common_positive_outcomes: List[str]
    regrets_or_warnings: List[str]
    summary: str


class FinalRecommendation(BaseModel):
    """Final recommendation with justification"""
    recommendation: str
    confidence_level: str
    key_supporting_factors: List[str]
    key_concerns: List[str]
    financial_impact_summary: str
    lifestyle_impact_summary: str
    next_steps: List[str]
    detailed_justification: str


# ============================================================================
# Custom Tools (Reused from existing apps)
# ============================================================================

def find_best_city_match(city_name: str, cutoff: float = 0.6) -> Optional[dict]:
    """Find the best matching city from the database using fuzzy matching."""
    if not CITY_DATABASE:
        return None
    
    city_name = city_name.strip()
    
    # Try exact match first
    for city_key, city_data in CITY_DATABASE.items():
        if city_key.lower() == city_name.lower():
            return city_data
        if city_data['city'].lower() == city_name.lower():
            return city_data
        if city_data.get('display_name', '').lower() == city_name.lower():
            return city_data
    
    # Try fuzzy matching
    display_names = [city_data.get('display_name', key) for key, city_data in CITY_DATABASE.items()]
    matches = get_close_matches(city_name, display_names, n=1, cutoff=cutoff)
    
    if matches:
        for city_key, city_data in CITY_DATABASE.items():
            if city_data.get('display_name', city_key) == matches[0]:
                return city_data
    
    return None


def format_city_for_url(city_name: str) -> str:
    """Format city name for NerdWallet URL using the city database."""
    import re
    
    city_match = find_best_city_match(city_name)
    
    if city_match:
        return city_match['url_format']
    
    # Fallback to basic formatting
    city_clean = re.sub(r',?\s*(AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|VA|WA|WV|WI|WY)\s*$', '', city_name, flags=re.IGNORECASE)
    city_formatted = city_clean.strip().lower().replace(' ', '-')
    city_formatted = re.sub(r'[^a-z0-9-]', '', city_formatted)
    
    return city_formatted


def get_cost_of_living_comparison(current_city: str, desired_city: str) -> str:
    """Get cost of living comparison between two cities from NerdWallet."""
    current_formatted = format_city_for_url(current_city)
    desired_formatted = format_city_for_url(desired_city)
    
    url = f"https://www.nerdwallet.com/cost-of-living-calculator/compare/{current_formatted}-vs-{desired_formatted}"
    
    print(f"\n🔍 [COST TOOL] Fetching data from: {url}\n")
    
    try:
        firecrawl = FirecrawlTools()
        result = firecrawl.scrape_website(url)
        
        print(f"✅ [COST TOOL] Successfully retrieved cost of living data!\n")
        
        return f"""
Cost of Living Comparison Data from NerdWallet:
URL: {url}

{result}

Please extract and analyze the cost metrics from the above data.
"""
    except Exception as e:
        print(f"⚠️ [COST TOOL] Error fetching data: {e}\n")
        return f"""
Unable to fetch real-time cost of living data from NerdWallet.
URL attempted: {url}
Error: {e}

Please provide analysis based on your general knowledge of {current_city} and {desired_city}.
"""


# ============================================================================
# Define Agents with AgentOS Integration
# ============================================================================

cost_analyst = Agent(
    name="Cost Analyst",
    agent_id="cost-analyst",  # Unique ID for AgentOS
    model=OpenAIChat("gpt-4o-mini"),
    role="Analyzes cost of living differences between cities",
    description=(
        "You are a financial analyst specializing in cost of living comparisons. "
        "Analyze the cost differences between cities using real-time data from NerdWallet."
    ),
    instructions=[
        "Use the get_cost_of_living_comparison function to fetch real cost data",
        "Extract specific metrics: overall cost difference %, housing, transportation, food, taxes",
        "Provide comprehensive cost analysis with specific numbers",
        "If the tool fails, fall back to general knowledge but note this",
    ],
    tools=[get_cost_of_living_comparison],
    output_schema=CostAnalysis,
    storage=agent_storage,  # Enable session storage
    memory=memory_db,  # Enable memory persistence
    knowledge=relocation_knowledge,  # Attach knowledge base
    markdown=True,
)

sentiment_analyst = Agent(
    name="Sentiment Analyst",
    agent_id="sentiment-analyst",  # Unique ID for AgentOS
    model=OpenAIChat("gpt-4o-mini"),
    role="Researches city vibe, culture, and livability",
    description=(
        "You are a city culture and livability expert. "
        "Research and analyze the vibe, culture, and livability of cities."
    ),
    instructions=[
        "Analyze the overall vibe and culture of the destination city",
        "Assess livability based on factors like walkability, public spaces, community",
        "Identify notable pros and cons",
        "Consider: arts/culture scene, outdoor activities, social atmosphere, diversity, food scene",
    ],
    output_schema=SentimentAnalysis,
    storage=agent_storage,  # Enable session storage
    memory=memory_db,  # Enable memory persistence
    knowledge=relocation_knowledge,  # Attach knowledge base
    markdown=True,
)

migration_researcher = Agent(
    name="Migration Researcher",
    agent_id="migration-researcher",  # Unique ID for AgentOS
    model=OpenAIChat("gpt-4o-mini"),
    role="Finds and summarizes experiences from people who made similar moves",
    description=(
        "You are a research specialist focused on finding real-world experiences from Reddit. "
        "Use Brave Search to find Reddit discussions about city migrations."
    ),
    instructions=[
        "Use the search_reddit_discussions function to find Reddit migration stories",
        "Extract common themes, challenges, and outcomes from discussions",
        "Highlight what Redditors say about the move",
        "Identify common reasons, challenges, positive outcomes, and warnings",
        "Set reddit_insights_included to True if Reddit data was successfully retrieved",
    ],
    tools=[search_reddit_discussions],
    output_schema=MigrationInsights,
    storage=agent_storage,  # Enable session storage
    memory=memory_db,  # Enable memory persistence
    knowledge=relocation_knowledge,  # Attach knowledge base
    markdown=True,
)


# ============================================================================
# Define Team with AgentOS Integration
# ============================================================================

move_decision_team = Team(
    name="City Move Decision Team",
    team_id="move-decision-team",  # Unique ID for AgentOS
    model=OpenAIChat("gpt-4o-mini"),
    members=[cost_analyst, sentiment_analyst, migration_researcher],
    tools=[LocalFileSystemTools(
        target_directory="./reports",
        default_extension="md"
    )],
    instructions=[
        "You are a coordinator helping users decide whether to move to a new city.",
        "",
        "Step 1 - Information Verification:",
        "Check if you have all necessary information:",
        "  - Current city name",
        "  - Desired destination city name",
        "  - Financial situation (income, expenses, or budget concerns)",
        "  - City preferences or values",
        "",
        "If missing essential information, ask the user before proceeding.",
        "",
        "Step 2 - Delegate to Sub-Agents:",
        "  - Delegate to the Cost Analyst to analyze cost of living differences",
        "  - Delegate to the Sentiment Analyst to research the city's vibe and livability",
        "  - Delegate to the Migration Researcher to find experiences from similar moves",
        "",
        "Step 3 - Synthesize Results:",
        "After receiving all three analyses, synthesize into a clear recommendation.",
        "Provide a balanced assessment considering financial, lifestyle, and experiential factors.",
        "",
        "Step 4 - Save Report:",
        "Save a comprehensive markdown report using write_file.",
        "Filename format: '{current_city}_to_{desired_city}_{timestamp}_analysis.md'",
    ],
    output_schema=FinalRecommendation,
    storage=agent_storage,  # Enable session storage
    memory=memory_db,  # Enable memory persistence
    knowledge=relocation_knowledge,  # Attach knowledge base
    add_member_tools_to_context=False,
    markdown=True,
    show_members_responses=True,
)


# ============================================================================
# AgentOS FastAPI Application
# ============================================================================

from agno.api.app import create_agentos_app

# Create the AgentOS FastAPI application
app = create_agentos_app(
    agents=[cost_analyst, sentiment_analyst, migration_researcher],
    teams=[move_decision_team],
    knowledge=[relocation_knowledge],
    storage=agent_storage,
)


# ============================================================================
# Run the AgentOS Server
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*80)
    print("🚀 Starting AgentOS for 'Should I Move?' Application")
    print("="*80)
    print("\n📋 Available Resources:")
    print("   - Agents: Cost Analyst, Sentiment Analyst, Migration Researcher")
    print("   - Team: City Move Decision Team")
    print("   - Knowledge Base: City Relocation Data")
    print("\n🌐 Server Information:")
    print("   - Local URL: http://localhost:7777")
    print("   - API Docs: http://localhost:7777/docs")
    print("\n🔗 Next Steps:")
    print("   1. Visit https://app.agno.com to access the Control Plane")
    print("   2. Click 'Connect AgentOS' and enter: http://localhost:7777")
    print("   3. Start chatting with your agents through the web interface!")
    print("\n" + "="*80 + "\n")
    
    # Run the FastAPI server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=7777,
        log_level="info",
    )


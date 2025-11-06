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
from agno.db.postgres import PostgresDb
from agno.knowledge.knowledge import Knowledge
from agno.knowledge.embedder.openai import OpenAIEmbedder
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

# Configure database for session and memory management
db = PostgresDb(
    db_url=DB_URL,
    session_table="agent_sessions",
    memory_table="agent_memory",
)

# Configure vector database for knowledge base
vector_db = PgVector(
    table_name="agent_knowledge",
    db_url=DB_URL,
    embedder=OpenAIEmbedder(id="text-embedding-3-small"),
)

# ============================================================================
# Knowledge Base Setup
# ============================================================================

# Create system documentation for the knowledge base
SYSTEM_DOCS = """
# Should I Move? - Multi-Agent System Documentation

## System Overview
This is a comprehensive city relocation analysis system that helps people make informed decisions about moving to a new city. The system consists of specialized agents working together as a coordinated team.

## Team Structure

### Cost Analyst Agent
**Role:** Financial Analysis Expert
**Specialty:** Cost of living comparisons and financial impact assessment
**Capabilities:**
- Fetches real-time cost data from NerdWallet
- Compares housing, food, transportation, and tax costs
- Provides detailed financial impact analysis
- Calculates overall cost differences as percentages
**Tool Access:** get_cost_of_living_comparison (NerdWallet scraper)
**Output:** Structured CostAnalysis with specific metrics and insights

### Sentiment Analyst Agent
**Role:** City Culture & Livability Expert
**Specialty:** Urban lifestyle, culture, and quality of life assessment
**Capabilities:**
- Analyzes city vibe, culture, and atmosphere
- Evaluates livability factors (walkability, public spaces, community)
- Assesses arts, culture, outdoor activities, food scene
- Identifies notable pros and cons of the destination city
**Output:** Structured SentimentAnalysis with vibe descriptions and livability scores

### Migration Researcher Agent
**Role:** Real-World Experience Gatherer
**Specialty:** Finding and synthesizing experiences from people who made similar moves
**Capabilities:**
- Searches Reddit discussions using Brave Search API
- Extracts common themes from migration stories
- Identifies challenges, positive outcomes, and warnings
- Summarizes real Redditor perspectives on the move
**Tool Access:** search_reddit_discussions (Brave Search for Reddit)
**Output:** Structured MigrationInsights with common patterns and perspectives

### City Move Decision Team (Lead Agent)
**Role:** Coordinator & Decision Synthesizer
**Capabilities:**
- Manages multi-turn conversations with users
- Collects necessary information (current city, desired city, finances, preferences)
- Delegates work to specialized agents
- Synthesizes all analyses into a comprehensive recommendation
- Saves detailed markdown reports
**Tool Access:** LocalFileSystemTools for report generation
**Output:** FinalRecommendation with confidence level and justification

## Conversation Flow

1. **Information Gathering:** The team engages with the user to understand their situation
2. **Delegation:** Work is distributed to specialized agents in parallel
3. **Analysis:** Each agent performs their specialized analysis independently
4. **Synthesis:** The team leader combines all insights into a coherent recommendation
5. **Report Generation:** A comprehensive markdown report is saved for reference

## Knowledge Base Contents

This knowledge base contains:
- System documentation (this file)
- City relocation data from the data/ directory
- Historical analysis reports from previous conversations
- Team member roles and capabilities

## How to Use This System

When interacting with this system:
1. Provide your current city and desired destination city
2. Share your financial situation (income, budget concerns)
3. Mention what you value in a city (culture, nature, walkability, etc.)
4. The team will analyze and provide a comprehensive recommendation

The system excels at:
- Financial impact analysis with real-time data
- Cultural fit assessment
- Learning from others' experiences
- Balanced decision-making considering multiple factors
"""

# Create a knowledge base with system documentation and city data
relocation_knowledge = Knowledge(
    vector_db=vector_db,
)

# Add system documentation to knowledge base
try:
    print("📚 Adding system documentation to knowledge base...")
    relocation_knowledge.add_text(
        text=SYSTEM_DOCS,
        title="System Documentation",
    )
    print("✅ System documentation added to knowledge base")
except Exception as e:
    print(f"⚠️  Could not add system docs to knowledge base: {e}")

# Load existing city data if available
try:
    print("📚 Loading city data into knowledge base...")
    relocation_knowledge.add_directory(
        path="data",
        glob="*.json",
    )
    print("✅ City data loaded into knowledge base")
except Exception as e:
    print(f"⚠️  Could not load city data: {e}")

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
    id="cost-analyst",  # Unique ID for AgentOS
    model=OpenAIChat("gpt-4o-mini"),
    role="Financial Analysis Expert - Cost of Living Specialist",
    description=(
        "Expert financial analyst specializing in cost of living comparisons between cities. "
        "Provides detailed analysis of housing costs, transportation expenses, food prices, "
        "tax implications, and overall cost differences using real-time data from NerdWallet."
    ),
    instructions=[
        "You are a financial analyst helping people understand the cost implications of relocating.",
        "",
        "🔍 DATA COLLECTION:",
        "- Use get_cost_of_living_comparison to fetch real-time NerdWallet data",
        "- Extract specific percentages and dollar amounts for all cost categories",
        "",
        "📊 ANALYSIS REQUIREMENTS:",
        "Analyze and report on:",
        "- Overall cost of living difference (percentage)",
        "- Housing costs (rent/mortgage comparison)",
        "- Food and groceries pricing",
        "- Transportation costs (gas, insurance, public transit)",
        "- Tax implications (income tax, sales tax, property tax)",
        "",
        "💡 INSIGHTS:",
        "- Highlight the most significant cost differences",
        "- Note any surprising findings",
        "- Consider the impact on different income levels",
        "- If data fetch fails, acknowledge this and use general knowledge",
        "",
        "📋 OUTPUT:",
        "Provide a structured CostAnalysis with clear, specific numbers and actionable insights.",
    ],
    tools=[get_cost_of_living_comparison],
    output_schema=CostAnalysis,
    db=db,  # Enable session storage and memory
    knowledge=relocation_knowledge,  # Attach knowledge base
    markdown=True,
)

sentiment_analyst = Agent(
    name="Sentiment Analyst",
    id="sentiment-analyst",  # Unique ID for AgentOS
    model=OpenAIChat("gpt-4o-mini"),
    role="City Culture & Livability Expert",
    description=(
        "Urban lifestyle expert specializing in city culture, vibe, and quality of life assessment. "
        "Analyzes the intangible aspects of cities including walkability, culture scene, social atmosphere, "
        "outdoor activities, diversity, and overall livability factors that impact daily life."
    ),
    instructions=[
        "You are a city culture expert helping people understand what life would be like in a new city.",
        "",
        "🏙️ CITY VIBE ANALYSIS:",
        "Assess and describe:",
        "- Overall atmosphere and personality of the city",
        "- Social scene and community feel",
        "- Pace of life (fast-paced, relaxed, balanced)",
        "- Cultural identity and unique characteristics",
        "",
        "🌟 LIVABILITY FACTORS:",
        "Evaluate:",
        "- Walkability and public transportation",
        "- Parks, public spaces, and outdoor recreation",
        "- Arts, culture, and entertainment scene",
        "- Food and dining culture",
        "- Diversity and inclusivity",
        "- Weather and climate impact on lifestyle",
        "",
        "⚖️ BALANCED ASSESSMENT:",
        "- List notable pros (what makes this city great)",
        "- List notable cons (challenges or drawbacks)",
        "- Provide an overall livability score/rating",
        "",
        "💡 CONTEXT AWARENESS:",
        "- Consider what the user values when highlighting features",
        "- Draw on knowledge base for city-specific insights",
        "- Be honest about both positives and negatives",
        "",
        "📋 OUTPUT:",
        "Provide a structured SentimentAnalysis with vivid descriptions and clear pros/cons.",
    ],
    output_schema=SentimentAnalysis,
    db=db,  # Enable session storage and memory
    knowledge=relocation_knowledge,  # Attach knowledge base
    markdown=True,
)

migration_researcher = Agent(
    name="Migration Researcher",
    id="migration-researcher",  # Unique ID for AgentOS
    model=OpenAIChat("gpt-4o-mini"),
    role="Real-World Experience Researcher",
    description=(
        "Research specialist focused on gathering and analyzing real experiences from people "
        "who have made similar city moves. Uses Brave Search to find authentic Reddit discussions "
        "and extracts valuable insights, common challenges, and practical advice from those who "
        "have lived through similar relocations."
    ),
    instructions=[
        "You are a research specialist uncovering real stories from people who made similar moves.",
        "",
        "🔎 DATA GATHERING:",
        "- Use search_reddit_discussions to find relevant Reddit threads",
        "- Search for discussions about the specific city pair",
        "- Look for first-hand experiences and detailed stories",
        "",
        "📖 ANALYSIS APPROACH:",
        "Extract and synthesize:",
        "- Common reasons people made this move",
        "- Typical challenges encountered",
        "- Positive outcomes and pleasant surprises",
        "- Regrets, warnings, or 'wish I knew' moments",
        "- Overall sentiment from Redditors about the move",
        "",
        "💬 REDDITOR PERSPECTIVES:",
        "- Quote or paraphrase specific insights when relevant",
        "- Capture the authentic voice of people's experiences",
        "- Balance positive and negative perspectives",
        "- Note the number of sources found",
        "",
        "✅ DATA QUALITY:",
        "- Set reddit_insights_included to True if you successfully retrieved Reddit data",
        "- Set it to False if the search failed or returned no useful results",
        "- If no Reddit data is available, acknowledge this limitation",
        "",
        "📋 OUTPUT:",
        "Provide a structured MigrationInsights report with authentic, actionable perspectives.",
    ],
    tools=[search_reddit_discussions],
    output_schema=MigrationInsights,
    db=db,  # Enable session storage and memory
    knowledge=relocation_knowledge,  # Attach knowledge base
    markdown=True,
)


# ============================================================================
# Define Team with AgentOS Integration
# ============================================================================

move_decision_team = Team(
    name="City Move Decision Team",
    id="move-decision-team",  # Unique ID for AgentOS
    model=OpenAIChat("gpt-4o-mini"),
    members=[cost_analyst, sentiment_analyst, migration_researcher],
    tools=[LocalFileSystemTools(
        target_directory="./reports",
        default_extension="md"
    )],
    instructions=[
        "You are the coordinator of a specialized team helping people make informed city relocation decisions.",
        "",
        "🤝 YOUR ROLE:",
        "- Engage in natural, helpful conversations about city moves",
        "- Ask clarifying questions when needed",
        "- Coordinate three specialized agents to provide comprehensive analysis",
        "- Synthesize their insights into clear, actionable recommendations",
        "",
        "💬 CONVERSATIONAL APPROACH:",
        "- Be warm, professional, and empathetic",
        "- Remember context from earlier in the conversation",
        "- Explain what your team will do before delegating",
        "- You can answer questions about the team, the process, or provide updates",
        "- If asked about your capabilities, reference the knowledge base for team member details",
        "",
        "📋 INFORMATION YOU NEED:",
        "Before conducting analysis, gather:",
        "  - Current city (where they live now)",
        "  - Desired city (where they're considering moving)",
        "  - Financial context (income, budget, or financial concerns)",
        "  - What they value in a city (culture, nature, walkability, affordability, etc.)",
        "",
        "Don't ask for everything at once - have a natural conversation and gather details as you go.",
        "",
        "🔄 ANALYSIS WORKFLOW:",
        "Once you have the key information:",
        "1. Explain briefly what analysis you'll perform",
        "2. Delegate to your three specialists:",
        "   - Cost Analyst: Financial impact & cost of living comparison",
        "   - Sentiment Analyst: City vibe, culture, and livability assessment",
        "   - Migration Researcher: Real experiences from Reddit discussions",
        "3. Wait for all three analyses to complete",
        "4. Synthesize results into a clear recommendation",
        "5. Save a detailed report using write_file",
        "",
        "📊 FINAL OUTPUT:",
        "Provide a FinalRecommendation that includes:",
        "- Clear recommendation (move/don't move/consider carefully)",
        "- Confidence level (high/medium/low)",
        "- Key supporting factors and concerns",
        "- Financial and lifestyle impact summaries",
        "- Practical next steps",
        "- Detailed justification",
        "",
        "💾 REPORT SAVING:",
        "After delivering the recommendation, save a markdown report.",
        "Format: '{current_city}_to_{desired_city}_{timestamp}_analysis.md'",
        "The report should be comprehensive and include all agent analyses.",
        "",
        "🧠 REMEMBER:",
        "- You have access to a knowledge base with system documentation and city data",
        "- You can reference team member capabilities when explaining the process",
        "- You maintain conversation memory across messages in the same session",
        "- Be concise but thorough - users appreciate clarity over verbosity",
    ],
    output_schema=FinalRecommendation,
    db=db,  # Enable session storage and memory
    knowledge=relocation_knowledge,  # Attach knowledge base
    add_member_tools_to_context=False,
    markdown=True,
    show_members_responses=True,
)


# ============================================================================
# AgentOS FastAPI Application
# ============================================================================

from agno.os import AgentOS

# Create the AgentOS instance
agent_os = AgentOS(
    id="should-i-move-os",
    description="Should I Move? - City Relocation Analysis System",
    agents=[cost_analyst, sentiment_analyst, migration_researcher],
    teams=[move_decision_team],
    knowledge=[relocation_knowledge],
)

# Get the FastAPI app
app = agent_os.get_app()


# ============================================================================
# Run the AgentOS Server
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("🚀 Starting AgentOS for 'Should I Move?' Application")
    print("="*80)
    print("\n📋 Available Resources:")
    print("   - 👥 Agents: Cost Analyst, Sentiment Analyst, Migration Researcher")
    print("   - 🤝 Team: City Move Decision Team (coordinator)")
    print("   - 🧠 Knowledge Base: System docs, team capabilities, city data")
    print("\n💡 Agent Capabilities:")
    print("   - Cost Analyst: Real-time cost of living data from NerdWallet")
    print("   - Sentiment Analyst: City culture, vibe, and livability analysis")
    print("   - Migration Researcher: Real Reddit experiences via Brave Search")
    print("\n🌐 Server Information:")
    print("   - Local URL: http://localhost:7777")
    print("   - API Docs: http://localhost:7777/docs")
    print("   - Health Check: http://localhost:7777/health")
    print("\n🔗 Next Steps:")
    print("   1. Visit https://app.agno.com to access the Control Plane")
    print("   2. Click 'Connect AgentOS' and enter: http://localhost:7777")
    print("   3. Start chatting with your agents through the web interface!")
    print("   4. Try: 'Should I move from [City A] to [City B]?'")
    print("\n💬 Conversation Tips:")
    print("   - The team maintains conversation memory across messages")
    print("   - Ask about agent capabilities: 'What can you help me with?'")
    print("   - Request specific analysis: 'Compare costs between X and Y'")
    print("   - Get process updates: 'How does your analysis work?'")
    print("\n" + "="*80 + "\n")
    
    # Run the AgentOS server
    agent_os.serve(
        app="04-agno-agentos:app",
        host="0.0.0.0",
        port=7777,
        reload=True,
    )


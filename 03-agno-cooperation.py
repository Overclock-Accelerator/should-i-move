from typing import List, Optional
import os
import re
import json
import time
import threading
import logging
from datetime import datetime
from dotenv import load_dotenv
from difflib import get_close_matches

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.team.team import Team
from agno.tools.firecrawl import FirecrawlTools
from agno.tools.local_file_system import LocalFileSystemTools
from pydantic import BaseModel, Field

# Import custom Brave Search tool
from brave_tools.brave_search_tool import search_reddit_discussions

# Load environment variables from .env file
load_dotenv()

# Suppress debug logging from Agno framework and related libraries
# This prevents verbose DEBUG output during synthesis
logging.getLogger("agno").setLevel(logging.WARNING)
logging.getLogger("phi").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)  # Suppress HTTP request logs

# Load city database for URL formatting
CITY_DATABASE = {}
try:
    with open("data/nerdwallet_cities_comprehensive.json", "r", encoding="utf-8") as f:
        CITY_DATABASE = json.load(f)
    print(f"✅ Loaded {len(CITY_DATABASE)} cities from database")
except FileNotFoundError:
    print("⚠️  City database not found. Run 'python nerdwallet-tools/create_city_database.py' first.")
    print("   Falling back to basic URL formatting.")


# ============================================================================
# Animation Helper
# ============================================================================

class ThinkingAnimation:
    """Animated thinking indicator"""
    
    def __init__(self, message: str = "Thinking"):
        self.message = message
        self.is_running = False
        self.thread = None
        self.frames = [
            "▰▱▱▱▱▱▱",
            "▰▰▱▱▱▱▱",
            "▰▰▰▱▱▱▱",
            "▰▰▰▰▱▱▱",
            "▰▰▰▰▰▱▱",
            "▰▰▰▰▰▰▱",
            "▰▰▰▰▰▰▰",
            "▱▰▰▰▰▰▰",
            "▱▱▰▰▰▰▰",
            "▱▱▱▰▰▰▰",
            "▱▱▱▱▰▰▰",
            "▱▱▱▱▱▰▰",
            "▱▱▱▱▱▱▰",
            "▱▱▱▱▱▱▱",
        ]
    
    def _animate(self):
        """Animation loop"""
        idx = 0
        while self.is_running:
            frame = self.frames[idx % len(self.frames)]
            print(f"\r{frame} {self.message}...", end="", flush=True)
            time.sleep(0.1)
            idx += 1
    
    def start(self):
        """Start the animation"""
        self.is_running = True
        self.thread = threading.Thread(target=self._animate, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop the animation"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=0.5)
        # Clear the line
        print("\r" + " " * 80 + "\r", end="", flush=True)


# ============================================================================
# Pydantic Models for Structured Data
# ============================================================================

class UserProfile(BaseModel):
    """Captures user's financial info and preferences"""
    current_city: str = Field(..., description="The city the user currently lives in")
    desired_city: str = Field(..., description="The city the user is considering moving to")
    annual_income: Optional[float] = Field(None, description="User's annual income")
    monthly_expenses: Optional[float] = Field(None, description="User's monthly expenses")
    city_preferences: List[str] = Field(
        default_factory=list,
        description="What the user values in a city (culture, weather, job market, etc.)"
    )
    current_city_likes: List[str] = Field(
        default_factory=list,
        description="What the user likes about their current city"
    )
    current_city_dislikes: List[str] = Field(
        default_factory=list,
        description="What the user dislikes about their current city"
    )
    most_important_factor: Optional[str] = Field(
        None,
        description="The single most important factor for the user in making this decision (e.g., 'affordability', 'job opportunities', 'culture', 'family proximity')"
    )


class CostAnalysis(BaseModel):
    """Cost of living comparison between cities"""
    overall_cost_difference: str = Field(
        ..., description="Summary of overall cost difference (e.g., '15% more expensive')"
    )
    housing_comparison: str = Field(..., description="Housing cost comparison")
    food_comparison: str = Field(..., description="Food cost comparison")
    transportation_comparison: str = Field(..., description="Transportation cost comparison")
    taxes_comparison: str = Field(..., description="Tax differences")
    key_insights: List[str] = Field(
        ..., description="Key financial insights from the comparison"
    )
    perspective_on_user_priority: str = Field(
        ..., description="How the cost analysis relates to the user's most important factor"
    )


class SentimentAnalysis(BaseModel):
    """City vibe and livability analysis"""
    overall_sentiment: str = Field(
        ..., description="Overall sentiment about the city (positive/mixed/negative)"
    )
    vibe_description: str = Field(..., description="General vibe and culture of the city")
    livability_score: str = Field(..., description="Assessment of livability")
    alignment_with_preferences: str = Field(
        ..., description="How well the city aligns with user's stated preferences"
    )
    notable_pros: List[str] = Field(..., description="Notable positive aspects")
    notable_cons: List[str] = Field(..., description="Notable negative aspects")
    perspective_on_user_priority: str = Field(
        ..., description="How the lifestyle/cultural factors relate to the user's most important factor"
    )


class MigrationInsights(BaseModel):
    """Insights from people who made similar moves"""
    number_of_sources: int = Field(..., description="Number of migration stories analyzed")
    reddit_insights_included: bool = Field(
        ..., description="Whether Reddit discussions were successfully analyzed"
    )
    redditor_perspectives: str = Field(
        ..., description="Summary of what Redditors are saying about this move, including key quotes or themes"
    )
    common_reasons_for_moving: List[str] = Field(
        ..., description="Common reasons people gave for the move"
    )
    common_challenges: List[str] = Field(
        ..., description="Common challenges people faced during/after the move"
    )
    common_positive_outcomes: List[str] = Field(
        ..., description="Common positive outcomes people reported"
    )
    regrets_or_warnings: List[str] = Field(
        ..., description="Any regrets or warnings from those who made the move"
    )
    summary: str = Field(..., description="Overall summary of migration experiences")
    perspective_on_user_priority: str = Field(
        ..., description="How real migration experiences relate to the user's most important factor"
    )


class DebateSummary(BaseModel):
    """Summary of the debate between agents"""
    debate_rounds: int = Field(..., description="Number of discussion rounds that occurred")
    key_points_of_agreement: List[str] = Field(
        ..., description="Main points where all agents agreed"
    )
    key_points_of_disagreement: List[str] = Field(
        ..., description="Main points where agents had different perspectives"
    )
    how_user_priority_influenced_debate: str = Field(
        ..., description="How the user's most important factor shaped the discussion and consensus"
    )
    consensus_reached: str = Field(
        ..., description="The final consensus the team reached through discussion"
    )
    debate_highlights: List[str] = Field(
        ..., description="Notable moments or insights from the collaborative discussion"
    )


class FinalRecommendation(BaseModel):
    """Final recommendation with justification"""
    recommendation: str = Field(
        ..., description="Clear recommendation (e.g., 'Recommend moving', 'Recommend staying', 'More research needed')"
    )
    confidence_level: str = Field(
        ..., description="Confidence level in the recommendation (High/Medium/Low)"
    )
    key_supporting_factors: List[str] = Field(
        ..., description="Key factors supporting the recommendation"
    )
    key_concerns: List[str] = Field(
        ..., description="Key concerns or potential risks"
    )
    financial_impact_summary: str = Field(
        ..., description="Summary of expected financial impact"
    )
    lifestyle_impact_summary: str = Field(
        ..., description="Summary of expected lifestyle impact"
    )
    alignment_with_user_priority: str = Field(
        ..., description="How well the recommendation aligns with what the user values most"
    )
    debate_summary: DebateSummary = Field(...)  # No description on nested model fields
    next_steps: List[str] = Field(
        ..., description="Suggested next steps for the user"
    )
    detailed_justification: str = Field(
        ..., description="Detailed explanation of the recommendation based on collaborative discussion"
    )


# ============================================================================
# Custom Tools
# ============================================================================

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


# ============================================================================
# Specialized Sub-Agents (Cooperation Mode)
# ============================================================================

cost_analyst = Agent(
    name="Cost Analyst",
    model=OpenAIChat("gpt-5-mini"),
    role="Analyzes cost of living differences between cities with emphasis on user's priority",
    description=(
        "You are a financial analyst specializing in cost of living comparisons. "
        "You participate in collaborative discussions with other agents to reach consensus. "
        "While you provide cost analysis expertise, you must always consider and defer to "
        "the user's most important factor, even if the financial data suggests a different perspective."
    ),
    instructions=[
        "You are participating in a COLLABORATIVE DEBATE with other specialists",
        "CRITICAL: Always consider the user's MOST IMPORTANT FACTOR in your analysis",
        "If the user prioritizes something other than cost (e.g., culture, job opportunities), acknowledge this",
        "Be willing to adjust your recommendation based on what the user values most",
        "Even if the cost data suggests one decision, defer to user priorities if they conflict",
        "",
        "FORMAT YOUR RESPONSE:",
        "- Start with: '💰 COST ANALYST - [Brief summary of your findings]'",
        "- This helps users see the debate flow in real-time",
        "",
        "Your role in the debate:",
        "- Provide factual cost of living analysis using real data",
        "- FIRST: Use the get_cost_of_living_comparison function to fetch real data",
        "- Extract specific metrics: overall cost difference %, housing, transportation, food, taxes",
        "- Discuss how financial factors support or contradict the user's main priority",
        "- Listen to other agents' perspectives and find common ground",
        "- Be open to changing your position based on the user's stated values",
        "",
        "During discussion:",
        "- Present your cost analysis clearly",
        "- Acknowledge when financial concerns should take a backseat to user priorities",
        "- Work toward consensus that respects what the user values most",
        "- If cost is NOT the user's priority, frame your analysis as supporting information, not the deciding factor",
    ],
    tools=[get_cost_of_living_comparison],
    output_schema=CostAnalysis,
    markdown=True,
    add_name_to_context=True,
)

sentiment_analyst = Agent(
    name="Sentiment Analyst",
    model=OpenAIChat("gpt-5-mini"),
    role="Researches city vibe, culture, and livability with emphasis on user's priority",
    description=(
        "You are a city culture and livability expert participating in collaborative discussions. "
        "While you provide lifestyle and cultural analysis, you must always consider and defer to "
        "the user's most important factor, even if lifestyle factors suggest a different perspective."
    ),
    instructions=[
        "You are participating in a COLLABORATIVE DEBATE with other specialists",
        "CRITICAL: Always consider the user's MOST IMPORTANT FACTOR in your analysis",
        "If the user prioritizes something other than lifestyle (e.g., cost, job market), acknowledge this",
        "Be willing to adjust your recommendation based on what the user values most",
        "Even if lifestyle factors suggest one decision, defer to user priorities if they conflict",
        "",
        "FORMAT YOUR RESPONSE:",
        "- Start with: '🏙️ SENTIMENT ANALYST - [Brief summary of your findings]'",
        "- This helps users see the debate flow in real-time",
        "",
        "Your role in the debate:",
        "- Analyze the overall vibe, culture, and livability of the destination city",
        "- Assess how well the city matches the user's stated preferences",
        "- Identify notable pros and cons about city life",
        "- Discuss how lifestyle factors support or contradict the user's main priority",
        "- Listen to other agents' perspectives and find common ground",
        "- Be open to changing your position based on the user's stated values",
        "",
        "During discussion:",
        "- Present your lifestyle and cultural analysis clearly",
        "- Acknowledge when lifestyle factors should take a backseat to user priorities",
        "- Work toward consensus that respects what the user values most",
        "- If lifestyle is NOT the user's priority, frame your analysis as supporting information, not the deciding factor",
    ],
    output_schema=SentimentAnalysis,
    markdown=True,
    add_name_to_context=True,
)

migration_researcher = Agent(
    name="Migration Researcher",
    model=OpenAIChat("gpt-5-mini"),
    role="Finds real experiences from similar moves with emphasis on user's priority",
    description=(
        "You are a research specialist focused on finding real-world Reddit experiences. "
        "You participate in collaborative discussions with other agents. "
        "While you provide insights from real migration stories, you must always consider and defer to "
        "the user's most important factor, even if migration stories suggest a different perspective."
    ),
    instructions=[
        "You are participating in a COLLABORATIVE DEBATE with other specialists",
        "CRITICAL: Always consider the user's MOST IMPORTANT FACTOR in your analysis",
        "If the user prioritizes a specific factor, look for migration stories that address it",
        "Be willing to adjust your recommendation based on what the user values most",
        "Even if migration stories suggest one decision, defer to user priorities if they conflict",
        "",
        "FORMAT YOUR RESPONSE:",
        "- Start with: '📊 MIGRATION RESEARCHER - [Brief summary of your findings]'",
        "- This helps users see the debate flow in real-time",
        "",
        "Your role in the debate:",
        "- FIRST: Use search_reddit_discussions function to find real Reddit migration stories",
        "- Extract common themes, challenges, and outcomes from Reddit discussions",
        "- SPECIFICALLY highlight what Redditors say about the user's most important factor",
        "- Include direct perspectives from the Reddit discussions",
        "- Discuss how real migration experiences support or contradict the user's main priority",
        "- Listen to other agents' perspectives and find common ground",
        "- Be open to changing your position based on the user's stated values",
        "",
        "During discussion:",
        "- Present insights from real people's experiences clearly",
        "- Pay special attention to Reddit stories that mention the user's priority factor",
        "- Acknowledge when migration stories should be weighted by user priorities",
        "- Work toward consensus that respects what the user values most",
        "- If reddit discussions conflict with user priority, acknowledge the user's values take precedence",
    ],
    tools=[search_reddit_discussions],
    output_schema=MigrationInsights,
    markdown=True,
    add_name_to_context=True,
)


# ============================================================================
# Team Coordination (Cooperation Mode)
# ============================================================================

move_decision_team = Team(
    name="City Move Decision Team",
    model=OpenAIChat("gpt-5-mini"),
    members=[cost_analyst, sentiment_analyst, migration_researcher],
    tools=[LocalFileSystemTools(
        target_directory="./reports",
        default_extension="md"
    )],
    instructions=[
        "You are a discussion moderator facilitating a COLLABORATIVE DEBATE between specialists.",
        "Your role is to guide the team to reach CONSENSUS on whether the user should move.",
        "",
        "CRITICAL: The user's MOST IMPORTANT FACTOR must be the PRIMARY consideration in the debate.",
        "All agents must weight their analysis according to what the user values most.",
        "",
        "Step 1 - Information Verification:",
        "Review the user profile to ensure you have:",
        "  - Current city name",
        "  - Desired destination city name",
        "  - Financial situation (income, expenses, or budget concerns)",
        "  - City preferences or values",
        "  - MOST IMPORTANT FACTOR (what matters most to the user)",
        "",
        "If missing essential information, ask the user before proceeding.",
        "",
        "Step 2 - Initiate Collaborative Debate:",
        "ANNOUNCE: Start by announcing the debate is beginning and which agents are participating.",
        "Example: '🎭 Beginning collaborative debate with Cost Analyst, Sentiment Analyst, and Migration Researcher...'",
        "",
        "Delegate the analysis task TO ALL MEMBERS simultaneously (cooperation mode).",
        "Frame the task to emphasize the user's most important factor.",
        "Example: 'The user prioritizes [FACTOR]. Analyze this move with that priority in mind.'",
        "",
        "Step 3 - Moderate the Discussion:",
        "IMPORTANT: You must EXPLICITLY RELAY what each agent says for user visibility.",
        "",
        "As you delegate and receive responses:",
        "  1. ANNOUNCE when you're delegating: '🎭 Delegating to all agents...'",
        "  2. As EACH agent responds, REPEAT their key findings:",
        "     - '💰 Cost Analyst reports: [summary of their analysis]'",
        "     - '🏙️ Sentiment Analyst reports: [summary of their analysis]'",  
        "     - '📊 Migration Researcher reports: [summary of their analysis]'",
        "  3. DO NOT just say 'agents are analyzing' - SHOW what they found",
        "  4. Include key data points and quotes from each agent",
        "",
        "Then moderate:",
        "- Highlight areas of agreement and disagreement",
        "- Remind agents to weight their analysis by the user's stated priority",
        "- If multiple discussion rounds occur, announce each round clearly",
        "- Guide the discussion toward consensus",
        "- Call out when an agent should defer to the user's priority",
        "- Determine when the team has reached consensus",
        "",
        "Step 4 - Synthesize Consensus:",
        "ANNOUNCE when the debate has concluded and consensus is reached.",
        "Example: '✅ Consensus reached after [N] rounds of discussion...'",
        "",
        "After the debate concludes, create a comprehensive recommendation that:",
        "  - Reflects the team's consensus",
        "  - Prioritizes the user's most important factor",
        "  - Acknowledges areas where agents initially disagreed",
        "  - Shows how the user's priority influenced the final decision",
        "  - Includes a detailed debate summary",
        "",
        "Step 5 - Save Report:",
        "Save a comprehensive markdown report using write_file.",
        "IMPORTANT: Only provide the FILENAME (no path), files auto-save to reports/ folder.",
        "Filename format: '{current_city}_to_{desired_city}_cooperation_analysis.md'",
        "  - Normalize city names to lowercase with underscores",
        "  - Example: 'dallas_to_austin_cooperation_analysis.md' (NO 'reports/' prefix)",
        "",
        "The markdown report must include:",
        "  - # Title: Should You Move from {Current City} to {Desired City}?",
        "  - ## Subtitle: Collaborative Analysis with Priority: {User's Most Important Factor}",
        "  - ## Report Generated",
        "    - Date: [Date and Time]",
        "    - Analysis Type: Collaborative Multi-Agent Analysis (Cooperation Pattern)",
        "    - User Priority: {User's Most Important Factor}",
        "  - ## Executive Summary",
        "  - ## User's Most Important Factor",
        "  - ## Debate Summary (key points of agreement/disagreement, how priority influenced discussion)",
        "  - ## Financial Analysis (from Cost Analyst)",
        "  - ## Lifestyle & Culture Analysis (from Sentiment Analyst)",
        "  - ## Migration Insights (from Migration Researcher)",
        "  - ## Final Consensus Recommendation",
        "  - ## How This Recommendation Aligns with Your Priority",
        "  - ## Key Supporting Factors",
        "  - ## Key Concerns",
        "  - ## Next Steps",
        "  - ## Report Metadata",
        "    - Analysis Pattern: Cooperation (Collaborative Debate)",
        "    - Specialists Consulted: Cost Analyst, Sentiment Analyst, Migration Researcher (all in debate)",
        "    - Report File: [filename]",
        "    - Generated By: Should I Move? - City Relocation Decision Helper",
        "",
        "After saving, confirm the file was saved successfully.",
    ],
    output_schema=FinalRecommendation,
    delegate_task_to_all_members=True,  # COOPERATION MODE
    show_members_responses=False,  # We're showing them manually now
    add_member_tools_to_context=False,
    markdown=True,
)


# ============================================================================
# Main Application
# ============================================================================

def gather_user_information(debug=False):
    """Interactive session to gather user information"""
    # ANSI color codes
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    MAGENTA = '\033[95m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Display colorful banner
    print("\n")
    print(f"{CYAN}{'='*80}{RESET}")
    print(f"{BOLD}{MAGENTA}")
    print(r"   _____ _                 _     _   ___   __  __                 ___  ")
    print(r"  / ____| |               | |   | | |_ _| |  \/  | _____   _____  |__ \ ")
    print(r" | (___ | |__   ___  _   _| | __| |  | |  | |\/| |/ _ \ \ / / _ \   ) |")
    print(r"  \___ \| '_ \ / _ \| | | | |/ _` |  | |  | |  | | (_) \ V /  __/  / / ")
    print(r"  ____) | | | | (_) | |_| | | (_| | _| |_ | |  | |\___/ \_/ \___| |_|  ")
    print(r" |_____/|_| |_|\___/ \__,_|_|\__,_||_____||_|  |_|                 (_)  ")
    print(f"{RESET}")
    print(f"{GREEN}            🏙️  City Move Decision Helper (Cooperation Mode) 🌆{RESET}")
    print(f"{CYAN}{'='*80}{RESET}")
    print(f"\n{YELLOW}Welcome!{RESET} I'll help you decide whether moving to a new city is right for you.")
    print(f"\n{BOLD}In this version, my team of specialists will DEBATE and reach CONSENSUS.{RESET}")
    print(f"They'll prioritize what matters MOST to you in their discussion.\n")
    print(f"\nTo get started, tell me about your situation. You can share whatever feels")
    print(f"relevant - your current city, where you're thinking of moving, your financial")
    print(f"situation, what you value in a city, etc.\n")
    
    initial_input = input("Tell me about your move consideration: ").strip()
    
    if not initial_input:
        print("\nLet's start with the basics then.\n")
        initial_input = "I'm considering a move but haven't decided yet."
    
    # Start animation
    animation = ThinkingAnimation("Analyzing your response")
    print()
    animation.start()
    
    # Use an agent to interpret the input and ask follow-up questions
    question_agent = Agent(
        name="Question Generator",
        model=OpenAIChat("gpt-5-mini"),
        role="Asks follow-up questions to gather complete user information",
        description=(
            "You are a friendly assistant helping gather information from a user "
            "who is considering moving to a new city. Based on what they've told you, "
            "ask follow-up questions to gather missing information one at a time. "
            "Be conversational, friendly, and natural."
        ),
        instructions=[
            "Review what the user has already provided",
            "Identify what information is still missing",
            "Ask ONLY ONE question (or ONE topic with closely related sub-parts) at a time",
            "Be conversational and natural - like a friend helping them think through their decision",
            "Don't overwhelm them with multiple unrelated questions",
            "Priority order for missing information:",
            "  1. SPECIFIC current city - if they said 'New York', clarify if they mean NYC and which borough",
            "  2. SPECIFIC desired city - if they said a state, ask which city in that state",
            "  3. Financial information - ask about income AND monthly expenses together (they're related)",
            "  4. City preferences and current city opinions - what they value, like, and dislike",
            "  5. MOST IMPORTANT FACTOR - what matters MOST to them (affordability, jobs, culture, family, etc.)",
            "Examples of good single questions:",
            "  - 'When you say New York, do you mean New York City? If so, which borough (Manhattan, Brooklyn, etc.)?'",
            "  - 'Can you share your household income and typical monthly expenses? Ranges are fine.'",
            "  - 'What do you value most in a city, and what do you like/dislike about where you live now?'",
            "  - 'What's the SINGLE MOST IMPORTANT factor in your decision? (e.g., cost, job opportunities, lifestyle, family)'",
            "Don't ask for information they've already provided",
            "Keep it friendly and conversational - avoid sounding like an interrogation",
        ],
        markdown=False,
    )
    
    profile_extractor = Agent(
        name="Profile Extractor",
        model=OpenAIChat("gpt-5-mini"),
        role="Extracts complete user profile from conversation",
        description="Extract a complete UserProfile from the conversation history.",
        instructions=[
            "Extract all information from the conversation into a UserProfile",
            "Ensure current_city and desired_city are SPECIFIC city names",
            "If you have income, expenses, preferences, likes, or dislikes - include them",
            "IMPORTANT: Extract the user's MOST IMPORTANT FACTOR",
            "The most_important_factor should be ONE clear priority (e.g., 'affordability', 'career growth', 'culture', 'family proximity')",
            "Look for phrases like 'most important', 'mainly concerned about', 'biggest priority', 'key factor'",
        ],
        output_schema=UserProfile,
        markdown=False,
    )
    
    # Build conversation context
    conversation_history = f"User's initial input: {initial_input}\n\n"
    max_questions = 10  # Allow more rounds to capture most important factor
    question_count = 0
    
    # Stop animation
    animation.stop()
    print("Great! Let me ask you a few questions to understand your situation better.\n")
    
    # Helper function to check if we have comprehensive required info
    def has_comprehensive_info(history):
        """Check if conversation has comprehensive required information"""
        history_lower = history.lower()
        
        # Check for financial info
        has_income = any(term in history_lower for term in 
                        ["income", "salary", "earn", "make", "$"])
        has_expenses = any(term in history_lower for term in 
                          ["expense", "spend", "budget", "cost"])
        
        # Check for preferences info
        has_preferences = any(term in history_lower for term in 
                             ["prefer", "like", "love", "value", "important", "want", "need"])
        
        # Check for likes about current city
        has_likes = any(term in history_lower for term in 
                       ["like about", "love about", "enjoy", "appreciate", "good thing"])
        
        # Check for dislikes about current city  
        has_dislikes = any(term in history_lower for term in 
                          ["dislike", "hate", "don't like", "problem with", "issue with", "bad thing"])
        
        # Check for most important factor
        has_priority = any(term in history_lower for term in 
                          ["most important", "biggest priority", "key factor", "mainly concerned", 
                           "priority is", "matters most", "primary concern"])
        
        # Must have asked at least 3 rounds
        min_question_rounds = question_count >= 3
        
        # Require comprehensive coverage including priority
        has_financial_info = has_income or has_expenses
        has_current_city_opinion = has_likes or has_dislikes
        
        return (has_financial_info and 
                has_preferences and 
                has_current_city_opinion and 
                has_priority and  # NEW: Must have priority
                min_question_rounds)
    
    while question_count < max_questions:
        try:
            if debug:
                print(f"[DEBUG] Question iteration {question_count + 1}/{max_questions}")
                print(f"[DEBUG] Checking if we have enough information...", flush=True)
            
            # Check if we have comprehensive required information
            if has_comprehensive_info(conversation_history):
                if debug:
                    print("[DEBUG] Comprehensive info threshold met, attempting extraction...", flush=True)
                
                # Animate profile extraction
                profile_animation = ThinkingAnimation("Finalizing your profile")
                print()
                profile_animation.start()
                
                try:
                    profile = profile_extractor.run(
                        conversation_history + "\nExtract the complete UserProfile from this conversation. "
                        "Ensure current_city and desired_city are specific city names. "
                        "IMPORTANT: Extract the user's most_important_factor.",
                        stream=False
                    )
                    
                    profile_animation.stop()
                    
                    if debug:
                        print(f"[DEBUG] Extracted profile: {profile.content}")
                    
                    # Validate the profile has specific cities and priority
                    if (profile.content.current_city and 
                        profile.content.desired_city and
                        profile.content.most_important_factor and  # NEW: Must have priority
                        len(profile.content.current_city.split()) <= 4 and
                        len(profile.content.desired_city.split()) <= 4):
                        
                        if debug:
                            print("[DEBUG] Profile validation passed!")
                        return profile.content
                    else:
                        if debug:
                            print("[DEBUG] Profile validation failed - missing critical info")
                except Exception as e:
                    profile_animation.stop()
                    if debug:
                        print(f"[DEBUG] Extraction failed: {e}")
            
            # Need more info - generate questions
            if debug:
                print("[DEBUG] Need more information, generating questions...", flush=True)
            
            question_prompt = (
                conversation_history + 
                "\nBased on the conversation so far, what is the MOST IMPORTANT piece of missing information? "
                "Ask ONE question (or ONE topic with closely related sub-parts) to gather it.\n\n"
                "Priority order:\n"
                "1. If cities are vague, clarify to get SPECIFIC city/borough\n"
                "2. If no financial info, ask about income AND expenses together\n"
                "3. If no preferences, ask what they value AND what they like/dislike about current city\n"
                "4. If no MOST IMPORTANT FACTOR mentioned, ask what matters MOST to them in this decision\n\n"
                "IMPORTANT: Ask only ONE question. Don't bundle multiple unrelated topics.\n"
                "Be natural and conversational.\n"
                "Don't repeat information they've already provided.\n\n"
                "Just provide the question to ask - nothing else."
            )
            
            # Animate question generation
            question_animation = ThinkingAnimation("Thinking")
            print()
            question_animation.start()
            
            question_response = question_agent.run(question_prompt, stream=False)
            
            question_animation.stop()
            
            if debug:
                print(f"[DEBUG] Question response: {question_response.content}")
            
            # Ask the question
            print(f"\n{question_response.content}\n")
            user_answer = input("You: ").strip()
            
            if not user_answer:
                user_answer = "I'd prefer not to answer that."
            
            conversation_history += f"Assistant: {question_response.content}\n"
            conversation_history += f"User: {user_answer}\n\n"
            question_count += 1
            
            if debug:
                print(f"[DEBUG] User answered, moving to next iteration\n")
            
        except Exception as e:
            if debug:
                print(f"[DEBUG] Exception occurred: {e}")
            print(f"\nLet me work with what we have...\n")
            break
    
    # Final attempt to extract profile with whatever we have
    try:
        if debug:
            print("[DEBUG] Making final attempt to extract profile...", flush=True)
        
        # Animate final processing
        final_animation = ThinkingAnimation("Processing your information")
        print()
        final_animation.start()
        
        final_response = profile_extractor.run(
            conversation_history + 
            "\nExtract the UserProfile from all available information. "
            "For current_city and desired_city, use the most specific city names mentioned. "
            "For most_important_factor, identify what the user cares about most. "
            "If not explicitly stated, infer from context (e.g., if they emphasize budget, use 'affordability').",
            stream=False
        )
        
        final_animation.stop()
        return final_response.content
    except Exception as e:
        try:
            final_animation.stop()
        except:
            pass
        if debug:
            print(f"[DEBUG] Final extraction failed: {e}")
        print(f"Error gathering information: {e}")
        print("Using default profile...")
        return UserProfile(
            current_city="Unknown City",
            desired_city="Unknown Destination",
            annual_income=None,
            monthly_expenses=None,
            city_preferences=["general livability"],
            current_city_likes=["some aspects"],
            current_city_dislikes=["some aspects"],
            most_important_factor="overall quality of life"
        )


def main():
    """Main application flow"""
    # Check for debug mode
    import sys
    debug = "--debug" in sys.argv
    
    if debug:
        print("[DEBUG MODE ENABLED]")
        print("="*80)
    
    # Gather user information
    user_profile = gather_user_information(debug=debug)
    
    # ANSI color codes
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    print(f"\n{CYAN}{'='*80}{RESET}")
    print(f"{BOLD}{BLUE}🎯 Starting Collaborative Debate{RESET}")
    print(f"{CYAN}{'='*80}{RESET}")
    print(f"\n{GREEN}Current City:{RESET} {BOLD}{user_profile.current_city}{RESET}")
    print(f"{YELLOW}Considering:{RESET} {BOLD}{user_profile.desired_city}{RESET}")
    print(f"{MAGENTA}Your Priority:{RESET} {BOLD}{user_profile.most_important_factor or 'Not specified'}{RESET}")
    print(f"\n{BLUE}My team of specialists will now DEBATE this move together...{RESET}")
    print(f"{BLUE}They'll prioritize what matters MOST to you: {BOLD}{user_profile.most_important_factor}{RESET}")
    print(f"\n{CYAN}{'-'*80}{RESET}\n")
    
    # Prepare the context for the team
    income_str = f"${user_profile.annual_income:,.2f}" if user_profile.annual_income else "Not specified"
    expenses_str = f"${user_profile.monthly_expenses:,.2f}" if user_profile.monthly_expenses else "Not specified"
    preferences_str = ', '.join(user_profile.city_preferences) if user_profile.city_preferences else 'Not specified'
    likes_str = ', '.join(user_profile.current_city_likes) if user_profile.current_city_likes else 'Not specified'
    dislikes_str = ', '.join(user_profile.current_city_dislikes) if user_profile.current_city_dislikes else 'Not specified'
    priority_str = user_profile.most_important_factor or "overall quality of life"
    
    context = f"""
User Profile:
- Current City: {user_profile.current_city}
- Desired City: {user_profile.desired_city}
- Annual Income: {income_str}
- Monthly Expenses: {expenses_str}
- City Preferences: {preferences_str}
- Likes About Current City: {likes_str}
- Dislikes About Current City: {dislikes_str}
- MOST IMPORTANT FACTOR: {priority_str}

CRITICAL: The user's MOST IMPORTANT FACTOR is "{priority_str}".
All agents must weight their analysis and recommendations according to this priority.
Even if an agent's data suggests one direction, they must defer to the user's stated priority.

Please initiate a collaborative debate where all three specialists (Cost Analyst, Sentiment Analyst, 
Migration Researcher) analyze this move simultaneously and reach consensus.

The debate should:
1. Consider each specialist's perspective
2. PRIORITIZE the user's most important factor: "{priority_str}"
3. Reach consensus on whether the user should move
4. Document areas of agreement and disagreement
5. Show how the user's priority influenced the final recommendation
"""
    
    # Run the team analysis in cooperation mode with visible agent responses
    print(f"\n{MAGENTA}{'▼'*80}{RESET}")
    print(f"{BOLD}{MAGENTA}🗣️  AGENT DEBATE IN PROGRESS{RESET}")
    print(f"{MAGENTA}{'▼'*80}{RESET}\n")
    
    # Manually orchestrate agents to show their contributions
    print(f"{BLUE}🎭 Team Moderator: Delegating analysis to all specialists...{RESET}\n")
    
    # Prepare task for agents
    agent_task = f"""
The user is considering moving from {user_profile.current_city} to {user_profile.desired_city}.

Key user profile:
- Current City: {user_profile.current_city}
- Desired City: {user_profile.desired_city}
- Annual Income: {income_str}
- Monthly Expenses: {expenses_str}
- Preferences: {preferences_str}
- Likes about current city: {likes_str}
- Dislikes: {dislikes_str}
- MOST IMPORTANT FACTOR: {priority_str} — prioritize and weight every part of your analysis by {priority_str} above all else.

Task: Analyze this move with {priority_str} as the primary lens. Provide your complete structured analysis.
Remember: The user's MOST IMPORTANT FACTOR is {priority_str}. Weight all advice accordingly.
"""
    
    # Run each agent and display their output
    agent_results = {}
    
    # Cost Analyst
    print(f"{GREEN}{'─'*80}{RESET}")
    print(f"{BOLD}💰 COST ANALYST{RESET}")
    print(f"{GREEN}{'─'*80}{RESET}")
    cost_result = cost_analyst.run(agent_task, stream=False)
    if hasattr(cost_result, 'content'):
        agent_results['cost'] = cost_result.content
        print(f"\n{CYAN}Key Finding:{RESET} {cost_result.content.overall_cost_difference}")
        print(f"{CYAN}Housing:{RESET} {cost_result.content.housing_comparison}")
        print(f"{CYAN}Priority Perspective:{RESET} {cost_result.content.perspective_on_user_priority}\n")
    
    # Sentiment Analyst
    print(f"{GREEN}{'─'*80}{RESET}")
    print(f"{BOLD}🏙️  SENTIMENT ANALYST{RESET}")
    print(f"{GREEN}{'─'*80}{RESET}")
    sentiment_result = sentiment_analyst.run(agent_task, stream=False)
    if hasattr(sentiment_result, 'content'):
        agent_results['sentiment'] = sentiment_result.content
        print(f"\n{CYAN}Overall Sentiment:{RESET} {sentiment_result.content.overall_sentiment}")
        print(f"{CYAN}Livability:{RESET} {sentiment_result.content.livability_score}")
        print(f"{CYAN}Priority Perspective:{RESET} {sentiment_result.content.perspective_on_user_priority}\n")
    
    # Migration Researcher
    print(f"{GREEN}{'─'*80}{RESET}")
    print(f"{BOLD}📊 MIGRATION RESEARCHER{RESET}")
    print(f"{GREEN}{'─'*80}{RESET}")
    migration_result = migration_researcher.run(agent_task, stream=False)
    if hasattr(migration_result, 'content'):
        agent_results['migration'] = migration_result.content
        print(f"\n{CYAN}Reddit Sources:{RESET} {migration_result.content.number_of_sources} discussions")
        print(f"{CYAN}Summary:{RESET} {migration_result.content.summary[:200]}...")
        print(f"{CYAN}Priority Perspective:{RESET} {migration_result.content.perspective_on_user_priority}\n")
    
    # Now have the team synthesize
    print(f"\n{BLUE}{'═'*80}{RESET}")
    print(f"{BOLD}{BLUE}🎯 TEAM MODERATOR: Synthesizing Consensus & Creating Report{RESET}")
    print(f"{BLUE}{'═'*80}{RESET}\n")
    
    synthesis_context = f"""
{context}

AGENT FINDINGS:

Cost Analyst Analysis:
{agent_results.get('cost', 'Not available')}

Sentiment Analyst Analysis:
{agent_results.get('sentiment', 'Not available')}

Migration Researcher Analysis:
{agent_results.get('migration', 'Not available')}

Now synthesize these findings into a final consensus recommendation that:
1. Reflects the team's collective insights
2. Prioritizes the user's most important factor: {priority_str}
3. Includes a debate summary showing agreement/disagreement
4. Provides actionable next steps
"""
    
    move_decision_team.print_response(input=synthesis_context, stream=True)
    
    print(f"\n{MAGENTA}{'▲'*80}{RESET}")
    print(f"{BOLD}{MAGENTA}🗣️  AGENT DEBATE COMPLETE{RESET}")
    print(f"{MAGENTA}{'▲'*80}{RESET}\n")
    
    print(f"\n{CYAN}{'='*80}{RESET}")
    print(f"{BOLD}{GREEN}✅ Collaborative analysis complete! Thank you for using Should I Move?{RESET}")
    print(f"{CYAN}{'='*80}{RESET}\n")


if __name__ == "__main__":
    main()


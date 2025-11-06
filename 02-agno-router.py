from typing import List, Optional
import os
import re
import json
import time
import threading
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
    """Captures user's move decision info"""
    current_city: str = Field(..., description="The city the user currently lives in")
    desired_city: str = Field(..., description="The city the user is considering moving to")
    primary_concern: str = Field(
        ..., 
        description="The single most important factor in their decision (cost, culture, or experiences)"
    )
    additional_context: Optional[str] = Field(
        None, 
        description="Any additional context about their situation"
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
    recommendation: str = Field(
        ..., description="Recommendation specifically focused on financial factors"
    )


class SentimentAnalysis(BaseModel):
    """City vibe and livability analysis"""
    overall_sentiment: str = Field(
        ..., description="Overall sentiment about the city (positive/mixed/negative)"
    )
    vibe_description: str = Field(..., description="General vibe and culture of the city")
    livability_score: str = Field(..., description="Assessment of livability")
    notable_pros: List[str] = Field(..., description="Notable positive aspects")
    notable_cons: List[str] = Field(..., description="Notable negative aspects")
    recommendation: str = Field(
        ..., description="Recommendation specifically focused on lifestyle and culture factors"
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
    recommendation: str = Field(
        ..., description="Recommendation based on real experiences from people who made this move"
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

Provide a clear recommendation focused on the financial aspects of this move.
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
# Specialized Sub-Agents
# ============================================================================

cost_analyst = Agent(
    name="Cost Analyst",
    model=OpenAIChat("gpt-4o-mini"),
    role="Analyzes cost of living differences between cities",
    description=(
        "You are a financial analyst specializing in cost of living comparisons. "
        "Analyze the cost differences between the user's current city and their desired city. "
        "You have access to real-time cost of living data from NerdWallet. "
        "Use the get_cost_of_living_comparison function to fetch actual data, then analyze it. "
        "Provide a clear recommendation focused on financial considerations."
    ),
    instructions=[
        "FIRST: Use the get_cost_of_living_comparison function to fetch real cost of living data",
        "Extract specific metrics from the data: overall cost difference %, housing, transportation, food, entertainment, healthcare",
        "Provide a comprehensive cost of living analysis based on the real data",
        "Compare housing costs (rent/mortgage, utilities) with specific numbers",
        "Compare food and grocery costs with specific percentages or dollar amounts",
        "Compare transportation costs (public transit, car ownership, gas)",
        "Compare tax implications (state/local taxes)",
        "Provide a clear RECOMMENDATION in the 'recommendation' field about whether the move makes financial sense",
        "Be specific and actionable in your recommendation",
        "If the tool fails, fall back to general knowledge but note this in your analysis"
    ],
    tools=[get_cost_of_living_comparison],
    output_schema=CostAnalysis,
    markdown=True,
)

sentiment_analyst = Agent(
    name="Sentiment Analyst",
    model=OpenAIChat("gpt-4o-mini"),
    role="Researches city vibe, culture, and livability",
    description=(
        "You are a city culture and livability expert. "
        "Research and analyze the general vibe, culture, and livability of the destination city. "
        "Provide insights based on your knowledge of the city's culture, lifestyle, and character. "
        "Give a clear recommendation focused on lifestyle and cultural fit."
    ),
    instructions=[
        "Analyze the overall vibe and culture of the destination city",
        "Assess livability factors like walkability, public spaces, community feel",
        "Identify notable pros and cons of living in this city",
        "Consider factors like: arts/culture scene, outdoor activities, social atmosphere, diversity, food scene",
        "Compare the destination city's vibe to the current city if you have context",
        "Provide a clear RECOMMENDATION in the 'recommendation' field about whether the move makes sense from a lifestyle/culture perspective",
        "Be specific and actionable in your recommendation",
        "Use your general knowledge of these cities"
    ],
    output_schema=SentimentAnalysis,
    markdown=True,
)

migration_researcher = Agent(
    name="Migration Researcher",
    model=OpenAIChat("gpt-4o-mini"),
    role="Finds and summarizes experiences from people who made similar moves",
    description=(
        "You are a research specialist focused on finding real-world experiences from Reddit. "
        "You use Brave Search to find Reddit discussions about people who moved from the user's current city to their desired city. "
        "Extract common themes, challenges, and outcomes from these migration stories. "
        "Provide a clear recommendation based on what real people experienced."
    ),
    instructions=[
        "FIRST: Use the search_reddit_discussions function with the current_city and desired_city",
        "The function will automatically search Reddit using multiple query variations via Brave Search",
        "It returns formatted Reddit discussion results including titles, URLs, and descriptions",
        "Analyze the returned Reddit discussions to extract insights",
        "SPECIFICALLY call out what Redditors are saying in the 'redditor_perspectives' field",
        "Include direct themes, common sentiments, or representative perspectives from the discussions",
        "Identify common reasons people gave for moving from the Reddit results",
        "Highlight common challenges mentioned in the discussions",
        "Report common positive outcomes from the Reddit threads",
        "Note any regrets or warnings shared by Redditors who made this move",
        "Set 'reddit_insights_included' to True if Reddit data was successfully retrieved",
        "Set 'number_of_sources' to the count of Reddit discussions found",
        "Provide a clear RECOMMENDATION in the 'recommendation' field based on what real people experienced",
        "Be specific and actionable in your recommendation",
        "If the function returns an error or no results, set 'reddit_insights_included' to False and use general knowledge"
    ],
    tools=[search_reddit_discussions],
    output_schema=MigrationInsights,
    markdown=True,
)


# ============================================================================
# Router Team
# ============================================================================

move_decision_router = Team(
    name="City Move Decision Router",
    model=OpenAIChat("gpt-4o-mini"),
    members=[cost_analyst, sentiment_analyst, migration_researcher],
    respond_directly=True,
    instructions=[
        "You are a router that directs move decision questions to the most appropriate specialist.",
        "",
        "Based on the user's PRIMARY CONCERN, route to the appropriate agent:",
        "  - If they care most about COST/FINANCES/AFFORDABILITY → route to Cost Analyst",
        "  - If they care most about CULTURE/LIFESTYLE/VIBE → route to Sentiment Analyst",
        "  - If they care most about REAL EXPERIENCES/WHAT OTHERS SAY → route to Migration Researcher",
        "",
        "The user will specify their primary concern. Use that to make your routing decision.",
        "",
        "If the primary concern is unclear or mentions multiple factors equally:",
        "  - Default to Cost Analyst if any financial mention exists",
        "  - Otherwise default to Sentiment Analyst",
        "",
        "DO NOT respond yourself - always delegate to exactly ONE specialist agent.",
        "The specialist will provide their analysis and recommendation directly to the user.",
    ],
    markdown=True,
    show_members_responses=True,
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
    print(f"{GREEN}                    🏙️  City Relocation Decision Helper 🌆{RESET}")
    print(f"{CYAN}{'='*80}{RESET}")
    print(f"\n{YELLOW}Welcome!{RESET} I'll connect you with a specialist to help with your move decision.")
    print(f"\nLet me ask you a few quick questions:\n")
    
    # Ask for current city
    current_city = input(f"{BLUE}What city do you currently live in?{RESET} ").strip()
    while not current_city:
        current_city = input(f"{YELLOW}Please enter your current city:{RESET} ").strip()
    
    # Ask for desired city
    desired_city = input(f"{BLUE}What city are you considering moving to?{RESET} ").strip()
    while not desired_city:
        desired_city = input(f"{YELLOW}Please enter the city you're considering:{RESET} ").strip()
    
    # Ask for primary concern
    print(f"\n{BLUE}What is the SINGLE MOST IMPORTANT factor in your decision?{RESET}")
    print(f"  {GREEN}1.{RESET} Cost of living and financial impact")
    print(f"  {GREEN}2.{RESET} City culture, vibe, and lifestyle")
    print(f"  {GREEN}3.{RESET} Real experiences from people who made this move")
    
    concern_map = {
        "1": "cost",
        "2": "culture", 
        "3": "experiences"
    }
    
    concern_choice = input(f"\n{BLUE}Enter 1, 2, or 3:{RESET} ").strip()
    while concern_choice not in concern_map:
        concern_choice = input(f"{YELLOW}Please enter 1, 2, or 3:{RESET} ").strip()
    
    primary_concern = concern_map[concern_choice]
    
    # Ask for additional context
    print(f"\n{BLUE}Any additional context about your situation?{RESET} (or press Enter to skip)")
    additional_context = input(f"{BLUE}>{RESET} ").strip()
    
    return UserProfile(
        current_city=current_city,
        desired_city=desired_city,
        primary_concern=primary_concern,
        additional_context=additional_context if additional_context else None
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
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    print(f"\n{CYAN}{'='*80}{RESET}")
    print(f"{BOLD}{BLUE}🎯 Routing to Specialist{RESET}")
    print(f"{CYAN}{'='*80}{RESET}")
    print(f"\n{GREEN}Current City:{RESET} {BOLD}{user_profile.current_city}{RESET}")
    print(f"{YELLOW}Considering:{RESET} {BOLD}{user_profile.desired_city}{RESET}")
    print(f"{BLUE}Primary Concern:{RESET} {BOLD}{user_profile.primary_concern.title()}{RESET}")
    print(f"\n{BLUE}Connecting you with the best specialist for your question...{RESET}")
    print(f"\n{CYAN}{'-'*80}{RESET}\n")
    
    # Prepare the context for the router
    context = f"""
User Profile:
- Current City: {user_profile.current_city}
- Desired City: {user_profile.desired_city}
- Primary Concern: {user_profile.primary_concern}
- Additional Context: {user_profile.additional_context or 'None provided'}

The user is considering moving from {user_profile.current_city} to {user_profile.desired_city}.
Their primary concern is: {user_profile.primary_concern}

Route this to the appropriate specialist agent based on their primary concern.
"""
    
    # Run the router (it will delegate to the appropriate agent) and capture response
    response = move_decision_router.run(input=context, stream=False)
    
    # Display the response
    print(f"\n{response.content}\n")
    
    # Generate and save report
    print(f"\n{BLUE}📝 Generating report...{RESET}")
    
    # Normalize city names for filename
    current_city_normalized = re.sub(r'[^a-z0-9]', '_', user_profile.current_city.lower()).strip('_')
    desired_city_normalized = re.sub(r'[^a-z0-9]', '_', user_profile.desired_city.lower()).strip('_')
    
    # Create timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create filename
    filename = f"{current_city_normalized}_to_{desired_city_normalized}_{timestamp}_router_analysis.md"
    
    # Determine specialist type based on primary concern
    specialist_map = {
        "cost": "Financial Analysis",
        "culture": "Lifestyle & Culture Analysis",
        "experiences": "Migration Experiences Analysis"
    }
    analysis_type = specialist_map.get(user_profile.primary_concern, "Analysis")
    
    # Generate report content
    report_content = f"""# Should You Move from {user_profile.current_city} to {user_profile.desired_city}?

## Report Generated
**Date:** {datetime.now().strftime("%B %d, %Y at %I:%M %p")}  
**Analysis Type:** {analysis_type} (Router Pattern)  
**Primary Concern:** {user_profile.primary_concern.title()}

---

## User Profile

- **Current City:** {user_profile.current_city}
- **Desired City:** {user_profile.desired_city}
- **Primary Concern:** {user_profile.primary_concern.title()}
- **Additional Context:** {user_profile.additional_context or 'None provided'}

---

## Specialist Analysis

This analysis was generated using the **Router Pattern**, where your question was directed to the most appropriate specialist based on your primary concern.

{response.content}

---

## Report Metadata

- **Analysis Pattern:** Router (Single Specialist)
- **Specialist Consulted:** {analysis_type}
- **Report File:** `{filename}`
- **Generated By:** Should I Move? - City Relocation Decision Helper

---

*This report was generated by an AI-powered analysis system. Please use this as one input in your decision-making process and verify all information independently.*
"""
    
    # Save report to file
    try:
        report_path = os.path.join("reports", filename)
        os.makedirs("reports", exist_ok=True)
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        
        print(f"{GREEN}✅ Report saved successfully!{RESET}")
        print(f"{CYAN}   📄 Location: {report_path}{RESET}")
    except Exception as e:
        print(f"{YELLOW}⚠️  Could not save report: {e}{RESET}")
    
    print(f"\n{CYAN}{'='*80}{RESET}")
    print(f"{BOLD}{GREEN}✅ Analysis complete! Thank you for using Should I Move?{RESET}")
    print(f"{CYAN}{'='*80}{RESET}\n")


if __name__ == "__main__":
    main()


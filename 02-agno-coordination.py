from typing import List, Optional
import os
import re
import json
import time
import threading
from dotenv import load_dotenv
from difflib import get_close_matches

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.team.team import Team
from agno.tools.firecrawl import FirecrawlTools
from pydantic import BaseModel, Field

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


class MigrationInsights(BaseModel):
    """Insights from people who made similar moves"""
    number_of_sources: int = Field(..., description="Number of migration stories analyzed")
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
    next_steps: List[str] = Field(
        ..., description="Suggested next steps for the user"
    )
    detailed_justification: str = Field(
        ..., description="Detailed explanation of the recommendation based on all sub-agent inputs"
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
# Specialized Sub-Agents
# ============================================================================

cost_analyst = Agent(
    name="Cost Analyst",
    model=OpenAIChat("gpt-5-mini"),
    role="Analyzes cost of living differences between cities",
    description=(
        "You are a financial analyst specializing in cost of living comparisons. "
        "Analyze the cost differences between the user's current city and their desired city. "
        "You have access to real-time cost of living data from NerdWallet. "
        "Use the get_cost_of_living_comparison function to fetch actual data, then analyze it."
    ),
    instructions=[
        "FIRST: Use the get_cost_of_living_comparison function to fetch real cost of living data",
        "Extract specific metrics from the data: overall cost difference %, housing, transportation, food, entertainment, healthcare",
        "Provide a comprehensive cost of living analysis based on the real data",
        "Compare housing costs (rent/mortgage, utilities) with specific numbers",
        "Compare food and grocery costs with specific percentages or dollar amounts",
        "Compare transportation costs (public transit, car ownership, gas)",
        "Compare tax implications (state/local taxes)",
        "Provide practical insights about the financial impact using the real data",
        "If the tool fails, fall back to general knowledge but note this in your analysis"
    ],
    tools=[get_cost_of_living_comparison],
    output_schema=CostAnalysis,
    markdown=True,
)

sentiment_analyst = Agent(
    name="Sentiment Analyst",
    model=OpenAIChat("gpt-5-mini"),
    role="Researches city vibe, culture, and livability",
    description=(
        "You are a city culture and livability expert. "
        "Research and analyze the general vibe, culture, and livability of the destination city. "
        "Consider the user's stated preferences when providing your analysis. "
        "For now, provide generic insights based on common knowledge about the city. "
        "Later, you will use real web scraping tools to analyze articles and reviews."
    ),
    instructions=[
        "Analyze the overall vibe and culture of the destination city",
        "Assess livability based on the user's preferences",
        "Identify notable pros and cons",
        "Provide insights on how well the city matches user preferences",
        "Consider factors like: arts/culture scene, outdoor activities, social atmosphere, diversity, food scene",
        "Note: Use your general knowledge for now; real sentiment analysis tools will be added later"
    ],
    output_schema=SentimentAnalysis,
    markdown=True,
)

migration_researcher = Agent(
    name="Migration Researcher",
    model=OpenAIChat("gpt-5-mini"),
    role="Finds and summarizes experiences from people who made similar moves",
    description=(
        "You are a research specialist focused on finding real-world experiences. "
        "Find and summarize stories from people who moved from the user's current city to their desired city. "
        "Extract common themes, challenges, and outcomes from these migration stories. "
        "For now, provide generic placeholder insights based on typical migration patterns. "
        "Later, you will use real web scraping tools to find blog posts and Reddit discussions."
    ),
    instructions=[
        "Summarize experiences from people who made similar moves",
        "Identify common reasons people gave for moving",
        "Highlight common challenges faced during/after the move",
        "Report common positive outcomes",
        "Note any regrets or warnings from those who made the move",
        "Provide a balanced summary of migration experiences",
        "Note: Use your general knowledge for now; real blog/Reddit scraping tools will be added later"
    ],
    output_schema=MigrationInsights,
    markdown=True,
)


# ============================================================================
# Team Coordination
# ============================================================================

move_decision_team = Team(
    name="City Move Decision Team",
    model=OpenAIChat("gpt-5-mini"),
    members=[cost_analyst, sentiment_analyst, migration_researcher],
    instructions=[
        "You are a coordinator helping users decide whether to move to a new city.",
        "",
        "CRITICAL: Do NOT delegate to any sub-agents until you have confirmed you have all necessary information.",
        "",
        "Step 1 - Information Verification:",
        "First, review the user profile information provided to you.",
        "Check if you have ALL of the following essential information:",
        "  - Current city name",
        "  - Desired destination city name",
        "  - At least SOME information about their financial situation (income, expenses, or general budget concerns)",
        "  - At least SOME information about their city preferences or what they value",
        "",
        "If you are missing any essential information above, you MUST:",
        "  - Ask the user to provide the missing information",
        "  - Wait for their response",
        "  - Do NOT proceed to Step 2 until you have this information",
        "",
        "Step 2 - Delegate to Sub-Agents (ONLY after Step 1 is complete):",
        "Once you have confirmed you have all necessary information, proceed with delegation:",
        "  - First, delegate to the Cost Analyst to analyze the cost of living differences",
        "  - Then, delegate to the Sentiment Analyst to research the city's vibe and livability",
        "  - Then, delegate to the Migration Researcher to find experiences from similar moves",
        "",
        "Step 3 - Synthesize Results:",
        "After receiving all three analyses, synthesize the information into a clear recommendation.",
        "Provide a balanced assessment considering financial, lifestyle, and experiential factors.",
        "Be honest about uncertainties and suggest next steps for further research.",
    ],
    output_schema=FinalRecommendation,
    add_member_tools_to_context=False,
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
    print(f"\n{YELLOW}Welcome!{RESET} I'll help you decide whether moving to a new city is right for you.")
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
    # Note: We'll use this agent WITHOUT output_schema first to ask questions,
    # then WITH output_schema to extract the final profile
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
            "Examples of good single questions:",
            "  - 'When you say New York, do you mean New York City? If so, which borough (Manhattan, Brooklyn, etc.)?'",
            "  - 'Can you share your household income and typical monthly expenses? Ranges are fine.'",
            "  - 'What do you value most in a city, and what do you like/dislike about where you live now?'",
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
        ],
        output_schema=UserProfile,
        markdown=False,
    )
    
    # Build conversation context
    conversation_history = f"User's initial input: {initial_input}\n\n"
    max_questions = 8  # Allow more rounds since we're asking one question at a time
    question_count = 0
    
    # Stop animation
    animation.stop()
    print("Great! Let me ask you a few questions to understand your situation better.\n")
    
    # Helper function to check if we have comprehensive required info
    def has_comprehensive_info(history):
        """Check if conversation has comprehensive required information"""
        history_lower = history.lower()
        
        # Check for financial info (both income AND expenses ideally)
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
        
        # Must have asked at least 3 rounds since we're asking one at a time
        min_question_rounds = question_count >= 3
        
        # Require comprehensive coverage:
        # - At least one financial metric (income OR expenses)
        # - Preferences about what they value
        # - At least one of likes/dislikes about current city
        # - At least 2 rounds of questions asked
        
        has_financial_info = has_income or has_expenses
        has_current_city_opinion = has_likes or has_dislikes
        
        return (has_financial_info and 
                has_preferences and 
                has_current_city_opinion and 
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
                        "Ensure current_city and desired_city are specific city names.",
                        stream=False
                    )
                    
                    profile_animation.stop()
                    
                    if debug:
                        print(f"[DEBUG] Extracted profile: {profile.content}")
                    
                    # Validate the profile has specific cities (not vague)
                    if (profile.content.current_city and 
                        profile.content.desired_city and
                        len(profile.content.current_city.split()) <= 4 and  # Not a long explanation
                        len(profile.content.desired_city.split()) <= 4):  # Not a long explanation
                        
                        if debug:
                            print("[DEBUG] Profile validation passed!")
                        return profile.content
                    else:
                        if debug:
                            print("[DEBUG] Profile validation failed - cities not specific enough")
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
                "1. If cities are vague (like 'New York' or 'Florida'), clarify to get SPECIFIC city/borough\n"
                "2. If no financial info, ask about income AND expenses together (since they're related)\n"
                "3. If no preferences, ask what they value AND what they like/dislike about current city\n\n"
                "IMPORTANT: Ask only ONE question. Don't bundle multiple unrelated topics.\n"
                "Be natural and conversational, like a friend helping them think through this decision.\n"
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
            
            # Ask the questions
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
            # If there's an error, try one more time to extract what we have
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
            "If only a state was mentioned, note that in the city field but try to get a city name.",
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
            current_city_dislikes=["some aspects"]
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
    print(f"{BOLD}{BLUE}📊 Analyzing Your Move Decision{RESET}")
    print(f"{CYAN}{'='*80}{RESET}")
    print(f"\n{GREEN}Current City:{RESET} {BOLD}{user_profile.current_city}{RESET}")
    print(f"{YELLOW}Considering:{RESET} {BOLD}{user_profile.desired_city}{RESET}")
    print(f"\n{BLUE}I'm now consulting with specialized research agents to analyze your move...{RESET}")
    print(f"\n{CYAN}{'-'*80}{RESET}\n")
    
    # Prepare the context for the team
    income_str = f"${user_profile.annual_income:,.2f}" if user_profile.annual_income else "Not specified"
    expenses_str = f"${user_profile.monthly_expenses:,.2f}" if user_profile.monthly_expenses else "Not specified"
    preferences_str = ', '.join(user_profile.city_preferences) if user_profile.city_preferences else 'Not specified'
    likes_str = ', '.join(user_profile.current_city_likes) if user_profile.current_city_likes else 'Not specified'
    dislikes_str = ', '.join(user_profile.current_city_dislikes) if user_profile.current_city_dislikes else 'Not specified'
    
    context = f"""
User Profile:
- Current City: {user_profile.current_city}
- Desired City: {user_profile.desired_city}
- Annual Income: {income_str}
- Monthly Expenses: {expenses_str}
- City Preferences: {preferences_str}
- Likes About Current City: {likes_str}
- Dislikes About Current City: {dislikes_str}

Please analyze whether this user should move from {user_profile.current_city} to {user_profile.desired_city}.
Coordinate with all three specialist agents and provide a comprehensive recommendation.
"""
    
    # Run the team analysis
    move_decision_team.print_response(input=context, stream=True)
    
    print(f"\n{CYAN}{'='*80}{RESET}")
    print(f"{BOLD}{GREEN}✅ Analysis complete! Thank you for using Should I Move?{RESET}")
    print(f"{CYAN}{'='*80}{RESET}\n")


if __name__ == "__main__":
    main()


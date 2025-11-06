from typing import List, Optional
import os
from dotenv import load_dotenv

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.team.team import Team
from pydantic import BaseModel, Field

# Load environment variables from .env file
load_dotenv()


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
# Specialized Sub-Agents
# ============================================================================

cost_analyst = Agent(
    name="Cost Analyst",
    model=OpenAIChat("gpt-5-mini"),
    role="Analyzes cost of living differences between cities",
    description=(
        "You are a financial analyst specializing in cost of living comparisons. "
        "Analyze the cost differences between the user's current city and their desired city. "
        "Focus on housing, food, transportation, and taxes. "
        "For now, provide generic placeholder analysis based on common knowledge about these cities. "
        "Later, you will use real web scraping tools to get accurate data."
    ),
    instructions=[
        "Provide a comprehensive cost of living analysis",
        "Compare housing costs (rent/mortgage, utilities)",
        "Compare food and grocery costs",
        "Compare transportation costs (public transit, car ownership, gas)",
        "Compare tax implications (state/local taxes)",
        "Provide practical insights about the financial impact",
        "Note: Use your general knowledge for now; real data tools will be added later"
    ],
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
    
    print("\n💭 Analyzing your response...", flush=True)
    
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
            "ask follow-up questions to gather missing information. Be conversational "
            "and friendly."
        ),
        instructions=[
            "Review what the user has already provided",
            "Identify what CRITICAL information is missing:",
            "  - SPECIFIC current city name (not just a state)",
            "  - SPECIFIC desired destination city name (not just a state - must be a specific city)",
            "  - At least SOME financial information (income OR expenses OR general budget concerns)",
            "  - At least SOME preferences about what they value in a city",
            "Ask questions naturally and conversationally",
            "Don't ask for information they've already provided",
            "Focus on getting specific city names - 'Florida' is NOT specific enough",
            "If they said a state, ask which city in that state",
            "You can ask 2-3 questions at a time, but keep it manageable",
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
    max_questions = 6  # Allow more rounds to gather comprehensive info
    question_count = 0
    
    print("\nGreat! Let me ask you a few questions to understand your situation better.\n")
    
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
        
        # Must have asked at least 2 rounds of questions to be thorough
        min_question_rounds = question_count >= 2
        
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
                
                print("💭 Finalizing your profile...", flush=True)
                try:
                    profile = profile_extractor.run(
                        conversation_history + "\nExtract the complete UserProfile from this conversation. "
                        "Ensure current_city and desired_city are specific city names.",
                        stream=False
                    )
                    
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
                    if debug:
                        print(f"[DEBUG] Extraction failed: {e}")
            
            # Need more info - generate questions
            if debug:
                print("[DEBUG] Need more information, generating questions...", flush=True)
            
            question_prompt = (
                conversation_history + 
                "\nBased on the conversation so far, what information is still missing to provide a comprehensive analysis? "
                "Generate 1-3 friendly, conversational questions to ask the user. Make sure to gather:\n"
                "1. SPECIFIC city names (if they said a state, ask which city)\n"
                "2. Financial information - BOTH income AND monthly expenses if possible\n"
                "3. What they value or prioritize in a city (lifestyle, culture, activities, etc.)\n"
                "4. What they LIKE about their current city\n"
                "5. What they DISLIKE about their current city\n\n"
                "Don't ask for information already provided. Focus on filling gaps. "
                "Be friendly and conversational. Just provide the questions."
            )
            
            print("💭 Thinking...", flush=True)
            question_response = question_agent.run(question_prompt, stream=False)
            
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
        print("💭 Processing your information...", flush=True)
        final_response = profile_extractor.run(
            conversation_history + 
            "\nExtract the UserProfile from all available information. "
            "For current_city and desired_city, use the most specific city names mentioned. "
            "If only a state was mentioned, note that in the city field but try to get a city name.",
            stream=False
        )
        return final_response.content
    except Exception as e:
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


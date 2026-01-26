from typing import List, Optional
import os
import time
import threading
from dotenv import load_dotenv

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.team.team import Team
from agno.tools.local_file_system import LocalFileSystemTools

# Import agents and models from sub-agents structure
from sub_agents.schemas import UserProfile, FinalRecommendation
from sub_agents.cost_analyst.agent import cost_analyst
from sub_agents.sentiment_analyst.agent import sentiment_analyst
from sub_agents.migration_researcher.agent import migration_researcher

# Load environment variables from .env file
load_dotenv()

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
# Team Coordination
# ============================================================================

move_decision_team = Team(
    name="City Move Decision Team",
    model=OpenAIChat("gpt-4o-mini"),
    members=[cost_analyst, sentiment_analyst, migration_researcher],
    tools=[LocalFileSystemTools(
        target_directory="./reports",
        default_extension="md"
    )],
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
        "",
        "Step 4 - Save Report:",
        "After synthesizing the final recommendation, save a comprehensive markdown report using the write_file tool.",
        "IMPORTANT: Only provide the FILENAME (no path/directory), as files automatically save to the reports/ folder.",
        "The filename should be: '{current_city}_to_{desired_city}_{timestamp}_analysis.md'",
        "  - Normalize city names to lowercase with underscores, remove special characters",
        "  - Use timestamp format: YYYYMMDD_HHMMSS (e.g., 20250106_143022)",
        "  - Example filename: 'dallas_to_austin_20250106_143022_analysis.md' (NO 'reports/' prefix)",
        "The markdown report should include:",
        "  - # Title: Should You Move from {Current City} to {Desired City}?",
        "  - ## Report Generated",
        "    - Date: [Current Date and Time]",
        "    - Analysis Type: Comprehensive Multi-Agent Analysis (Coordination Pattern)",
        "  - ## Executive Summary (with your recommendation and confidence level)",
        "  - ## Financial Analysis (from Cost Analyst)",
        "  - ## Lifestyle & Culture Analysis (from Sentiment Analyst)",
        "  - ## Migration Insights (from Migration Researcher)",
        "  - ## Final Recommendation (detailed justification)",
        "  - ## Key Supporting Factors (bulleted list)",
        "  - ## Key Concerns (bulleted list)",
        "  - ## Next Steps (bulleted list)",
        "  - ## Report Metadata",
        "    - Analysis Pattern: Coordination (Sequential Multi-Agent)",
        "    - Specialists Consulted: Cost Analyst, Sentiment Analyst, Migration Researcher",
        "    - Report File: [filename]",
        "    - Generated By: Should I Move? - City Relocation Decision Helper",
        "Format it as a well-structured, professional markdown document with proper headings, bullets, and formatting.",
        "After saving, confirm the file was saved successfully with the full filename.",
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
        model=OpenAIChat("gpt-4o-mini"),
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
        model=OpenAIChat("gpt-4o-mini"),
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

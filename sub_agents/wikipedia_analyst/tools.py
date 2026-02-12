import re
from typing import Optional
from agno.tools.wikipedia import WikipediaTools

def extract_numeric_data(text: str, search_terms: list[str]) -> dict:
    """
    Extract numeric data from Wikipedia text based on search terms.
    
    Args:
        text: Wikipedia article text
        search_terms: List of terms to search for (e.g., ['population', 'density', 'median income'])
        
    Returns:
        Dictionary of found numeric data with context
    """
    results = {}
    
    # Split into sentences
    sentences = re.split(r'[.!?]', text)
    
    for term in search_terms:
        matches = []
        for sentence in sentences:
            # Check if the search term appears in this sentence
            if term.lower() in sentence.lower():
                # Look for numbers in the sentence (including percentages, currency, etc.)
                numbers = re.findall(r'[\$]?[\d,]+\.?\d*%?', sentence)
                if numbers:
                    matches.append({
                        'context': sentence.strip(),
                        'values': numbers
                    })
        
        if matches:
            results[term] = matches
    
    return results


def search_wikipedia_for_criteria(current_city: str, desired_city: str, criteria: str) -> str:
    """
    Search Wikipedia for both cities and extract numeric data relevant to user criteria.
    
    Args:
        current_city: The user's current city
        desired_city: The city the user is considering moving to
        criteria: The criteria the user cares about (e.g., 'diversity', 'weather', 'crime', 'education', 'income')
        
    Returns:
        Comparative analysis with numeric data from both cities
    """
    print(f"\n🔍 [WIKIPEDIA TOOL] Searching Wikipedia for relevant data...")
    print(f"   Current City: {current_city}")
    print(f"   Desired City: {desired_city}")
    print(f"   Criteria: {criteria}")
    print(f"   ⏳ Searching Wikipedia...\n")
    
    # Map criteria to search terms
    criteria_mapping = {
        'diversity': ['population', 'demographics', 'race', 'ethnicity', 'percent', 'percentage', 'composition'],
        'weather': ['climate', 'temperature', 'rainfall', 'precipitation', 'humidity', 'snow', 'sunny days'],
        'crime': ['crime', 'murder', 'violent', 'property crime', 'safety', 'crime rate', 'homicide'],
        'education': ['education', 'school', 'university', 'literacy', 'college', 'graduation rate', 'test scores'],
        'income': ['income', 'median household', 'per capita', 'poverty', 'salary', 'wage', 'gdp', 'economic'],
        'cost of living': ['cost', 'housing', 'rent', 'median home', 'price', 'affordable'],
        'population': ['population', 'density', 'metropolitan', 'residents', 'inhabitants'],
        'healthcare': ['hospital', 'health', 'life expectancy', 'mortality', 'healthcare', 'medical'],
        'transportation': ['transit', 'commute', 'public transport', 'traffic', 'walkability', 'bike'],
    }
    
    # Get search terms for this criteria
    criteria_lower = criteria.lower()
    search_terms = []
    
    # Find matching criteria
    for key, terms in criteria_mapping.items():
        if key in criteria_lower or any(term in criteria_lower for term in terms):
            search_terms.extend(terms)
            break
    
    # If no match, use generic terms
    if not search_terms:
        search_terms = ['population', 'demographics', 'median', 'average', 'rate', 'percent']
    
    # Remove duplicates
    search_terms = list(set(search_terms))
    
    try:
        # Initialize Wikipedia tool
        wiki_tool = WikipediaTools()
        
        # Search for current city
        print(f"📖 Searching Wikipedia for {current_city}...")
        current_city_data = wiki_tool.search_wikipedia(current_city)
        current_city_numeric = extract_numeric_data(current_city_data, search_terms)
        
        # Search for desired city
        print(f"📖 Searching Wikipedia for {desired_city}...")
        desired_city_data = wiki_tool.search_wikipedia(desired_city)
        desired_city_numeric = extract_numeric_data(desired_city_data, search_terms)
        
        print(f"✅ [WIKIPEDIA TOOL] Successfully retrieved Wikipedia data!\n")
        
        # Build the response
        response = f"""
Wikipedia Analysis - {criteria.title()}
==========================================

Current City: {current_city}
Desired City: {desired_city}
Criteria: {criteria}

NUMERIC DATA FROM {current_city.upper()}:
"""
        
        if current_city_numeric:
            for term, matches in current_city_numeric.items():
                response += f"\n{term.title()}:\n"
                for match in matches[:3]:  # Limit to top 3 matches per term
                    response += f"  • {match['context']}\n"
                    response += f"    Values found: {', '.join(match['values'])}\n"
        else:
            response += "  No numeric data found for the specified criteria.\n"
        
        response += f"""

NUMERIC DATA FROM {desired_city.upper()}:
"""
        
        if desired_city_numeric:
            for term, matches in desired_city_numeric.items():
                response += f"\n{term.title()}:\n"
                for match in matches[:3]:  # Limit to top 3 matches per term
                    response += f"  • {match['context']}\n"
                    response += f"    Values found: {', '.join(match['values'])}\n"
        else:
            response += "  No numeric data found for the specified criteria.\n"
        
        response += """

INSTRUCTIONS FOR ANALYSIS:
Compare the numeric data between the two cities for the specified criteria.
Highlight significant differences and explain what they mean for the user.
If data is missing for either city, note this limitation in your analysis.
Focus on objective comparisons based on the numeric data extracted.
"""
        
        return response
        
    except Exception as e:
        print(f"⚠️ [WIKIPEDIA TOOL] Error fetching data: {e}")
        print(f"   Falling back to general knowledge analysis\n")
        return f"""
Unable to fetch Wikipedia data for the specified criteria.
Error: {e}

Please provide analysis for {criteria} in {current_city} vs {desired_city} based on your general knowledge.
Note this limitation in your response.
"""

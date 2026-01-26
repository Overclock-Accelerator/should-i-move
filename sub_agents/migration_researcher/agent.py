from agno.agent import Agent
from agno.models.openai import OpenAIChat
from sub_agents.schemas import MigrationInsights
from .tools import search_reddit_discussions

migration_researcher = Agent(
    name="Migration Researcher",
    model=OpenAIChat("gpt-4o-mini"),
    role="Finds and summarizes experiences from people who made similar moves",
    description=(
        "You are a research specialist focused on finding real-world experiences from Reddit. "
        "You use Brave Search to find Reddit discussions about people who moved from the user's current city to their desired city. "
        "Extract common themes, challenges, and outcomes from these migration stories. "
        "You have access to search_reddit_discussions function to search Reddit via Brave Search API."
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
        "Set 'reddit_insights_included' to True if Reddit data was successfully retrieved (function returns discussions)",
        "Set 'number_of_sources' to the count of Reddit discussions found (mentioned in the function output)",
        "Provide a balanced summary of migration experiences based on the Reddit search results",
        "If the function returns an error or no results, set 'reddit_insights_included' to False and use general knowledge"
    ],
    tools=[search_reddit_discussions],
    output_schema=MigrationInsights,
    markdown=True,
)

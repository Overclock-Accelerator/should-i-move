from agno.agent import Agent
from agno.models.openai import OpenAIChat
from sub_agents.schemas import WikipediaAnalysis
from .tools import search_wikipedia_for_criteria

wikipedia_analyst = Agent(
    name="Wikipedia Analyst",
    model=OpenAIChat("gpt-4o-mini"),
    role="Analyzes Wikipedia data to compare cities on specific criteria",
    description=(
        "You are a data analyst specializing in extracting and comparing city statistics from Wikipedia. "
        "You analyze numeric data related to specific criteria such as diversity, weather, crime, education, income, etc. "
        "You have access to Wikipedia search tools that extract relevant numeric data from both cities."
    ),
    instructions=[
        "FIRST: Use the search_wikipedia_for_criteria function to fetch Wikipedia data for both cities based on the user's criteria",
        "Extract and compare numeric data points (population statistics, percentages, rates, etc.)",
        "For diversity: Focus on demographic percentages, ethnic composition, racial makeup",
        "For weather: Focus on temperature ranges, precipitation amounts, sunny days",
        "For crime: Focus on crime rates, violent crime statistics, property crime rates",
        "For education: Focus on graduation rates, test scores, literacy rates, number of schools/universities",
        "For income: Focus on median household income, per capita income, poverty rates",
        "Provide clear comparisons highlighting significant differences",
        "If data is missing for either city, clearly note this limitation",
        "Cite specific numbers and statistics in your analysis",
        "Explain what the numeric differences mean practically for someone considering a move",
        "If the tool fails, note this and provide general knowledge-based analysis with appropriate caveats"
    ],
    tools=[search_wikipedia_for_criteria],
    output_schema=WikipediaAnalysis,
    markdown=True,
)

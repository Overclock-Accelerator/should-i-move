from agno.agent import Agent
from agno.models.openai import OpenAIChat
from sub_agents.schemas import SentimentAnalysis

sentiment_analyst = Agent(
    name="Sentiment Analyst",
    model=OpenAIChat("gpt-4o-mini"),
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

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from sub_agents.schemas import CostAnalysis
from .tools import get_cost_of_living_comparison

cost_analyst = Agent(
    name="Cost Analyst",
    model=OpenAIChat("gpt-4o-mini"),
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

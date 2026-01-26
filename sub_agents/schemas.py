from typing import List, Optional
from pydantic import BaseModel, Field

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

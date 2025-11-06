# City Move Decision Multi-Agent Application

This is a multi-agent terminal application built with Agno that helps users decide whether to move from their current city to a new city.

## Architecture

The application uses a coordinated team structure with:

- **Coordinator Agent**: Gathers user information through conversational Q&A
- **Cost Analyst**: Analyzes cost of living differences (placeholder implementation)
- **Sentiment Analyst**: Researches city vibe and livability (placeholder implementation)
- **Migration Researcher**: Finds migration experiences from similar moves (placeholder implementation)
- **Team Leader**: Synthesizes all inputs into a final recommendation

## How It Works

1. **Initial Input**: User provides freeform information about their situation
2. **Interactive Q&A**: Coordinator asks follow-up questions to gather missing information
3. **Parallel Analysis**: Three specialized agents analyze different aspects of the move
4. **Synthesis**: Team coordinator provides a comprehensive recommendation

## Current Implementation

This version uses **placeholder data** for the three research agents. They provide generic insights based on the AI's general knowledge about cities. Future versions will integrate:

- Web scraping for real-time cost of living data
- Sentiment analysis from articles and reviews
- Blog/Reddit post analysis for migration experiences

## Usage

### Prerequisites

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install agno openai python-dotenv
```

### Environment Setup

Create a `.env` file in the project root with your OpenAI API key:

```bash
OPENAI_API_KEY=your_api_key_here
```

The application will automatically load this file when it runs.

### Run the Application

```bash
# Normal mode
python 02-agno-coordination.py

# Debug mode (shows detailed LLM call information)
python 02-agno-coordination.py --debug
```

**To stop the application at any time:** Press `Ctrl+C`

### Example Session

```
Tell me about your move consideration: I'm thinking about moving from Austin to Seattle
  
Assistant: Great! Let me ask you a few questions...
- What's your approximate annual income?
- How much do you typically spend per month?
- What do you value most in a city?
...
```

## Data Models

- **UserProfile**: Captures financial info, preferences, and city opinions
- **CostAnalysis**: Cost of living comparison results
- **SentimentAnalysis**: City vibe and livability assessment
- **MigrationInsights**: Experiences from similar moves
- **FinalRecommendation**: Comprehensive recommendation with justification

## Future Enhancements

- Integration of real web scraping tools for cost data
- Sentiment analysis from actual reviews and articles  
- Reddit/blog post scraping for migration stories
- Alternative team coordination patterns
- Enhanced visualization of results



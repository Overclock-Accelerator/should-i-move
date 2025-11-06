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

### Real Data Integration

**Cost Analyst** now uses real-time data:
- ✅ **NerdWallet Cost of Living Calculator** - Fetches actual cost comparison data using Firecrawl
- Extracts housing, transportation, food, entertainment, and healthcare costs
- Provides specific percentages and dollar amounts from real data
- Console logging shows when the tool is being used

### Placeholder Implementations

**Sentiment Analyst** and **Migration Researcher** still use placeholder data:
- Sentiment analysis from articles and reviews (coming soon)
- Blog/Reddit post analysis for migration experiences (coming soon)

## Usage

### Prerequisites

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install agno openai python-dotenv firecrawl-py
```

### Environment Setup

Create a `.env` file in the project root with your API keys:

```bash
OPENAI_API_KEY=your_api_key_here
FIRECRAWL_API_KEY=your_firecrawl_key_here
```

The application will automatically load this file when it runs.

**Note:** Get a Firecrawl API key from [firecrawl.dev](https://firecrawl.dev) for the cost of living data scraping feature.

### Setup: Create City Database (First Time Only)

Before running the application, create the city database:

```bash
cd nerdwallet-tools
python create_city_database.py
cd ..
```

This creates `data/nerdwallet_cities_comprehensive.json` with 200+ validated cities and proper URL formats.

### Run the Application

```bash
# Normal mode
python 02-agno-coordination.py

# Debug mode (shows detailed LLM call information)
python 02-agno-coordination.py --debug
```

**To stop the application at any time:** Press `Ctrl+C`

### Test the Cost Scraper

To verify the NerdWallet scraper is working correctly:

```bash
cd nerdwallet-tools
python test_cost_scraper.py
cd ..
```

This standalone test will:
- Verify your FIRECRAWL_API_KEY is configured
- Test city name formatting
- Scrape a comparison page and show the results
- Validate the scraped data contains expected fields

### Build City List for Matching

Create a comprehensive database of US cities:

```bash
cd nerdwallet-tools

# Step 1: Create the city database
python create_city_database.py

# Step 2: Test the city matcher
python city_matcher.py

# Step 3 (Optional): Validate cities against NerdWallet
python validate_cities.py

cd ..
```

This will:
1. Create a comprehensive database of 200+ major US cities
2. Save to `data/nerdwallet_cities_comprehensive.json` with URL format mappings
3. Enable fuzzy matching of user input to valid NerdWallet city formats
4. Handle variations like "NYC" → "New York (Manhattan), NY" → "new-york-manhattan-ny"
5. Support aliases like "SF" → "San Francisco", "Philly" → "Philadelphia"

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

## Features

### Real-Time Cost Analysis
The Cost Analyst agent now fetches real data from NerdWallet's cost of living calculator:
- Automatically generates comparison URLs based on user's cities
- Scrapes actual housing, transportation, food, entertainment, and healthcare costs
- Provides specific percentages and dollar amounts in analysis
- Console logs show the tool in action:
  ```
  🔍 [COST TOOL] Fetching real cost of living data...
     Current City: New York City (new-york-city)
     Desired City: Miami (miami)
     URL: https://www.nerdwallet.com/cost-of-living-calculator/compare/new-york-city-vs-miami
     ⏳ Scraping data with Firecrawl...
  
  ✅ [COST TOOL] Successfully retrieved cost of living data!
  ```

## Future Enhancements

- ✅ ~~Integration of real web scraping tools for cost data~~ (COMPLETED)
- Sentiment analysis from actual reviews and articles  
- Reddit/blog post scraping for migration stories
- Alternative team coordination patterns
- Enhanced visualization of results



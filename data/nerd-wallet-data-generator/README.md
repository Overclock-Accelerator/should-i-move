# NerdWallet City Tools

Utilities for creating, validating, and matching city data for NerdWallet's cost of living calculator.

## Files

### Core Tools

**`create_city_database.py`**
- Creates a comprehensive database of 200+ US cities
- Includes proper NerdWallet URL formats
- Handles special cases (NYC boroughs, etc.)
- **Output:** `../data/nerdwallet_cities_comprehensive.json`

**`city_matcher.py`**
- Fuzzy matching utility to find cities
- Supports aliases (NYC, LA, SF, etc.)
- Test interface for validation
- **Input:** `../data/nerdwallet_cities_comprehensive.json`

**`validate_cities.py`**
- Validates city URLs against actual NerdWallet pages
- Tests sample of cities to ensure they work
- Identifies cities that need URL format corrections
- **Output:** `../data/validation_results.json`

### Testing & Debugging

**`test_cost_scraper.py`**
- Standalone test for the cost of living scraper
- Verifies Firecrawl integration
- Tests city URL formatting
- Validates scraped data quality

**`scrape_city_list.py`**
- Attempts to scrape NerdWallet for city list (limited by JavaScript)
- Useful for discovering new cities
- **Output:** `../data/nerdwallet_cities_merged.json` and raw scrapes

## Usage

### First Time Setup

```bash
# Create the city database
python create_city_database.py

# Verify it works
python city_matcher.py
```

### Testing

```bash
# Test the scraper with specific cities
python test_cost_scraper.py

# Validate cities against NerdWallet (optional)
python validate_cities.py
```

### Development

When adding new cities:
1. Add them to `US_CITIES` list in `create_city_database.py`
2. Run `python create_city_database.py` to regenerate database
3. Run `python validate_cities.py` to verify they work on NerdWallet

## Data Files

All data files are stored in `../data/`:
- `nerdwallet_cities_comprehensive.json` - Main city database (commit this)
- `nerdwallet_raw_scrape.txt` - Raw HTML from scraping (temporary)
- `nerdwallet_comparison_raw.txt` - Raw comparison page (temporary)
- `validation_results.json` - City validation results (temporary)

## Notes

- NYC has 5 separate boroughs (Brooklyn, Manhattan, Queens, Bronx, Staten Island)
- NerdWallet uses format like `new-york-brooklyn-ny` not `new-york-city-ny`
- All tools use relative paths (`../data/`) to work from the tools directory


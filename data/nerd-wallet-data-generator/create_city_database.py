"""
Create a comprehensive database of US cities in NerdWallet format.
Since the city list is loaded dynamically via JavaScript, we'll create
a curated list of major US cities that NerdWallet likely supports.
"""

import json

# Comprehensive list of major US cities organized by state
# Format: (city_name, state_name, state_abbr)
US_CITIES = [
    # Alabama
    ("Birmingham", "Alabama", "AL"),
    ("Mobile", "Alabama", "AL"),
    ("Montgomery", "Alabama", "AL"),
    
    # Arizona
    ("Phoenix", "Arizona", "AZ"),
    ("Tucson", "Arizona", "AZ"),
    ("Mesa", "Arizona", "AZ"),
    ("Chandler", "Arizona", "AZ"),
    ("Scottsdale", "Arizona", "AZ"),
    ("Glendale", "Arizona", "AZ"),
    
    # Arkansas
    ("Little Rock", "Arkansas", "AR"),
    
    # California
    ("Los Angeles", "California", "CA"),
    ("San Francisco", "California", "CA"),
    ("San Diego", "California", "CA"),
    ("San Jose", "California", "CA"),
    ("Sacramento", "California", "CA"),
    ("Oakland", "California", "CA"),
    ("Fresno", "California", "CA"),
    ("Long Beach", "California", "CA"),
    ("Bakersfield", "California", "CA"),
    ("Anaheim", "California", "CA"),
    ("Santa Ana", "California", "CA"),
    ("Riverside", "California", "CA"),
    ("Irvine", "California", "CA"),
    ("Stockton", "California", "CA"),
    ("Chula Vista", "California", "CA"),
    ("Fremont", "California", "CA"),
    ("San Bernardino", "California", "CA"),
    ("Modesto", "California", "CA"),
    
    # Colorado
    ("Denver", "Colorado", "CO"),
    ("Colorado Springs", "Colorado", "CO"),
    ("Aurora", "Colorado", "CO"),
    ("Fort Collins", "Colorado", "CO"),
    ("Boulder", "Colorado", "CO"),
    
    # Connecticut
    ("Bridgeport", "Connecticut", "CT"),
    ("New Haven", "Connecticut", "CT"),
    ("Hartford", "Connecticut", "CT"),
    
    # Florida
    ("Jacksonville", "Florida", "FL"),
    ("Miami", "Florida", "FL"),
    ("Tampa", "Florida", "FL"),
    ("Orlando", "Florida", "FL"),
    ("St Petersburg", "Florida", "FL"),
    ("Hialeah", "Florida", "FL"),
    ("Tallahassee", "Florida", "FL"),
    ("Fort Lauderdale", "Florida", "FL"),
    ("Port St Lucie", "Florida", "FL"),
    ("Cape Coral", "Florida", "FL"),
    ("Pembroke Pines", "Florida", "FL"),
    ("Hollywood", "Florida", "FL"),
    ("Gainesville", "Florida", "FL"),
    
    # Georgia
    ("Atlanta", "Georgia", "GA"),
    ("Augusta", "Georgia", "GA"),
    ("Columbus", "Georgia", "GA"),
    ("Macon", "Georgia", "GA"),
    ("Savannah", "Georgia", "GA"),
    
    # Idaho
    ("Boise", "Idaho", "ID"),
    
    # Illinois
    ("Chicago", "Illinois", "IL"),
    ("Aurora", "Illinois", "IL"),
    ("Rockford", "Illinois", "IL"),
    ("Joliet", "Illinois", "IL"),
    ("Naperville", "Illinois", "IL"),
    ("Springfield", "Illinois", "IL"),
    
    # Indiana
    ("Indianapolis", "Indiana", "IN"),
    ("Fort Wayne", "Indiana", "IN"),
    ("Evansville", "Indiana", "IN"),
    
    # Iowa
    ("Des Moines", "Iowa", "IA"),
    ("Cedar Rapids", "Iowa", "IA"),
    
    # Kansas
    ("Wichita", "Kansas", "KS"),
    ("Overland Park", "Kansas", "KS"),
    ("Kansas City", "Kansas", "KS"),
    
    # Kentucky
    ("Louisville", "Kentucky", "KY"),
    ("Lexington", "Kentucky", "KY"),
    
    # Louisiana
    ("New Orleans", "Louisiana", "LA"),
    ("Baton Rouge", "Louisiana", "LA"),
    ("Shreveport", "Louisiana", "LA"),
    
    # Maryland
    ("Baltimore", "Maryland", "MD"),
    
    # Massachusetts
    ("Boston", "Massachusetts", "MA"),
    ("Worcester", "Massachusetts", "MA"),
    ("Springfield", "Massachusetts", "MA"),
    ("Cambridge", "Massachusetts", "MA"),
    
    # Michigan
    ("Detroit", "Michigan", "MI"),
    ("Grand Rapids", "Michigan", "MI"),
    ("Warren", "Michigan", "MI"),
    ("Sterling Heights", "Michigan", "MI"),
    ("Ann Arbor", "Michigan", "MI"),
    
    # Minnesota
    ("Minneapolis", "Minnesota", "MN"),
    ("St Paul", "Minnesota", "MN"),
    ("Rochester", "Minnesota", "MN"),
    
    # Missouri
    ("Kansas City", "Missouri", "MO"),
    ("St Louis", "Missouri", "MO"),
    ("Springfield", "Missouri", "MO"),
    
    # Nebraska
    ("Omaha", "Nebraska", "NE"),
    ("Lincoln", "Nebraska", "NE"),
    
    # Nevada
    ("Las Vegas", "Nevada", "NV"),
    ("Henderson", "Nevada", "NV"),
    ("Reno", "Nevada", "NV"),
    
    # New Hampshire
    ("Manchester", "New Hampshire", "NH"),
    
    # New Jersey
    ("Newark", "New Jersey", "NJ"),
    ("Jersey City", "New Jersey", "NJ"),
    ("Paterson", "New Jersey", "NJ"),
    
    # New Mexico
    ("Albuquerque", "New Mexico", "NM"),
    
    # New York
    # Note: NerdWallet uses borough-specific identifiers for NYC
    ("New York (Brooklyn)", "New York", "NY"),
    ("New York (Manhattan)", "New York", "NY"),
    ("New York (Queens)", "New York", "NY"),
    ("New York (Bronx)", "New York", "NY"),
    ("New York (Staten Island)", "New York", "NY"),
    ("Buffalo", "New York", "NY"),
    ("Rochester", "New York", "NY"),
    ("Yonkers", "New York", "NY"),
    ("Syracuse", "New York", "NY"),
    ("Albany", "New York", "NY"),
    
    # North Carolina
    ("Charlotte", "North Carolina", "NC"),
    ("Raleigh", "North Carolina", "NC"),
    ("Greensboro", "North Carolina", "NC"),
    ("Durham", "North Carolina", "NC"),
    ("Winston-Salem", "North Carolina", "NC"),
    ("Fayetteville", "North Carolina", "NC"),
    ("Cary", "North Carolina", "NC"),
    
    # Ohio
    ("Columbus", "Ohio", "OH"),
    ("Cleveland", "Ohio", "OH"),
    ("Cincinnati", "Ohio", "OH"),
    ("Toledo", "Ohio", "OH"),
    ("Akron", "Ohio", "OH"),
    ("Dayton", "Ohio", "OH"),
    
    # Oklahoma
    ("Oklahoma City", "Oklahoma", "OK"),
    ("Tulsa", "Oklahoma", "OK"),
    
    # Oregon
    ("Portland", "Oregon", "OR"),
    ("Salem", "Oregon", "OR"),
    ("Eugene", "Oregon", "OR"),
    
    # Pennsylvania
    ("Philadelphia", "Pennsylvania", "PA"),
    ("Pittsburgh", "Pennsylvania", "PA"),
    ("Allentown", "Pennsylvania", "PA"),
    
    # Rhode Island
    ("Providence", "Rhode Island", "RI"),
    
    # South Carolina
    ("Columbia", "South Carolina", "SC"),
    ("Charleston", "South Carolina", "SC"),
    
    # Tennessee
    ("Memphis", "Tennessee", "TN"),
    ("Nashville", "Tennessee", "TN"),
    ("Knoxville", "Tennessee", "TN"),
    ("Chattanooga", "Tennessee", "TN"),
    
    # Texas
    ("Houston", "Texas", "TX"),
    ("San Antonio", "Texas", "TX"),
    ("Dallas", "Texas", "TX"),
    ("Austin", "Texas", "TX"),
    ("Fort Worth", "Texas", "TX"),
    ("El Paso", "Texas", "TX"),
    ("Arlington", "Texas", "TX"),
    ("Corpus Christi", "Texas", "TX"),
    ("Plano", "Texas", "TX"),
    ("Laredo", "Texas", "TX"),
    ("Lubbock", "Texas", "TX"),
    ("Garland", "Texas", "TX"),
    ("Irving", "Texas", "TX"),
    ("Amarillo", "Texas", "TX"),
    ("Grand Prairie", "Texas", "TX"),
    ("Brownsville", "Texas", "TX"),
    ("McKinney", "Texas", "TX"),
    ("Frisco", "Texas", "TX"),
    ("Pasadena", "Texas", "TX"),
    ("Mesquite", "Texas", "TX"),
    ("Killeen", "Texas", "TX"),
    ("McAllen", "Texas", "TX"),
    ("Waco", "Texas", "TX"),
    ("Beaumont", "Texas", "TX"),
    ("Conroe", "Texas", "TX"),
    
    # Utah
    ("Salt Lake City", "Utah", "UT"),
    ("West Valley City", "Utah", "UT"),
    ("Provo", "Utah", "UT"),
    
    # Virginia
    ("Virginia Beach", "Virginia", "VA"),
    ("Norfolk", "Virginia", "VA"),
    ("Chesapeake", "Virginia", "VA"),
    ("Richmond", "Virginia", "VA"),
    ("Newport News", "Virginia", "VA"),
    ("Arlington", "Virginia", "VA"),
    
    # Washington
    ("Seattle", "Washington", "WA"),
    ("Spokane", "Washington", "WA"),
    ("Tacoma", "Washington", "WA"),
    ("Vancouver", "Washington", "WA"),
    
    # Wisconsin
    ("Milwaukee", "Wisconsin", "WI"),
    ("Madison", "Wisconsin", "WI"),
]


# Common city aliases for fuzzy matching
CITY_ALIASES = {
    "NYC": ("New York (Manhattan)", "New York", "NY"),
    "New York City": ("New York (Manhattan)", "New York", "NY"),
    "Brooklyn": ("New York (Brooklyn)", "New York", "NY"),
    "Manhattan": ("New York (Manhattan)", "New York", "NY"),
    "Queens": ("New York (Queens)", "New York", "NY"),
    "Bronx": ("New York (Bronx)", "New York", "NY"),
    "Staten Island": ("New York (Staten Island)", "New York", "NY"),
    "LA": ("Los Angeles", "California", "CA"),
    "SF": ("San Francisco", "California", "CA"),
    "San Fran": ("San Francisco", "California", "CA"),
    "Philly": ("Philadelphia", "Pennsylvania", "PA"),
    "Vegas": ("Las Vegas", "Nevada", "NV"),
}


def create_city_database():
    """
    Create a comprehensive city database in NerdWallet format.
    """
    print("="*80)
    print("CREATING CITY DATABASE")
    print("="*80)
    
    cities = {}
    
    for city, state, state_abbr in US_CITIES:
        # Create display name
        display_name = f"{city}, {state_abbr}"
        
        # Create URL format (lowercase, spaces to dashes)
        city_url = city.lower().replace(' ', '-').replace('.', '')
        
        # Handle NYC boroughs specially (remove parentheses for URL)
        if "New York (" in city:
            # Extract borough name
            borough = city.split('(')[1].rstrip(')')
            city_url = f"new-york-{borough.lower().replace(' ', '-')}"
        
        state_url = state_abbr.lower()
        url_format = f"{city_url}-{state_url}"
        
        # Add to database
        cities[display_name] = {
            "display_name": display_name,
            "city": city,
            "state": state,
            "state_abbr": state_abbr,
            "url_format": url_format
        }
    
    # Add aliases
    for alias, (city, state, state_abbr) in CITY_ALIASES.items():
        display_name = f"{city}, {state_abbr}"
        if display_name in cities:
            cities[display_name]["aliases"] = cities[display_name].get("aliases", []) + [alias]
    
    # Save to JSON
    with open("../data/nerdwallet_cities_comprehensive.json", "w", encoding="utf-8") as f:
        json.dump(cities, f, indent=2, sort_keys=True)
    
    print(f"\n✅ Created database with {len(cities)} cities")
    print(f"✅ Saved to: data/nerdwallet_cities_comprehensive.json")
    
    # Show statistics
    states = {}
    for city_data in cities.values():
        state = city_data['state_abbr']
        states[state] = states.get(state, 0) + 1
    
    print(f"\n📊 Cities by state (top 10):")
    for state, count in sorted(states.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"   {state}: {count} cities")
    
    print(f"\n📋 Sample cities:")
    for i, (key, value) in enumerate(sorted(cities.items())[:20]):
        print(f"   {value['display_name']:35} → {value['url_format']}")
    
    print("\n" + "="*80 + "\n")
    
    return cities


if __name__ == "__main__":
    create_city_database()


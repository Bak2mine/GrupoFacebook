"""
Fetch population data from Wikipedia for Brazilian cities
"""

import json
import requests
import logging
from pathlib import Path
from typing import Dict

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

WIKI_API = "https://en.wikipedia.org/w/api.php"


def get_wikipedia_population(city: str, state: str = None) -> int:
    """
    Fetch population from Wikipedia for a Brazilian city

    Args:
        city: City name
        state: State abbreviation (optional)

    Returns:
        Population as integer, or 0 if not found
    """
    try:
        import re

        # Try direct page request first (common format: City, State)
        search_query = f"{city}, {state}" if state else city

        params = {
            'action': 'query',
            'titles': search_query,
            'prop': 'extracts',
            'explaintext': True,
            'format': 'json'
        }

        response = requests.get(WIKI_API, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        pages = data.get('query', {}).get('pages', {})

        # Check if we got a valid page (not -1)
        valid_pages = {k: v for k, v in pages.items() if k != '-1'}

        if not valid_pages:
            # Try search as fallback
            params = {
                'action': 'query',
                'list': 'search',
                'srsearch': search_query,
                'format': 'json'
            }

            response = requests.get(WIKI_API, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()

            if not data.get('query', {}).get('search'):
                logger.debug(f"  No Wikipedia results for {city}")
                return 0

            first_result = data['query']['search'][0]
            page_title = first_result['title']

            params = {
                'action': 'query',
                'titles': page_title,
                'prop': 'extracts',
                'explaintext': True,
                'format': 'json'
            }

            response = requests.get(WIKI_API, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            pages = data.get('query', {}).get('pages', {})

        if not pages:
            return 0

        page = list(pages.values())[0]
        extract = page.get('extract', '')

        if not extract:
            logger.debug(f"  No extract for {city}")
            return 0

        # Look for population in the extract
        patterns = [
            r'population.*?(\d{1,3}(?:[,\s]\d{3})*)',  # population of 2,355,039 or 2 355 039
            r'(\d{1,3}(?:[,\s]\d{3})*)\s*(?:inhabitants|residents|people|population)',
            r'pop[uation]*:?\s*(\d{1,3}(?:[,\s]\d{3})*)',
        ]

        for pattern in patterns:
            match = re.search(pattern, extract, re.IGNORECASE)
            if match:
                pop_str = match.group(1).replace(',', '').replace(' ', '')
                try:
                    population = int(pop_str)
                    if population > 0:
                        logger.info(f"  ✓ {city}: {population:,}")
                        return population
                except ValueError:
                    continue

        logger.debug(f"  Could not parse population for {city}")
        return 0

    except Exception as e:
        logger.debug(f"  Error fetching {city}: {e}")
        return 0


def update_populations_from_wikipedia():
    """
    Load scraped groups, extract unique cities, fetch populations from Wikipedia,
    and update the config file
    """
    logger.info("Fetching population data from Wikipedia...\n")

    # Load scraped data to get unique cities
    searches_file = Path("data/searches_with_group_ids.json")

    if not searches_file.exists():
        logger.error(f"Searches file not found: {searches_file}")
        return

    with open(searches_file, 'r', encoding='utf-8') as f:
        searches = json.load(f)

    # Extract unique cities
    cities = {}
    for search in searches:
        city = search.get('city')
        state = search.get('state')
        if city:
            cities[city] = state

    logger.info(f"Found {len(cities)} unique cities\n")
    logger.info("Fetching populations from Wikipedia:\n")

    # Fetch population for each city
    populations = {}
    for city, state in sorted(cities.items()):
        population = get_wikipedia_population(city, state)
        if population > 0:
            populations[city] = population

    logger.info(f"\n✓ Successfully fetched {len(populations)} cities\n")

    # Update config.py
    config_file = Path("config.py")

    if not config_file.exists():
        logger.error("config.py not found")
        return

    # Read current config
    with open(config_file, 'r', encoding='utf-8') as f:
        config_content = f.read()

    # Build new CITY_POPULATION dictionary
    cities_dict_str = "CITY_POPULATION = {\n"
    for city in sorted(populations.keys()):
        pop = populations[city]
        cities_dict_str += f"    '{city}': {pop},\n"
    cities_dict_str += "}"

    # Replace old CITY_POPULATION with new one
    import re
    new_config = re.sub(
        r"CITY_POPULATION = \{[^}]+\}",
        cities_dict_str,
        config_content,
        flags=re.DOTALL
    )

    # Write back
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(new_config)

    logger.info(f"✓ Updated config.py with {len(populations)} cities\n")

    # Show summary
    logger.info("Population Summary:")
    logger.info("=" * 60)
    for city in sorted(populations.keys()):
        logger.info(f"  {city}: {populations[city]:,}")

    total_pop = sum(populations.values())
    logger.info("=" * 60)
    logger.info(f"Total population: {total_pop:,}\n")


if __name__ == '__main__':
    update_populations_from_wikipedia()

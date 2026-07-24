"""
Phase 1: Dynamically extract cities from Leiloaria Smart website and fetch population from IBGE API
"""

import json
import requests
import re
from pathlib import Path
from playwright.sync_api import sync_playwright
from config import DATA_DIR

class CityExtractor:
    """Extract unique cities from website dynamically using Playwright and fetch population data from IBGE API"""

    def __init__(self):
        self.output_file = DATA_DIR / "search_configuration.json"
        self.website_url = "https://www.leiloariasmart.com.br"
        self.ibge_api = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"

    def scrape_cities_from_website(self):
        """Scrape cities from Leiloaria Smart website using Playwright"""
        try:
            print("Fetching website with Playwright...")
            playwright = sync_playwright().start()
            browser = playwright.chromium.launch(headless=True, channel="chrome")
            page = browser.new_page()
            page.goto(self.website_url, wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")

            # Get page content
            content = page.content()
            browser.close()
            playwright.stop()

            print("Parsing cities from website...\n")

            # Extract city URLs using regex (format: href='/filtro/cidade/city-name')
            cities = set()
            pattern = r"href=['\"]?/filtro/cidade/([^'\" ]+)['\"]?"
            matches = re.findall(pattern, content)

            for city_slug in matches:
                city_slug = city_slug.strip()
                if city_slug:  # Skip empty ones
                    cities.add(city_slug)

            cities = sorted(list(cities))
            print(f"[OK] Found {len(cities)} unique cities from website\n")
            return cities if cities else None

        except Exception as e:
            print(f"[ERROR] Failed to scrape website: {e}")
            import traceback
            traceback.print_exc()
            return None

    def fetch_population_from_ibge(self, city_name):
        """Fetch population for a city from IBGE API"""
        try:
            response = requests.get(self.ibge_api, timeout=10)
            if response.status_code != 200:
                return None

            municipalities = response.json()

            # Try to find matching city (case-insensitive)
            city_lower = city_name.lower()
            for municipality in municipalities:
                if municipality.get('nome', '').lower() == city_lower:
                    return municipality.get('populacao')

            return None
        except Exception as e:
            print(f"[WARNING] Could not fetch population for {city_name}: {e}")
            return None

    def extract_cities(self):
        """Scrape cities from website, fetch populations, and create search config"""
        print("=" * 70)
        print("EXTRACTING CITIES FROM LEILOARIA SMART WEBSITE")
        print("=" * 70)
        print("")

        # Scrape cities from website
        cities = self.scrape_cities_from_website()
        if not cities:
            print("[ERROR] No cities found on website")
            return False

        print("Fetching population data from IBGE API...\n")

        # Create search configuration
        searches = []
        large_cities = 0
        small_cities = 0
        unknown_pop = 0

        for city_slug in cities:
            # Format city name (replace hyphens with spaces, title case)
            display_name = city_slug.replace('-', ' ').title()

            # Fetch population from IBGE
            population = self.fetch_population_from_ibge(display_name)

            if population is None:
                print(f"[?] {display_name}: population unknown")
                unknown_pop += 1
                population = 0

            # Determine search type based on population threshold (500,000)
            search_type = "city"
            if population >= 500000:
                search_type = "bairro"
                large_cities += 1
                print(f"[LARGE] {display_name}: {population:,} inhabitants (search bairro level)")
            else:
                small_cities += 1
                print(f"[SMALL] {display_name}: {population:,} inhabitants (search city level)")

            search = {
                'city': display_name,
                'state': 'Unknown',
                'type': search_type,
                'search_term': f"imoveis {display_name}",
                'population': population,
                'group_ids': [],
                'group_details': []
            }
            searches.append(search)

        print("")
        print(f"Summary:")
        print(f"  Large cities (>500k): {large_cities}")
        print(f"  Small cities (≤500k): {small_cities}")
        print(f"  Unknown population: {unknown_pop}")
        print(f"  Total cities: {len(searches)}")
        print("")

        # Save configuration
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(searches, f, ensure_ascii=False, indent=2)

        print(f"[OK] Saved {len(searches)} city searches to {self.output_file}")
        print("")
        print("=" * 70)
        print("CITY EXTRACTION COMPLETE!")
        print("=" * 70)
        print("")

        return True

    def run(self):
        """Main pipeline"""
        return self.extract_cities()


if __name__ == '__main__':
    extractor = CityExtractor()
    success = extractor.run()
    exit(0 if success else 1)

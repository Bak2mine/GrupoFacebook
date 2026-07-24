"""
Phase 1: Extract cities from local file and fetch population from IBGE API
Cities file can be updated manually when website changes
"""

import json
from pathlib import Path
from config import DATA_DIR
import requests

class CityExtractor:
    """Extract cities from file and fetch population data from IBGE API"""

    def __init__(self):
        self.cities_file = DATA_DIR / "leiloaria_cities.txt"
        self.output_file = DATA_DIR / "search_configuration.json"
        self.ibge_api = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"

    def load_cities_from_file(self):
        """Load cities from leiloaria_cities.txt file"""
        if not self.cities_file.exists():
            print(f"[ERROR] Cities file not found: {self.cities_file}")
            print("[HINT] You can update this file by:")
            print("  1. Opening leiloariasmart.com.br")
            print("  2. Copying the cities from the dropdown")
            print("  3. Saving them to data/leiloaria_cities.txt (one per line)")
            return None

        with open(self.cities_file, 'r', encoding='utf-8') as f:
            cities = [line.strip() for line in f if line.strip()]

        print(f"[OK] Loaded {len(cities)} cities from {self.cities_file}\n")
        return cities if cities else None

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
        """Load cities from file, fetch populations, and create search config"""
        print("=" * 70)
        print("EXTRACTING CITIES FROM FILE")
        print("=" * 70)
        print("")

        # Load cities from file
        cities = self.load_cities_from_file()
        if not cities:
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

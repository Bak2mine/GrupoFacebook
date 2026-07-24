"""
Phase 1: Extract cities from Leiloaria Smart website
Uses the actual city list from the site instead of Wikipedia
"""

import json
from pathlib import Path
from config import DATA_DIR

class CityExtractor:
    """Extract search configuration directly from website cities"""

    def __init__(self):
        self.cities_file = DATA_DIR / "leiloaria_cities.txt"
        self.output_file = DATA_DIR / "search_configuration.json"

    def extract_cities(self):
        """Read cities from leiloaria_cities.txt and create search config"""
        if not self.cities_file.exists():
            print(f"[ERROR] Cities file not found: {self.cities_file}")
            return False

        print("=" * 70)
        print("EXTRACTING CITIES FROM LEILOARIA SMART")
        print("=" * 70)
        print("")

        # Read cities from file
        with open(self.cities_file, 'r', encoding='utf-8') as f:
            cities = [line.strip() for line in f if line.strip()]

        print(f"[OK] Found {len(cities)} cities\n")

        # Create search configuration
        searches = []
        for city in cities:
            # Format city name (replace hyphens with spaces, title case)
            display_name = city.replace('-', ' ').title()

            search = {
                'city': display_name,
                'state': 'Unknown',  # We don't have state info from the site
                'type': 'city',
                'search_term': f"imoveis {display_name}",
                'group_ids': [],
                'group_details': []
            }
            searches.append(search)

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

"""
Phase 2B: Generate search queries with bairro-level searches for large cities (500k+)
Uses property data with extracted bairro information to create detailed searches
"""

import json
import sys
from pathlib import Path
from typing import List, Dict
from config import CITY_POPULATION, DATA_DIR

# Add Post folder to path to import its scraper
# Grupo is in C:\Users\andre\Desktop\Leiloaria\Grupo
# Post is in C:\Users\andre\Desktop\Leiloaria\Post
post_folder = Path(__file__).resolve().parent.parent / 'Post'
sys.path.insert(0, str(post_folder.resolve()))

try:
    from scraper import PropertyScraper
except ImportError:
    print("ERROR: Could not import PropertyScraper from Post folder")
    print("Make sure the Post folder exists with scraper.py")
    sys.exit(1)


class BairroSearchBuilder:
    """Build searches using bairro data for large cities"""

    LARGE_CITY_THRESHOLD = 500000

    def __init__(self):
        self.scraper = PropertyScraper()
        self.large_cities = self._identify_large_cities()
        self.bairros_by_city = {}

    def _identify_large_cities(self) -> Dict[str, int]:
        """Identify cities with 500k+ population"""
        return {
            city: pop for city, pop in CITY_POPULATION.items()
            if pop > self.LARGE_CITY_THRESHOLD
        }

    def extract_bairros_from_properties(self) -> Dict[str, set]:
        """
        Scrape property listings and extract unique bairros for large cities

        Returns:
            Dict mapping city -> set of unique bairros
        """
        print(f"Extracting bairro data for {len(self.large_cities)} large cities...\n")

        bairros_by_city = {city: set() for city in self.large_cities.keys()}

        # Get all auctions
        auctions = self.scraper.get_all_auctions()
        print(f"Found {len(auctions)} total properties\n")

        # Extract data for each property
        for i, auction in enumerate(auctions, 1):
            try:
                # Get property data (includes extracted bairro)
                prop_data = self.scraper.get_property_data(auction['url'], auction['title'])

                if not prop_data:
                    continue

                cidade = prop_data.get('cidade')
                bairro = prop_data.get('bairro')

                # If city is large and bairro was found, add it
                if cidade in self.large_cities and bairro:
                    bairros_by_city[cidade].add(bairro)
                    print(f"[{i}] {cidade}: {bairro}")
                elif i % 50 == 0:
                    print(f"[{i}] Processing... ({cidade if cidade else 'unknown'})")

            except Exception as e:
                if i % 50 == 0:
                    print(f"[{i}] Error: {e}")
                continue

        print("\n" + "="*70)
        print("BAIRROS EXTRACTED PER CITY:")
        print("="*70)

        total_bairros = 0
        for city in sorted(self.large_cities.keys()):
            bairro_list = sorted(list(bairros_by_city[city]))
            count = len(bairro_list)
            total_bairros += count

            print(f"\n{city} ({self.large_cities[city]:,} habitantes):")
            if bairro_list:
                for bairro in bairro_list:
                    print(f"  - {bairro}")
            else:
                print("  (no bairros found - will use city-level search)")

        print("\n" + "="*70)
        print(f"Total unique bairros: {total_bairros}")
        print("="*70 + "\n")

        return bairros_by_city

    def build_search_configuration(self, existing_searches: List[Dict]) -> List[Dict]:
        """
        Update search configuration to use bairro-level searches for large cities

        Args:
            existing_searches: Current search list (city-level for all)

        Returns:
            Updated search list with bairro-level searches for large cities
        """
        new_searches = []

        for search in existing_searches:
            city = search.get('city')
            state = search.get('state')

            # If small city, keep as-is (city-level search)
            if city not in self.large_cities:
                new_searches.append(search)
                continue

            # For large city, create searches by bairro
            if city in self.bairros_by_city and self.bairros_by_city[city]:
                for bairro in sorted(self.bairros_by_city[city]):
                    new_search = {
                        'city': city,
                        'state': state,
                        'type': 'bairro',  # Mark as bairro-level search
                        'search_term': f"{bairro} {city}",
                        'bairro': bairro,
                        'group_ids': [],
                        'group_details': []
                    }
                    new_searches.append(new_search)
                    print(f"[BAIRRO] {bairro}, {city}")
            else:
                # If no bairros found for large city, keep city-level search
                print(f"[CITY] {city} (no bairro data - fallback to city search)")
                new_searches.append(search)

        return new_searches

    def save_updated_configuration(self, searches: List[Dict], output_file: Path = None):
        """Save updated search configuration"""
        if output_file is None:
            output_file = DATA_DIR / "search_configuration_bairro.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(searches, f, ensure_ascii=False, indent=2)

        print(f"\nSaved updated configuration to {output_file}")
        print(f"Total searches: {len(searches)}")

        # Count by type
        city_searches = sum(1 for s in searches if s.get('type') != 'bairro')
        bairro_searches = sum(1 for s in searches if s.get('type') == 'bairro')

        print(f"  City-level searches: {city_searches}")
        print(f"  Bairro-level searches: {bairro_searches}")

    def run(self, existing_config_file: Path = None):
        """Main pipeline"""
        print("\n" + "="*70)
        print("PHASE 2B: GENERATE BAIRRO-LEVEL SEARCHES FOR LARGE CITIES")
        print("="*70 + "\n")

        # Load existing search configuration
        if existing_config_file is None:
            existing_config_file = DATA_DIR / "search_configuration.json"

        print(f"Loading existing configuration from {existing_config_file}...\n")
        with open(existing_config_file, 'r', encoding='utf-8') as f:
            existing_searches = json.load(f)

        # Extract bairros from properties
        self.bairros_by_city = self.extract_bairros_from_properties()

        # Build updated configuration
        print("Building updated search configuration...\n")
        updated_searches = self.build_search_configuration(existing_searches)

        # Save updated configuration
        self.save_updated_configuration(updated_searches)

        print("\n" + "="*70)
        print("PHASE 2B COMPLETE!")
        print("="*70)
        print("\nNext step: Run Phase 3 with the new configuration")
        print("  python phase3_simple_login.py")
        print("="*70 + "\n")


if __name__ == '__main__':
    builder = BairroSearchBuilder()
    builder.run()

"""
Standalone scraper to extract bairro data from leiloariasmart.com.br properties
Used to build bairro-level searches for large cities (500k+ population)
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import json
from pathlib import Path
from typing import List, Dict, Optional
from config import CITY_POPULATION

# Configuration
BASE_URL = "https://leiloariasmart.com.br"
MAIN_URL = "https://leiloariasmart.com.br/busca"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}
TIMEOUT = 10

# Truncation normalization: truncated city -> full name
CITY_NORMALIZATION = {
    'Paulo': 'São Paulo',
    'Janeiro': 'Rio de Janeiro',
    'Leopoldo': 'São Leopoldo',
    'José': 'São José',
    'Pessoa': 'João Pessoa',
    'Luís': 'São Luís',
    'Preto': 'São Paulo',  # Likely "São Paulo" - full name for common large cities
    'Minas': 'Belo Horizonte',  # common truncation
}


class BairroExtractor:
    """Extracts bairro information from property listings"""

    LARGE_CITY_THRESHOLD = 500000

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.large_cities = self._identify_large_cities()
        self.bairros_by_city = {city: set() for city in self.large_cities.keys()}

    def _identify_large_cities(self) -> Dict[str, int]:
        """Identify cities with 500k+ population"""
        return {
            city: pop for city, pop in CITY_POPULATION.items()
            if pop > self.LARGE_CITY_THRESHOLD
        }

    def normalize_city_name(self, city: str) -> str:
        """Normalize truncated city names to full names"""
        if city in CITY_NORMALIZATION:
            return CITY_NORMALIZATION[city]
        return city

    def get_all_auctions(self, limit: Optional[int] = None) -> List[Dict]:
        """Get all auctions from search page"""
        try:
            response = self.session.get(MAIN_URL, timeout=TIMEOUT)
            soup = BeautifulSoup(response.text, 'html.parser')
            auctions = []

            for card in soup.find_all('div', class_='caixa-imoveis'):
                title_tag = card.find('div', class_='info-imovel-2')
                if not title_tag:
                    continue
                link_tag = title_tag.find('a', href=True)
                if not link_tag:
                    continue

                title = link_tag.text.strip()
                url = urljoin(BASE_URL, link_tag['href'])
                auctions.append({'title': title, 'url': url})

                if limit and len(auctions) >= limit:
                    break

            print(f"[OK] Found {len(auctions)} properties\n")
            return auctions

        except Exception as e:
            print(f"[ERROR] Error fetching auctions: {e}")
            return []

    @staticmethod
    def extract_city_from_title(title: str) -> tuple:
        """Extract city and state from property title"""
        # Match multi-word city names (e.g., São Paulo, Rio de Janeiro)
        # Pattern: Capital + letters, optionally followed by more words (capital OR lowercase "de/do/da/dos/das")
        # Handles: São Paulo (capital-capital), Rio de Janeiro (capital-lowercase-capital)

        # First pass: strict with trailing constraints
        loc_match = re.search(
            r'([A-Z][a-záàâãéèêíïóôõöúçñ]*(?:\s+(?:[A-Z]|de|do|da|dos|das)?[a-záàâãéèêíïóôõöúçñ]+)*)\s*/\s*([A-Z]{2})(?:\s|–|—|\-|$)',
            title, re.UNICODE
        )
        if loc_match:
            cidade = loc_match.group(1).strip()
            estado = loc_match.group(2).strip()
            return (cidade, estado)

        # Fallback: flexible pattern without strict trailing constraints
        slash_match = re.search(
            r'([A-Z][a-záàâãéèêíïóôõöúçñ]*(?:\s+(?:[A-Z]|de|do|da|dos|das)?[a-záàâãéèêíïóôõöúçñ]+)*)\s*/\s*([A-Z]{2})',
            title, re.UNICODE
        )
        if slash_match:
            cidade = slash_match.group(1).strip()
            estado = slash_match.group(2).strip()
            return (cidade, estado)

        return (None, None)

    @staticmethod
    def extract_bairro_from_description(html_text: str) -> Optional[str]:
        """Extract bairro (neighborhood) from property description"""
        try:
            # Pattern 1: "Bairro: Name" or "bairro: Name"
            pattern1 = r'(?:Bairro|bairro):\s*([A-Z][a-záàâãéèêíïóôõöúçñ\s-]+?)(?:\n|<br|$)'
            match = re.search(pattern1, html_text, re.IGNORECASE)
            if match:
                bairro = match.group(1).strip()
                bairro = re.sub(r'<[^>]+>', '', bairro).strip()
                if len(bairro) > 2 and len(bairro) < 100:
                    return bairro

            # Pattern 2: "no bairro de Name" or "no bairro Name"
            pattern2 = r'no\s+bairro\s+(?:de\s+)?([A-Z][a-záàâãéèêíïóôõöúçñ\s-]+?)(?:\n|<br|,|$)'
            match = re.search(pattern2, html_text, re.IGNORECASE)
            if match:
                bairro = match.group(1).strip()
                bairro = re.sub(r'<[^>]+>', '', bairro).strip()
                if len(bairro) > 2 and len(bairro) < 100:
                    return bairro

            # Pattern 3: Look in description blocks
            pattern3 = r'<p>([A-Z][a-záàâãéèêíïóôõöúçñ\s-]*),\s*(?:Bairro|bairro).*?</p>'
            match = re.search(pattern3, html_text, re.IGNORECASE)
            if match:
                bairro = match.group(1).strip()
                if len(bairro) > 2 and len(bairro) < 100:
                    return bairro

            return None

        except Exception as e:
            return None

    def scrape_property(self, url: str, title: str) -> Optional[Dict]:
        """Scrape single property for bairro info"""
        try:
            response = self.session.get(url, timeout=TIMEOUT)
            response.encoding = 'utf-8'
            html_text = response.text

            city, state = self.extract_city_from_title(title)
            if city:
                city = self.normalize_city_name(city)  # Normalize truncated names
            bairro = self.extract_bairro_from_description(html_text)

            if city and bairro:
                return {
                    'city': city,
                    'state': state,
                    'bairro': bairro,
                    'url': url
                }

            return None

        except Exception as e:
            return None

    def extract_all_bairros(self):
        """Extract bairros from all properties"""
        print("="*70)
        print(f"EXTRACTING BAIRROS FOR {len(self.large_cities)} LARGE CITIES")
        print("="*70 + "\n")

        auctions = self.get_all_auctions()

        print(f"Processing {len(auctions)} properties...\n")

        for i, auction in enumerate(auctions, 1):
            try:
                prop_data = self.scrape_property(auction['url'], auction['title'])

                if prop_data:
                    city = prop_data['city']
                    bairro = prop_data['bairro']

                    if city in self.large_cities:
                        self.bairros_by_city[city].add(bairro)
                        print(f"[{i:3d}] {city}: {bairro}")

                if i % 50 == 0:
                    print(f"[{i:3d}] Processing...", flush=True)

            except Exception as e:
                if i % 100 == 0:
                    print(f"[{i:3d}] Error: {e}", flush=True)
                continue

        print("\n" + "="*70)
        print("BAIRROS EXTRACTED:")
        print("="*70)

        total_bairros = 0
        for city in sorted(self.large_cities.keys()):
            bairro_list = sorted(list(self.bairros_by_city[city]))
            count = len(bairro_list)
            total_bairros += count

            print(f"\n{city} ({self.large_cities[city]:,} inhabitants): {count} bairros")
            if bairro_list:
                for bairro in bairro_list[:10]:  # Show first 10
                    print(f"  - {bairro}")
                if len(bairro_list) > 10:
                    print(f"  ... and {len(bairro_list) - 10} more")
            else:
                print("  (no bairros found)")

        print("\n" + "="*70)
        print(f"Total unique bairros: {total_bairros}")
        print("="*70 + "\n")

        return self.bairros_by_city

    def save_bairro_data(self, output_file: Path = None):
        """Save extracted bairros to JSON"""
        if output_file is None:
            output_file = Path("data/bairros_by_city.json")

        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Convert sets to lists for JSON serialization
        data = {
            city: sorted(list(bairros))
            for city, bairros in self.bairros_by_city.items()
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"[OK] Saved bairro data to {output_file}\n")

    def build_search_configuration(self, output_file: Path = None):
        """Build search configuration with bairro-level searches for large cities"""
        if output_file is None:
            output_file = Path("data/search_configuration_bairro.json")

        print("Building search configuration with bairro-level searches...\n")

        searches = []

        # Load existing search config, or create from CITY_POPULATION if not found
        existing_config = Path("data/search_configuration.json")
        if existing_config.exists():
            with open(existing_config, 'r', encoding='utf-8') as f:
                existing_searches = json.load(f)
        else:
            # No existing config - create from CITY_POPULATION
            from config import CITY_POPULATION
            existing_searches = []
            for city in CITY_POPULATION.keys():
                # Guess state (simplified - just use "SP" for most, "RJ" for Rio)
                state = "RJ" if "Janeiro" in city or "Jacare" in city else "SP"
                existing_searches.append({
                    'city': city,
                    'state': state,
                    'type': 'city',
                    'search_term': f"imoveis {city}",
                    'group_ids': [],
                    'group_details': []
                })
            print(f"Created {len(existing_searches)} city-level searches from CITY_POPULATION")

        # Process each search
        for search in existing_searches:
            city = search.get('city')
            state = search.get('state')

            # If small city, keep as-is
            if city not in self.large_cities:
                searches.append(search)
                print(f"[CITY] {city} (small city)")
                continue

            # For large city with bairros, create bairro-level searches
            if city in self.bairros_by_city and self.bairros_by_city[city]:
                for bairro in sorted(self.bairros_by_city[city]):
                    new_search = {
                        'city': city,
                        'state': state,
                        'type': 'bairro',
                        'search_term': f"{bairro} {city}",
                        'bairro': bairro,
                        'group_ids': [],
                        'group_details': []
                    }
                    searches.append(new_search)
                print(f"[BAIRRO] {city}: {len(self.bairros_by_city[city])} bairros")
            else:
                # Fallback to city search if no bairros found
                print(f"[CITY] {city} (no bairro data - fallback)")
                searches.append(search)

        # Save configuration
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(searches, f, ensure_ascii=False, indent=2)

        print(f"\n[OK] Saved to {output_file}")
        print(f"Total searches: {len(searches)}")

        city_count = sum(1 for s in searches if s.get('type') != 'bairro')
        bairro_count = sum(1 for s in searches if s.get('type') == 'bairro')
        print(f"  City-level: {city_count}")
        print(f"  Bairro-level: {bairro_count}\n")

    def run(self):
        """Main pipeline"""
        self.extract_all_bairros()
        self.save_bairro_data()
        self.build_search_configuration()

        print("="*70)
        print("BAIRRO EXTRACTION COMPLETE!")
        print("="*70)
        print("\nNext: Run Phase 3 with new configuration")
        print("  python phase3_simple_login.py --config data/search_configuration_bairro.json")
        print("="*70 + "\n")


if __name__ == '__main__':
    extractor = BairroExtractor()
    extractor.run()

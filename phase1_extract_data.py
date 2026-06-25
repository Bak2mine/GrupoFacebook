"""
Phase 1: Extract cities/neighborhoods from property data
Integrates with Post scraper to get property information automatically
"""

import sys
import json
import logging
from pathlib import Path
from collections import defaultdict

# Setup paths
GRUPO_DIR = Path(__file__).parent
POST_DIR = GRUPO_DIR.parent / "Post"
DATA_DIR = GRUPO_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Import Grupo config
from config import (
    LARGE_CITY_THRESHOLD, CITY_POPULATION, LOG_LEVEL, LOG_FORMAT
)

# Setup logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)
logger = logging.getLogger(__name__)

# Import PropertyScraper from Post folder (inline to avoid config conflicts)
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import time

# Use Post's configuration values directly
POST_BASE_URL = "https://leiloariasmart.com.br"
POST_MAIN_URL = "https://leiloariasmart.com.br/busca"
POST_HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
POST_TIMEOUT = 30

# Copy PropertyScraper class from Post/scraper.py to avoid import conflicts
class PropertyScraper:
    """Scrapes and extracts property data from leiloariasmart.com.br"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(POST_HEADERS)

    def get_all_auctions(self, limit=None):
        """Get all auctions from search page"""
        try:
            response = self.session.get(POST_MAIN_URL, timeout=POST_TIMEOUT)
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
                url = urljoin(POST_BASE_URL, link_tag['href'])
                auctions.append({'title': title, 'url': url})

                if limit and len(auctions) >= limit:
                    break

            logger.info(f"[OK] Found {len(auctions)} properties")
            return auctions

        except Exception as e:
            logger.error(f"[ERROR] Error fetching auctions: {e}")
            return []

    @staticmethod
    def split_by_em_dashes(title):
        """Split title by em-dashes and extract location and title parts."""
        parts = re.split(r'\s*[–—]\s*', title)

        if len(parts) == 3:
            titulo_clean = parts[0].strip()
            location_part = parts[1].strip()
            identifier = parts[2].strip()

            loc_match = re.search(r'([A-Z][a-záàâãéèêíïóôõöúçñ\s]+)/([A-Z]{2})', location_part)
            if loc_match:
                cidade = loc_match.group(1).strip()
                estado = loc_match.group(2).strip()
                titulo_clean = f"{titulo_clean} {identifier}".strip()
                return (titulo_clean, cidade, estado)

        elif len(parts) >= 2:
            titulo_clean = parts[0].strip()
            location_part = parts[1].strip()

            loc_match = re.search(r'([A-Z][a-záàâãéèêíïóôõöúçñ\s]+)/([A-Z]{2})', location_part)
            if loc_match:
                cidade = loc_match.group(1).strip()
                estado = loc_match.group(2).strip()
                return (titulo_clean, cidade, estado)

        return (None, None, None)

    @staticmethod
    def split_by_brackets(title):
        """Extract bracket content"""
        bracket_match = re.search(r'\(([^)]+)\)', title)
        if bracket_match:
            bracket_content = bracket_match.group(1)
            title_without_brackets = re.sub(r'\s*\([^)]+\)\s*', '', title)
            return (title_without_brackets, bracket_content)
        return (title, None)

    @staticmethod
    def split_by_separator_words(title):
        """Split by known separator words like 'cada', 'em', etc."""
        separator_words = ['cada', 'em']

        for word in separator_words:
            pattern = rf'^(.+?)\s+{word}\s+([A-Z][a-záàâãéèêíïóôõöúçñ\s]+)/([A-Z]{{2}})(?:\s|$)'
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                titulo_clean = match.group(1).strip()
                cidade = match.group(2).strip()
                estado = match.group(3).strip()
                return (titulo_clean, cidade, estado)

        return (None, None, None)

    def get_property_data(self, auction_url, auction_title):
        """Extract all relevant data from property page"""
        try:
            response = self.session.get(auction_url, timeout=POST_TIMEOUT)
            response.encoding = 'utf-8'
            html_text = response.text

            titulo_clean = None
            cidade = None
            estado = None

            titulo_clean, cidade, estado = self.split_by_em_dashes(auction_title)

            if not cidade:
                title_without_brackets, bracket_content = self.split_by_brackets(auction_title)
                titulo_clean, cidade, estado = self.split_by_em_dashes(title_without_brackets)
                if titulo_clean and bracket_content:
                    titulo_clean = f"{titulo_clean} ({bracket_content})"

            if not cidade:
                titulo_clean, cidade, estado = self.split_by_separator_words(auction_title)

            if not titulo_clean:
                titulo_clean = auction_title

            data = {
                'titulo': titulo_clean,
                'cidade': cidade,
                'estado': estado,
            }

            return data

        except Exception as e:
            logger.error(f"[ERROR] Error extracting data from {auction_url}: {e}")
            return None


class DataExtractor:
    """Extract cities and neighborhoods from property data"""

    def __init__(self):
        self.scraper = PropertyScraper()
        self.cities_data = defaultdict(lambda: {'neighborhoods': set(), 'state': None})

    def scrape_properties(self, limit=None):
        """Scrape properties from leiloariasmart.com.br

        Args:
            limit: Optional limit of properties to scrape

        Returns:
            List of property dictionaries
        """
        logger.info("Starting property scrape...")
        auctions = self.scraper.get_all_auctions(limit=limit)

        if not auctions:
            logger.error("No auctions found!")
            return []

        logger.info(f"Found {len(auctions)} auction listings")

        properties = []
        for i, auction in enumerate(auctions, 1):
            logger.info(f"[{i}/{len(auctions)}] Extracting data from {auction['title'][:60]}...")
            prop_data = self.scraper.get_property_data(auction['url'], auction['title'])
            if prop_data:
                properties.append(prop_data)

            # Small delay to be respectful to server
            if i % 5 == 0:
                import time
                time.sleep(1)

        return properties

    def extract_cities_neighborhoods(self, properties):
        """Extract unique cities and neighborhoods from properties

        Args:
            properties: List of property dictionaries

        Returns:
            Dict with cities and their metadata
        """
        logger.info(f"Extracting unique cities from {len(properties)} properties...")

        for prop in properties:
            cidade = prop.get('cidade')
            estado = prop.get('estado')

            if not cidade:
                continue

            # Normalize city name
            cidade = cidade.strip().title()

            self.cities_data[cidade]['state'] = estado

        logger.info(f"Found {len(self.cities_data)} unique cities")
        return dict(self.cities_data)

    def classify_cities_by_size(self, cities_data):
        """Classify cities as large (search by neighborhood) or small (search by city)

        Args:
            cities_data: Dict of city information

        Returns:
            Dict with 'large_cities' and 'small_cities'
        """
        logger.info("Classifying cities by population size...")

        large_cities = []
        small_cities = []

        for city_name, city_info in cities_data.items():
            population = CITY_POPULATION.get(city_name, 0)

            if population >= LARGE_CITY_THRESHOLD:
                large_cities.append({
                    'name': city_name,
                    'state': city_info.get('state'),
                    'population': population,
                    'search_type': 'neighborhood'
                })
                logger.info(f"  {city_name}: LARGE (pop: {population:,}) - search by neighborhood")
            else:
                small_cities.append({
                    'name': city_name,
                    'state': city_info.get('state'),
                    'population': population,
                    'search_type': 'city'
                })
                logger.info(f"  {city_name}: SMALL (pop: {population:,}) - search by city")

        return {
            'large_cities': large_cities,
            'small_cities': small_cities
        }

    def save_classification(self, classification, output_file):
        """Save classification to JSON file

        Args:
            classification: Dict with city classifications
            output_file: Path to save JSON
        """
        logger.info(f"Saving classification to {output_file}...")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(classification, f, ensure_ascii=False, indent=2)
        logger.info("Classification saved successfully")

    def run(self, limit=None, skip_scrape=False, input_file=None):
        """Main extraction pipeline

        Args:
            limit: Limit properties to scrape
            skip_scrape: Skip scraping if True (use existing data)
            input_file: Path to existing property JSON file

        Returns:
            Tuple of (properties, classification)
        """
        # Load or scrape properties
        if skip_scrape and input_file and Path(input_file).exists():
            logger.info(f"Loading existing properties from {input_file}...")
            with open(input_file, 'r', encoding='utf-8') as f:
                properties = json.load(f)
            logger.info(f"Loaded {len(properties)} properties")
        else:
            properties = self.scrape_properties(limit=limit)

            # Save scraped properties
            props_file = DATA_DIR / "scraped_properties.json"
            with open(props_file, 'w', encoding='utf-8') as f:
                json.dump(properties, f, ensure_ascii=False, indent=2)
            logger.info(f"Properties saved to {props_file}")

        # Extract cities
        cities_data = self.extract_cities_neighborhoods(properties)

        # Classify cities
        classification = self.classify_cities_by_size(cities_data)

        # Save classification
        class_file = DATA_DIR / "city_classification.json"
        self.save_classification(classification, class_file)

        logger.info("Phase 1 complete!")
        return properties, classification


def main():
    """Execute Phase 1"""
    import argparse

    parser = argparse.ArgumentParser(description='Phase 1: Extract property data')
    parser.add_argument('--limit', type=int, default=None, help='Limit properties to scrape')
    parser.add_argument('--skip-scrape', action='store_true', help='Skip scraping if data exists')
    parser.add_argument('--input-file', type=str, default=None, help='Path to existing property JSON')

    args = parser.parse_args()

    extractor = DataExtractor()
    properties, classification = extractor.run(
        limit=args.limit,
        skip_scrape=args.skip_scrape,
        input_file=args.input_file
    )

    logger.info(f"\nResults:")
    logger.info(f"  Large cities: {len(classification['large_cities'])}")
    logger.info(f"  Small cities: {len(classification['small_cities'])}")
    logger.info(f"  Total properties: {len(properties)}")


if __name__ == '__main__':
    main()

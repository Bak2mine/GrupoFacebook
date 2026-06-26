"""
Standalone script to scrape properties using Post/scraper.py
Generates Grupo/data/scraped_properties.json with proper city extraction
"""

import sys
import json
import logging
from pathlib import Path

# Add Post directory to path to import scraper
POST_DIR = Path(__file__).parent.parent / "Post"
sys.path.insert(0, str(POST_DIR))

from scraper import PropertyScraper

# Use Grupo data directory (not Post's)
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting property scraping...")

    # Initialize scraper
    scraper = PropertyScraper()

    # Get all auctions
    auctions = scraper.get_all_auctions()
    logger.info(f"Found {len(auctions)} properties to process")

    # Extract data for each property
    properties_data = []
    for i, auction in enumerate(auctions, 1):
        if i % 10 == 0:
            logger.info(f"Processing property {i}/{len(auctions)}...")

        try:
            data = scraper.get_property_data(auction['url'], auction['title'])
            if data:
                properties_data.append(data)
        except Exception as e:
            logger.debug(f"Error processing {auction['title']}: {e}")

    # Save to JSON
    output_file = DATA_DIR / "scraped_properties.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(properties_data, f, ensure_ascii=False, indent=2)

    # Report results
    logger.info("")
    logger.info("="*70)
    logger.info("SCRAPING COMPLETE")
    logger.info("="*70)
    logger.info(f"Total properties: {len(auctions)}")
    logger.info(f"With city/state: {sum(1 for p in properties_data if p.get('cidade'))}")
    logger.info(f"Success rate: {100*sum(1 for p in properties_data if p.get('cidade'))/len(auctions):.1f}%")
    logger.info(f"Saved to: {output_file}")
    logger.info("="*70)
    logger.info("")

    return True

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

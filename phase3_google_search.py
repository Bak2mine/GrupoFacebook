"""
Phase 3: Search Google for Facebook group IDs
Uses multiple search patterns to find relevant Facebook groups
"""

import re
import json
import logging
import time
from pathlib import Path
from typing import List, Set
from urllib.parse import urlparse
import requests
from config import DATA_DIR, GOOGLE_SEARCH_PATTERNS, LOG_LEVEL, LOG_FORMAT

# Setup logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)
logger = logging.getLogger(__name__)

# Note: This uses requests library for educational purposes
# In production, consider using google-api-client or selenium
class GoogleGroupSearcher:
    """Search Google for Facebook group IDs using site: queries"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.found_group_ids = set()
        self.failed_searches = []

    def extract_facebook_group_id(self, url: str) -> str:
        """Extract numeric ID from Facebook group URL

        Args:
            url: Facebook group URL

        Returns:
            Numeric group ID or empty string if not found
        """
        # Pattern: facebook.com/groups/NUMERIC_ID or facebook.com/groups/GROUP_NAME
        match = re.search(r'facebook\.com/groups/(\d+)', url)
        if match:
            return match.group(1)

        # Also try to extract alphanumeric IDs
        match = re.search(r'facebook\.com/groups/([a-zA-Z0-9._-]+)', url)
        if match:
            group_id = match.group(1)
            # Only return if it's numeric
            if group_id.isdigit():
                return group_id

        return ""

    def search_google(self, search_term: str, pattern: str = None) -> List[str]:
        """Search Google for Facebook group URLs

        Args:
            search_term: Term to search for (city/neighborhood)
            pattern: Optional search pattern (default: first pattern in config)

        Returns:
            List of found group IDs
        """
        if pattern is None:
            pattern = GOOGLE_SEARCH_PATTERNS[0]

        query = pattern.format(search_term=search_term)
        logger.debug(f"Searching: {query}")

        group_ids = []

        try:
            from urllib.parse import quote

            # Properly encode the query
            encoded_query = quote(query)
            url = f"https://www.google.com/search?q={encoded_query}"

            logger.debug(f"URL: {url}")

            response = self.session.get(url, timeout=10)
            response.encoding = 'utf-8'

            # Look for Facebook group URLs in multiple patterns
            # Pattern 1: Full URLs with numeric IDs
            fb_urls = re.findall(r'https://www\.facebook\.com/groups/(\d+)', response.text)
            for fb_id in fb_urls:
                if fb_id not in self.found_group_ids:
                    group_ids.append(fb_id)
                    self.found_group_ids.add(fb_id)

            # Pattern 2: Alphanumeric group names
            fb_urls_alpha = re.findall(r'https://www\.facebook\.com/groups/([\w\.-]+)(?:[/?]|\")', response.text)
            for fb_url in fb_urls_alpha:
                # Only accept if looks like numeric
                if fb_url.isdigit() and fb_url not in self.found_group_ids:
                    group_ids.append(fb_url)
                    self.found_group_ids.add(fb_url)

            if not group_ids:
                logger.debug(f"  No Facebook URLs found in response")

        except requests.exceptions.RequestException as e:
            logger.warning(f"Search failed for '{search_term}': {e}")
            self.failed_searches.append(search_term)
        except Exception as e:
            logger.warning(f"Error processing search results: {e}")
            self.failed_searches.append(search_term)

        return group_ids

    def search_multiple_patterns(self, search_term: str) -> List[str]:
        """Search using multiple patterns to find more results

        Args:
            search_term: Term to search for

        Returns:
            List of found group IDs
        """
        all_group_ids = []

        for pattern in GOOGLE_SEARCH_PATTERNS:
            group_ids = self.search_google(search_term, pattern)
            all_group_ids.extend(group_ids)
            time.sleep(1)  # Be respectful to Google

        return all_group_ids

    def process_searches(self, searches: List[dict]) -> List[dict]:
        """Process all searches and populate group IDs

        Args:
            searches: List of search configurations from phase 2

        Returns:
            Updated searches with group IDs
        """
        logger.info(f"Processing {len(searches)} searches...")

        for i, search in enumerate(searches, 1):
            search_term = search.get('search_term')
            city = search.get('city')

            logger.info(f"[{i}/{len(searches)}] Searching for groups in {city}...")

            group_ids = self.search_multiple_patterns(search_term)

            if group_ids:
                search['group_ids'] = group_ids
                logger.info(f"  Found {len(group_ids)} groups: {group_ids[:5]}{'...' if len(group_ids) > 5 else ''}")
            else:
                logger.warning(f"  No groups found for {search_term}")

            # Save progress periodically
            if (i % 5) == 0:
                logger.info(f"Progress: {i}/{len(searches)} searches completed")

        return searches

    def save_results(self, searches, output_file):
        """Save search results to JSON

        Args:
            searches: List of searches with group IDs
            output_file: Path to save results
        """
        logger.info(f"Saving results to {output_file}...")

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(searches, f, ensure_ascii=False, indent=2)

        logger.info("Results saved successfully")

    def get_statistics(self, searches):
        """Print statistics about search results

        Args:
            searches: List of searches
        """
        total_ids = sum(len(s.get('group_ids', [])) for s in searches)
        unique_ids = len(self.found_group_ids)
        successful = len([s for s in searches if s.get('group_ids')])

        logger.info("\n=== Search Statistics ===")
        logger.info(f"  Searches completed: {len(searches)}")
        logger.info(f"  Searches with results: {successful}")
        logger.info(f"  Total IDs found: {total_ids}")
        logger.info(f"  Unique IDs: {unique_ids}")
        logger.info(f"  Failed searches: {len(self.failed_searches)}")

        if self.failed_searches:
            logger.info(f"  Failed: {', '.join(self.failed_searches[:5])}")

    def run(self, searches_file):
        """Main pipeline

        Args:
            searches_file: Path to search configuration from phase 2

        Returns:
            Updated searches with group IDs
        """
        logger.info(f"Loading searches from {searches_file}...")

        with open(searches_file, 'r', encoding='utf-8') as f:
            searches = json.load(f)

        # Process searches
        searches = self.process_searches(searches)

        # Save results
        results_file = DATA_DIR / "searches_with_group_ids.json"
        self.save_results(searches, results_file)

        # Print statistics
        self.get_statistics(searches)

        logger.info("Phase 3 complete!")
        return searches


def main():
    """Execute Phase 3"""
    import argparse

    parser = argparse.ArgumentParser(description='Phase 3: Search Google for Facebook group IDs')
    parser.add_argument('--input', type=str, default=str(DATA_DIR / "search_configuration.json"),
                        help='Path to search configuration from phase 2')

    args = parser.parse_args()

    searcher = GoogleGroupSearcher()
    searches = searcher.run(args.input)

    logger.info(f"\nResults saved to {DATA_DIR / 'searches_with_group_ids.json'}")


if __name__ == '__main__':
    main()

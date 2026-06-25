"""
Phase 3: Scrape Facebook groups using Playwright
Direct scraping from Facebook group search - no API needed!
"""

import json
import logging
import time
from typing import List, Dict
from pathlib import Path
from urllib.parse import quote

from playwright.sync_api import sync_playwright, Page
from config import DATA_DIR, LOG_LEVEL, LOG_FORMAT

# Setup logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)
logger = logging.getLogger(__name__)


class FacebookGroupScraper:
    """Scrape Facebook groups from search results using Playwright"""

    def __init__(self, headless: bool = True):
        """
        Initialize Playwright browser

        Args:
            headless: Run browser in headless mode (no UI)
        """
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.page = None

    def start_browser(self):
        """Start Playwright browser"""
        logger.info("Starting Playwright browser...")
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.page = self.browser.new_page()
        logger.info("Browser started successfully")

    def stop_browser(self):
        """Stop Playwright browser"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        logger.info("Browser stopped")

    def scrape_groups(self, city: str, state: str, limit: int = 10) -> List[Dict]:
        """
        Scrape Facebook groups for a city

        Args:
            city: City name
            state: State code
            limit: Maximum groups to extract (default: 10)

        Returns:
            List of group dicts with id, name, url
        """
        try:
            search_query = f"{city} {state} imobiliário"
            encoded_query = quote(search_query)
            url = f"https://www.facebook.com/groups/search/groups_home/?q={encoded_query}"

            logger.info(f"Scraping groups for {city}...")
            logger.debug(f"URL: {url}")

            # Navigate to the page
            try:
                self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
            except Exception as e:
                logger.warning(f"Page load warning for {city}: {e}")
                # Continue anyway - might still have content

            time.sleep(3)  # Wait for content to load

            # Try to get page HTML
            html_content = self.page.content()
            logger.debug(f"Page loaded, content length: {len(html_content)}")

            # Check if we need to login
            if "login" in html_content.lower() and len(html_content) < 50000:
                logger.warning(f"Facebook login might be required for {city}")

            # Scroll down to load more groups via infinite scroll
            logger.debug(f"Scrolling to load groups...")
            for i in range(4):  # Scroll 4 times
                try:
                    self.page.evaluate("window.scrollBy(0, window.innerHeight)")
                    time.sleep(1)
                except:
                    pass

            # Extract group links using multiple selector strategies
            groups = []

            # Strategy 1: Look for links with group IDs in href
            try:
                # Get all <a> tags that have /groups/ in href
                link_elements = self.page.query_selector_all('a[href*="/groups/"]')
                logger.debug(f"Found {len(link_elements)} links with /groups/ in href")

                for element in link_elements:
                    if len(groups) >= limit:
                        break

                    try:
                        href = element.get_attribute("href") or ""
                        text = element.inner_text() or ""

                        if not href or not text or len(text) < 2:
                            continue

                        # Skip if it's a link to create a group or other UI elements
                        if any(skip in text.lower() for skip in ["create", "browse", "home", "search", "suggestions"]):
                            continue

                        # Extract group ID from href
                        # href format: /groups/810414915422393/ or /groups/810414915422393
                        if "/groups/" in href:
                            parts = href.strip("/").split("/")
                            try:
                                group_idx = parts.index("groups")
                                if group_idx + 1 < len(parts):
                                    group_id = parts[group_idx + 1]
                                    if group_id.isdigit() and len(group_id) >= 6:
                                        groups.append({
                                            "id": group_id,
                                            "name": text.strip(),
                                            "url": f"https://www.facebook.com/groups/{group_id}/"
                                        })
                                        logger.debug(f"  Found: {text.strip()[:50]}... ({group_id})")
                            except (ValueError, IndexError):
                                pass

                    except Exception as e:
                        logger.debug(f"Error extracting group: {e}")
                        continue

            except Exception as e:
                logger.warning(f"Error with link extraction for {city}: {e}")

            logger.info(f"  Scraped {len(groups)} groups for {city}")
            return groups

        except Exception as e:
            logger.error(f"Error scraping groups for {city}: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return []

    def process_searches(self, searches: List[dict], groups_per_city: int = 10) -> List[dict]:
        """
        Process all searches and scrape groups

        Args:
            searches: List of search configurations from phase 2
            groups_per_city: Max groups to fetch per city (default: 10)

        Returns:
            Updated searches with scraped group data
        """
        self.start_browser()

        try:
            logger.info(f"Processing {len(searches)} searches...")

            for i, search in enumerate(searches, 1):
                city = search.get('city', 'Unknown')
                state = search.get('state', '')

                logger.info(f"[{i}/{len(searches)}] Searching for groups in {city}...")

                # Scrape groups for this city
                groups = self.scrape_groups(city, state, limit=groups_per_city)

                if groups:
                    search['group_ids'] = [g['id'] for g in groups]
                    search['group_details'] = groups
                    logger.info(f"  Found {len(groups)} real groups for {city}")
                else:
                    search['group_ids'] = []
                    search['group_details'] = []
                    logger.warning(f"  No groups found for {city}")

                time.sleep(1)  # Rate limiting between cities

            logger.info("Scraping complete!")
            return searches

        finally:
            self.stop_browser()

    def save_results(self, searches: List[dict], output_file: Path):
        """
        Save scraping results to JSON

        Args:
            searches: List of searches with group data
            output_file: Path to save JSON
        """
        logger.info(f"Saving results to {output_file}...")

        # Prepare data for JSON
        data_to_save = []
        for search in searches:
            search_data = {
                'city': search.get('city'),
                'state': search.get('state'),
                'type': search.get('type'),
                'search_term': search.get('search_term'),
                'group_ids': search.get('group_ids', []),
                'group_details': search.get('group_details', [])
            }
            data_to_save.append(search_data)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=2)

        logger.info("Results saved successfully")

    def run(self, searches_file: Path) -> List[dict]:
        """
        Main pipeline

        Args:
            searches_file: Path to search configuration from phase 2

        Returns:
            Updated searches with scraped group data
        """
        logger.info(f"Loading searches from {searches_file}...")

        with open(searches_file, 'r', encoding='utf-8') as f:
            searches = json.load(f)

        # Process searches
        searches = self.process_searches(searches, groups_per_city=10)

        # Save results
        results_file = DATA_DIR / "searches_with_group_ids.json"
        self.save_results(searches, results_file)

        total_groups = sum(len(s.get('group_ids', [])) for s in searches)
        logger.info(f"Phase 3 (Web Scraping) complete! Found {total_groups} groups")

        return searches


def main():
    """Execute Phase 3 with web scraping"""
    import argparse

    parser = argparse.ArgumentParser(description='Phase 3: Scrape Facebook groups using Playwright')
    parser.add_argument('--input', type=str, default=str(DATA_DIR / "search_configuration.json"),
                        help='Path to search configuration from phase 2')
    parser.add_argument('--headless', action='store_true', default=True,
                        help='Run browser in headless mode (default: True)')
    parser.add_argument('--no-headless', dest='headless', action='store_false',
                        help='Show browser window during scraping')

    args = parser.parse_args()

    scraper = FacebookGroupScraper(headless=args.headless)
    searches = scraper.run(Path(args.input))

    total_groups = sum(len(s.get('group_ids', [])) for s in searches)
    logger.info(f"Total groups found: {total_groups}")


if __name__ == '__main__':
    main()

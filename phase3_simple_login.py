"""
Phase 3: Simple Facebook scraping with login
Opens browser, you log in, then scrapes groups automatically
"""

import json
import logging
import time
from typing import List, Dict
from pathlib import Path
from urllib.parse import quote

from playwright.sync_api import sync_playwright
from config import DATA_DIR, LOG_LEVEL, LOG_FORMAT

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

COOKIES_FILE = Path("facebook_cookies.json")


class FacebookScraper:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None

    def start(self):
        logger.info("\n" + "="*70)
        logger.info("  STARTING FACEBOOK GROUP SCRAPER")
        logger.info("="*70 + "\n")

        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False)
        self.page = self.browser.new_page()

        # Load saved cookies if they exist
        if COOKIES_FILE.exists():
            with open(COOKIES_FILE, 'r') as f:
                cookies = json.load(f)
                self.page.context.add_cookies(cookies)
                logger.info(f"✓ Loaded saved cookies from {COOKIES_FILE}\n")

    def check_login(self):
        """Check if we're logged in, if not prompt user to log in"""
        logger.info("Checking if you're logged in to Facebook...")
        self.page.goto("https://www.facebook.com", wait_until="domcontentloaded", timeout=30000)
        time.sleep(2)

        # If we see login form, we need to log in
        if self.page.query_selector('[name="email"]') or "login" in self.page.url.lower():
            logger.info("\n" + "!"*70)
            logger.info("  NOT LOGGED IN - PLEASE LOG IN NOW")
            logger.info("!"*70)
            logger.info("")
            logger.info("A browser window has opened with Facebook login page.")
            logger.info("")
            logger.info("STEPS:")
            logger.info("  1. Log in with your Facebook account")
            logger.info("  2. Wait for Facebook to load fully")
            logger.info("  3. Come back to this terminal")
            logger.info("  4. Press Enter when you're done\n")
            logger.info("="*70 + "\n")

            input("Press Enter after you've logged in...")
            time.sleep(3)

            # Save cookies after login
            self.save_cookies()
            logger.info("\n✓ Cookies saved! Next time login will be automatic.\n")
        else:
            logger.info("✓ Already logged in!\n")
            self.save_cookies()

    def save_cookies(self):
        """Save cookies to file"""
        try:
            cookies = self.page.context.cookies()
            with open(COOKIES_FILE, 'w') as f:
                json.dump(cookies, f, indent=2)
            logger.info(f"✓ Saved {len(cookies)} cookies")
        except Exception as e:
            logger.error(f"Could not save cookies: {e}")

    def scrape_groups(self, city: str, state: str, limit: int = 10) -> List[Dict]:
        """Scrape groups for a city"""
        try:
            search_query = f"{city} {state} imobiliário"
            encoded_query = quote(search_query)
            url = f"https://www.facebook.com/groups/search/groups_home/?q={encoded_query}"

            print(f"  Searching: {city}...", end=" ", flush=True)

            self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(2)

            # Scroll to load groups
            for i in range(5):
                self.page.evaluate("window.scrollBy(0, window.innerHeight)")
                time.sleep(0.5)

            # Extract groups
            groups = []
            link_elements = self.page.query_selector_all('a[href*="/groups/"]')

            seen_ids = set()
            for element in link_elements:
                if len(groups) >= limit:
                    break

                try:
                    href = element.get_attribute("href") or ""
                    text = element.inner_text() or ""

                    if not href or not text or len(text) < 3:
                        continue

                    # Skip UI elements
                    if any(x in text.lower() for x in ["create", "browse", "home", "search", "join", "suggestions"]):
                        continue

                    # Extract group ID
                    if "/groups/" in href:
                        parts = href.strip("/").split("/")
                        try:
                            idx = parts.index("groups")
                            if idx + 1 < len(parts):
                                group_id = parts[idx + 1]

                                if len(group_id) >= 6 and group_id[0].isdigit() and group_id not in seen_ids:
                                    seen_ids.add(group_id)
                                    groups.append({
                                        "id": group_id,
                                        "name": text.strip()[:100],
                                        "url": f"https://www.facebook.com/groups/{group_id}/"
                                    })
                        except (ValueError, IndexError):
                            pass

                except Exception as e:
                    pass

            print(f"Found {len(groups)} groups")
            return groups

        except Exception as e:
            print(f"Error: {e}")
            return []

    def process_searches(self, searches: List[dict]) -> List[dict]:
        """Process all searches"""
        logger.info("\n" + "="*70)
        logger.info(f"SCRAPING {len(searches)} CITIES FOR FACEBOOK GROUPS")
        logger.info("="*70 + "\n")

        for i, search in enumerate(searches, 1):
            city = search.get('city', 'Unknown')
            state = search.get('state', '')

            print(f"[{i:2d}/{len(searches)}]", end=" ", flush=True)
            groups = self.scrape_groups(city, state, limit=10)

            if groups:
                search['group_ids'] = [g['id'] for g in groups]
                search['group_details'] = groups
            else:
                search['group_ids'] = []
                search['group_details'] = []

            time.sleep(1)

        logger.info("\n" + "="*70)
        logger.info("SCRAPING COMPLETE!")
        logger.info("="*70 + "\n")

        return searches

    def save_results(self, searches: List[dict]):
        """Save results"""
        data = [
            {
                'city': s.get('city'),
                'state': s.get('state'),
                'type': s.get('type'),
                'search_term': s.get('search_term'),
                'group_ids': s.get('group_ids', []),
                'group_details': s.get('group_details', [])
            }
            for s in searches
        ]

        output_file = DATA_DIR / "searches_with_group_ids.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        total_groups = sum(len(s.get('group_ids', [])) for s in searches)
        logger.info(f"✓ Saved results to {output_file}")
        logger.info(f"✓ Total groups found: {total_groups}\n")

    def stop(self):
        """Close browser"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        logger.info("Browser closed.")

    def run(self, searches_file: Path):
        """Main pipeline"""
        try:
            self.start()
            self.check_login()

            with open(searches_file, 'r', encoding='utf-8') as f:
                searches = json.load(f)

            searches = self.process_searches(searches)
            self.save_results(searches)

            logger.info("="*70)
            logger.info("SUCCESS! Continue pipeline with: python phase6_build_excel.py")
            logger.info("="*70 + "\n")

        finally:
            self.stop()


if __name__ == '__main__':
    scraper = FacebookScraper()
    scraper.run(DATA_DIR / "search_configuration.json")

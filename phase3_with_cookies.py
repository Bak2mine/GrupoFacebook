"""
Phase 3: Scrape Facebook groups using authenticated cookies
This bypasses login requirements by using your existing Facebook session
"""

import os
import sys

# Force Playwright to look outside the temporary EXE folder
if getattr(sys, 'frozen', False):
    # Running as PyInstaller .exe - use actual ms-playwright folder
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.expanduser(r"~\AppData\Local\ms-playwright")
else:
    # Running normally in venv - use default system pathing
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "0"

import json
import logging
import time
from typing import List, Dict
from pathlib import Path
from urllib.parse import quote

from playwright.sync_api import sync_playwright
from config import DATA_DIR, LOG_LEVEL, LOG_FORMAT, FACEBOOK_COOKIES

# Setup logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)
logger = logging.getLogger(__name__)

# Path to store cookies (fallback if not in config)
# Look for cookies file next to the .exe when frozen, otherwise next to the script
if getattr(sys, 'frozen', False):
    COOKIES_FILE = Path(sys.executable).parent / "facebook_cookies.json"
else:
    COOKIES_FILE = Path(__file__).parent / "facebook_cookies.json"


class FacebookGroupScraper:
    """Scrape Facebook groups using authenticated session"""

    def __init__(self, headless: bool = False):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.page = None

    def start_browser(self):
        """Start Playwright browser using system Chrome only"""
        logger.info("Starting browser...")
        self.playwright = sync_playwright().start()

        # Use ONLY system Chrome, never Chromium
        user_data_dir = str(Path.home() / ".leiloaria-browser-data")

        # Try explicit Chrome path first
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ]

        chrome_found = False
        for chrome_path in chrome_paths:
            if Path(chrome_path).exists():
                try:
                    logger.info(f"Launching Google Chrome from {chrome_path}...")
                    self.browser = self.playwright.chromium.launch_persistent_context(
                        user_data_dir=user_data_dir,
                        executable_path=chrome_path,
                        headless=self.headless
                    )
                    self.page = self.browser.new_page()
                    logger.info("Successfully launched Google Chrome")
                    chrome_found = True
                    break
                except Exception as e:
                    logger.debug(f"Chrome path failed: {e}")
                    continue

        if not chrome_found:
            # Fallback to channel method
            try:
                logger.info("Trying Chrome via channel...")
                self.browser = self.playwright.chromium.launch_persistent_context(
                    user_data_dir=user_data_dir,
                    channel="chrome",
                    headless=self.headless
                )
                self.page = self.browser.new_page()
                logger.info("Successfully launched Google Chrome via channel")
            except Exception as e:
                logger.error(f"Failed to launch Chrome: {e}")
                logger.error("Make sure Google Chrome is installed at:")
                logger.error("  C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe")
                raise

        # Load cookies - priority: config.py > facebook_cookies.json
        cookies = None
        if FACEBOOK_COOKIES:
            cookies = FACEBOOK_COOKIES
            logger.info(f"Using {len(cookies)} cookies from config.py")
        elif COOKIES_FILE.exists():
            with open(COOKIES_FILE, 'r') as f:
                cookies = json.load(f)
            logger.info(f"Using {len(cookies)} cookies from {COOKIES_FILE}")

        if cookies:
            self.page.context.add_cookies(cookies)
            logger.info("Cookies loaded - using saved Facebook session")

        logger.info("Browser started successfully")

    def stop_browser(self):
        """Stop Playwright browser"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        logger.info("Browser stopped")

    def save_cookies(self):
        """Save cookies for future use"""
        try:
            cookies = self.page.context.cookies()
            with open(COOKIES_FILE, 'w') as f:
                json.dump(cookies, f, indent=2)
            logger.info(f"Saved {len(cookies)} cookies to {COOKIES_FILE}")
        except Exception as e:
            logger.warning(f"Could not save cookies: {e}")

    def login_if_needed(self):
        """Check if login is needed and open Facebook for login"""
        logger.info("Checking if logged in...")
        self.page.goto("https://www.facebook.com", wait_until="domcontentloaded")
        time.sleep(2)

        # Check if we're on login page
        if "login" in self.page.url.lower() or self.page.query_selector('[name="email"]'):
            logger.warning("Not logged in! Please log in manually...")
            logger.info("Browser window is open. Log in to Facebook, then close the script.")
            logger.info("Press Enter after you've logged in...")
            input()
            time.sleep(2)

            # Save cookies after login
            self.save_cookies()
            logger.info("Cookies saved! You can now close the script.")
        else:
            logger.info("Already logged in!")
            self.save_cookies()

    def scrape_groups(self, city: str, state: str, limit: int = 10) -> List[Dict]:
        """Scrape Facebook groups for a city using authenticated session"""
        try:
            # Try multiple search queries
            search_queries = [
                f"{city} {state} imobiliário",
                f"imóveis {city}",
                f"grupos imobiliários {city}",
                f"{city} compra venda imóveis",
            ]

            all_groups = []

            for search_query in search_queries:
                if len(all_groups) >= limit:
                    break

                encoded_query = quote(search_query)
                url = f"https://www.facebook.com/groups/search/groups_home/?q={encoded_query}"

                logger.debug(f"Searching: {search_query}")

                try:
                    self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    time.sleep(2)

                    # Scroll to load more groups
                    for i in range(5):
                        if len(all_groups) >= limit:
                            break

                        self.page.evaluate("window.scrollBy(0, window.innerHeight)")
                        time.sleep(0.5)

                    # Extract groups from current page
                    groups = self._extract_groups_from_page(limit - len(all_groups))
                    all_groups.extend(groups)

                except Exception as e:
                    logger.debug(f"Error with query '{search_query}': {e}")
                    continue

            logger.info(f"Scraped {len(all_groups)} groups for {city}")
            return all_groups[:limit]

        except Exception as e:
            logger.error(f"Error scraping groups for {city}: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return []

    def _extract_groups_from_page(self, limit: int) -> List[Dict]:
        """Extract group data from current page"""
        groups = []

        try:
            # Find all group links
            link_elements = self.page.query_selector_all('a[href*="/groups/"]')
            logger.debug(f"Found {len(link_elements)} group links")

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
                    if any(x in text.lower() for x in ["create", "browse", "home", "search", "join", "create group", "suggestions", "back"]):
                        continue

                    # Extract group ID
                    if "/groups/" in href:
                        parts = href.strip("/").split("/")
                        try:
                            group_idx = parts.index("groups")
                            if group_idx + 1 < len(parts):
                                group_id = parts[group_idx + 1]

                                # Validate ID (should be mostly digits, 6+ chars)
                                if len(group_id) >= 6 and group_id[0].isdigit():
                                    if group_id not in seen_ids:
                                        seen_ids.add(group_id)
                                        groups.append({
                                            "id": group_id,
                                            "name": text.strip()[:100],
                                            "url": f"https://www.facebook.com/groups/{group_id}/"
                                        })
                                        logger.debug(f"  → {text.strip()[:50]}... ({group_id})")

                        except (ValueError, IndexError):
                            pass

                except Exception as e:
                    logger.debug(f"Error extracting group element: {e}")
                    continue

        except Exception as e:
            logger.warning(f"Error extracting groups from page: {e}")

        return groups

    def process_searches(self, searches: List[dict], groups_per_city: int = 10) -> List[dict]:
        """Process all searches"""
        self.start_browser()

        try:
            # Check if we need to login
            self.login_if_needed()

            logger.info(f"Processing {len(searches)} searches...")

            for i, search in enumerate(searches, 1):
                city = search.get('city', 'Unknown')
                state = search.get('state', '')

                logger.info(f"[{i}/{len(searches)}] Searching for groups in {city}...")

                groups = self.scrape_groups(city, state, limit=groups_per_city)

                if groups:
                    search['group_ids'] = [g['id'] for g in groups]
                    search['group_details'] = groups
                else:
                    search['group_ids'] = []
                    search['group_details'] = []

                time.sleep(1)

            logger.info("Scraping complete!")
            return searches

        finally:
            self.stop_browser()

    def save_results(self, searches: List[dict], output_file: Path):
        """Save results to JSON"""
        logger.info(f"Saving results to {output_file}...")

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
        """Main pipeline"""
        logger.info(f"Loading searches from {searches_file}...")

        with open(searches_file, 'r', encoding='utf-8') as f:
            searches = json.load(f)

        searches = self.process_searches(searches, groups_per_city=10)

        results_file = DATA_DIR / "searches_with_group_ids.json"
        self.save_results(searches, results_file)

        total_groups = sum(len(s.get('group_ids', [])) for s in searches)
        logger.info(f"Phase 3 complete! Found {total_groups} real groups")

        return searches


def main():
    """Execute Phase 3 with cookies"""
    import argparse

    parser = argparse.ArgumentParser(description='Phase 3: Scrape Facebook groups with authentication')
    parser.add_argument('--input', type=str, default=str(DATA_DIR / "search_configuration.json"),
                        help='Path to search configuration from phase 2')
    parser.add_argument('--show-browser', action='store_true',
                        help='Show browser window during scraping')

    args = parser.parse_args()

    scraper = FacebookGroupScraper(headless=not args.show_browser)
    searches = scraper.run(Path(args.input))

    total_groups = sum(len(s.get('group_ids', [])) for s in searches)
    logger.info(f"Total real groups found: {total_groups}")


if __name__ == '__main__':
    main()

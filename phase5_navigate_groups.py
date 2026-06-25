"""
Phase 5: Navigate Facebook groups and capture real names
Uses Playwright for automated browser navigation (no Claude Cowork needed)
"""

import json
import logging
import re
import time
from pathlib import Path
from typing import Dict, List, Optional
from config import (
    DATA_DIR, GROUP_NAMES_JSON, SAVE_INTERVAL, RETRY_ATTEMPTS,
    LOG_LEVEL, LOG_FORMAT
)

# Setup logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)
logger = logging.getLogger(__name__)

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning("Playwright not available - install with: pip install playwright")


class GroupNameNavigator:
    """Navigate Facebook groups and capture real group names using Playwright"""

    def __init__(self):
        self.group_names = {}  # Map group_id -> group_name
        self.private_groups = set()  # IDs of private groups
        self.failed_ids = []  # IDs that failed to load
        self.browser = None
        self.context = None

    def load_existing_names(self, json_file):
        """Load previously captured group names

        Args:
            json_file: Path to group_names.json

        Returns:
            Dict of group_id -> name
        """
        if Path(json_file).exists():
            with open(json_file, 'r', encoding='utf-8') as f:
                self.group_names = json.load(f)
            logger.info(f"Loaded {len(self.group_names)} existing group names")
            return self.group_names
        return {}

    def save_group_names(self, json_file):
        """Save captured group names to JSON

        Args:
            json_file: Path to save group_names.json
        """
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.group_names, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved {len(self.group_names)} group names")

    def get_missing_ids(self, all_ids):
        """Get list of IDs that still need names

        Args:
            all_ids: List of all group IDs

        Returns:
            List of IDs missing group names
        """
        missing = []
        for group_id in all_ids:
            if group_id not in self.group_names and group_id not in self.private_groups:
                missing.append(group_id)
        return missing

    def extract_group_name_from_title(self, page_title: str) -> Optional[str]:
        """Extract group name from browser page title

        Pattern: (N+) GROUP_NAME | Facebook

        Args:
            page_title: Title from browser tab

        Returns:
            Cleaned group name or None if generic Facebook title
        """
        if not page_title:
            return None

        title = page_title.replace('| Facebook', '').strip()
        title = re.sub(r'^\(\d+\+?\)\s*', '', title).strip()

        if title.lower() in ['facebook', '']:
            return None

        return title

    def navigate_and_capture(self, group_id: str, page) -> Optional[str]:
        """Navigate to a Facebook group and capture its name

        Args:
            group_id: Numeric Facebook group ID
            page: Playwright page object

        Returns:
            Group name or None if private/failed
        """
        try:
            url = f"https://www.facebook.com/groups/{group_id}"
            logger.debug(f"Navigating to {url}...")

            page.goto(url, wait_until="domcontentloaded", timeout=10000)
            time.sleep(1)  # Wait for title to update

            page_title = page.title()
            logger.debug(f"  Page title: {page_title}")

            group_name = self.extract_group_name_from_title(page_title)

            if group_name:
                logger.info(f"  [OK] {group_id}: {group_name}")
                return group_name
            else:
                logger.info(f"  [PRIVATE] {group_id}: Private group")
                self.private_groups.add(group_id)
                return "Grupo Privado"

        except Exception as e:
            logger.warning(f"  [FAIL] {group_id}: Failed - {e}")
            self.failed_ids.append(group_id)
            return None

    def navigate_batch(self, group_ids: List[str], browser_page) -> Dict[str, str]:
        """Navigate batch of groups sequentially and capture names

        Args:
            group_ids: List of group IDs to navigate
            browser_page: Playwright page object

        Returns:
            Dict mapping group_id -> group_name
        """
        captured = {}
        for group_id in group_ids:
            name = self.navigate_and_capture(group_id, browser_page)
            if name:
                self.group_names[group_id] = name
                captured[group_id] = name

        return captured

    def print_progress_summary(self, all_ids: List[str]):
        """Print progress summary

        Args:
            all_ids: Total list of all group IDs
        """
        total = len(all_ids)
        captured = len(self.group_names)
        private = len(self.private_groups)
        failed = len(self.failed_ids)
        missing = total - captured - private - failed

        logger.info("\n" + "="*70)
        logger.info("PROGRESS SUMMARY")
        logger.info("="*70)
        logger.info(f"Total groups to navigate: {total}")

        if total > 0:
            logger.info(f"Captured names: {captured} ({100*captured/total:.1f}%)")
            logger.info(f"Private groups: {private} ({100*private/total:.1f}%)")
            logger.info(f"Failed to load: {failed} ({100*failed/total:.1f}%)")
            logger.info(f"Still needed: {missing} ({100*missing/total:.1f}%)")
        else:
            logger.info("No groups to process")

    def run(self, unique_ids_file, resume=False):
        """Main pipeline - Navigate all Facebook groups

        Args:
            unique_ids_file: Path to unique group IDs from phase 4
            resume: Resume from existing group_names.json

        Returns:
            Dict of group_id -> group_name
        """
        if not PLAYWRIGHT_AVAILABLE:
            logger.error("Playwright not installed!")
            logger.error("Install with: pip install playwright")
            logger.error("Then run: playwright install")
            return None

        logger.info(f"Loading unique group IDs from {unique_ids_file}...")

        with open(unique_ids_file, 'r', encoding='utf-8') as f:
            all_ids = json.load(f)

        logger.info(f"Loaded {len(all_ids)} unique group IDs")

        # Load existing names if resuming
        if resume:
            self.load_existing_names(GROUP_NAMES_JSON)

        # Get missing IDs
        missing_ids = self.get_missing_ids(all_ids)

        if not missing_ids:
            logger.info("All group names already captured!")
            self.print_progress_summary(all_ids)
            return self.group_names

        logger.info(f"Found {len(missing_ids)} groups still needing names")
        logger.info(f"Starting automated Playwright navigation...")

        # Navigate all groups
        try:
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False)
                page = browser.new_page()

                for i, group_id in enumerate(missing_ids, 1):
                    logger.info(f"[{i}/{len(missing_ids)}] Processing {group_id}...")
                    self.navigate_and_capture(group_id, page)

                    # Save progress every SAVE_INTERVAL groups
                    if i % SAVE_INTERVAL == 0:
                        logger.info(f"Saving progress ({i}/{len(missing_ids)})...")
                        self.save_group_names(GROUP_NAMES_JSON)

                browser.close()

        except Exception as e:
            logger.error(f"Navigation failed: {e}", exc_info=True)
            return None

        # Save final results
        self.save_group_names(GROUP_NAMES_JSON)

        # Print progress
        self.print_progress_summary(all_ids)

        logger.info("\nPhase 5 complete!")
        return self.group_names


def main():
    """Execute Phase 5"""
    import argparse

    parser = argparse.ArgumentParser(description='Phase 5: Navigate and capture Facebook group names')
    parser.add_argument('--input', type=str, default=str(DATA_DIR / "unique_group_ids.json"),
                        help='Path to unique group IDs from phase 4')
    parser.add_argument('--resume', action='store_true', help='Resume from existing group_names.json')

    args = parser.parse_args()

    navigator = GroupNameNavigator()
    navigator.run(args.input, resume=args.resume)

    logger.info(f"\nWhen navigation is complete, run Phase 6 to generate the Excel file.")


if __name__ == '__main__':
    main()

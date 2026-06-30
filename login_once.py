"""
One-time Facebook login script.
Run this once to log in to Facebook, then your session is saved in config.py
All future runs will use the saved cookies - no login needed!
"""

import json
import logging
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_cookies_from_browser():
    """Launch browser, let user log in, capture cookies"""
    logger.info("=" * 70)
    logger.info("FACEBOOK LOGIN - One-Time Setup")
    logger.info("=" * 70)
    logger.info("")
    logger.info("Starting browser...")
    logger.info("A browser window will open - please log in to Facebook")
    logger.info("")

    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()

    # Navigate to Facebook
    logger.info("Loading Facebook...")
    page.goto("https://www.facebook.com", wait_until="domcontentloaded")

    # Wait for user to log in
    logger.info("")
    logger.info("Waiting for you to log in...")
    logger.info("(Browser will show Facebook login page)")
    logger.info("")
    logger.info("Press Enter in this terminal once you've logged in...")
    input()

    # Wait a moment for the page to fully load after login
    time.sleep(3)

    # Get cookies
    cookies = page.context.cookies()
    logger.info(f"Captured {len(cookies)} cookies")

    # Close browser
    browser.close()
    playwright.stop()

    return cookies

def format_cookies_for_config(cookies):
    """Format cookies as Python list for config.py"""
    # Convert cookies to a clean format
    formatted = []
    for cookie in cookies:
        formatted.append({
            'name': cookie.get('name'),
            'value': cookie.get('value'),
            'domain': cookie.get('domain'),
            'path': cookie.get('path', '/'),
            'secure': cookie.get('secure', True),
            'httpOnly': cookie.get('httpOnly', True),
        })
    return formatted

def inject_cookies_into_config(cookies):
    """Update config.py with the captured cookies"""
    config_path = Path(__file__).parent / "config.py"

    logger.info("")
    logger.info("Reading config.py...")
    with open(config_path, 'r', encoding='utf-8') as f:
        config_content = f.read()

    # Format the cookies as a Python literal
    cookies_json = json.dumps(cookies, indent=4)

    # Replace the FACEBOOK_COOKIES line
    pattern = r'FACEBOOK_COOKIES = \[\]  # Auto-populated by login script'
    replacement = f'FACEBOOK_COOKIES = {cookies_json}  # Auto-populated by login_once.py'

    new_config = re.sub(pattern, replacement, config_content)

    if new_config == config_content:
        logger.error("Could not find FACEBOOK_COOKIES in config.py")
        logger.error("Make sure config.py has: FACEBOOK_COOKIES = []")
        return False

    # Write back to config.py
    logger.info("Updating config.py with your session cookies...")
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(new_config)

    logger.info("Done!")
    return True

def main():
    logger.info("")
    logger.info("This script will:")
    logger.info("  1. Open Facebook in a browser")
    logger.info("  2. Let you log in manually")
    logger.info("  3. Save your session cookies to config.py")
    logger.info("  4. Future runs will auto-login (no browser needed!)")
    logger.info("")

    try:
        # Get cookies from user login
        cookies = get_cookies_from_browser()

        if not cookies:
            logger.error("No cookies captured - login may have failed")
            return False

        # Format and inject into config.py
        formatted_cookies = format_cookies_for_config(cookies)
        success = inject_cookies_into_config(formatted_cookies)

        if success:
            logger.info("")
            logger.info("=" * 70)
            logger.info("SUCCESS! Your session is now saved.")
            logger.info("=" * 70)
            logger.info("")
            logger.info("You can now run: python Grupo/main.py")
            logger.info("It will automatically use your saved Facebook login.")
            logger.info("")
            logger.info("(No browser login will be needed in future runs)")
            logger.info("")
            return True
        else:
            logger.error("Failed to update config.py")
            return False

    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    input("Press Enter to exit...")
    exit(0 if success else 1)

"""
Bootstrap script to auto-install Playwright browsers before main pipeline runs.
Also handles one-time Facebook login setup.
This ensures the .exe works completely standalone without user intervention.
"""

import sys
import os

# CRITICAL: Set Playwright environment BEFORE any imports
# Force Playwright to look outside the temporary EXE folder
if getattr(sys, 'frozen', False):
    # Running as PyInstaller .exe - use actual ms-playwright folder
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.expanduser(r"~\AppData\Local\ms-playwright")
else:
    # Running normally in venv - use default system pathing
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "0"

import subprocess
import logging
import json
import re
import time
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Catch any import errors
try:
    from playwright.sync_api import sync_playwright
    logger.info("Playwright imported successfully")
except Exception as e:
    logger.error(f"Failed to import Playwright: {e}")
    import traceback
    traceback.print_exc()
    input("Press Enter to exit...")
    sys.exit(1)

def ensure_playwright_installed():
    """Ensure Playwright browsers are installed"""
    logger.info("Checking Playwright browsers...")

    try:
        import playwright
        logger.info("Playwright is available!")
        return True
    except ImportError:
        logger.error("Playwright not found")
        return False

def check_facebook_cookies():
    """Check if Facebook cookies exist (for auto-login)"""
    try:
        # Try to import config - handle both .exe and direct python execution
        try:
            from config import FACEBOOK_COOKIES
        except ImportError:
            from Grupo.config import FACEBOOK_COOKIES
    except ImportError:
        logger.warning("Could not import config, assuming no cookies")
        return False

    # Look for cookies file next to the .exe
    if getattr(sys, 'frozen', False):
        cookies_file = Path(sys.executable).parent / "facebook_cookies.json"
    else:
        cookies_file = Path(__file__).parent / "facebook_cookies.json"

    if FACEBOOK_COOKIES:
        logger.info("Found Facebook session in config.py - will use saved login")
        return True
    elif cookies_file.exists():
        logger.info("Found Facebook session cookies - will use saved login")
        return True
    else:
        return False

def capture_facebook_login():
    """Launch browser for one-time Facebook login, save cookies to config.py"""
    logger.info("")
    logger.info("=" * 70)
    logger.info("FACEBOOK LOGIN SETUP (One-Time Only)")
    logger.info("=" * 70)
    logger.info("")
    logger.info("Opening browser for Facebook login...")
    logger.info("")

    try:
        from playwright.sync_api import sync_playwright

        # Start browser with timeout
        try:
            playwright = sync_playwright().start()
            browser = playwright.chromium.launch(headless=False, timeout=30000)
            page = browser.new_page()
        except Exception as e:
            logger.error(f"Could not open browser: {e}")
            logger.error("This usually means Playwright browsers aren't properly installed")
            return False

        # Navigate to Facebook
        logger.info("Opening Facebook...")
        page.goto("https://www.facebook.com", wait_until="domcontentloaded")

        # Wait for login
        logger.info("")
        logger.info("Please log in to Facebook in the browser window")
        logger.info("(After login, you can close this message or wait)")
        logger.info("")
        logger.info("Press Enter here when you've logged in...")
        input()

        # Wait for page to settle
        time.sleep(3)

        # Get cookies
        cookies = page.context.cookies()
        logger.info(f"Captured {len(cookies)} session cookies")

        # Close browser
        browser.close()
        playwright.stop()

        # Format cookies for config
        formatted_cookies = []
        for cookie in cookies:
            formatted_cookies.append({
                'name': cookie.get('name'),
                'value': cookie.get('value'),
                'domain': cookie.get('domain'),
                'path': cookie.get('path', '/'),
                'secure': cookie.get('secure', True),
                'httpOnly': cookie.get('httpOnly', True),
            })

        # Save cookies to a JSON file next to the .exe
        if getattr(sys, 'frozen', False):
            cookies_save_path = Path(sys.executable).parent / "facebook_cookies.json"
        else:
            cookies_save_path = Path(__file__).parent / "facebook_cookies.json"

        logger.info(f"Saving cookies to {cookies_save_path}...")
        with open(cookies_save_path, 'w', encoding='utf-8') as f:
            json.dump(formatted_cookies, f, indent=4)

        logger.info("")
        logger.info("=" * 70)
        logger.info("SUCCESS! Your Facebook session is now saved.")
        logger.info("=" * 70)
        logger.info("")
        logger.info("You won't need to log in again.")
        logger.info("")
        return True

    except Exception as e:
        logger.error(f"Login failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main entry point - bootstrap then run pipeline"""

    try:
        logger.info("=" * 70)
        logger.info("LEILOARIA SMART - INITIALIZATION")
        logger.info("=" * 70)
        logger.info("")

        # Ensure Playwright is installed
        if not ensure_playwright_installed():
            logger.error("Cannot continue without Playwright browsers")
            input("Press Enter to exit...")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Startup error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
        sys.exit(1)

    logger.info("")

    # Check for Facebook cookies
    has_cookies = check_facebook_cookies()

    if not has_cookies:
        logger.info("No Facebook session found")
        logger.info("")
        logger.info("You need to log in to Facebook once.")
        logger.info("Running login setup...")
        logger.info("")

        try:
            if not capture_facebook_login():
                logger.error("Facebook login setup failed")
                logger.error("This may happen if:")
                logger.error("  - Browser won't open")
                logger.error("  - Network connection issue")
                logger.error("Please try again or contact support")
                input("Press Enter to exit...")
                sys.exit(1)
        except KeyboardInterrupt:
            logger.info("Login cancelled by user")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Login error: {e}")
            input("Press Enter to exit...")
            sys.exit(1)

    logger.info("")
    logger.info("Starting pipeline...")
    logger.info("")

    # Now run the actual pipeline
    try:
        # Try both import paths for bundled vs direct execution
        try:
            from main import main as run_pipeline
        except ImportError:
            from Grupo.main import main as run_pipeline

        run_pipeline()
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == '__main__':
    try:
        main()
        # If we get here, pipeline succeeded
        logger.info("")
        logger.info("=" * 70)
        logger.info("PIPELINE COMPLETE!")
        logger.info("=" * 70)
        logger.info("")
        logger.info("Press Enter to exit...")
        input()
    except Exception as e:
        logger.error("")
        logger.error("=" * 70)
        logger.error("FATAL ERROR - Application crashed")
        logger.error("=" * 70)
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        logger.error("")
        logger.error("Press Enter to exit and copy the error above...")
        input()
        sys.exit(1)

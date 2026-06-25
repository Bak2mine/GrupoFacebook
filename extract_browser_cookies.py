"""
Extract Facebook cookies from your browser
This allows using your existing authenticated session
"""

import json
import sqlite3
import os
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_cookies_from_firefox():
    """Extract cookies from Firefox"""
    logger.info("Trying to extract cookies from Firefox...")

    firefox_profile = os.path.expanduser("~/.mozilla/firefox")

    if not os.path.exists(firefox_profile):
        logger.warning("Firefox profile not found")
        return None

    try:
        # Find the default profile
        for profile_dir in os.listdir(firefox_profile):
            cookies_db = os.path.join(firefox_profile, profile_dir, "cookies.sqlite")

            if os.path.exists(cookies_db):
                logger.info(f"Found Firefox cookies at: {cookies_db}")

                # Copy database (it might be locked)
                import shutil
                temp_db = "cookies_temp.sqlite"
                shutil.copy(cookies_db, temp_db)

                # Read cookies
                conn = sqlite3.connect(temp_db)
                cursor = conn.cursor()

                cursor.execute("SELECT name, value, domain, path FROM moz_cookies WHERE host LIKE '%facebook%'")
                rows = cursor.fetchall()

                conn.close()
                os.remove(temp_db)

                if rows:
                    cookies = []
                    for name, value, domain, path in rows:
                        cookies.append({
                            "name": name,
                            "value": value,
                            "domain": domain,
                            "path": path,
                        })
                    logger.info(f"Extracted {len(cookies)} Facebook cookies from Firefox")
                    return cookies

    except Exception as e:
        logger.error(f"Error extracting Firefox cookies: {e}")

    return None


def extract_cookies_from_chrome():
    """Extract cookies from Chrome/Chromium"""
    logger.info("Trying to extract cookies from Chrome...")

    # Chrome stores cookies in AppData\Local\Google\Chrome\User Data\Default
    chrome_path = os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Cookies")

    if not os.path.exists(chrome_path):
        logger.warning("Chrome cookies database not found")
        return None

    try:
        logger.info(f"Found Chrome cookies at: {chrome_path}")

        # Copy database (it's locked while Chrome is running)
        import shutil
        temp_db = "chrome_cookies_temp.sqlite"
        shutil.copy(chrome_path, temp_db)

        # Read cookies
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name, encrypted_value, host_key, path
            FROM cookies
            WHERE host_key LIKE '%facebook%'
        """)
        rows = cursor.fetchall()

        conn.close()
        os.remove(temp_db)

        if rows:
            logger.warning("Note: Chrome cookies are encrypted and need decryption key")
            logger.info(f"Found {len(rows)} Facebook cookies in Chrome (encrypted)")
            return None  # Encrypted cookies need special handling

    except Exception as e:
        logger.error(f"Error extracting Chrome cookies: {e}")

    return None


def extract_cookies_from_edge():
    """Extract cookies from Microsoft Edge"""
    logger.info("Trying to extract cookies from Edge...")

    edge_path = os.path.expanduser("~\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\Cookies")

    if not os.path.exists(edge_path):
        logger.warning("Edge cookies database not found")
        return None

    try:
        logger.info(f"Found Edge cookies at: {edge_path}")
        logger.warning("Note: Edge cookies are encrypted and need decryption key")
        return None

    except Exception as e:
        logger.error(f"Error extracting Edge cookies: {e}")

    return None


def extract_cookies_from_opera_gx():
    """Extract cookies from Opera GX"""
    logger.info("Trying to extract cookies from Opera GX...")

    # Opera GX stores cookies in AppData\Local\Opera Software\Opera GX Stable
    opera_path = os.path.expanduser("~\\AppData\\Local\\Opera Software\\Opera GX Stable\\Cookies")

    if not os.path.exists(opera_path):
        logger.warning("Opera GX cookies database not found, trying alternative path...")
        opera_path = os.path.expanduser("~\\AppData\\Roaming\\Opera Software\\Opera GX Stable\\Cookies")

        if not os.path.exists(opera_path):
            logger.warning("Opera GX profile not found in standard locations")
            return None

    try:
        logger.info(f"Found Opera GX cookies at: {opera_path}")

        # Copy database (it might be locked)
        import shutil
        temp_db = "opera_cookies_temp.sqlite"
        try:
            shutil.copy(opera_path, temp_db)
        except PermissionError:
            logger.warning("Opera GX is running - close it first for cookie extraction")
            logger.info("Cookies are encrypted anyway, trying alternative method...")
            return None

        # Read cookies
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name, encrypted_value, host_key, path
            FROM cookies
            WHERE host_key LIKE '%facebook%'
        """)
        rows = cursor.fetchall()

        conn.close()
        os.remove(temp_db)

        if rows:
            logger.warning("Note: Opera GX cookies are encrypted")
            logger.info(f"Found {len(rows)} Facebook cookies in Opera GX (encrypted)")
            return None  # Encrypted - needs special handling

    except Exception as e:
        logger.error(f"Error extracting Opera GX cookies: {e}")

    return None


def main():
    """Try to extract Facebook cookies from browser"""
    print("\n" + "="*70)
    print("  FACEBOOK COOKIE EXTRACTOR")
    print("="*70 + "\n")

    print("This will extract your Facebook session cookies from your browser.")
    print("This only works if you're logged in to Facebook in your browser.\n")

    cookies = None

    # Try Opera GX first (you're using this!)
    cookies = extract_cookies_from_opera_gx()

    # Try Firefox if Opera didn't work
    if not cookies:
        cookies = extract_cookies_from_firefox()

    # Try Chrome if Firefox didn't work
    if not cookies:
        cookies = extract_cookies_from_chrome()

    # Try Edge if Chrome didn't work
    if not cookies:
        cookies = extract_cookies_from_edge()

    if cookies:
        # Save to file
        output_file = "facebook_cookies.json"
        with open(output_file, 'w') as f:
            json.dump(cookies, f, indent=2)

        logger.info(f"✓ Cookies saved to {output_file}")
        print(f"\n✓ SUCCESS! Cookies saved to {output_file}")
        print(f"  You can now run: python phase3_with_cookies.py\n")

        return True

    else:
        logger.error("Could not extract cookies from any browser")
        print("\n✗ FAILED: Could not extract cookies")
        print("\nOptions:")
        print("  1. Make sure you're logged in to Facebook in Firefox")
        print("  2. Or manually log in using: python phase3_with_cookies.py --show-browser")
        print("  3. Or use the working sample data (safe option)\n")

        return False


if __name__ == '__main__':
    main()

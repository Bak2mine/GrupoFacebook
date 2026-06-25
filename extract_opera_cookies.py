"""
Extract cookies from running Opera GX process
Uses Windows DPAPI to decrypt them
"""

import sqlite3
import json
import os
import shutil
import logging
from pathlib import Path
from win32crypt import CryptUnprotectData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def decrypt_opera_cookie(encrypted_value):
    """Decrypt Opera GX cookie using Windows DPAPI"""
    try:
        # Opera uses Windows DPAPI encryption
        decrypted = CryptUnprotectData(encrypted_value, None, None, None, 0)
        return decrypted[1].decode('utf-8', errors='ignore')
    except Exception as e:
        logger.debug(f"Could not decrypt cookie: {e}")
        return None


def extract_opera_cookies():
    """Extract Facebook cookies from Opera GX"""
    logger.info("Extracting cookies from Opera GX...\n")

    # Opera GX cookie locations
    paths_to_try = [
        Path(os.path.expanduser("~\\AppData\\Roaming\\Opera Software\\Opera GX Stable\\Default\\Network\\Cookies")),
        Path(os.path.expanduser("~\\AppData\\Local\\Opera Software\\Opera GX Stable\\Default\\Cookies")),
        Path(os.path.expanduser("~\\AppData\\Roaming\\Opera Software\\Opera GX Stable\\Default\\Cookies")),
    ]

    cookies_found = False

    for cookies_path in paths_to_try:
        if not cookies_path.exists():
            logger.debug(f"Not found: {cookies_path}")
            continue

        logger.info(f"Found: {cookies_path}\n")

        try:
            # Copy to temp location (database might be locked)
            temp_db = "opera_cookies_temp.sqlite"
            shutil.copy(cookies_path, temp_db)
            logger.info("Copied to temp database\n")

            # Connect to database
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()

            # Query Facebook cookies
            cursor.execute("""
                SELECT name, encrypted_value, host_key, path, expires_utc
                FROM cookies
                WHERE host_key LIKE '%facebook%'
                ORDER BY host_key
            """)
            rows = cursor.fetchall()

            conn.close()
            os.remove(temp_db)

            if not rows:
                logger.warning("No Facebook cookies found in this location")
                continue

            logger.info(f"Found {len(rows)} encrypted Facebook cookies\n")
            logger.info("Decrypting...\n")

            # Try to decrypt cookies
            decrypted_cookies = []
            failed_decrypt = 0

            for name, encrypted_value, host_key, path, expires in rows:
                try:
                    # encrypted_value is bytes
                    if isinstance(encrypted_value, str):
                        encrypted_value = encrypted_value.encode()

                    decrypted_value = decrypt_opera_cookie(encrypted_value)

                    if decrypted_value:
                        cookie = {
                            "name": name,
                            "value": decrypted_value,
                            "domain": host_key,
                            "path": path,
                        }
                        decrypted_cookies.append(cookie)
                        logger.info(f"✓ {name}: {decrypted_value[:30]}...")
                    else:
                        failed_decrypt += 1

                except Exception as e:
                    logger.debug(f"Error decrypting {name}: {e}")
                    failed_decrypt += 1

            if failed_decrypt > 0:
                logger.warning(f"\n⚠ Failed to decrypt {failed_decrypt} cookies")

            if decrypted_cookies:
                logger.info(f"\n✓ Successfully decrypted {len(decrypted_cookies)} cookies\n")

                # Save to file
                output_file = "facebook_cookies.json"
                with open(output_file, 'w') as f:
                    json.dump(decrypted_cookies, f, indent=2)

                logger.info(f"✓ Saved to {output_file}")
                logger.info(f"✓ You can now run: python phase3_simple_login.py\n")

                return True

        except PermissionError:
            logger.error("Permission denied - Opera GX might be running")
            logger.info("Try closing Opera GX and running this again\n")
        except Exception as e:
            logger.error(f"Error: {e}\n")

    logger.error("\nCould not extract cookies from Opera GX")
    return False


if __name__ == '__main__':
    try:
        import win32crypt
        logger.info("Windows crypto module found\n")
    except ImportError:
        logger.error("ERROR: Need 'pywin32' for cookie decryption")
        logger.error("Install with: pip install pywin32\n")
        exit(1)

    success = extract_opera_cookies()
    exit(0 if success else 1)

"""
Test utilities for the Leiloaria Facebook Groups pipeline
Quick tests to verify each phase works correctly
"""

import json
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

from config import DATA_DIR, UNIQUE_IDS_JSON, GROUP_NAMES_JSON


class PipelineTester:
    """Test pipeline components"""

    @staticmethod
    def test_phase1():
        """Test Phase 1: Property scraping"""
        logger.info("Testing Phase 1: Property Scraping...")

        from phase1_extract_data import DataExtractor

        try:
            extractor = DataExtractor()
            # Quick test with just 5 properties
            properties, classification = extractor.run(limit=5, skip_scrape=True)

            if properties:
                logger.info(f"  ✓ Scraped {len(properties)} properties")
                logger.info(f"  ✓ Found {len(classification['large_cities'])} large cities")
                logger.info(f"  ✓ Found {len(classification['small_cities'])} small cities")
                return True
            else:
                logger.error("  ✗ No properties scraped")
                return False

        except Exception as e:
            logger.error(f"  ✗ Phase 1 failed: {e}")
            return False

    @staticmethod
    def test_phase2():
        """Test Phase 2: Build searches"""
        logger.info("Testing Phase 2: Build Searches...")

        classification_file = DATA_DIR / "city_classification.json"

        if not classification_file.exists():
            logger.warning(f"  ⚠ Classification file not found: {classification_file}")
            logger.info("  Run Phase 1 first to generate classification")
            return False

        try:
            from phase2_build_searches import SearchBuilder

            builder = SearchBuilder()
            searches = builder.run(str(classification_file))

            if searches:
                logger.info(f"  ✓ Built {len(searches)} searches")
                return True
            else:
                logger.error("  ✗ No searches built")
                return False

        except Exception as e:
            logger.error(f"  ✗ Phase 2 failed: {e}")
            return False

    @staticmethod
    def test_phase3():
        """Test Phase 3: Google search"""
        logger.info("Testing Phase 3: Google Search...")

        searches_file = DATA_DIR / "search_configuration.json"

        if not searches_file.exists():
            logger.warning(f"  ⚠ Searches file not found: {searches_file}")
            logger.info("  Run Phase 2 first to generate searches")
            return False

        try:
            # Load searches to count
            with open(searches_file, 'r', encoding='utf-8') as f:
                searches = json.load(f)

            logger.info(f"  ✓ Loaded {len(searches)} searches")

            # Note: Actual Google search may be slow/blocked, so we just check structure
            if searches and all('search_term' in s for s in searches):
                logger.info(f"  ✓ Searches have correct structure")
                logger.info("  ℹ Actual Google search can be tested manually:")
                logger.info("    python phase3_google_search.py")
                return True
            else:
                logger.error("  ✗ Searches have invalid structure")
                return False

        except Exception as e:
            logger.error(f"  ✗ Phase 3 failed: {e}")
            return False

    @staticmethod
    def test_phase4():
        """Test Phase 4: Deduplicate IDs"""
        logger.info("Testing Phase 4: Deduplicate IDs...")

        searches_file = DATA_DIR / "searches_with_group_ids.json"

        if not searches_file.exists():
            logger.warning(f"  ⚠ Searches with IDs not found: {searches_file}")
            logger.info("  Run Phase 3 first to get group IDs")
            return False

        try:
            from phase4_deduplicate import GroupIDDeduplicator

            dedup = GroupIDDeduplicator()
            unique_ids = dedup.run(str(searches_file))

            if unique_ids:
                logger.info(f"  ✓ Generated {len(unique_ids)} unique IDs")
                logger.info(f"  ✓ Saved to {UNIQUE_IDS_JSON}")
                return True
            else:
                logger.error("  ✗ No unique IDs generated")
                return False

        except Exception as e:
            logger.error(f"  ✗ Phase 4 failed: {e}")
            return False

    @staticmethod
    def test_phase5():
        """Test Phase 5: Check navigation setup"""
        logger.info("Testing Phase 5: Navigation Setup...")

        if not UNIQUE_IDS_JSON.exists():
            logger.warning(f"  ⚠ Unique IDs file not found: {UNIQUE_IDS_JSON}")
            logger.info("  Run Phase 4 first to generate unique IDs")
            return False

        try:
            with open(UNIQUE_IDS_JSON, 'r', encoding='utf-8') as f:
                unique_ids = json.load(f)

            logger.info(f"  ✓ Loaded {len(unique_ids)} unique group IDs")

            if GROUP_NAMES_JSON.exists():
                with open(GROUP_NAMES_JSON, 'r', encoding='utf-8') as f:
                    names = json.load(f)
                logger.info(f"  ✓ Already captured {len(names)} group names")
            else:
                logger.info(f"  ℹ No group names captured yet")

            logger.info("  ℹ Phase 5 requires manual Claude Cowork navigation")
            logger.info("    python main.py --skip-to-phase 5")
            return True

        except Exception as e:
            logger.error(f"  ✗ Phase 5 setup failed: {e}")
            return False

    @staticmethod
    def test_phase6():
        """Test Phase 6: Excel generation"""
        logger.info("Testing Phase 6: Excel Generation...")

        searches_file = DATA_DIR / "searches_with_group_ids.json"

        if not searches_file.exists():
            logger.warning(f"  ⚠ Searches file not found: {searches_file}")
            logger.info("  Run Phase 3 first")
            return False

        try:
            from phase6_build_excel import ExcelReportBuilder

            # Check if openpyxl is available
            try:
                import openpyxl
            except ImportError:
                logger.warning("  ⚠ openpyxl not available")
                logger.info("    Install with: pip install openpyxl")
                return False

            builder = ExcelReportBuilder()
            excel_file = builder.run()

            if excel_file and Path(excel_file).exists():
                logger.info(f"  ✓ Generated Excel file: {excel_file}")
                logger.info(f"  ✓ File size: {Path(excel_file).stat().st_size / 1024:.1f} KB")
                return True
            else:
                logger.error("  ✗ Excel file not generated")
                return False

        except Exception as e:
            logger.error(f"  ✗ Phase 6 failed: {e}")
            return False

    @staticmethod
    def test_dependencies():
        """Test required dependencies"""
        logger.info("Testing Dependencies...")

        dependencies = {
            'requests': 'pip install requests',
            'bs4': 'pip install beautifulsoup4',
            'openpyxl': 'pip install openpyxl',
        }

        missing = []

        for pkg, install_cmd in dependencies.items():
            try:
                __import__(pkg)
                logger.info(f"  ✓ {pkg}")
            except ImportError:
                logger.warning(f"  ✗ {pkg} (missing: {install_cmd})")
                missing.append(install_cmd)

        if missing:
            logger.warning("\nInstall missing packages:")
            for cmd in missing:
                logger.warning(f"  {cmd}")
            return False

        return True

    @staticmethod
    def run_all_tests():
        """Run all tests"""
        logger.info("="*70)
        logger.info("LEILOARIA FACEBOOK GROUPS - PIPELINE TEST SUITE")
        logger.info("="*70 + "\n")

        tests = [
            ("Dependencies", PipelineTester.test_dependencies),
            ("Phase 1: Extract Data", PipelineTester.test_phase1),
            ("Phase 2: Build Searches", PipelineTester.test_phase2),
            ("Phase 3: Google Search", PipelineTester.test_phase3),
            ("Phase 4: Deduplicate", PipelineTester.test_phase4),
            ("Phase 5: Navigation Setup", PipelineTester.test_phase5),
            ("Phase 6: Excel Generation", PipelineTester.test_phase6),
        ]

        results = []

        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
                logger.info()
            except Exception as e:
                logger.error(f"Test crashed: {e}")
                results.append((test_name, False))
                logger.info()

        # Summary
        logger.info("="*70)
        logger.info("TEST SUMMARY")
        logger.info("="*70)

        passed = sum(1 for _, r in results if r)
        total = len(results)

        for test_name, result in results:
            status = "✓ PASS" if result else "✗ FAIL"
            logger.info(f"  {status}: {test_name}")

        logger.info(f"\nResults: {passed}/{total} passed")

        return all(r for _, r in results)


def main():
    """Run test suite"""
    import argparse

    parser = argparse.ArgumentParser(description='Test pipeline components')
    parser.add_argument('--phase', type=int, choices=range(1, 7),
                       help='Test specific phase (default: all)')
    parser.add_argument('--deps-only', action='store_true',
                       help='Only test dependencies')

    args = parser.parse_args()

    tester = PipelineTester()

    if args.deps_only:
        success = tester.test_dependencies()
    elif args.phase:
        test_map = {
            1: tester.test_phase1,
            2: tester.test_phase2,
            3: tester.test_phase3,
            4: tester.test_phase4,
            5: tester.test_phase5,
            6: tester.test_phase6,
        }
        success = test_map[args.phase]()
    else:
        success = tester.run_all_tests()

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

"""
Leiloaria Smart - Facebook Groups Automation
Main orchestration script that runs all phases sequentially
"""

import sys
import logging
import argparse
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('leiloaria_grupos.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import all phases
from phase1_extract_data import DataExtractor
from phase2_build_searches import SearchBuilder
from phase3_google_search import GoogleGroupSearcher
from phase4_deduplicate import GroupIDDeduplicator
from phase5_navigate_groups import GroupNameNavigator
from phase6_build_excel import ExcelReportBuilder

from config import DATA_DIR, OUTPUT_DIR, UNIQUE_IDS_JSON


class LeiloariaGruposAutomation:
    """Orchestrates the complete Facebook groups extraction pipeline"""

    def __init__(self):
        self.phases_completed = []

    def run_phase(self, phase_num: int, phase_name: str, phase_func, *args, **kwargs):
        """Execute a single phase

        Args:
            phase_num: Phase number
            phase_name: Name of phase
            phase_func: Function to execute
            *args: Args for phase function
            **kwargs: Kwargs for phase function

        Returns:
            Result from phase function
        """
        logger.info("\n" + "="*70)
        logger.info(f"PHASE {phase_num}: {phase_name}")
        logger.info("="*70)

        try:
            result = phase_func(*args, **kwargs)
            self.phases_completed.append((phase_num, phase_name))
            logger.info(f"[OK] Phase {phase_num} completed successfully")
            return result
        except Exception as e:
            logger.error(f"[ERROR] Phase {phase_num} failed: {e}", exc_info=True)
            raise

    def run_all_phases(self, scrape_properties=True, skip_to_phase=1, property_limit=None):
        """Run complete pipeline

        Args:
            scrape_properties: Whether to scrape properties from website
            skip_to_phase: Start from this phase (1-6)
            property_limit: Limit properties to scrape (None = all)
        """
        logger.info("Starting Leiloaria Smart Facebook Groups Automation")
        logger.info(f"Output directory: {OUTPUT_DIR}")

        try:
            # Phase 1: Extract property data
            if skip_to_phase <= 1:
                extractor = DataExtractor()
                properties, classification = self.run_phase(
                    1, "Extract Property Data",
                    extractor.run,
                    skip_scrape=not scrape_properties,
                    limit=property_limit
                )
            else:
                logger.info("Skipping Phase 1 (as requested)")

            # Phase 2: Build search configuration
            if skip_to_phase <= 2:
                builder = SearchBuilder()
                searches = self.run_phase(
                    2, "Build Search Configuration",
                    builder.run,
                    DATA_DIR / "city_classification.json"
                )
            else:
                logger.info("Skipping Phase 2 (as requested)")

            # Phase 3: Google search for Facebook groups
            if skip_to_phase <= 3:
                searcher = GoogleGroupSearcher()
                searches = self.run_phase(
                    3, "Search Google for Facebook Groups",
                    searcher.run,
                    DATA_DIR / "search_configuration.json"
                )
            else:
                logger.info("Skipping Phase 3 (as requested)")

            # Phase 4: Deduplicate group IDs
            if skip_to_phase <= 4:
                deduplicator = GroupIDDeduplicator()
                unique_ids = self.run_phase(
                    4, "Deduplicate Group IDs",
                    deduplicator.run,
                    DATA_DIR / "searches_with_group_ids.json"
                )
            else:
                logger.info("Skipping Phase 4 (as requested)")

            # Phase 5: Navigate and capture group names (fully automated with Playwright)
            if skip_to_phase <= 5:
                navigator = GroupNameNavigator()
                group_names = self.run_phase(
                    5, "Navigate Facebook Groups (Automated)",
                    navigator.run,
                    UNIQUE_IDS_JSON,
                    resume=False
                )
                if group_names is None:
                    logger.error("Phase 5 failed. Ensure Playwright is installed:")
                    logger.error("  pip install playwright")
                    logger.error("  playwright install chromium")
                    return False
            else:
                logger.info("Skipping Phase 5 (as requested)")

            # Phase 6: Generate Excel report
            if skip_to_phase <= 6:
                excel_builder = ExcelReportBuilder()
                excel_file = self.run_phase(
                    6, "Generate Excel Report",
                    excel_builder.run
                )
                logger.info(f"\n✓ Final report generated: {excel_file}")
            else:
                logger.info("Skipping Phase 6 (as requested)")

        except Exception as e:
            logger.error(f"\nPipeline failed at phase {self.phases_completed[-1][0] if self.phases_completed else 0}")
            logger.error(f"Error: {e}")
            return False

        # Print completion summary
        self.print_summary()
        return True

    def print_summary(self):
        """Print summary of completed phases"""
        logger.info("\n" + "="*70)
        logger.info("PIPELINE SUMMARY")
        logger.info("="*70)

        if self.phases_completed:
            logger.info("Completed phases:")
            for phase_num, phase_name in self.phases_completed:
                logger.info(f"  [OK] Phase {phase_num}: {phase_name}")
        else:
            logger.info("No phases completed")

        logger.info("\nGenerated files:")
        logger.info(f"  - {DATA_DIR / 'scraped_properties.json'}")
        logger.info(f"  - {DATA_DIR / 'city_classification.json'}")
        logger.info(f"  - {DATA_DIR / 'search_configuration.json'}")
        logger.info(f"  - {DATA_DIR / 'searches_with_group_ids.json'}")
        logger.info(f"  - {UNIQUE_IDS_JSON}")
        logger.info(f"  - {DATA_DIR / 'group_names.json'}")
        logger.info(f"  - {OUTPUT_DIR / 'Leiloaria_Smart_Grupos_Facebook_COMPLETO.xlsx'}")

        logger.info("\nFor detailed logs, see: leiloaria_grupos.log")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Leiloaria Smart - Automated Facebook Groups Extraction',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run complete pipeline from scratch
  python main.py

  # Skip property scraping (use existing data)
  python main.py --no-scrape

  # Start from phase 3 (assumes phases 1-2 already done)
  python main.py --skip-to-phase 3

  # Limit properties to 50 for testing
  python main.py --limit 50

  # Resume from phase 5 (after Claude Cowork navigation)
  python main.py --skip-to-phase 5
        """
    )

    parser.add_argument('--no-scrape', action='store_true',
                       help='Skip property scraping (use existing data)')
    parser.add_argument('--skip-to-phase', type=int, default=1,
                       choices=range(1, 7),
                       help='Start from this phase (default: 1)')
    parser.add_argument('--limit', type=int, default=None,
                       help='Limit properties to scrape (default: all)')

    args = parser.parse_args()

    automation = LeiloariaGruposAutomation()
    success = automation.run_all_phases(
        scrape_properties=not args.no_scrape,
        skip_to_phase=args.skip_to_phase,
        property_limit=args.limit
    )

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

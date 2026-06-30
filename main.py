"""
Leiloaria Smart - Facebook Groups Automation Pipeline
Fully automated discovery and collection of real estate groups

Complete pipeline: extract bairros → scrape Facebook groups → generate Excel report
"""

import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('leiloaria_grupos.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def run_phase(phase_name: str, phase_func, *args, **kwargs):
    """Run a phase and handle errors"""
    try:
        logger.info("")
        logger.info("="*70)
        logger.info(f"PHASE: {phase_name}")
        logger.info("="*70)
        logger.info("")

        result = phase_func(*args, **kwargs)

        logger.info(f"[OK] {phase_name} completed successfully")
        return True

    except Exception as e:
        logger.error(f"[ERROR] {phase_name} failed: {e}")
        logger.error("")
        return False


def main():
    """Main pipeline orchestrator"""
    logger.info("")
    logger.info("="*70)
    logger.info("STARTING FACEBOOK GROUPS AUTOMATION PIPELINE")
    logger.info("="*70)
    logger.info("")

    completed_phases = []
    failed_phase = None

    # Phase 1: Extract bairros for large cities
    try:
        from extract_bairros import BairroExtractor
        extractor = BairroExtractor()

        if run_phase("1: Extract Bairros", extractor.run):
            completed_phases.append("Extract Bairros")
        else:
            failed_phase = "Extract Bairros"
            raise Exception("Bairro extraction failed")

    except Exception as e:
        logger.error(f"Phase 1 error: {e}")
        failed_phase = "Extract Bairros"

    if failed_phase:
        logger.error("")
        logger.error(f"Pipeline failed at {failed_phase}")
        return False

    # Phase 1B: DISABLED - name fixing was causing incorrect substitutions
    # The truncation issue is in Post/scraper.py property extraction, not search terms
    logger.info("")
    logger.info("="*70)
    logger.info("PHASE: 1B (SKIPPED - Name fixing disabled)")
    logger.info("="*70)
    logger.info("Reason: Truncation issue should be fixed in Post/scraper.py extraction")
    logger.info("")

    # Phase 2: Scrape Facebook groups with cookies
    try:
        from phase3_with_cookies import FacebookGroupScraper
        scraper = FacebookGroupScraper()

        # Use bairro config if available, otherwise fall back to regular config
        from config import DATA_DIR
        config_file = DATA_DIR / "search_configuration_bairro.json"
        if not config_file.exists():
            config_file = DATA_DIR / "search_configuration.json"

        if run_phase("2: Scrape Facebook Groups", scraper.run, config_file):
            completed_phases.append("Scrape Facebook Groups")
        else:
            failed_phase = "Scrape Facebook Groups"
            raise Exception("Facebook scraping failed")

    except Exception as e:
        logger.error(f"Phase 2 error: {e}")
        failed_phase = "Scrape Facebook Groups"

    if failed_phase:
        logger.error("")
        logger.error(f"Pipeline failed at {failed_phase}")
        return False

    # Phase 3: Generate Excel report
    try:
        from phase6_build_excel import ExcelReportBuilder
        builder = ExcelReportBuilder()

        if run_phase("3: Generate Excel Report", builder.run):
            completed_phases.append("Generate Excel Report")
        else:
            failed_phase = "Generate Excel Report"
            raise Exception("Excel generation failed")

    except Exception as e:
        logger.error(f"Phase 3 error: {e}")
        failed_phase = "Generate Excel Report"

    if failed_phase:
        logger.error("")
        logger.error(f"Pipeline failed at {failed_phase}")
        return False

    # Success!
    logger.info("")
    logger.info("="*70)
    logger.info("PIPELINE SUMMARY")
    logger.info("="*70)
    logger.info(f"Completed phases: {len(completed_phases)}")
    for phase in completed_phases:
        logger.info(f"  [OK] {phase}")
    logger.info("")
    logger.info("Pipeline completed successfully!")
    logger.info("="*70)
    logger.info("")

    return True


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.warning("\nPipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

"""
Phase 4: Extract and deduplicate unique Facebook group IDs
"""

import json
import logging
from pathlib import Path
from collections import OrderedDict
from config import DATA_DIR, UNIQUE_IDS_JSON, LOG_LEVEL, LOG_FORMAT

# Setup logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)
logger = logging.getLogger(__name__)


class GroupIDDeduplicator:
    """Extract unique group IDs and maintain mapping to searches"""

    def __init__(self):
        self.unique_ids = []
        self.id_to_searches = {}  # Map ID -> list of searches it appears in

    def extract_all_ids(self, searches):
        """Extract all group IDs from searches

        Args:
            searches: List of search configurations

        Returns:
            List of (group_id, search_info) tuples
        """
        logger.info("Extracting all group IDs from searches...")

        all_ids = []
        for search in searches:
            city = search.get('city')
            search_term = search.get('search_term')
            group_ids = search.get('group_ids', [])

            for group_id in group_ids:
                all_ids.append({
                    'id': str(group_id),
                    'city': city,
                    'search_term': search_term,
                    'type': search.get('type')
                })

        logger.info(f"Extracted {len(all_ids)} total IDs (including duplicates)")
        return all_ids

    def deduplicate(self, all_ids):
        """Remove duplicate IDs, keeping first occurrence

        Args:
            all_ids: List of ID records

        Returns:
            List of unique IDs, ordered by first appearance
        """
        logger.info("Deduplicating IDs...")

        seen_ids = set()
        unique_ids = []

        for id_record in all_ids:
            group_id = id_record['id']

            if group_id not in seen_ids:
                seen_ids.add(group_id)
                unique_ids.append(id_record)
                self.id_to_searches[group_id] = []

            # Track which searches each ID appears in
            self.id_to_searches[group_id].append({
                'city': id_record['city'],
                'search_term': id_record['search_term']
            })

        logger.info(f"After deduplication: {len(unique_ids)} unique IDs")
        if len(all_ids) > 0:
            reduction = len(all_ids) - len(unique_ids)
            logger.info(f"Removed {reduction} duplicate entries ({100*reduction/len(all_ids):.1f}%)")
        else:
            logger.warning("No group IDs found in searches")

        return unique_ids

    def save_unique_ids(self, unique_ids, output_file):
        """Save unique IDs to JSON file

        Args:
            unique_ids: List of unique ID records
            output_file: Path to save JSON
        """
        logger.info(f"Saving unique IDs to {output_file}...")

        # Save just the numeric IDs as a simple list for easy reference
        id_list = [record['id'] for record in unique_ids]

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(id_list, f, indent=2)

        logger.info(f"Saved {len(id_list)} unique IDs")

    def save_detailed_mapping(self, unique_ids):
        """Save detailed ID -> search mapping

        Args:
            unique_ids: List of unique ID records
        """
        output_file = DATA_DIR / "group_ids_detailed.json"
        logger.info(f"Saving detailed mapping to {output_file}...")

        detailed = {}
        for record in unique_ids:
            group_id = record['id']
            detailed[group_id] = {
                'first_search': record['search_term'],
                'first_city': record['city'],
                'appears_in': self.id_to_searches.get(group_id, [])
            }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(detailed, f, ensure_ascii=False, indent=2)

        logger.info("Detailed mapping saved")

    def calculate_navigation_batches(self, unique_ids, batch_size=4):
        """Calculate number of batches needed for navigation (phase 5)

        Args:
            unique_ids: List of unique IDs
            batch_size: Number of parallel tabs per batch

        Returns:
            Number of navigation rounds needed
        """
        total = len(unique_ids)
        batches = (total + batch_size - 1) // batch_size
        logger.info(f"\nNavigation planning:")
        logger.info(f"  Total unique IDs: {total}")
        logger.info(f"  Batch size (parallel tabs): {batch_size}")
        logger.info(f"  Navigation rounds needed: {batches}")
        return batches

    def run(self, searches_file):
        """Main pipeline

        Args:
            searches_file: Path to searches with group IDs from phase 3

        Returns:
            List of unique IDs
        """
        logger.info(f"Loading searches from {searches_file}...")

        with open(searches_file, 'r', encoding='utf-8') as f:
            searches = json.load(f)

        # Extract all IDs
        all_ids = self.extract_all_ids(searches)

        # Deduplicate
        unique_ids = self.deduplicate(all_ids)

        # Save unique IDs
        self.save_unique_ids(unique_ids, UNIQUE_IDS_JSON)

        # Save detailed mapping
        self.save_detailed_mapping(unique_ids)

        # Calculate navigation batches
        self.calculate_navigation_batches(unique_ids)

        logger.info("Phase 4 complete!")
        return unique_ids


def main():
    """Execute Phase 4"""
    import argparse

    parser = argparse.ArgumentParser(description='Phase 4: Deduplicate group IDs')
    parser.add_argument('--input', type=str, default=str(DATA_DIR / "searches_with_group_ids.json"),
                        help='Path to searches with group IDs from phase 3')

    args = parser.parse_args()

    deduplicator = GroupIDDeduplicator()
    unique_ids = deduplicator.run(args.input)

    logger.info(f"\nUnique IDs saved to {UNIQUE_IDS_JSON}")


if __name__ == '__main__':
    main()

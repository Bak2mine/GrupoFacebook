"""
Phase 2: Generate search configuration from city classification
Creates the Python script structure for phase 3 (Google searches)
"""

import json
import logging
from pathlib import Path
from config import DATA_DIR, BUILD_SCRIPT, LOG_LEVEL, LOG_FORMAT

# Setup logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)
logger = logging.getLogger(__name__)


class SearchBuilder:
    """Build search configuration from classified cities"""

    def __init__(self):
        self.searches = []
        self.search_count = 0

    def add_search(self, city_name, state, search_type, search_term):
        """Add a search entry

        Args:
            city_name: Name of city
            state: State abbreviation
            search_type: 'city' or 'neighborhood'
            search_term: Term to search for in Facebook
        """
        search_entry = {
            'city': city_name,
            'state': state,
            'type': search_type,
            'search_term': search_term,
            'group_ids': []
        }
        self.searches.append(search_entry)
        self.search_count += 1

    def build_from_classification(self, classification):
        """Build searches from city classification

        Args:
            classification: Dict from phase 1 classification

        Returns:
            List of search entries
        """
        logger.info("Building search configuration...")

        # Large cities: search by neighborhood (if available)
        for city in classification.get('large_cities', []):
            city_name = city['name']
            state = city['state']

            # For large cities, we could search by neighborhood, but defaulting to city
            # since neighborhood data isn't extracted from properties
            search_term = f"{city_name} {state}"
            self.add_search(city_name, state, 'city', search_term)
            logger.info(f"  Added search: {search_term} (type: city)")

        # Small cities: search by city
        for city in classification.get('small_cities', []):
            city_name = city['name']
            state = city['state']
            search_term = f"{city_name} {state}"
            self.add_search(city_name, state, 'city', search_term)
            logger.info(f"  Added search: {search_term} (type: city)")

        logger.info(f"Total searches configured: {self.search_count}")
        return self.searches

    def generate_python_script(self, searches, output_file):
        """Generate a Python script with search configuration

        Args:
            searches: List of search entries
            output_file: Path to save the script
        """
        logger.info(f"Generating Python script to {output_file}...")

        script_content = '''"""
Generated search configuration for Facebook groups
Phase 2 output - DO NOT EDIT MANUALLY (regenerate with phase2_build_searches.py)
"""

# Search configuration - format: (search_term, city, type, [group_ids])
# group_ids will be filled by phase 3 (Google search)
SEARCHES = [
'''

        for search in searches:
            script_content += f'''    {{
        'search_term': "{search['search_term']}",
        'city': "{search['city']}",
        'state': "{search['state']}",
        'type': "{search['type']}",
        'group_ids': []
    }},
'''

        script_content += ''']

def get_search_count():
    """Return total number of searches"""
    return len(SEARCHES)

def get_searches():
    """Return all searches"""
    return SEARCHES

def update_group_ids(search_index, group_ids):
    """Update group IDs for a specific search

    Args:
        search_index: Index in SEARCHES list
        group_ids: List of numeric Facebook group IDs
    """
    if 0 <= search_index < len(SEARCHES):
        SEARCHES[search_index]['group_ids'] = group_ids
'''

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(script_content)

        logger.info(f"Python script generated: {output_file}")

    def save_json_config(self, searches, output_file):
        """Also save as JSON for easy inspection

        Args:
            searches: List of search entries
            output_file: Path to save JSON
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(searches, f, ensure_ascii=False, indent=2)
        logger.info(f"JSON configuration saved to {output_file}")

    def run(self, classification_file):
        """Main pipeline

        Args:
            classification_file: Path to classification JSON from phase 1

        Returns:
            List of searches
        """
        logger.info(f"Loading classification from {classification_file}...")

        with open(classification_file, 'r', encoding='utf-8') as f:
            classification = json.load(f)

        searches = self.build_from_classification(classification)

        # Generate Python script
        self.generate_python_script(searches, BUILD_SCRIPT)

        # Also save as JSON
        json_config = DATA_DIR / "search_configuration.json"
        self.save_json_config(searches, json_config)

        logger.info("Phase 2 complete!")
        return searches


def main():
    """Execute Phase 2"""
    import argparse

    parser = argparse.ArgumentParser(description='Phase 2: Build search configuration')
    parser.add_argument('--input', type=str, default=str(DATA_DIR / "city_classification.json"),
                        help='Path to classification JSON from phase 1')

    args = parser.parse_args()

    builder = SearchBuilder()
    searches = builder.run(args.input)

    logger.info(f"\nSearch Summary:")
    logger.info(f"  Total searches: {len(searches)}")
    logger.info(f"  Output script: {BUILD_SCRIPT}")


if __name__ == '__main__':
    main()

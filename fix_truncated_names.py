"""
Smart substitution for truncated city names
Only substitutes when safe based on context (state abbreviations)
"""

import json
from pathlib import Path

# Mapping of truncated -> full names
TRUNCATION_MAP = {
    'Janeiro': 'Rio de Janeiro',
    'Paulo': 'São Paulo',
    'Leopoldo': 'São Leopoldo',
    'José': 'São José',
    'Pessoa': 'João Pessoa',
    'Luís': 'São Luís',
}

# State mappings to verify context
STATE_CITIES = {
    'RJ': ['Janeiro', 'Nilópolis', 'Jacarepaguá'],  # Rio de Janeiro, etc.
    'SP': ['Paulo', 'Preto', 'José', 'Luís'],  # São Paulo, São José do Rio Preto, São José, São Luís
    'RS': ['Leopoldo', 'Cachoeirinha'],  # São Leopoldo
    'PB': ['Pessoa'],  # João Pessoa
    'MA': ['Luís'],  # São Luís
}

def fix_city_name_in_search_term(search_term: str, state: str) -> str:
    """
    Intelligently substitute truncated city names based on state context

    Args:
        search_term: e.g., "Paulo SP" or "Amaralina Paulo"
        state: State abbreviation from search config

    Returns:
        Fixed search term, e.g., "São Paulo SP" or unchanged if not safe
    """
    # Quick check: if state is not in our STATE_CITIES, don't substitute
    if state not in STATE_CITIES:
        return search_term

    words = search_term.split()
    fixed_words = []

    for i, word in enumerate(words):
        # Check if this word is a truncation
        if word in TRUNCATION_MAP:
            # Verify it's safe based on state
            truncated = word
            if truncated in STATE_CITIES.get(state, []):
                # Safe to substitute!
                fixed_words.append(TRUNCATION_MAP[truncated])
            else:
                # Not safe for this state, keep original
                fixed_words.append(word)
        else:
            fixed_words.append(word)

    return ' '.join(fixed_words)


def fix_city_names_in_file():
    """Apply substitutions to searches_with_group_ids.json - callable from pipeline"""

    search_file = Path('data/searches_with_group_ids.json')

    if not search_file.exists():
        print(f'[WARNING] {search_file} not found, skipping name fixes')
        return False

    with open(search_file, 'r', encoding='utf-8') as f:
        searches = json.load(f)

    changes = 0
    for search in searches:
        old_term = search.get('search_term', '')
        state = search.get('state', '')

        if old_term and state:
            new_term = fix_city_name_in_search_term(old_term, state)

            if new_term != old_term:
                print(f'[FIXED] {old_term:30} -> {new_term:30} ({state})')
                search['search_term'] = new_term
                changes += 1

    print(f'Total changes: {changes}')

    # Save updated file
    with open(search_file, 'w', encoding='utf-8') as f:
        json.dump(searches, f, ensure_ascii=False, indent=2)

    print(f'Saved to {search_file}')
    return True


def main():
    """CLI entry point"""
    print('Applying smart name substitutions...\n')
    fix_city_names_in_file()


if __name__ == '__main__':
    main()

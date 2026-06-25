"""
Analyze which truncated words can be safely substituted
"""

import json

# Load bairro data
with open('data/bairros_by_city.json', 'r', encoding='utf-8') as f:
    bairros = json.load(f)

# Load search config
with open('data/searches_with_group_ids.json', 'r', encoding='utf-8') as f:
    searches = json.load(f)

print('\nANALYZING TRUNCATED WORDS:')
print('='*80)

truncated_words = {
    'Janeiro': 'Rio de Janeiro',
    'Paulo': 'São Paulo',
    'Leopoldo': 'São Leopoldo',
    'José': 'São José',
    'Pessoa': 'João Pessoa',
    'Luís': 'São Luís',
}

safe_to_substitute = []
unsafe_words = []

# Check each truncated word
for truncated, full_name in truncated_words.items():
    print(f'\n{truncated} -> {full_name}')
    print('-' * 80)

    # Check if this word appears in any bairro name
    bairro_matches = []
    for city, bairro_list in bairros.items():
        for bairro in bairro_list:
            if truncated.lower() in bairro.lower():
                bairro_matches.append((city, bairro))

    # Check if this word appears in any search term (not as the sole word)
    search_matches = []
    for search in searches:
        search_term = search.get('search_term', '')
        if search_term and truncated.lower() in search_term.lower():
            # Don't count if it's just the truncated word alone
            if search_term.lower() != truncated.lower():
                search_matches.append(search_term)

    is_safe = not bool(bairro_matches) and not bool(search_matches)

    if bairro_matches:
        print(f'[WARNING] Found in {len(bairro_matches)} bairro name(s):')
        for city, bairro in bairro_matches[:5]:  # Show first 5
            print(f'  - {bairro} ({city})')
        if len(bairro_matches) > 5:
            print(f'  ... and {len(bairro_matches) - 5} more')

    if search_matches:
        unique_matches = set(search_matches)
        print(f'[WARNING] Found in {len(unique_matches)} search term(s):')
        for term in list(unique_matches)[:5]:
            print(f'  - {term}')
        if len(unique_matches) > 5:
            print(f'  ... and {len(unique_matches) - 5} more')

    if not bairro_matches and not search_matches:
        print('[SAFE] Can safely substitute!')
        safe_to_substitute.append((truncated, full_name))
    else:
        unsafe_words.append((truncated, full_name))

print('\n' + '='*80)
print('SUMMARY:')
print('='*80)

print(f'\nSafe to substitute ({len(safe_to_substitute)}):')
for truncated, full_name in safe_to_substitute:
    print(f'  {truncated} -> {full_name}')

if unsafe_words:
    print(f'\nUNSAFE to substitute ({len(unsafe_words)}):')
    for truncated, full_name in unsafe_words:
        print(f'  {truncated} -> {full_name} (could conflict)')

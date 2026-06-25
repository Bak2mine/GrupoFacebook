"""
Check what group details are available in the scraped data
"""

import json

with open('data/searches_with_group_ids.json', 'r', encoding='utf-8') as f:
    searches = json.load(f)

print('\nANALYZING GROUP DETAILS IN SCRAPED DATA:')
print('='*80)

# Check what's in group_details
for i, search in enumerate(searches[:3]):
    search_term = search.get('search_term', '')
    print(f'\nSearch {i+1}: {search_term}')
    print('-'*80)

    group_details = search.get('group_details', [])
    print(f'Group details available: {len(group_details)} items')

    if group_details:
        for j, group in enumerate(group_details[:3]):
            print(f'  Group {j+1}:')
            for key, val in group.items():
                print(f'    {key}: {val}')
    else:
        print('  (empty)')

print('\n' + '='*80)
print('CHECKING GROUP NAMES ACROSS ALL SEARCHES:')
print('='*80)

all_names = set()
for search in searches:
    for group in search.get('group_details', []):
        name = group.get('name', '')
        if name:
            all_names.add(name)

print(f'\nTotal unique group names found: {len(all_names)}')

if all_names:
    print('\nSample group names:')
    for name in list(all_names)[:10]:
        print(f'  - {name}')
else:
    print('\nNo group names found in group_details!')

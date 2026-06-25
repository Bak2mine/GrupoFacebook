"""
Analyze how many groups were found per search
"""

import json

with open('data/searches_with_group_ids.json', 'r', encoding='utf-8') as f:
    searches = json.load(f)

print('\nGROUPS FOUND PER SEARCH:')
print('='*80)

groups_per_search = []
for search in searches:
    count = len(search.get('group_ids', []))
    groups_per_search.append(count)
    search_term = search.get('search_term', '')[:40]
    print(f'{search_term:40} | {count} groups')

print()
print('='*80)
print(f'Average groups per search: {sum(groups_per_search)/len(groups_per_search):.1f}')
print(f'Min: {min(groups_per_search)}, Max: {max(groups_per_search)}')
print()

# Check if all searches got exactly 10
all_ten = all(count == 10 for count in groups_per_search)
print(f'All searches returned exactly 10 groups: {all_ten}')

if not all_ten:
    print()
    print('Searches with fewer than 10 groups:')
    for search, count in zip(searches, groups_per_search):
        if count < 10:
            term = search.get('search_term', '')
            print(f'  {term}: {count} groups')

print()
print('SUMMARY:')
print('='*80)
print(f'Total searches: {len(searches)}')
print(f'Total groups (with duplicates): {sum(groups_per_search)}')
print(f'Unique groups: {len(set(g for s in searches for g in s.get("group_ids", [])))}')
print(f'Duplicate groups: {sum(groups_per_search) - len(set(g for s in searches for g in s.get("group_ids", [])))}')

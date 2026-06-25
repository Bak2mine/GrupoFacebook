"""Verify data quality"""
import json

print("=== DATA QUALITY VERIFICATION ===\n")

with open('data/searches_with_group_ids.json', 'r', encoding='utf-8') as f:
    searches = json.load(f)

with open('data/group_names.json', 'r', encoding='utf-8') as f:
    names = json.load(f)

# Check 1: Unique IDs
all_ids = [gid for s in searches for gid in s['group_ids']]
unique_ids = set(all_ids)

print(f"Total group IDs in searches: {len(all_ids)}")
print(f"Unique group IDs: {len(unique_ids)}")
print(f"Duplicates: {len(all_ids) - len(unique_ids)}")
print(f"Names dict entries: {len(names)}")
print()

# Check 2: Sample entries
print("SAMPLE ENTRIES:")
print()
s = searches[0]
print(f"Search 1 - {s['city']} ({s['state']})")
print(f"  Groups: {len(s['group_ids'])}")
print(f"  IDs: {s['group_ids'][:3]}...")
print()

print("Group names for these IDs:")
for gid in s['group_ids'][:3]:
    print(f"  ID {gid}: {names.get(gid, 'MISSING')}")
print()

# Check 3: Look for problematic entries
print("CHECKING FOR ISSUES:")
print()

# Find groups with 0 population in searches
zero_pop_count = sum(1 for s in searches if 'population' in s and s['population'] == 0)
print(f"Searches with 0 population: {zero_pop_count}")

# Check ID range
ids_list = list(unique_ids)
ids_int = [int(gid) for gid in ids_list]
print(f"ID range: {min(ids_int)} to {max(ids_int)}")
print(f"First 5 IDs: {sorted(ids_int)[:5]}")
print(f"Last 5 IDs: {sorted(ids_int)[-5:]}")
print()

# Verify each search has unique groups
print("SEARCH GROUP DISTRIBUTION:")
for search in searches[:5]:
    print(f"  {search['city']}: {len(search['group_ids'])} groups")
print(f"  ... and {len(searches) - 5} more cities")
print()

# Final status
all_good = (
    len(all_ids) == len(unique_ids) and  # No duplicates
    len(unique_ids) == len(names) and    # All IDs have names
    len(searches) == 42                  # Correct number of cities
)

print(f"Status: {'PASS - All data quality checks passed!' if all_good else 'FAIL - Issues detected'}")

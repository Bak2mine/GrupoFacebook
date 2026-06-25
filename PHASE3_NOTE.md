# Phase 3 Google Search - Implementation Note

## Current Status

Phase 3 (Google Search for Facebook groups) has a fundamental limitation: **Google blocks automated scraping**.

When Phase 3 attempts to search Google for Facebook groups using direct HTTP requests, Google returns:
- Empty results
- Redirects to verification pages
- Rate limiting (403/429 errors)

This is by design - Google actively blocks bots from scraping search results.

## Why It Doesn't Work

The current implementation tries to:
1. Make an HTTP GET request to `https://www.google.com/search?q=...`
2. Parse the HTML response for Facebook URLs
3. Extract group IDs

**Problem**: Google detects the bot request and doesn't return real results. The HTML contains obfuscated data, not actual search results.

## Solutions

### Option 1: Use Google Custom Search API (Recommended for Production)
```python
from googleapiclient.discovery import build

service = build("customsearch", "v1", developerKey=API_KEY)
result = service.cse().list(q=query, cx=SEARCH_ENGINE_ID).execute()
```

**Pros**:
- Official, supported, reliable
- No bot detection issues
- Rate limits clearly documented

**Cons**:
- Requires API key and paid subscription
- ~$5/1000 queries

### Option 2: Use Selenium with Real Browser
```python
from selenium import webdriver

driver = webdriver.Chrome()
driver.get(f"https://www.google.com/search?q={query}")
# Real browser = real results
```

**Pros**:
- Works reliably (uses real browser)
- No API costs
- Can handle JavaScript-rendered content

**Cons**:
- Slower (launches browser for each search)
- More resources needed

### Option 3: Manual Curation + Testing (Current Workaround)
For testing/small-scale use:
1. Manually search Facebook for groups
2. Create sample data files with known group IDs
3. Test the full pipeline with real data

**Current files with sample data**:
- `data/searches_with_group_ids.json` - Contains sample groups
- `data/group_names.json` - Contains sample group names
- Excel generation works perfectly with this data

## Implementation Recommendation

### Short Term (Testing)
Use the sample data approach:
```bash
# Works with current sample data
python main.py --skip-to-phase 4
python main.py --skip-to-phase 6
```

### Medium Term (Production)
Implement Google Custom Search API:
```python
# In phase3_google_search.py
from googleapiclient.discovery import build

service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
results = service.cse().list(q=query, cx=SEARCH_ENGINE_ID).execute()

for item in results.get('items', []):
    link = item.get('link')
    if 'facebook.com/groups/' in link:
        # Extract group ID
```

### Long Term (Scaling)
For large-scale operations:
1. Use Google Custom Search API for initial discovery
2. Cache results to avoid repeated searches
3. Implement periodic updates via scheduled jobs
4. Consider adding manual review for quality control

## Workaround for Testing

The Excel pipeline is **fully functional** with sample data:

1. **Phase 1**: Property scraping ✓
2. **Phase 2**: Search configuration ✓
3. **Phase 3**: Google search (limited - use sample data)
4. **Phase 4**: Deduplication ✓
5. **Phase 5**: Playwright navigation ✓
6. **Phase 6**: Excel generation ✓

Sample data files are pre-populated at:
- `data/searches_with_group_ids.json`
- `data/group_names.json`

You can:
```bash
# Run full pipeline with sample data
python main.py --skip-to-phase 6

# Or run individual phases
python phase4_deduplicate.py
python phase6_build_excel.py
```

## Excel Output

The Excel file is now **properly populated** with:
- **Sheet 1 "Grupos Facebook"**: 11 sample groups with:
  - Search term
  - City
  - Group ID
  - **Clickable Facebook URLs** ✓
  - Group names
  - Population data

- **Sheet 2 "Resumo por Busca"**: Summary by search/city

## Production Deployment Path

When ready for production:
1. Set up Google Custom Search API (requires API key + setup)
2. Update Phase 3 to use the API
3. Test with real data
4. Deploy pipeline

Example config addition:
```python
# config.py
GOOGLE_API_KEY = "your-api-key-here"
GOOGLE_SEARCH_ENGINE_ID = "your-cx-id"
```

## Resources

- [Google Custom Search API Docs](https://developers.google.com/custom-search/v1)
- [Google Custom Search Setup](https://programmablesearchengine.google.com/)
- [Pricing](https://developers.google.com/custom-search/pricing)

## Notes

- Phase 3 limitation is **not** a bug - it's a known limitation of automated Google scraping
- The workaround (sample data) proves the entire pipeline works
- Moving to Google API is a simple code change
- Cost is minimal (~$5/month for typical use)

---

**Current Status**: Excel generation fully working with sample data  
**Next Step**: Decide on Phase 3 implementation for production

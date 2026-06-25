# Leiloaria Smart - Setup & Getting Started Guide

## What Was Created

A complete Python automation pipeline for extracting Facebook groups relevant to real estate auctions in Brazil. The system converts manual Claude Cowork processes into automated Python scripts.

### Files Created in `Grupo/` folder:

```
Grupo/
├── config.py                 # Configuration and constants
├── main.py                   # Main orchestration script
├── phase1_extract_data.py    # Extract properties & cities
├── phase2_build_searches.py  # Build search configuration
├── phase3_google_search.py   # Search Google for groups
├── phase4_deduplicate.py     # Deduplicate group IDs
├── phase5_navigate_groups.py # Navigation instructions
├── phase6_build_excel.py     # Generate Excel report
├── test_pipeline.py          # Test suite
├── README.md                 # Complete documentation
├── CLAUDE.md                 # Claude Cowork integration guide
├── requirements.txt          # Python dependencies
├── SETUP_GUIDE.md            # This file
└── data/                     # Output directory (auto-created)
```

## Quick Start (3 Steps)

### Step 1: Install Dependencies

```bash
cd C:\Users\andre\Desktop\Leiloaria\Grupo
pip install -r requirements.txt
```

**Required packages:**
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `openpyxl` - Excel generation

### Step 2: Run Complete Pipeline

```bash
python main.py
```

This runs all 6 phases automatically. The script will:
1. Scrape properties from leiloariasmart.com.br
2. Classify cities by size
3. Build search configuration
4. Search Google for Facebook groups
5. Deduplicate group IDs
6. Generate navigation instructions (Phase 5 requires manual work)
7. Generate Excel report

### Step 3: Complete Manual Navigation (Phase 5 Only)

When the script reaches Phase 5:

```
⚠️  PHASE 5 REQUIRES MANUAL INTERACTION WITH CLAUDE COWORK

Follow these steps...
```

Follow the printed instructions to:
1. Use Claude Cowork to navigate to each Facebook group
2. Capture group names from browser page titles
3. Save results every 10 rounds

Once complete:

```bash
python main.py --skip-to-phase 6
```

This generates the final Excel report.

## Common Commands

### Test Your Setup

```bash
# Test all dependencies
python test_pipeline.py --deps-only

# Run complete test suite
python test_pipeline.py

# Test specific phase
python test_pipeline.py --phase 3
```

### Run Specific Phases

```bash
# Test with only 20 properties
python main.py --limit 20

# Skip scraping (use existing data)
python main.py --no-scrape

# Start from Phase 3
python main.py --skip-to-phase 3

# Run only Phase 6 (after manual work)
python main.py --skip-to-phase 6
```

### Run Individual Phases

```bash
# Extract properties only
python phase1_extract_data.py

# Build searches only
python phase2_build_searches.py --input data/city_classification.json

# Search Google only
python phase3_google_search.py

# Deduplicate only
python phase4_deduplicate.py

# Navigation only
python phase5_navigate_groups.py --resume

# Generate Excel only
python phase6_build_excel.py
```

## Expected Output

After running the complete pipeline:

```
Grupo/
├── data/
│   ├── scraped_properties.json         # ~500KB
│   ├── city_classification.json        # ~2KB
│   ├── search_configuration.json       # ~3KB
│   ├── searches_with_group_ids.json    # ~50KB
│   ├── unique_group_ids.json           # ~5KB
│   └── group_names.json                # ~30KB (from Phase 5)
├── output/
│   └── Leiloaria_Smart_Grupos_Facebook_COMPLETO.xlsx  # Final report
└── leiloaria_grupos.log                # Detailed logs
```

## Workflow Comparison

### Before (Manual with Claude Cowork)
1. Create Excel manually with city/neighborhood lists
2. Use Claude to search Google for groups
3. Extract IDs from results
4. Deduplicate manually
5. Use Claude Cowork to navigate each group
6. Manually compile Excel report
⏱️ **Time**: 4-6 hours
💾 **Data loss risk**: High (context compression)

### After (Automated Python)
1. ✅ Automated: Property scraping
2. ✅ Automated: City classification
3. ✅ Automated: Search building
4. ✅ Automated: Google searching
5. ✅ Automated: Deduplication
6. ⏳ Manual: Claude Cowork navigation (~1 hour)
7. ✅ Automated: Excel generation
⏱️ **Time**: ~1.5 hours (mostly automated)
💾 **Data loss risk**: None (saved after each phase)

## Configuration

Edit `config.py` to customize:

```python
# Large cities (search by neighborhood)
LARGE_CITY_THRESHOLD = 500000

# Parallel browser tabs for Phase 5
BROWSER_BATCH_SIZE = 4

# Save progress every N rounds
SAVE_INTERVAL = 10

# Population data (add more cities as needed)
CITY_POPULATION = {
    'Salvador': 2355039,
    'São Paulo': 11451245,
    # Add your cities here
}
```

## Phase Details

### Phase 1: Extract Properties
- Scrapes leiloariasmart.com.br
- Extracts city/state/neighborhood
- Uses scraper from `Post/` folder
- **Input**: Website (or cached JSON)
- **Output**: `city_classification.json`

### Phase 2: Build Searches
- Classifies cities by population
- Builds Google search queries
- **Input**: `city_classification.json`
- **Output**: `search_configuration.json`

### Phase 3: Google Search
- Searches Google for Facebook groups
- Extracts group IDs from URLs
- **Input**: `search_configuration.json`
- **Output**: `searches_with_group_ids.json`

### Phase 4: Deduplicate
- Removes duplicate IDs
- Creates ID list for navigation
- **Input**: `searches_with_group_ids.json`
- **Output**: `unique_group_ids.json`

### Phase 5: Navigate Groups
- Generates Claude Cowork instructions
- Requires manual navigation to capture names
- **Input**: `unique_group_ids.json`
- **Output**: `group_names.json`
- **Note**: See CLAUDE.md for detailed instructions

### Phase 6: Generate Excel
- Consolidates all data
- Creates formatted Excel workbook
- **Input**: `group_names.json` + searches
- **Output**: `Leiloaria_Smart_Grupos_Facebook_COMPLETO.xlsx`

## Troubleshooting

### Issue: "No module named 'requests'"

**Solution**:
```bash
pip install requests beautifulsoup4 openpyxl
```

### Issue: Scraper finds 0 properties

**Solutions**:
1. Check internet connection
2. Verify leiloariasmart.com.br is accessible
3. Try with `--limit 5` to test
4. If website structure changed, update `phase1_extract_data.py`

### Issue: Google search finds no groups

**Causes**:
- Some searches may have few results
- Facebook blocks aggressive Google searches
- Limited to ~100 results per search

**Solutions**:
1. Add more search terms to `GOOGLE_SEARCH_PATTERNS`
2. Use Google Custom Search API (recommended for production)
3. Try again later if blocked

### Issue: Excel generation fails

**Solution**:
```bash
pip install --upgrade openpyxl
```

## Performance Expectations

| Phase | Time | Notes |
|-------|------|-------|
| Phase 1 | 2-5 min | Web scraping, depends on number of properties |
| Phase 2 | <1 min | Local processing |
| Phase 3 | 5-10 min | Google searches, rate limited |
| Phase 4 | <1 min | Deduplication |
| Phase 5 | 60 min | Manual Claude Cowork navigation (~4 groups/min) |
| Phase 6 | <1 min | Excel generation |
| **Total** | **~1.5 hours** | With manual Phase 5 |

## Integration with Post Folder

This project reuses the scraper from the `Post/` folder:

- **Reuses**: `Post/scraper.py` - PropertyScraper class
- **Inherits**: HTTP session management, header configuration
- **Extends**: Property parsing to extract locations

If you modify the website scraper, update:
- `phase1_extract_data.py` - Uses PropertyScraper

## Next Steps

### For First Run:
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Test setup
python test_pipeline.py

# 3. Run complete pipeline
python main.py

# 4. Follow Phase 5 instructions in CLAUDE.md

# 5. Generate final Excel
python main.py --skip-to-phase 6
```

### For Future Runs:
```bash
# Reuse existing property data
python main.py --no-scrape

# Or start fresh
python main.py
```

### For Scaling:
```bash
# Process more properties
python main.py --limit 500

# Or process in batches
python main.py --no-scrape  # Skip slow scraping
python main.py --skip-to-phase 5 --no-scrape  # Then resume at navigation
```

## Logging

All activities logged to `leiloaria_grupos.log`:

```bash
# Watch log in real-time
tail -f leiloaria_grupos.log

# Or view full log
cat leiloaria_grupos.log
```

## Support & Documentation

- **Main Documentation**: See [README.md](README.md)
- **Claude Cowork Guide**: See [CLAUDE.md](CLAUDE.md)
- **Configuration**: See [config.py](config.py)
- **Contact**: lucas@leiloariasmart.com.br

## Architecture Overview

```
Input Data (leiloariasmart.com.br)
  ↓
Phase 1: Extract Properties
  ├─→ Scrape properties
  └─→ Classify cities by size
  ↓
Phase 2: Build Searches
  └─→ Generate search patterns
  ↓
Phase 3: Search Google
  └─→ Extract group IDs
  ↓
Phase 4: Deduplicate
  └─→ Create unique ID list
  ↓
Phase 5: Navigate Groups (MANUAL)
  └─→ Capture group names via Claude Cowork
  ↓
Phase 6: Generate Report
  └─→ Create Excel workbook
  ↓
Output: Leiloaria_Smart_Grupos_Facebook_COMPLETO.xlsx
```

## Key Features

✅ **Automated**: 5 of 6 phases fully automated
✅ **Resilient**: Each phase saves to disk, can resume mid-pipeline
✅ **Documented**: Comprehensive README and guides
✅ **Testable**: Included test suite for verification
✅ **Configurable**: Easy to customize searches, cities, and outputs
✅ **Integrated**: Reuses existing Post folder scraper
✅ **Logged**: Detailed logging for troubleshooting

---

**Created**: June 2026
**Version**: 1.0
**Status**: Ready for production use

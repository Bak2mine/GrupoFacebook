# Leiloaria Smart - Facebook Groups Automation

Automated extraction of Facebook groups relevant to real estate auctions in Brazil. This pipeline scrapes property data, identifies relevant cities, searches for Facebook groups, and generates a comprehensive Excel report.

## Overview

The automation pipeline consists of 6 phases:

1. **Phase 1**: Extract property data from leiloariasmart.com.br
2. **Phase 2**: Build search configuration from cities/neighborhoods
3. **Phase 3**: Search Google for Facebook group IDs
4. **Phase 4**: Deduplicate group IDs
5. **Phase 5**: Navigate Facebook groups and capture real names (requires Claude Cowork)
6. **Phase 6**: Generate final Excel report

## Quick Start

### Prerequisites

```bash
pip install -r requirements.txt
```

**Required packages:**
- `requests` - HTTP requests for scraping and searching
- `beautifulsoup4` - HTML parsing
- `openpyxl` - Excel file generation

### Run Complete Pipeline

```bash
python main.py
```

This runs all phases sequentially from start to finish.

### Run Specific Phases

```bash
# Start from Phase 3 (skip scraping and search building)
python main.py --skip-to-phase 3

# Skip property scraping (use existing data)
python main.py --no-scrape

# Limit scraping to 50 properties for testing
python main.py --limit 50

# Resume from Phase 5 after Claude Cowork navigation
python main.py --skip-to-phase 5
```

## Detailed Phase Descriptions

### Phase 1: Extract Property Data

**File**: `phase1_extract_data.py`

Scrapes properties from leiloariasmart.com.br and extracts city/neighborhood information.

**Output files:**
- `data/scraped_properties.json` - Raw property data
- `data/city_classification.json` - Cities classified by size

**Run directly:**
```bash
python phase1_extract_data.py --limit 100
```

**Features:**
- Integrates with Post folder scraper
- Classifies cities by population (large = neighborhood search, small = city search)
- Automatic extraction of location from property titles

### Phase 2: Build Search Configuration

**File**: `phase2_build_searches.py`

Generates search configurations from classified cities.

**Output files:**
- `data/search_configuration.json` - Search queries for each city

**Run directly:**
```bash
python phase2_build_searches.py
```

**Features:**
- Creates search patterns for Google searches
- Handles both large and small cities
- Configurable search terms

### Phase 3: Search Google for Facebook Groups

**File**: `phase3_google_search.py`

Searches Google for Facebook group URLs matching each city/neighborhood.

**Output files:**
- `data/searches_with_group_ids.json` - Searches with extracted group IDs

**Run directly:**
```bash
python phase3_google_search.py
```

**Features:**
- Multiple search patterns for better coverage
- Extracts numeric group IDs from URLs
- Respectful rate limiting (1-second delays)
- Tracks failed searches

**Note**: Uses requests library for simplicity. For production, consider:
- Google Custom Search API
- Selenium with more sophisticated scraping
- Rotating proxies for larger-scale searches

### Phase 4: Deduplicate Group IDs

**File**: `phase4_deduplicate.py`

Removes duplicate group IDs across searches while tracking which searches they appear in.

**Output files:**
- `data/unique_group_ids.json` - List of unique group IDs
- `data/group_ids_detailed.json` - Detailed ID mapping

**Run directly:**
```bash
python phase4_deduplicate.py
```

**Features:**
- Preserves first occurrence of each ID
- Calculates navigation batches needed for Phase 5
- Generates detailed mapping of IDs to searches

### Phase 5: Navigate Facebook Groups

**File**: `phase5_navigate_groups.py`

**⚠️ REQUIRES MANUAL INTERACTION WITH CLAUDE COWORK**

This phase generates navigation instructions for Claude Cowork to:
1. Navigate to each Facebook group URL
2. Capture the group name from the browser page title
3. Save results periodically

**Output files:**
- `data/group_names.json` - Mapping of group ID → group name

**Run directly:**
```bash
python phase5_navigate_groups.py --resume
```

**How to Use:**

1. Run the script to generate instructions:
   ```bash
   python main.py --skip-to-phase 5
   ```

2. Follow the printed navigation instructions to:
   - Open Claude Cowork
   - Use Claude in Chrome to navigate to Facebook groups
   - Capture group names from page titles
   - Save group_names.json every 10 rounds

3. Resume or continue with Phase 6 once navigation complete

**Process Overview:**
- 4 browser tabs operate in parallel (batch size = 4)
- Always reset to Google before navigating to Facebook (security requirement)
- Read page titles separately with `tabs_context_mcp` (never trust batch context)
- Save progress every 10 rounds (~40 groups)

**Important Rules:**
- ❌ Never navigate Facebook→Facebook in same batch (Permission Denied)
- ✅ Always reset to Google first, then navigate to Facebook
- ✅ Call `tabs_context_mcp` separately after navigation
- ✅ Save `group_names.json` every 10 rounds

### Phase 6: Generate Excel Report

**File**: `phase6_build_excel.py`

Consolidates all data into a formatted Excel workbook.

**Output files:**
- `output/Leiloaria_Smart_Grupos_Facebook_COMPLETO.xlsx`

**Run directly:**
```bash
python phase6_build_excel.py
```

**Excel Sheets:**

**Sheet 1: Grupos Facebook**
- Columns: Busca, Cidade, Tipo, ID, URL, Nome do Grupo, Habitantes
- One row per group per search
- Clickable URLs to Facebook groups
- Yellow highlighting for private groups

**Sheet 2: Resumo por Busca**
- Columns: Busca, Cidade, Tipo, Qtd. Grupos, Habitantes
- Summary aggregated by search
- Shows group count per search
- Shows population of each city

**Features:**
- Formatted headers with blue background
- Clickable hyperlinks to Facebook groups
- Population numbers formatted with thousands separator
- Yellow highlighting for groups marked as "Grupo Privado"
- Frozen header row for easy scrolling
- Optimized column widths

## Data Directory Structure

```
Grupo/
├── data/
│   ├── scraped_properties.json         # Phase 1 output
│   ├── city_classification.json        # Phase 1 output
│   ├── search_configuration.json       # Phase 2 output
│   ├── searches_with_group_ids.json    # Phase 3 output
│   ├── unique_group_ids.json           # Phase 4 output
│   ├── group_ids_detailed.json         # Phase 4 output
│   └── group_names.json                # Phase 5 output
├── output/
│   └── Leiloaria_Smart_Grupos_Facebook_COMPLETO.xlsx
├── .temp/                              # Temporary files
├── config.py                           # Configuration
├── phase1_extract_data.py
├── phase2_build_searches.py
├── phase3_google_search.py
├── phase4_deduplicate.py
├── phase5_navigate_groups.py
├── phase6_build_excel.py
├── main.py                             # Orchestration script
└── README.md
```

## Configuration

Edit `config.py` to customize:

```python
# Large cities threshold for search type
LARGE_CITY_THRESHOLD = 500000

# Number of parallel tabs for navigation
BROWSER_BATCH_SIZE = 4

# Save interval for group names
SAVE_INTERVAL = 10  # Save every 10 rounds

# Population data (IBGE 2022)
CITY_POPULATION = {
    'Salvador': 2355039,
    'São Paulo': 11451245,
    # ... add more cities
}
```

## Examples

### Example 1: Quick Test Run

Test the pipeline with limited data:

```bash
python main.py --limit 20
```

This runs the complete pipeline with only 20 properties scraped, which is faster for testing.

### Example 2: Reuse Existing Property Data

Skip scraping and use previously scraped properties:

```bash
python main.py --no-scrape
```

This runs phases 2-6, reusing `data/scraped_properties.json` from a previous run.

### Example 3: Resume After Claude Cowork Session

After completing Phase 5 navigation in Claude Cowork:

```bash
python main.py --skip-to-phase 6
```

This skips directly to Excel generation using the captured group names.

### Example 4: Run Individual Phases

Run a specific phase standalone:

```bash
python phase3_google_search.py
python phase4_deduplicate.py
```

## Troubleshooting

### Phase 1: No properties scraped

**Problem**: Script returns 0 properties

**Solutions**:
- Check internet connection
- Verify leiloariasmart.com.br is accessible
- Check if website structure changed (may need HTML selector updates in scraper.py)
- Try with `--limit 5` to test with fewer properties

### Phase 3: Few or no group IDs found

**Problem**: Google search finds few Facebook groups

**Solutions**:
- Some searches may have limited results on Facebook
- Add more search terms to `GOOGLE_SEARCH_PATTERNS` in config.py
- Use Google Custom Search API for more reliable results
- Consider using Selenium with JavaScript rendering

### Phase 5: Browser navigation issues

**Problem**: "Permission denied" errors in Claude Cowork

**Solutions**:
- ✅ Always reset tabs to Google BEFORE navigating to Facebook
- ✅ Call `tabs_context_mcp` SEPARATELY after batch navigation
- Check that you're using correct tab IDs
- Review browser console for errors

### Phase 6: Excel generation fails

**Problem**: "openpyxl not available"

**Solution**:
```bash
pip install openpyxl
```

## Performance Characteristics

Based on pilot project (258 groups):

| Metric | Value |
|--------|-------|
| Properties scraped | 130+ |
| Unique cities found | 43 |
| Search queries performed | 43 |
| Initial group IDs (raw) | 350+ |
| Unique group IDs | 258 |
| Navigation batches | 65 |
| Execution time | ~2 hours (with Claude Cowork) |

Time varies based on:
- Number of properties to scrape
- Google search response times
- Facebook group page load times
- Manual work in Claude Cowork

## Integration with Post Folder

This project integrates with the existing `Post` folder scraper:

- **Reuses**: `scraper.py` to extract property data from leiloariasmart.com.br
- **Shares**: Configuration patterns and HTTP session management
- **Extends**: Property parsing to extract geographic information

To use different property sources:

1. Implement a data provider in Phase 1 that matches the interface:
   ```python
   properties = [
       {
           'titulo': str,
           'cidade': str,
           'estado': str,
           'praca1_valor': str,
           # ...
       }
   ]
   ```

2. Update `DataExtractor.scrape_properties()` to use your source

## Advanced Topics

### Extending the Pipeline

To add a new phase or modify existing ones:

1. Create `phaseN_description.py` file
2. Implement a class with a `run()` method
3. Add phase to `main.py` in the `run_all_phases()` method
4. Update documentation

### Handling Private Groups

Groups that return generic "Facebook" as name are marked as "Grupo Privado" in the Excel:

- Visible with yellow highlighting in Excel
- Represent groups with restricted access
- Team members can manually attempt to join and verify

### Scaling to Larger Datasets

For 500+ groups:

1. Divide navigation into multiple sessions:
   ```bash
   # Session 1: Groups 1-150
   python main.py --skip-to-phase 5
   
   # Session 2: Groups 151-300
   python main.py --skip-to-phase 5 --resume
   ```

2. Use process manager for long-running tasks:
   ```bash
   nohup python main.py > output.log 2>&1 &
   ```

3. Consider database storage instead of JSON for very large datasets

## Known Limitations

1. **Phase 3 (Google Search)**: Basic implementation using requests library
   - Limited to ~100 results per search
   - May be blocked by Google with aggressive use
   - Recommended: Use Google Custom Search API for production

2. **Phase 5 (Manual Navigation)**: Requires Claude Cowork interaction
   - Cannot be fully automated due to Facebook's anti-bot protections
   - Private groups cannot be accessed without membership
   - Session timeouts may require resuming navigation

3. **Population Data**: Uses IBGE 2022 census
   - Not all cities may be included
   - Population changes over time
   - Can be manually updated in `CITY_POPULATION` dict

## Future Enhancements

Suggested improvements (referenced in documentation):

1. **Phase 5 Automation**:
   - Integrate with Playwright for direct browser control
   - Use Claude API directly instead of Claude Cowork
   - Cache group names to avoid re-navigation

2. **Post-Generation**:
   - Automatic message sending to groups
   - Periodic group status monitoring
   - Integration with dispatch control spreadsheet
   - Monthly automated updates via `/schedule` skill

3. **Reporting**:
   - Analytics dashboard
   - Group performance tracking
   - Response rate monitoring

## Logs

All logging is saved to `leiloaria_grupos.log`. Check this file for:
- Detailed error messages
- Performance metrics
- Data statistics

## Support

For questions about this process, contact:
- Lucas — lucas@leiloariasmart.com.br

Generated by Claude Code | Leiloaria Smart | 2026

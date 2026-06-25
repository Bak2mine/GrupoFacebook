# Phase 5: Automated Browser Navigation with Playwright

This guide explains how Phase 5 now works with Playwright for fully automated group name capture (no Claude Cowork needed).

## Overview

Phase 5 uses Playwright to automatically:
1. Navigate to each Facebook group URL
2. Wait for page to load
3. Capture the group name from the page title
4. Save results to `group_names.json`

**No manual intervention required!**

## Prerequisites

### 1. Install Playwright

```bash
pip install playwright
```

### 2. Install Browser

```bash
playwright install chromium
```

This downloads the Chromium browser that Playwright uses.

### 3. Facebook Account (Optional)

While not strictly required, having a Facebook account logged into your browser can improve success rates:
- You'll see more groups (some require membership to view)
- Private groups may show their names instead of just "Facebook"

## Running Phase 5

### Simple Execution

```bash
python main.py --skip-to-phase 5
```

This automatically:
1. Loads unique group IDs from Phase 4
2. Launches a Chromium browser
3. Navigates to each group
4. Captures the real group name
5. Saves progress every 10 groups
6. Closes the browser

### Resume After Interruption

If Phase 5 is interrupted:

```bash
python main.py --skip-to-phase 5
```

The script will:
1. Load existing `group_names.json`
2. Skip already-captured groups
3. Continue with remaining groups
4. Save incrementally

### Run Directly

```bash
python phase5_navigate_groups.py --resume
```

## How It Works

### The Process

For each group ID:

1. **Navigate**: Visit `https://www.facebook.com/groups/{ID}`
2. **Wait**: Wait up to 10 seconds for page to load
3. **Capture**: Read the browser page title
4. **Extract**: Parse group name from title pattern:
   - `(5+) Group Name | Facebook` → `Group Name`
   - `(1+) Facebook` → `Grupo Privado` (private group)
5. **Save**: Update `group_names.json`

### Page Title Parsing

Facebook group page titles follow this pattern:

```
(N+) GROUP_NAME | Facebook
```

Where:
- `(N+)` = notification count (e.g., "(5)", "(1+)", "(0)")
- `GROUP_NAME` = actual group name
- `| Facebook` = constant suffix

**Examples**:
- `(5) Grupo de Imóveis Salvador | Facebook` → `Grupo de Imóveis Salvador`
- `(1+) Imóveis SP | Facebook` → `Imóveis SP`
- `(1+) Facebook` → `Grupo Privado` (no real name available)

### Performance

- **Speed**: ~2-3 seconds per group
- **Total time**: 258 groups ≈ 10-15 minutes
- **Batching**: Groups processed sequentially (not parallel)

**Why sequential?**
- Facebook rate-limits parallel requests
- More reliable and less likely to trigger blocking

## Output

### group_names.json

Example output:

```json
{
  "123456789": "Grupo de Imóveis Salvador",
  "987654321": "Imóveis São Paulo",
  "555555555": "Grupo Privado",
  "444444444": "Leilões Brasil"
}
```

### Logging

All activity logged to `leiloaria_grupos.log`:

```
[INFO] [1/258] Processing 123456789...
[INFO]   ✓ 123456789: Grupo de Imóveis Salvador
[INFO] Saving progress (10/258)...
[INFO] [258/258] Processing 444444444...
[INFO]   ✓ 444444444: Leilões Brasil
[INFO] Phase 5 complete!
```

## Troubleshooting

### Issue: "Playwright not installed"

**Solution**:
```bash
pip install playwright
playwright install chromium
```

### Issue: "Timeout waiting for group page"

**Causes**:
- Facebook is rate-limiting requests
- Internet connection is slow
- Group page takes too long to load

**Solutions**:
- Increase timeout in code (currently 10 seconds)
- Run during off-peak hours
- Check internet connection
- Resume from where it stopped

### Issue: Group names not captured (empty or just "Facebook")

These are **private groups**:
- User isn't a member
- Facebook hides the name from non-members
- Marked as `"Grupo Privado"` in output
- Team can manually join later if interested

### Issue: Browser window won't close

**Solution**:
- Manually close the browser window
- Script will exit after cleanup
- Playwright will release resources

### Issue: "Headless mode error"

If running on server without display:

Edit phase5_navigate_groups.py, change:
```python
browser = p.chromium.launch(headless=False)
```

To:
```python
browser = p.chromium.launch(headless=True)
```

This runs browser in headless mode (no visible window).

## Advanced Options

### Modify Timeout

In `phase5_navigate_groups.py`, line with `timeout=10000`:

```python
page.goto(url, wait_until="domcontentloaded", timeout=15000)  # 15 seconds
```

### Add Delays Between Groups

In `phase5_navigate_groups.py`:

```python
page.goto(url, wait_until="domcontentloaded", timeout=10000)
time.sleep(2)  # 2-second delay instead of 1
```

### Use Headless Mode

For server deployments without display:

```python
browser = p.chromium.launch(headless=True)  # No visible window
```

### Login to Facebook First

To access more groups (optional):

```python
page.goto("https://facebook.com")
# Login manually when browser appears
# Then continue with group navigation
```

## Performance Tips

1. **Run during off-peak**: Facebook is less congested at night
2. **Good internet**: Slower connections = longer timeouts needed
3. **Close other apps**: Free up system resources
4. **Be patient**: 10-15 minutes for 258 groups is reasonable

## After Phase 5

Once complete:

```bash
# Generate final Excel report
python main.py --skip-to-phase 6
```

This creates:
- `output/Leiloaria_Smart_Grupos_Facebook_COMPLETO.xlsx`

With two sheets:
1. **Grupos Facebook**: All groups with names, URLs, population
2. **Resumo por Busca**: Summary by city/search

## Comparison: Playwright vs Claude Cowork

| Aspect | Playwright (New) | Claude Cowork (Old) |
|--------|------------------|-------------------|
| Cost | Free (browser automation) | Expensive (Claude usage) |
| Time | 10-15 min (automated) | 60+ min (manual) |
| Data Safety | All saved to disk | Risk of context loss |
| Error Handling | Automatic retries | Manual intervention |
| Parallelization | Sequential (safe) | Limited parallelism |
| Headless Mode | Yes (servers) | Requires browser window |

## Automation is Complete

Phase 5 no longer requires Claude Cowork or manual intervention. It's fully automated and integrated with the pipeline.

Simply run:

```bash
python main.py
```

And let the pipeline complete automatically!

---

**Notes**:
- Playwright is cross-platform (Windows, Mac, Linux)
- Works in headless mode for server deployments
- Handles timeouts and errors gracefully
- Resumes automatically if interrupted
- No API keys or external services needed

**Questions?** See README.md or check leiloaria_grupos.log for detailed logs.

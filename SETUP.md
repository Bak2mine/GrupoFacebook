# Leiloaria Facebook Groups Automation - Setup Guide

## Prerequisites

Before running the pipeline, ensure you have:

1. **Python 3.8+** installed
2. **pip** (Python package manager)

## Installation Steps

### 1. Install Dependencies

Navigate to the `Grupo` directory and install required packages:

```bash
cd Grupo
pip install -r requirements.txt
```

### 2. Install Playwright Browsers

This is **REQUIRED** for the Facebook scraping to work:

```bash
playwright install
```

This command downloads the Chromium browser needed for web automation. It may take a few minutes.

### 3. Configure Paths (First Run Only)

If paths are hardcoded in `config.py`, update them to be relative:

```python
# ❌ DON'T USE (hardcoded):
LEILOARIA_DIR = Path(r"C:\Users\andre\Desktop\Leiloaria")

# ✅ DO USE (relative):
LEILOARIA_DIR = Path(__file__).parent.parent
GRUPO_DIR = LEILOARIA_DIR / "Grupo"
```

### 4. Verify Installation

Test that everything works:

```bash
python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
```

## Running the Pipeline

Once setup is complete:

```bash
cd Grupo
python main.py
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'playwright'"
→ Run `pip install -r requirements.txt`

### "Browser initialization failed" or "No such file or directory"
→ Run `playwright install`

### Permission Denied on paths
→ Update `config.py` to use relative paths instead of absolute paths

### "Facebook login required"
→ The script will open a browser window for you to log in manually
→ Log in to Facebook, then press Enter in the console

## File Structure

```
Leiloaria/
├── Grupo/
│   ├── config.py                              (Update paths here)
│   ├── requirements.txt                       (Dependencies)
│   ├── main.py                                (Main pipeline entry)
│   ├── phase1_extract_bairros.py
│   ├── phase2_scrape_properties.py
│   ├── phase3_with_cookies.py                (Needs Playwright)
│   ├── phase6_build_excel.py
│   ├── output/                                (Excel output)
│   └── data/                                  (JSON configs)
├── Post/
│   └── (Property scraping scripts)
└── SETUP.md                                   (This file)
```

## Quick Start

```bash
# 1. Install everything
pip install -r Grupo/requirements.txt
playwright install

# 2. Update config.py paths if needed
# (Use relative paths, not absolute)

# 3. Run the pipeline
cd Grupo
python main.py

# 4. If it asks to log in, do it manually in the browser
# then press Enter in the console
```

## Next Steps

After successful setup:
1. Run `python main.py` to start the pipeline
2. Check `output/Leiloaria_Smart_Grupos_Facebook_COMPLETO.xlsx` for results
3. All intermediate data is saved in `data/` directory as JSON files

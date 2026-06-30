# Building a Standalone .EXE for Leiloaria Smart

This .EXE is completely self-contained and will auto-install everything needed on first run.

## Prerequisites (For You, The Builder)

1. **Python 3.8+** installed
2. **PyInstaller** for packaging Python into .exe
3. All dependencies from `requirements.txt`

## Step 1: Install Build Tools

```bash
pip install pyinstaller
```

## Step 2: Build the .EXE

Navigate to the Leiloaria directory and run **one of these options:**

### Option 1: One-Click Build (Easiest)

```bash
build_exe.bat
```

### Option 2: Manual Build (Windows)

```bash
pyinstaller --name "Leiloaria Smart" ^
  --onefile ^
  --add-data "Grupo/data:data" ^
  --add-data "Post:Post" ^
  --hidden-import=openpyxl ^
  --hidden-import=playwright ^
  --hidden-import=bs4 ^
  --console ^
  bootstrap.py
```

### Option 3: Manual Build (Mac/Linux)

```bash
pyinstaller --name "Leiloaria Smart" \
  --onefile \
  --add-data "Grupo/data:data" \
  --add-data "Post:Post" \
  --hidden-import=openpyxl \
  --hidden-import=playwright \
  --hidden-import=bs4 \
  --console \
  bootstrap.py
```

This creates:
- `dist/Leiloaria Smart.exe` - The standalone executable
- `build/` - Build intermediate files (can be deleted)

## Step 3: Distribution

Create a zip file with:

```
leiloaria-smart.zip
├── Leiloaria Smart.exe          (from dist/)
└── COWORKER_INSTALL.md          (simple instructions)
```

## For Your Coworker

They need to:

1. **Extract the .zip** file to their machine
2. **Double-click `Leiloaria Smart.exe`**

**That's it!** The .exe will:
- Auto-download the browser engine on first run (~5 minutes)
- Handle all setup automatically
- Ask for Facebook login (one-time)
- Scrape groups and create Excel

## How It Works

The `.exe` includes a **bootstrap script** that automatically:
- Checks if Playwright browsers are installed
- Downloads them if needed (one-time on first run)
- Runs the main pipeline
- Handles all errors gracefully

Your coworker never sees or needs the terminal!

## File Structure

Everything works with **relative paths**, so the .exe can run anywhere:

```
any-folder/
├── Leiloaria Smart.exe    (the standalone app)
├── Grupo/
│   ├── data/              (configs)
│   ├── output/            (results go here)
│   └── ...
└── Post/
    └── ...
```

## System Requirements for Coworker

- **Windows 7+, Mac, or Linux**
- **No Python needed** (it's bundled in the .exe!)
- **Internet connection** (to access Facebook)
- **~500MB free disk** (for browser download on first run)

## Advanced: Customize the Build

To change the .exe behavior, edit `build_exe.bat`:

| Option | Purpose |
|--------|---------|
| `--onefile` | Single .exe (slower startup, easier to share) |
| `--onedir` | Multiple files (faster startup, needs folder) |
| `--icon=icon.ico` | Custom icon for the .exe |
| `--windowed` | Hide console window (remove `--console` to hide) |

Example with custom icon:

```bash
pyinstaller --name "Leiloaria Smart" ^
  --onefile ^
  --icon=my_icon.ico ^
  --add-data "Grupo/data:data" ^
  --add-data "Post:Post" ^
  --hidden-import=openpyxl ^
  --hidden-import=playwright ^
  --hidden-import=bs4 ^
  --console ^
  bootstrap.py
```

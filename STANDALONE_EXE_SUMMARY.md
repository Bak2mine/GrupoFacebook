# Standalone .EXE - Complete Solution

## What Changed

### Files Modified
- `Grupo/config.py` - All paths now relative
- `Post/config.py` - All paths now relative  
- `Post/diagnose_pptx.py` - All paths now relative

### Files Created
- `bootstrap.py` - Auto-installs Playwright browsers on first run
- `build_exe.bat` - One-click build script (Windows)
- `build_exe.ps1` - PowerShell build script
- `BUILD_EXE.md` - Complete build guide
- `COWORKER_INSTALL.md` - Ultra-simple install guide for end users

## How It Works

### For You (The Developer)

```bash
# Build the .exe (one time)
build_exe.bat

# Creates: dist/Leiloaria Smart.exe
```

### For Your Coworker

```
1. Extract the zip
2. Double-click "Leiloaria Smart.exe"
3. Wait for browser download (first run only, ~5 minutes)
4. Log in to Facebook (one time)
5. Results appear in Grupo/output/
```

That's literally it. **No Python, no pip, no terminal commands needed.**

## What bootstrap.py Does

When coworker runs the .exe:

1. **Check Playwright** - Are browsers already installed?
   - YES → Skip to step 3
   - NO → Continue to step 2

2. **Auto-Download Browsers** - ~300MB, one-time only
   - Shows progress to user
   - Takes ~5 minutes on first run
   - Cached for future runs

3. **Run Pipeline** - Same as normal
   - Scrapes Facebook groups
   - Creates Excel file
   - Saves cookies for next run

4. **Handle Errors** - If anything fails, show helpful message

## Build Checklist

- [x] All absolute paths converted to relative ✓
- [x] bootstrap.py created ✓
- [x] build_exe.bat updated ✓
- [x] build_exe.ps1 updated ✓
- [x] BUILD_EXE.md updated ✓
- [x] COWORKER_INSTALL.md simplified ✓

## To Build Right Now

```bash
cd C:\Users\andre\Desktop\Leiloaria
build_exe.bat
```

## Distribution Package

Zip these together:

```
leiloaria-smart.zip
├── Leiloaria Smart.exe
└── COWORKER_INSTALL.md
```

Share with coworker. They extract and run. Done.

## System Requirements (Coworker)

- Windows 7+ (or Mac/Linux)
- **NO Python needed** (bundled in .exe)
- Internet connection
- ~500MB free disk

## Result

Your coworker gets a **completely standalone application** that:
- Requires zero setup knowledge
- Auto-installs browser engine if needed
- Works offline after first run
- Saves cookies for automatic Facebook login next time

# Leiloaria Smart - Installation Guide for Coworkers

## Quickest Start Ever (Literally Just 2 Steps)

### 1. Extract the Zip
Extract `leiloaria-smart.zip` to any folder on your computer.

### 2. Double-Click the .exe
- Open the folder you extracted
- Double-click **`Leiloaria Smart.exe`**
- **That's it!** The program will handle everything automatically

### First Run

The first run will:
1. Download the browser engine (~5 minutes, one-time setup)
2. Ask you to **log in to Facebook** (one-time setup)
   - A browser window opens
   - Log in normally
   - Press Enter when done
   - Your session is saved permanently
3. Scrape Facebook groups automatically
4. Create an Excel file with results

**After first run, you're done!** Every future run is completely automatic - no login, no setup, no nothing. Just double-click and wait.

## Where's My Results?

After the program finishes, find your Excel file:
```
[Your extracted folder]\Grupo\output\Leiloaria_Smart_Grupos_Facebook_COMPLETO.xlsx
```

Double-click to open and see all the scraped Facebook groups!

## Next Runs

From now on, every run is **fully automatic**:
1. Double-click the .exe
2. Wait for results
3. Done!

No login, no setup, no manual steps needed.

## Troubleshooting

### "playwright install" command not found
**Solution:** Make sure Python is installed and in your PATH
```bash
# Verify Python is installed
python --version

# If it shows a version (3.8+), then try:
python -m pip install --upgrade playwright
playwright install
```

### "File not found" or "Permission denied"
**Solution:** Make sure the .exe is in the same folder as `Grupo/` and `Post/`

**Correct structure:**
```
your-folder/
├── Leiloaria Smart.exe
├── Grupo/
│   ├── data/
│   ├── output/
│   └── ...
└── Post/
    └── ...
```

### Browser won't open / "Browser initialization failed"
**Solution:** Make sure you ran `playwright install` (see step 2 above)

### "Module not found" errors
**Solution:** The .exe includes all Python dependencies. This error shouldn't happen, but if it does:
1. Delete the `.exe`
2. Run `playwright install` again
3. Re-download the .exe

### Script runs but finds no groups
**Solution:** Check your search configurations in `Grupo/data/search_configuration_bairro.json`

## Advanced: Uninstall

To remove everything:
1. Delete the entire folder
2. Optionally remove Playwright browsers:
   ```bash
   playwright uninstall
   ```

## Support

If you encounter issues:
1. Check the console output for error messages
2. Make sure you have Python 3.8+ installed
3. Verify `playwright install` completed successfully
4. Check your internet connection (for Facebook access)

## What Gets Downloaded/Installed

- **Playwright browsers:** ~300MB (downloaded to `%APPDATA%\Local\ms-playwright`)
- **No data** is sent anywhere except Facebook.com
- **Cookies** are saved locally in `facebook_cookies.json`

## System Requirements

- **Windows 7+, Mac, or Linux**
- **Python 3.8+** (must be installed separately)
- **Internet connection** (to access Facebook)
- **~500MB free disk space** (for Playwright browsers)

---

**Questions?** Contact your team lead or the developer who provided this.

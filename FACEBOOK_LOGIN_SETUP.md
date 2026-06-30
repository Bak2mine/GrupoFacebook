# Facebook Login Setup - One-Time Configuration

## Overview

There are **three ways** to provide Facebook credentials:

1. **Zero-Login Method** (Best) - Bake cookies into `config.py`
2. **Cookies File Method** - Save to `facebook_cookies.json`
3. **Manual Login** (Worst) - Log in every time

## Method 1: Zero-Login Setup (Recommended)

This is what you want! Run the login script **once**, and your session is permanently saved in `config.py`. No login ever needed again.

### For You (Developer) - First Time Setup

```bash
cd Grupo
python login_once.py
```

This will:
1. Open a browser window
2. Ask you to log in to Facebook
3. Press Enter when done
4. Your session is saved to `config.py` automatically

### Result

Your `config.py` will now have something like:

```python
FACEBOOK_COOKIES = [
    {
        "name": "c_user",
        "value": "123456789",
        "domain": ".facebook.com",
        ...
    },
    {
        "name": "xs",
        "value": "abc123...",
        "domain": ".facebook.com",
        ...
    },
    # ... more cookies
]
```

### For Your Coworker

They get the `.exe` which includes your `config.py` with cookies already embedded. **They never need to log in.**

The `.exe` will run completely automated:
1. Extract and double-click
2. Browser downloads (first run only)
3. Scrapes Facebook automatically
4. Done!

## Method 2: Cookies File Setup (Fallback)

If you don't want to check in cookies to `config.py`, they can be saved separately:

```python
FACEBOOK_COOKIES = []  # Leave empty
```

Then use `facebook_cookies.json` instead:

```bash
cd Grupo
python login_once.py
```

It will create/update `facebook_cookies.json` with your session.

**For distribution:** Include `facebook_cookies.json` in the zip with the `.exe`.

## Method 3: Manual Login (No Setup)

Leave both empty:
- `FACEBOOK_COOKIES = []` in config.py
- No `facebook_cookies.json` file

Every run will ask the user to log in:
- A browser opens
- User logs in
- Cookies are saved
- Pipeline runs

This works but requires manual login each time.

---

## Step-by-Step: Full Setup Process

### You (Developer):

1. **Log in once:**
   ```bash
   cd C:\Users\andre\Desktop\Leiloaria\Grupo
   python login_once.py
   ```

2. **Follow the prompts:**
   - Browser opens
   - Log in to Facebook
   - Press Enter in terminal when done

3. **Verify `config.py` updated:**
   ```bash
   cat config.py | grep FACEBOOK_COOKIES
   ```
   Should show a long list of cookie data (not empty `[]`)

4. **Build the .exe:**
   ```bash
   cd C:\Users\andre\Desktop\Leiloaria
   build_exe.bat
   ```

5. **Distribute:**
   - Share `dist/Leiloaria Smart.exe`
   - Coworker extracts and runs it
   - Zero login needed!

### Your Coworker:

1. Extract the zip
2. Double-click `Leiloaria Smart.exe`
3. Waits for browser download (5 min first run only)
4. Pipeline runs automatically
5. Gets Excel results

**No login, no setup knowledge needed.**

---

## Security Considerations

### If You Trust Your Coworker

Bake cookies into `config.py` - they get full automatic access. Fastest and best UX.

### If You Don't Trust Them

Use `facebook_cookies.json` separately. Don't include it in the zip. They still need to log in first.

### If You Need Revocation

Facebook cookies expire over time (usually days/weeks). To invalidate:
1. Log out of Facebook on your phone/browser
2. Cookies become invalid
3. Next run will ask to log in again

---

## Troubleshooting

### "Could not find FACEBOOK_COOKIES in config.py"

Make sure `config.py` has this line:
```python
FACEBOOK_COOKIES = []  # Auto-populated by login_once.py
```

### Browser doesn't open

Make sure Playwright is installed:
```bash
pip install playwright
playwright install
```

### Login doesn't save

After logging in, before pressing Enter:
- Wait 3-5 seconds for Facebook to fully load
- Check that you're logged in (see your name in top right)
- Then press Enter

### Cookies expired

Just run `login_once.py` again to refresh:
```bash
python login_once.py
```

---

## Which Method Should I Use?

| Scenario | Method | Why |
|----------|--------|-----|
| Solo developer | Zero-Login | No setup needed, works offline |
| Trusted team | Zero-Login | Simplest distribution, best UX |
| Untrusted user | Cookies File | They log in first time, then auto-login |
| One-time use | Manual | Don't need to save anything |

**Recommendation:** Use **Zero-Login Method** - it's the best experience for everyone.

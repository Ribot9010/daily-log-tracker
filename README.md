# Daily Log Tracker

A personal habit-survey app. One tap on the Pixel home screen, fill in carbs / exercise / sleep / alcohol for the day, and an all-day event lands on Google Calendar. A small Python script later turns the calendar into stats.

Built 2026-05-03 as my first end-to-end project with Claude Code. Documents everything we put in place and the things we deliberately did not.

## Live

- **App:** https://ribot9010.github.io/daily-log-tracker/ (also installed as a PWA on Pixel 7)
- **Repo:** https://github.com/Ribot9010/daily-log-tracker
- **Data:** all-day events on my primary Google Calendar, titled `Daily log — ...`

## Architecture

```
[ Pixel / desktop browser ]
    index.html  ── form ──►  Apps Script web app  ──►  Google Calendar
   (GitHub Pages)              (Google account)         (default calendar)
                                                              │
                                                              ▼
                                                     analytics.py + Cowork
```

- **Frontend** is a single static HTML file with a service worker (real installable PWA), hosted on GitHub Pages.
- **Backend** is a Google Apps Script web app — no server to run, no database to host. `doPost` writes events; `doGet?action=list` reads them back as JSON.
- **Storage** is Google Calendar itself. Already syncs to every device, already readable by Cowork's calendar connector, already free.
- **Analytics** is a local Python script that fetches the JSON, parses event descriptions into a pandas DataFrame, and prints a summary.

## What's in this folder

| File | Purpose |
|------|---------|
| `index.html` | The form (date + carbs + exercise + sleep + alcohol). |
| `app.js` | Submit handler, registers the service worker. |
| `config.js` | Holds the Apps Script web app URL. |
| `manifest.json` | PWA manifest — name, icons, theme. |
| `sw.js` | Service worker — caches the app shell, makes the page installable. |
| `icon-192.png`, `icon-512.png` | App icons. Regenerate with `generate_icons.py`. |
| `generate_icons.py` | Pillow script that produces the two PNG icons. |
| `apps-script.gs` | Google Apps Script backend (paste into script.google.com). |
| `analytics.py` | Reads events, prints summary stats. |
| `run_analytics.bat` | Double-click to run analytics on Windows. |
| `seed_test_data.py` | One-shot helper that POSTs 10 plausible test entries. |

## How to use

**Log a day.** Tap the Daily Log icon on the Pixel home screen (or open the live URL in any browser). Pick the options. Tap *Save to calendar*. Re-submitting the same date overwrites — no duplicates.

**See your stats.** Double-click `run_analytics.bat`. The console shows tracking range, calendar days vs. logged days vs. missed days, then category stats over the logged days only.

**Get a CSV.** `python analytics.py --csv` writes `daily_log.csv` next to the script. (Gitignored — your real log data never gets pushed.)

## How to extend

**Add a new survey category.** Four files change in lockstep:

1. `index.html` — add a fieldset with the new input.
2. `app.js` — read the new field into the POST payload.
3. `apps-script.gs` — include it in `formatTitle` and `formatDescription`.
4. `analytics.py` — parse it from the description and add a stat to `summarise()`.

Then push to GitHub, **redeploy the Apps Script** (Manage deployments → edit current → "New version" → Deploy — keeps the same URL), and reload the form.

## Status

Working end-to-end as of 2026-05-03:

- [x] Form on phone + desktop
- [x] Google Calendar storage with overwrite-on-resubmit
- [x] Real PWA install on Pixel 7
- [x] Apps Script JSON read endpoint
- [x] Python analytics with carbs / exercise / sleep / alcohol
- [x] Missed-days metric (calendar window vs. logged days)
- [x] One-click analytics via `.bat` shortcut

## Deferred

Things we discussed but chose not to build yet:

- **Shared-secret token on the Apps Script URL.** The URL is in `config.js`, which is in a public repo. Worst case: someone could spam-create "Daily log" events on my calendar. ~5 min of work to add `data.token` check in `doPost`.
- **Calendar-true streaks.** `current_streak` in `analytics.py` walks logged rows, not calendar dates, so a missed day doesn't break the streak. Cosmetic until I see it lying to me.
- **Charts.** Adding matplotlib trend lines is premature with little data. Revisit after a few weeks of real entries.
- **`beforeinstallprompt` install button.** Not needed; "Add to Home screen" already triggers a full PWA install on engagement-eligible Android Chrome.

## Gotchas worth remembering

- **Apps Script redeploys:** always use *Manage deployments → edit → New version*. *New deployment* gives you a different URL and breaks `config.js`.
- **Windows console encoding:** Python 3.14 stdout defaults to cp1252 on Windows; `analytics.py` reconfigures to utf-8 so the em-dash and arrow render. Don't remove that block.
- **Google Calendar UI sync lag:** events created via API can take a minute or two to appear in the UI. If something looks "missing" right after a backfill, it usually shows up shortly.
- **Android Chrome install prompt:** "Install app" only surfaces after Chrome decides you're engaged. "Add to Home screen" performs the same real PWA install in the meantime.

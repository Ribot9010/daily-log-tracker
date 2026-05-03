"""Seed 10 days of plausible-looking test entries via the live POST endpoint.

Idempotent: re-running will UPDATE existing events for those dates rather than
duplicate, because the Apps Script overwrites events whose title starts with
'Daily log' on the same day.

Cleanup: open Google Calendar, navigate to April 23 - May 2 2026, click each
all-day "Daily log" event, hit the trash icon. Or keep them — they're real
data points if you actually want to remember those days.
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

import requests

HERE = Path(__file__).parent
match = re.search(
    r'window\.APPS_SCRIPT_URL\s*=\s*"([^"]+)"',
    (HERE / "config.js").read_text(encoding="utf-8"),
)
if not match:
    print("Could not find APPS_SCRIPT_URL in config.js", file=sys.stderr)
    sys.exit(1)
URL = match.group(1)


# 10 days of made-up but realistic-looking entries.
# Mix: leans low-carb, cardio appears most days, sleep is hit-or-miss.
SEED = [
    {"date": "2026-04-23", "carbs": "medium", "exercise": ["Cardio"],                              "sleep": True},
    {"date": "2026-04-24", "carbs": "low",    "exercise": ["Resistance"],                         "sleep": True},
    {"date": "2026-04-25", "carbs": "high",   "exercise": [],                                     "sleep": False},
    {"date": "2026-04-26", "carbs": "low",    "exercise": ["Animal Moves", "Cardio"],             "sleep": True},
    {"date": "2026-04-27", "carbs": "medium", "exercise": ["Cardio", "Resistance"],               "sleep": False},
    {"date": "2026-04-28", "carbs": "low",    "exercise": ["Cardio"],                             "sleep": True},
    {"date": "2026-04-29", "carbs": "low",    "exercise": ["Animal Moves"],                       "sleep": True},
    {"date": "2026-04-30", "carbs": "medium", "exercise": [],                                     "sleep": True},
    {"date": "2026-05-01", "carbs": "high",   "exercise": ["Cardio", "Resistance"],               "sleep": False},
    {"date": "2026-05-02", "carbs": "low",    "exercise": ["Cardio", "Animal Moves", "Resistance"], "sleep": True},
]


def main() -> None:
    print(f"Seeding {len(SEED)} entries to {URL[:60]}...")
    for i, entry in enumerate(SEED, start=1):
        resp = requests.post(URL, data=json.dumps(entry), timeout=30)
        result = resp.json()
        status = result.get("action", "error")
        print(f"  [{i:2d}/{len(SEED)}] {entry['date']}  -> {status}")
        time.sleep(0.3)  # be polite to Apps Script
    print("Done. Now run: python analytics.py")


if __name__ == "__main__":
    main()

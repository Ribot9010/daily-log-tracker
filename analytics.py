"""Pull Daily Log entries from Google Calendar (via Apps Script) and summarise.

Usage:
    python analytics.py            # print summary to stdout
    python analytics.py --csv      # also dump full DataFrame to daily_log.csv
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import pandas as pd
import requests

# Windows consoles default to cp1252 which can't render em-dashes / arrows.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, OSError):
    pass


HERE = Path(__file__).parent
APPS_SCRIPT_URL = (HERE / "config.js").read_text(encoding="utf-8")
match = re.search(r'window\.APPS_SCRIPT_URL\s*=\s*"([^"]+)"', APPS_SCRIPT_URL)
if not match:
    print("Could not find APPS_SCRIPT_URL in config.js — set it first.", file=sys.stderr)
    sys.exit(1)
URL = match.group(1)


EXERCISE_TYPES = ["Animal Moves", "Cardio", "Resistance"]


def fetch_events() -> list[dict]:
    """Hit the Apps Script ?action=list endpoint and return the raw event list."""
    resp = requests.get(URL, params={"action": "list"}, timeout=30)
    resp.raise_for_status()
    payload = resp.json()
    if not payload.get("ok"):
        raise RuntimeError(f"Server returned error: {payload}")
    return payload["events"]


def parse_description(desc: str) -> dict:
    """Extract structured fields from the event description string."""
    out = {"carbs": None, "exercise": [], "sleep": False, "alcohol": False}
    for line in desc.splitlines():
        if line.startswith("Carbs:"):
            out["carbs"] = line.split(":", 1)[1].strip().lower()
        elif line.startswith("Exercise:"):
            value = line.split(":", 1)[1].strip()
            if value and value.lower() != "none":
                out["exercise"] = [x.strip() for x in value.split(",")]
        elif line.startswith("Sleep"):
            out["sleep"] = line.rstrip().endswith("Y")
        elif line.startswith("Alcohol"):
            out["alcohol"] = line.rstrip().endswith("Y")
    return out


def build_dataframe(events: list[dict]) -> pd.DataFrame:
    rows = []
    for ev in events:
        parsed = parse_description(ev["description"])
        row = {
            "date": pd.to_datetime(ev["date"]),
            "carbs": parsed["carbs"],
            "sleep_ok": parsed["sleep"],
            "alcohol": parsed["alcohol"],
        }
        for ex in EXERCISE_TYPES:
            row[ex] = ex in parsed["exercise"]
        rows.append(row)
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    return df.sort_values("date").reset_index(drop=True)


def summarise(df: pd.DataFrame) -> None:
    if df.empty:
        print("No Daily log entries found yet.")
        return

    n = len(df)
    print(f"Daily Log summary — {n} day{'s' if n != 1 else ''} logged")
    print(f"  range: {df['date'].min().date()} → {df['date'].max().date()}")
    print()

    print("Carbs distribution:")
    carb_counts = df["carbs"].value_counts(dropna=False)
    for level, count in carb_counts.items():
        print(f"  {level or 'unset':<8} {count:3d}  ({count / n:.0%})")
    print()

    print("Exercise frequency:")
    for ex in EXERCISE_TYPES:
        count = int(df[ex].sum())
        print(f"  {ex:<14} {count:3d}  ({count / n:.0%})")
    any_ex = (df[EXERCISE_TYPES].any(axis=1)).sum()
    print(f"  {'(any)':<14} {any_ex:3d}  ({any_ex / n:.0%})")
    print()

    sleep_count = int(df["sleep_ok"].sum())
    print(f"Sleep 7.5h+: {sleep_count}/{n}  ({sleep_count / n:.0%})")
    print(f"Current sleep streak: {current_streak(df['sleep_ok'])} days")
    print()

    alcohol_count = int(df["alcohol"].sum())
    print(f"Alcohol days: {alcohol_count}/{n}  ({alcohol_count / n:.0%})")
    print(f"Current dry streak: {current_streak(~df['alcohol'])} days")


def current_streak(series: pd.Series) -> int:
    """How many consecutive trailing True values are at the end."""
    count = 0
    for v in reversed(series.tolist()):
        if v:
            count += 1
        else:
            break
    return count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", action="store_true", help="Also write daily_log.csv")
    args = parser.parse_args()

    events = fetch_events()
    df = build_dataframe(events)
    summarise(df)

    if args.csv and not df.empty:
        out = HERE / "daily_log.csv"
        df.to_csv(out, index=False)
        print(f"\nWrote {out}")


if __name__ == "__main__":
    main()

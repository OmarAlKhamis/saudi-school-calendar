"""Sanity-check the data files. Exits non-zero on any problem (runs in CI before deploy)."""

from __future__ import annotations

import datetime as dt
import sys
from collections import Counter

from calendar_data import REGIONS, TYPES, load

SUNDAY = 6


def check() -> list[str]:
    years, events = load()
    errors: list[str] = []

    for y in years:
        if y.path.stem != str(y.year):
            errors.append(f"{y.path.name}: file name must match year = {y.year}")
    nums = sorted(y.year for y in years)
    for a, b in zip(nums, nums[1:]):
        if b != a + 1:
            errors.append(f"gap between {a} and {b}: add data/{a + 1}.toml")

    for eid, n in Counter(e.id for e in events).items():
        if n > 1:
            errors.append(f"{eid}: duplicate id")

    for e in events:
        where = f"{e.id}"
        if not e.id.startswith(f"{e.year}-"):
            errors.append(f"{where}: id must start with '{e.year}-'")
        if e.type not in TYPES:
            errors.append(f"{where}: unknown type '{e.type}'")
        if not isinstance(e.start, dt.date) or not isinstance(e.end, dt.date):
            errors.append(f"{where}: start/end must be bare dates (YYYY-MM-DD)")
            continue
        if e.end < e.start:
            errors.append(f"{where}: end {e.end} is before start {e.start}")
        if not e.regions or any(r not in REGIONS for r in e.regions):
            errors.append(f"{where}: regions must be a non-empty subset of {sorted(REGIONS)}")
        if not e.source.startswith("https://"):
            errors.append(f"{where}: source must be an https URL or a key in [sources]")
        if not e.title_ar.strip() or not e.title_en.strip():
            errors.append(f"{where}: both title_ar and title_en are required")
        if e.type in ("first-day", "semester-start") and e.start.weekday() != SUNDAY:
            errors.append(f"{where}: {e.type} {e.start} is a {e.start:%A}, expected Sunday")

    # Within one region, breaks must not overlap each other.
    breaks = [e for e in events if e.type not in ("staff-return", "first-day", "semester-start", "last-day")]
    for region in REGIONS:
        rb = sorted((e for e in breaks if region in e.regions), key=lambda e: e.start)
        for a, b in zip(rb, rb[1:]):
            if b.start <= a.end:
                errors.append(f"{a.id} and {b.id} overlap in region '{region}'")

    return errors


if __name__ == "__main__":
    problems = check()
    for p in problems:
        print(f"ERROR: {p}")
    if problems:
        sys.exit(1)
    years, events = load()
    print(f"OK: {len(years)} years, {len(events)} events")

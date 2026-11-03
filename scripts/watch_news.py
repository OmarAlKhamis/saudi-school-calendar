"""Watch MoE and SPA news for a new school-calendar announcement and open a GitHub issue.

It only alerts. A person adds the dates (with sources) and merges.

    python scripts/watch_news.py --dry-run     # print what it would open
    GH_TOKEN=... GITHUB_REPOSITORY=owner/repo python scripts/watch_news.py
"""

from __future__ import annotations

import argparse
import datetime as dt
import email.utils
import json
import os
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

from calendar_data import load

QUERIES = [
    'التقويم الدراسي site:moe.gov.sa',
    'التقويم الدراسي site:spa.gov.sa',
    '"وزارة التعليم" "التقويم الدراسي" العام الدراسي',
]
LOOKBACK_DAYS = 14
YEAR_RE = re.compile(r"14[4-9]\d")
# "1448-1449" / "1448/1449" names the 1448 school year; keep only the first number.
RANGE_RE = re.compile(r"(14[4-9]\d)\s*[-/–]\s*14[4-9]\d")
UA = {"User-Agent": "saudi-school-calendar-watcher (+https://github.com/OmarAlKhamis/saudi-school-calendar)"}


def news(query: str) -> list[dict]:
    url = "https://news.google.com/rss/search?" + urllib.parse.urlencode(
        {"q": query, "hl": "ar", "gl": "SA", "ceid": "SA:ar"})
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        root = ET.fromstring(r.read())
    items = []
    for it in root.iter("item"):
        pub = it.findtext("pubDate")
        items.append({
            "title": it.findtext("title", ""),
            "link": it.findtext("link", ""),
            "date": email.utils.parsedate_to_datetime(pub) if pub else None,
        })
    return items


def pending_years() -> set[int]:
    """Years we would still want news about: incomplete ones, and the two after the last."""
    years, _ = load()
    last = max(y.year for y in years)
    return {y.year for y in years if not y.complete} | {last + 1, last + 2}


def gh(method: str, path: str, body: dict | None = None):
    req = urllib.request.Request(
        f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}{path}",
        method=method,
        data=json.dumps(body).encode() if body else None,
        headers={"Authorization": f"Bearer {os.environ['GH_TOKEN']}",
                 "Accept": "application/vnd.github+json", **UA},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read() or "null")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--lookback", type=int, default=LOOKBACK_DAYS, help="days of news to consider")
    args = ap.parse_args()

    wanted = pending_years()
    since = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=args.lookback)
    hits: dict[int, dict[str, dict]] = {}
    for q in QUERIES:
        try:
            items = news(q)
        except Exception as exc:  # a news outage shouldn't fail the job and email the owner
            print(f"WARNING: could not read news for {q!r}: {exc}")
            continue
        for item in items:
            if item["date"] and item["date"] < since:
                continue
            if "تقويم" not in item["title"]:
                continue
            years = {int(m) for m in YEAR_RE.findall(RANGE_RE.sub(r"\1", item["title"]))}
            for y in years & wanted:
                hits.setdefault(y, {})[item["link"]] = item

    if not hits:
        print(f"No calendar news in the last {args.lookback} days for years {sorted(wanted)}.")
        return 0

    for year, items in sorted(hits.items()):
        title = f"New school-calendar news for {year}هـ"
        body = ("Possible new MoE calendar announcement. Check the official source, then add or update "
                f"`data/{year}.toml` (every event needs a `source`).\n\n"
                + "\n".join(f"- [{i['title']}]({i['link']}) ({i['date']:%Y-%m-%d})" for i in items.values()))
        if args.dry_run:
            print(f"WOULD OPEN: {title}\n{body}\n")
            continue
        existing = gh("GET", "/issues?state=open&labels=calendar-news&per_page=100") or []
        if any(i["title"] == title for i in existing):
            print(f"Issue already open: {title}")
            continue
        gh("POST", "/issues", {"title": title, "body": body, "labels": ["calendar-news"]})
        print(f"Opened: {title}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

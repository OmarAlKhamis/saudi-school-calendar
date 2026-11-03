"""Build the subscribable .ics feeds and the landing page into site/.

    python scripts/build.py                 # uses the default GitHub Pages URL
    SITE_URL=https://example.org python scripts/build.py
"""

from __future__ import annotations

import datetime as dt
import html
import json
import os
import shutil
from pathlib import Path
from urllib.parse import quote

from calendar_data import REGIONS, ROOT, Event, load

SITE_URL = os.environ.get("SITE_URL", "https://omaralkhamis.github.io/saudi-school-calendar").rstrip("/")
REPO_URL = os.environ.get("REPO_URL", "https://github.com/OmarAlKhamis/saudi-school-calendar")
OUT = ROOT / "site"
LANGS = ("ar", "en")
# Fixed stamp keeps builds byte-identical; calendars track changes by UID + content.
DTSTAMP = "20260101T000000Z"


def feed_name(region: str, lang: str) -> str:
    return f"{region}-{lang}.ics"


# --- iCalendar -------------------------------------------------------------------------

def esc(text: str) -> str:
    return (text.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,")
            .replace("\r\n", "\\n").replace("\n", "\\n"))


def fold(line: str) -> str:
    """Fold to 75 octets per RFC 5545 without splitting a UTF-8 character."""
    out, cur, size = [], "", 0
    for ch in line:
        n = len(ch.encode("utf-8"))
        if size + n > 75:
            out.append(cur)
            cur, size = " ", 1
        cur += ch
        size += n
    out.append(cur)
    return "\r\n".join(out)


def ics(region: str, lang: str, events: list[Event]) -> str:
    meta = REGIONS[region]
    name = meta[lang]
    scope = meta[f"{lang}_scope"]
    desc = (f"تواريخ التقويم الدراسي الرسمي لوزارة التعليم ({scope}). يتحدث تلقائيًا كل عام. {REPO_URL}"
            if lang == "ar" else
            f"Official Saudi MoE school calendar ({scope}). Updates itself every year. {REPO_URL}")
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        f"PRODID:-//saudi-school-calendar//{region}-{lang}//{lang.upper()}",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"NAME:{esc(name)}",
        f"X-WR-CALNAME:{esc(name)}",
        f"X-WR-CALDESC:{esc(desc)}",
        "X-WR-TIMEZONE:Asia/Riyadh",
        "REFRESH-INTERVAL;VALUE=DURATION:P1D",
        "X-PUBLISHED-TTL:P1D",
    ]
    for e in events:
        if region not in e.regions:
            continue
        title = e.title_ar if lang == "ar" else e.title_en
        note = (f"{scope}\nالمصدر: {e.source}" if lang == "ar" else f"{scope}\nSource: {e.source}")
        lines += [
            "BEGIN:VEVENT",
            f"UID:{e.id}-{region}-{lang}@saudi-school-calendar",
            f"DTSTAMP:{DTSTAMP}",
            f"DTSTART;VALUE=DATE:{e.start:%Y%m%d}",
            f"DTEND;VALUE=DATE:{e.end + dt.timedelta(days=1):%Y%m%d}",
            f"SUMMARY:{esc(title)}",
            f"DESCRIPTION:{esc(note)}",
            f"CATEGORIES:{e.type.upper()}",
            "TRANSP:TRANSPARENT",
            "END:VEVENT",
        ]
    lines.append("END:VCALENDAR")
    return "\r\n".join(fold(l) for l in lines) + "\r\n"


# --- Landing page ----------------------------------------------------------------------

def links(region: str, lang: str) -> dict[str, str]:
    https_url = f"{SITE_URL}/{feed_name(region, lang)}"
    webcal = "webcal://" + https_url.split("://", 1)[1]
    return {
        "google": "https://calendar.google.com/calendar/render?cid=" + quote(webcal, safe=""),
        "apple": webcal,
        "outlook": "https://outlook.live.com/calendar/0/addfromweb?url=" + quote(https_url, safe="")
                   + "&name=" + quote(REGIONS[region][lang], safe=""),
        "m365": "https://outlook.office.com/calendar/0/addfromweb?url=" + quote(https_url, safe="")
                + "&name=" + quote(REGIONS[region][lang], safe=""),
        "ics": https_url,
    }


def card(region: str, lang: str) -> str:
    l = {k: html.escape(v) for k, v in links(region, lang).items()}
    label = "عربي" if lang == "ar" else "English"
    return f"""
      <div class="feed" data-region="{region}">
        <div class="feed-head"><span class="lang">{label}</span></div>
        <div class="buttons">
          <a class="btn primary" href="{l['google']}" target="_blank" rel="noopener">Google</a>
          <a class="btn" href="{l['apple']}">Apple / iPhone</a>
          <a class="btn" href="{l['outlook']}" target="_blank" rel="noopener">Outlook.com</a>
          <a class="btn" href="{l['m365']}" target="_blank" rel="noopener">Microsoft 365</a>
        </div>
        <div class="copy">
          <input readonly value="{l['ics']}" aria-label="iCal URL">
          <button type="button" data-copy="{l['ics']}">نسخ · Copy</button>
        </div>
      </div>"""


def page(events: list[Event]) -> str:
    data = [
        {"s": e.start.isoformat(), "e": e.end.isoformat(), "ar": e.title_ar, "en": e.title_en,
         "r": list(e.regions), "t": e.type}
        for e in events
    ]
    sections = "".join(f"""
    <section class="region">
      <h2>{html.escape(REGIONS[r]['label_ar'])} <small>{html.escape(REGIONS[r]['label_en'])}</small></h2>
      <p class="scope">{html.escape(REGIONS[r]['ar_scope'])}</p>
      <div class="feeds">{card(r, 'ar')}{card(r, 'en')}</div>
    </section>""" for r in REGIONS)
    template = (ROOT / "scripts" / "page.html").read_text(encoding="utf-8")
    return (template
            .replace("{{SECTIONS}}", sections)
            .replace("{{EVENTS_JSON}}", json.dumps(data, ensure_ascii=False))
            .replace("{{REPO_URL}}", html.escape(REPO_URL)))


def main() -> None:
    _, events = load()
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    for region in REGIONS:
        for lang in LANGS:
            (OUT / feed_name(region, lang)).write_bytes(ics(region, lang, events).encode("utf-8"))
    (OUT / "index.html").write_text(page(events), encoding="utf-8")
    (OUT / ".nojekyll").write_text("")
    print(f"Built {len(REGIONS) * len(LANGS)} feeds + index.html into {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()

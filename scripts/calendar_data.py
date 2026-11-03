"""Load the academic-year files in data/ into a flat list of events."""

from __future__ import annotations

import datetime as dt
import tomllib
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"

REGIONS = {
    "main": {
        "ar": "التقويم الدراسي السعودي",
        "en": "Saudi School Calendar",
        "label_ar": "معظم مناطق المملكة",
        "label_en": "Most of the Kingdom",
        "ar_scope": "جميع المناطق عدا مكة المكرمة والمدينة المنورة وجدة والطائف",
        "en_scope": "All regions except Makkah, Madinah, Jeddah and Taif",
    },
    "west": {
        "ar": "التقويم الدراسي السعودي — مكة والمدينة وجدة والطائف",
        "en": "Saudi School Calendar — Makkah, Madinah, Jeddah & Taif",
        "label_ar": "مكة المكرمة والمدينة المنورة وجدة والطائف",
        "label_en": "Makkah, Madinah, Jeddah & Taif",
        "ar_scope": "مكة المكرمة والمدينة المنورة وجدة والطائف",
        "en_scope": "Makkah, Madinah, Jeddah and Taif",
    },
}

TYPES = {
    "staff-return", "first-day", "semester-start", "last-day", "summer", "break",
    "national-day", "founding-day", "eid", "long-weekend", "exams",
}


@dataclass(frozen=True)
class Event:
    id: str
    year: int
    type: str
    start: dt.date
    end: dt.date  # inclusive
    title_ar: str
    title_en: str
    regions: tuple[str, ...]
    source: str  # resolved URL


@dataclass(frozen=True)
class Year:
    year: int
    gregorian: str
    complete: bool
    path: Path


def load() -> tuple[list[Year], list[Event]]:
    years: list[Year] = []
    events: list[Event] = []
    for path in sorted(DATA_DIR.glob("*.toml")):
        with path.open("rb") as f:
            doc = tomllib.load(f)
        sources = doc.get("sources", {})
        years.append(Year(doc["year"], doc["gregorian"], doc.get("complete", False), path))
        for raw in doc.get("events", []):
            src = raw.get("source", "")
            events.append(Event(
                id=raw["id"],
                year=doc["year"],
                type=raw["type"],
                start=raw["start"],
                end=raw.get("end", raw["start"]),
                title_ar=raw["title_ar"],
                title_en=raw["title_en"],
                regions=tuple(raw["regions"]),
                source=sources.get(src, src),
            ))
    events.sort(key=lambda e: (e.start, e.id))
    return years, events

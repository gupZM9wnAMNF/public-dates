#!/usr/bin/env python3
"""Genera una pagina statica per ogni evento in events.json.

Uso:  python3 build.py
Output: <eventId>/index.html  (accanto a build.py)
Solo libreria standard, nessuna dipendenza.
"""
import datetime
import html
import json
from pathlib import Path

ROOT = Path(__file__).parent
GIORNI = ["lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato", "domenica"]
MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio",
        "agosto", "settembre", "ottobre", "novembre", "dicembre"]


def date_human(iso: str) -> str:
    d = datetime.date.fromisoformat(iso)
    return f"{GIORNI[d.weekday()]} {d.day} {MESI[d.month - 1]} {d.year}"


def map_url(ev: dict) -> str:
    c = ev.get("locationCoordinates")
    if c:
        return f"https://www.google.com/maps/search/?api=1&query={c['lat']},{c['lng']}"
    from urllib.parse import quote
    return f"https://www.google.com/maps/search/?api=1&query={quote(ev['location'])}"


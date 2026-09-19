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

def guests_html(guests: list) -> str:
    if not guests:
        return ""
    tags = "".join(f'<span class="guest-tag">{html.escape(g)}</span>' for g in guests)
    return ('<div class="detail-item">'
            '<span class="detail-label">👥 Ospiti</span>'
            f'<div class="guests-list">{tags}</div></div>')


def build_event(ev: dict, base_url: str, template: str) -> Path:
    for key in ("eventId", "title", "date", "startTime", "endTime", "location", "description", "image"):
        if not ev.get(key):
            raise ValueError(f"Evento {ev.get('eventId', '?')}: manca il campo '{key}'")

    event_id = ev["eventId"]
    page_url = f"{base_url}/{event_id}/"
    image_url = ev["image"] if ev["image"].startswith("http") else f"{base_url}/{event_id}/{ev['image']}"
    human = date_human(ev["date"])

    # dati per il JS (senza "</" per non chiudere il tag <script>)
    js_data = {**ev, "dateHuman": human, "pageUrl": page_url, "image": image_url}
    event_json = json.dumps(js_data, ensure_ascii=False).replace("</", "<\\/")

    esc = lambda s: html.escape(s, quote=True)
    values = {
        "title": esc(ev["title"]),
        "subtitle": esc(ev.get("subtitle", "")),
        "description": esc(ev["description"]),
        "date_human": esc(human),
        "time": f"{ev['startTime']} - {ev['endTime']}",
        "location": esc(ev["location"]),
        "map_url": esc(map_url(ev)),
        "image_url": esc(image_url),
        "page_url": esc(page_url),
        "guests_html": guests_html(ev.get("guests", [])),
        "event_json": event_json,
    }

    out = template
    for k, v in values.items():
        out = out.replace("{{" + k + "}}", v)

    dest = ROOT / event_id / "index.html"
    dest.parent.mkdir(exist_ok=True)
    dest.write_text(out, encoding="utf-8")
    return dest


def main() -> None:
    cfg = json.loads((ROOT / "events.json").read_text(encoding="utf-8"))
    base_url = cfg["base_url"].rstrip("/")
    template = (ROOT / "template.html").read_text(encoding="utf-8")
    for ev in cfg["events"]:
        print("OK ", build_event(ev, base_url, template))


if __name__ == "__main__":
    main()

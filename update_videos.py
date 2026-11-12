#!/usr/bin/env python3
"""Merge new videos from the Totin My Pack YouTube RSS feed into site data.

Uses only the Python standard library. The public Atom feed lists the latest
15 uploads; older videos already in data/videos.json are left unchanged.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
CHANNEL_ID = "UCUrz36HXFx9ABE4UDtjYeNg"
FEED_URL = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"
USER_AGENT = (
    "TotinMyPackSite/1.0 (+https://totinmypack.com; video catalog updater)"
)
TZ = ZoneInfo("America/New_York")
ATOM = "http://www.w3.org/2005/Atom"
YT = "http://www.youtube.com/xml/schemas/2015"
MEDIA = "http://search.yahoo.com/mrss/"

# Higher-weight phrases are listed first within each group. Generic state
# names score lower so "Dallas, Texas" or "Route 66, Texas" land correctly.
DEST_KEYWORDS: list[tuple[str, list[tuple[str, int]]]] = [
    (
        "dallas",
        [
            ("white rock lake", 6),
            ("white rock", 6),
            ("solar eclipse", 5),
            ("cooper's hawk", 5),
            ("fox squirrel", 5),
            ("hummingbird", 5),
            ("total eclipse", 5),
            ("totality", 4),
            ("damselfly", 4),
            ("eclipse", 3),
            ("anole", 4),
            ("dallas", 6),
        ],
    ),
    (
        "route66",
        [
            ("cadillac ranch", 6),
            ("devil's elbow", 6),
            ("devils elbow", 6),
            ("mother road", 6),
            ("route 66", 8),
            ("winslow", 5),
        ],
    ),
    (
        "berlin",
        [
            ("brandenburg gate", 6),
            ("berlin wall", 6),
            ("reichstag", 5),
            ("berlin", 6),
        ],
    ),
    (
        "greece",
        [
            ("agios nikolaos", 6),
            ("mount olympus", 6),
            ("halkidiki", 6),
            ("gerakini", 6),
            ("skopelos", 6),
            ("meteora", 6),
            ("itamos", 6),
            ("dragoudeli", 6),
            ("aegean", 5),
            ("olympus", 4),
            ("greece", 6),
            ("greek", 6),
        ],
    ),
    (
        "california",
        [
            ("chandelier tree", 6),
            ("santa rosa", 5),
            ("mendocino", 6),
            ("redwood", 5),
            ("california", 6),
            ("napa", 4),
        ],
    ),
    (
        "southwest",
        [
            ("rio grande gorge", 6),
            ("monument valley", 6),
            ("petrified forest", 6),
            ("sunset crater", 6),
            ("four corners", 6),
            ("oak creek", 5),
            ("grand canyon", 6),
            ("new mexico", 5),
            ("flagstaff", 5),
            ("shiprock", 6),
            ("wupatki", 6),
            ("arizona", 5),
            ("sedona", 6),
            ("santa fe", 6),
            ("roswell", 5),
            ("taos", 5),
        ],
    ),
    (
        "plains",
        [
            ("buffalo national", 6),
            ("devils tower", 6),
            ("devil's tower", 6),
            ("eureka springs", 6),
            ("south dakota", 6),
            ("black hills", 6),
            ("fort smith", 5),
            ("bella vista", 5),
            ("war eagle", 5),
            ("mount scott", 6),
            ("chickasha", 5),
            ("talimena", 6),
            ("pig trail", 6),
            ("carhenge", 6),
            ("oklahoma", 6),
            ("arkansas", 6),
            ("ozarks", 5),
        ],
    ),
    (
        "southeast",
        [
            ("new river gorge", 6),
            ("virginia beach", 6),
            ("south carolina", 6),
            ("north carolina", 6),
            ("cape charles", 6),
            ("myrtle beach", 6),
            ("georgia guidestones", 6),
            ("the waltons", 5),
            ("appomattox", 6),
            ("gatlinburg", 6),
            ("monticello", 5),
            ("moundville", 6),
            ("key west", 6),
            ("virginia", 5),
            ("norfolk", 6),
            ("savannah", 6),
            ("florida", 5),
            ("alabama", 5),
            ("roanoke", 5),
            ("meridian", 4),
            ("georgia", 5),
            ("tybee", 5),
        ],
    ),
    (
        "texas",
        [
            ("enchanted rock", 6),
            ("seminole canyon", 6),
            ("daingerfield", 6),
            ("purtis creek", 6),
            ("mother neff", 6),
            ("devils river", 6),
            ("devil's river", 6),
            ("caddo lake", 6),
            ("cranfills", 6),
            ("big bend", 6),
            ("bomarton", 6),
            ("beaumont", 5),
            ("el paso", 7),
            ("caddo", 4),
            ("texas", 5),
        ],
    ),
]


def log(msg: str) -> None:
    print(msg, flush=True)


def set_output(name: str, value: str) -> None:
    path = os.environ.get("GITHUB_OUTPUT")
    if path:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(f"{name}={value}\n")


def fetch(url: str, timeout: int = 30) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def parse_feed(xml_bytes: bytes) -> list[dict]:
    root = ET.fromstring(xml_bytes)
    entries = []
    for entry in root.findall(f"{{{ATOM}}}entry"):
        video_id_el = entry.find(f"{{{YT}}}videoId")
        title_el = entry.find(f"{{{ATOM}}}title")
        published_el = entry.find(f"{{{ATOM}}}published")
        if video_id_el is None or title_el is None or published_el is None:
            continue
        link_el = entry.find(f"{{{ATOM}}}link")
        href = link_el.get("href", "") if link_el is not None else ""
        desc_el = entry.find(f"{{{MEDIA}}}group/{{{MEDIA}}}description")
        description = desc_el.text or "" if desc_el is not None else ""
        entries.append(
            {
                "id": video_id_el.text.strip(),
                "title": (title_el.text or "").strip(),
                "published_raw": published_el.text.strip(),
                "url": href,
                "description": description,
            }
        )
    return entries


def is_short(entry: dict) -> bool:
    url = (entry.get("url") or "").lower()
    title = entry.get("title") or ""
    if "/shorts/" in url:
        return True
    if re.search(r"#shorts\b", title, re.I):
        return True
    return False


def assign_destination(title: str, description: str = "") -> str | None:
    text = f"{title}\n{description}".lower()
    # Normalize common punctuation so "route 66" still matches "Route 66".
    haystack = text.replace("–", "-").replace("—", "-")
    scores: dict[str, int] = {}
    for group, phrases in DEST_KEYWORDS:
        score = 0
        for phrase, weight in phrases:
            if phrase in haystack:
                score += weight
        if score:
            scores[group] = score
    if not scores:
        return None
    # Highest score wins; on a tie, the earlier (more specific) group wins.
    best = max(scores.values())
    for group, _phrases in DEST_KEYWORDS:
        if scores.get(group) == best:
            return group
    return None


def format_date(published_raw: str) -> tuple[str, str]:
    raw = published_raw.replace("Z", "+00:00")
    dt = datetime.fromisoformat(raw)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    local = dt.astimezone(TZ)
    display = f"{local.strftime('%B')} {local.day}, {local.year}"
    iso = local.strftime("%Y-%m-%d")
    return display, iso


def format_length(seconds: int) -> str:
    if seconds < 0:
        return ""
    hours, rem = divmod(seconds, 3600)
    minutes, secs = divmod(rem, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def fetch_length(video_id: str) -> str:
    url = f"https://www.youtube.com/watch?v={video_id}"
    try:
        html = fetch(url, timeout=30).decode("utf-8", "replace")
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        log(f"  warning: could not fetch duration for {video_id}: {exc}")
        return ""
    match = re.search(r'lengthSeconds":"(\d+)"', html)
    if not match:
        log(f"  warning: no duration found for {video_id}")
        return ""
    return format_length(int(match.group(1)))


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def merge(videos: list[dict], site: dict, entries: list[dict], *, fetch_durations: bool) -> list[dict]:
    known = {v["id"] for v in videos}
    new_entries = [e for e in entries if e["id"] not in known]
    if not new_entries:
        return []

    def published_key(entry: dict) -> datetime:
        raw = entry["published_raw"].replace("Z", "+00:00")
        dt = datetime.fromisoformat(raw)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt

    new_entries.sort(key=published_key)  # oldest first; insert(0) leaves newest on top
    added: list[dict] = []
    for entry in new_entries:
        kind = "short" if is_short(entry) else "film"
        group = assign_destination(entry["title"], entry.get("description", ""))
        date, published = format_date(entry["published_raw"])
        length = fetch_length(entry["id"]) if fetch_durations else ""
        record = {
            "id": entry["id"],
            "title": entry["title"],
            "kind": kind,
            "date": date,
            "published": published,
            "length": length,
            "groups": [group] if group else [],
        }
        videos.insert(0, record)
        added.append(record)
        dest = group or "unassigned (All videos / Latest only)"
        log(f"  added {record['id']}: {record['title']} [{kind}, {dest}, {date}, {length or 'no duration'}]")

        if kind == "short":
            teasers = [vid for vid in site["short_teaser_ids"] if vid != record["id"]]
            site["short_teaser_ids"] = [record["id"]] + teasers
            site["short_teaser_ids"] = site["short_teaser_ids"][:6]
        else:
            latest = [vid for vid in site["latest_film_ids"] if vid != record["id"]]
            site["latest_film_ids"] = [record["id"]] + latest
            site["latest_film_ids"] = site["latest_film_ids"][:8]
    return added


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--feed", help="Local RSS/Atom file instead of the live feed")
    parser.add_argument("--skip-duration", action="store_true", help="Do not scrape video lengths")
    parser.add_argument("--dry-run", action="store_true", help="Merge in memory and do not write files")
    args = parser.parse_args(argv)

    videos_path = ROOT / "data" / "videos.json"
    site_path = ROOT / "data" / "site.json"
    videos = load_json(videos_path)
    site = load_json(site_path)

    if args.feed:
        xml_bytes = Path(args.feed).read_bytes()
        log(f"Reading feed from {args.feed}")
    else:
        log(f"Fetching {FEED_URL}")
        xml_bytes = fetch(FEED_URL)
    entries = parse_feed(xml_bytes)
    log(f"Feed has {len(entries)} entries; catalog has {len(videos)} videos")

    added = merge(videos, site, entries, fetch_durations=not args.skip_duration)
    if not added:
        log("No new videos.")
        set_output("changed", "false")
        set_output("added", "")
        return 0

    if not args.dry_run:
        dump_json(videos_path, videos)
        dump_json(site_path, site)
        log(f"Wrote {videos_path.relative_to(ROOT)} and {site_path.relative_to(ROOT)}")

    set_output("changed", "true")
    set_output("added", ",".join(v["id"] for v in added))
    log(f"Added {len(added)} video(s).")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001 — surface a clear Actions failure
        log(f"error: {exc}")
        raise

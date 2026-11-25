#!/usr/bin/env python3
"""Publish planned New England films to the site only after YouTube releases them.

The manifest supplies the exact Central-time schedule and YouTube IDs. A due
film must appear in the public channel feed and have a working YouTube oEmbed
response before its catalog record and article are added. Failed checks leave
the website unchanged; the next scheduled run retries without duplicating posts.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

from update_videos import FEED_URL, fetch, parse_feed, set_output

ROOT = Path(__file__).resolve().parent
MANIFEST_PATH = ROOT / "data" / "new-england-releases.json"
COPY_PATH = ROOT / "data" / "new-england-episode-copy.json"
STATE_PATH = ROOT / "data" / "new-england-release-state.json"
ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{11}$")


def timestamp(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("Release times must contain a timezone offset")
    return dt


def load_manifest(path: Path = MANIFEST_PATH) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        raise ValueError("Unsupported release manifest schema")
    tz = ZoneInfo(data["timezone"])
    days: set[int] = set()
    ids: set[str] = set()
    previous = None
    for item in data["episodes"]:
        day = item["day"]
        if day in days or not isinstance(day, int) or day < 1:
            raise ValueError("Release day numbers must be unique positive integers")
        days.add(day)
        due = timestamp(item["publish_at"])
        if due.utcoffset() != due.astimezone(tz).utcoffset():
            raise ValueError("Release time offset does not match the manifest timezone")
        if previous and due <= previous:
            raise ValueError("Episode release times must be in chronological order")
        previous = due
        vid = item.get("video_id")
        if vid:
            if not ID_PATTERN.fullmatch(vid) or vid in ids:
                raise ValueError("YouTube video IDs must be valid and unique")
            ids.add(vid)
    return data


def public_and_embeddable(video_id: str, public_ids: set[str]) -> bool:
    # A playable oEmbed alone can also describe an unlisted video. Requiring
    # membership in the channel's public feed avoids treating that as public.
    if video_id not in public_ids:
        return False
    url = "https://www.youtube.com/oembed?" + urlencode(
        {"url": f"https://www.youtube.com/watch?v={video_id}", "format": "json"}
    )
    try:
        data = json.loads(fetch(url, timeout=20, attempts=2))
    except (OSError, ValueError) as exc:
        print(f"  pending {video_id}: YouTube embed check unavailable ({type(exc).__name__})")
        return False
    return (
        data.get("provider_name") == "YouTube"
        and data.get("type") == "video"
        and video_id in data.get("html", "")
        and bool(data.get("title"))
    )


def release_episode(
    episode: dict, article: dict, series: dict, videos: list, site: dict,
    blog: dict, state: dict, now: datetime,
) -> bool:
    """Apply one verified release in memory. Existing releases are idempotent."""
    vid = episode.get("video_id")
    if not vid or not ID_PATTERN.fullmatch(vid):
        raise ValueError("A real YouTube video ID is required before publication")
    if vid in state["published"]:
        return False
    due = timestamp(episode["publish_at"])
    if now < due:
        return False
    local = due.astimezone(ZoneInfo(series["timezone"]))
    seconds = round(episode["duration_seconds"])
    minutes, secs = divmod(seconds, 60)
    record = {
        "id": vid,
        "title": episode["video_title"],
        "kind": "film",
        "date": f"{local.strftime('%B')} {local.day}, {local.year}",
        "published": local.strftime("%Y-%m-%d"),
        "length": f"{minutes}:{secs:02d}",
        "groups": ["newengland"],
    }
    videos[:] = [v for v in videos if v["id"] != vid]
    videos.insert(0, record)
    site["latest_film_ids"] = (
        [vid] + [old for old in site["latest_film_ids"] if old != vid]
    )[:8]
    if not any(card["slug"] == "new-england" for card in site["dest_cards"]):
        site["dest_cards"].append({"slug": "new-england", "name": "New England", "img": vid})

    post = copy.deepcopy(article)
    post.update({
        "video_id": vid,
        "date_published": episode["publish_at"],
        "series_slug": series["series_slug"],
        "series_title": series["title"],
        "episode_day": episode["day"],
    })
    existing = [p for p in blog["posts"] if p["slug"] == post["slug"]]
    if existing and existing[0].get("video_id") not in (None, vid):
        raise ValueError(f"Article slug already belongs to a different video: {post['slug']}")
    blog["posts"] = [p for p in blog["posts"] if p["slug"] != post["slug"]] + [post]
    state["published"][vid] = {
        "day": episode["day"], "publish_at": episode["publish_at"],
        "verified_public_at": now.astimezone(timezone.utc).isoformat(),
        "article_slug": post["slug"],
    }
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Check due films without writing site data")
    args = parser.parse_args(argv)
    manifest = load_manifest()
    now = datetime.now(timezone.utc)
    state = json.loads(STATE_PATH.read_text(encoding="utf-8")) if STATE_PATH.exists() else {"published": {}}
    due = [e for e in manifest["episodes"]
           if timestamp(e["publish_at"]) <= now and e.get("video_id") not in state["published"]]
    missing = [e for e in due if not e.get("video_id")]
    for e in missing:
        print(f"  pending Day {e['day']}: YouTube upload ID has not been assigned")
    due = [e for e in due if e.get("video_id")]
    if not due:
        print("No new assigned releases are due.")
        set_output("changed", "false")
        return 0
    try:
        public_ids = {e["id"] for e in parse_feed(fetch(FEED_URL, timeout=20, attempts=2))}
    except Exception as exc:
        print(f"Public channel feed unavailable ({type(exc).__name__}); no planned films released.")
        set_output("changed", "false")
        return 0
    articles = {p["day"]: p for p in json.loads(COPY_PATH.read_text(encoding="utf-8"))}
    paths = [ROOT / "data" / name for name in ("videos.json", "site.json", "blog.json")]
    videos, site, blog = [json.loads(p.read_text(encoding="utf-8")) for p in paths]
    added = []
    for e in due:
        if not public_and_embeddable(e["video_id"], public_ids):
            print(f"  pending Day {e['day']}: public YouTube release is not yet confirmed")
            continue
        if release_episode(e, articles[e["day"]], manifest, videos, site, blog, state, now):
            added.append(e["video_id"])
            print(f"  released Day {e['day']}: film, article and series listing")
    if added and not args.dry_run:
        # All publication decisions and validation have completed before writing.
        for path, data in zip(paths + [STATE_PATH], [videos, site, blog, state]):
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    set_output("changed", "true" if added else "false")
    set_output("added", ",".join(added))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

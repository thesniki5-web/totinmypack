#!/usr/bin/env python3
"""Generate the Totin My Pack static site."""
from __future__ import annotations

import html
import json
import shutil
import unicodedata
from collections import OrderedDict
from pathlib import Path
from urllib.parse import parse_qs, quote, urlparse

ROOT = Path(__file__).resolve().parent
SITE = "https://totinmypack.com"
CHANNEL = "https://youtube.com/@totinmypack"
PLAYLIST = "https://www.youtube.com/playlist?list=PLVqSQzmPjiMw"
CHANNEL_DESC = (
    "Travel with Totin My Pack through Greece and across the United States. "
    "We share short travel films, scenic drives, state parks, historic places, "
    "and personal memories from our trips."
)
CHANNEL_META = (
    "Travel with Totin My Pack through Greece and the United States: "
    "short travel films, scenic drives, state parks, historic places, "
    "and memories from our trips."
)

# Preview branches set this True so the built pages stay noindex, show a
# banner, and omit GoatCounter. Production builds leave it False.
PREVIEW = True
PREVIEW_BANNER = (
    '<div class="draft-banner" role="status">'
    "<p><strong>Preview only.</strong> These changes are not on the live site yet.</p>"
    "</div>"
)

# Dates are America/New_York. Eight early films use YouTube's published date only.
# The catalog itself lives in data/videos.json and is updated from the channel RSS feed.
SITE_DATA = json.loads((ROOT / "data" / "site.json").read_text(encoding="utf-8"))
VIDEOS = json.loads((ROOT / "data" / "videos.json").read_text(encoding="utf-8"))
START_IDS = SITE_DATA["start_ids"]
HERO_ID = SITE_DATA["hero_id"]
LATEST_FILM_IDS = SITE_DATA["latest_film_ids"]
SHORT_TEASER_IDS = SITE_DATA["short_teaser_ids"]
DEST_CARDS = SITE_DATA["dest_cards"]
BY_ID = {v["id"]: v for v in VIDEOS}

DESTINATIONS = [
    {
        "slug": "greece",
        "name": "Greece",
        "count_label": "films from Halkidiki and beyond",
        "hero": "ONbdk7yflpM",
        "hero_pos": "30% 50%",
        "blurb": "Films from Halkidiki — Gerakini, Mount Itamos, Mount Dragoudeli, and a summer camp at Agios Nikolaos — and a 2008 trip to Skopelos, Meteora, and Mount Olympus.",
        "og": "ONbdk7yflpM",
    },
    {
        "slug": "texas",
        "name": "Texas",
        "count_label": "road trips, parks, and churches",
        "hero": "_pAqzkL05D8",
        "hero_pos": "16% 100%",
        "blurb": "Road trips, state parks, country churches, and river country: Big Bend, Devils River, Caddo Lake, Enchanted Rock, Seminole Canyon, and small towns across the state.",
        "meta": "Texas road trips, state parks, country churches, and river country, including Big Bend, Devils River, Caddo Lake, Enchanted Rock, and Seminole Canyon.",
        "og": "_pAqzkL05D8",
        "hero_alt": "A hiker on the granite slope of Enchanted Rock in Texas.",
    },
    {
        "slug": "dallas",
        "name": "Dallas & close to home",
        "count_label": "wildlife, weather, and the sky",
        "hero": "e6Wr9Cpg0y8",
        "hero_pos": "80% 40%",
        "blurb": "Wildlife, weather, and the sky close to home — including the total solar eclipse of April 8, 2024, snow at White Rock Lake, and birds filmed on a Dallas balcony.",
        "meta": "Wildlife, weather, and the sky close to home, including the total solar eclipse of April 8, 2024, snow at White Rock Lake, and birds on a Dallas balcony.",
        "og": "VktGvxzG4sU",
    },
    {
        "slug": "route-66",
        "key": "route66",
        "name": "Route 66",
        "count_label": "the Mother Road, one stop at a time",
        "hero": "egYLfHGUae4",
        "hero_pos": "90% 50%",
        "blurb": "Stops along the Mother Road in Texas, Oklahoma, Missouri, New Mexico, and Arizona. The films have not covered every mile — yet.",
        "og": "DHxZueP0Z04",
    },
    {
        "slug": "plains",
        "name": "Oklahoma, Arkansas & the Plains",
        "count_label": "fall color, the Ozarks, and the road north",
        "hero": "3cFk5Tf7nOg",
        "hero_pos": "100% 48%",
        "blurb": "Fall color on the Talimena Scenic Byway, the Ozarks, Oklahoma landmarks, and a road trip from Dallas to the Black Hills and Devils Tower.",
        "og": "3cFk5Tf7nOg",
    },
    {
        "slug": "southeast",
        "name": "Southeast & Mid-Atlantic",
        "count_label": "Virginia to Key West",
        "hero": "jNoREzI7-B0",
        "hero_pos": "80% 50%",
        "blurb": "Virginia’s coast and historic country, the Carolinas, Georgia, Alabama, a Key West journey, and a 2014 throwback to Gatlinburg.",
        "og": "jNoREzI7-B0",
    },
    {
        "slug": "california",
        "name": "California",
        "count_label": "redwoods to the Pacific",
        "hero": "lbhHR6MpSlA",
        "hero_pos": "75% 50%",
        "blurb": "A northern road trip through Santa Rosa, Mendocino, and Napa, and a drive from the redwoods to the Pacific.",
        "og": "lbhHR6MpSlA",
    },
    {
        "slug": "southwest",
        "name": "The Southwest",
        "count_label": "canyon country and desert roads",
        "hero": "5cLy5YOaPW8",
        "hero_pos": "50% 85%",
        "blurb": "Grand Canyon, Sedona, Santa Fe, Taos, Monument Valley, Shiprock, and the road home through Petrified Forest and Roswell.",
        "og": "5cLy5YOaPW8",
    },
    {
        "slug": "berlin",
        "name": "Berlin",
        "count_label": "a winter film from 2012",
        "hero": "VeKh55kDqeg",
        "hero_pos": "50% 50%",
        "blurb": "A winter film of Brandenburg Gate, the Reichstag, and the Berlin Wall, from a 2012 trip.",
        "og": "VeKh55kDqeg",
    },
]




def thumb(vid: str, name: str = "maxresdefault") -> str:
    """Absolute YouTube still URL. Used for Open Graph and JSON-LD."""
    return f"https://i.ytimg.com/vi/{vid}/{name}.jpg"


THUMB_WIDTHS = (640, 960, 1280)


def _local_thumb_widths(vid: str) -> list[int]:
    return [w for w in THUMB_WIDTHS if (ROOT / "assets" / "thumbs" / f"{vid}-{w}.webp").exists()]


def _thumb_srcset_attrs(
    vid: str,
    *,
    sizes: str,
    prefix: str,
    default_width: int | None = None,
) -> str | None:
    widths = _local_thumb_widths(vid)
    if not widths:
        return None
    if default_width not in widths:
        default_width = 960 if 960 in widths else widths[0]
    src = f"{prefix}assets/thumbs/{vid}-{default_width}.webp"
    srcset = ", ".join(f"{prefix}assets/thumbs/{vid}-{w}.webp {w}w" for w in widths)
    height = round(default_width * 9 / 16)
    return (
        f'src="{src}" srcset="{srcset}" sizes="{sizes}" '
        f'width="{default_width}" height="{height}"'
    )


def thumb_srcset(
    vid: str,
    *,
    sizes: str = "(max-width: 700px) 92vw, (max-width: 1100px) 45vw, 400px",
    prefix: str = "",
) -> str:
    """Card thumbnails: local WebP when present, otherwise YouTube stills."""
    local = _thumb_srcset_attrs(vid, sizes=sizes, prefix=prefix, default_width=640)
    if local:
        return local
    src = thumb(vid, "hqdefault")
    srcset = (
        f"{thumb(vid, 'mqdefault')} 320w, "
        f"{thumb(vid, 'hqdefault')} 480w, "
        f"{thumb(vid, 'maxresdefault')} 1280w"
    )
    return (
        f'src="{src}" srcset="{srcset}" sizes="{sizes}" '
        f'width="480" height="360" data-fallback="{esc(vid)}"'
    )


HERO_WIDTHS = (640, 960, 1280)
HERO_WEBP_QUALITY = 60


def _hero_ids() -> list[str]:
    ids: list[str] = [HERO_ID, "3cFk5Tf7nOg", "p9PXuj51NJs", "2f-wKhlW_PE"]
    ids.extend(d["hero"] for d in DESTINATIONS)
    seen: set[str] = set()
    out: list[str] = []
    for vid in ids:
        if vid and vid not in seen:
            seen.add(vid)
            out.append(vid)
    return out


def ensure_hero_images(vid: str | None = None) -> None:
    """Write right-sized, more tightly compressed WebP heroes from the largest local thumb."""
    from PIL import Image

    out_dir = ROOT / "assets" / "heroes"
    out_dir.mkdir(parents=True, exist_ok=True)
    for v in ([vid] if vid else _hero_ids()):
        src_widths = _local_thumb_widths(v)
        if not src_widths:
            continue
        src_path = ROOT / "assets" / "thumbs" / f"{v}-{src_widths[-1]}.webp"
        try:
            im = Image.open(src_path)
            if im.mode not in ("RGB", "RGBA"):
                im = im.convert("RGB")
        except OSError:
            continue
        src_w, src_h = im.size
        for w in HERO_WIDTHS:
            dest = out_dir / f"{v}-{w}.webp"
            if dest.exists() and dest.stat().st_mtime >= src_path.stat().st_mtime and dest.stat().st_size > 0:
                continue
            if w == src_w:
                frame = im
            else:
                h = max(1, round(src_h * w / src_w))
                frame = im.resize((w, h), Image.Resampling.LANCZOS)
            frame.save(dest, format="WEBP", quality=HERO_WEBP_QUALITY, method=6)


def _hero_local_widths(vid: str) -> list[int]:
    return [w for w in HERO_WIDTHS if (ROOT / "assets" / "heroes" / f"{vid}-{w}.webp").exists()]


def _hero_srcset_attrs(vid: str, prefix: str, default_width: int = 960) -> str | None:
    ensure_hero_images(vid)
    widths = _hero_local_widths(vid)
    folder = "heroes"
    if not widths:
        widths = _local_thumb_widths(vid)
        folder = "thumbs"
    if not widths:
        return None
    if default_width not in widths:
        default_width = 960 if 960 in widths else widths[0]
    src = f"{prefix}assets/{folder}/{vid}-{default_width}.webp"
    srcset = ", ".join(f"{prefix}assets/{folder}/{vid}-{w}.webp {w}w" for w in widths)
    height = round(default_width * 9 / 16)
    return (
        f'src="{src}" srcset="{srcset}" sizes="100vw" '
        f'width="{default_width}" height="{height}"'
    )


def hero_img(vid: str, alt: str, prefix: str = "", style: str = "") -> str:
    style_attr = f" style=\"{style}\"" if style else ""
    local = _hero_srcset_attrs(vid, prefix=prefix)
    if local:
        return (
            f'<img {local} alt="{esc(alt)}" '
            f'fetchpriority="high" loading="eager" decoding="async"{style_attr}>'
        )
    return (
        f'<img src="{thumb(vid)}" alt="{esc(alt)}" width="1280" height="720" '
        f'fetchpriority="high" loading="eager" decoding="async"{style_attr}>'
    )


def hero_preload(vid: str, prefix: str = "") -> str:
    ensure_hero_images(vid)
    widths = _hero_local_widths(vid)
    folder = "heroes"
    if not widths:
        widths = _local_thumb_widths(vid)
        folder = "thumbs"
    if not widths:
        return ""
    default = 960 if 960 in widths else widths[0]
    href = f"{prefix}assets/{folder}/{vid}-{default}.webp"
    srcset = ", ".join(f"{prefix}assets/{folder}/{vid}-{w}.webp {w}w" for w in widths)
    return (
        f'<link rel="preload" as="image" href="{href}" type="image/webp" '
        f'imagesrcset="{srcset}" imagesizes="100vw" fetchpriority="high">'
    )


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def play_icon() -> str:
    return (
        '<span class="play-badge" aria-hidden="true">'
        '<svg viewBox="0 0 24 24" focusable="false"><polygon points="8,5 20,12 8,19"/></svg>'
        "</span>"
    )


def film_card(v: dict, *, featured: bool = False, lazy: bool = True, prefix: str = "") -> str:
    kind = v["kind"]
    cls = "film-card"
    thumb_cls = "thumb thumb-short" if kind == "short" else "thumb"
    loading = "eager" if featured or not lazy else "lazy"
    fetch = ' fetchpriority="high"' if featured else ""
    alt = esc(v["title"])
    return f"""
<article>
  <button class="{cls}" type="button" data-video-id="{esc(v['id'])}" data-title="{esc(v['title'])}" data-kind="{kind}" data-filter-item data-group="{esc(v['groups'][0]) if v.get('groups') else ''}">
    <span class="{thumb_cls}">
      <img {thumb_srcset(v['id'], prefix=prefix)} alt="{alt}" loading="{loading}" decoding="async"{fetch}>
      {play_icon()}
      {f'<span class="chip">{esc(v["length"])}</span>' if v.get("length") else ""}
    </span>
    <span class="film-meta">
      <span class="film-title">{esc(v['title'])}</span>
      <span class="film-sub">{esc(v['date'])} · {'Short' if kind == 'short' else 'Film'}</span>
    </span>
  </button>
</article>"""



def _goat_event_path(href: str, *, kind: str | None = None, name: str | None = None) -> str:
    """Readable GoatCounter event path for an outbound link. Must not start with /."""
    if kind and name:
        return f"{kind}: {name}"
    try:
        parsed = urlparse(href)
    except ValueError:
        return "out: link"
    host = (parsed.hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]
    path = parsed.path or ""
    if host in {"youtube.com", "m.youtube.com", "youtu.be", "youtube-nocookie.com"}:
        vid = ""
        if host == "youtu.be":
            vid = path.strip("/").split("/")[0] if path.strip("/") else ""
        else:
            vid = (parse_qs(parsed.query).get("v") or [""])[0]
            parts = [part for part in path.split("/") if part]
            if not vid and parts and parts[0] in {"embed", "shorts", "live", "v"} and len(parts) > 1:
                vid = parts[1]
            elif not vid and parts and parts[0].startswith("@"):
                return f"out: youtube.com/{parts[0]}"
            elif not vid and "playlist" in parts:
                return "out: youtube.com/playlist"
        if vid:
            return f"out: youtube.com/{vid}"
        return "out: youtube.com"
    label = host or "link"
    if path and path != "/":
        short = path.rstrip("/")
        if len(short) > 48:
            short = short[:45] + "..."
        label = f"{host}{short}"
    return f"out: {label}"


def _goat_click_attrs(
    href: str,
    *,
    kind: str | None = None,
    name: str | None = None,
    title: str | None = None,
) -> str:
    path = _goat_event_path(href, kind=kind, name=name)
    label = title or path
    return (
        f' data-goatcounter-click="{esc(path)}"'
        f' data-goatcounter-title="{esc(label)}"'
    )


def nav(prefix: str, current: str) -> str:
    def cur(name: str) -> str:
        return ' aria-current="page"' if current == name else ""

    dest_cur = (
        ' aria-current="page"'
        if current == "dest" or current.startswith("dest-")
        else ""
    )
    html = f"""
<header class="site-header">
  <div class="header-inner">
    <a class="logo" href="{prefix}index.html">
      <img src="{prefix}assets/logo-128.webp" width="128" height="128" alt="">
      <span class="logo-text">Totin&nbsp;<span>My Pack</span></span>
    </a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav" aria-label="Open menu">
      <span class="nav-toggle-bars"></span>
    </button>
    <nav class="site-nav" id="site-nav" aria-label="Primary">
      <ul>
        <li><a href="{prefix}videos.html"{cur("videos")}>Films</a></li>
        <li><a href="{prefix}trips/index.html"{cur("trips")}>Trips</a></li>
        <li><a href="{prefix}destinations/index.html"{dest_cur}>Destinations</a></li>
        <li class="has-sub">
          <button class="nav-label" type="button" id="nav-food-stays-btn" aria-expanded="false" aria-haspopup="true" aria-controls="nav-food-stays">Food &amp; Stays</button>
          <ul class="subnav" id="nav-food-stays" aria-labelledby="nav-food-stays-btn">
            <li><a href="{prefix}restaurants.html"{cur("restaurants")}>Restaurants</a></li>
            <li><a href="{prefix}hotels.html"{cur("hotels")}>Hotels</a></li>
          </ul>
        </li>
        <li><a href="{prefix}about.html"{cur("about")}>About</a></li>
      </ul>
      <a class="btn btn-gold nav-cta" href="{CHANNEL}" rel="noopener noreferrer"{_goat_click_attrs(CHANNEL)}>Subscribe on YouTube</a>
    </nav>
  </div>
</header>"""

    if PREVIEW:
        html = (
            '\n<div class="preview-topbar" role="status">'
            "<p><strong>Preview only.</strong> These changes are not on the live site yet.</p>"
            "</div>"
            + html
        )
    return html


def footer(prefix: str, extra_js: str = "") -> str:
    dest_links = "\n      ".join(
        f'<a href="{prefix}destinations/{d["slug"]}.html">{esc(d["name"])}</a>'
        for d in DESTINATIONS
    )
    trip_links = "\n      ".join(
        f'<a href="{prefix}trips/{trip["slug"]}.html">{esc(trip["name"])}</a>'
        for trip in (_trip_data(slug) for slug in _trip_slugs())
    )
    goat = _goat_script()
    return f"""
<footer class="site-footer">
  <div class="footer-inner">
    <div>
      <a class="logo" href="{prefix}index.html">
      <img src="{prefix}assets/logo-128.webp" width="128" height="128" alt="">
      <span class="logo-text">Totin&nbsp;<span>My Pack</span></span>
    </a>
      <p>Short travel films from Greece and the United States.</p>
    </div>
    <nav class="footer-navs" aria-label="Footer">
    <div class="footer-nav-group">
      <p class="footer-nav-label">The site</p>
      <div class="footer-nav">
      <a href="{prefix}videos.html">Films</a>
      <a href="{prefix}trips/index.html">Trips</a>
      <a href="{prefix}destinations/index.html">Destinations</a>
      <a href="{prefix}restaurants.html">Restaurants</a>
      <a href="{prefix}hotels.html">Hotels</a>
      <a href="{prefix}shorts.html">Shorts</a>
      <a href="{prefix}gear.html">What I film with</a>
      <a href="{prefix}about.html">About</a>
      <a href="{prefix}privacy.html">Privacy</a>
      <a href="{CHANNEL}" rel="noopener noreferrer"{_goat_click_attrs(CHANNEL)}>YouTube</a>
      </div>
    </div>
    <div class="footer-nav-group">
      <p class="footer-nav-label">Destinations</p>
      <div class="footer-nav">
      {dest_links}
      </div>
    </div>
    <div class="footer-nav-group">
      <p class="footer-nav-label">Trips</p>
      <div class="footer-nav">
      {trip_links}
      </div>
    </div>
    </nav>
  </div>
</footer>
<dialog class="player-dialog" id="player-dialog" aria-labelledby="player-caption">
  <form method="dialog"><button class="player-close" type="submit">Close</button></form>
  <div class="player-frame"></div>
  <p class="player-caption" id="player-caption"></p>
  <p class="youtube-fallback"></p>
  <div class="player-tour" id="player-tour" hidden>
    <button type="button" class="btn btn-ghost player-tour-btn" id="player-tour-prev" disabled>Previous stop</button>
    <p class="player-tour-status" id="player-tour-status" aria-live="polite"></p>
    <button type="button" class="btn btn-gold player-tour-btn" id="player-tour-next">Next stop</button>
  </div>
</dialog>
<script src="{prefix}js/main.js" defer></script>
{extra_js}{goat}"""



def _goat_script() -> str:
    # Async, at the end of the body so it does not compete with LCP work in the head.
    if PREVIEW:
        return ""
    return (
        '\n<script data-goatcounter="https://totinmypack.goatcounter.com/count" '
        'async src="https://gc.zgo.at/count.js"></script>'
    )


def head(title: str, description: str, path: str, og_id: str, prefix: str, extra: str = "", og_logo: bool = False, robots: str | None = None, preconnect_yt: bool = True, early_extra: str = "") -> str:
    canon = SITE + path
    if og_logo or og_id == "logo":
        image = f"{SITE}/assets/og-image.jpg"
        og_w, og_h = 1200, 630
    else:
        image = thumb(og_id)
        og_w, og_h = 1280, 720
    if PREVIEW:
        robots = robots or "noindex"
    robots_tag = (
        f'  <meta name="robots" content="{esc(robots)}">\n' if robots else ""
    )
    yt_preconnect = (
        '<link rel="preconnect" href="https://i.ytimg.com">\n  ' if preconnect_yt else ""
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
{robots_tag}  <link rel="canonical" href="{esc(canon)}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Totin My Pack">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{esc(canon)}">
  <meta property="og:image" content="{esc(image)}">
  <meta property="og:image:width" content="{og_w}">
  <meta property="og:image:height" content="{og_h}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(description)}">
  <meta name="twitter:image" content="{esc(image)}">
  <meta name="theme-color" content="#0e0c0a">
  <link rel="icon" href="{prefix}assets/favicon-32.png" type="image/png" sizes="32x32">
  <link rel="icon" href="{prefix}assets/icon-512.png" type="image/png" sizes="512x512">
  <link rel="apple-touch-icon" href="{prefix}assets/apple-touch-icon.png" sizes="180x180">
  <link rel="shortcut icon" href="{prefix}favicon.ico">
  {early_extra}
  <link rel="preload" href="{prefix}assets/fonts/outfit-latin.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="{prefix}assets/fonts/fraunces-italic-latin.woff2" as="font" type="font/woff2" crossorigin>
  {yt_preconnect}<link rel="stylesheet" href="{prefix}css/styles.css">
  {extra}
</head>"""


def json_ld_home() -> str:
    items = []
    for i, vid in enumerate(START_IDS, 1):
        v = BY_ID[vid]
        items.append(
            {
                "@type": "VideoObject",
                "position": i,
                "name": v["title"],
                "url": f"https://www.youtube.com/watch?v={v['id']}",
                "thumbnailUrl": thumb(v["id"]),
                "embedUrl": f"https://www.youtube-nocookie.com/embed/{v['id']}",
            }
        )
    data = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebSite",
                "name": "Totin My Pack",
                "url": SITE,
                "description": CHANNEL_DESC,
                "publisher": {"@type": "Organization", "name": "Totin My Pack", "url": SITE, "sameAs": [CHANNEL]},
            },
            {"@type": "ItemList", "name": "Start Here | Totin My Pack Travel Favorites", "itemListElement": items},
        ],
    }
    return f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>'


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print("wrote", path.relative_to(ROOT))


def page_home() -> str:
    prefix = ""
    start_cards = "".join(film_card(BY_ID[i], featured=(n == 0), lazy=(n != 0), prefix=prefix) for n, i in enumerate(START_IDS))
    latest = "".join(film_card(BY_ID[i], lazy=True) for i in LATEST_FILM_IDS)
    shorts = "".join(film_card(BY_ID[i], lazy=True) for i in SHORT_TEASER_IDS)
    dest_cards = []
    for card in DEST_CARDS:
        slug, name, img = card["slug"], card["name"], card["img"]
        key = "route66" if slug == "route-66" else slug.replace("-", "")
        n = sum(1 for v in BY_ID.values() if key in v["groups"])
        label = "1 film" if n == 1 else f"{n} films"
        photo = ""
        if img:
            photo = (
                f'<img {thumb_srcset(img, sizes="(max-width: 560px) 46vw, (max-width: 900px) 30vw, 280px", prefix=prefix)} '
                f'alt="" loading="lazy" decoding="async">'
            )
        dest_cards.append(
            f"""
<a class="region-tile" href="destinations/{slug}.html">
  {photo}
  <span class="region-tile-copy">
    <h3>{esc(name)}</h3>
    <p>{esc(label)}</p>
  </span>
</a>"""
        )
    return f"""{head("Totin My Pack — Travel films from Greece and the United States", CHANNEL_META, "/", "logo", prefix, json_ld_home(), og_logo=True)}
<body>
<a class="skip-link" href="#content">Skip to content</a>
{nav(prefix, "home")}
<main id="content">
  <section class="hero" aria-label="Introduction">
    <div class="hero-media">
      {hero_img(HERO_ID, "Autumn cypress trees and moss reflected in still water at Caddo Lake, East Texas, from the film Caddo Lake in Fall.", prefix)}
    </div>
    <div class="hero-shade" aria-hidden="true"></div>
    <div class="hero-copy">
      <p class="kicker">Travel films</p>
      <h1>Totin My Pack</h1>
      <p class="lede">{esc(CHANNEL_DESC)}</p>
      <div class="hero-actions">
        <a class="btn btn-gold" href="#start-here">Start here</a>
        <a class="btn btn-ghost" href="{CHANNEL}" rel="noopener noreferrer"{_goat_click_attrs(CHANNEL)}>Subscribe on YouTube</a>
      </div>
    </div>
  </section>

  <section class="section" id="start-here" aria-labelledby="start-heading">
    <div class="wrap">
      <div class="section-head">
        <div class="section-intro">
          <p class="kicker">Watch first</p>
          <h2 id="start-heading">Start Here</h2>
          <p>Five short travel films chosen as a first look: a historic Texas church, an ancient tree in Greece, autumn in the mountains, turquoise river water, and a cypress swamp.</p>
        </div>
        <a class="link-arrow" href="{PLAYLIST}" rel="noopener noreferrer"{_goat_click_attrs(PLAYLIST)}>Play all on YouTube</a>
      </div>
      <div class="film-grid featured">
        {start_cards}
      </div>
    </div>
  </section>

  <section class="section" id="destinations" aria-labelledby="dest-heading" style="padding-top:0">
    <div class="wrap">
      <div class="section-head">
        <div class="section-intro">
          <p class="kicker">Places</p>
          <h2 id="dest-heading">Destinations</h2>
          <p>From Halkidiki to Route 66, the films follow roads, parks, and historic places across Greece and the United States.</p>
        </div>
        <a class="link-arrow" href="destinations/index.html">All destinations</a>
      </div>
      <div class="region-grid">
        {''.join(dest_cards)}
      </div>
    </div>
  </section>

  <section class="section" aria-labelledby="latest-heading" style="padding-top:0">
    <div class="wrap">
      <div class="section-head">
        <div class="section-intro">
          <p class="kicker">Recent</p>
          <h2 id="latest-heading">Latest films</h2>
        </div>
        <a class="link-arrow" href="videos.html">All films</a>
      </div>
      <div class="film-grid">
        {latest}
      </div>
    </div>
  </section>

  <section class="section" aria-labelledby="shorts-heading" style="padding-top:0">
    <div class="wrap">
      <div class="section-head">
        <div class="section-intro">
          <p class="kicker">Moments</p>
          <h2 id="shorts-heading">Shorts</h2>
          <p>Brief scenes from the same roads and places — hummingbirds, river water, fall color, and roadside stops.</p>
        </div>
        <a class="link-arrow" href="shorts.html">All Shorts</a>
      </div>
      <div class="shorts-row">
        {shorts}
      </div>
    </div>
  </section>

  <section class="band" aria-labelledby="subscribe-heading">
    <div>
      <h2 id="subscribe-heading">Watch the next film on YouTube</h2>
      <p>New travel films and Shorts are published on the Totin My Pack channel.</p>
    </div>
    <a class="btn btn-gold" href="{CHANNEL}" rel="noopener noreferrer"{_goat_click_attrs(CHANNEL)}>Subscribe on YouTube</a>
  </section>
</main>
{footer(prefix)}
</body>
</html>"""


def page_destinations_index() -> str:
    prefix = "../"
    cards = []
    for d in DESTINATIONS:
        n = sum(1 for v in BY_ID.values() if d.get("key", d["slug"].replace("-", "")) in [g if g != "route-66" else "route66" for g in v["groups"]] or d.get("key", d["slug"]) in v["groups"] or d["slug"].replace("-", "") in v["groups"])
        # simpler count:
        key = d.get("key", d["slug"].replace("-", ""))
        if d["slug"] == "route-66":
            key = "route66"
        n = sum(1 for v in BY_ID.values() if key in v["groups"])
        cards.append(
            f"""
<a class="dest-card" href="{d['slug']}.html">
  <img {thumb_srcset(d['hero'], sizes="(max-width: 560px) 92vw, (max-width: 900px) 45vw, 380px", prefix=prefix)} alt="{esc(d['name'])}" loading="lazy" decoding="async">
  <span class="dest-copy">
    <h2>{esc(d['name'])}</h2>
    <p>{n} {'film' if n == 1 else 'films'}</p>
  </span>
</a>"""
        )
    desc = "Browse Totin My Pack travel films by place: Greece, Texas, Dallas, Route 66, the Plains, the Southeast, California, the Southwest, and Berlin."
    return f"""{head("Destinations — Totin My Pack", desc, "/destinations/", "logo", prefix, og_logo=True, early_extra=hero_preload("3cFk5Tf7nOg", prefix))}
<body>
<a class="skip-link" href="#content">Skip to content</a>
{nav(prefix, "dest")}
<main id="content">
  <section class="page-hero" aria-label="Destinations">
    <div class="hero-media">
      {hero_img('3cFk5Tf7nOg', "Autumn forest and ridgelines along the Talimena Scenic Byway.", prefix, style="object-position:78% 45%")}
    </div>
    <div class="hero-shade" aria-hidden="true"></div>
    <div class="hero-copy">
      <p class="kicker">Places</p>
      <h1>Destinations</h1>
      <p class="lede">Short travel films grouped by the roads and places they follow, from Halkidiki to Route 66.</p>
    </div>
  </section>
  <section class="section">
    <div class="wrap">
      <div class="dest-grid">
        {''.join(cards)}
      </div>
    </div>
  </section>
</main>
{footer(prefix)}
</body>
</html>"""


def dest_key(d: dict) -> str:
    if d["slug"] == "route-66":
        return "route66"
    return d.get("key", d["slug"].replace("-", ""))


def page_destination(d: dict) -> str:
    prefix = "../"
    key = dest_key(d)
    films = [v for v in BY_ID.values() if key in v["groups"] and v["kind"] == "film"]
    shorts = [v for v in BY_ID.values() if key in v["groups"] and v["kind"] == "short"]
    # Keep plan order: films first as listed in VIDEOS
    # The first film card sits below the page hero, so do not mark it featured:
    # fetchpriority=high and eager loading would compete with the LCP image.
    film_cards = "".join(film_card(v, featured=False, lazy=True, prefix=prefix) for v in films)
    short_cards = "".join(film_card(v, lazy=True, prefix=prefix) for v in shorts)
    shorts_block = ""
    if shorts:
        shorts_block = f"""
  <section class="section" aria-labelledby="shorts-heading" style="padding-top:0">
    <div class="wrap">
      <div class="section-head">
        <div class="section-intro">
          <h2 id="shorts-heading">Shorts</h2>
        </div>
      </div>
      <div class="shorts-row">
        {short_cards}
      </div>
    </div>
  </section>"""
    trip_cta = ""
    if (ROOT / "data" / "trips" / f"{d['slug']}.json").is_file():
        trip_cta = (
            '<div class="hero-actions">'
            f'<a class="btn btn-gold" href="../trips/{d["slug"]}.html">Follow the journey on the map</a>'
            "</div>"
        )
    title = f"{d['name']} — Totin My Pack"
    desc = d.get("meta") or d["blurb"]
    return f"""{head(title, desc, f"/destinations/{d['slug']}.html", d["og"], prefix, early_extra=hero_preload(d["hero"], prefix))}
<body>
<a class="skip-link" href="#content">Skip to content</a>
{nav(prefix, "dest-"+d["slug"])}
<main id="content">
  <section class="page-hero" aria-label="{esc(d['name'])}">
    <div class="hero-media">
      {hero_img(d["hero"], d.get("hero_alt") or d["name"], prefix, style=f"object-position:{d['hero_pos']}" if d.get("hero_pos") else "")}
    </div>
    <div class="hero-shade" aria-hidden="true"></div>
    <div class="hero-copy">
      <p class="kicker">Destination</p>
      <h1>{esc(d['name'])}</h1>
      <p class="lede">{esc(d['blurb'])}</p>
      {trip_cta}
    </div>
  </section>
  <section class="section" aria-labelledby="films-heading">
    <div class="wrap">
      <div class="section-head">
        <div class="section-intro">
          <h2 id="films-heading">Films</h2>
        </div>
      </div>
      <div class="film-grid">
        {film_cards}
      </div>
    </div>
  </section>
  {shorts_block}
  <section class="band" aria-labelledby="subscribe-heading">
    <div>
      <h2 id="subscribe-heading">Subscribe on YouTube</h2>
      <p>Watch these films, and new ones as they are published, on the Totin My Pack channel.</p>
    </div>
    <a class="btn btn-gold" href="{CHANNEL}" rel="noopener noreferrer"{_goat_click_attrs(CHANNEL)}>Subscribe on YouTube</a>
  </section>
</main>
{footer(prefix)}
</body>
</html>"""


def page_videos() -> str:
    prefix = ""
    films = [v for v in BY_ID.values() if v["kind"] == "film"]
    # newest first — use a simple month map
    def sort_key(v):
        months = {m: i for i, m in enumerate(
            ["January","February","March","April","May","June","July","August","September","October","November","December"], 1)}
        parts = v["date"].replace(",", "").split()
        month, day, year = months[parts[0]], int(parts[1]), int(parts[2])
        return (-year, -month, -day)
    films = sorted(films, key=sort_key)
    cards = "".join(film_card(v, lazy=True) for v in films)
    filters = [
        ("all", "All places"),
        ("greece", "Greece"),
        ("texas", "Texas"),
        ("dallas", "Dallas"),
        ("route66", "Route 66"),
        ("plains", "Plains"),
        ("southeast", "Southeast"),
        ("california", "California"),
        ("southwest", "Southwest"),
        ("berlin", "Berlin"),
    ]
    btns = "".join(
        f'<button type="button" data-filter="{k}" aria-pressed="{"true" if k=="all" else "false"}" class="{"is-active" if k=="all" else ""}">{esc(label)}</button>'
        for k, label in filters
    )
    desc = "All Totin My Pack travel films, from Greece, Texas, Route 66, and roads across the United States."
    return f"""{head("Films — Totin My Pack", desc, "/videos.html", "logo", prefix, extra=hero_preload("p9PXuj51NJs", prefix), og_logo=True)}
<body>
<a class="skip-link" href="#content">Skip to content</a>
{nav(prefix, "videos")}
<main id="content">
  <section class="page-hero" aria-label="Films">
    <div class="hero-media">
      {hero_img("p9PXuj51NJs", "Turquoise water of the Devils River in West Texas, seen from above.", prefix, style="object-position:80% 50%")}
    </div>
    <div class="hero-shade" aria-hidden="true"></div>
    <div class="hero-copy">
      <p class="kicker">The collection</p>
      <h1>Films</h1>
      <p class="lede">Short cinematic travel films — scenic drives, state parks, historic places, and personal memories from the road.</p>
    </div>
  </section>
  <section class="section">
    <div class="wrap">
      <div class="filters" data-filters role="group" aria-label="Filter films by place">
        {btns}
      </div>
      <p class="filter-status" data-filter-status>{len(films)} films shown.</p>
      <div class="film-grid">
        {cards}
      </div>
    </div>
  </section>
</main>
{footer(prefix)}
</body>
</html>"""


def page_shorts() -> str:
    prefix = ""
    shorts = [v for v in BY_ID.values() if v["kind"] == "short"]
    months = {m: i for i, m in enumerate(
        ["January","February","March","April","May","June","July","August","September","October","November","December"], 1)}
    def sort_key(v):
        parts = v["date"].replace(",", "").split()
        return (-int(parts[2]), -months[parts[0]], -int(parts[1]))
    shorts = sorted(shorts, key=sort_key)
    cards = "".join(film_card(v, lazy=True) for v in shorts)
    desc = "Totin My Pack YouTube Shorts: brief scenes from Greece, Texas, Route 66, and roads across the United States."
    return f"""{head("Shorts — Totin My Pack", desc, "/shorts.html", "logo", prefix, og_logo=True)}
<body>
<a class="skip-link" href="#content">Skip to content</a>
{nav(prefix, "shorts")}
<main id="content">
  <section class="page-hero" aria-label="Shorts">
    <div class="hero-media">
      {hero_img("2f-wKhlW_PE", (BY_ID.get("2f-wKhlW_PE") or {}).get("title") or "Autumn From Above in Talimena #Shorts", prefix, style="object-position:70% 40%")}
    </div>
    <div class="hero-shade" aria-hidden="true"></div>
    <div class="hero-copy">
      <p class="kicker">Moments</p>
      <h1>Shorts</h1>
      <p class="lede">Brief scenes from the same trips — wildlife close to home, river water in West Texas, fall color, and roadside stops.</p>
    </div>
  </section>
  <section class="section">
    <div class="wrap">
      <div class="shorts-row">
        {cards}
      </div>
    </div>
  </section>
  <section class="band" aria-labelledby="subscribe-heading">
    <div>
      <h2 id="subscribe-heading">Subscribe on YouTube</h2>
      <p>New Shorts are published on the Totin My Pack channel.</p>
    </div>
    <a class="btn btn-gold" href="{CHANNEL}" rel="noopener noreferrer"{_goat_click_attrs(CHANNEL)}>Subscribe on YouTube</a>
  </section>
</main>
{footer(prefix)}
</body>
</html>"""


def _about_source_text() -> str:
    path = ROOT / "data" / "about-source-teddy-2026-11-14.txt"
    return path.read_text(encoding="utf-8")


def _about_paragraphs(text: str) -> list[str]:
    parts = [p.strip() for p in text.strip("\n").split("\n\n")]
    return [p for p in parts if p]


def page_about() -> str:
    prefix = ""
    paragraphs = _about_paragraphs(_about_source_text())
    first = paragraphs[0] if paragraphs else ""
    # Meta description uses sentences already on the About page, lengthened
    # from the first line alone so it falls in the usual 120–160 character range.
    desc = (
        "Hi, I’m Teddy. Totin My Pack is where I share the places, roads, "
        "and moments I want to remember, from Greece and across the United States."
    )
    body = []
    for i, para in enumerate(paragraphs):
        cls = ' class="lead"' if i == 0 else ""
        body.append(f"<p{cls}>{esc(para)}</p>")
    body_html = "\n        ".join(body)
    return f"""{head("About — Totin My Pack", desc, "/about.html", "logo", prefix, og_logo=True)}
<body>
<a class="skip-link" href="#content">Skip to content</a>
{nav(prefix, "about")}
<main id="content">
  <section class="page-hero" aria-label="About">
    <div class="hero-shade" aria-hidden="true"></div>
    <div class="hero-copy">
      <h1>About</h1>
    </div>
  </section>
  <section class="section">
    <div class="wrap">
      <div class="prose">
        {body_html}
      </div>
    </div>
  </section>
</main>
{footer(prefix)}
</body>
</html>"""


def _trip_slugs() -> list[str]:
    names = [p.stem for p in (ROOT / "data" / "trips").glob("*.json")]
    preferred = [
        "route-66",
        "greece",
        "texas",
        "dallas",
        "plains",
        "virginia-2024",
        "southeast",
        "california",
        "southwest",
        "berlin",
    ]
    ordered = [s for s in preferred if s in names]
    ordered += sorted(s for s in names if s not in ordered)
    return ordered


def _trip_data(slug: str) -> dict:
    path = ROOT / "data" / "trips" / f"{slug}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _trip_intro_line(trip: dict) -> str:
    """A short existing line only — lede, or the first intro sentence that is not about the map."""
    lede = (trip.get("lede") or "").strip()
    if lede:
        return lede
    for para in trip.get("intro") or []:
        text = (para or "").strip()
        if text and "the map" not in text.lower() and "map line" not in text.lower():
            return text
    return ""


def _trip_place_city(place: dict) -> str:
    city = (place.get("city") or "").strip()
    region = (place.get("region") or "").strip()
    if city and region:
        return f"{city}, {region}"
    return city or region


def _trip_simple_place_list(heading: str, heading_id: str, items: list[dict], *, kind: str) -> str:
    if not items:
        return ""
    rows = []
    for item in items:
        name = item.get("name") or ""
        place = _trip_place_city(item)
        website = (item.get("website") or "").strip()
        if website:
            label = f"Website for {name}"
            name_html = (
                f'<a class="trip-where-name" href="{esc(website)}" '
                f'target="_blank" rel="noopener noreferrer" '
                f'aria-label="{esc(label)}"{_goat_click_attrs(website, kind=f"{kind}-website", name=name, title=label)}>'
                f"{esc(name)}</a>"
            )
        else:
            name_html = f'<span class="trip-where-name">{esc(name)}</span>'
        place_html = f'<span class="trip-where-place">{esc(place)}</span>' if place else ""
        rows.append(f"<li>{name_html}{place_html}</li>")
    return (
        f'<section class="trip-where" aria-labelledby="{esc(heading_id)}">'
        f'<h2 id="{esc(heading_id)}">{esc(heading)}</h2>'
        f'<ul>{"".join(rows)}</ul></section>'
    )


def page_trips_index() -> str:
    prefix = "../"
    trips = [_trip_data(slug) for slug in _trip_slugs()]
    desc = "Travel journeys from Totin My Pack, from the places named in the films — including Route 66 and Greece."
    items = []
    for trip in trips:
        blurb = (trip.get("index_blurb") or "").strip()
        blurb_html = f'<span class="trips-index-blurb">{esc(blurb)}</span>' if blurb else ""
        items.append(
            "<li>"
            f'<a href="{esc(trip["slug"])}.html">'
            f'<span class="trips-index-name">{esc(trip["name"])}</span>'
            f"{blurb_html}</a></li>"
        )
    return f"""{head("Trips — Totin My Pack", desc, "/trips/", "logo", prefix, og_logo=True)}
<body class="trip-simple-page">
<a class="skip-link" href="#content">Skip to content</a>
{nav(prefix, "trips")}
<main id="content">
  <div class="trip-simple">
    <header class="trip-simple-head">
      <h1>Trips</h1>
      <p class="trip-simple-intro">Films arranged as a journey, one road at a time, from the places named in the videos.</p>
    </header>
    <ul class="trips-index-list">
      {''.join(items)}
    </ul>
  </div>
</main>
{footer(prefix)}
</body>
</html>"""



def _stop_videos(stop: dict) -> list[dict]:
    out = []
    for vid in stop.get("videos") or []:
        v = BY_ID.get(vid)
        if v:
            out.append({"id": v["id"], "title": v["title"], "kind": v["kind"]})
    return out


def _trip_places(trip: dict) -> list[tuple[str, dict]]:
    """Restaurants and hotels already in site data whose city matches a filmed stop."""
    rests = {r["id"]: r for r in (_restaurant_data().get("restaurants") or [])}
    hotels = {h["id"]: h for h in (_hotel_data().get("hotels") or [])}
    out: list[tuple[str, dict]] = []
    for rid in trip.get("restaurants") or []:
        r = rests.get(rid)
        if r:
            out.append(("restaurant", r))
    for hid in trip.get("hotels") or []:
        h = hotels.get(hid)
        if h:
            out.append(("hotel", h))
    return out


def _trip_postcard_video(trip: dict) -> str | None:
    candidates: list[str] = []
    for key in ("hero", "overview_film"):
        if trip.get(key):
            candidates.append(trip[key])
    candidates.extend(trip.get("films") or [])
    for stop in trip.get("stops") or []:
        candidates.extend(stop.get("videos") or [])
    seen: set[str] = set()
    for vid in candidates:
        if not vid or vid in seen:
            continue
        seen.add(vid)
        if vid in BY_ID or _local_thumb_widths(vid):
            return vid
    return None


def _trip_postcard_alt(trip: dict, vid: str) -> str:
    if vid == trip.get("hero"):
        alt = (trip.get("hero_alt") or "").strip()
        if alt:
            return alt
    video = BY_ID.get(vid) or {}
    title = (video.get("title") or "").strip()
    if title:
        return f"A still from {title}"
    return trip.get("name") or "Trip still"


def _trip_postcard(trip: dict, prefix: str) -> str:
    vid = _trip_postcard_video(trip)
    if not vid:
        return ""
    alt = _trip_postcard_alt(trip, vid)
    img_attrs = thumb_srcset(
        vid,
        sizes="(max-width: 42rem) 92vw, 42rem",
        prefix=prefix,
    )
    return (
        f'<figure class="trip-postcard">'
        f'<img {img_attrs} alt="{esc(alt)}" decoding="async">'
        f"</figure>"
    )


def page_trip(slug: str) -> str:
    prefix = "../"
    trip = _trip_data(slug)
    along = _trip_places(trip)
    hotels = [p for k, p in along if k == "hotel"]
    restaurants = [p for k, p in along if k == "restaurant"]

    stops_html = []
    for stop in trip.get("stops") or []:
        name = stop.get("name") or ""
        place = (stop.get("place") or "").strip()
        videos = _stop_videos(stop)
        if videos:
            href = f"https://www.youtube.com/watch?v={videos[0]['id']}"
            label = f"Watch the film for {name}" if videos[0]["kind"] != "short" else f"Watch the Short for {name}"
            if len(videos) == 1:
                # keep the label short; the visible text is the stop name
                label = videos[0]["title"]
            name_html = (
                f'<a class="trip-stop-name" href="{esc(href)}" '
                f'target="_blank" rel="noopener noreferrer" '
                f'aria-label="{esc(label)}"{_goat_click_attrs(href)}>{esc(name)}</a>'
            )
        else:
            name_html = f'<span class="trip-stop-name">{esc(name)}</span>'
        place_html = f'<span class="trip-stop-place">{esc(place)}</span>' if place else ""
        desc = (stop.get("description") or "").strip()
        desc_html = f'<p class="trip-stop-desc">{esc(desc)}</p>' if desc else ""
        stops_html.append(f"<li><div>{name_html}{place_html}{desc_html}</div></li>")

    # add a route-line dot on each stop
    stops_html = [
        item.replace("<li><div>", '<li><span class="trip-stop-dot" aria-hidden="true"></span><div>', 1)
        for item in stops_html
    ]
    intro = _trip_intro_line(trip)
    intro_html = f'<p class="trip-simple-intro">{esc(intro)}</p>' if intro else ""
    postcard = _trip_postcard(trip, prefix)
    stops_block = (
        f'<ol class="trip-stops">{"".join(stops_html)}</ol>' if stops_html else ""
    )
    stayed = _trip_simple_place_list("Where we stayed", "trip-stayed-heading", hotels, kind="hotel")
    ate = _trip_simple_place_list("Where we ate", "trip-ate-heading", restaurants, kind="restaurant")
    desc = trip.get("description") or trip["name"]
    og = trip.get("hero") or "logo"
    og_logo = not trip.get("hero")
    html_title = f'{trip["title"]} — Totin My Pack'
    dest_titles = {f"{d['name']} — Totin My Pack" for d in DESTINATIONS}
    if html_title in dest_titles:
        html_title = f"{trip['name']} trip — Totin My Pack"
    return f"""{head(html_title, desc, f"/trips/{slug}.html", og if not og_logo else "logo", prefix, og_logo=og_logo)}
<body class="trip-simple-page">
<a class="skip-link" href="#content">Skip to content</a>
{nav(prefix, "trips")}
<main id="content">
  <article class="trip-simple">
    {postcard}
    <header class="trip-simple-head">
      <h1>{esc(trip["name"])}</h1>
      {intro_html}
    </header>
    {stops_block}
    {stayed}
    {ate}
  </article>
</main>
{footer(prefix)}
</body>
</html>"""


def page_trip_route66() -> str:
    return page_trip("route-66")


def _restaurant_data() -> dict:
    path = ROOT / "data" / "restaurants.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _restaurant_place(r: dict) -> str:
    parts = [r.get("city") or "", r.get("region") or "", r.get("country") or ""]
    seen: list[str] = []
    for part in parts:
        part = part.strip()
        if part and part not in seen:
            seen.append(part)
    return ", ".join(seen)


def _fold_slug(text: str) -> str:
    folded = "".join(
        ch for ch in unicodedata.normalize("NFKD", text) if not unicodedata.combining(ch)
    )
    slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in folded).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug


def _restaurant_slug(r: dict, index: int) -> str:
    raw = _fold_slug((r.get("id") or "").strip())
    if raw:
        return raw
    base = "-".join(x for x in [(r.get("name") or "").strip(), (r.get("city") or "").strip()] if x)
    return _fold_slug(base) or f"restaurant-{index + 1}"


def _restaurant_region(r: dict) -> str:
    country = (r.get("country") or "").strip()
    if country and country not in {"United States", "USA", "US"}:
        return country
    return (r.get("region") or country or "").strip()


def _names_differ(listed: str, official: str) -> bool:
    def norm(s: str) -> str:
        return (
            (s or "")
            .replace("’", "'")
            .replace("‘", "'")
            .replace("`", "'")
            .strip()
        )

    return bool((listed or "").strip()) and norm(listed) != norm(official)



def _source_label(url: str) -> str:
    host = (urlparse(url).netloc or "").lower()
    if host.startswith("www."):
        host = host[4:]
    labels = {
        "openstreetmap.org": "OpenStreetMap",
        "facebook.com": "Facebook",
        "maps.apple.com": "Apple Maps",
        "geocoding.geo.census.gov": "U.S. Census geocoder",
        "visitmckinney.com": "Visit McKinney",
        "catfishhotel.com": "Official visit page",
        "sirved.com": "Sirved",
        "wilsoncountynews.com": "Wilson County News",
        "visitfrisco.com": "Visit Frisco",
        "yelp.com": "Yelp",
    }
    if host in labels:
        return labels[host]
    for key, label in labels.items():
        if host == key or host.endswith("." + key):
            return label
    return host or "Source"


def _directions_url(r: dict) -> str:
    lat, lng = r.get("lat"), r.get("lng")
    if lat is not None and lng is not None:
        return f"https://www.openstreetmap.org/?mlat={lat}&mlon={lng}#map=18/{lat}/{lng}"
    addr = (r.get("address") or "").strip()
    if addr:
        return f"https://www.openstreetmap.org/search?query={quote(addr)}"
    return ""


def _external_link(href: str, label: str, aria: str, *, kind: str | None = None, name: str | None = None) -> str:
    return (
        f'<a href="{esc(href)}" target="_blank" rel="noopener noreferrer" '
        f'aria-label="{esc(aria)}"{_goat_click_attrs(href, kind=kind, name=name, title=aria)}>'
        f"{esc(label)}</a>"
    )



def _restaurant_card(r: dict, index: int, prefix: str, *, link_kind: str = "restaurant") -> str:
    rid = esc(_restaurant_slug(r, index))
    name = r.get("name") or "Restaurant"
    place = _restaurant_place(r)
    status = (r.get("status") or "").strip().lower()
    status_label = {"open": "Open", "closed": "Closed", "unverified": "Unverified"}.get(status, "")
    status_html = (
        f'<p class="restaurant-status is-{esc(status)}">{esc(status_label)}</p>'
        if status_label
        else ""
    )
    cuisine = f'<p class="restaurant-cuisine">{esc(r["cuisine"])}</p>' if r.get("cuisine") else ""
    address = f'<p class="restaurant-address">{esc(r["address"])}</p>' if r.get("address") else ""
    note = (
        f'<p class="restaurant-note">{esc(r["teddy_note"])}</p>'
        if (r.get("teddy_note") or "").strip()
        else ""
    )
    visited = (
        f'<p class="restaurant-visited">Visited {esc(r["visited"])}</p>'
        if (r.get("visited") or "").strip()
        else ""
    )
    actions: list[str] = []
    if r.get("website"):
        actions.append(
            _external_link(r["website"], "Website", f"Website for {name}", kind=f"{link_kind}-website", name=name)
        )
    directions = _directions_url(r)
    if directions:
        actions.append(
            _external_link(directions, "Directions", f"Directions to {name}", kind=f"{link_kind}-directions", name=name)
        )
    if r.get("lat") is not None and r.get("lng") is not None:
        actions.append(
            f'<button type="button" class="trip-stop-locate" data-restaurant-focus="{rid}" '
            f'aria-label="Show on the map: {esc(name)}">'
            "Show on the map</button>"
        )
    video_id = (r.get("video_id") or "").strip()
    if video_id:
        v = BY_ID.get(video_id)
        title = v["title"] if v else name
        kind = v["kind"] if v else "film"
        start = r.get("start_seconds")
        start_attr = f' data-start="{int(start)}"' if start else ""
        actions.append(
            f'<button type="button" class="trip-watch" data-video-id="{esc(video_id)}" '
            f'data-title="{esc(title)}" data-kind="{esc(kind)}"{start_attr}>'
            "Watch the film</button>"
        )
    actions_html = (
        f'<p class="restaurant-card-actions">{"".join(actions)}</p>' if actions else ""
    )
    sources = [s for s in (r.get("sources") or []) if s]
    if sources:
        items = "".join(
            f"<li>{_external_link(s, _source_label(s), f'Source for {name}: {_source_label(s)}', kind=f'{link_kind}-source', name=name)}</li>"
            for s in sources
        )
        sources_html = (
            f'<details class="restaurant-sources">'
            f'<summary aria-label="Sources for {esc(name)}">Sources</summary>'
            f'<ul>{items}</ul>'
            f"</details>"
        )
    else:
        sources_html = ""
    place_html = f'<p class="restaurant-place">{esc(place)}</p>' if place else ""
    listed = (r.get("listed_as") or "").strip()
    listed_html = (
        f'<p class="restaurant-listed">Listed as: {esc(listed)}</p>'
        if _names_differ(listed, name)
        else ""
    )
    loc_note = (r.get("location_note") or "").strip()
    loc_html = f'<p class="restaurant-location-note">{esc(loc_note)}</p>' if loc_note else ""
    photo = (r.get("photo") or "").strip()
    photo_html = ""
    card_class = "restaurant-card"
    if photo:
        domain = (r.get("photo_domain") or "").strip()
        alt = (r.get("photo_alt") or "").strip() or (
            f"{name}, photo from {domain}" if domain else name
        )
        w = r.get("photo_width") or 800
        h = r.get("photo_height") or ""
        size_attrs = f' width="{int(w)}"' + (f' height="{int(h)}"' if h else "")
        credit = ""
        credit_href = (r.get("photo_credit_url") or r.get("website") or "").strip()
        credit_label = (r.get("photo_credit") or (f"Photo: {domain}" if domain else "")).strip()
        if credit_label and credit_href:
            credit = (
                f'<figcaption class="restaurant-photo-credit">'
                f'{_external_link(credit_href, credit_label, f"Photo of {name} from {domain or credit_label}", kind=f"{link_kind}-photo", name=name)}'
                f"</figcaption>"
            )
        elif credit_label:
            credit = f'<figcaption class="restaurant-photo-credit">{esc(credit_label)}</figcaption>'
        photo_html = (
            f'<figure class="restaurant-photo">'
            f'<img src="{prefix}assets/{esc(photo)}" alt="{esc(alt)}"{size_attrs} loading="lazy" decoding="async">'
            f"{credit}</figure>"
        )
        card_class += " has-photo"
    return (
        f'<article class="{card_class}" id="restaurant-{rid}">'
        f"{photo_html}"
        f'<div class="restaurant-card-body">'
        f"<h4>{esc(name)}</h4>"
        f"{place_html}{listed_html}{cuisine}{address}{status_html}{loc_html}{note}{visited}{actions_html}{sources_html}"
        f"</div>"
        "</article>"
    )



LEAFLET_CSS = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
LEAFLET_JS = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
LEAFLET_CSS_INTEGRITY = "sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
LEAFLET_JS_INTEGRITY = "sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo="


def _map_poster_hints(prefix: str, poster: str) -> str:
    # LCP is a same-origin static first-view of the map. Preload that image
    # and do not preload Leaflet, so the poster wins the first paint.
    return (
        f'<link rel="preload" as="image" href="{prefix}assets/maps/{poster}" '
        f'type="image/webp" fetchpriority="high">'
    )


def _map_leaflet_hints() -> str:
    # Used on hotels, where a static poster hurt the live 98 score.
    return (
        '<link rel="preconnect" href="https://unpkg.com" crossorigin>\n'
        '  <link rel="preconnect" href="https://tile.openstreetmap.org">\n'
        f'  <link rel="preload" as="style" href="{LEAFLET_CSS}" crossorigin '
        f'integrity="{LEAFLET_CSS_INTEGRITY}">\n'
        f'  <link rel="preload" as="script" href="{LEAFLET_JS}" crossorigin '
        f'integrity="{LEAFLET_JS_INTEGRITY}">'
    )


def _map_mount(map_id: str, label: str, poster: str, prefix: str) -> str:
    attrib = (
        '<p class="trip-map-static-attrib">'
        "© "
        + _external_link(
            "https://www.openstreetmap.org/copyright",
            "OpenStreetMap",
            "OpenStreetMap copyright",
        )
        + " contributors</p>"
    )
    return (
        f'<div id="{map_id}" class="trip-map has-poster" role="region" aria-label="{label}">'
        f'<img class="trip-map-poster" src="{prefix}assets/maps/{poster}" '
        f'width="740" height="704" alt="" fetchpriority="high">'
        f"{attrib}"
        '<p class="trip-map-placeholder">The map loads when you scroll to it. The list is below.</p>'
        "</div>"
    )


def page_restaurants() -> str:
    prefix = ""
    data = _restaurant_data()
    restaurants = list(data.get("restaurants") or [])
    payload_places = []
    number = 0
    groups: OrderedDict[str, OrderedDict[str, list[tuple[int, dict]]]] = OrderedDict()
    for i, r in enumerate(restaurants):
        rid = _restaurant_slug(r, i)
        has_pin = r.get("lat") is not None and r.get("lng") is not None
        if has_pin:
            number += 1
        video_id = (r.get("video_id") or "").strip()
        v = BY_ID.get(video_id) if video_id else None
        item = {
            "id": rid,
            "name": r.get("name") or "",
            "place": _restaurant_place(r),
            "lat": r.get("lat"),
            "lng": r.get("lng"),
            "cuisine": r.get("cuisine") or "",
            "address": r.get("address") or "",
            "website": r.get("website") or "",
            "status": r.get("status") or "",
            "teddy_note": (r.get("teddy_note") or "").strip(),
        }
        if has_pin:
            item["number"] = number
        if video_id:
            item["video_id"] = video_id
            if v:
                item["video_title"] = v["title"]
                item["video_kind"] = v["kind"]
            if r.get("start_seconds"):
                item["start_seconds"] = int(r["start_seconds"])
        payload_places.append(item)
        region = _restaurant_region(r) or "Other"
        city = (r.get("city") or "").strip() or "Unspecified"
        groups.setdefault(region, OrderedDict()).setdefault(city, []).append((i, r))

    if groups:
        sections = []
        for region, cities in groups.items():
            region_id = esc(_fold_slug(f"region-{region}") or "region")
            city_blocks = []
            for city, items in cities.items():
                cards = "".join(_restaurant_card(r, i, prefix) for i, r in items)
                city_blocks.append(
                    '<div class="restaurant-city-group">'
                    f'<p class="restaurant-city-label">{esc(city)}</p>'
                    f'<div class="restaurant-city-cards">{cards}</div>'
                    "</div>"
                )
            sections.append(
                f'<section class="restaurant-region" aria-labelledby="{region_id}">'
                f'<h3 id="{region_id}">{esc(region)}</h3>'
                + "".join(city_blocks)
                + "</section>"
            )
        list_html = f'<div class="restaurant-list">{"".join(sections)}</div>'
    else:
        list_html = (
            '<div class="restaurant-empty" role="status">'
            "<p><strong>Coming soon.</strong> When restaurants are added, they will appear "
            "on the map and in this list.</p>"
            "</div>"
        )

    map_payload = {
        "default_bounds": [[24.5, -125.0], [49.4, 28.3]],
        "maxZoom": 12,
        "restaurants": payload_places,
    }
    map_json = json.dumps(map_payload, ensure_ascii=False)
    extra_js = f'<script src="{prefix}js/restaurant-map.js" defer></script>'
    title = "Restaurants — Totin My Pack"
    desc = "Places we’ve eaten and liked along the way, from Greece and the United States. Each pin sits at the restaurant’s true location."
    early = _map_poster_hints(prefix, "restaurants.webp")
    return f"""{head(title, desc, "/restaurants.html", "logo", prefix, early_extra=early, og_logo=True, preconnect_yt=False)}
<body>
<a class="skip-link" href="#content">Skip to content</a>
{nav(prefix, "restaurants")}
<main id="content">
  <section class="page-hero" aria-label="Restaurants">
    <div class="hero-shade" aria-hidden="true"></div>
    <div class="hero-copy">
      <p class="kicker">Along the way</p>
      <h1>Restaurants</h1>
      <p class="lede">Places we’ve eaten and liked along the way.</p>
      <div class="hero-actions">
        <a class="btn btn-gold" href="#restaurant-map">View the map</a>
      </div>
    </div>
  </section>
  <section class="section restaurant-map-section" aria-labelledby="map-heading">
    <div class="wrap">
      <div class="section-head">
        <div class="section-intro">
          <p class="kicker">The places</p>
          <h2 id="map-heading">The map</h2>
          <p>Each pin sits at the restaurant’s true location. Local restaurants with more than one location are pinned at the city center. Places without a precise point stay in the list without a pin.</p>
        </div>
      </div>
      <div class="trip-map-frame restaurant-map-frame">
        {_map_mount("restaurant-map", "Map of restaurants", "restaurants.webp", prefix)}
      </div>
      <p class="map-attrib">Map data © <a href="https://www.openstreetmap.org/copyright" rel="noopener noreferrer"{_goat_click_attrs("https://www.openstreetmap.org/copyright")}>OpenStreetMap</a></p>
    </div>
  </section>
  <section class="section" aria-labelledby="list-heading" style="padding-top:0">
    <div class="wrap">
      <div class="section-head">
        <div class="section-intro">
          <p class="kicker">The list</p>
          <h2 id="list-heading">Places</h2>
        </div>
      </div>
      {list_html}
    </div>
  </section>
</main>
{footer(prefix, extra_js)}
<script type="application/json" id="restaurant-map-data">{map_json}</script>
</body>
</html>"""


def _hotel_data() -> dict:
    path = ROOT / "data" / "hotels.json"
    if not path.exists():
        return {"hotels": []}
    return json.loads(path.read_text(encoding="utf-8"))


def page_hotels() -> str:
    prefix = ""
    data = _hotel_data()
    hotels = list(data.get("hotels") or [])
    payload_places = []
    number = 0
    groups: OrderedDict[str, OrderedDict[str, list[tuple[int, dict]]]] = OrderedDict()
    for i, r in enumerate(hotels):
        rid = _restaurant_slug(r, i)
        has_pin = r.get("lat") is not None and r.get("lng") is not None
        if has_pin:
            number += 1
        item = {
            "id": rid,
            "name": r.get("name") or "",
            "place": _restaurant_place(r),
            "lat": r.get("lat"),
            "lng": r.get("lng"),
            "address": r.get("address") or "",
            "website": r.get("website") or "",
            "teddy_note": (r.get("teddy_note") or "").strip(),
        }
        if has_pin:
            item["number"] = number
        payload_places.append(item)
        region = _restaurant_region(r) or "Other"
        city = (r.get("city") or "").strip() or "Unspecified"
        groups.setdefault(region, OrderedDict()).setdefault(city, []).append((i, r))

    if groups:
        sections = []
        for region, cities in groups.items():
            region_id = esc(_fold_slug(f"region-{region}") or "region")
            city_blocks = []
            for city, items in cities.items():
                cards = "".join(_hotel_card(r, i, prefix) for i, r in items)
                city_blocks.append(
                    '<div class="restaurant-city-group">'
                    f'<p class="restaurant-city-label">{esc(city)}</p>'
                    f'<div class="restaurant-city-cards">{cards}</div>'
                    "</div>"
                )
            sections.append(
                f'<section class="restaurant-region" aria-labelledby="{region_id}">'
                f'<h3 id="{region_id}">{esc(region)}</h3>'
                + "".join(city_blocks)
                + "</section>"
            )
        list_html = f'<div class="restaurant-list">{"".join(sections)}</div>'
    else:
        list_html = (
            '<div class="restaurant-empty" role="status">'
            "<p><strong>Coming soon.</strong> When hotels are added, they will appear "
            "on the map and in this list.</p>"
            "</div>"
        )

    map_payload = {
        "default_bounds": [[24.5, -125.0], [49.4, 28.3]],
        "maxZoom": 12,
        "hotels": payload_places,
    }
    map_json = json.dumps(map_payload, ensure_ascii=False)
    extra_js = f'<script src="{prefix}js/restaurant-map.js" defer></script>'
    title = "Hotels — Totin My Pack"
    desc = "Places we’ve stayed and liked along the way, shown on the map at each stay’s true location when we have a precise point."
    extra = _map_leaflet_hints()
    return f"""{head(title, desc, "/hotels.html", "logo", prefix, extra=extra, og_logo=True, preconnect_yt=False)}
<body>
<a class="skip-link" href="#content">Skip to content</a>
{nav(prefix, "hotels")}
<main id="content">
  <section class="page-hero" aria-label="Hotels">
    <div class="hero-shade" aria-hidden="true"></div>
    <div class="hero-copy">
      <p class="kicker">Along the way</p>
      <h1>Hotels</h1>
      <p class="lede">Places we’ve stayed and liked along the way.</p>
      <div class="hero-actions">
        <a class="btn btn-gold" href="#hotel-map">View the map</a>
      </div>
    </div>
  </section>
  <section class="section restaurant-map-section" aria-labelledby="map-heading">
    <div class="wrap">
      <div class="section-head">
        <div class="section-intro">
          <p class="kicker">The places</p>
          <h2 id="map-heading">The map</h2>
          <p>Each pin sits at the stay’s true location. Places without a precise point stay in the list without a pin.</p>
        </div>
      </div>
      <div class="trip-map-frame restaurant-map-frame">
        <div id="hotel-map" class="trip-map" role="region" aria-label="Map of hotels">
          <p class="trip-map-placeholder">The map loads when you scroll to it. The list is below.</p>
        </div>
      </div>
      <p class="map-attrib">Map data © <a href="https://www.openstreetmap.org/copyright" rel="noopener noreferrer"{_goat_click_attrs("https://www.openstreetmap.org/copyright")}>OpenStreetMap</a></p>
    </div>
  </section>
  <section class="section" aria-labelledby="list-heading" style="padding-top:0">
    <div class="wrap">
      <div class="section-head">
        <div class="section-intro">
          <p class="kicker">The list</p>
          <h2 id="list-heading">Places</h2>
        </div>
      </div>
      {list_html}
    </div>
  </section>
</main>
{footer(prefix, extra_js)}
<script type="application/json" id="hotel-map-data">{map_json}</script>
</body>
</html>"""


def _hotel_card(r: dict, index: int, prefix: str) -> str:
    # Same card markup as restaurants, with hotel IDs so the shared map script can focus a pin.
    html = _restaurant_card(r, index, prefix, link_kind="hotel")
    html = html.replace('class="restaurant-card has-photo"', 'class="restaurant-card hotel-card has-photo"', 1)
    html = html.replace('class="restaurant-card"', 'class="restaurant-card hotel-card"', 1)
    html = html.replace('id="restaurant-', 'id="hotel-', 1)
    html = html.replace("data-restaurant-focus=", "data-hotel-focus=", 1)
    return html


def page_privacy() -> str:
    prefix = ""
    desc = (
        "Totin My Pack uses GoatCounter to count visits. It does not use cookies "
        "or collect personal data, and there is no email signup or contact form."
    )
    goat_privacy = "https://www.goatcounter.com/help/privacy"
    return f"""{head("Privacy — Totin My Pack", desc, "/privacy.html", "logo", prefix, og_logo=True)}
<body>
<a class="skip-link" href="#content">Skip to content</a>
{nav(prefix, "privacy")}
<main id="content">
  <section class="page-hero" aria-label="Privacy">
    <div class="hero-shade" aria-hidden="true"></div>
    <div class="hero-copy">
      <h1>Privacy</h1>
    </div>
  </section>
  <section class="section">
    <div class="wrap">
      <div class="prose">
        <p class="lead">This site uses GoatCounter to count visits. It does not have an email signup or a contact form.</p>
        <p>GoatCounter is a privacy-friendly analytics service. Its own documentation says it does not track personal data: it does not store cookies, localStorage, or other data in your browser; it does not store IP addresses or a tracker ID; and it does not share information with third parties. It is not used here for advertising. You can read GoatCounter’s <a href="{goat_privacy}" rel="noopener noreferrer"{_goat_click_attrs(goat_privacy)}>privacy documentation</a>.</p>
        <p>Visit counts for this site are public and can be read without signing in.</p>
        <p>Pages on this site link out to YouTube, and to restaurant and hotel websites, when those addresses are listed.</p>
      </div>
    </div>
  </section>
</main>
{footer(prefix)}
</body>
</html>"""


def _gear_data() -> dict:
    path = ROOT / "data" / "gear.json"
    return json.loads(path.read_text(encoding="utf-8"))


def page_gear() -> str:
    prefix = ""
    data = _gear_data()
    intro = (data.get("intro") or "").strip()
    intro_html = f'<p class="trip-simple-intro">{esc(intro)}</p>' if intro else ""
    sections = []
    for group in data.get("groups") or []:
        rows = []
        for item in group.get("items") or []:
            name = item.get("name") or ""
            note = (item.get("note") or "").strip()
            note_html = f'<span class="trip-where-place">{esc(note)}</span>' if note else ""
            rows.append(
                f'<li><span class="trip-where-name">{esc(name)}</span>{note_html}</li>'
            )
        if not rows:
            continue
        gid = esc(group.get("id") or "")
        heading = esc(group.get("name") or "")
        sections.append(
            f'<section class="trip-where" aria-labelledby="gear-{gid}">'
            f'<h2 id="gear-{gid}">{heading}</h2>'
            f'<ul>{"".join(rows)}</ul></section>'
        )
    desc = data.get("description") or data.get("intro") or data["title"]
    return f"""{head(data["title"] + " — Totin My Pack", desc, "/gear.html", "logo", prefix, og_logo=True)}
<body class="trip-simple-page gear-page">
<a class="skip-link" href="#content">Skip to content</a>
{nav(prefix, "gear")}
<main id="content">
  <article class="trip-simple">
    <header class="trip-simple-head">
      <h1>{esc(data["title"])}</h1>
      {intro_html}
    </header>
    {"".join(sections)}
  </article>
</main>
{footer(prefix)}
</body>
</html>"""


def robots_and_sitemap() -> None:


    pages = [
        "/",
        "/destinations/",
        "/videos.html",
        "/shorts.html",
        "/restaurants.html",
        "/hotels.html",
        "/about.html",
        "/privacy.html",
        "/gear.html",
        "/trips/",
    ] + [f"/trips/{slug}.html" for slug in _trip_slugs()] + [
        f"/destinations/{d['slug']}.html" for d in DESTINATIONS
    ]
    (ROOT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n",
        encoding="utf-8",
    )
    urls = "\n".join(
        f"  <url><loc>{SITE}{p}</loc></url>" for p in pages
    )
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}\n</urlset>\n",
        encoding="utf-8",
    )
    print("wrote robots.txt and sitemap.xml")



def page_404() -> str:
    prefix = "/"
    desc = "This page could not be found on Totin My Pack."
    return f"""{head("Page not found — Totin My Pack", desc, "/404.html", "logo", prefix, og_logo=True)}
<body>
<a class="skip-link" href="#content">Skip to content</a>
{nav(prefix, "")}
<main id="content">
  <section class="page-hero" aria-label="Page not found">
    <div class="hero-shade" aria-hidden="true"></div>
    <div class="hero-copy">
      <p class="kicker">404</p>
      <h1>Page not found</h1>
      <p class="lede">That address is not a page on this site.</p>
      <div class="hero-actions">
        <a class="btn btn-gold" href="/index.html">Home</a>
        <a class="btn btn-ghost" href="/videos.html">Films</a>
        <a class="btn btn-ghost" href="/trips/index.html">Trips</a>
      </div>
    </div>
  </section>
</main>
{footer(prefix)}
</body>
</html>"""


def main() -> None:
    ensure_hero_images()
    write(ROOT / "index.html", page_home())
    write(ROOT / "destinations" / "index.html", page_destinations_index())
    for d in DESTINATIONS:
        write(ROOT / "destinations" / f"{d['slug']}.html", page_destination(d))
    write(ROOT / "videos.html", page_videos())
    write(ROOT / "shorts.html", page_shorts())
    write(ROOT / "about.html", page_about())
    write(ROOT / "privacy.html", page_privacy())
    write(ROOT / "gear.html", page_gear())
    write(ROOT / "restaurants.html", page_restaurants())
    write(ROOT / "hotels.html", page_hotels())
    write(ROOT / "404.html", page_404())
    shutil.copyfile(ROOT / "assets" / "favicon.ico", ROOT / "favicon.ico")
    write(ROOT / "trips" / "index.html", page_trips_index())
    for slug in _trip_slugs():
        write(ROOT / "trips" / f"{slug}.html", page_trip(slug))
    robots_and_sitemap()
    ids = [v["id"] for v in VIDEOS]
    assert len(ids) == len(set(ids)), "duplicate video ids"
    print(f"OK — {len(ids)} unique videos")


if __name__ == "__main__":
    main()

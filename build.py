#!/usr/bin/env python3
"""Generate the Totin My Pack static site."""
from __future__ import annotations

import html
import json
import shutil
import unicodedata
from collections import OrderedDict
from pathlib import Path
from urllib.parse import quote, urlparse

ROOT = Path(__file__).resolve().parent
SITE = "https://totinmypack.com"
CHANNEL = "https://youtube.com/@totinmypack"
PLAYLIST = "https://www.youtube.com/playlist?list=PLVqSQzmPjiMw"
CHANNEL_DESC = (
    "Travel with Totin My Pack through Greece and across the United States. "
    "We share short travel films, scenic drives, state parks, historic places, "
    "and personal memories from our trips."
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
    return f"https://i.ytimg.com/vi/{vid}/{name}.jpg"


def thumb_srcset(
    vid: str,
    *,
    sizes: str = "(max-width: 700px) 92vw, (max-width: 1100px) 45vw, 400px",
) -> str:
    """Card thumbnails: hqdefault as the default, with a srcset of smaller and larger YouTube stills."""
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
      <img {thumb_srcset(v['id'])} alt="{alt}" loading="{loading}" decoding="async"{fetch}>
      {play_icon()}
      {f'<span class="chip">{esc(v["length"])}</span>' if v.get("length") else ""}
    </span>
    <span class="film-meta">
      <span class="film-title">{esc(v['title'])}</span>
      <span class="film-sub">{esc(v['date'])} · {'Short' if kind == 'short' else 'Film'}</span>
    </span>
  </button>
</article>"""


def nav(prefix: str, current: str) -> str:
    def cur(name: str) -> str:
        return ' aria-current="page"' if current == name else ""

    dest_links = "\n".join(
        f'          <li><a href="{prefix}destinations/{d["slug"]}.html"{cur("dest-"+d["slug"])}>{esc(d["name"])}</a></li>'
        for d in DESTINATIONS
    )
    return f"""
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
        <li><a href="{prefix}index.html"{cur("home")}>Home</a></li>
        <li class="has-sub">
          <button class="nav-label" type="button" aria-expanded="false">Destinations</button>
          <ul class="subnav">
            <li><a href="{prefix}destinations/index.html"{cur("dest")}>All destinations</a></li>
{dest_links}
          </ul>
        </li>
        <li><a href="{prefix}trips/index.html"{cur("trips")}>Trips</a></li>
        <li><a href="{prefix}videos.html"{cur("videos")}>Films</a></li>
        <li><a href="{prefix}shorts.html"{cur("shorts")}>Shorts</a></li>
        <li><a href="{prefix}restaurants.html"{cur("restaurants")}>Restaurants</a></li>
        <li><a href="{prefix}about.html"{cur("about")}>About</a></li>
      </ul>
      <a class="btn btn-gold nav-cta" href="{CHANNEL}" rel="noopener noreferrer">Subscribe on YouTube</a>
    </nav>
  </div>
</header>"""


def footer(prefix: str, extra_js: str = "") -> str:
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
    <nav class="footer-nav" aria-label="Footer">
      <a href="{prefix}destinations/index.html">Destinations</a>
      <a href="{prefix}trips/index.html">Trips</a>
      <a href="{prefix}videos.html">Films</a>
      <a href="{prefix}shorts.html">Shorts</a>
      <a href="{prefix}restaurants.html">Restaurants</a>
      <a href="{prefix}about.html">About</a>
      <a href="{CHANNEL}" rel="noopener noreferrer">YouTube</a>
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
{extra_js}"""


def head(title: str, description: str, path: str, og_id: str, prefix: str, extra: str = "", og_logo: bool = False, robots: str | None = None) -> str:
    canon = SITE + path
    if og_logo or og_id == "logo":
        image = f"{SITE}/assets/og-image.jpg"
        og_w, og_h = 1200, 630
    else:
        image = thumb(og_id)
        og_w, og_h = 1280, 720
    robots_tag = (
        f'  <meta name="robots" content="{esc(robots)}">\n' if robots else ""
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
  <link rel="preload" href="{prefix}assets/fonts/outfit-latin.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="{prefix}assets/fonts/fraunces-italic-latin.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preconnect" href="https://i.ytimg.com">
  <link rel="stylesheet" href="{prefix}css/styles.css">
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
        dest_cards.append(
            f"""
<a class="dest-card" href="destinations/{slug}.html">
  <img {thumb_srcset(img, sizes="(max-width: 560px) 92vw, (max-width: 900px) 45vw, 380px")} alt="{esc(name)}" loading="lazy" decoding="async">
  <span class="dest-copy">
    <h3>{esc(name)}</h3>
    <p>{esc(label)}</p>
  </span>
</a>"""
        )
    return f"""{head("Totin My Pack — Travel films from Greece and the United States", CHANNEL_DESC, "/", "logo", prefix, json_ld_home(), og_logo=True)}
<body>
<a class="skip-link" href="#content">Skip to content</a>
{nav(prefix, "home")}
<main id="content">
  <section class="hero" aria-label="Introduction">
    <div class="hero-media">
      <img src="{thumb(HERO_ID)}" alt="Autumn cypress trees and moss reflected in still water at Caddo Lake, East Texas, from the film Caddo Lake in Fall." width="1280" height="720" fetchpriority="high" decoding="async">
    </div>
    <div class="hero-shade" aria-hidden="true"></div>
    <div class="hero-copy">
      <p class="kicker">Travel films</p>
      <h1>Totin My Pack</h1>
      <p class="lede">{esc(CHANNEL_DESC)}</p>
      <div class="hero-actions">
        <a class="btn btn-gold" href="#start-here">Start here</a>
        <a class="btn btn-ghost" href="{CHANNEL}" rel="noopener noreferrer">Subscribe on YouTube</a>
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
        <a class="link-arrow" href="{PLAYLIST}" rel="noopener noreferrer">Play all on YouTube</a>
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
      <div class="dest-grid">
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
    <a class="btn btn-gold" href="{CHANNEL}" rel="noopener noreferrer">Subscribe on YouTube</a>
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
  <img {thumb_srcset(d['hero'], sizes="(max-width: 560px) 92vw, (max-width: 900px) 45vw, 380px")} alt="{esc(d['name'])}" loading="lazy" decoding="async">
  <span class="dest-copy">
    <h2>{esc(d['name'])}</h2>
    <p>{n} {'film' if n == 1 else 'films'}</p>
  </span>
</a>"""
        )
    desc = "Browse Totin My Pack travel films by place: Greece, Texas, Dallas, Route 66, the Plains, the Southeast, California, the Southwest, and Berlin."
    return f"""{head("Destinations — Totin My Pack", desc, "/destinations/", "logo", prefix, og_logo=True)}
<body>
<a class="skip-link" href="#content">Skip to content</a>
{nav(prefix, "dest")}
<main id="content">
  <section class="page-hero" aria-label="Destinations">
    <div class="hero-media">
      <img src="{thumb('3cFk5Tf7nOg')}" alt="Autumn forest and ridgelines along the Talimena Scenic Byway." width="1280" height="720" fetchpriority="high" decoding="async" style="object-position:78% 45%">
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
    film_cards = "".join(film_card(v, featured=(i == 0), lazy=(i != 0)) for i, v in enumerate(films))
    short_cards = "".join(film_card(v, lazy=True) for v in shorts)
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
    desc = d["blurb"]
    style = f'style="object-position:{d["hero_pos"]}"'
    return f"""{head(title, desc, f"/destinations/{d['slug']}.html", d["og"], prefix)}
<body>
<a class="skip-link" href="#content">Skip to content</a>
{nav(prefix, "dest-"+d["slug"])}
<main id="content">
  <section class="page-hero" aria-label="{esc(d['name'])}">
    <div class="hero-media">
      <img src="{thumb(d['hero'])}" alt="{esc(d.get('hero_alt') or d['name'])}" width="1280" height="720" fetchpriority="high" decoding="async" {style}>
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
    <a class="btn btn-gold" href="{CHANNEL}" rel="noopener noreferrer">Subscribe on YouTube</a>
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
    return f"""{head("Films — Totin My Pack", desc, "/videos.html", "logo", prefix, og_logo=True)}
<body>
<a class="skip-link" href="#content">Skip to content</a>
{nav(prefix, "videos")}
<main id="content">
  <section class="page-hero" aria-label="Films">
    <div class="hero-media">
      <img src="{thumb('p9PXuj51NJs')}" alt="Turquoise water of the Devils River in West Texas, seen from above." width="1280" height="720" fetchpriority="high" decoding="async" style="object-position:80% 50%">
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
      <img src="{thumb('2f-wKhlW_PE')}" alt="" width="1280" height="720" fetchpriority="high" decoding="async" style="object-position:70% 40%">
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
    <a class="btn btn-gold" href="{CHANNEL}" rel="noopener noreferrer">Subscribe on YouTube</a>
  </section>
</main>
{footer(prefix)}
</body>
</html>"""


def page_about() -> str:
    prefix = ""
    totin = "https://www.youtube.com/@totinmypack"
    unscripted = "https://www.youtube.com/@TeddyUnscripted"
    desc = (
        "Teddy (Theodore) films his trips under the name Totin My Pack. "
        "A draft about page, for him to personalize."
    )
    return f"""{head("About — Totin My Pack", desc, "/about.html", "logo", prefix, og_logo=True)}
<body>
<a class="skip-link" href="#content">Skip to content</a>
{nav(prefix, "about")}
<main id="content">
  <section class="page-hero" aria-label="About">
    <div class="hero-media">
      <img src="{thumb('is4VhiJbrPU')}" alt="" width="1280" height="720" fetchpriority="high" decoding="async" style="object-position:60% 40%">
    </div>
    <div class="hero-shade" aria-hidden="true"></div>
    <div class="hero-copy">
      <p class="kicker">A draft</p>
      <h1>About</h1>
    </div>
  </section>
  <section class="section">
    <div class="wrap">
      <div class="draft-banner" role="status">
        <p><strong>Draft.</strong> This page is a starting point only. Please replace it with your own words when you are ready.</p>
      </div>
      <div class="prose">
        <p class="lead">Teddy (Theodore) films his trips under the name Totin My Pack.</p>
        <p>The films follow places in Greece and the United States. They are published on two YouTube channels:</p>
        <ul>
          <li><a href="{totin}" rel="noopener noreferrer">Totin My Pack</a> — @totinmypack</li>
          <li><a href="{unscripted}" rel="noopener noreferrer">Teddy Unscripted</a> — @TeddyUnscripted</li>
        </ul>
        <p class="about-actions">
          <a class="btn btn-gold" href="{totin}" rel="noopener noreferrer">Totin My Pack on YouTube</a>
          <a class="btn btn-ghost" href="{unscripted}" rel="noopener noreferrer">Teddy Unscripted</a>
        </p>
      </div>
    </div>
  </section>
</main>
{footer(prefix)}
</body>
</html>"""


def _trip_slugs() -> list[str]:
    names = [p.stem for p in (ROOT / "data" / "trips").glob("*.json")]
    preferred = ["route-66", "greece"]
    ordered = [s for s in preferred if s in names]
    ordered += sorted(s for s in names if s not in ordered)
    return ordered


def _trip_data(slug: str) -> dict:
    path = ROOT / "data" / "trips" / f"{slug}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def page_trips_index() -> str:
    prefix = "../"
    trips = [_trip_data(slug) for slug in _trip_slugs()]
    desc = "Travel journeys from Totin My Pack, from the places named in the films — including Route 66 and Greece."
    cards = []
    for trip in trips:
        n_stops = sum(1 for s in trip["stops"] if s.get("on_map"))
        blurb = trip.get("index_blurb") or (f"{n_stops} filmed stops" if n_stops else "Filmed places")
        if not trip.get("index_blurb") and n_stops:
            blurb = f"{n_stops} filmed stops"
        cards.append(
            f'<a class="dest-card" href="{esc(trip["slug"])}.html">'
            f'<img {thumb_srcset(trip["hero"], sizes="(max-width: 560px) 92vw, 45vw")} '
            f'alt="{esc(trip.get("hero_alt") or trip["name"])}" loading="lazy" decoding="async">'
            f'<span class="dest-copy"><h2>{esc(trip["name"])}</h2>'
            f"<p>{esc(blurb)}</p></span></a>"
        )
    hero = trips[0]
    return f"""{head("Trips — Totin My Pack", desc, "/trips/", "logo", prefix, og_logo=True)}
<body>
<a class="skip-link" href="#content">Skip to content</a>
{nav(prefix, "trips")}
<main id="content">
  <section class="page-hero" aria-label="Trips">
    <div class="hero-media">
      <img src="{thumb(hero['hero'])}" alt="{esc(hero.get('hero_alt') or hero['name'])}" width="1280" height="720" fetchpriority="high" decoding="async" style="object-position:{esc(hero.get('hero_pos') or '50% 50%')}">
    </div>
    <div class="hero-shade" aria-hidden="true"></div>
    <div class="hero-copy">
      <p class="kicker">Journeys</p>
      <h1>Trips</h1>
      <p class="lede">Films arranged as a journey, one road at a time, from the places named in the videos.</p>
    </div>
  </section>
  <section class="section">
    <div class="wrap">
      <div class="trips-list dest-grid">
        {''.join(cards)}
      </div>
    </div>
  </section>
</main>
{footer(prefix)}
</body>
</html>"""


def _stop_photo(stop: dict, prefix: str) -> str | None:
    photo = (stop.get("photo") or "").strip()
    if not photo:
        return None
    return f"{prefix}assets/{photo}"


def _then_and_now(stop: dict) -> dict | None:
    raw = stop.get("then_and_now") or {}
    text = (raw.get("text") or "").strip()
    if not text:
        return None
    out = {"text": text}
    if raw.get("source_name"):
        out["source_name"] = raw["source_name"]
    if raw.get("source_url"):
        out["source_url"] = raw["source_url"]
    return out


def _then_and_now_html(stop: dict) -> str:
    info = _then_and_now(stop)
    if not info:
        return ""
    src = ""
    if info.get("source_url") and info.get("source_name"):
        src = (
            f'<p class="trip-then-source">Source: '
            f'<a href="{esc(info["source_url"])}" rel="noopener noreferrer">'
            f"{esc(info['source_name'])}</a></p>"
        )
    return (
        f'<div class="trip-then">'
        f'<p class="trip-then-label">Then and now</p>'
        f"<p>{esc(info['text'])}</p>{src}</div>"
    )


def _stop_videos(stop: dict) -> list[dict]:
    out = []
    for vid in stop.get("videos") or []:
        v = BY_ID.get(vid)
        if v:
            out.append({"id": v["id"], "title": v["title"], "kind": v["kind"]})
    return out


def _watch_label(v: dict, videos: list, trip: dict) -> str:
    if len(videos) == 1:
        return "Watch the Short" if v["kind"] == "short" else "Watch the film"
    short_title = v["title"].split(" | ")[0]
    if v["kind"] == "short":
        return short_title
    if v["id"] == trip.get("overview_film") and trip.get("overview_watch_label"):
        return trip["overview_watch_label"]
    return short_title


def _photo_strip(trip: dict, prefix: str) -> str:
    items = []
    for s in trip["stops"]:
        src = _stop_photo(s, prefix)
        if not src:
            continue
        num = s.get("number")
        label = f"{num}. {s['name']}" if num else s["name"]
        items.append(
            "<li>"
            f'<button type="button" class="trip-photo" data-stop-play="{esc(s["id"])}">'
            f'<img src="{esc(src)}" alt="{esc(s["name"])}" width="480" height="270" '
            f'loading="lazy" decoding="async">'
            f"<span>{esc(label)}</span></button></li>"
        )
    if not items:
        return ""
    return (
        '<div class="trip-photos" id="trip-photos">'
        '<p class="trip-photos-label">Stills from the films</p>'
        f'<ul class="trip-photos-list">{"".join(items)}</ul></div>'
    )


def page_trip(slug: str) -> str:
    prefix = "../"
    trip = _trip_data(slug)
    number = 0
    for stop in trip["stops"]:
        if stop.get("on_map"):
            number += 1
            stop["number"] = number
        else:
            stop["number"] = None

    map_payload = {
        "route": trip.get("route") or [],
        "spur": trip.get("spur") or [],
        "maxZoom": trip.get("map_max_zoom") or 7,
        "stops": [
            {
                "id": s["id"],
                "name": s["name"],
                "place": s.get("place") or "",
                "lat": s.get("lat"),
                "lon": s.get("lon"),
                "on_map": bool(s.get("on_map")),
                "spur": bool(s.get("spur")),
                "number": s.get("number"),
                "videos": _stop_videos(s),
                **({"start_seconds": int(s["start_seconds"])} if s.get("start_seconds") else {}),
                **({"then_and_now": _then_and_now(s)} if _then_and_now(s) else {}),
                **({"photo": _stop_photo(s, prefix)} if _stop_photo(s, prefix) else {}),
            }
            for s in trip["stops"]
        ],
    }
    map_json = json.dumps(map_payload, ensure_ascii=False)
    intro = "".join(f"<p>{esc(p)}</p>" for p in trip.get("intro") or [])
    overview = BY_ID[trip["overview_film"]] if trip.get("overview_film") in BY_ID else None

    seen: list[str] = []
    if trip.get("overview_film"):
        seen.append(trip["overview_film"])
    for s in trip["stops"]:
        for vid in s.get("videos") or []:
            if vid not in seen:
                seen.append(vid)
    group = trip.get("video_group")
    if group:
        for v in VIDEOS:
            if group in v["groups"] and v["id"] not in seen:
                seen.append(v["id"])
    film_cards = "".join(film_card(BY_ID[i], lazy=True) for i in seen if i in BY_ID)

    by_state: dict[str, list] = {}
    for s in trip["stops"]:
        by_state.setdefault(s["state"], []).append(s)

    state_blocks = []
    for state in trip["states"]:
        rows = []
        for s in by_state.get(state["id"], []):
            videos = _stop_videos(s)
            primary = videos[0] if videos else None
            thumb_id = s.get("thumb") or (primary["id"] if primary else trip["hero"])
            photo_src = _stop_photo(s, prefix)
            num = s.get("number")
            if num:
                num_html = f'<span class="trip-stop-num" aria-hidden="true">{num}</span>'
            else:
                num_html = '<span class="trip-stop-num is-off" aria-hidden="true">–</span>'
            note = f'<p>{esc(s["note"])}</p>' if s.get("note") else ""
            then_html = _then_and_now_html(s)
            locate_id = s["id"] if s.get("on_map") else s.get("focus")
            locate = ""
            if locate_id:
                locate = (
                    f'<button type="button" class="trip-stop-locate" data-stop-focus="{esc(locate_id)}">'
                    "Show on the map</button>"
                )
            watch_btns = []
            for v in videos:
                label = _watch_label(v, videos, trip)
                watch_btns.append(
                    "<li>"
                    f'<button type="button" class="trip-watch" data-video-id="{esc(v["id"])}" '
                    f'data-title="{esc(v["title"])}" data-kind="{esc(v["kind"])}">{esc(label)}</button>'
                    "</li>"
                )
            watch = f'<ul class="trip-watch-list">{"".join(watch_btns)}</ul>' if watch_btns else ""
            if photo_src:
                img = (
                    f'<img src="{esc(photo_src)}" alt="" width="480" height="270" loading="lazy" '
                    f'decoding="async">'
                )
            else:
                img = (
                    f'<img {thumb_srcset(thumb_id)} alt="" loading="lazy" decoding="async">'
                )
            if primary:
                thumb_btn = (
                    f'<button class="trip-stop-thumb" type="button" data-video-id="{esc(primary["id"])}" '
                    f'data-title="{esc(primary["title"])}" data-kind="{esc(primary["kind"])}" '
                    f'aria-label="Play {esc(primary["title"])}">'
                    f"{img}{play_icon()}</button>"
                )
            else:
                thumb_btn = f'<div class="trip-stop-thumb">{img}</div>'
            sep = " is-separate" if (s.get("separate") or not s.get("on_map")) else ""
            rows.append(
                f'<article class="trip-stop{sep}" id="stop-{esc(s["id"])}">'
                f"{thumb_btn}<div class=\"trip-stop-copy\">"
                f"<h3>{num_html}{esc(s['name'])}</h3>"
                f'<p class="trip-stop-place">{esc(s.get("place") or "")}</p>'
                f"{note}{then_html}{watch}{locate}</div></article>"
            )
        state_note = f'<p>{esc(state["note"])}</p>' if state.get("note") else ""
        state_blocks.append(
            f'<div class="trip-state" id="leg-{esc(state["id"])}">'
            f'<div class="trip-state-head"><p class="kicker">{esc(state.get("kicker") or "")}</p>'
            f"<h2>{esc(state['name'])}</h2>{state_note}</div>"
            f"{''.join(rows)}</div>"
        )

    legend_bits = []
    for item in trip.get("legend") or [{"type": "pin", "label": "Filmed place"}]:
        cls = {"pin": "trip-legend-pin", "line": "trip-legend-line", "spur": "trip-legend-spur"}.get(item["type"], "trip-legend-pin")
        legend_bits.append(
            f'<li><span class="{cls}" aria-hidden="true"></span> {esc(item["label"])}</li>'
        )
    legend = f'<ul class="trip-legend">{"".join(legend_bits)}</ul>' if legend_bits else ""

    dest_slug = trip.get("dest_slug") or slug
    dest_label = trip.get("dest_label") or "All films"
    dest_link = f'<a class="link-arrow" href="{prefix}destinations/{esc(dest_slug)}.html">{esc(dest_label)}</a>'
    watch_btn = ""
    if overview:
        watch_btn = (
            f'<button class="btn btn-ghost" type="button" data-video-id="{esc(overview["id"])}" '
            f'data-title="{esc(overview["title"])}" data-kind="{esc(overview["kind"])}">Watch the film</button>'
        )
    extra_js = f'<script src="{prefix}js/trip-map.js" defer></script>'
    style = f'style="object-position:{esc(trip.get("hero_pos") or "50% 50%")}"'
    map_aria = trip.get("map_aria") or f"Map of filmed places in {trip['name']}"
    return f"""{head(trip["title"] + " — Totin My Pack", trip["description"], f"/trips/{slug}.html", trip["hero"], prefix)}
<body>
<a class="skip-link" href="#content">Skip to content</a>
{nav(prefix, "trips")}
<main id="content">
  <section class="page-hero" aria-label="{esc(trip['name'])}">
    <div class="hero-media">
      <img src="{thumb(trip['hero'])}" alt="{esc(trip.get('hero_alt') or trip['name'])}" width="1280" height="720" fetchpriority="high" decoding="async" {style}>
    </div>
    <div class="hero-shade" aria-hidden="true"></div>
    <div class="hero-copy">
      <p class="kicker">{esc(trip.get("kicker") or "A journey")}</p>
      <h1>{esc(trip["name"])}</h1>
      <p class="lede">{esc(trip.get("lede") or "")}</p>
      <div class="hero-actions">
        <a class="btn btn-gold" href="#trip-map">View the map</a>
        {watch_btn}
      </div>
    </div>
  </section>
  <section class="section trip-map-section" aria-labelledby="map-heading">
    <div class="wrap">
      <div class="section-head">
        <div class="section-intro">
          <p class="kicker">{esc(trip.get("map_kicker") or "The places")}</p>
          <h2 id="map-heading">{esc(trip.get("map_heading") or "The places they filmed")}</h2>
          {intro}
        </div>
        {dest_link}
      </div>
      <div class="trip-map-frame">
        <div id="trip-map" class="trip-map" role="region" aria-label="{esc(map_aria)}">
          <p class="trip-map-placeholder">The map loads when you scroll to it. The stops are listed below.</p>
        </div>
      </div>
      <p class="map-attrib">Map data © <a href="https://www.openstreetmap.org/copyright" rel="noopener noreferrer">OpenStreetMap</a></p>
      <div class="trip-tour" id="trip-tour" hidden>
        <button type="button" class="btn btn-ghost trip-tour-btn" id="trip-tour-prev" disabled>Previous stop</button>
        <p class="trip-tour-status" id="trip-tour-status" aria-live="polite">Step through the stops</p>
        <button type="button" class="btn btn-gold trip-tour-btn" id="trip-tour-next">Next stop</button>
      </div>
      {_photo_strip(trip, prefix)}
      {legend}
    </div>
  </section>
  <section class="section" aria-labelledby="legs-heading" style="padding-top:0">
    <div class="wrap">
      <div class="section-head">
        <div class="section-intro">
          <p class="kicker">{esc(trip.get("legs_kicker") or "")}</p>
          <h2 id="legs-heading">{esc(trip.get("legs_heading") or "Stop by stop")}</h2>
        </div>
      </div>
      {"".join(state_blocks)}
    </div>
  </section>
  <section class="section" aria-labelledby="trip-films-heading" style="padding-top:0">
    <div class="wrap">
      <div class="section-head">
        <div class="section-intro">
          <p class="kicker">{esc(trip.get("films_kicker") or "The films")}</p>
          <h2 id="trip-films-heading">{esc(trip.get("films_heading") or "Watch along the way")}</h2>
        </div>
      </div>
      <div class="film-grid">
        {film_cards}
      </div>
    </div>
  </section>
</main>
{footer(prefix, extra_js)}
<script type="application/json" id="trip-map-data">{map_json}</script>
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


def _external_link(href: str, label: str, aria: str) -> str:
    return (
        f'<a href="{esc(href)}" target="_blank" rel="noopener noreferrer" '
        f'aria-label="{esc(aria)}">{esc(label)}</a>'
    )


def _restaurant_card(r: dict, index: int, prefix: str) -> str:
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
            _external_link(r["website"], "Website", f"Website for {name}")
        )
    directions = _directions_url(r)
    if directions:
        actions.append(
            _external_link(directions, "Directions", f"Directions to {name}")
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
            f"<li>{_external_link(s, _source_label(s), f'Source for {name}: {_source_label(s)}')}</li>"
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
    return (
        f'<article class="restaurant-card" id="restaurant-{rid}">'
        f"<h4>{esc(name)}</h4>"
        f"{place_html}{listed_html}{cuisine}{address}{status_html}{loc_html}{note}{visited}{actions_html}{sources_html}"
        "</article>"
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
    desc = "Places we’ve eaten and liked along the way."
    return f"""{head(title, desc, "/restaurants.html", "logo", prefix, og_logo=True)}
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
        <div id="restaurant-map" class="trip-map" role="region" aria-label="Map of restaurants">
          <p class="trip-map-placeholder">The map loads when you scroll to it. The list is below.</p>
        </div>
      </div>
      <p class="map-attrib">Map data © <a href="https://www.openstreetmap.org/copyright" rel="noopener noreferrer">OpenStreetMap</a></p>
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
    desc = (
        "A draft page of unique, independent places we have stayed, "
        "grouped by place and shown on a map."
    )
    return f"""{head(title, desc, "/hotels.html", "logo", prefix, og_logo=True, robots="noindex")}
<body>
<a class="skip-link" href="#content">Skip to content</a>
{nav(prefix, "")}
<main id="content">
  <section class="page-hero" aria-label="Hotels">
    <div class="hero-shade" aria-hidden="true"></div>
    <div class="hero-copy">
      <p class="kicker">A draft</p>
      <h1>Hotels</h1>
      <p class="lede">Unique, independent places we have stayed, shown on a map the same way as the restaurants.</p>
      <div class="hero-actions">
        <a class="btn btn-gold" href="#hotel-map">View the map</a>
      </div>
    </div>
  </section>
  <section class="section restaurant-map-section" aria-labelledby="map-heading">
    <div class="wrap">
      <div class="draft-banner" role="status">
        <p><strong>Draft.</strong> This page is a starting point only. It is not in the menu yet, and it will stay out of search results until the list is ready.</p>
      </div>
      <div class="section-head">
        <div class="section-intro">
          <p class="kicker">The places</p>
          <h2 id="map-heading">The map</h2>
          <p>When hotels are added, each pin will sit at the stay’s true location. Places without a precise point will stay in the list without a pin.</p>
        </div>
      </div>
      <div class="trip-map-frame restaurant-map-frame">
        <div id="hotel-map" class="trip-map" role="region" aria-label="Map of hotels">
          <p class="trip-map-placeholder">The map loads when you scroll to it. The list is below.</p>
        </div>
      </div>
      <p class="map-attrib">Map data © <a href="https://www.openstreetmap.org/copyright" rel="noopener noreferrer">OpenStreetMap</a></p>
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
    html = _restaurant_card(r, index, prefix)
    html = html.replace('class="restaurant-card"', 'class="restaurant-card hotel-card"', 1)
    html = html.replace('id="restaurant-', 'id="hotel-', 1)
    html = html.replace("data-restaurant-focus=", "data-hotel-focus=", 1)
    return html


def robots_and_sitemap() -> None:
    pages = [
        "/",
        "/destinations/",
        "/videos.html",
        "/shorts.html",
        "/restaurants.html",
        "/about.html",
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
    write(ROOT / "index.html", page_home())
    write(ROOT / "destinations" / "index.html", page_destinations_index())
    for d in DESTINATIONS:
        write(ROOT / "destinations" / f"{d['slug']}.html", page_destination(d))
    write(ROOT / "videos.html", page_videos())
    write(ROOT / "shorts.html", page_shorts())
    write(ROOT / "about.html", page_about())
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

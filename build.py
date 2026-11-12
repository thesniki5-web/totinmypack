#!/usr/bin/env python3
"""Generate the Totin My Pack static site."""
from __future__ import annotations

import html
import json
from pathlib import Path

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




def thumb(vid: str) -> str:
    return f"https://i.ytimg.com/vi/{vid}/maxresdefault.jpg"


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
      <img src="{thumb(v['id'])}" alt="{alt}" width="1280" height="720" loading="{loading}" decoding="async"{fetch} data-fallback="{esc(v['id'])}">
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
      <img src="{prefix}assets/icon-512.png" width="512" height="512" alt="">
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
      <img src="{prefix}assets/icon-512.png" width="512" height="512" alt="">
      <span class="logo-text">Totin&nbsp;<span>My Pack</span></span>
    </a>
      <p>Short travel films from Greece and the United States.</p>
    </div>
    <nav class="footer-nav" aria-label="Footer">
      <a href="{prefix}destinations/index.html">Destinations</a>
      <a href="{prefix}trips/index.html">Trips</a>
      <a href="{prefix}videos.html">Films</a>
      <a href="{prefix}shorts.html">Shorts</a>
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
</dialog>
<script src="{prefix}js/main.js" defer></script>
{extra_js}"""


def head(title: str, description: str, path: str, og_id: str, prefix: str, extra: str = "", og_logo: bool = False) -> str:
    canon = SITE + path
    if og_logo or og_id == "logo":
        image = f"{SITE}/assets/og-image.jpg"
        og_w, og_h = 1200, 630
    else:
        image = thumb(og_id)
        og_w, og_h = 1280, 720
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <link rel="canonical" href="{esc(canon)}">
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
  <link rel="shortcut icon" href="{prefix}assets/favicon.ico">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="preconnect" href="https://i.ytimg.com">
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,500;0,9..144,600;1,9..144,400;1,9..144,500&family=Outfit:wght@300;400;500;600&display=swap">
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
  <img src="{thumb(img)}" alt="{esc(name)}" width="1280" height="720" loading="lazy" decoding="async" data-fallback="{img}">
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
  <img src="{thumb(d['hero'])}" alt="{esc(d['name'])}" width="1280" height="720" loading="lazy" decoding="async" data-fallback="{d['hero']}">
  <span class="dest-copy">
    <h3>{esc(d['name'])}</h3>
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
    if d["slug"] == "route-66":
        trip_cta = (
            '<div class="hero-actions">'
            '<a class="btn btn-gold" href="../trips/route-66.html">Follow the journey on the map</a>'
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
    desc = CHANNEL_DESC
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
      <p class="kicker">The channel</p>
      <h1>About</h1>
    </div>
  </section>
  <section class="section">
    <div class="wrap">
      <div class="prose">
        <p class="lead">{esc(CHANNEL_DESC)}</p>
        <p>The channel began on September 24, 2022. The films are short — most run a few minutes — and follow scenic drives, state parks, historic places, and personal memories from the road.</p>
        <p>Places in the films include Halkidiki and a 2008 trip to Skopelos, Meteora, and Mount Olympus; Texas parks, churches, and river country; Dallas wildlife and weather, including the total solar eclipse of April 8, 2024; Route 66; the Ozarks and the Great Plains; the Southeast and Mid-Atlantic; California’s redwoods and coast; the Southwest; and a 2012 winter film of Berlin.</p>
        <p>Watch the films, and subscribe for new ones, on YouTube at <a href="{CHANNEL}" rel="noopener noreferrer">@totinmypack</a>.</p>
        <p style="margin-top:2rem"><a class="btn btn-gold" href="{CHANNEL}" rel="noopener noreferrer">Subscribe on YouTube</a></p>
      </div>
    </div>
  </section>
</main>
{footer(prefix)}
</body>
</html>"""


def _trip_data() -> dict:
    return json.loads((ROOT / "data" / "trips" / "route-66.json").read_text(encoding="utf-8"))


def page_trips_index() -> str:
    prefix = "../"
    trip = _trip_data()
    n_stops = sum(1 for s in trip["stops"] if s.get("on_map"))
    desc = (
        "Travel journeys from Totin My Pack, beginning with a Route 66 trip "
        "arranged east to west from the films."
    )
    card = (
        f'<a class="dest-card" href="route-66.html">'
        f'<img src="{thumb(trip["hero"])}" alt="{esc(trip.get("hero_alt") or trip["name"])}" '
        f'width="1280" height="720" loading="lazy" decoding="async" data-fallback="{trip["hero"]}">'
        f'<span class="dest-copy"><h3>{esc(trip["name"])}</h3>'
        f"<p>East to west, {n_stops} filmed stops</p></span></a>"
    )
    return f"""{head("Trips — Totin My Pack", desc, "/trips/", "logo", prefix, og_logo=True)}
<body>
<a class="skip-link" href="#content">Skip to content</a>
{nav(prefix, "trips")}
<main id="content">
  <section class="page-hero" aria-label="Trips">
    <div class="hero-media">
      <img src="{thumb(trip['hero'])}" alt="{esc(trip.get('hero_alt') or trip['name'])}" width="1280" height="720" fetchpriority="high" decoding="async" style="object-position:{esc(trip.get('hero_pos') or '50% 50%')}">
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
        {card}
      </div>
    </div>
  </section>
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


def _watch_label(v: dict, videos: list, overview_id: str) -> str:
    if len(videos) == 1:
        return "Watch the Short" if v["kind"] == "short" else "Watch the film"
    short_title = v["title"].split(" | ")[0]
    if v["kind"] == "short":
        return short_title
    if v["id"] == overview_id:
        return "East-to-west film"
    return short_title


def page_trip_route66() -> str:
    prefix = "../"
    trip = _trip_data()
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
            }
            for s in trip["stops"]
        ],
    }
    map_json = json.dumps(map_payload, ensure_ascii=False)
    intro = "".join(f"<p>{esc(p)}</p>" for p in trip["intro"])
    overview = BY_ID[trip["overview_film"]]

    seen: list[str] = []
    for vid in [trip["overview_film"]]:
        if vid not in seen:
            seen.append(vid)
    for s in trip["stops"]:
        for vid in s.get("videos") or []:
            if vid not in seen:
                seen.append(vid)
    for v in VIDEOS:
        if "route66" in v["groups"] and v["id"] not in seen:
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
            num = s.get("number")
            if num:
                num_html = f'<span class="trip-stop-num" aria-hidden="true">{num}</span>'
            else:
                num_html = '<span class="trip-stop-num is-off" aria-hidden="true">–</span>'
            note = f'<p>{esc(s["note"])}</p>' if s.get("note") else ""
            locate = ""
            if s.get("on_map"):
                locate = (
                    f'<button type="button" class="trip-stop-locate" data-stop-focus="{esc(s["id"])}">'
                    "Show on the map</button>"
                )
            watch_btns = []
            for v in videos:
                label = _watch_label(v, videos, trip["overview_film"])
                watch_btns.append(
                    "<li>"
                    f'<button type="button" class="trip-watch" data-video-id="{esc(v["id"])}" '
                    f'data-title="{esc(v["title"])}" data-kind="{esc(v["kind"])}">{esc(label)}</button>'
                    "</li>"
                )
            watch = f'<ul class="trip-watch-list">{"".join(watch_btns)}</ul>' if watch_btns else ""
            if primary:
                thumb_btn = (
                    f'<button class="trip-stop-thumb" type="button" data-video-id="{esc(primary["id"])}" '
                    f'data-title="{esc(primary["title"])}" data-kind="{esc(primary["kind"])}" '
                    f'aria-label="Play {esc(primary["title"])}">'
                    f'<img src="{thumb(thumb_id)}" alt="" width="480" height="300" loading="lazy" '
                    f'decoding="async" data-fallback="{esc(thumb_id)}">{play_icon()}</button>'
                )
            else:
                thumb_btn = (
                    f'<div class="trip-stop-thumb"><img src="{thumb(thumb_id)}" alt="" width="480" '
                    f'height="300" loading="lazy" decoding="async" data-fallback="{esc(thumb_id)}"></div>'
                )
            sep = " is-separate" if (s.get("separate") or not s.get("on_map")) else ""
            rows.append(
                f'<article class="trip-stop{sep}" id="stop-{esc(s["id"])}">'
                f"{thumb_btn}<div class=\"trip-stop-copy\">"
                f"<h3>{num_html}{esc(s['name'])}</h3>"
                f'<p class="trip-stop-place">{esc(s.get("place") or "")}</p>'
                f"{note}{watch}{locate}</div></article>"
            )
        state_note = f'<p>{esc(state["note"])}</p>' if state.get("note") else ""
        state_blocks.append(
            f'<div class="trip-state" id="leg-{esc(state["id"])}">'
            f'<div class="trip-state-head"><p class="kicker">{esc(state.get("kicker") or "")}</p>'
            f"<h2>{esc(state['name'])}</h2>{state_note}</div>"
            f"{''.join(rows)}</div>"
        )

    extra_js = f'<script src="{prefix}js/trip-map.js" defer></script>'
    style = f'style="object-position:{esc(trip.get("hero_pos") or "50% 50%")}"'
    return f"""{head(trip["title"] + " — Totin My Pack", trip["description"], "/trips/route-66.html", trip["hero"], prefix)}
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
      <p class="kicker">A journey</p>
      <h1>Route 66</h1>
      <p class="lede">One stop at a time, from Missouri to the Santa Monica Pier.</p>
      <div class="hero-actions">
        <a class="btn btn-gold" href="#trip-map">View the map</a>
        <button class="btn btn-ghost" type="button" data-video-id="{esc(overview['id'])}" data-title="{esc(overview['title'])}" data-kind="{esc(overview['kind'])}">Watch the film</button>
      </div>
    </div>
  </section>
  <section class="section trip-map-section" aria-labelledby="map-heading">
    <div class="wrap">
      <div class="section-head">
        <div class="section-intro">
          <p class="kicker">The road</p>
          <h2 id="map-heading">The stops they filmed</h2>
          {intro}
        </div>
        <a class="link-arrow" href="{prefix}destinations/route-66.html">All Route 66 films</a>
      </div>
      <div class="trip-map-frame">
        <div id="trip-map" class="trip-map" role="region" aria-label="Map of filmed Route 66 stops">
          <p class="trip-map-placeholder">The map loads when you scroll to it. The stops are listed below.</p>
        </div>
      </div>
      <ul class="trip-legend">
        <li><span class="trip-legend-pin" aria-hidden="true"></span> Filmed stop</li>
        <li><span class="trip-legend-line" aria-hidden="true"></span> Route 66, roughly, between those stops</li>
        <li><span class="trip-legend-spur" aria-hidden="true"></span> Spur to Pecos National Historical Park</li>
      </ul>
    </div>
  </section>
  <section class="section" aria-labelledby="legs-heading" style="padding-top:0">
    <div class="wrap">
      <div class="section-head">
        <div class="section-intro">
          <p class="kicker">East to west</p>
          <h2 id="legs-heading">Stop by stop</h2>
        </div>
      </div>
      {"".join(state_blocks)}
    </div>
  </section>
  <section class="section" aria-labelledby="trip-films-heading" style="padding-top:0">
    <div class="wrap">
      <div class="section-head">
        <div class="section-intro">
          <p class="kicker">The films</p>
          <h2 id="trip-films-heading">Watch along the way</h2>
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


def robots_and_sitemap() -> None:
    pages = [
        "/",
        "/destinations/",
        "/videos.html",
        "/shorts.html",
        "/about.html",
        "/trips/",
        "/trips/route-66.html",
    ] + [f"/destinations/{d['slug']}.html" for d in DESTINATIONS]
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


def main() -> None:
    write(ROOT / "index.html", page_home())
    write(ROOT / "destinations" / "index.html", page_destinations_index())
    for d in DESTINATIONS:
        write(ROOT / "destinations" / f"{d['slug']}.html", page_destination(d))
    write(ROOT / "videos.html", page_videos())
    write(ROOT / "shorts.html", page_shorts())
    write(ROOT / "about.html", page_about())
    write(ROOT / "trips" / "index.html", page_trips_index())
    write(ROOT / "trips" / "route-66.html", page_trip_route66())
    robots_and_sitemap()
    ids = [v["id"] for v in VIDEOS]
    assert len(ids) == len(set(ids)), "duplicate video ids"
    print(f"OK — {len(ids)} unique videos")


if __name__ == "__main__":
    main()

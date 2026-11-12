#!/usr/bin/env python3
"""Generate the Totin My Pack static site."""
from __future__ import annotations

import html
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
VIDEOS = [
    # id, title, kind, date, length, groups
    ("mC0ZWATfzvc", "Exploring an Abandoned Church in Texas | St. John’s in Bomarton", "film", "November 7, 2022", "2:56", ["texas", "start"]),
    ("ONbdk7yflpM", "Mount Itamos, Greece | Hiking to an Ancient Tree", "film", "October 17, 2022", "5:46", ["greece", "start"]),
    ("3cFk5Tf7nOg", "Talimena Scenic Byway in Fall | Oklahoma & Arkansas Road Trip", "film", "November 20, 2023", "3:51", ["plains", "start"]),
    ("p9PXuj51NJs", "Devils River, Texas | Turquoise Water & Drone Views", "film", "December 4, 2023", "4:21", ["texas", "start"]),
    ("ZKI-PbPRraw", "Caddo Lake in Fall | Cypress Swamps of East Texas (2023)", "film", "November 26, 2023", "3:09", ["texas", "start"]),
    ("vQvsLO0F0tE", "Greece with Tres & Teddy | Skopelos, Meteora & Mount Olympus (2008)", "film", "June 2, 2025", "3:15", ["greece"]),
    ("is4VhiJbrPU", "ΧΑΝΘ Κατασκήνωση Αγίου Νικολάου | My Summer Camp Tribute in Halkidiki", "film", "October 28, 2022", "11:02", ["greece"]),
    ("mk44NdLZgQs", "Swimming in Gerakini, Greece | Crystal Clear Water & Marine Life", "film", "October 1, 2022", "5:16", ["greece"]),
    ("RWvKeHEqRVM", "The Road to an Ancient Greek Tree | Mount Itamos", "short", "October 7, 2026", "0:21", ["greece"]),
    ("674bBByn45U", "A Greek Mountain Overlooking the Aegean", "short", "October 4, 2026", "0:21", ["greece"]),
    ("fdVL-Z72EKM", "The Ancient Itamos Tree | Halkidiki, Greece", "short", "November 19, 2022", "0:15", ["greece"]),
    ("Whbt1fpVyUE", "Mount Dragoudeli, Greece | Profítis Ilias Church", "short", "November 4, 2022", "0:15", ["greece"]),
    ("QWMI7iZEz1I", "Big Bend Twice in One Year | Two 2024 Road Trips", "film", "October 10, 2026", "5:21", ["texas"]),
    ("_JLdOGsAiLU", "From Dallas to El Paso | Airport, Flight & First Impressions", "film", "January 2, 2026", "3:06", ["texas"]),
    ("AFfq9r_-VVc", "3 Texas Parks and a Meteor Crater in 1 Day | Road to Big Bend", "film", "May 16, 2024", "2:41", ["texas"]),
    ("2uoq3FREvm0", "Texas Rivers & the Present Moment | Alan Watts on Life’s Flow", "film", "December 3, 2023", "2:37", ["texas"]),
    ("vlZ-VTkCJWc", "New Sweden Lutheran Church, Texas | Chasing the Steeple", "film", "December 3, 2023", "1:56", ["texas"]),
    ("MUVr2dNxiJU", "Daingerfield State Park | Scenic Trails & Lake Views in East Texas", "film", "December 3, 2023", "2:15", ["texas"]),
    ("nKqIFBJJD5Q", "Purtis Creek State Park, Texas | A Scenic Visit", "film", "October 6, 2022", "2:47", ["texas"]),
    ("8ISaQKSOX2I", "St. Olaf Rock Church | Cranfills Gap, Texas", "film", "October 6, 2022", "3:08", ["texas"]),
    ("NVj-nf5WV3s", "Mother Neff State Park, Texas | Tonkawa Cave & Rock Tower", "film", "October 1, 2022", "3:08", ["texas"]),
    ("u-07NbxVSmg", "Seminole Canyon, Judge Roy Bean & Pecos High Bridge | Texas Road Trip", "film", "October 1, 2022", "2:40", ["texas"]),
    ("mKbvoBOyDcg", "Mayfield’s Country Store | A West Texas Road Trip Stop", "film", "October 1, 2022", "2:41", ["texas"]),
    ("iAX9HuobAG4", "Downtown Beaumont, Texas | Quiet Streets & Historic Buildings", "film", "September 30, 2022", "3:32", ["texas"]),
    ("_pAqzkL05D8", "Enchanted Rock Summit Trail | A Personal Hiking Challenge in Texas", "film", "September 29, 2022", "3:53", ["texas"]),
    ("EBnbggUsdMw", "Turquoise Water in West Texas | Devils River", "short", "October 1, 2026", "0:21", ["texas"]),
    ("mJdj_aKcp5U", "This Texas River Looks Unreal | Devils River", "short", "September 28, 2026", "0:21", ["texas"]),
    ("SuYFwuJCK70", "Found From Above: An Abandoned Texas Church #Shorts", "short", "September 25, 2026", "0:21", ["texas"]),
    ("UVgpgOu0iMY", "This Abandoned Texas Church Is Still Standing #Shorts", "short", "September 22, 2026", "0:09", ["texas"]),
    ("kMLey2PDgr4", "The Open Road in West Texas", "short", "November 18, 2022", "0:15", ["texas"]),
    ("NPsozGVaW_M", "Maker of Peace Sculpture | Seminole Canyon, Texas", "short", "November 10, 2022", "0:15", ["texas"]),
    ("IsS0M0oikks", "One Tree, Many Lives | Wildlife in Dallas, Texas", "film", "September 26, 2026", "2:49", ["dallas"]),
    ("AWAJOYe12cU", "I Finally Filmed a Hummingbird Hovering | Canon R7", "film", "September 22, 2026", "0:45", ["dallas"]),
    ("VktGvxzG4sU", "Hummingbirds on My Dallas Balcony | Small Birds, Big Business", "film", "September 19, 2026", "3:21", ["dallas"]),
    ("e6Wr9Cpg0y8", "2024 Total Solar Eclipse in Dallas, Texas | April 8 Totality", "film", "April 11, 2024", "6:55", ["dallas"]),
    ("IAWKwGGkmuo", "Snow at White Rock Lake, Dallas | January 15, 2024", "film", "January 15, 2024", "2:42", ["dallas"]),
    ("K6H6o_XyXJ0", "Dallas Snowstorm 2021 | The Lakes at The Village", "film", "October 6, 2022", "5:35", ["dallas"]),
    ("eLENrH_cRhg", "White Rock Lake in Winter | Dallas Freeze (2021)", "film", "October 5, 2022", "4:46", ["dallas"]),
    ("q7nWd0ujrco", "White Rock Lake Frozen | Rare Snowstorm in Dallas, Texas (2021)", "film", "October 5, 2022", "2:17", ["dallas"]),
    ("-vBN1DJ2ghI", "The Moment Day Turned to Night | Total Eclipse #Shorts", "short", "October 13, 2026", "0:21", ["dallas"]),
    ("vXyd_HIr6tE", "Dallas Saw Totality in 2024 #Shorts", "short", "October 10, 2026", "0:21", ["dallas"]),
    ("T2cuzLzEK0s", "A Fox Squirrel's Busy Day Has a Quiet Ending", "short", "October 3, 2026", "0:24", ["dallas"]),
    ("K2cJeiEFkBs", "Look Closer: Anoles, Ants & a Damselfly | Texas Wildlife", "short", "September 30, 2026", "0:26", ["dallas"]),
    ("yBZF6kZQ1_I", "A Cooper's Hawk Watches, Then Takes Flight | Dallas Wildlife", "short", "September 27, 2026", "0:25", ["dallas"]),
    ("-ibB4Z-a5tQ", "This Hummingbird Takes Feather Care Seriously", "short", "September 25, 2026", "0:26", ["dallas"]),
    ("sQ1H9CDtSgA", "Why Land? A Hummingbird's Lunch Break", "short", "September 22, 2026", "0:13", ["dallas"]),
    ("DHxZueP0Z04", "Route 66, One Stop at a Time | Our Roadside Memories", "film", "September 27, 2026", "6:34", ["route66"]),
    ("MEWEWz0Ny9M", "Oklahoma Route 66 | Roadside Stops & Mother Road Memories", "film", "December 8, 2023", "1:39", ["route66"]),
    ("bwhDxYsaBT4", "Missouri on Route 66 | Devil’s Elbow, Rocking Chairs & Fudge in Uranus", "film", "December 7, 2023", "3:05", ["route66"]),
    ("egYLfHGUae4", "Route 66: Texas to New Mexico | Cadillac Ranch to Pecos", "film", "September 25, 2022", "2:41", ["route66"]),
    ("OkjZP-cKp6o", "We Haven't Driven Every Mile of Route 66—Yet #Shorts", "short", "October 5, 2026", "0:31", ["route66"]),
    ("E9TIfpZ69NU", "The Roadside Characters of Route 66", "short", "October 2, 2026", "0:32", ["route66"]),
    ("oGOguq2e0AI", "Route 66, One Stop at a Time | Our Roadside Memories", "short", "September 29, 2026", "0:32", ["route66"]),
    ("6dM9uO6qR5I", "Cadillac Ranch at Sunrise | Route 66, Texas", "short", "November 11, 2022", "0:16", ["route66"]),
    ("PGW3p9qo6aA", "Standin’ on the Corner | Winslow, Arizona Route 66", "short", "November 2, 2022", "0:26", ["route66"]),
    ("EgpjjRVXfWs", "Black Hills & Devils Tower | South Dakota Road Trip, Part 2", "film", "January 24, 2026", "1:52", ["plains"]),
    ("V7cVxfXdDqQ", "Dallas to South Dakota | Carhenge & Great Plains Road Trip, Part 1", "film", "December 2, 2025", "2:33", ["plains"]),
    ("3bheRk_JsVk", "World’s Largest Leg Lamp | A Christmas Story Landmark in Chickasha, Oklahoma", "film", "December 5, 2022", "2:52", ["plains"]),
    ("vcucLYAUPAQ", "Mount Scott, Oklahoma | Views from the Summit", "film", "October 6, 2022", "2:04", ["plains"]),
    ("WduI4TDWmn4", "Eureka Springs to War Eagle Mill | Arkansas Road Trip, Part 3", "film", "September 30, 2022", "3:21", ["plains"]),
    ("Zy74kbpTBF8", "Arkansas Grand Canyon & Bella Vista | Ozarks Winter Drive, Part 2", "film", "September 29, 2022", "3:20", ["plains"]),
    ("FmwMcGvxNrE", "Pig Trail Scenic Byway | Fort Smith to Rogers, Arkansas", "film", "September 29, 2022", "3:13", ["plains"]),
    ("5P7y5tmslhQ", "An Oklahoma–Arkansas Fall Drive #Shorts", "short", "October 19, 2026", "0:21", ["plains"]),
    ("2f-wKhlW_PE", "Autumn From Above in Talimena #Shorts", "short", "October 16, 2026", "0:21", ["plains"]),
    ("DEwRiH1wkbk", "South Dakota in Motion | Road Trip Moments", "short", "January 25, 2026", "0:12", ["plains"]),
    ("ky4mX9ykzxY", "Buffalo National River | Red Bluff Overlook, Arkansas", "short", "November 3, 2022", "0:27", ["plains"]),
    ("AVvLeGSLk50", "Buc-ee Visits Gatlinburg! (November 2014 Throwback)", "film", "June 3, 2025", "2:26", ["southeast"]),
    ("S_K-LyRann0", "From The Waltons to Monticello | Our Road Trip Through Virginia’s Past", "film", "April 3, 2025", "3:29", ["southeast"]),
    ("y0EhqN3QnnY", "Appomattox, Roanoke & New River Gorge | Road Trip 2024, Part 2", "film", "March 31, 2025", "3:52", ["southeast"]),
    ("jNoREzI7-B0", "Norfolk, Virginia Beach & Cape Charles | Coastal Road Trip (2024)", "film", "March 30, 2025", "4:36", ["southeast"]),
    ("aVUb43ZTMrI", "Key West, Florida | The Journey & Island Memories", "film", "October 1, 2022", "3:06", ["southeast"]),
    ("g6QLNAGmNDk", "Savannah & Tybee Island | Squares, Cemetery & Lighthouse", "film", "September 30, 2022", "3:48", ["southeast"]),
    ("qMI9-rGlwD4", "Myrtle Beach, South Carolina | Sunrises & Coastal Stops, Part 3", "film", "September 30, 2022", "4:27", ["southeast"]),
    ("VnSlljuciTI", "Athens, Georgia | R.E.M. Landmarks & Georgia Guidestones", "film", "September 30, 2022", "4:32", ["southeast"]),
    ("qbXorgrsIi4", "Texas to Alabama Road Trip | Meridian & Moundville, Part 1", "film", "September 29, 2022", "3:57", ["southeast"]),
    ("YfS65RVDiXY", "Northern California Road Trip | Santa Rosa, Mendocino & Napa", "film", "December 20, 2023", "4:31", ["california"]),
    ("lbhHR6MpSlA", "California Redwoods to the Pacific | Chandelier Tree Road Trip (2023)", "film", "December 15, 2023", "3:15", ["california"]),
    ("UEMTYT3kYA4", "Flagstaff to Sedona | Sunset Crater, Wupatki & Oak Creek Canyon", "film", "September 25, 2022", "3:06", ["southwest"]),
    ("ixpaxmrlv1w", "Grand Canyon Sunset at Lipan Point | Road Trip from Flagstaff", "film", "September 25, 2022", "2:48", ["southwest"]),
    ("N484V1EG0a0", "Santa Fe to Taos | Camel Rock & Rio Grande Gorge Road Trip", "film", "September 25, 2022", "3:25", ["southwest"]),
    ("7PROHmCUf_Q", "Santa Fe to Monument Valley | Loretto Chapel, Shiprock & Four Corners", "film", "September 25, 2022", "3:20", ["southwest"]),
    ("5cLy5YOaPW8", "Monument Valley Jeep Tour | Sunrise, Forrest Gump Point & Milky Way", "film", "September 25, 2022", "5:55", ["southwest"]),
    ("cuwNyFySMzQ", "Arizona to Roswell | Meteor Crater, Winslow & Petrified Forest", "film", "September 25, 2022", "4:00", ["southwest"]),
    ("1_Wc9tugXdg", "Rio Grande Gorge Bridge | New Mexico Views", "short", "November 13, 2022", "0:18", ["southwest"]),
    ("DZPAwk3lHsw", "Shiprock, New Mexico | A Striking Volcanic Landmark", "short", "November 9, 2022", "0:13", ["southwest"]),
    ("nydMxizVhQw", "Monument Valley Under the Stars | Night Sky", "short", "November 6, 2022", "0:17", ["southwest"]),
    ("GyP3qhUY8FA", "Grand Canyon Views | Arizona Road Trip", "short", "November 5, 2022", "0:26", ["southwest"]),
    ("h8lAvPv69wg", "Monument Valley Sunrise | First Light", "short", "October 31, 2022", "0:16", ["southwest"]),
    ("VeKh55kDqeg", "Berlin in Winter | Brandenburg Gate, Reichstag & Berlin Wall (2012)", "film", "August 26, 2024", "1:49", ["berlin"]),
]

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

# Homepage destination card stills (cropped via object-position in CSS where needed)
DEST_CARDS = [
    ("greece", "Greece", "ONbdk7yflpM", "8 films"),
    ("texas", "Texas", "p9PXuj51NJs", "22 films"),
    ("dallas", "Dallas & close to home", "VktGvxzG4sU", "15 films"),
    ("route-66", "Route 66", "egYLfHGUae4", "9 films"),
    ("plains", "Oklahoma, Arkansas & the Plains", "3cFk5Tf7nOg", "12 films"),
    ("southeast", "Southeast & Mid-Atlantic", "jNoREzI7-B0", "9 films"),
    ("california", "California", "lbhHR6MpSlA", "2 films"),
    ("southwest", "The Southwest", "ixpaxmrlv1w", "11 films"),
    ("berlin", "Berlin", "VeKh55kDqeg", "1 film"),
]

START_IDS = ["mC0ZWATfzvc", "ONbdk7yflpM", "3cFk5Tf7nOg", "p9PXuj51NJs", "ZKI-PbPRraw"]
HERO_ID = "ZKI-PbPRraw"
LATEST_FILM_IDS = [
    "QWMI7iZEz1I", "DHxZueP0Z04", "IsS0M0oikks", "AWAJOYe12cU",
    "VktGvxzG4sU", "EgpjjRVXfWs", "_JLdOGsAiLU", "V7cVxfXdDqQ",
]
SHORT_TEASER_IDS = [
    "-ibB4Z-a5tQ", "EBnbggUsdMw", "SuYFwuJCK70", "oGOguq2e0AI",
    "K2cJeiEFkBs", "2f-wKhlW_PE",
]

BY_ID = {
    v[0]: {"id": v[0], "title": v[1], "kind": v[2], "date": v[3], "length": v[4], "groups": v[5]}
    for v in VIDEOS
}


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
  <button class="{cls}" type="button" data-video-id="{esc(v['id'])}" data-title="{esc(v['title'])}" data-kind="{kind}" data-filter-item data-group="{esc(v['groups'][0])}">
    <span class="{thumb_cls}">
      <img src="{thumb(v['id'])}" alt="{alt}" width="1280" height="720" loading="{loading}" decoding="async"{fetch} data-fallback="{esc(v['id'])}">
      {play_icon()}
      <span class="chip">{esc(v['length'])}</span>
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
        <li><a href="{prefix}videos.html"{cur("videos")}>Films</a></li>
        <li><a href="{prefix}shorts.html"{cur("shorts")}>Shorts</a></li>
        <li><a href="{prefix}about.html"{cur("about")}>About</a></li>
      </ul>
      <a class="btn btn-gold nav-cta" href="{CHANNEL}" rel="noopener noreferrer">Subscribe on YouTube</a>
    </nav>
  </div>
</header>"""


def footer(prefix: str) -> str:
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
<script src="{prefix}js/main.js" defer></script>"""


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
    import json

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
    for slug, name, img, label in DEST_CARDS:
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


def robots_and_sitemap() -> None:
    pages = [
        "/",
        "/destinations/",
        "/videos.html",
        "/shorts.html",
        "/about.html",
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
    robots_and_sitemap()
    ids = [v[0] for v in VIDEOS]
    assert len(ids) == len(set(ids)) == 89, len(set(ids))
    print("OK — 89 unique videos")


if __name__ == "__main__":
    main()

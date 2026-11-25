# New England film and website releases

This change prepares companion website articles for the nine New England films.
The existing design and YouTube player are reused. No full-resolution video file
is hosted by this repository; the website embeds the matching YouTube film.

## Activation status

The nine `video_id` values in `data/new-england-releases.json` are intentionally
unset until the actual YouTube uploads exist. An unset or invalid ID cannot be
released. Do not replace an ID with a guessed value or a placeholder.

Before activation, fill in the nine real YouTube IDs and verify the matching
channel, title, duration and native YouTube publication timestamps. GitHub Pages
must use **GitHub Actions** as its publishing source, and the `github-pages`
environment must permit this repository's `main` branch to deploy unattended.

## Schedule

All main-film releases are at 6:00 pm in `America/Chicago`.

| Film | YouTube and companion website target |
| --- | --- |
| Day 1 | November 28, 2026 |
| Day 2 | December 2, 2026 |
| Day 3 | December 5, 2026 |
| Day 4 | December 9, 2026 |
| Day 5 | December 12, 2026 |
| Day 6 | December 16, 2026 |
| Day 7 | December 19, 2026 |
| Day 8 | December 23, 2026 |
| Day 9 | December 26, 2026 |

The workflow checks at the main-film release time and retries every 15 minutes.
GitHub runner queues, YouTube feed propagation and Pages deployment can delay the
website. It must never show a private or unavailable scheduled embed merely
because the clock has reached the target time.

## Publication flow

1. `release_videos.py` selects assigned, due and previously unpublished films.
2. Each film must appear in Totin My Pack's public YouTube feed and return a
   working video oEmbed response. oEmbed alone is insufficient because it can
   also describe an unlisted video. Failed checks leave the site data unchanged.
3. A verified release adds its catalog entry, homepage card, New England
   destination and companion article together. The series page and previous/next
   links contain only released articles. Exact music credits accompany each film.
4. `update_videos.py` preserves the existing RSS behavior for other uploads.
   Planned main-film IDs and titles are excluded from that generic path so it
   cannot bypass the article/release gate.
5. `build.py` generates the site; `package_site.py` copies only public website
   files into `_site`, excluding source data and unreleased article plans.
6. `actions/deploy-pages` explicitly deploys the artifact. Only after successful
   deployment does the workflow commit the updated catalog, articles and release
   state. A failed deployment therefore remains due on the next run. If a commit
   fails after a successful deployment, the next run safely rebuilds the same
   release without duplicate posts.

No website article is created for an individual Short. Existing Shorts catalog
updates continue through the RSS workflow. The scheduled website work runs on
GitHub and does not require Teddy's computer or a ChatGPT session to stay open.

## Verification and practical limits

Run `python -m unittest discover -s tests -v`, `python release_videos.py --dry-run`,
`python build.py`, and `python package_site.py` before activation. Tests cover the
timestamp and public-video gates, unset IDs, repeat runs, RSS bypass prevention,
destination assignment, article links and attribution. The full generator was
also checked with no releases and in an isolated all-nine release simulation.

The public YouTube feed retains its latest 15 uploads. If an extended outage lets
a main film fall out of that feed before its first website publication, the
workflow deliberately leaves it pending for manual verification. It does not
guess public status or silently publish a potentially private embed.

Current primary references:

- [GitHub schedule syntax and IANA timezones](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#onschedule)
- [GitHub scheduling delays](https://docs.github.com/en/actions/how-tos/troubleshoot-workflows)
- [Explicit GitHub Pages artifact deployment](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
- [Why GITHUB_TOKEN pushes do not trigger Pages builds](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)
- [Pillow 13.0.0, supporting Python 3.12](https://pypi.org/project/pillow/13.0.0/)

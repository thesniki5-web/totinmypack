import copy
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import build
import release_videos as releases
import update_videos as updater


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.manifest = releases.load_manifest()
        self.episode = copy.deepcopy(self.manifest["episodes"][0])
        self.episode["video_id"] = "TESTvideo01"
        self.article = json.loads(releases.COPY_PATH.read_text())[0]
        self.videos = []
        self.site = {"latest_film_ids": [], "short_teaser_ids": [], "dest_cards": []}
        self.blog = {"posts": []}
        self.state = {"published": {}}
        self.due = releases.timestamp(self.episode["publish_at"])

    def apply(self, now=None):
        return releases.release_episode(
            self.episode, self.article, self.manifest, self.videos,
            self.site, self.blog, self.state, now or self.due,
        )

    def test_schedule_is_nine_chronological_six_pm_central_releases(self):
        self.assertEqual([e["day"] for e in self.manifest["episodes"]], list(range(1, 10)))
        for episode in self.manifest["episodes"]:
            dt = releases.timestamp(episode["publish_at"])
            self.assertEqual((dt.hour, dt.minute), (18, 0))
            self.assertIn(dt.weekday(), (2, 5))
            self.assertEqual(dt.utcoffset().total_seconds(), -21600)

    def test_missing_id_cannot_publish(self):
        self.episode["video_id"] = None
        with self.assertRaises(ValueError):
            self.apply()
        self.assertFalse(self.blog["posts"])

    def test_cannot_publish_before_exact_timestamp(self):
        self.assertFalse(self.apply(datetime(2026, 11, 28, 23, 59, 59, tzinfo=timezone.utc)))
        self.assertEqual(self.videos, [])
        self.assertEqual(self.state["published"], {})

    def test_verified_release_adds_film_article_and_destination_together(self):
        self.assertTrue(self.apply())
        self.assertEqual(self.videos[0]["id"], self.episode["video_id"])
        self.assertEqual(self.videos[0]["published"], "2026-11-28")
        self.assertEqual(self.videos[0]["groups"], ["newengland"])
        self.assertEqual(self.blog["posts"][0]["music_credits"], self.article["music_credits"])
        self.assertEqual(self.site["dest_cards"][0]["slug"], "new-england")

    def test_retry_is_idempotent(self):
        self.assertTrue(self.apply())
        self.assertFalse(self.apply())
        self.assertEqual((len(self.videos), len(self.blog["posts"]), len(self.state["published"])), (1, 1, 1))

    def test_oembed_alone_is_not_proof_of_public_release(self):
        with patch.object(releases, "fetch") as fetch:
            self.assertFalse(releases.public_and_embeddable("TESTvideo01", set()))
        fetch.assert_not_called()

    def test_public_feed_and_playable_embed_are_both_required(self):
        data = {"provider_name": "YouTube", "type": "video", "title": "Film", "html": '<iframe src="https://www.youtube.com/embed/TESTvideo01"></iframe>'}
        with patch.object(releases, "fetch", return_value=json.dumps(data).encode()):
            self.assertTrue(releases.public_and_embeddable("TESTvideo01", {"TESTvideo01"}))
        with patch.object(releases, "fetch", side_effect=OSError("unavailable")):
            self.assertFalse(releases.public_and_embeddable("TESTvideo01", {"TESTvideo01"}))

    def test_invalid_manifest_id_rejected(self):
        self.manifest["episodes"][0]["video_id"] = "not a video id"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "plan.json"
            path.write_text(json.dumps(self.manifest))
            with self.assertRaises(ValueError):
                releases.load_manifest(path)

    def test_rss_cannot_bypass_managed_release_gate(self):
        entry = {"id": "TESTvideo01", "title": self.episode["video_title"],
                 "published_raw": "2026-11-28T23:30:00Z", "url": "https://www.youtube.com/watch?v=TESTvideo01"}
        added = updater.merge(self.videos, self.site, [entry], fetch_durations=False,
                              planned_main_ids={"TESTvideo01"})
        self.assertEqual(added, [])
        # Title matching also protects the pending plan before an ID is assigned.
        added = updater.merge(self.videos, self.site, [entry], fetch_durations=False,
                              planned_main_titles={self.episode["video_title"]})
        self.assertEqual(added, [])

    def test_new_england_trip_wins_over_dallas_departure_keyword(self):
        self.assertEqual(updater.assign_destination(self.episode["video_title"]), "newengland")

    def test_article_and_series_only_link_released_episodes(self):
        self.apply()
        with patch.object(build, "_blog_posts", return_value=self.blog["posts"]), \
             patch.object(build, "BY_ID", {self.episode["video_id"]: self.videos[0]}):
            article_html = build.page_blog_post(self.blog["posts"][0])
            series_html = build.page_new_england_series()
        self.assertIn('data-video-id="TESTvideo01"', article_html)
        self.assertIn("new-england-2026.html", article_html)
        self.assertIn("Music credits", article_html)
        self.assertNotIn("new-england-2026-day-02", article_html + series_html)
        self.assertNotIn("Next film", article_html)
        self.assertIn("new-england-2026-day-01", series_html)

    def test_all_articles_have_canonical_days_and_credits(self):
        articles = json.loads(releases.COPY_PATH.read_text())
        self.assertEqual([p["day"] for p in articles], list(range(1, 10)))
        self.assertEqual(len({p["slug"] for p in articles}), 9)
        for p in articles:
            self.assertIn("Kevin MacLeod", p["music_credits"])
            self.assertIn("https://creativecommons.org/licenses/by/4.0/", p["music_credits"])
            self.assertEqual(p["trip_dates"], f"November {p['day']+5}, 2026")


if __name__ == "__main__":
    unittest.main()

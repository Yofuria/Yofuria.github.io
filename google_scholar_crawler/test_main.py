"""Offline regression tests for the citation API and published data contract."""

import copy
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlparse

import main as crawler


SCHOLAR_ID = "exampleAAAAJ"
RESULT = {
    "search_metadata": {"status": "Success", "created_at": "2026-11-15 12:00:00 UTC"},
    "search_parameters": {"engine": "google_scholar_author", "author_id": SCHOLAR_ID},
    "author": {"name": "Example Author", "interests": [{"title": "Machine Learning"}]},
    "cited_by": {
        "table": [
            {"citations": {"all": 123, "since_2021": 120}},
            {"h_index": {"all": 6, "since_2021": 5}},
            {"i10_index": {"all": 4, "since_2021": 3}},
        ],
        "graph": [{"year": 2025, "citations": 50}, {"year": 2026, "citations": 73}],
    },
    "articles": [
        {"citation_id": SCHOLAR_ID + ":paper1", "title": "First paper", "year": "2025",
         "authors": "Example Author", "cited_by": {"value": 123}},
        {"citation_id": SCHOLAR_ID + ":paper2", "title": "New paper", "cited_by": {"value": None}},
    ],
}


class SerpApiTests(unittest.TestCase):
    def test_preserves_existing_output_fields_and_source_time(self):
        author = crawler.parse_serpapi(copy.deepcopy(RESULT), SCHOLAR_ID)
        self.assertEqual(author["scholar_id"], SCHOLAR_ID)
        self.assertEqual(author["citedby"], 123)
        self.assertEqual(author["citedby5y"], 120)
        self.assertEqual(author["hindex"], 6)
        self.assertEqual(author["i10index5y"], 3)
        self.assertEqual(author["updated"], "2026-11-15T12:00:00+00:00")
        self.assertEqual(author["cites_per_year"], {"2025": 50, "2026": 73})
        self.assertEqual(author["publications"][SCHOLAR_ID + ":paper1"]["num_citations"], 123)
        self.assertEqual(author["publications"][SCHOLAR_ID + ":paper2"]["num_citations"], 0)

    def test_rejects_invalid_totals_including_booleans(self):
        for value in (None, True, False, -1, 1.5, "123"):
            with self.subTest(value=value):
                result = copy.deepcopy(RESULT)
                result["cited_by"]["table"][0]["citations"]["all"] = value
                with self.assertRaises(ValueError):
                    crawler.parse_serpapi(result, SCHOLAR_ID)

    def test_zero_is_a_valid_total(self):
        result = copy.deepcopy(RESULT)
        result["cited_by"]["table"][0]["citations"]["all"] = 0
        self.assertEqual(crawler.parse_serpapi(result, SCHOLAR_ID)["citedby"], 0)

    def test_missing_total_is_not_zero(self):
        result = copy.deepcopy(RESULT)
        del result["cited_by"]["table"][0]["citations"]["all"]
        with self.assertRaises(KeyError):
            crawler.parse_serpapi(result, SCHOLAR_ID)

    def test_rejects_wrong_profile_or_publication(self):
        result = copy.deepcopy(RESULT)
        result["search_parameters"]["author_id"] = "another-author"
        with self.assertRaises(ValueError):
            crawler.parse_serpapi(result, SCHOLAR_ID)
        result = copy.deepcopy(RESULT)
        result["articles"][0]["citation_id"] = "another-author:paper1"
        with self.assertRaises(ValueError):
            crawler.parse_serpapi(result, SCHOLAR_ID)

    def test_rejects_failed_incomplete_or_wrong_engine_results(self):
        for changes in (
            {"error": "API failure"},
            {"search_metadata": {"status": "Processing"}},
            {"search_parameters": {"engine": "google", "author_id": SCHOLAR_ID}},
        ):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                crawler.parse_serpapi({**RESULT, **changes}, SCHOLAR_ID)

    def test_serpapi_is_primary_and_requests_fresh_json(self):
        with patch.object(crawler, "fetch_page", return_value=json.dumps(RESULT)) as fetch:
            author = crawler.fetch_author(SCHOLAR_ID, serpapi_key=" test-key ", scraperapi_key="unused")
        self.assertEqual(author["fetched_via"], "serpapi")
        self.assertEqual(fetch.call_count, 1)
        request = urlparse(fetch.call_args.args[0])
        self.assertEqual(request.netloc, "serpapi.com")
        self.assertEqual(request.path, "/search.json")
        self.assertEqual(parse_qs(request.query)["no_cache"], ["true"])
        self.assertEqual(parse_qs(request.query)["api_key"], ["test-key"])
        self.assertEqual(fetch.call_args.kwargs["accept"], "application/json")

    def test_transient_failure_retries_once(self):
        with patch.object(crawler, "fetch_page", side_effect=[
            crawler.FetchError("HTTP 503", retryable=True), json.dumps(RESULT)
        ]) as fetch, patch.object(crawler.time, "sleep"):
            author = crawler.fetch_serpapi(SCHOLAR_ID, "test-key")
        self.assertEqual(author["citedby"], 123)
        self.assertEqual(fetch.call_count, 2)

    def test_authentication_failure_is_not_retried(self):
        with patch.object(crawler, "fetch_page", side_effect=crawler.FetchError("HTTP 401")) as fetch:
            with self.assertRaises(crawler.FetchError):
                crawler.fetch_serpapi(SCHOLAR_ID, "test-key")
        self.assertEqual(fetch.call_count, 1)

    def test_api_error_can_fall_back_to_valid_public_profile(self):
        direct = {"scholar_id": SCHOLAR_ID, "citedby": 123, "publications": {}}
        with patch.object(crawler, "fetch_page", side_effect=[json.dumps({"error": "unavailable"}), "html"]), \
                patch.object(crawler, "parse_author", return_value=direct):
            author = crawler.fetch_author(SCHOLAR_ID, serpapi_key="test-key")
        self.assertEqual(author["fetched_via"], "direct")
        self.assertEqual(author["citedby"], 123)

    def test_http_errors_never_log_secret_urls(self):
        url = "https://serpapi.com/search.json?api_key=secret-test-value"
        error = HTTPError(url, 401, "failed: " + url, {}, None)
        output = io.StringIO()
        with patch.object(crawler, "urlopen", side_effect=error), redirect_stderr(output):
            with self.assertRaises(SystemExit):
                crawler.fetch_author(SCHOLAR_ID, serpapi_key="secret-test-value")
        self.assertIn("HTTP 401", output.getvalue())
        self.assertNotIn("secret-test-value", output.getvalue())

    def test_success_keeps_api_timestamp_and_writes_matching_badge(self):
        author = crawler.parse_serpapi(copy.deepcopy(RESULT), SCHOLAR_ID)
        with tempfile.TemporaryDirectory() as directory, \
                patch.object(crawler, "OUT_DIR", directory), \
                patch.dict(crawler.os.environ, {"GOOGLE_SCHOLAR_ID": SCHOLAR_ID}), \
                patch.object(crawler, "fetch_author", return_value=author):
            crawler.main()
            data = json.loads((Path(directory) / "gs_data.json").read_text())
            badge = json.loads((Path(directory) / "gs_data_shieldsio.json").read_text())
        self.assertEqual(data["updated"], "2026-11-15T12:00:00+00:00")
        self.assertEqual(badge["message"], "123")

    def test_total_failure_leaves_published_files_untouched(self):
        with tempfile.TemporaryDirectory() as directory, \
                patch.object(crawler, "OUT_DIR", directory), \
                patch.dict(crawler.os.environ, {"GOOGLE_SCHOLAR_ID": SCHOLAR_ID}), \
                patch.object(crawler, "fetch_page", side_effect=crawler.FetchError("HTTP 403")):
            files = [Path(directory) / name for name in ("gs_data.json", "gs_data_shieldsio.json")]
            for path in files:
                path.write_text("previous snapshot")
            with self.assertRaises(SystemExit):
                crawler.main()
            self.assertTrue(all(path.read_text() == "previous snapshot" for path in files))


if __name__ == "__main__":
    unittest.main()

"""Fetch Google Scholar stats and write them to results/*.json.

Use ScraperAPI when configured, with direct requests and free proxies as
fallbacks. A failed crawl exits before the workflow publishes any files.
"""

import json
import logging
import os
import sys
from datetime import datetime
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from bs4 import BeautifulSoup
from scholarly import scholarly, ProxyGenerator
from scholarly.author_parser import AuthorParser

SCHOLAR_ID = os.environ["GOOGLE_SCHOLAR_ID"]
SCRAPERAPI_KEY = os.environ.get("SCRAPERAPI_KEY")
OUT_DIR = "results"
SCRAPERAPI_ATTEMPTS = 3
FREE_PROXY_ATTEMPTS = 6
AUTHOR_SECTIONS = ["basics", "indices", "counts", "publications"]


class ScraperAPIPages:
    """Serve the existing author parser with pages from ScraperAPI's HTTPS endpoint."""

    def __init__(self, key):
        self.key = key
        self.logger = logging.getLogger(__name__)

    def _get_soup(self, path):
        query = urlencode({"api_key": self.key, "url": f"https://scholar.google.com{path}"})
        try:
            with urlopen(f"https://api.scraperapi.com/?{query}", timeout=75) as response:
                html = response.read().decode("utf-8", errors="replace")
        except HTTPError as error:
            raise RuntimeError(f"ScraperAPI returned HTTP {error.code}") from None
        except (URLError, TimeoutError):
            raise RuntimeError("ScraperAPI request failed or timed out") from None
        return BeautifulSoup(html.replace("\xa0", " "), "html.parser")


def validate_author(author):
    if author.get("scholar_id") != SCHOLAR_ID:
        raise ValueError("Google Scholar returned a different author profile")
    citations = author.get("citedby")
    if type(citations) is not int or citations < 0:
        raise ValueError("Google Scholar returned an invalid citation count")
    author["publications"] = {p["author_pub_id"]: p for p in author["publications"]}
    return author


def fetch_author():
    author = scholarly.search_author_id(SCHOLAR_ID)
    return validate_author(scholarly.fill(author, sections=AUTHOR_SECTIONS))


def fetch_with_retries():
    if SCRAPERAPI_KEY:
        parser = AuthorParser(ScraperAPIPages(SCRAPERAPI_KEY))
        for attempt in range(1, SCRAPERAPI_ATTEMPTS + 1):
            try:
                print(f"[scraperapi {attempt}] fetching via HTTPS...", file=sys.stderr)
                author = parser.get_author(SCHOLAR_ID)
                return validate_author(parser.fill(author, sections=AUTHOR_SECTIONS))
            except Exception as e:  # noqa: BLE001
                print(f"[scraperapi {attempt}] failed: {e}", file=sys.stderr)
    else:
        print("SCRAPERAPI_KEY not set; using direct + free proxies.", file=sys.stderr)

    # Passing both arguments prevents scholarly from initializing a free proxy.
    try:
        direct = ProxyGenerator()
        scholarly.use_proxy(direct, direct)
        print("[direct] fetching...", file=sys.stderr)
        return fetch_author()
    except Exception as e:  # noqa: BLE001
        print(f"[direct] failed: {e}", file=sys.stderr)

    # Rotate free proxies as a last resort.
    for attempt in range(1, FREE_PROXY_ATTEMPTS + 1):
        try:
            pg = ProxyGenerator()
            if not pg.FreeProxies():
                print(f"[freeproxy {attempt}] no free proxy available", file=sys.stderr)
                continue
            scholarly.use_proxy(pg, pg)
            print(f"[freeproxy {attempt}] got proxy, fetching...", file=sys.stderr)
            return fetch_author()
        except Exception as e:  # noqa: BLE001
            print(f"[freeproxy {attempt}] failed: {e}", file=sys.stderr)

    return None


def main():
    author = fetch_with_retries()

    if author is None:
        raise SystemExit(
            "Could not fetch valid Google Scholar data after all retries. "
            "Keeping the last published data."
        )

    author["updated"] = str(datetime.now())

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "gs_data.json"), "w") as f:
        json.dump(author, f, ensure_ascii=False)

    shieldsio = {
        "schemaVersion": 1,
        "label": "citations",
        "message": f"{author['citedby']}",
    }
    with open(os.path.join(OUT_DIR, "gs_data_shieldsio.json"), "w") as f:
        json.dump(shieldsio, f, ensure_ascii=False)

    print(f"OK: citedby={author['citedby']}, publications={len(author['publications'])}")


if __name__ == "__main__":
    main()

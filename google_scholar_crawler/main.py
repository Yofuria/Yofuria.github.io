"""Fetch Google Scholar stats and write them to results/*.json.

Read the public author page directly, with configured API fallbacks.
A failed crawl exits before the workflow publishes any files.
"""

import json
import logging
import os
import sys
from datetime import datetime, timezone
from http.client import HTTPException
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup
from scholarly.author_parser import AuthorParser

OUT_DIR = "results"
SCHOLAR_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)


class FetchedProfile:
    """Let AuthorParser reuse the one public page already fetched."""

    def __init__(self, html):
        self.soup = BeautifulSoup(html.replace("\xa0", " "), "html.parser")
        self.logger = logging.getLogger(__name__)

    def _get_soup(self, _path):
        return self.soup


def fetch_page(url, timeout):
    headers = {
        "Accept": "text/html",
        "Accept-Language": "en-US,en;q=0.9",
        "User-Agent": SCHOLAR_USER_AGENT,
    }
    request = Request(url, headers=headers)
    try:
        with urlopen(request, timeout=timeout) as response:
            encoding = response.headers.get_content_charset() or "utf-8"
            return response.read().decode(encoding, errors="replace")
    except HTTPError as error:
        raise RuntimeError(f"HTTP {error.code}") from None
    except (OSError, HTTPException):
        raise RuntimeError("Request failed or timed out") from None


def parse_author(html, scholar_id):
    profile = FetchedProfile(html)
    parser = AuthorParser(profile)
    author = parser.get_author(scholar_id)
    sections = ["basics", "indices", "counts"]
    rows = profile.soup.select("tr.gsc_a_tr")
    if rows:
        sections.append("publications")
    author = parser.fill(author, sections=sections, publication_limit=len(rows))

    if author.get("scholar_id") != scholar_id:
        raise ValueError("Google Scholar returned a different author profile")
    citations = author.get("citedby")
    if type(citations) is not int or citations < 0:
        raise ValueError("Google Scholar returned an invalid citation count")
    author["publications"] = {p["author_pub_id"]: p for p in author.get("publications", [])}
    return author


def fetch_author(scholar_id, *, serpapi_key=None, scraperapi_key=None):
    # The public profile route starts with user=, as allowed by Scholar's robots.txt.
    profile_url = "https://scholar.google.com/citations?" + urlencode({"user": scholar_id, "hl": "en"})
    sources = [("direct", profile_url, 20)]

    if serpapi_key:
        query = urlencode({
            "engine": "google_scholar_author",
            "author_id": scholar_id,
            "hl": "en",
            "output": "html",
            "api_key": serpapi_key,
        })
        sources.append(("serpapi", "https://serpapi.com/search?" + query, 45))

    if scraperapi_key:
        query = urlencode({"api_key": scraperapi_key, "max_cost": 25, "url": profile_url})
        sources.append(("scraperapi", "https://api.scraperapi.com/?" + query, 75))

    for label, url, timeout in sources:
        print(f"[{label}] fetching public profile...", file=sys.stderr)
        try:
            html = fetch_page(url, timeout)
        except RuntimeError as error:
            print(f"[{label}] failed: {error}", file=sys.stderr)
            continue

        try:
            return parse_author(html, scholar_id)
        except (AttributeError, IndexError, KeyError, TypeError, ValueError) as error:
            print(f"[{label}] invalid author profile ({type(error).__name__})", file=sys.stderr)

    raise SystemExit("Could not fetch valid Google Scholar data. Keeping the last published data.")


def main():
    author = fetch_author(
        os.environ["GOOGLE_SCHOLAR_ID"].strip(),
        serpapi_key=os.environ.get("SERPAPI_KEY"),
        scraperapi_key=os.environ.get("SCRAPERAPI_KEY"),
    )
    author["updated"] = datetime.now(timezone.utc).isoformat(timespec="seconds")

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

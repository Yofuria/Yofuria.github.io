"""Fetch Google Scholar stats and write them to results/*.json.

Read the public author page directly, with ScraperAPI as a fallback.
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


def fetch_profile(scholar_id, *, api_key=None, country_code=None):
    # The public profile route starts with user=, as allowed by Scholar's robots.txt.
    profile_query = {"user": scholar_id, "hl": "en"}
    if api_key and not country_code:
        profile_query["pagesize"] = 100
    profile_url = "https://scholar.google.com/citations?" + urlencode(profile_query)

    url = profile_url
    timeout = 20
    headers = {"Accept": "text/html", "Accept-Language": "en-US,en;q=0.9"}
    if api_key:
        options = {"api_key": api_key}
        if country_code:
            options["country_code"] = country_code
        options["url"] = profile_url
        url = "https://api.scraperapi.com/?" + urlencode(options)
        timeout = 75
    else:
        headers["User-Agent"] = SCHOLAR_USER_AGENT

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


def fetch_author(scholar_id, api_key):
    sources = [("direct", None, None)]
    if api_key:
        sources.extend([("scraperapi", api_key, None), ("scraperapi-us", api_key, "us")])

    for label, key, country_code in sources:
        print(f"[{label}] fetching public profile...", file=sys.stderr)
        try:
            html = fetch_profile(scholar_id, api_key=key, country_code=country_code)
        except RuntimeError as error:
            print(f"[{label}] failed: {error}", file=sys.stderr)
            continue

        try:
            return parse_author(html, scholar_id)
        except (AttributeError, IndexError, KeyError, TypeError, ValueError) as error:
            print(f"[{label}] invalid author profile ({type(error).__name__})", file=sys.stderr)

    raise SystemExit("Could not fetch valid Google Scholar data. Keeping the last published data.")


def main():
    author = fetch_author(os.environ["GOOGLE_SCHOLAR_ID"].strip(), os.environ.get("SCRAPERAPI_KEY"))
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

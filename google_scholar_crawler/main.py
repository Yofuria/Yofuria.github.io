"""Fetch Google Scholar stats and write them to results/*.json.

Prefer SerpApi's structured author API, with public-page fallbacks.
A failed crawl exits before the workflow publishes any files.
"""

import json
import logging
import os
import sys
import time
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


class FetchError(RuntimeError):
    def __init__(self, message, *, retryable=False):
        super().__init__(message)
        self.retryable = retryable


def fetch_page(url, timeout, *, accept="text/html"):
    headers = {
        "Accept": accept,
        "Accept-Language": "en-US,en;q=0.9",
        "User-Agent": SCHOLAR_USER_AGENT,
    }
    request = Request(url, headers=headers)
    try:
        with urlopen(request, timeout=timeout) as response:
            encoding = response.headers.get_content_charset() or "utf-8"
            return response.read().decode(encoding, errors="replace")
    except HTTPError as error:
        # HTTPError includes the request URL, which may contain an API key.
        raise FetchError(
            f"HTTP {error.code}", retryable=error.code == 429 or error.code >= 500
        ) from None
    except (OSError, HTTPException):
        raise FetchError("Request failed or timed out", retryable=True) from None


def count(value):
    if type(value) is not int or value < 0:
        raise ValueError("Expected a non-negative integer count")
    return value


def parse_serpapi(payload, scholar_id):
    """Translate the structured response to the existing Scholar JSON contract."""
    if not isinstance(payload, dict) or payload.get("error"):
        raise ValueError("SerpApi did not return a successful author result")
    metadata = payload["search_metadata"]
    params = payload["search_parameters"]
    if metadata.get("status") != "Success":
        raise ValueError("SerpApi search has not succeeded")
    if params.get("engine") != "google_scholar_author" or params.get("author_id") != scholar_id:
        raise ValueError("SerpApi returned a different author profile")

    # Use the search's timestamp, so a cached response never looks newly fetched.
    updated = datetime.strptime(metadata["created_at"], "%Y-%m-%d %H:%M:%S UTC")
    profile = payload["author"]
    cited_by = payload["cited_by"]
    metrics = {key: value for row in cited_by["table"] for key, value in row.items()}
    author = {
        "container_type": "Author",
        "source": "AUTHOR_PROFILE_PAGE",
        "fetched_via": "serpapi",
        "filled": ["basics", "indices", "counts", "publications"],
        "scholar_id": scholar_id,
        "name": profile["name"],
        "affiliation": profile.get("affiliations", ""),
        "url_picture": profile.get("thumbnail", ""),
        "interests": [item["title"] for item in profile.get("interests", [])],
        "citedby": count(metrics["citations"]["all"]),
        "cites_per_year": {
            str(row["year"]): count(row["citations"]) for row in cited_by.get("graph", [])
        },
        "publications": {},
        "updated": updated.replace(tzinfo=timezone.utc).isoformat(timespec="seconds"),
    }
    for api_name, output_name in (("citations", "citedby"), ("h_index", "hindex"), ("i10_index", "i10index")):
        metric = metrics.get(api_name, {})
        if "all" in metric:
            author[output_name] = count(metric["all"])
        recent = [key for key in metric if key.startswith("since_")]
        if recent:
            author[output_name + "5y"] = count(metric[max(recent)])

    for article in payload.get("articles", []):
        publication_id = article["citation_id"]
        if not publication_id.startswith(scholar_id + ":"):
            raise ValueError("SerpApi returned another author's publication")
        cited = article.get("cited_by", {})
        publication = {
            "container_type": "Publication",
            "source": "AUTHOR_PUBLICATION_ENTRY",
            "filled": False,
            "author_pub_id": publication_id,
            "bib": {
                "title": article["title"],
                "author": article.get("authors", ""),
                "citation": article.get("publication", ""),
                "pub_year": article.get("year", ""),
            },
            "num_citations": count(cited["value"] if cited.get("value") is not None else 0),
        }
        if cited.get("link"):
            publication["citedby_url"] = cited["link"]
        if cited.get("cites_id"):
            publication["cites_id"] = cited["cites_id"].split(",")
        author["publications"][publication_id] = publication
    return author


def fetch_serpapi(scholar_id, api_key):
    query = urlencode({
        "engine": "google_scholar_author",
        "author_id": scholar_id,
        "hl": "en",
        "num": 100,
        "no_cache": "true",
        "api_key": api_key,
    })
    url = "https://serpapi.com/search.json?" + query
    for attempt in range(2):
        try:
            response = fetch_page(url, 45, accept="application/json")
            return parse_serpapi(json.loads(response), scholar_id)
        except FetchError as error:
            if not error.retryable or attempt == 1:
                raise
            print(f"[serpapi] {error}; retrying once...", file=sys.stderr)
            time.sleep(5)


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
    if serpapi_key and serpapi_key.strip():
        print("[serpapi] fetching structured author data...", file=sys.stderr)
        try:
            return fetch_serpapi(scholar_id, serpapi_key.strip())
        except FetchError as error:
            print(f"[serpapi] failed: {error}", file=sys.stderr)
        except (AttributeError, IndexError, KeyError, TypeError, ValueError) as error:
            # Never log the raw response or URL: either could contain the key.
            print(f"[serpapi] invalid author response ({type(error).__name__})", file=sys.stderr)
    else:
        print("[serpapi] SERPAPI_KEY is not configured; trying public-page fallbacks.", file=sys.stderr)

    # The public profile route starts with user=, as allowed by Scholar's robots.txt.
    profile_url = "https://scholar.google.com/citations?" + urlencode({"user": scholar_id, "hl": "en"})
    sources = [("direct", profile_url, 20)]

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
            author = parse_author(html, scholar_id)
            author["fetched_via"] = label
            return author
        except (AttributeError, IndexError, KeyError, TypeError, ValueError) as error:
            print(f"[{label}] invalid author profile ({type(error).__name__})", file=sys.stderr)

    raise SystemExit("Could not fetch valid Google Scholar data. Keeping the last published data.")


def main():
    author = fetch_author(
        os.environ["GOOGLE_SCHOLAR_ID"].strip(),
        serpapi_key=os.environ.get("SERPAPI_KEY"),
        scraperapi_key=os.environ.get("SCRAPERAPI_KEY"),
    )
    author.setdefault("updated", datetime.now(timezone.utc).isoformat(timespec="seconds"))

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

    print(f"OK: source={author['fetched_via']}, citedby={author['citedby']}, "
          f"publications={len(author['publications'])}, updated={author['updated']}")


if __name__ == "__main__":
    main()

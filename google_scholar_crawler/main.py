"""Fetch Google Scholar stats and write them to results/*.json.

Use ScraperAPI when configured, with direct requests and free proxies as
fallbacks. A failed crawl exits before the workflow publishes any files.
"""

import json
import os
import sys
from datetime import datetime

from scholarly import scholarly, ProxyGenerator

SCHOLAR_ID = os.environ["GOOGLE_SCHOLAR_ID"]
SCRAPERAPI_KEY = os.environ.get("SCRAPERAPI_KEY")
OUT_DIR = "results"
SCRAPERAPI_ATTEMPTS = 3
FREE_PROXY_ATTEMPTS = 6


def fetch_author():
    author = scholarly.search_author_id(SCHOLAR_ID)
    scholarly.fill(author, sections=["basics", "indices", "counts", "publications"])
    if author.get("scholar_id") != SCHOLAR_ID:
        raise ValueError("Google Scholar returned a different author profile")
    citations = author.get("citedby")
    if type(citations) is not int or citations < 0:
        raise ValueError("Google Scholar returned an invalid citation count")
    author["publications"] = {p["author_pub_id"]: p for p in author["publications"]}
    return author


def fetch_with_retries():
    # 1) ScraperAPI — paid proxy, by far the most reliable from CI.
    if SCRAPERAPI_KEY:
        for attempt in range(1, SCRAPERAPI_ATTEMPTS + 1):
            try:
                pg = ProxyGenerator()
                if not pg.ScraperAPI(SCRAPERAPI_KEY):
                    print(f"[scraperapi {attempt}] setup returned False", file=sys.stderr)
                    continue
                # A single argument makes scholarly initialize a free proxy
                # for author pages, even when ScraperAPI is already available.
                scholarly.use_proxy(pg, pg)
                print(f"[scraperapi {attempt}] fetching...", file=sys.stderr)
                return fetch_author()
            except Exception as e:  # noqa: BLE001
                print(f"[scraperapi {attempt}] failed: {e}", file=sys.stderr)
    else:
        print("SCRAPERAPI_KEY not set; using direct + free proxies.", file=sys.stderr)

    # 2) Direct attempt — fast when the runner IP isn't blocked.
    try:
        direct = ProxyGenerator()
        scholarly.use_proxy(direct, direct)
        print("[direct] fetching...", file=sys.stderr)
        return fetch_author()
    except Exception as e:  # noqa: BLE001
        print(f"[direct] failed: {e}", file=sys.stderr)

    # 3) Rotate free proxies as a last resort.
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

"""Fetch Google Scholar stats and write them to results/*.json.

Robustness notes:
- Google Scholar frequently blocks requests coming from shared CI IPs.
  We first try a direct request, then rotate free proxies with retries.
- If every attempt fails we write NOTHING and exit 0, so the workflow can
  skip the publish step and keep the last good data instead of overwriting
  it with garbage / breaking the citations badge.
"""

import json
import os
import sys
from datetime import datetime

from scholarly import scholarly, ProxyGenerator

SCHOLAR_ID = os.environ["GOOGLE_SCHOLAR_ID"]
OUT_DIR = "results"
MAX_PROXY_ATTEMPTS = 6


def fetch_author():
    author = scholarly.search_author_id(SCHOLAR_ID)
    scholarly.fill(author, sections=["basics", "indices", "counts", "publications"])
    return author


def fetch_with_retries():
    # 1) Direct attempt — fast when the runner IP isn't blocked.
    try:
        print("[direct] fetching...", file=sys.stderr)
        return fetch_author()
    except Exception as e:  # noqa: BLE001
        print(f"[direct] failed: {e}", file=sys.stderr)

    # 2) Rotate free proxies.
    for attempt in range(1, MAX_PROXY_ATTEMPTS + 1):
        try:
            pg = ProxyGenerator()
            if not pg.FreeProxies():
                print(f"[proxy {attempt}] no free proxy available", file=sys.stderr)
                continue
            scholarly.use_proxy(pg)
            print(f"[proxy {attempt}] got proxy, fetching...", file=sys.stderr)
            return fetch_author()
        except Exception as e:  # noqa: BLE001
            print(f"[proxy {attempt}] failed: {e}", file=sys.stderr)

    return None


def main():
    author = fetch_with_retries()

    # Validate before writing anything.
    if not author or "citedby" not in author:
        print(
            "Could not fetch valid Google Scholar data after all retries. "
            "Leaving existing data untouched.",
            file=sys.stderr,
        )
        # Exit 0 so the workflow succeeds (no red X) and simply skips publish.
        sys.exit(0)

    author["updated"] = str(datetime.now())
    author["publications"] = {v["author_pub_id"]: v for v in author["publications"]}

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

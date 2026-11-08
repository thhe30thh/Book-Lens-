import hashlib
import json
import os
import ssl
import certifi
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


API_URL = "https://openlibrary.org/search.json"

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CACHE_DIR = PROJECT_ROOT / "data" / "cache"


def search_works(query, limit=50, use_cache=True):
    """
    Search Open Library for literary works.

    Results are cached locally to avoid unnecessary API requests.
    This is for targeted discovery, not bulk harvesting.
    """

    query = query.strip()

    if not query:
        raise ValueError("Search query cannot be empty.")

    if not 1 <= limit <= 100:
        raise ValueError("Limit must be between 1 and 100.")

    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    cache_key = hashlib.sha256(
        f"{query}:{limit}".encode("utf-8")
    ).hexdigest()

    cache_file = CACHE_DIR / f"{cache_key}.json"

    if use_cache and cache_file.exists():
        return json.loads(cache_file.read_text(encoding="utf-8"))

    parameters = urlencode({
        "q": query,
        "limit": limit,
        "fields": (
            "key,title,author_name,author_key,"
            "first_publish_year,language,subject,edition_count,type"
        ),
    })

    request = Request(
        f"{API_URL}?{parameters}",
        headers={
            "User-Agent": (
                "BookLens/0.1 "
                "(educational literary discovery project)"
            ),
            "Accept": "application/json",
        },
    )

    try:
        with urlopen(
            request,
            timeout=20,
            context=ssl.create_default_context(cafile=certifi.where()),
        ) as response:
            data = json.loads(response.read().decode("utf-8"))

    except Exception as error:
        raise RuntimeError(
            f"Open Library request failed: {error}"
        ) from error

    if not isinstance(data.get("docs"), list):
        raise ValueError("Unexpected response from Open Library.")

    cache_file.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return data

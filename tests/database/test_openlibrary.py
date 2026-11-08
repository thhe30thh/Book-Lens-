import json

import pytest

from booklens.database import openlibrary


class FakeResponse:
    def __init__(self, data):
        self.data = json.dumps(data).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def read(self):
        return self.data


def test_search_rejects_empty_query():
    with pytest.raises(ValueError, match="cannot be empty"):
        openlibrary.search_works("")


def test_search_rejects_invalid_limit():
    with pytest.raises(ValueError, match="between 1 and 100"):
        openlibrary.search_works("Dostoevsky", limit=101)


def test_search_fetches_and_caches_results(tmp_path, monkeypatch):
    monkeypatch.setattr(openlibrary, "CACHE_DIR", tmp_path)

    sample_data = {
        "numFound": 1,
        "docs": [
            {
                "key": "/works/OL123W",
                "title": "Crime and Punishment",
                "author_name": ["Fyodor Dostoevsky"],
                "first_publish_year": 1866,
                "language": ["rus"],
            }
        ],
    }

    def fake_urlopen(request, timeout, context=None):
        assert "search.json" in request.full_url
        return FakeResponse(sample_data)

    monkeypatch.setattr(openlibrary, "urlopen", fake_urlopen)

    result = openlibrary.search_works("Crime and Punishment")

    assert result["docs"][0]["title"] == "Crime and Punishment"
    assert len(list(tmp_path.glob("*.json"))) == 1


def test_search_uses_cache_without_network(tmp_path, monkeypatch):
    monkeypatch.setattr(openlibrary, "CACHE_DIR", tmp_path)

    sample_data = {
        "numFound": 1,
        "docs": [{"title": "The Stranger"}],
    }

    openlibrary.CACHE_DIR.mkdir(parents=True, exist_ok=True)

    import hashlib

    cache_key = hashlib.sha256(
        "The Stranger:50".encode("utf-8")
    ).hexdigest()

    cache_file = tmp_path / f"{cache_key}.json"
    cache_file.write_text(
        json.dumps(sample_data),
        encoding="utf-8",
    )

    def should_not_run(*args, **kwargs):
        raise AssertionError("Network should not be called.")

    monkeypatch.setattr(openlibrary, "urlopen", should_not_run)

    result = openlibrary.search_works("The Stranger")

    assert result == sample_data

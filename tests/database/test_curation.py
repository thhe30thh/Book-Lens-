from booklens.database.curation import normalize_search_results


def test_normalize_search_results_keeps_valid_works():
    data = {
        "docs": [
            {
                "key": "/works/OL123W",
                "title": "Things Fall Apart",
                "author_name": ["Chinua Achebe"],
                "first_publish_year": 1958,
                "edition_count": 94,
                "subject": ["Colonialism", "Identity"],
                "language": ["eng"],
                "type": "work",
            }
        ]
    }

    result = normalize_search_results(data)

    assert len(result) == 1
    assert result[0]["title"] == "Things Fall Apart"
    assert result[0]["authors"] == ["Chinua Achebe"]
    assert result[0]["review_status"] == "pending"


def test_normalize_search_results_rejects_invalid_records():
    data = {
        "docs": [
            {"title": "Missing author", "type": "work"},
            {
                "key": "/books/OL123M",
                "title": "Edition, not work",
                "author_name": ["Someone"],
                "type": "edition",
            },
        ]
    }

    assert normalize_search_results(data) == []


def test_normalize_search_results_removes_duplicate_work_ids():
    book = {
        "key": "/works/OL123W",
        "title": "Things Fall Apart",
        "author_name": ["Chinua Achebe"],
        "type": "work",
    }

    result = normalize_search_results({"docs": [book, book]})

    assert len(result) == 1


def test_normalize_search_results_handles_empty_results():
    assert normalize_search_results({"docs": []}) == []


def test_export_review_queue_creates_csv(tmp_path):
    from booklens.database.curation import export_review_queue

    candidates = [
        {
            "openlibrary_id": "/works/OL123W",
            "title": "Things Fall Apart",
            "authors": ["Chinua Achebe"],
            "publication_year": 1958,
            "edition_count": 94,
            "subjects": ["Colonialism", "Identity"],
            "edition_languages": ["eng"],
            "review_status": "pending",
        }
    ]

    output = tmp_path / "review" / "books.csv"

    count = export_review_queue(candidates, output)

    assert count == 1
    assert output.exists()

    content = output.read_text(encoding="utf-8")

    assert "Things Fall Apart" in content
    assert "Chinua Achebe" in content

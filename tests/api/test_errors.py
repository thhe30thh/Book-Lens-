from booklens import create_app


def test_api_not_found_returns_json():
    app = create_app("testing")
    client = app.test_client()

    response = client.get("/api/does-not-exist")

    assert response.status_code == 404
    assert response.is_json

    data = response.get_json()

    assert data["error"] == "Not Found"
    assert data["status"] == 404

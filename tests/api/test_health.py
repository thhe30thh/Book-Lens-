from booklens import create_app


def test_health_endpoint_returns_success():
    app = create_app("testing")
    client = app.test_client()

    response = client.get("/api/health")

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "ok"
    assert data["service"] == "booklens"
    assert data["version"] == "0.1.0"
    assert data["environment"] == "testing"

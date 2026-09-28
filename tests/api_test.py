import httpx


BASE_URL = "http://127.0.0.1:8000"


def test_search_documents():
    with httpx.Client(trust_env=False) as client:
        response = client.get(
            f"{BASE_URL}/documents/search",
            params={"q": "а"},
        )

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) <= 20


def test_empty_query():
    with httpx.Client(trust_env=False) as client:
        response = client.get(
            f"{BASE_URL}/documents/search",
            params={"q": ""},
        )

    assert response.status_code == 422

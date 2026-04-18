def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def _auth_headers(client):
    register = client.post(
        "/api/v1/auth/register",
        json={"username": "tester", "password": "StrongPass123"},
    )
    assert register.status_code == 201

    login = client.post(
        "/api/v1/auth/login",
        json={"username": "tester", "password": "StrongPass123"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_book_crud_and_recommendation(client):
    headers = _auth_headers(client)

    payload_1 = {
        "title": "Dune",
        "author": "Frank Herbert",
        "genre": "Sci-Fi",
        "published_year": 1965,
        "average_rating": 4.6,
        "ratings_count": 1200,
        "description": "Classic sci-fi novel.",
    }
    payload_2 = {
        "title": "Neuromancer",
        "author": "William Gibson",
        "genre": "Sci-Fi",
        "published_year": 1984,
        "average_rating": 4.1,
        "ratings_count": 980,
        "description": "Cyberpunk pioneer.",
    }

    create_1 = client.post("/api/v1/books", json=payload_1, headers=headers)
    assert create_1.status_code == 201
    book_1 = create_1.json()

    create_2 = client.post("/api/v1/books", json=payload_2, headers=headers)
    assert create_2.status_code == 201
    book_2 = create_2.json()

    list_resp = client.get("/api/v1/books", headers=headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 2

    update_resp = client.put(
        f"/api/v1/books/{book_2['id']}",
        json={"average_rating": 4.3, "ratings_count": 1100},
        headers=headers,
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["average_rating"] == 4.3

    rec_resp = client.get(
        f"/api/v1/books/{book_1['id']}/recommendations?limit=3",
        headers=headers,
    )
    assert rec_resp.status_code == 200
    assert rec_resp.json()["seed_book_id"] == book_1["id"]
    assert len(rec_resp.json()["recommendations"]) >= 1

    analytics_genre = client.get("/api/v1/analytics/genres", headers=headers)
    assert analytics_genre.status_code == 200
    assert len(analytics_genre.json()["genres"]) >= 1

    analytics_rating = client.get("/api/v1/analytics/ratings", headers=headers)
    assert analytics_rating.status_code == 200
    assert analytics_rating.json()["total_books"] == 2

    delete_resp = client.delete(f"/api/v1/books/{book_1['id']}", headers=headers)
    assert delete_resp.status_code == 204

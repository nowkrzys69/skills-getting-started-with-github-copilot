from src.app import activities


def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_details(client):
    response = client.get("/activities")

    assert response.status_code == 200
    assert "Chess Club" in response.json()
    assert set(response.json()["Chess Club"]) == {
        "description",
        "schedule",
        "max_participants",
        "participants",
    }


def test_signup_adds_participant(client):
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 200
    assert "student@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_rejects_unknown_activity(client):
    response = client.post(
        "/activities/Unknown/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404


def test_signup_requires_email(client):
    response = client.post("/activities/Chess Club/signup")

    assert response.status_code == 422


def test_signup_rejects_duplicate_participant(client):
    existing_email = activities["Chess Club"]["participants"][0]

    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": existing_email},
    )

    assert response.status_code == 400


def test_signup_rejects_full_activity(client):
    activity = activities["Art Club"]
    activity["participants"] = [
        f"student-{number}@mergington.edu"
        for number in range(activity["max_participants"])
    ]

    response = client.post(
        "/activities/Art Club/signup",
        params={"email": "late-student@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"
    assert "late-student@mergington.edu" not in activity["participants"]


def test_delete_removes_participant(client):
    existing_email = activities["Chess Club"]["participants"][0]

    response = client.delete(
        f"/activities/Chess Club/participants/{existing_email}"
    )

    assert response.status_code == 200
    assert existing_email not in client.get("/activities").json()["Chess Club"]["participants"]


def test_delete_rejects_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown/participants/student%40mergington.edu"
    )

    assert response.status_code == 404


def test_delete_rejects_missing_participant(client):
    response = client.delete(
        "/activities/Chess Club/participants/missing%40mergington.edu"
    )

    assert response.status_code == 404

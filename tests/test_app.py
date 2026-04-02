import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Reset activities to initial state before each test"""
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Practice and compete in basketball games",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": []
        },
        "Soccer Club": {
            "description": "Train and play soccer matches",
            "schedule": "Wednesdays and Saturdays, 3:00 PM - 5:00 PM",
            "max_participants": 22,
            "participants": []
        },
        "Art Club": {
            "description": "Explore various art forms and create projects",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": []
        },
        "Drama Club": {
            "description": "Act in plays and improve theatrical skills",
            "schedule": "Fridays, 4:00 PM - 6:00 PM",
            "max_participants": 20,
            "participants": []
        },
        "Debate Club": {
            "description": "Develop argumentation and public speaking skills",
            "schedule": "Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 16,
            "participants": []
        },
        "Science Club": {
            "description": "Conduct experiments and learn about scientific concepts",
            "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
            "max_participants": 14,
            "participants": []
        }
    })
    return TestClient(app)


def test_get_activities(client):
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert data["Chess Club"]["max_participants"] == 12
    assert len(data["Chess Club"]["participants"]) == 2


def test_signup_success(client):
    response = client.post("/activities/Chess%20Club/signup?email=newstudent@mergington.edu")
    assert response.status_code == 200
    result = response.json()
    assert "Signed up newstudent@mergington.edu for Chess Club" == result["message"]


def test_signup_duplicate(client):
    # First signup
    client.post("/activities/Chess%20Club/signup?email=duplicate@mergington.edu")
    # Second signup should fail
    response = client.post("/activities/Chess%20Club/signup?email=duplicate@mergington.edu")
    assert response.status_code == 400
    result = response.json()
    assert "Student already signed up for this activity" == result["detail"]


def test_signup_activity_not_found(client):
    response = client.post("/activities/Nonexistent%20Club/signup?email=test@mergington.edu")
    assert response.status_code == 404
    result = response.json()
    assert "Activity not found" == result["detail"]


def test_signup_full_activity(client):
    # Fill up Chess Club (max 12, already 2, so add 10 more)
    for i in range(10):
        client.post(f"/activities/Chess%20Club/signup?email=user{i}@mergington.edu")
    # Next should fail
    response = client.post("/activities/Chess%20Club/signup?email=overflow@mergington.edu")
    assert response.status_code == 400
    result = response.json()
    assert "Activity is full" == result["detail"]


def test_remove_participant_success(client):
    response = client.delete("/activities/Chess%20Club/participants?email=michael@mergington.edu")
    assert response.status_code == 200
    result = response.json()
    assert "Removed michael@mergington.edu from Chess Club" == result["message"]


def test_remove_participant_not_found(client):
    response = client.delete("/activities/Chess%20Club/participants?email=nonexistent@mergington.edu")
    assert response.status_code == 404
    result = response.json()
    assert "Participant not found in activity" == result["detail"]


def test_remove_participant_activity_not_found(client):
    response = client.delete("/activities/Nonexistent%20Club/participants?email=test@mergington.edu")
    assert response.status_code == 404
    result = response.json()
    assert "Activity not found" == result["detail"]


def test_root_redirect(client):
    response = client.get("/")
    assert response.status_code == 307  # RedirectResponse
    assert "/static/index.html" in response.headers.get("location", "")
from copy import deepcopy

from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)
INITIAL_ACTIVITIES = deepcopy(activities)


def setup_function():
    activities.clear()
    activities.update(deepcopy(INITIAL_ACTIVITIES))


def test_get_activities_returns_expected_structure():
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert expected_activity in data
    assert data[expected_activity]["max_participants"] == 12
    assert isinstance(data[expected_activity]["participants"], list)


def test_signup_adds_participant():
    # Arrange
    test_email = "testuser@example.com"
    activity_name = "Chess Club"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": test_email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {test_email} for {activity_name}"}
    assert test_email in activities[activity_name]["participants"]


def test_duplicate_signup_returns_400():
    # Arrange
    existing_email = "michael@mergington.edu"
    activity_name = "Chess Club"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": existing_email},
    )

    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()


def test_remove_participant_from_activity():
    # Arrange
    participant_email = "michael@mergington.edu"
    activity_name = "Chess Club"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": participant_email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {participant_email} from {activity_name}"}
    assert participant_email not in activities[activity_name]["participants"]


def test_remove_nonexistent_participant_returns_404():
    # Arrange
    participant_email = "not-a-real-user@example.com"
    activity_name = "Chess Club"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": participant_email},
    )

    # Assert
    assert response.status_code == 404
    assert "participant not found" in response.json()["detail"].lower()


def test_signup_for_unknown_activity_returns_404():
    # Arrange
    test_email = "newstudent@example.com"
    activity_name = "Unknown Activity"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": test_email},
    )

    # Assert
    assert response.status_code == 404
    assert "activity not found" in response.json()["detail"].lower()

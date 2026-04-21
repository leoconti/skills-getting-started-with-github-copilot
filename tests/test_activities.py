"""
Tests for the Mergington High School Activities API.
Uses the AAA (Arrange-Act-Assert) pattern for test structure.
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """
        Arrange: Prepare client with test data
        Act: Call GET /activities
        Assert: Verify response contains all activities
        """
        # Arrange - client fixture provides test activities

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities

    def test_get_activities_includes_participant_count(self, client):
        """
        Arrange: Prepare client with test data
        Act: Call GET /activities
        Assert: Verify each activity has correct participant information
        """
        # Arrange - client fixture provides test activities

        # Act
        response = client.get("/activities")

        # Assert
        activities = response.json()
        chess = activities["Chess Club"]
        assert chess["max_participants"] == 12
        assert len(chess["participants"]) == 2
        assert "michael@mergington.edu" in chess["participants"]


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_success(self, client, test_activities):
        """
        Arrange: Set up new student email
        Act: Call POST signup endpoint
        Assert: Verify student is added to activity
        """
        # Arrange
        new_student = "newstudent@mergington.edu"
        activity_name = "Chess Club"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={new_student}"
        )

        # Assert
        assert response.status_code == 200
        assert new_student in test_activities[activity_name]["participants"]
        assert response.json()["message"] == f"Signed up {new_student} for {activity_name}"

    def test_signup_nonexistent_activity(self, client):
        """
        Arrange: Prepare request for non-existent activity
        Act: Call POST signup endpoint
        Assert: Verify 404 error response
        """
        # Arrange
        email = "student@mergington.edu"
        nonexistent_activity = "Nonexistent Activity"

        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_duplicate_student(self, client):
        """
        Arrange: Use a student already registered for an activity
        Act: Attempt to sign up the same student again
        Assert: Verify 400 error for duplicate signup
        """
        # Arrange
        existing_student = "michael@mergington.edu"
        activity_name = "Chess Club"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={existing_student}"
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_multiple_students(self, client, test_activities):
        """
        Arrange: Prepare two different students
        Act: Sign up both students for the same activity
        Assert: Verify both are successfully added
        """
        # Arrange
        student1 = "alice@mergington.edu"
        student2 = "bob@mergington.edu"
        activity_name = "Gym Class"

        # Act
        response1 = client.post(
            f"/activities/{activity_name}/signup?email={student1}"
        )
        response2 = client.post(
            f"/activities/{activity_name}/signup?email={student2}"
        )

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert student1 in test_activities[activity_name]["participants"]
        assert student2 in test_activities[activity_name]["participants"]


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/signup endpoint."""

    def test_unregister_success(self, client, test_activities):
        """
        Arrange: Set up student currently registered for activity
        Act: Call DELETE signup endpoint
        Assert: Verify student is removed from activity
        """
        # Arrange
        student_to_remove = "michael@mergington.edu"
        activity_name = "Chess Club"
        assert student_to_remove in test_activities[activity_name]["participants"]

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup?email={student_to_remove}"
        )

        # Assert
        assert response.status_code == 200
        assert student_to_remove not in test_activities[activity_name]["participants"]
        assert (
            response.json()["message"]
            == f"Unregistered {student_to_remove} from {activity_name}"
        )

    def test_unregister_nonexistent_activity(self, client):
        """
        Arrange: Prepare request for non-existent activity
        Act: Call DELETE signup endpoint
        Assert: Verify 404 error response
        """
        # Arrange
        email = "student@mergington.edu"
        nonexistent_activity = "Nonexistent Activity"

        # Act
        response = client.delete(
            f"/activities/{nonexistent_activity}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_student_not_registered(self, client):
        """
        Arrange: Use a student not registered for an activity
        Act: Attempt to unregister them
        Assert: Verify 400 error response
        """
        # Arrange
        unregistered_student = "notregistered@mergington.edu"
        activity_name = "Chess Club"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup?email={unregistered_student}"
        )

        # Assert
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]

    def test_unregister_then_signup_again(self, client, test_activities):
        """
        Arrange: Set up a registered student
        Act: Unregister and then re-register them
        Assert: Verify student is back in the activity
        """
        # Arrange
        student = "daniel@mergington.edu"
        activity_name = "Chess Club"

        # Act
        delete_response = client.delete(
            f"/activities/{activity_name}/signup?email={student}"
        )
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={student}"
        )

        # Assert
        assert delete_response.status_code == 200
        assert signup_response.status_code == 200
        assert student in test_activities[activity_name]["participants"]


class TestRedirect:
    """Tests for GET / endpoint."""

    def test_root_redirects_to_static_index(self, client):
        """
        Arrange: Prepare client
        Act: Call GET /
        Assert: Verify redirect to /static/index.html
        """
        # Arrange - client fixture provides TestClient

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"

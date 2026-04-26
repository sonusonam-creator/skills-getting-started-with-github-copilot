"""
Comprehensive test suite for Mergington High School API
Tests follow the AAA (Arrange-Act-Assert) pattern for clarity.
"""

import pytest
from fastapi.testclient import TestClient
from copy import deepcopy
from src.app import app, activities


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def client():
    """Fixture providing a TestClient for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Fixture to reset activities to initial state before each test."""
    original_activities = deepcopy(activities)
    yield
    # Restore original state after test
    activities.clear()
    activities.update(original_activities)


# ============================================================================
# GET /ACTIVITIES TESTS
# ============================================================================

class TestGetActivities:
    """Tests for the GET /activities endpoint"""

    def test_get_activities_returns_success(self, client, reset_activities):
        """Test that GET /activities returns status 200"""
        # Arrange
        # (no setup needed)
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200

    def test_get_activities_returns_dict(self, client, reset_activities):
        """Test that response is a dictionary of activities"""
        # Arrange
        # (no setup needed)
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert isinstance(data, dict)
        assert len(data) > 0

    def test_get_activities_contains_expected_activities(self, client, reset_activities):
        """Test that response contains all expected activities"""
        # Arrange
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class", "Basketball Team",
            "Tennis Club", "Art Studio", "Drama Club", "Debate Team", "Science Club"
        ]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        for activity in expected_activities:
            assert activity in data

    def test_get_activities_structure(self, client, reset_activities):
        """Test that each activity has required fields"""
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        for activity_name, activity_data in data.items():
            for field in required_fields:
                assert field in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_participants(self, client, reset_activities):
        """Test that participants are correctly stored"""
        # Arrange
        expected_chess_participants = ["michael@mergington.edu", "daniel@mergington.edu"]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        chess_club_participants = data["Chess Club"]["participants"]
        
        # Assert
        for email in expected_chess_participants:
            assert email in chess_club_participants


# ============================================================================
# POST /ACTIVITIES/{ACTIVITY_NAME}/SIGNUP TESTS
# ============================================================================

class TestSignup:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self, client, reset_activities):
        """Test successful signup"""
        # Arrange
        activity_name = "Chess Club"
        new_email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "message" in response.json()

    def test_signup_adds_participant(self, client, reset_activities):
        """Test that signup adds participant to activity"""
        # Arrange
        activity_name = "Chess Club"
        new_email = "newstudent@mergington.edu"
        
        # Act
        client.post(f"/activities/{activity_name}/signup", params={"email": new_email})
        response = client.get("/activities")
        participants = response.json()[activity_name]["participants"]
        
        # Assert
        assert new_email in participants

    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test signup to non-existent activity returns 404"""
        # Arrange
        nonexistent_activity = "Fake Club"
        test_email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup",
            params={"email": test_email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_multiple_students(self, client, reset_activities):
        """Test multiple students can signup to same activity"""
        # Arrange
        activity_name = "Chess Club"
        emails = ["student1@mergington.edu", "student2@mergington.edu"]
        
        # Act
        for email in emails:
            response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
            assert response.status_code == 200
        
        response = client.get("/activities")
        participants = response.json()[activity_name]["participants"]
        
        # Assert
        for email in emails:
            assert email in participants

    def test_signup_same_student_multiple_activities(self, client, reset_activities):
        """Test same student can signup for multiple activities"""
        # Arrange
        email = "versatile@mergington.edu"
        activities_list = ["Chess Club", "Programming Class", "Tennis Club"]
        
        # Act
        for activity in activities_list:
            response = client.post(f"/activities/{activity}/signup", params={"email": email})
            assert response.status_code == 200
        
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        for activity in activities_list:
            assert email in data[activity]["participants"]

    def test_signup_returns_message(self, client, reset_activities):
        """Test that signup response includes descriptive message"""
        # Arrange
        activity_name = "Programming Class"
        test_email = "cs_student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        data = response.json()
        
        # Assert
        assert "message" in data
        assert test_email in data["message"]
        assert activity_name in data["message"]


# ============================================================================
# DELETE /ACTIVITIES/{ACTIVITY_NAME}/PARTICIPANTS TESTS
# ============================================================================

class TestRemoveParticipant:
    """Tests for the DELETE /activities/{activity_name}/participants endpoint"""

    def test_remove_participant_success(self, client, reset_activities):
        """Test successful removal of participant"""
        # Arrange
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email_to_remove}
        )
        
        # Assert
        assert response.status_code == 200
        assert "message" in response.json()

    def test_remove_participant_actually_removes(self, client, reset_activities):
        """Test that participant is actually removed from activity"""
        # Arrange
        activity_name = "Chess Club"
        email_to_remove = "daniel@mergington.edu"
        
        # Act
        client.delete(f"/activities/{activity_name}/participants", params={"email": email_to_remove})
        response = client.get("/activities")
        participants = response.json()[activity_name]["participants"]
        
        # Assert
        assert email_to_remove not in participants

    def test_remove_nonexistent_participant(self, client, reset_activities):
        """Test removing non-existent participant returns 404"""
        # Arrange
        activity_name = "Chess Club"
        nonexistent_email = "nonexistent@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": nonexistent_email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]

    def test_remove_from_nonexistent_activity(self, client, reset_activities):
        """Test removing from non-existent activity returns 404"""
        # Arrange
        nonexistent_activity = "Fake Club"
        test_email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{nonexistent_activity}/participants",
            params={"email": test_email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_remove_returns_descriptive_message(self, client, reset_activities):
        """Test that remove response includes descriptive message"""
        # Arrange
        activity_name = "Programming Class"
        email = "emma@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        data = response.json()
        
        # Assert
        assert "message" in data
        assert "Removed" in data["message"]
        assert email in data["message"]


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests for multiple operations"""

    def test_signup_and_remove_flow(self, client, reset_activities):
        """Test complete signup and removal flow"""
        # Arrange
        activity_name = "Programming Class"
        new_email = "flow_test@mergington.edu"
        
        # Act - Sign up
        signup_response = client.post(f"/activities/{activity_name}/signup", params={"email": new_email})
        assert signup_response.status_code == 200
        
        # Assert - Verify in list
        get_response = client.get("/activities")
        assert new_email in get_response.json()[activity_name]["participants"]
        
        # Act - Remove
        remove_response = client.delete(f"/activities/{activity_name}/participants", params={"email": new_email})
        assert remove_response.status_code == 200
        
        # Assert - Verify removed
        final_response = client.get("/activities")
        assert new_email not in final_response.json()[activity_name]["participants"]

    def test_multiple_operations_preserve_state(self, client, reset_activities):
        """Test that multiple operations preserve state correctly"""
        # Arrange
        activity_name = "Chess Club"
        new_participants = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        
        # Act - Add 3 participants
        for email in new_participants:
            client.post(f"/activities/{activity_name}/signup", params={"email": email})
        
        # Act - Remove middle one
        client.delete(f"/activities/{activity_name}/participants", params={"email": new_participants[1]})
        
        # Assert - Verify state
        response = client.get("/activities")
        participants = response.json()[activity_name]["participants"]
        assert new_participants[0] in participants
        assert new_participants[1] not in participants
        assert new_participants[2] in participants

    def test_concurrent_signups_to_different_activities(self, client, reset_activities):
        """Test that signups to different activities don't interfere"""
        # Arrange
        email = "concurrent_test@mergington.edu"
        activities_to_join = ["Chess Club", "Tennis Club", "Drama Club"]
        
        # Act
        for activity in activities_to_join:
            response = client.post(f"/activities/{activity}/signup", params={"email": email})
            assert response.status_code == 200
        
        # Assert
        response = client.get("/activities")
        data = response.json()
        for activity in activities_to_join:
            assert email in data[activity]["participants"]

    def test_remove_then_readd_participant(self, client, reset_activities):
        """Test that removed participant can be re-added"""
        # Arrange
        activity_name = "Basketball Team"
        email = "james@mergington.edu"
        
        # Act - Remove
        client.delete(f"/activities/{activity_name}/participants", params={"email": email})
        response = client.get("/activities")
        
        # Assert - Verify removed
        assert email not in response.json()[activity_name]["participants"]
        
        # Act - Re-add
        client.post(f"/activities/{activity_name}/signup", params={"email": email})
        response = client.get("/activities")
        
        # Assert - Verify re-added
        assert email in response.json()[activity_name]["participants"]

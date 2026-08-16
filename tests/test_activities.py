"""
Test suite for Mergington High School Activities API.

Tests are structured using the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test data and preconditions
- Act: Call the endpoint being tested
- Assert: Verify the response and side effects

Each test uses fresh fixtures, ensuring isolation and preventing test interdependencies.
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""
    
    def test_get_all_activities_returns_success(self, client):
        """Arrange-Act-Assert: Verify endpoint returns all activities."""
        # Act: Fetch all activities
        response = client.get("/activities")
        
        # Assert: Verify response structure and content
        assert response.status_code == 200
        activities = response.json()
        
        # Verify all expected activities are present
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities
    
    def test_activities_have_required_fields(self, client):
        """Arrange-Act-Assert: Verify activity objects have all required fields."""
        # Act: Fetch activities
        response = client.get("/activities")
        activities = response.json()
        
        # Assert: Check structure of each activity
        chess_club = activities["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)
    
    def test_participant_counts_are_accurate(self, client):
        """Arrange-Act-Assert: Verify participant lists match expected counts."""
        # Act: Fetch activities
        response = client.get("/activities")
        activities = response.json()
        
        # Assert: Verify participant counts
        assert len(activities["Chess Club"]["participants"]) == 2
        assert len(activities["Programming Class"]["participants"]) == 2
        assert len(activities["Gym Class"]["participants"]) == 2


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""
    
    def test_successful_signup(self, client):
        """Arrange-Act-Assert: Verify student can successfully sign up for activity."""
        # Arrange: Prepare test data
        activity_name = "Chess Club"
        new_student = "alice@mergington.edu"
        
        # Act: Sign up for activity
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_student}
        )
        
        # Assert: Verify successful response and participant was added
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert new_student in data["message"]
    
    def test_participant_added_to_activity(self, client):
        """Arrange-Act-Assert: Verify participant appears in activity list after signup."""
        # Arrange: Prepare student to sign up
        activity_name = "Chess Club"
        new_student = "bob@mergington.edu"
        
        # Act: Sign up and then fetch activities
        client.post(f"/activities/{activity_name}/signup", params={"email": new_student})
        response = client.get("/activities")
        activities = response.json()
        
        # Assert: Verify student is in participants list
        assert new_student in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == 3  # 2 original + 1 new
    
    def test_duplicate_signup_returns_400_error(self, client):
        """Arrange-Act-Assert: Verify duplicate signup is rejected."""
        # Arrange: Use an already-registered participant
        activity_name = "Chess Club"
        existing_student = "michael@mergington.edu"
        
        # Act: Try to sign up again
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_student}
        )
        
        # Assert: Verify error response
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_duplicate_signup_doesnt_add_participant(self, client):
        """Arrange-Act-Assert: Verify duplicate signup doesn't modify participants list."""
        # Arrange: Get initial state
        activity_name = "Chess Club"
        existing_student = "michael@mergington.edu"
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])
        
        # Act: Try duplicate signup
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_student}
        )
        
        # Assert: Verify participant count unchanged
        final_response = client.get("/activities")
        final_count = len(final_response.json()[activity_name]["participants"])
        assert initial_count == final_count
    
    def test_signup_for_nonexistent_activity_returns_404(self, client):
        """Arrange-Act-Assert: Verify signup for non-existent activity is rejected."""
        # Arrange: Use a non-existent activity name
        activity_name = "Nonexistent Club"
        student = "test@mergington.edu"
        
        # Act: Try to sign up for non-existent activity
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student}
        )
        
        # Assert: Verify 404 error
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/remove endpoint."""
    
    def test_successful_removal(self, client):
        """Arrange-Act-Assert: Verify student can be removed from activity."""
        # Arrange: Prepare removal of existing participant
        activity_name = "Chess Club"
        participant = "michael@mergington.edu"
        
        # Act: Remove participant
        response = client.delete(
            f"/activities/{activity_name}/remove",
            params={"email": participant}
        )
        
        # Assert: Verify successful response
        assert response.status_code == 200
        data = response.json()
        assert "Removed" in data["message"]
        assert participant in data["message"]
    
    def test_participant_removed_from_activity(self, client):
        """Arrange-Act-Assert: Verify participant is removed from activity list."""
        # Arrange: Prepare removal
        activity_name = "Chess Club"
        participant = "daniel@mergington.edu"
        
        # Act: Remove participant and fetch updated activities
        client.delete(
            f"/activities/{activity_name}/remove",
            params={"email": participant}
        )
        response = client.get("/activities")
        activities = response.json()
        
        # Assert: Verify participant is gone
        assert participant not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == 1
    
    def test_remove_nonexistent_participant_returns_400(self, client):
        """Arrange-Act-Assert: Verify removal of non-existent participant is rejected."""
        # Arrange: Use a student not signed up for this activity
        activity_name = "Chess Club"
        non_participant = "notasigned@mergington.edu"
        
        # Act: Try to remove non-existent participant
        response = client.delete(
            f"/activities/{activity_name}/remove",
            params={"email": non_participant}
        )
        
        # Assert: Verify 400 error
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"].lower()
    
    def test_remove_from_nonexistent_activity_returns_404(self, client):
        """Arrange-Act-Assert: Verify removal from non-existent activity is rejected."""
        # Arrange: Use non-existent activity
        activity_name = "Nonexistent Club"
        email = "test@mergington.edu"
        
        # Act: Try to remove from non-existent activity
        response = client.delete(
            f"/activities/{activity_name}/remove",
            params={"email": email}
        )
        
        # Assert: Verify 404 error
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_removal_doesnt_affect_other_participants(self, client):
        """Arrange-Act-Assert: Verify removing one participant doesn't affect others."""
        # Arrange: Get initial state for verification
        activity_name = "Chess Club"
        removed_student = "michael@mergington.edu"
        remaining_student = "daniel@mergington.edu"
        
        # Act: Remove one participant
        client.delete(
            f"/activities/{activity_name}/remove",
            params={"email": removed_student}
        )
        response = client.get("/activities")
        
        # Assert: Verify removed student is gone, others remain
        activities = response.json()
        assert removed_student not in activities[activity_name]["participants"]
        assert remaining_student in activities[activity_name]["participants"]


class TestSignupAndRemoveIntegration:
    """Integration tests combining signup and removal flows."""
    
    def test_signup_then_remove_flow(self, client):
        """Arrange-Act-Assert: Verify signup followed by removal works correctly."""
        # Arrange: Prepare test data
        activity_name = "Programming Class"
        new_student = "charlie@mergington.edu"
        
        # Act: Sign up for activity
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_student}
        )
        
        # Assert: Verify signup succeeded
        assert signup_response.status_code == 200
        response = client.get("/activities")
        assert new_student in response.json()[activity_name]["participants"]
        initial_count = len(response.json()[activity_name]["participants"])
        
        # Act: Remove the participant
        remove_response = client.delete(
            f"/activities/{activity_name}/remove",
            params={"email": new_student}
        )
        
        # Assert: Verify removal succeeded and count decreased
        assert remove_response.status_code == 200
        response = client.get("/activities")
        assert new_student not in response.json()[activity_name]["participants"]
        assert len(response.json()[activity_name]["participants"]) == initial_count - 1
    
    def test_participant_count_accuracy_after_modifications(self, client):
        """Arrange-Act-Assert: Verify participant counts stay accurate through operations."""
        # Arrange: Get initial counts
        activity_name = "Gym Class"
        response = client.get("/activities")
        initial_count = len(response.json()[activity_name]["participants"])
        
        # Act: Perform multiple signups
        new_students = ["student1@mergington.edu", "student2@mergington.edu"]
        for student in new_students:
            client.post(
                f"/activities/{activity_name}/signup",
                params={"email": student}
            )
        
        # Assert: Verify count after signups
        response = client.get("/activities")
        assert len(response.json()[activity_name]["participants"]) == initial_count + 2
        
        # Act: Remove one student
        client.delete(
            f"/activities/{activity_name}/remove",
            params={"email": new_students[0]}
        )
        
        # Assert: Verify final count is correct
        response = client.get("/activities")
        assert len(response.json()[activity_name]["participants"]) == initial_count + 1
    
    def test_cannot_signup_after_removal_then_signup_again(self, client):
        """Arrange-Act-Assert: Verify student can re-signup after being removed."""
        # Arrange: Prepare test data
        activity_name = "Chess Club"
        student = "testuser@mergington.edu"
        
        # Act: First signup
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student}
        )
        assert response1.status_code == 200
        
        # Act: Remove the student
        response2 = client.delete(
            f"/activities/{activity_name}/remove",
            params={"email": student}
        )
        assert response2.status_code == 200
        
        # Act: Re-signup the student
        response3 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student}
        )
        
        # Assert: Verify re-signup succeeded
        assert response3.status_code == 200
        response = client.get("/activities")
        assert student in response.json()[activity_name]["participants"]

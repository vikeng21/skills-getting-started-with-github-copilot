"""
Tests for the Mergington High School Activities API
"""

from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestActivities:
    """Test the /activities endpoint"""

    def test_get_activities(self):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Tennis Club" in data
        assert "Basketball Team" in data
        assert "participants" in data["Tennis Club"]

    def test_activities_structure(self):
        """Test that activities have the correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignup:
    """Test the /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self):
        """Test successful signup"""
        email = "testuser@mergington.edu"
        activity = "Tennis Club"
        
        # Get initial participant count
        initial = client.get("/activities").json()
        initial_count = len(initial[activity]["participants"])
        
        # Sign up
        response = client.post(
            f"/activities/{activity}/signup?email={email}",
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        
        # Verify participant was added
        after = client.get("/activities").json()
        assert len(after[activity]["participants"]) == initial_count + 1
        assert email in after[activity]["participants"]

    def test_signup_duplicate(self):
        """Test that duplicate signup fails"""
        email = "alex@mergington.edu"
        activity = "Tennis Club"
        
        response = client.post(
            f"/activities/{activity}/signup?email={email}",
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity(self):
        """Test signup for non-existent activity"""
        email = "test@mergington.edu"
        activity = "Nonexistent Activity"
        
        response = client.post(
            f"/activities/{activity}/signup?email={email}",
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]


class TestUnregister:
    """Test the /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success(self):
        """Test successful unregistration"""
        email = "testuser2@mergington.edu"
        activity = "Basketball Team"
        
        # First sign up
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Get count before unregister
        before = client.get("/activities").json()
        before_count = len(before[activity]["participants"])
        
        # Unregister
        response = client.delete(
            f"/activities/{activity}/unregister?email={email}",
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        
        # Verify participant was removed
        after = client.get("/activities").json()
        assert len(after[activity]["participants"]) == before_count - 1
        assert email not in after[activity]["participants"]

    def test_unregister_not_signed_up(self):
        """Test unregister for someone not signed up"""
        email = "notregistered@mergington.edu"
        activity = "Tennis Club"
        
        response = client.delete(
            f"/activities/{activity}/unregister?email={email}",
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]

    def test_unregister_nonexistent_activity(self):
        """Test unregister from non-existent activity"""
        email = "test@mergington.edu"
        activity = "Nonexistent Activity"
        
        response = client.delete(
            f"/activities/{activity}/unregister?email={email}",
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]


class TestRoot:
    """Test the root endpoint"""

    def test_root_redirect(self):
        """Test that root redirects to static files"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"

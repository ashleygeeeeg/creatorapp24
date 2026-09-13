"""Tests for build endpoints."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime, timezone
import uuid

from backend.server import app, create_token, hash_password

client = TestClient(app)


class TestCreateBuild:
    """Tests for create build endpoint."""

    @patch('backend.server.db')
    def test_create_build_success_first_free(self, mock_db):
        """Test creating first build (should be free)."""
        mock_builds = AsyncMock()
        mock_builds.count_documents.return_value = 0
        mock_builds.insert_one.return_value = None
        mock_db.builds = mock_builds
        
        mock_users = AsyncMock()
        mock_users.find_one.return_value = {
            "id": "test-user-id",
            "email": "test@example.com",
            "name": "Test User",
            "has_free_build": True
        }
        mock_users.update_one.return_value = None
        mock_db.users = mock_users
        
        with patch('backend.server.uuid.uuid4') as mock_uuid:
            mock_uuid.return_value = uuid.UUID('12345678-1234-5678-1234-567812345678')
            
            headers = {"Authorization": f"Bearer {create_token("test-user-id", "test@example.com")}"}
            response = client.post(
                "/api/builds",
                json={"name": "Test Build", "description": "A test build"},
                headers=headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == "12345678-1234-5678-1234-567812345678"
            assert data["name"] == "Test Build"
            assert data["description"] == "A test build"
            assert data["is_free"] is True
            assert data["payment_status"] == "free"
            assert data["status"] == "draft"

    @patch('backend.server.db')
    def test_create_build_success_paid(self, mock_db):
        """Test creating a paid build (after first free build)."""
        mock_builds = AsyncMock()
        mock_builds.count_documents.return_value = 1  # Already has one build
        mock_builds.insert_one.return_value = None
        mock_db.builds = mock_builds
        
        mock_users = AsyncMock()
        mock_users.find_one.return_value = {
            "id": "test-user-id",
            "email": "test@example.com",
            "name": "Test User",
            "has_free_build": False  # Already used free build
        }
        mock_users.update_one.return_value = None
        mock_db.users = mock_users
        
        with patch('backend.server.uuid.uuid4') as mock_uuid:
            mock_uuid.return_value = uuid.UUID('12345678-1234-5678-1234-567812345678')
            
            headers = {"Authorization": f"Bearer {create_token("test-user-id", "test@example.com")}"}
            response = client.post(
                "/api/builds",
                json={"name": "Paid Build"},
                headers=headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["is_free"] is False
            assert data["payment_status"] == "pending"
            assert data["price"] == 10.0

    @patch('backend.server.db')
    def test_create_build_without_auth(self, mock_db):
        """Test creating build without authentication."""
        response = client.post(
            "/api/builds",
            json={"name": "Test Build"}
        )
        
        assert response.status_code == 401

    @patch('backend.server.db')
    def test_create_build_missing_name(self, mock_db):
        """Test creating build with missing name."""
        headers = {"Authorization": f"Bearer {create_token("test-user-id", "test@example.com")}"}
        response = client.post(
            "/api/builds",
            json={"description": "A test build"},
            headers=headers
        )
        
        assert response.status_code == 422

    @patch('backend.server.db')
    def test_create_build_empty_description(self, mock_db):
        """Test creating build with empty description."""
        mock_builds = AsyncMock()
        mock_builds.count_documents.return_value = 0
        mock_builds.insert_one.return_value = None
        mock_db.builds = mock_builds
        
        mock_users = AsyncMock()
        mock_users.find_one.return_value = {
            "id": "test-user-id",
            "email": "test@example.com",
            "has_free_build": True
        }
        mock_users.update_one.return_value = None
        mock_db.users = mock_users
        
        with patch('backend.server.uuid.uuid4') as mock_uuid:
            mock_uuid.return_value = uuid.UUID('12345678-1234-5678-1234-567812345678')
            
            headers = {"Authorization": f"Bearer {create_token("test-user-id", "test@example.com")}"}
            response = client.post(
                "/api/builds",
                json={"name": "Test Build", "description": ""},
                headers=headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["description"] == ""


class TestGetBuilds:
    """Tests for get builds endpoint."""

    @patch('backend.server.db')
    def test_get_builds_success(self, mock_db):
        """Test getting user's builds."""
        mock_builds = AsyncMock()
        mock_builds.find.return_value = MagicMock()
        mock_builds.find.return_value.sort.return_value.to_list.return_value = [
            {
                "id": "build-1",
                "user_id": "test-user-id",
                "name": "Build 1",
                "description": "First build",
                "status": "draft",
                "is_free": True,
                "payment_status": "free",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            },
            {
                "id": "build-2",
                "user_id": "test-user-id",
                "name": "Build 2",
                "description": "Second build",
                "status": "deployed",
                "is_free": False,
                "payment_status": "paid",
                "created_at": "2024-01-02T00:00:00",
                "updated_at": "2024-01-02T00:00:00"
            }
        ]
        mock_db.builds = mock_builds
        
        headers = {"Authorization": f"Bearer {create_token("test-user-id", "test@example.com")}"}
        response = client.get("/api/builds", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Build 2"  # Should be sorted by created_at descending
        assert data[1]["name"] == "Build 1"

    @patch('backend.server.db')
    def test_get_builds_empty(self, mock_db):
        """Test getting builds when user has none."""
        mock_builds = AsyncMock()
        mock_builds.find.return_value = MagicMock()
        mock_builds.find.return_value.sort.return_value.to_list.return_value = []
        mock_db.builds = mock_builds
        
        headers = {"Authorization": f"Bearer {create_token("test-user-id", "test@example.com")}"}
        response = client.get("/api/builds", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    @patch('backend.server.db')
    def test_get_builds_without_auth(self, mock_db):
        """Test getting builds without authentication."""
        response = client.get("/api/builds")
        
        assert response.status_code == 401


class TestEditBuild:
    """Tests for edit build endpoint."""

    @patch('backend.server.db')
    def test_edit_build_success(self, mock_db):
        """Test editing a build."""
        mock_builds = AsyncMock()
        mock_builds.find_one.return_value = {
            "id": "build-1",
            "user_id": "test-user-id",
            "name": "Original Name",
            "description": "Original description",
            "status": "draft"
        }
        mock_builds.update_one.return_value = None
        mock_builds.find_one.return_value = {
            "id": "build-1",
            "user_id": "test-user-id",
            "name": "Updated Name",
            "description": "Updated description",
            "status": "draft"
        }
        mock_db.builds = mock_builds
        
        headers = {"Authorization": f"Bearer {create_token("test-user-id", "test@example.com")}"}
        response = client.put(
            "/api/builds/build-1",
            json={"name": "Updated Name", "description": "Updated description"},
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["description"] == "Updated description"

    @patch('backend.server.db')
    def test_edit_build_not_found(self, mock_db):
        """Test editing a non-existent build."""
        mock_builds = AsyncMock()
        mock_builds.find_one.return_value = None
        mock_db.builds = mock_builds
        
        headers = {"Authorization": f"Bearer {create_token("test-user-id", "test@example.com")}"}
        response = client.put(
            "/api/builds/nonexistent",
            json={"name": "Updated Name"},
            headers=headers
        )
        
        assert response.status_code == 404
        assert "Build not found" in response.json()["detail"]

    @patch('backend.server.db')
    def test_edit_build_not_owner(self, mock_db):
        """Test editing a build that doesn't belong to user."""
        mock_builds = AsyncMock()
        mock_builds.find_one.return_value = {
            "id": "build-1",
            "user_id": "other-user-id",  # Different user
            "name": "Original Name"
        }
        mock_db.builds = mock_builds
        
        headers = {"Authorization": f"Bearer {create_token("test-user-id", "test@example.com")}"}
        response = client.put(
            "/api/builds/build-1",
            json={"name": "Updated Name"},
            headers=headers
        )
        
        assert response.status_code == 404

    @patch('backend.server.db')
    def test_edit_build_partial_update(self, mock_db):
        """Test editing only some fields of a build."""
        mock_builds = AsyncMock()
        mock_builds.find_one.return_value = {
            "id": "build-1",
            "user_id": "test-user-id",
            "name": "Original Name",
            "description": "Original description"
        }
        mock_builds.update_one.return_value = None
        mock_builds.find_one.return_value = {
            "id": "build-1",
            "user_id": "test-user-id",
            "name": "Updated Name",
            "description": "Original description"  # Not updated
        }
        mock_db.builds = mock_builds
        
        headers = {"Authorization": f"Bearer {create_token("test-user-id", "test@example.com")}"}
        response = client.put(
            "/api/builds/build-1",
            json={"name": "Updated Name"},  # Only update name
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["description"] == "Original description"

    @patch('backend.server.db')
    def test_edit_build_without_auth(self, mock_db):
        """Test editing build without authentication."""
        response = client.put(
            "/api/builds/build-1",
            json={"name": "Updated Name"}
        )
        
        assert response.status_code == 401


class TestDeployBuild:
    """Tests for deploy build endpoint."""

    @patch('backend.server.db')
    def test_deploy_build_success_free(self, mock_db):
        """Test deploying a free build."""
        mock_builds = AsyncMock()
        mock_builds.find_one.return_value = {
            "id": "build-1",
            "user_id": "test-user-id",
            "name": "Free Build",
            "is_free": True,
            "payment_status": "free",
            "status": "draft"
        }
        mock_builds.update_one.return_value = None
        mock_db.builds = mock_builds
        
        headers = {"Authorization": f"Bearer {create_token("test-user-id", "test@example.com")}"}
        response = client.post(
            "/api/builds/build-1/deploy",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "deployed"
        assert data["message"] == "Build deployed successfully"

    @patch('backend.server.db')
    def test_deploy_build_success_paid(self, mock_db):
        """Test deploying a paid build."""
        mock_builds = AsyncMock()
        mock_builds.find_one.return_value = {
            "id": "build-1",
            "user_id": "test-user-id",
            "name": "Paid Build",
            "is_free": False,
            "payment_status": "paid",
            "status": "draft"
        }
        mock_builds.update_one.return_value = None
        mock_db.builds = mock_builds
        
        headers = {"Authorization": f"Bearer {create_token("test-user-id", "test@example.com")}"}
        response = client.post(
            "/api/builds/build-1/deploy",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "deployed"

    @patch('backend.server.db')
    def test_deploy_build_payment_required(self, mock_db):
        """Test deploying a build that requires payment."""
        mock_builds = AsyncMock()
        mock_builds.find_one.return_value = {
            "id": "build-1",
            "user_id": "test-user-id",
            "name": "Unpaid Build",
            "is_free": False,
            "payment_status": "pending",
            "status": "draft"
        }
        mock_db.builds = mock_builds
        
        headers = {"Authorization": f"Bearer {create_token("test-user-id", "test@example.com")}"}
        response = client.post(
            "/api/builds/build-1/deploy",
            headers=headers
        )
        
        assert response.status_code == 402
        assert "Payment required" in response.json()["detail"]

    @patch('backend.server.db')
    def test_deploy_build_not_found(self, mock_db):
        """Test deploying a non-existent build."""
        mock_builds = AsyncMock()
        mock_builds.find_one.return_value = None
        mock_db.builds = mock_builds
        
        headers = {"Authorization": f"Bearer {create_token("test-user-id", "test@example.com")}"}
        response = client.post(
            "/api/builds/nonexistent/deploy",
            headers=headers
        )
        
        assert response.status_code == 404

    @patch('backend.server.db')
    def test_deploy_build_without_auth(self, mock_db):
        """Test deploying build without authentication."""
        response = client.post("/api/builds/build-1/deploy")
        
        assert response.status_code == 401


class TestPayForBuild:
    """Tests for pay for build endpoint."""

    @patch('backend.server.db')
    def test_pay_for_build_success(self, mock_db):
        """Test paying for a build."""
        mock_builds = AsyncMock()
        mock_builds.find_one.return_value = {
            "id": "build-1",
            "user_id": "test-user-id",
            "name": "Build to Pay",
            "is_free": False,
            "payment_status": "pending"
        }
        mock_builds.update_one.return_value = None
        mock_db.builds = mock_builds
        
        mock_payments = AsyncMock()
        mock_payments.insert_one.return_value = None
        mock_db.payments = mock_payments
        
        with patch('backend.server.uuid.uuid4') as mock_uuid:
            mock_uuid.return_value = uuid.UUID('payment-123')
            
            headers = {"Authorization": f"Bearer {create_token("test-user-id", "test@example.com")}"}
            response = client.post(
                "/api/builds/build-1/pay",
                headers=headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "Payment successful" in data["message"]
            assert data["payment_status"] == "mock_paid"

    @patch('backend.server.db')
    def test_pay_for_free_build(self, mock_db):
        """Test paying for a free build (should return free status)."""
        mock_builds = AsyncMock()
        mock_builds.find_one.return_value = {
            "id": "build-1",
            "user_id": "test-user-id",
            "name": "Free Build",
            "is_free": True,
            "payment_status": "free"
        }
        mock_db.builds = mock_builds
        
        headers = {"Authorization": f"Bearer {create_token("test-user-id", "test@example.com")}"}
        response = client.post(
            "/api/builds/build-1/pay",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "This build is free!" in data["message"]
        assert data["payment_status"] == "free"

    @patch('backend.server.db')
    def test_pay_for_already_paid_build(self, mock_db):
        """Test paying for an already paid build."""
        mock_builds = AsyncMock()
        mock_builds.find_one.return_value = {
            "id": "build-1",
            "user_id": "test-user-id",
            "name": "Already Paid Build",
            "is_free": False,
            "payment_status": "paid"
        }
        mock_db.builds = mock_builds
        
        headers = {"Authorization": f"Bearer {create_token("test-user-id", "test@example.com")}"}
        response = client.post(
            "/api/builds/build-1/pay",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Already paid" in data["message"]

    @patch('backend.server.db')
    def test_pay_for_build_not_found(self, mock_db):
        """Test paying for a non-existent build."""
        mock_builds = AsyncMock()
        mock_builds.find_one.return_value = None
        mock_db.builds = mock_builds
        
        headers = {"Authorization": f"Bearer {create_token("test-user-id", "test@example.com")}"}
        response = client.post(
            "/api/builds/nonexistent/pay",
            headers=headers
        )
        
        assert response.status_code == 404

    @patch('backend.server.db')
    def test_pay_for_build_without_auth(self, mock_db):
        """Test paying for build without authentication."""
        response = client.post("/api/builds/build-1/pay")
        
        assert response.status_code == 401


class TestPricing:
    """Tests for pricing endpoint."""

    def test_get_pricing(self):
        """Test getting pricing information."""
        response = client.get("/api/pricing")
        
        assert response.status_code == 200
        data = response.json()
        assert "plans" in data
        assert len(data["plans"]) == 2
        
        # Check first build plan
        first_plan = data["plans"][0]
        assert first_plan["name"] == "First Build"
        assert first_plan["price"] == 0
        assert first_plan["price_label"] == "FREE"
        
        # Check per build plan
        second_plan = data["plans"][1]
        assert second_plan["name"] == "Per Build"
        assert second_plan["price"] == 10.0
        assert second_plan["price_label"] == "$10.00"
        
        assert "notes" in data
        assert len(data["notes"]) > 0

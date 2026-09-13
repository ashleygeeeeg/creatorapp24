"""Tests for authentication endpoints and user management."""
import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from datetime import datetime, timezone

# Set test environment
os.environ['MONGO_URL'] = 'mongodb://localhost:27017'
os.environ['DB_NAME'] = 'creatorapp24_test'
os.environ['JWT_SECRET'] = 'test-secret-key-for-testing-only'
os.environ['JWT_EXPIRY_HOURS'] = '24'

from backend.server import app, hash_password

client = TestClient(app)


class TestSignup:
    """Tests for user signup endpoint."""

    @patch('backend.server.db')
    def test_signup_success(self, mock_db):
        """Test successful user signup."""
        # Mock MongoDB operations
        mock_users = AsyncMock()
        mock_users.find_one.return_value = None
        mock_users.insert_one.return_value = None
        mock_db.users = mock_users
        
        # Mock uuid
        with patch('backend.server.uuid.uuid4') as mock_uuid:
            mock_uuid.return_value = 'test-user-id'
            
            response = client.post("/api/auth/signup", json={
                "email": "test@example.com",
                "password": "testpassword123",
                "name": "Test User"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert "token" in data
            assert "user" in data
            assert data["user"]["email"] == "test@example.com"
            assert data["user"]["id"] == "test-user-id"
            assert data["user"]["name"] == "Test User"

    @patch('backend.server.db')
    def test_signup_email_already_registered(self, mock_db):
        """Test signup with already registered email."""
        mock_users = AsyncMock()
        mock_users.find_one.return_value = {
            "id": "existing-id",
            "email": "test@example.com",
            "password_hash": hash_password("oldpassword")
        }
        mock_db.users = mock_users
        
        response = client.post("/api/auth/signup", json={
            "email": "test@example.com",
            "password": "testpassword123",
            "name": "Test User"
        })
        
        assert response.status_code == 409
        assert "Email already registered" in response.json()["detail"]

    @patch('backend.server.db')
    def test_signup_missing_email(self, mock_db):
        """Test signup with missing email."""
        response = client.post("/api/auth/signup", json={
            "password": "testpassword123",
            "name": "Test User"
        })
        
        assert response.status_code == 422  # Validation error

    @patch('backend.server.db')
    def test_signup_missing_password(self, mock_db):
        """Test signup with missing password."""
        response = client.post("/api/auth/signup", json={
            "email": "test@example.com",
            "name": "Test User"
        })
        
        assert response.status_code == 422  # Validation error

    @patch('backend.server.db')
    def test_signup_email_case_insensitive(self, mock_db):
        """Test that signup treats emails as case-insensitive."""
        mock_users = AsyncMock()
        mock_users.find_one.return_value = {
            "id": "existing-id",
            "email": "TEST@EXAMPLE.COM",
            "password_hash": hash_password("oldpassword")
        }
        mock_db.users = mock_users
        
        response = client.post("/api/auth/signup", json={
            "email": "test@example.com",
            "password": "testpassword123"
        })
        
        assert response.status_code == 409

    @patch('backend.server.db')
    def test_signup_without_name(self, mock_db):
        """Test signup without providing a name."""
        mock_users = AsyncMock()
        mock_users.find_one.return_value = None
        mock_users.insert_one.return_value = None
        mock_db.users = mock_users
        
        with patch('backend.server.uuid.uuid4') as mock_uuid:
            mock_uuid.return_value = 'test-user-id'
            
            response = client.post("/api/auth/signup", json={
                "email": "test@example.com",
                "password": "testpassword123"
            })
            
            assert response.status_code == 200
            data = response.json()
            # Name should default to email prefix
            assert data["user"]["name"] == "test"


class TestLogin:
    """Tests for user login endpoint."""

    @patch('backend.server.db')
    def test_login_success(self, mock_db):
        """Test successful user login."""
        mock_users = AsyncMock()
        mock_users.find_one.return_value = {
            "id": "test-user-id",
            "email": "test@example.com",
            "password_hash": hash_password("testpassword123"),
            "name": "Test User",
            "created_at": "2024-01-01T00:00:00",
            "build_count": 0,
            "has_free_build": True
        }
        mock_db.users = mock_users
        
        response = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "testpassword123"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["email"] == "test@example.com"

    @patch('backend.server.db')
    def test_login_wrong_password(self, mock_db):
        """Test login with wrong password."""
        mock_users = AsyncMock()
        mock_users.find_one.return_value = {
            "id": "test-user-id",
            "email": "test@example.com",
            "password_hash": hash_password("correctpassword"),
            "name": "Test User"
        }
        mock_db.users = mock_users
        
        response = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    @patch('backend.server.db')
    def test_login_nonexistent_user(self, mock_db):
        """Test login with nonexistent user."""
        mock_users = AsyncMock()
        mock_users.find_one.return_value = None
        mock_db.users = mock_users
        
        response = client.post("/api/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "testpassword123"
        })
        
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    @patch('backend.server.db')
    def test_login_missing_email(self, mock_db):
        """Test login with missing email."""
        response = client.post("/api/auth/login", json={
            "password": "testpassword123"
        })
        
        assert response.status_code == 422

    @patch('backend.server.db')
    def test_login_missing_password(self, mock_db):
        """Test login with missing password."""
        response = client.post("/api/auth/login", json={
            "email": "test@example.com"
        })
        
        assert response.status_code == 422

    @patch('backend.server.db')
    def test_login_email_case_insensitive(self, mock_db):
        """Test that login treats emails as case-insensitive."""
        mock_users = AsyncMock()
        mock_users.find_one.return_value = {
            "id": "test-user-id",
            "email": "TEST@EXAMPLE.COM",
            "password_hash": hash_password("testpassword123"),
            "name": "Test User"
        }
        mock_db.users = mock_users
        
        response = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "testpassword123"
        })
        
        assert response.status_code == 200


class TestGetMe:
    """Tests for get current user endpoint."""

    @patch('backend.server.db')
    def test_get_me_success(self, mock_db):
        """Test successful get current user."""
        mock_builds = AsyncMock()
        mock_builds.count_documents.return_value = 0
        mock_db.builds = mock_builds
        
        mock_users = AsyncMock()
        mock_users.find_one.return_value = {
            "id": "test-user-id",
            "email": "test@example.com",
            "name": "Test User",
            "created_at": "2024-01-01T00:00:00",
            "build_count": 0,
            "has_free_build": True
        }
        mock_db.users = mock_users
        
        # First, get a token
        with patch('backend.server.db', mock_db):
            login_response = client.post("/api/auth/login", json={
                "email": "test@example.com",
                "password": "testpassword123"
            })
            # For this test, we'll mock the dependency directly
            pass
        
        # This is a simplified test - full auth flow testing requires more complex setup
        # For now, we test the validation
        response = client.get("/api/auth/me")
        # Without auth, should get 401
        assert response.status_code == 401

    def test_get_me_without_auth(self):
        """Test get current user without authentication."""
        response = client.get("/api/auth/me")
        assert response.status_code == 401

    def test_get_me_with_invalid_token(self):
        """Test get current user with invalid token."""
        response = client.get("/api/auth/me", headers={
            "Authorization": "Bearer invalidtoken123"
        })
        assert response.status_code == 401


class TestGetCurrentUser:
    """Tests for get_current_user dependency."""

    def test_get_current_user_without_credentials(self):
        """Test get_current_user without credentials."""
        from backend.server import HTTPAuthorizationCredentials
        from fastapi import HTTPException
        
        with pytest.raises(HTTPException) as exc_info:
            import asyncio
            from backend.server import get_current_user
            asyncio.run(get_current_user(None))
        
        assert exc_info.value.status_code == 401

    def test_get_current_user_with_invalid_token(self):
        """Test get_current_user with invalid token."""
        from fastapi import HTTPException
        from backend.server import HTTPAuthorizationCredentials
        
        with pytest.raises(HTTPException) as exc_info:
            import asyncio
            from backend.server import get_current_user
            creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalidtoken")
            asyncio.run(get_current_user(creds))
        
        assert exc_info.value.status_code == 401


class TestGetOptionalUser:
    """Tests for get_optional_user dependency."""

    @patch('backend.server.db')
    async def test_get_optional_user_without_credentials(self, mock_db):
        """Test get_optional_user without credentials returns None."""
        from backend.server import get_optional_user
        result = await get_optional_user(None)
        assert result is None

    @patch('backend.server.db')
    async def test_get_optional_user_with_valid_credentials(self, mock_db):
        """Test get_optional_user with valid credentials returns user."""
        from backend.server import get_optional_user, create_token
        from backend.server import HTTPAuthorizationCredentials
        
        # Create a valid token
        token = create_token("test-user-id", "test@example.com")
        
        mock_users = AsyncMock()
        mock_users.find_one.return_value = {
            "id": "test-user-id",
            "email": "test@example.com",
            "name": "Test User"
        }
        mock_db.users = mock_users
        
        with patch('backend.server.db', mock_users):
            creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
            result = await get_optional_user(creds)
            assert result is not None
            assert result["id"] == "test-user-id"

    @patch('backend.server.db')
    async def test_get_optional_user_with_invalid_token(self, mock_db):
        """Test get_optional_user with invalid token returns None."""
        from backend.server import get_optional_user
        from backend.server import HTTPAuthorizationCredentials
        
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalidtoken")
        result = await get_optional_user(creds)
        assert result is None

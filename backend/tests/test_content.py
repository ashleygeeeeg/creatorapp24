"""Tests for content endpoints: showcase, features, stats, waitlist."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime, timezone
import uuid

from backend.server import app, create_token

client = TestClient(app)


class TestShowcase:
    """Tests for showcase endpoint."""

    @patch('backend.server.db')
    def test_get_showcase_with_data(self, mock_db):
        """Test getting showcase items when data exists."""
        mock_showcase = AsyncMock()
        mock_showcase.find.return_value = MagicMock()
        mock_showcase.find.return_value.sort.return_value.to_list.return_value = [
            {
                "id": "showcase-1",
                "mobile_image": "https://example.com/mobile1.webp",
                "laptop_image": "https://example.com/laptop1.webp",
                "order": 1
            },
            {
                "id": "showcase-2",
                "mobile_image": "https://example.com/mobile2.webp",
                "laptop_image": "https://example.com/laptop2.webp",
                "order": 2
            }
        ]
        mock_db.showcase = mock_showcase
        
        response = client.get("/api/showcase")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["order"] == 1
        assert data[1]["order"] == 2

    @patch('backend.server.db')
    @patch('backend.server.seed_data_internal')
    def test_get_showcase_empty_seeds_data(self, mock_seed, mock_db):
        """Test that empty showcase triggers data seeding."""
        mock_showcase = AsyncMock()
        mock_showcase.find.return_value = MagicMock()
        mock_showcase.find.return_value.sort.return_value.to_list.return_value = []
        mock_db.showcase = mock_showcase
        
        # After seeding, data should be available
        mock_showcase.find.return_value.sort.return_value.to_list.return_value = [
            {"id": "seeded-1", "mobile_image": "img1", "laptop_image": "img2", "order": 1}
        ]
        
        response = client.get("/api/showcase")
        
        assert response.status_code == 200
        mock_seed.assert_called_once()

    @patch('backend.server.db')
    @patch('backend.server.seed_data_internal')
    def test_get_showcase_seeded_data(self, mock_seed, mock_db):
        """Test getting showcase with seeded data."""
        # Mock that data already exists
        mock_showcase = AsyncMock()
        mock_showcase.find.return_value = MagicMock()
        mock_showcase.find.return_value.sort.return_value.to_list.return_value = [
            {"id": "seeded-1", "mobile_image": "img1", "laptop_image": "img2", "order": 1}
        ]
        mock_db.showcase = mock_showcase
        
        response = client.get("/api/showcase")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        # Seed should not be called if data exists
        mock_seed.assert_not_called()


class TestFeatures:
    """Tests for features endpoint."""

    @patch('backend.server.db')
    def test_get_features_with_data(self, mock_db):
        """Test getting features when data exists."""
        mock_features = AsyncMock()
        mock_features.find.return_value = MagicMock()
        mock_features.find.return_value.sort.return_value.to_list.return_value = [
            {
                "id": "feature-1",
                "icon": "code",
                "title": "Build Apps",
                "description": "Build amazing apps",
                "mockup_type": "library",
                "order": 1
            },
            {
                "id": "feature-2",
                "icon": "bot",
                "title": "AI Agents",
                "description": "Create AI agents",
                "mockup_type": "agent",
                "order": 2
            }
        ]
        mock_db.features = mock_features
        
        response = client.get("/api/features")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["order"] == 1
        assert data[1]["order"] == 2

    @patch('backend.server.db')
    @patch('backend.server.seed_data_internal')
    def test_get_features_empty_seeds_data(self, mock_seed, mock_db):
        """Test that empty features triggers data seeding."""
        mock_features = AsyncMock()
        mock_features.find.return_value = MagicMock()
        mock_features.find.return_value.sort.return_value.to_list.return_value = []
        mock_db.features = mock_features
        
        # After seeding
        mock_features.find.return_value.sort.return_value.to_list.return_value = [
            {"id": "seeded-1", "icon": "code", "title": "Build", "description": "Desc", "mockup_type": "library", "order": 1}
        ]
        
        response = client.get("/api/features")
        
        assert response.status_code == 200
        mock_seed.assert_called_once()


class TestStats:
    """Tests for stats endpoint."""

    @patch('backend.server.db')
    def test_get_stats_with_data(self, mock_db):
        """Test getting stats when data exists."""
        mock_stats = AsyncMock()
        mock_stats.find_one.return_value = {
            "users_count": "5M+",
            "description": "users worldwide"
        }
        mock_db.stats = mock_stats
        
        response = client.get("/api/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["users_count"] == "5M+"
        assert data["description"] == "users worldwide"

    @patch('backend.server.db')
    @patch('backend.server.seed_data_internal')
    def test_get_stats_empty_seeds_data(self, mock_seed, mock_db):
        """Test that empty stats triggers data seeding."""
        mock_stats = AsyncMock()
        mock_stats.find_one.return_value = None
        mock_db.stats = mock_stats
        
        # After seeding
        mock_stats.find_one.return_value = {
            "users_count": "3M+",
            "description": "users worldwide building & launching real applications in minutes."
        }
        
        response = client.get("/api/stats")
        
        assert response.status_code == 200
        mock_seed.assert_called_once()
        data = response.json()
        assert data["users_count"] == "3M+"

    @patch('backend.server.db')
    @patch('backend.server.seed_data_internal')
    def test_get_stats_returns_default(self, mock_seed, mock_db):
        """Test that stats returns default when no data exists."""
        mock_stats = AsyncMock()
        mock_stats.find_one.return_value = None
        mock_db.stats = mock_stats
        
        response = client.get("/api/stats")
        
        assert response.status_code == 200
        data = response.json()
        # Should return default Stats model
        assert "users_count" in data
        assert "description" in data


class TestWaitlist:
    """Tests for waitlist endpoints."""

    @patch('backend.server.db')
    def test_create_waitlist_entry_success(self, mock_db):
        """Test creating a waitlist entry."""
        mock_waitlist = AsyncMock()
        mock_waitlist.find_one.return_value = None
        mock_waitlist.insert_one.return_value = None
        mock_db.waitlist = mock_waitlist
        
        with patch('backend.server.uuid.uuid4') as mock_uuid:
            mock_uuid.return_value = uuid.UUID('waitlist-123')
            
            response = client.post("/api/waitlist", json={
                "email": "waitlist@example.com",
                "name": "Waitlist User"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["email"] == "waitlist@example.com"
            assert data["name"] == "Waitlist User"
            assert data["id"] == "waitlist-123"

    @patch('backend.server.db')
    def test_create_waitlist_entry_email_already_exists(self, mock_db):
        """Test creating a waitlist entry with existing email."""
        mock_waitlist = AsyncMock()
        mock_waitlist.find_one.return_value = {
            "id": "existing-123",
            "email": "waitlist@example.com",
            "name": "Existing User"
        }
        mock_db.waitlist = mock_waitlist
        
        response = client.post("/api/waitlist", json={
            "email": "waitlist@example.com",
            "name": "New User"
        })
        
        assert response.status_code == 409
        assert "Email already on waitlist" in response.json()["detail"]

    @patch('backend.server.db')
    def test_create_waitlist_entry_without_name(self, mock_db):
        """Test creating a waitlist entry without name."""
        mock_waitlist = AsyncMock()
        mock_waitlist.find_one.return_value = None
        mock_waitlist.insert_one.return_value = None
        mock_db.waitlist = mock_waitlist
        
        with patch('backend.server.uuid.uuid4') as mock_uuid:
            mock_uuid.return_value = uuid.UUID('waitlist-456')
            
            response = client.post("/api/waitlist", json={
                "email": "waitlist@example.com"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["email"] == "waitlist@example.com"
            assert data["name"] is None

    @patch('backend.server.db')
    def test_create_waitlist_entry_missing_email(self, mock_db):
        """Test creating a waitlist entry with missing email."""
        response = client.post("/api/waitlist", json={
            "name": "Waitlist User"
        })
        
        assert response.status_code == 422

    @patch('backend.server.db')
    def test_get_waitlist_count(self, mock_db):
        """Test getting waitlist count."""
        mock_waitlist = AsyncMock()
        mock_waitlist.count_documents.return_value = 42
        mock_db.waitlist = mock_waitlist
        
        response = client.get("/api/waitlist/count")
        
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 42


class TestSeed:
    """Tests for seed endpoint."""

    @patch('backend.server.seed_data_internal')
    def test_seed_data_success(self, mock_seed):
        """Test seeding data."""
        response = client.post("/api/seed")
        
        assert response.status_code == 200
        data = response.json()
        assert "Database seeded successfully" in data["message"]
        mock_seed.assert_called_once()


class TestRoot:
    """Tests for root endpoint."""

    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/api/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "maligeeAi API is running" in data["message"]

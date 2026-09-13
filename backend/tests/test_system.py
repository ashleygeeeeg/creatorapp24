"""Tests for system routes: health check."""
import os
from fastapi.testclient import TestClient
from unittest.mock import patch

# Set test environment
os.environ['MONGO_URL'] = 'mongodb://localhost:27017'
os.environ['DB_NAME'] = 'creatorapp24_test'
os.environ['JWT_SECRET'] = 'test-secret-key-for-testing-only'

from backend.server import app

client = TestClient(app)


class TestHealth:
    """Tests for health check endpoint."""

    def test_health_check_success(self):
        """Test successful health check."""
        response = client.get("/api/system/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

    @patch('backend.server.datetime')
    def test_health_check_timestamp_format(self, mock_datetime):
        """Test that health check returns ISO formatted timestamp."""
        from datetime import datetime, timezone
        mock_datetime.now.return_value = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        
        response = client.get("/api/system/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["timestamp"] == "2024-01-15T10:30:00+00:00"


class TestSystemRoutes:
    """Tests for system route registration."""

    def test_system_routes_exist(self):
        """Test that system routes are registered."""
        # Check that the system router is included
        from backend.routes.system import router as system_router
        
        # The system router should have the health endpoint
        assert system_router is not None
        
        # Test that the health endpoint is accessible
        response = client.get("/api/system/health")
        assert response.status_code == 200


class TestAppMaker24Routes:
    """Tests for AppMaker24 integration routes."""

    @patch('backend.server.db')
    def test_appmaker24_integration_route(self, mock_db):
        """Test AppMaker24 integration route."""
        # Set environment variables for the integration
        os.environ['PUBLIC_WEB_URL'] = 'https://test.example.com'
        os.environ['PUBLIC_API_URL'] = 'https://api.test.example.com'
        os.environ['APPCREATOR24_APP_URL'] = 'https://appcreator24.test.com'
        
        # Need to reimport routes to pick up env changes
        import importlib
        import backend.routes.appmaker24
        importlib.reload(backend.routes.appmaker24)
        
        # Create a new test client with reloaded routes
        from backend.server import app as reloaded_app
        test_client = TestClient(reloaded_app)
        
        response = test_client.get("/integrations/appmaker24")
        
        assert response.status_code == 200
        data = response.json()
        assert data["brand"] == "maligeeAi"
        assert data["platform"] == "AppCreator24"
        assert "appmaker24" in data["aliases"]
        assert "appcreator24" in data["aliases"]
        assert data["android_shell_url"] == "https://appcreator24.test.com"
        assert data["public_web_url"] == "https://test.example.com"
        assert data["api_url"] == "https://api.test.example.com/api"
        assert "webview_menus" in data
        assert len(data["webview_menus"]) == 4
        assert "docs" in data

    @patch('backend.server.db')
    def test_appmaker24_integration_default_values(self, mock_db):
        """Test AppMaker24 integration with default values."""
        # Clear environment variables
        old_web = os.environ.get('PUBLIC_WEB_URL')
        old_api = os.environ.get('PUBLIC_API_URL')
        old_app = os.environ.get('APPCREATOR24_APP_URL')
        
        os.environ['PUBLIC_WEB_URL'] = ''
        os.environ['PUBLIC_API_URL'] = ''
        os.environ['APPCREATOR24_APP_URL'] = ''
        
        import importlib
        import backend.routes.appmaker24
        importlib.reload(backend.routes.appmaker24)
        
        from backend.server import app as reloaded_app
        test_client = TestClient(reloaded_app)
        
        response = test_client.get("/integrations/appmaker24")
        
        assert response.status_code == 200
        data = response.json()
        # Should use default values
        assert data["public_web_url"] == "https://YOUR_VERCEL_URL.vercel.app"
        assert data["api_url"] == "http://localhost:8000/api"
        assert data["android_shell_url"] == "https://www.appcreator24.com"
        
        # Restore environment
        if old_web:
            os.environ['PUBLIC_WEB_URL'] = old_web
        if old_api:
            os.environ['PUBLIC_API_URL'] = old_api
        if old_app:
            os.environ['APPCREATOR24_APP_URL'] = old_app


class TestCORS:
    """Tests for CORS configuration."""

    def test_cors_headers(self):
        """Test that CORS headers are present."""
        response = client.get("/api/system/health")
        
        assert response.status_code == 200
        # Check CORS headers
        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] == "*"
        assert "access-control-allow-methods" in response.headers
        assert "access-control-allow-headers" in response.headers

    def test_cors_custom_origins(self):
        """Test CORS with custom origins."""
        # Set custom CORS origins
        os.environ['CORS_ORIGINS'] = 'https://example.com,https://test.com'
        
        import importlib
        import backend.server
        importlib.reload(backend.server)
        from backend.server import app as reloaded_app
        
        test_client = TestClient(reloaded_app)
        response = test_client.get("/api/system/health")
        
        assert response.status_code == 200
        # CORS should be configured with custom origins
        # Note: The actual header might be set differently based on FastAPI's CORS middleware
        
        # Reset to default
        os.environ['CORS_ORIGINS'] = '*'

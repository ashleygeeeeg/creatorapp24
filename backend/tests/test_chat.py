"""Tests for chat endpoints."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime, timezone

from backend.server import app, create_token, hash_password

client = TestClient(app)


class TestChatWithAI:
    """Tests for chat with AI endpoint."""

    @patch('backend.server.db')
    @patch('backend.server.LlmChat')
    def test_chat_with_ai_success(self, mock_llm_chat, mock_db):
        """Test successful chat with AI."""
        # Mock LLM chat
        mock_chat_instance = AsyncMock()
        mock_chat_instance.messages = []
        mock_chat_instance.with_model.return_value = None
        mock_chat_instance.send_message.return_value = "This is a test response"
        mock_llm_chat.return_value = mock_chat_instance
        
        # Mock database
        mock_chat_history = AsyncMock()
        mock_chat_history.find.return_value = MagicMock()
        mock_chat_history.find.return_value.sort.return_value.to_list.return_value = []
        mock_chat_history.insert_many.return_value = None
        mock_db.chat_history = mock_chat_history
        
        mock_users = AsyncMock()
        mock_users.find_one.return_value = {
            "id": "test-user-id",
            "email": "test@example.com"
        }
        mock_db.users = mock_users
        
        mock_builds = AsyncMock()
        mock_builds.count_documents.return_value = 1  # Has paid builds
        mock_db.builds = mock_builds
        
        headers = {"Authorization": f"Bearer {create_token("test-user-id", "test@example.com")}"}
        response = client.post(
            "/api/chat",
            json={"message": "Hello, AI!"},
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert data["response"] == "This is a test response"
        assert "session_id" in data

    @patch('backend.server.db')
    @patch('backend.server.LlmChat')
    def test_chat_with_ai_with_session_id(self, mock_llm_chat, mock_db):
        """Test chat with AI with existing session."""
        mock_chat_instance = AsyncMock()
        mock_chat_instance.messages = []
        mock_chat_instance.with_model.return_value = None
        mock_chat_instance.send_message.return_value = "Response with session"
        mock_llm_chat.return_value = mock_chat_instance
        
        mock_chat_history = AsyncMock()
        mock_chat_history.find.return_value = MagicMock()
        mock_chat_history.find.return_value.sort.return_value.to_list.return_value = [
            {"role": "user", "content": "Previous message", "created_at": "2024-01-01T00:00:00"}
        ]
        mock_chat_history.insert_many.return_value = None
        mock_db.chat_history = mock_chat_history
        
        mock_users = AsyncMock()
        mock_users.find_one.return_value = {
            "id": "test-user-id",
            "email": "test@example.com"
        }
        mock_db.users = mock_users
        
        mock_builds = AsyncMock()
        mock_builds.count_documents.return_value = 1
        mock_db.builds = mock_builds
        
        headers = {"Authorization": f"Bearer {create_token("test-user-id", "test@example.com")}"}
        response = client.post(
            "/api/chat",
            json={"message": "Hello", "session_id": "existing-session-id"},
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "existing-session-id"

    @patch('backend.server.db')
    def test_chat_with_ai_no_llm_key(self, mock_db):
        """Test chat with AI when LLM key is not configured."""
        # Temporarily remove LLM key
        old_key = os.environ.get('EMERGENT_LLM_KEY')
        os.environ['EMERGENT_LLM_KEY'] = ''
        
        # Need to reimport to pick up the change
        import importlib
        import backend.server
        importlib.reload(backend.server)
        from backend.server import app as reloaded_app
        
        test_client = TestClient(reloaded_app)
        
        headers = {"Authorization": f"Bearer {create_token("test-user-id", "test@example.com")}"}
        response = test_client.post(
            "/api/chat",
            json={"message": "Hello"},
            headers=headers
        )
        
        assert response.status_code == 500
        assert "AI service not configured" in response.json()["detail"]
        
        # Restore key
        if old_key:
            os.environ['EMERGENT_LLM_KEY'] = old_key

    @patch('backend.server.db')
    @patch('backend.server.LlmChat')
    def test_chat_with_ai_anonymous_user(self, mock_llm_chat, mock_db):
        """Test chat with AI for anonymous user (no auth)."""
        mock_chat_instance = AsyncMock()
        mock_chat_instance.messages = []
        mock_chat_instance.with_model.return_value = None
        mock_chat_instance.send_message.return_value = "Response for anonymous"
        mock_llm_chat.return_value = mock_chat_instance
        
        mock_chat_history = AsyncMock()
        mock_chat_history.find.return_value = MagicMock()
        mock_chat_history.find.return_value.sort.return_value.to_list.return_value = []
        mock_chat_history.insert_many.return_value = None
        mock_db.chat_history = mock_chat_history
        
        mock_builds = AsyncMock()
        mock_builds.count_documents.return_value = 0  # No paid builds
        mock_db.builds = mock_builds
        
        # No auth headers
        response = client.post(
            "/api/chat",
            json={"message": "Hello from anonymous"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data

    @patch('backend.server.db')
    @patch('backend.server.LlmChat')
    def test_chat_with_ai_user_without_builds(self, mock_llm_chat, mock_db):
        """Test chat with AI for user without any builds."""
        mock_chat_instance = AsyncMock()
        mock_chat_instance.messages = []
        mock_chat_instance.with_model.return_value = None
        mock_chat_instance.send_message.return_value = "Please create a build first"
        mock_llm_chat.return_value = mock_chat_instance
        
        mock_chat_history = AsyncMock()
        mock_chat_history.find.return_value = MagicMock()
        mock_chat_history.find.return_value.sort.return_value.to_list.return_value = []
        mock_chat_history.insert_many.return_value = None
        mock_db.chat_history = mock_chat_history
        
        mock_users = AsyncMock()
        mock_users.find_one.return_value = {
            "id": "test-user-id",
            "email": "test@example.com"
        }
        mock_db.users = mock_users
        
        mock_builds = AsyncMock()
        mock_builds.count_documents.return_value = 0  # No paid builds
        mock_db.builds = mock_builds
        
        headers = {"Authorization": f"Bearer {create_token("test-user-id", "test@example.com")}"}
        response = client.post(
            "/api/chat",
            json={"message": "Build me an app"},
            headers=headers
        )
        
        # Should still work but with restricted system message
        assert response.status_code == 200
        data = response.json()
        assert "response" in data

    @patch('backend.server.db')
    @patch('backend.server.LlmChat')
    def test_chat_with_ai_error(self, mock_llm_chat, mock_db):
        """Test chat with AI when LLM service returns error."""
        mock_chat_instance = AsyncMock()
        mock_chat_instance.messages = []
        mock_chat_instance.with_model.return_value = None
        mock_chat_instance.send_message.side_effect = Exception("LLM service error")
        mock_llm_chat.return_value = mock_chat_instance
        
        mock_chat_history = AsyncMock()
        mock_chat_history.find.return_value = MagicMock()
        mock_chat_history.find.return_value.sort.return_value.to_list.return_value = []
        mock_db.chat_history = mock_chat_history
        
        mock_users = AsyncMock()
        mock_users.find_one.return_value = {
            "id": "test-user-id",
            "email": "test@example.com"
        }
        mock_db.users = mock_users
        
        mock_builds = AsyncMock()
        mock_builds.count_documents.return_value = 1
        mock_db.builds = mock_builds
        
        headers = {"Authorization": f"Bearer {create_token("test-user-id", "test@example.com")}"}
        response = client.post(
            "/api/chat",
            json={"message": "Hello"},
            headers=headers
        )
        
        assert response.status_code == 500
        assert "AI service error" in response.json()["detail"]


class TestGetChatHistory:
    """Tests for get chat history endpoint."""

    @patch('backend.server.db')
    def test_get_chat_history_success(self, mock_db):
        """Test getting chat history for a session."""
        mock_chat_history = AsyncMock()
        mock_chat_history.find.return_value = MagicMock()
        mock_chat_history.find.return_value.sort.return_value.to_list.return_value = [
            {
                "session_id": "test-session",
                "user_id": "test-user-id",
                "role": "user",
                "content": "Hello",
                "created_at": "2024-01-01T00:00:00"
            },
            {
                "session_id": "test-session",
                "user_id": "test-user-id",
                "role": "assistant",
                "content": "Hi there!",
                "created_at": "2024-01-01T00:00:01"
            }
        ]
        mock_db.chat_history = mock_chat_history
        
        headers = {"Authorization": f"Bearer {create_token("test-user-id", "test@example.com")}"}
        response = client.get(
            "/api/chat/history/test-session",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["role"] == "user"
        assert data[1]["role"] == "assistant"

    @patch('backend.server.db')
    def test_get_chat_history_empty(self, mock_db):
        """Test getting chat history for empty session."""
        mock_chat_history = AsyncMock()
        mock_chat_history.find.return_value = MagicMock()
        mock_chat_history.find.return_value.sort.return_value.to_list.return_value = []
        mock_db.chat_history = mock_chat_history
        
        headers = {"Authorization": f"Bearer {create_token("test-user-id", "test@example.com")}"}
        response = client.get(
            "/api/chat/history/empty-session",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    @patch('backend.server.db')
    def test_get_chat_history_without_auth(self, mock_db):
        """Test getting chat history without authentication."""
        response = client.get("/api/chat/history/test-session")
        
        assert response.status_code == 401

    @patch('backend.server.db')
    def test_get_chat_history_different_user(self, mock_db):
        """Test getting chat history for a session belonging to another user."""
        mock_chat_history = AsyncMock()
        mock_chat_history.find.return_value = MagicMock()
        mock_chat_history.find.return_value.sort.return_value.to_list.return_value = []
        mock_db.chat_history = mock_chat_history
        
        # User tries to access another user's session
        headers = {"Authorization": f"Bearer {create_token("test-user-id", "test@example.com")}"}
        response = client.get(
            "/api/chat/history/other-user-session",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0  # Returns empty for different user's session


class TestGetChatSessions:
    """Tests for get chat sessions endpoint."""

    @patch('backend.server.db')
    def test_get_chat_sessions_success(self, mock_db):
        """Test getting user's chat sessions."""
        mock_chat_history = AsyncMock()
        mock_aggregate = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.to_list.return_value = [
            {
                "_id": "session-1",
                "last_message": "Last message from session 1",
                "last_time": "2024-01-02T00:00:00",
                "count": 5
            },
            {
                "_id": "session-2",
                "last_message": "Last message from session 2",
                "last_time": "2024-01-01T00:00:00",
                "count": 3
            }
        ]
        mock_aggregate.return_value = mock_cursor
        mock_chat_history.aggregate.return_value = mock_aggregate
        mock_db.chat_history = mock_chat_history
        
        headers = {"Authorization": f"Bearer {create_token("test-user-id", "test@example.com")}"}
        response = client.get("/api/chat/sessions", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["session_id"] == "session-1"  # Sorted by last_time descending
        assert data[1]["session_id"] == "session-2"
        assert data[0]["message_count"] == 5

    @patch('backend.server.db')
    def test_get_chat_sessions_empty(self, mock_db):
        """Test getting chat sessions when user has none."""
        mock_chat_history = AsyncMock()
        mock_aggregate = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.to_list.return_value = []
        mock_aggregate.return_value = mock_cursor
        mock_chat_history.aggregate.return_value = mock_aggregate
        mock_db.chat_history = mock_chat_history
        
        headers = {"Authorization": f"Bearer {create_token("test-user-id", "test@example.com")}"}
        response = client.get("/api/chat/sessions", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    @patch('backend.server.db')
    def test_get_chat_sessions_without_auth(self, mock_db):
        """Test getting chat sessions without authentication."""
        response = client.get("/api/chat/sessions")
        
        assert response.status_code == 401

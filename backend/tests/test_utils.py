"""Tests for utility functions: password hashing, JWT tokens."""
import os
import pytest
import jwt
from datetime import datetime, timezone, timedelta
from unittest.mock import patch

# Set test JWT secret
os.environ['JWT_SECRET'] = 'test-secret-key-for-testing-only'
os.environ['JWT_EXPIRY_HOURS'] = '24'

from backend.server import (
    hash_password,
    verify_password,
    create_token,
    decode_token,
    JWT_SECRET,
    JWT_ALGORITHM,
    JWT_EXPIRY_HOURS,
)


class TestPasswordHashing:
    """Tests for password hashing and verification."""

    def test_hash_password_returns_string(self):
        """Test that hash_password returns a string."""
        password = "testpassword123"
        hashed = hash_password(password)
        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_hash_password_different_each_time(self):
        """Test that hashing the same password produces different hashes."""
        password = "testpassword123"
        hashed1 = hash_password(password)
        hashed2 = hash_password(password)
        assert hashed1 != hashed2

    def test_verify_password_correct(self):
        """Test that verify_password returns True for correct password."""
        password = "testpassword123"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test that verify_password returns False for incorrect password."""
        password = "testpassword123"
        hashed = hash_password(password)
        assert verify_password("wrongpassword", hashed) is False

    def test_verify_password_empty_password(self):
        """Test that verify_password handles empty password."""
        hashed = hash_password("testpassword123")
        assert verify_password("", hashed) is False

    def test_verify_password_empty_hash(self):
        """Test that verify_password handles empty hash."""
        assert verify_password("testpassword123", "") is False

    def test_hash_password_special_characters(self):
        """Test password hashing with special characters."""
        password = "p@$$w0rd!#$%"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_hash_password_unicode(self):
        """Test password hashing with unicode characters."""
        password = "пароль密码🔒"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_hash_password_very_long(self):
        """Test password hashing with very long password."""
        password = "a" * 1000
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True


class TestJWTTokens:
    """Tests for JWT token creation and decoding."""

    def test_create_token_returns_string(self):
        """Test that create_token returns a string."""
        token = create_token("user123", "test@example.com")
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_token_valid(self):
        """Test that decode_token correctly decodes a valid token."""
        token = create_token("user123", "test@example.com")
        payload = decode_token(token)
        assert payload['user_id'] == "user123"
        assert payload['email'] == "test@example.com"
        assert 'exp' in payload
        assert 'iat' in payload

    def test_decode_token_expired(self):
        """Test that decode_token raises error for expired token."""
        # Create a token that expired 1 hour ago
        payload = {
            'user_id': 'user123',
            'email': 'test@example.com',
            'exp': datetime.now(timezone.utc) - timedelta(hours=1),
            'iat': datetime.now(timezone.utc) - timedelta(hours=2)
        }
        expired_token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        
        with pytest.raises(Exception) as exc_info:
            decode_token(expired_token)
        assert "Token expired" in str(exc_info.value) or "expired" in str(exc_info.value).lower()

    def test_decode_token_invalid_signature(self):
        """Test that decode_token raises error for invalid signature."""
        token = create_token("user123", "test@example.com")
        # Tamper with the token
        tampered_token = token[:-5] + "abcde"
        
        with pytest.raises(Exception) as exc_info:
            decode_token(tampered_token)
        assert "Invalid token" in str(exc_info.value) or "invalid" in str(exc_info.value).lower()

    def test_decode_token_wrong_secret(self):
        """Test that decode_token raises error for token with wrong secret."""
        wrong_secret = "wrong-secret-key"
        payload = {
            'user_id': 'user123',
            'email': 'test@example.com',
            'exp': datetime.now(timezone.utc) + timedelta(hours=24),
            'iat': datetime.now(timezone.utc)
        }
        token = jwt.encode(payload, wrong_secret, algorithm=JWT_ALGORITHM)
        
        with pytest.raises(Exception):
            decode_token(token)

    def test_create_token_with_special_characters(self):
        """Test token creation with special characters in user data."""
        token = create_token("user@123#$%", "test+alias@example.com")
        payload = decode_token(token)
        assert payload['user_id'] == "user@123#$%"
        assert payload['email'] == "test+alias@example.com"

    def test_token_expiry_time(self):
        """Test that token expiry is set correctly."""
        token = create_token("user123", "test@example.com")
        payload = decode_token(token)
        exp_timestamp = payload['exp']
        iat_timestamp = payload['iat']
        # Expiry should be approximately JWT_EXPIRY_HOURS after creation
        expiry_seconds = exp_timestamp - iat_timestamp
        expected_seconds = JWT_EXPIRY_HOURS * 3600
        # Allow 1 second tolerance
        assert abs(expiry_seconds - expected_seconds) <= 1


class TestJWTEdgeCases:
    """Edge case tests for JWT functionality."""

    def test_empty_user_id(self):
        """Test token creation with empty user_id."""
        token = create_token("", "test@example.com")
        payload = decode_token(token)
        assert payload['user_id'] == ""

    def test_empty_email(self):
        """Test token creation with empty email."""
        token = create_token("user123", "")
        payload = decode_token(token)
        assert payload['email'] == ""

    def test_none_values(self):
        """Test token creation with None values."""
        token = create_token(None, None)
        payload = decode_token(token)
        assert payload['user_id'] is None
        assert payload['email'] is None

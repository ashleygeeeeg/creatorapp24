"""Pytest configuration and fixtures for backend tests."""
import os
import asyncio
from typing import AsyncGenerator, Generator
import pytest
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# Set test environment variables before importing server
os.environ['MONGO_URL'] = 'mongodb://localhost:27017'
os.environ['DB_NAME'] = 'creatorapp24_test'
os.environ['JWT_SECRET'] = 'test-secret-key-for-testing-only'
os.environ['JWT_EXPIRY_HOURS'] = '24'
os.environ['EMERGENT_LLM_KEY'] = 'test-llm-key'
os.environ['CORS_ORIGINS'] = '*'
os.environ['PUBLIC_WEB_URL'] = 'http://localhost:3000'
os.environ['PUBLIC_API_URL'] = 'http://localhost:8000'
os.environ['APPCREATOR24_APP_URL'] = 'https://www.appcreator24.com'


@pytest.fixture
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Check if MongoDB is available for integration tests
try:
    client = MongoClient(os.environ['MONGO_URL'], serverSelectionTimeoutMS=1000)
    client.server_info()
    MONGO_AVAILABLE = True
    client.close()
except ConnectionFailure:
    MONGO_AVAILABLE = False


@pytest.fixture(scope='session')
def mongo_available() -> bool:
    """Check if MongoDB is available for testing."""
    return MONGO_AVAILABLE


@pytest.fixture
def mongo_client() -> AsyncIOMotorClient:
    """Create a test MongoDB client."""
    return AsyncIOMotorClient(os.environ['MONGO_URL'])


@pytest.fixture
async def db(mongo_client: AsyncIOMotorClient) -> AsyncGenerator[AsyncIOMotorClient, None]:
    """Create a test database instance."""
    db = mongo_client[os.environ['DB_NAME']]
    # Clear all collections before each test
    collections = await db.list_collection_names()
    for collection_name in collections:
        if not collection_name.startswith('system.'):
            await db[collection_name].delete_many({})
    yield db
    # Clean up after test
    collections = await db.list_collection_names()
    for collection_name in collections:
        if not collection_name.startswith('system.'):
            await db[collection_name].delete_many({})


# Import server after setting environment variables
from backend.server import app, get_current_user, get_optional_user, db as app_db


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Create a TestClient for FastAPI app."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def test_user_data() -> dict:
    """Sample user data for testing."""
    return {
        'email': 'test@example.com',
        'password': 'testpassword123',
        'name': 'Test User'
    }


@pytest.fixture
def another_user_data() -> dict:
    """Sample data for another user."""
    return {
        'email': 'another@example.com',
        'password': 'anotherpassword456',
        'name': 'Another User'
    }


@pytest.fixture
def sample_build_data() -> dict:
    """Sample build data for testing."""
    return {
        'name': 'Test Build',
        'description': 'A test build'
    }


@pytest.fixture
def sample_waitlist_data() -> dict:
    """Sample waitlist entry data."""
    return {
        'email': 'waitlist@example.com',
        'name': 'Waitlist User'
    }

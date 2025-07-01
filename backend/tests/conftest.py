"""Test configuration for pytest."""

import pytest
from app import create_app
from tests.mocks.mock_firebase import MockFirebaseService

@pytest.fixture
def mock_firebase():
    """Create a mock Firebase service."""
    return MockFirebaseService()

@pytest.fixture
def app(mock_firebase):
    """Create a test Flask application."""
    app = create_app('testing')
    
    # Replace Firebase service with mock
    from app.services.firebase_service import firebase_service
    firebase_service.db = mock_firebase.db
    
    return app

@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create a test CLI runner."""
    return app.test_cli_runner()

@pytest.fixture
def mock_config():
    """Sample configuration data for testing."""
    return {
        'openai_api_key': 'sk-test123456789',
        'firebase_project_id': 'test-project',
        'google_analytics_id': 'GA-12345',
        'google_ads_id': 'ADS-12345'
    } 
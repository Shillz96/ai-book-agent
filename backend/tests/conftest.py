"""Test configuration for pytest."""

import pytest
import os
from app import create_app
from tests.mocks.mock_firebase import MockFirebaseService
from tests.mocks.mock_social_media import MockSocialMediaManager

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

@pytest.fixture
def mock_social_config():
    """Mock social media configuration for testing."""
    return {
        'TWITTER_API_KEY': 'mock_twitter_key',
        'TWITTER_API_SECRET': 'mock_twitter_secret', 
        'TWITTER_ACCESS_TOKEN': 'mock_twitter_token',
        'TWITTER_ACCESS_TOKEN_SECRET': 'mock_twitter_token_secret',
        'FACEBOOK_ACCESS_TOKEN': 'mock_facebook_token',
        'FACEBOOK_PAGE_ID': 'mock_facebook_page',
        'INSTAGRAM_ACCESS_TOKEN': 'mock_instagram_token',
        'INSTAGRAM_BUSINESS_ACCOUNT_ID': 'mock_instagram_account',
        'PINTEREST_ACCESS_TOKEN': 'mock_pinterest_token',
        'PINTEREST_BOARD_ID': 'mock_pinterest_board'
    }

@pytest.fixture
def mock_social_manager(mock_social_config):
    """Create a mock social media manager for testing."""
    return MockSocialMediaManager(mock_social_config)

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment variables."""
    # Enable testing mode
    os.environ['TESTING'] = 'true'
    os.environ['MOCK_SOCIAL_MEDIA'] = 'true'
    
    # Set mock API keys to avoid 401 errors in tests
    test_env_vars = {
        'OPENAI_API_KEY': 'sk-test-key-for-testing-purposes-only',
        'TWITTER_API_KEY': 'mock_twitter_key',
        'FACEBOOK_ACCESS_TOKEN': 'mock_facebook_token',
        'INSTAGRAM_ACCESS_TOKEN': 'mock_instagram_token',
        'PINTEREST_ACCESS_TOKEN': 'mock_pinterest_token'
    }
    
    for key, value in test_env_vars.items():
        if key not in os.environ:
            os.environ[key] = value
    
    yield
    
    # Clean up after tests
    for key in test_env_vars:
        if os.environ.get(key) == test_env_vars[key]:
            del os.environ[key]
    
    if 'TESTING' in os.environ:
        del os.environ['TESTING']
    if 'MOCK_SOCIAL_MEDIA' in os.environ:
        del os.environ['MOCK_SOCIAL_MEDIA'] 
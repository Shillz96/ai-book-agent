import pytest
from flask import Flask
from app import create_app
from app.services.configuration_service import ConfigurationService
from app.services.firebase_service import FirebaseService

@pytest.fixture
def app():
    """Create and configure a test Flask application."""
    app = create_app('testing')
    return app

@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()

@pytest.fixture
def mock_config():
    """Sample configuration data for testing."""
    return {
        'openai_api_key': 'sk-test123456789',
        'firebase_project_id': 'test-project',
        'google_analytics_id': 'GA-12345',
        'google_ads_id': 'ADS-12345'
    }

def test_health_check(client):
    """Test the basic health check endpoint."""
    response = client.get('/api/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'

def test_detailed_health_check(client):
    """Test the detailed health check endpoint."""
    response = client.get('/api/health/detailed')
    assert response.status_code == 200
    data = response.get_json()
    assert 'services' in data
    assert 'api' in data['services']
    assert 'firebase' in data['services']
    assert 'configuration' in data['services']

def test_configuration_endpoints(client, mock_config):
    """Test the configuration endpoints."""
    # Test saving configuration
    response = client.post('/api/configuration', json=mock_config)
    assert response.status_code == 200
    
    # Test retrieving configuration
    response = client.get('/api/configuration')
    assert response.status_code == 200
    data = response.get_json()
    assert data['firebase_project_id'] == mock_config['firebase_project_id']
    # API key should be masked
    assert '...' in data['openai_api_key']

def test_configuration_validation(client, mock_config):
    """Test configuration validation."""
    response = client.post('/api/configuration/validate', json=mock_config)
    assert response.status_code == 200
    data = response.get_json()
    assert data['valid'] == True
    
    # Test with invalid OpenAI key
    invalid_config = mock_config.copy()
    invalid_config['openai_api_key'] = 'invalid-key'
    response = client.post('/api/configuration/validate', json=invalid_config)
    assert response.status_code == 200
    data = response.get_json()
    assert data['valid'] == False
    assert any('Invalid OpenAI API Key' in error for error in data['errors'])

def test_error_handling(client):
    """Test error handling in configuration endpoints."""
    # Test with invalid JSON
    response = client.post('/api/configuration', data='invalid json')
    assert response.status_code == 500
    
    # Test with missing required fields
    response = client.post('/api/configuration', json={})
    assert response.status_code == 200  # Should still accept empty config
    
    # Test validation with empty config
    response = client.post('/api/configuration/validate', json={})
    assert response.status_code == 200
    data = response.get_json()
    assert 'valid' in data 
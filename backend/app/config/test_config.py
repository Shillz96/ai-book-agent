"""Test configuration for the AI Book Marketing Agent."""

class TestConfig:
    """Test configuration settings."""
    
    TESTING = True
    DEBUG = True
    
    # Use a test database
    FIREBASE_PROJECT_ID = 'test-project'
    
    # Test API keys
    OPENAI_API_KEY = 'sk-test123456789'
    GOOGLE_ANALYTICS_ID = 'GA-12345'
    GOOGLE_ADS_ID = 'ADS-12345'
    
    # Test mode settings
    AUTONOMOUS_MODE = False
    
    # Security settings
    SECRET_KEY = 'test-secret-key'
    
    # Mock Firebase credentials for testing
    FIREBASE_CREDENTIALS = {
        'type': 'service_account',
        'project_id': FIREBASE_PROJECT_ID,
        'private_key_id': 'test-key-id',
        'private_key': '-----BEGIN PRIVATE KEY-----\ntest\n-----END PRIVATE KEY-----\n',
        'client_email': 'test@test-project.iam.gserviceaccount.com',
        'client_id': 'test-client-id',
        'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
        'token_uri': 'https://oauth2.googleapis.com/token',
        'auth_provider_x509_cert_url': 'https://www.googleapis.com/oauth2/v1/certs',
        'client_x509_cert_url': 'https://www.googleapis.com/robot/v1/metadata/x509/test'
    } 
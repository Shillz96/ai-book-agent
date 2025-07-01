"""Tests for the validation service."""

import unittest
from unittest.mock import patch
from app.services.validation_service import ValidationService

class TestValidationService(unittest.TestCase):
    """Test cases for ValidationService."""

    def setUp(self):
        """Set up test cases."""
        self.validation_service = ValidationService()

    def test_validate_openai_key_valid(self):
        """Test valid OpenAI API key validation."""
        result = self.validation_service.validate_openai_key('sk-test123456789')
        self.assertTrue(result)

    def test_validate_openai_key_invalid(self):
        """Test invalid OpenAI API key validation."""
        result = self.validation_service.validate_openai_key('invalid-key')
        self.assertFalse(result)

    def test_validate_firebase_project_id_valid(self):
        """Test valid Firebase project ID validation."""
        result = self.validation_service.validate_firebase_project_id('my-project-123')
        self.assertTrue(result)

    def test_validate_firebase_project_id_invalid(self):
        """Test invalid Firebase project ID validation."""
        result = self.validation_service.validate_firebase_project_id('')
        self.assertFalse(result)

    def test_validate_analytics_id_valid(self):
        """Test valid Google Analytics ID validation."""
        result = self.validation_service.validate_analytics_id('GA-12345')
        self.assertTrue(result)

    def test_validate_analytics_id_invalid(self):
        """Test invalid Google Analytics ID validation."""
        result = self.validation_service.validate_analytics_id('invalid-id')
        self.assertFalse(result)

    def test_validate_ads_id_valid(self):
        """Test valid Google Ads ID validation."""
        result = self.validation_service.validate_ads_id('ADS-12345')
        self.assertTrue(result)

    def test_validate_ads_id_invalid(self):
        """Test invalid Google Ads ID validation."""
        result = self.validation_service.validate_ads_id('invalid-id')
        self.assertFalse(result)

    def test_validate_configuration(self):
        """Test full configuration validation."""
        config = {
            'openai_api_key': 'sk-test123456789',
            'firebase_project_id': 'my-project-123',
            'google_analytics_id': 'GA-12345',
            'google_ads_id': 'ADS-12345'
        }

        results = self.validation_service.validate_configuration(config)
        self.assertTrue(results['valid'])
        self.assertEqual(len(results['errors']), 0)

if __name__ == '__main__':
    unittest.main() 
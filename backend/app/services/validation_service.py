"""Validation service for the AI Book Marketing Agent."""

import openai
import re
from typing import Dict, Any

class ValidationService:
    """Service for validating configuration settings."""

    def __init__(self):
        """Initialize the validation service."""
        self.validation_rules = {
            'openai_api_key': self.validate_openai_key,
            'firebase_project_id': self.validate_firebase_project_id,
            'google_analytics_id': self.validate_analytics_id,
            'google_ads_id': self.validate_ads_id
        }

    def validate_configuration(self, config_data):
        """Validate all configuration settings.
        
        Args:
            config_data: Dictionary containing configuration settings
            
        Returns:
            Dictionary with validation results
        """
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }

        for key, value in config_data.items():
            if key in self.validation_rules:
                if not self.validation_rules[key](value):
                    validation_results['errors'].append(f'Invalid {key}')
                    validation_results['valid'] = False

        return validation_results

    def validate_openai_key(self, api_key):
        """Validate OpenAI API Key format.
        
        Args:
            api_key: OpenAI API key to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        return isinstance(api_key, str) and api_key.startswith('sk-') and len(api_key) > 20

    def validate_firebase_project_id(self, project_id):
        """Validate Firebase Project ID.
        
        Args:
            project_id: Firebase project ID to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        return isinstance(project_id, str) and bool(project_id.strip())

    def validate_analytics_id(self, analytics_id):
        """Validate Google Analytics ID.
        
        Args:
            analytics_id: Google Analytics ID to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        return isinstance(analytics_id, str) and analytics_id.startswith('GA-')

    def validate_ads_id(self, ads_id):
        """Validate Google Ads ID.
        
        Args:
            ads_id: Google Ads ID to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        return isinstance(ads_id, str) and ads_id.startswith('ADS-')

    def _validate_firebase_project_id(self, project_id: str) -> Dict[str, Any]:
        """
        Validate Firebase project ID format
        Args:
            project_id: Firebase project ID to validate
        Returns:
            Dict containing validation result and message
        """
        if not project_id:
            return {
                'valid': False,
                'message': 'Project ID is required'
            }

        # Firebase project IDs must be between 6-30 characters
        # and can only contain lowercase letters, numbers, and hyphens
        if not re.match(r'^[a-z0-9-]{6,30}$', project_id):
            return {
                'valid': False,
                'message': 'Project ID must be 6-30 characters long and can only contain lowercase letters, numbers, and hyphens'
            }

        return {
            'valid': True,
            'message': 'Project ID format is valid'
        }

    def _validate_analytics_id(self, analytics_id: str) -> Dict[str, Any]:
        """
        Validate Google Analytics measurement ID format
        Args:
            analytics_id: Google Analytics ID to validate
        Returns:
            Dict containing validation result and message
        """
        if not analytics_id:
            return {
                'valid': True,
                'message': 'Analytics ID is optional'
            }

        # Google Analytics 4 measurement IDs start with 'G-' followed by 10 characters
        if not re.match(r'^G-[A-Z0-9]{10}$', analytics_id):
            return {
                'valid': False,
                'message': 'Invalid Analytics ID format. Should be in format G-XXXXXXXXXX'
            }

        return {
            'valid': True,
            'message': 'Analytics ID format is valid'
        }

    def _validate_ads_id(self, ads_id: str) -> Dict[str, Any]:
        """
        Validate Google Ads ID format
        Args:
            ads_id: Google Ads ID to validate
        Returns:
            Dict containing validation result and message
        """
        if not ads_id:
            return {
                'valid': True,
                'message': 'Ads ID is optional'
            }

        # Google Ads conversion IDs are typically 10 digits
        if not re.match(r'^\d{10}$', ads_id):
            return {
                'valid': False,
                'message': 'Invalid Ads ID format. Should be a 10-digit number'
            }

        return {
            'valid': True,
            'message': 'Ads ID format is valid'
        } 
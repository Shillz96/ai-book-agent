"""Configuration service for the AI Book Marketing Agent."""

import os
import json
from firebase_admin import firestore
from .firebase_service import FirebaseService

class ConfigurationService:
    """Service for managing application configuration."""

    def __init__(self):
        """Initialize the configuration service."""
        self.firebase = FirebaseService()
        self.db = firestore.client()
        self.config_collection = 'configurations'
        self.config_doc = 'system_config'

    def get_configuration(self):
        """Retrieve configuration from Firestore."""
        try:
            doc_ref = self.db.collection(self.config_collection).document(self.config_doc)
            doc = doc_ref.get()
            
            if doc.exists:
                config = doc.to_dict()
                # Remove sensitive data before sending
                if 'openai_api_key' in config:
                    config['openai_api_key'] = self._mask_key(config['openai_api_key'])
                return config
            return {}
        except Exception as e:
            raise Exception(f"Error retrieving configuration: {str(e)}")

    def save_configuration(self, config_data):
        """Save configuration to Firestore."""
        try:
            doc_ref = self.db.collection(self.config_collection).document(self.config_doc)
            
            # Get existing config to preserve sensitive data if not updated
            existing_config = doc_ref.get()
            if existing_config.exists:
                existing_data = existing_config.to_dict()
                # Only update API key if a new one is provided
                if not config_data.get('openai_api_key'):
                    config_data['openai_api_key'] = existing_data.get('openai_api_key', '')

            doc_ref.set(config_data, merge=True)
            return True
        except Exception as e:
            raise Exception(f"Error saving configuration: {str(e)}")

    def validate_configuration(self, config_data):
        """Validate configuration settings."""
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }

        # Validate OpenAI API Key
        if 'openai_api_key' in config_data:
            if not self._validate_openai_key(config_data['openai_api_key']):
                validation_results['errors'].append('Invalid OpenAI API Key')
                validation_results['valid'] = False

        # Validate Firebase Project ID
        if 'firebase_project_id' in config_data:
            if not self._validate_firebase_project(config_data['firebase_project_id']):
                validation_results['errors'].append('Invalid Firebase Project ID')
                validation_results['valid'] = False

        return validation_results

    def _validate_openai_key(self, api_key):
        """Validate OpenAI API Key format."""
        return api_key.startswith('sk-') and len(api_key) > 20

    def _validate_firebase_project(self, project_id):
        """Validate Firebase Project ID."""
        return bool(project_id and isinstance(project_id, str))

    def _mask_key(self, key):
        """Mask sensitive key data."""
        if not key:
            return ''
        return f"{key[:4]}...{key[-4:]}" 
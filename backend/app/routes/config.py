"""
Configuration routes for user settings and API key management.
Provides endpoints for users to configure their API keys and settings.
"""

from flask import Blueprint, request, jsonify
import logging
from ..services import firebase_service, config_loader

logger = logging.getLogger(__name__)

config_bp = Blueprint('config', __name__)

@config_bp.route('/config/<app_id>/<user_id>', methods=['GET'])
def get_user_config(app_id, user_id):
    """Get user configuration settings."""
    try:
        if not config_loader:
            return jsonify({'error': 'Configuration service not available'}), 500
        
        user_config = config_loader.get_user_config(user_id, app_id)
        
        # Remove sensitive information from response
        safe_config = {}
        for service, settings in user_config.items():
            if isinstance(settings, dict):
                safe_config[service] = {}
                for key, value in settings.items():
                    if 'key' in key.lower() or 'token' in key.lower() or 'secret' in key.lower():
                        # Only show if key is configured (masked)
                        safe_config[service][key] = '***configured***' if value else ''
                    else:
                        safe_config[service][key] = value
            else:
                safe_config[service] = settings
        
        return jsonify({
            'config': safe_config,
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error getting user config: {str(e)}")
        return jsonify({'error': str(e)}), 500

@config_bp.route('/config/<app_id>/<user_id>', methods=['POST'])
def update_user_config(app_id, user_id):
    """Update user configuration settings."""
    try:
        if not firebase_service:
            return jsonify({'error': 'Firebase service not available'}), 500
        
        config_data = request.get_json()
        if not config_data:
            return jsonify({'error': 'No configuration data provided'}), 400
        
        # Validate required fields based on configuration type
        validation_errors = _validate_config_data(config_data)
        if validation_errors:
            return jsonify({'error': 'Validation failed', 'details': validation_errors}), 400
        
        # Save configuration to Firebase
        doc_ref = firebase_service.db.collection('artifacts').document(app_id).collection('users').document(user_id).collection('userSettings').document('settings')
        doc_ref.set(config_data, merge=True)
        
        # Invalidate cache
        if config_loader:
            config_loader.invalidate_cache(user_id, app_id)
        
        logger.info(f"Updated configuration for user {user_id}")
        return jsonify({
            'message': 'Configuration updated successfully',
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error updating user config: {str(e)}")
        return jsonify({'error': str(e)}), 500

@config_bp.route('/config/<app_id>/<user_id>/validate', methods=['POST'])
def validate_config(app_id, user_id):
    """Validate user configuration without saving."""
    try:
        config_data = request.get_json()
        if not config_data:
            return jsonify({'error': 'No configuration data provided'}), 400
        
        validation_results = _validate_config_data(config_data, test_connections=True)
        
        return jsonify({
            'validation_results': validation_results,
            'status': 'success' if not validation_results else 'validation_errors'
        })
        
    except Exception as e:
        logger.error(f"Error validating config: {str(e)}")
        return jsonify({'error': str(e)}), 500

def _validate_config_data(config_data, test_connections=False):
    """Validate configuration data structure and optionally test connections."""
    errors = []
    
    # Validate OpenAI configuration
    openai_config = config_data.get('openai', {})
    if 'apiKey' in openai_config:
        if not openai_config['apiKey'] or len(openai_config['apiKey']) < 10:
            errors.append('OpenAI API key is too short or empty')
    
    # Validate Google services configuration
    google_config = config_data.get('google', {})
    if google_config:
        if 'analytics' in google_config:
            analytics = google_config['analytics']
            if 'propertyId' in analytics and analytics['propertyId']:
                if not analytics['propertyId'].startswith('GA'):
                    errors.append('Google Analytics Property ID should start with "GA"')
        
        if 'ads' in google_config:
            ads = google_config['ads']
            required_ads_fields = ['customerId', 'developerToken']
            for field in required_ads_fields:
                if field not in ads or not ads[field]:
                    errors.append(f'Google Ads {field} is required')
    
    # Validate social media configurations
    social_platforms = ['twitter', 'facebook', 'instagram', 'pinterest']
    for platform in social_platforms:
        platform_config = config_data.get(platform, {})
        if platform_config:
            # Each platform has different required fields
            if platform == 'twitter':
                required_fields = ['apiKey', 'apiSecret', 'accessToken', 'accessTokenSecret']
            elif platform == 'facebook':
                required_fields = ['accessToken', 'pageId']
            elif platform == 'instagram':
                required_fields = ['accessToken', 'businessAccountId']
            elif platform == 'pinterest':
                required_fields = ['accessToken', 'boardId']
            
            for field in required_fields:
                if field not in platform_config or not platform_config[field]:
                    errors.append(f'{platform.title()} {field} is required')
    
    # Validate budget configuration
    budget_config = config_data.get('budget', {})
    if budget_config:
        monthly_budget = budget_config.get('monthlyBudget', 0)
        if isinstance(monthly_budget, (int, float)) and monthly_budget < 0:
            errors.append('Monthly budget must be positive')
    
    return errors 
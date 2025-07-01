"""Configuration management endpoints for the AI Book Marketing Agent."""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging
from ..config import Config
from ..services import firebase_service

# Create blueprint
config_bp = Blueprint('config', __name__)

# Configure logging
logger = logging.getLogger(__name__)

# Simple in-memory cache for user configs to avoid hitting Firebase on every request
config_cache = {}
CACHE_DURATION = timedelta(minutes=5)  # Cache configs for 5 minutes

def get_cached_config(user_id: str) -> Optional[Dict[str, Any]]:
    """Get cached config if still valid."""
    if user_id in config_cache:
        cached_data, timestamp = config_cache[user_id]
        if datetime.now() - timestamp < CACHE_DURATION:
            return cached_data
    return None

def cache_config(user_id: str, config_data: Dict[str, Any]) -> None:
    """Cache config data with timestamp."""
    config_cache[user_id] = (config_data, datetime.now())

def clear_config_cache(user_id: str) -> None:
    """Clear cached config for a user."""
    if user_id in config_cache:
        del config_cache[user_id]

@config_bp.route("/config/<user_id>", methods=["GET"])
def get_user_config(user_id):
    """
    Get user configuration from Firebase.
    This replaces reading from .env files.
    """
    try:
        if not firebase_service:
            return jsonify({"error": "Firebase service not initialized"}), 500
        
        # Check cache first
        cached_config = get_cached_config(user_id)
        if cached_config:
            logger.info(f"Returning cached config for user {user_id}")
            return jsonify({
                "success": True,
                "config": cached_config,
                "source": "cache",
                "timestamp": datetime.now().isoformat()
            })
        
        app_id = request.args.get("app_id", Config.DEFAULT_APP_ID)
        
        # Get user settings from Firebase (this contains all the API keys and config)
        user_settings = firebase_service.get_user_settings(app_id, user_id)
        
        if not user_settings:
            # Return default/fallback config for new users
            default_config = get_default_config()
            cache_config(user_id, default_config)
            
            return jsonify({
                "success": True,
                "config": default_config,
                "source": "default",
                "timestamp": datetime.now().isoformat(),
                "message": "No user config found, using defaults"
            })
        
        # Extract configuration values from user settings
        config_data = extract_config_from_settings(user_settings)
        
        # Cache the config
        cache_config(user_id, config_data)
        
        return jsonify({
            "success": True,
            "config": config_data,
            "source": "firebase",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting user config: {str(e)}")
        return jsonify({"error": str(e)}), 500

@config_bp.route("/config/<user_id>", methods=["POST"])
def save_user_config(user_id):
    """
    Save user configuration to Firebase.
    This replaces editing .env files.
    """
    try:
        if not firebase_service:
            return jsonify({"error": "Firebase service not initialized"}), 500
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        config_data = data.get("config")
        if not config_data:
            return jsonify({"error": "config data is required"}), 400
        
        app_id = data.get("app_id", Config.DEFAULT_APP_ID)
        
        # Validate configuration data
        validation_errors = validate_config_data(config_data)
        if validation_errors:
            return jsonify({
                "error": "Configuration validation failed",
                "validation_errors": validation_errors
            }), 400
        
        # Convert config data to user settings format
        user_settings = convert_config_to_settings(config_data)
        
        # Save to Firebase
        success = save_config_to_firebase(app_id, user_id, user_settings)
        
        if not success:
            return jsonify({"error": "Failed to save configuration"}), 500
        
        # Clear cache so next request gets fresh data
        clear_config_cache(user_id)
        
        return jsonify({
            "success": True,
            "message": "Configuration saved successfully",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error saving user config: {str(e)}")
        return jsonify({"error": str(e)}), 500

@config_bp.route("/config/<user_id>/validate", methods=["POST"])
def validate_user_config(user_id):
    """
    Validate user configuration by testing API connections.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        config_data = data.get("config")
        if not config_data:
            return jsonify({"error": "config data is required"}), 400
        
        # Test each service with the provided configuration
        validation_results = test_config_services(config_data)
        
        return jsonify({
            "success": True,
            "validation_results": validation_results,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error validating user config: {str(e)}")
        return jsonify({"error": str(e)}), 500

def get_default_config() -> Dict[str, Any]:
    """
    Get default configuration that falls back to .env values for local development.
    """
    return {
        # OpenAI Configuration
        "openai": {
            "apiKey": Config.OPENAI_API_KEY or "",
            "model": Config.OPENAI_MODEL or "gpt-4"
        },
        
        # Firebase Configuration
        "firebase": {
            "projectId": Config.FIREBASE_PROJECT_ID or "",
            "credentialsPath": Config.FIREBASE_CREDENTIALS_PATH or ""
        },
        
        # Social Media API Keys
        "twitter": {
            "apiKey": Config.TWITTER_API_KEY or "",
            "apiSecret": Config.TWITTER_API_SECRET or "",
            "accessToken": Config.TWITTER_ACCESS_TOKEN or "",
            "accessTokenSecret": Config.TWITTER_ACCESS_TOKEN_SECRET or ""
        },
        
        "facebook": {
            "accessToken": Config.FACEBOOK_ACCESS_TOKEN or "",
            "pageId": Config.FACEBOOK_PAGE_ID or ""
        },
        
        "instagram": {
            "accessToken": Config.INSTAGRAM_ACCESS_TOKEN or "",
            "businessAccountId": Config.INSTAGRAM_BUSINESS_ACCOUNT_ID or ""
        },
        
        "pinterest": {
            "accessToken": Config.PINTEREST_ACCESS_TOKEN or "",
            "boardId": Config.PINTEREST_BOARD_ID or ""
        },
        
        # Google Services
        "google": {
            "analytics": {
                "propertyId": Config.GOOGLE_ANALYTICS_PROPERTY_ID or "",
                "credentialsPath": Config.GOOGLE_ANALYTICS_CREDENTIALS_PATH or ""
            },
            "ads": {
                "customerId": Config.GOOGLE_ADS_CUSTOMER_ID or "",
                "developerToken": Config.GOOGLE_ADS_DEVELOPER_TOKEN or "",
                "credentialsPath": Config.GOOGLE_ADS_CREDENTIALS_PATH or ""
            }
        },
        
        # Budget Management
        "budget": {
            "monthlyBudget": Config.MONTHLY_MARKETING_BUDGET,
            "alertThreshold": Config.BUDGET_ALERT_THRESHOLD,
            "emergencyStopThreshold": Config.EMERGENCY_STOP_THRESHOLD,
            "autoReallocation": Config.AUTO_BUDGET_REALLOCATION
        },
        
        # Autonomous Operation Settings
        "autonomous": {
            "enabled": Config.AUTONOMOUS_MODE,
            "dailyPostSchedule": Config.DAILY_POST_SCHEDULE,
            "weeklyReportDay": Config.WEEKLY_REPORT_DAY,
            "weeklyReportTime": Config.WEEKLY_REPORT_TIME,
            "autoOptimization": Config.AUTO_OPTIMIZATION_ENABLED,
            "minConfidenceThreshold": Config.MIN_CONFIDENCE_THRESHOLD
        },
        
        # Book Information
        "book": {
            "title": Config.BOOK_TITLE,
            "amazonUrl": Config.BOOK_AMAZON_URL,
            "audibleUrl": Config.BOOK_AUDIBLE_URL,
            "landingPageUrl": Config.LANDING_PAGE_URL,
            "primaryAudience": Config.PRIMARY_AUDIENCE,
            "targetAgeRange": Config.TARGET_AGE_RANGE,
            "geographicTargets": Config.GEOGRAPHIC_TARGETS
        },
        
        # Performance Thresholds
        "performance": {
            "minEngagementRate": Config.MIN_ENGAGEMENT_RATE,
            "minCTR": Config.MIN_CTR,
            "targetROAS": Config.TARGET_ROAS,
            "minConversionRate": Config.MIN_CONVERSION_RATE
        }
    }

def extract_config_from_settings(user_settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract configuration data from user settings stored in Firebase.
    Maps the frontend Settings.js structure to our config format.
    """
    # Get values from user settings with fallbacks to env vars
    def safe_get(settings, *keys, default=""):
        """Safely navigate nested dictionary keys."""
        current = settings
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current if current is not None else default
    
    return {
        "openai": {
            "apiKey": safe_get(user_settings, "openai", "apiKey", default=Config.OPENAI_API_KEY or ""),
            "model": safe_get(user_settings, "openai", "model", default=Config.OPENAI_MODEL or "gpt-4")
        },
        
        "firebase": {
            "projectId": safe_get(user_settings, "firebase", "projectId", default=Config.FIREBASE_PROJECT_ID or ""),
            "credentialsPath": safe_get(user_settings, "firebase", "credentialsPath", default=Config.FIREBASE_CREDENTIALS_PATH or "")
        },
        
        "twitter": {
            "apiKey": safe_get(user_settings, "twitter", "apiKey", default=Config.TWITTER_API_KEY or ""),
            "apiSecret": safe_get(user_settings, "twitter", "apiSecret", default=Config.TWITTER_API_SECRET or ""),
            "accessToken": safe_get(user_settings, "twitter", "accessToken", default=Config.TWITTER_ACCESS_TOKEN or ""),
            "accessTokenSecret": safe_get(user_settings, "twitter", "accessTokenSecret", default=Config.TWITTER_ACCESS_TOKEN_SECRET or "")
        },
        
        "facebook": {
            "accessToken": safe_get(user_settings, "facebook", "accessToken", default=Config.FACEBOOK_ACCESS_TOKEN or ""),
            "pageId": safe_get(user_settings, "facebook", "pageId", default=Config.FACEBOOK_PAGE_ID or "")
        },
        
        "instagram": {
            "accessToken": safe_get(user_settings, "instagram", "accessToken", default=Config.INSTAGRAM_ACCESS_TOKEN or ""),
            "businessAccountId": safe_get(user_settings, "instagram", "businessAccountId", default=Config.INSTAGRAM_BUSINESS_ACCOUNT_ID or "")
        },
        
        "pinterest": {
            "accessToken": safe_get(user_settings, "pinterest", "accessToken", default=Config.PINTEREST_ACCESS_TOKEN or ""),
            "boardId": safe_get(user_settings, "pinterest", "boardId", default=Config.PINTEREST_BOARD_ID or "")
        },
        
        "google": {
            "analytics": {
                "propertyId": safe_get(user_settings, "googleAnalytics", "propertyId", default=Config.GOOGLE_ANALYTICS_PROPERTY_ID or ""),
                "credentialsPath": safe_get(user_settings, "googleAnalytics", "credentialsPath", default=Config.GOOGLE_ANALYTICS_CREDENTIALS_PATH or "")
            },
            "ads": {
                "customerId": safe_get(user_settings, "googleAds", "customerId", default=Config.GOOGLE_ADS_CUSTOMER_ID or ""),
                "developerToken": safe_get(user_settings, "googleAds", "developerToken", default=Config.GOOGLE_ADS_DEVELOPER_TOKEN or ""),
                "credentialsPath": safe_get(user_settings, "googleAds", "credentialsPath", default=Config.GOOGLE_ADS_CREDENTIALS_PATH or "")
            }
        },
        
        "budget": {
            "monthlyBudget": safe_get(user_settings, "budget", "monthlyBudget", default=Config.MONTHLY_MARKETING_BUDGET),
            "alertThreshold": safe_get(user_settings, "budget", "alertThreshold", default=Config.BUDGET_ALERT_THRESHOLD),
            "emergencyStopThreshold": safe_get(user_settings, "budget", "emergencyStopThreshold", default=Config.EMERGENCY_STOP_THRESHOLD),
            "autoReallocation": safe_get(user_settings, "budget", "autoReallocation", default=Config.AUTO_BUDGET_REALLOCATION)
        },
        
        "autonomous": {
            "enabled": safe_get(user_settings, "autonomous", "enabled", default=Config.AUTONOMOUS_MODE),
            "dailyPostSchedule": safe_get(user_settings, "autonomous", "dailyPostSchedule", default=Config.DAILY_POST_SCHEDULE),
            "weeklyReportDay": safe_get(user_settings, "autonomous", "weeklyReportDay", default=Config.WEEKLY_REPORT_DAY),
            "weeklyReportTime": safe_get(user_settings, "autonomous", "weeklyReportTime", default=Config.WEEKLY_REPORT_TIME),
            "autoOptimization": safe_get(user_settings, "autonomous", "autoOptimization", default=Config.AUTO_OPTIMIZATION_ENABLED),
            "minConfidenceThreshold": safe_get(user_settings, "autonomous", "minConfidenceThreshold", default=Config.MIN_CONFIDENCE_THRESHOLD)
        },
        
        "book": {
            "title": safe_get(user_settings, "book", "title", default=Config.BOOK_TITLE),
            "amazonUrl": safe_get(user_settings, "book", "amazonUrl", default=Config.BOOK_AMAZON_URL),
            "audibleUrl": safe_get(user_settings, "book", "audibleUrl", default=Config.BOOK_AUDIBLE_URL),
            "landingPageUrl": safe_get(user_settings, "book", "landingPageUrl", default=Config.LANDING_PAGE_URL),
            "primaryAudience": safe_get(user_settings, "book", "primaryAudience", default=Config.PRIMARY_AUDIENCE),
            "targetAgeRange": safe_get(user_settings, "book", "targetAgeRange", default=Config.TARGET_AGE_RANGE),
            "geographicTargets": safe_get(user_settings, "book", "geographicTargets", default=Config.GEOGRAPHIC_TARGETS)
        },
        
        "performance": {
            "minEngagementRate": safe_get(user_settings, "performance", "minEngagementRate", default=Config.MIN_ENGAGEMENT_RATE),
            "minCTR": safe_get(user_settings, "performance", "minCTR", default=Config.MIN_CTR),
            "targetROAS": safe_get(user_settings, "performance", "targetROAS", default=Config.TARGET_ROAS),
            "minConversionRate": safe_get(user_settings, "performance", "minConversionRate", default=Config.MIN_CONVERSION_RATE)
        }
    }

def convert_config_to_settings(config_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert config data to the user settings format expected by Firebase.
    This matches the structure used in Settings.js.
    """
    return config_data  # Since our config structure matches Settings.js structure

def validate_config_data(config_data: Dict[str, Any]) -> list:
    """
    Validate configuration data and return list of errors.
    """
    errors = []
    
    # Check required OpenAI API key
    openai_key = config_data.get("openai", {}).get("apiKey", "")
    if openai_key and not openai_key.startswith("sk-"):
        errors.append("OpenAI API key must start with 'sk-'")
    
    # Check budget values
    budget = config_data.get("budget", {})
    monthly_budget = budget.get("monthlyBudget", 0)
    if monthly_budget and (not isinstance(monthly_budget, (int, float)) or monthly_budget <= 0):
        errors.append("Monthly budget must be a positive number")
    
    alert_threshold = budget.get("alertThreshold", 0.8)
    if not isinstance(alert_threshold, (int, float)) or alert_threshold <= 0 or alert_threshold > 1:
        errors.append("Alert threshold must be between 0 and 1")
    
    # Check performance thresholds
    performance = config_data.get("performance", {})
    for field in ["minEngagementRate", "minCTR", "minConversionRate"]:
        value = performance.get(field, 0)
        if value and (not isinstance(value, (int, float)) or value < 0 or value > 1):
            errors.append(f"{field} must be between 0 and 1")
    
    return errors

def save_config_to_firebase(app_id: str, user_id: str, user_settings: Dict[str, Any]) -> bool:
    """
    Save configuration to Firebase using the Firebase service.
    """
    try:
        from firebase_admin import firestore
        
        # Add timestamp
        user_settings['lastUpdated'] = firestore.SERVER_TIMESTAMP
        
        # Save to Firebase (same path as Settings.js uses)
        doc_ref = firebase_service.db.collection('settings').document(user_id)
        doc_ref.set(user_settings, merge=True)
        
        logger.info(f"Saved configuration for user {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving configuration to Firebase: {str(e)}")
        return False

def test_config_services(config_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Test configuration by attempting to connect to each service.
    Returns a dictionary of service_name -> test_result.
    """
    results = {}
    
    # Test OpenAI
    try:
        openai_key = config_data.get("openai", {}).get("apiKey", "")
        if openai_key:
            import openai
            client = openai.OpenAI(api_key=openai_key)
            # Test with a simple completion
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=5
            )
            results["openai"] = {"status": "success", "message": "OpenAI API key is valid"}
        else:
            results["openai"] = {"status": "skipped", "message": "No API key provided"}
    except Exception as e:
        results["openai"] = {"status": "error", "message": str(e)}
    
    # Test Firebase (basic connectivity check)
    try:
        firebase_project = config_data.get("firebase", {}).get("projectId", "")
        if firebase_project and firebase_service and firebase_service.db:
            # Test by trying to read a dummy document
            firebase_service.db.collection('test').limit(1).get()
            results["firebase"] = {"status": "success", "message": "Firebase connection is working"}
        else:
            results["firebase"] = {"status": "skipped", "message": "Firebase not configured or not available"}
    except Exception as e:
        results["firebase"] = {"status": "error", "message": str(e)}
    
    # Add tests for other services as needed (Twitter, Facebook, etc.)
    # For now, just mark them as not tested
    for service in ["twitter", "facebook", "instagram", "pinterest", "google"]:
        results[service] = {"status": "not_tested", "message": "Service testing not implemented yet"}
    
    return results 
"""
Dynamic Configuration Loader Service

This service replaces static .env configuration with user-specific configuration
loaded from Firebase. Each service can request configuration for a specific user
and get their personalized API keys and settings.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from ..config import Config

# Configure logging
logger = logging.getLogger(__name__)

class ConfigLoader:
    """
    Dynamic configuration loader that fetches user-specific settings from Firebase.
    
    This replaces the static environment variable approach with user-specific
    configuration that can be managed through the web interface.
    """
    
    def __init__(self, firebase_service=None):
        """
        Initialize the config loader with Firebase service.
        
        Args:
            firebase_service: Firebase service instance for database access
        """
        self.firebase_service = firebase_service
        self.config_cache = {}  # Simple in-memory cache
        self.cache_duration = timedelta(minutes=5)  # Cache for 5 minutes
        
    def get_user_config(self, user_id: str, app_id: str = None) -> Dict[str, Any]:
        """
        Get complete configuration for a user.
        
        Args:
            user_id: User ID to get configuration for
            app_id: Application ID (optional, uses default if not provided)
            
        Returns:
            Dictionary containing user configuration with fallbacks to .env values
        """
        if not app_id:
            app_id = Config.DEFAULT_APP_ID
            
        # Check cache first
        cache_key = f"{user_id}:{app_id}"
        cached_config = self._get_cached_config(cache_key)
        if cached_config:
            logger.debug(f"Returning cached config for user {user_id}")
            return cached_config
        
        try:
            # Get user settings from Firebase
            if self.firebase_service:
                user_settings = self.firebase_service.get_user_settings(app_id, user_id)
            else:
                user_settings = None
            
            # Build configuration with fallbacks
            config = self._build_config_with_fallbacks(user_settings)
            
            # Cache the result
            self._cache_config(cache_key, config)
            
            logger.info(f"Loaded configuration for user {user_id} from Firebase")
            return config
            
        except Exception as e:
            logger.error(f"Error loading user config: {str(e)}")
            # Return fallback configuration on error
            return self._get_fallback_config()
    
    def get_openai_config(self, user_id: str, app_id: str = None) -> Dict[str, str]:
        """
        Get OpenAI configuration for a user.
        
        Args:
            user_id: User ID
            app_id: Application ID (optional)
            
        Returns:
            Dictionary with apiKey and model
        """
        config = self.get_user_config(user_id, app_id)
        return config.get("openai", {
            "apiKey": Config.OPENAI_API_KEY or "",
            "model": Config.OPENAI_MODEL or "gpt-4"
        })
    
    def get_social_media_config(self, user_id: str, platform: str, app_id: str = None) -> Dict[str, str]:
        """
        Get social media platform configuration for a user.
        
        Args:
            user_id: User ID
            platform: Platform name (twitter, facebook, instagram, pinterest)
            app_id: Application ID (optional)
            
        Returns:
            Dictionary with platform-specific configuration
        """
        config = self.get_user_config(user_id, app_id)
        return config.get(platform, {})
    
    def get_google_services_config(self, user_id: str, service: str = None, app_id: str = None) -> Dict[str, str]:
        """
        Get Google services configuration for a user.
        
        Args:
            user_id: User ID
            service: Specific service (analytics, ads) or None for all
            app_id: Application ID (optional)
            
        Returns:
            Dictionary with Google services configuration
        """
        config = self.get_user_config(user_id, app_id)
        google_config = config.get("google", {})
        
        if service:
            return google_config.get(service, {})
        return google_config
    
    def get_budget_config(self, user_id: str, app_id: str = None) -> Dict[str, Any]:
        """
        Get budget configuration for a user.
        
        Args:
            user_id: User ID
            app_id: Application ID (optional)
            
        Returns:
            Dictionary with budget settings
        """
        config = self.get_user_config(user_id, app_id)
        return config.get("budget", {
            "monthlyBudget": Config.MONTHLY_MARKETING_BUDGET,
            "alertThreshold": Config.BUDGET_ALERT_THRESHOLD,
            "emergencyStopThreshold": Config.EMERGENCY_STOP_THRESHOLD,
            "autoReallocation": Config.AUTO_BUDGET_REALLOCATION
        })
    
    def get_autonomous_config(self, user_id: str, app_id: str = None) -> Dict[str, Any]:
        """
        Get autonomous operation configuration for a user.
        
        Args:
            user_id: User ID
            app_id: Application ID (optional)
            
        Returns:
            Dictionary with autonomous settings
        """
        config = self.get_user_config(user_id, app_id)
        return config.get("autonomous", {
            "enabled": Config.AUTONOMOUS_MODE,
            "dailyPostSchedule": Config.DAILY_POST_SCHEDULE,
            "weeklyReportDay": Config.WEEKLY_REPORT_DAY,
            "weeklyReportTime": Config.WEEKLY_REPORT_TIME,
            "autoOptimization": Config.AUTO_OPTIMIZATION_ENABLED,
            "minConfidenceThreshold": Config.MIN_CONFIDENCE_THRESHOLD
        })
    
    def get_book_config(self, user_id: str, app_id: str = None) -> Dict[str, Any]:
        """
        Get book information configuration for a user.
        
        Args:
            user_id: User ID
            app_id: Application ID (optional)
            
        Returns:
            Dictionary with book information
        """
        config = self.get_user_config(user_id, app_id)
        return config.get("book", {
            "title": Config.BOOK_TITLE,
            "amazonUrl": Config.BOOK_AMAZON_URL,
            "audibleUrl": Config.BOOK_AUDIBLE_URL,
            "landingPageUrl": Config.LANDING_PAGE_URL,
            "primaryAudience": Config.PRIMARY_AUDIENCE,
            "targetAgeRange": Config.TARGET_AGE_RANGE,
            "geographicTargets": Config.GEOGRAPHIC_TARGETS
        })
    
    def invalidate_cache(self, user_id: str, app_id: str = None) -> None:
        """
        Invalidate cached configuration for a user.
        
        Args:
            user_id: User ID
            app_id: Application ID (optional)
        """
        if not app_id:
            app_id = Config.DEFAULT_APP_ID
            
        cache_key = f"{user_id}:{app_id}"
        if cache_key in self.config_cache:
            del self.config_cache[cache_key]
            logger.info(f"Invalidated config cache for user {user_id}")
    
    def _get_cached_config(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached config if still valid."""
        if cache_key in self.config_cache:
            cached_data, timestamp = self.config_cache[cache_key]
            if datetime.now() - timestamp < self.cache_duration:
                return cached_data
        return None
    
    def _cache_config(self, cache_key: str, config_data: Dict[str, Any]) -> None:
        """Cache config data with timestamp."""
        self.config_cache[cache_key] = (config_data, datetime.now())
    
    def _build_config_with_fallbacks(self, user_settings: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Build configuration dictionary with fallbacks to environment variables.
        
        Args:
            user_settings: User settings from Firebase (can be None)
            
        Returns:
            Complete configuration dictionary
        """
        if not user_settings:
            return self._get_fallback_config()
        
        def safe_get(settings, *keys, default=""):
            """Safely navigate nested dictionary keys with fallback."""
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
    
    def _get_fallback_config(self) -> Dict[str, Any]:
        """
        Get fallback configuration using environment variables.
        Used when Firebase is not available or user has no settings.
        """
        return {
            "openai": {
                "apiKey": Config.OPENAI_API_KEY or "",
                "model": Config.OPENAI_MODEL or "gpt-4"
            },
            "firebase": {
                "projectId": Config.FIREBASE_PROJECT_ID or "",
                "credentialsPath": Config.FIREBASE_CREDENTIALS_PATH or ""
            },
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
            "budget": {
                "monthlyBudget": Config.MONTHLY_MARKETING_BUDGET,
                "alertThreshold": Config.BUDGET_ALERT_THRESHOLD,
                "emergencyStopThreshold": Config.EMERGENCY_STOP_THRESHOLD,
                "autoReallocation": Config.AUTO_BUDGET_REALLOCATION
            },
            "autonomous": {
                "enabled": Config.AUTONOMOUS_MODE,
                "dailyPostSchedule": Config.DAILY_POST_SCHEDULE,
                "weeklyReportDay": Config.WEEKLY_REPORT_DAY,
                "weeklyReportTime": Config.WEEKLY_REPORT_TIME,
                "autoOptimization": Config.AUTO_OPTIMIZATION_ENABLED,
                "minConfidenceThreshold": Config.MIN_CONFIDENCE_THRESHOLD
            },
            "book": {
                "title": Config.BOOK_TITLE,
                "amazonUrl": Config.BOOK_AMAZON_URL,
                "audibleUrl": Config.BOOK_AUDIBLE_URL,
                "landingPageUrl": Config.LANDING_PAGE_URL,
                "primaryAudience": Config.PRIMARY_AUDIENCE,
                "targetAgeRange": Config.TARGET_AGE_RANGE,
                "geographicTargets": Config.GEOGRAPHIC_TARGETS
            },
            "performance": {
                "minEngagementRate": Config.MIN_ENGAGEMENT_RATE,
                "minCTR": Config.MIN_CTR,
                "targetROAS": Config.TARGET_ROAS,
                "minConversionRate": Config.MIN_CONVERSION_RATE
            }
        }


# Global config loader instance
config_loader = None

def initialize_config_loader(firebase_service=None):
    """Initialize the global config loader instance."""
    global config_loader
    config_loader = ConfigLoader(firebase_service)
    logger.info("Config loader initialized")

def get_config_loader() -> Optional[ConfigLoader]:
    """Get the global config loader instance."""
    return config_loader 
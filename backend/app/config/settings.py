"""Configuration settings for the AI Book Marketing Agent."""

import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Production-ready configuration settings class."""
    
    # Flask settings - Production ready
    SECRET_KEY = os.getenv("SECRET_KEY", os.urandom(32).hex())  # Generate secure key if not provided
    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"  # Default to production mode
    TESTING = False
    
    # OpenAI settings - Production API
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
    
    # Firebase settings - Production database
    FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")
    FIREBASE_CREDENTIALS_PATH = os.getenv(
        "FIREBASE_CREDENTIALS_PATH",
        os.path.join(os.path.dirname(__file__), "../../firebase-credentials.json")
    )
    
    # Google Analytics settings - Production tracking
    GOOGLE_ANALYTICS_PROPERTY_ID = os.getenv("GOOGLE_ANALYTICS_PROPERTY_ID")
    GOOGLE_ANALYTICS_CREDENTIALS_PATH = os.getenv("GOOGLE_ANALYTICS_CREDENTIALS_PATH")
    
    # Google Ads settings - Production advertising
    GOOGLE_ADS_CUSTOMER_ID = os.getenv("GOOGLE_ADS_CUSTOMER_ID")
    GOOGLE_ADS_DEVELOPER_TOKEN = os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN")
    GOOGLE_ADS_CREDENTIALS_PATH = os.getenv("GOOGLE_ADS_CREDENTIALS_PATH")
    
    # Social Media Platform Credentials - Production APIs
    TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
    TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
    TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
    TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
    
    FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")
    FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
    
    INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    INSTAGRAM_BUSINESS_ACCOUNT_ID = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")
    
    PINTEREST_ACCESS_TOKEN = os.getenv("PINTEREST_ACCESS_TOKEN")
    PINTEREST_BOARD_ID = os.getenv("PINTEREST_BOARD_ID")
    
    # Application settings - Production configuration
    DEFAULT_APP_ID = os.getenv("DEFAULT_APP_ID", "ai-book-agent")
    AUTONOMOUS_MODE = os.getenv("AUTONOMOUS_MODE", "false").lower() == "true"
    
    # Content generation settings - Production limits
    MAX_POSTS_PER_DAY = int(os.getenv("MAX_POSTS_PER_DAY", "10"))
    MIN_POST_INTERVAL = int(os.getenv("MIN_POST_INTERVAL", "3600"))  # seconds
    
    # Budget settings - Production budget management
    MONTHLY_MARKETING_BUDGET = float(os.getenv("MONTHLY_MARKETING_BUDGET", "500.0"))
    DEFAULT_DAILY_BUDGET = float(os.getenv("DEFAULT_DAILY_BUDGET", "50.0"))
    MAX_DAILY_BUDGET = float(os.getenv("MAX_DAILY_BUDGET", "500.0"))
    BUDGET_ALERT_THRESHOLD = float(os.getenv("BUDGET_ALERT_THRESHOLD", "0.8"))
    EMERGENCY_STOP_THRESHOLD = float(os.getenv("EMERGENCY_STOP_THRESHOLD", "0.95"))
    AUTO_BUDGET_REALLOCATION = os.getenv("AUTO_BUDGET_REALLOCATION", "true").lower() == "true"
    
    # Autonomous operation settings - Production automation
    DAILY_POST_SCHEDULE = os.getenv("DAILY_POST_SCHEDULE", "9:00,14:00,19:00").split(",")
    WEEKLY_REPORT_DAY = os.getenv("WEEKLY_REPORT_DAY", "monday").lower()
    WEEKLY_REPORT_TIME = os.getenv("WEEKLY_REPORT_TIME", "09:00")
    AUTO_OPTIMIZATION_ENABLED = os.getenv("AUTO_OPTIMIZATION_ENABLED", "true").lower() == "true"
    MIN_CONFIDENCE_THRESHOLD = float(os.getenv("MIN_CONFIDENCE_THRESHOLD", "0.7"))
    
    # Book information - Production book details
    BOOK_TITLE = os.getenv("BOOK_TITLE", "Unstoppable - the young athlete's guide to rock solid mental strength")
    BOOK_AMAZON_URL = os.getenv("BOOK_AMAZON_URL", "https://amazon.com/dp/your-book-id")
    BOOK_AUDIBLE_URL = os.getenv("BOOK_AUDIBLE_URL", "https://audible.com/pd/your-book-id")
    LANDING_PAGE_URL = os.getenv("LANDING_PAGE_URL", "https://your-landing-page.com")
    
    # Target audience - Production targeting
    PRIMARY_AUDIENCE = os.getenv("PRIMARY_AUDIENCE", "youth athletes, parents, coaches")
    TARGET_AGE_RANGE = os.getenv("TARGET_AGE_RANGE", "13-25")
    GEOGRAPHIC_TARGETS = os.getenv("GEOGRAPHIC_TARGETS", "US,CA,UK,AU").split(",")
    
    # Performance thresholds - Production metrics
    MIN_ENGAGEMENT_RATE = float(os.getenv("MIN_ENGAGEMENT_RATE", "0.02"))
    MIN_CTR = float(os.getenv("MIN_CTR", "0.01"))
    TARGET_ROAS = float(os.getenv("TARGET_ROAS", "3.0"))
    MIN_CONVERSION_RATE = float(os.getenv("MIN_CONVERSION_RATE", "0.005"))
    
    # Redis configuration for production task queue
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Production server settings
    PORT = int(os.getenv("PORT", "5000"))
    HOST = os.getenv("HOST", "0.0.0.0")
    
    @classmethod
    def validate_config(cls) -> List[str]:
        """Validate the production configuration and return a list of missing required settings."""
        missing = []
        warnings = []
        
        # Check critical production settings
        if not cls.OPENAI_API_KEY:
            missing.append("OPENAI_API_KEY")
        if not cls.FIREBASE_PROJECT_ID:
            missing.append("FIREBASE_PROJECT_ID")
        if not cls.FIREBASE_CREDENTIALS_PATH or not os.path.exists(cls.FIREBASE_CREDENTIALS_PATH):
            missing.append("FIREBASE_CREDENTIALS_PATH (file not found)")
        
        # Check for production-specific security
        if cls.SECRET_KEY == "dev-secret-key-123":
            warnings.append("SECRET_KEY should be changed from default value for production")
        
        # Check autonomous mode requirements
        if cls.AUTONOMOUS_MODE:
            if not cls.GOOGLE_ANALYTICS_PROPERTY_ID:
                missing.append("GOOGLE_ANALYTICS_PROPERTY_ID (required for autonomous mode)")
            if not cls.GOOGLE_ADS_CUSTOMER_ID:
                missing.append("GOOGLE_ADS_CUSTOMER_ID (required for autonomous mode)")
            if not cls.GOOGLE_ADS_DEVELOPER_TOKEN:
                missing.append("GOOGLE_ADS_DEVELOPER_TOKEN (required for autonomous mode)")
        
        # Check social media platform configurations
        social_platforms = {
            'Twitter': ['TWITTER_API_KEY', 'TWITTER_API_SECRET', 'TWITTER_ACCESS_TOKEN', 'TWITTER_ACCESS_TOKEN_SECRET'],
            'Facebook': ['FACEBOOK_ACCESS_TOKEN', 'FACEBOOK_PAGE_ID'],
            'Instagram': ['INSTAGRAM_ACCESS_TOKEN', 'INSTAGRAM_BUSINESS_ACCOUNT_ID'],
            'Pinterest': ['PINTEREST_ACCESS_TOKEN', 'PINTEREST_BOARD_ID']
        }
        
        for platform, required_keys in social_platforms.items():
            if not all(getattr(cls, key, None) for key in required_keys):
                warnings.append(f"{platform} credentials incomplete - platform will be disabled")
        
        # Log warnings but don't treat as missing
        if warnings:
            import logging
            logger = logging.getLogger(__name__)
            for warning in warnings:
                logger.warning(warning)
        
        return missing
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production mode."""
        return not cls.DEBUG and not cls.TESTING
    
    @classmethod
    def get_enabled_platforms(cls) -> List[str]:
        """Get list of enabled social media platforms based on available credentials."""
        enabled = []
        
        if all(getattr(cls, key, None) for key in ['TWITTER_API_KEY', 'TWITTER_API_SECRET', 'TWITTER_ACCESS_TOKEN', 'TWITTER_ACCESS_TOKEN_SECRET']):
            enabled.append('twitter')
        
        if all(getattr(cls, key, None) for key in ['FACEBOOK_ACCESS_TOKEN', 'FACEBOOK_PAGE_ID']):
            enabled.append('facebook')
        
        if all(getattr(cls, key, None) for key in ['INSTAGRAM_ACCESS_TOKEN', 'INSTAGRAM_BUSINESS_ACCOUNT_ID']):
            enabled.append('instagram')
        
        if all(getattr(cls, key, None) for key in ['PINTEREST_ACCESS_TOKEN', 'PINTEREST_BOARD_ID']):
            enabled.append('pinterest')
        
        return enabled 
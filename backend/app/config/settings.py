"""Configuration settings for the AI Book Marketing Agent."""

import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration settings class."""
    
    # Flask settings
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-123")
    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    
    # OpenAI settings
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
    
    # Firebase settings
    FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")
    FIREBASE_CREDENTIALS_PATH = os.getenv(
        "FIREBASE_CREDENTIALS_PATH",
        os.path.join(os.path.dirname(__file__), "../../firebase-credentials.json")
    )
    
    # Google Analytics settings
    GOOGLE_ANALYTICS_PROPERTY_ID = os.getenv("GOOGLE_ANALYTICS_PROPERTY_ID")
    
    # Google Ads settings
    GOOGLE_ADS_CUSTOMER_ID = os.getenv("GOOGLE_ADS_CUSTOMER_ID")
    GOOGLE_ADS_DEVELOPER_TOKEN = os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN")
    
    # Application settings
    DEFAULT_APP_ID = os.getenv("DEFAULT_APP_ID", "ai-book-agent")
    AUTONOMOUS_MODE = os.getenv("AUTONOMOUS_MODE", "false").lower() == "true"
    
    # Content generation settings
    MAX_POSTS_PER_DAY = int(os.getenv("MAX_POSTS_PER_DAY", "10"))
    MIN_POST_INTERVAL = int(os.getenv("MIN_POST_INTERVAL", "3600"))  # seconds
    
    # Budget settings
    DEFAULT_DAILY_BUDGET = float(os.getenv("DEFAULT_DAILY_BUDGET", "50.0"))
    MAX_DAILY_BUDGET = float(os.getenv("MAX_DAILY_BUDGET", "500.0"))
    
    @classmethod
    def validate_config(cls) -> List[str]:
        """Validate the configuration and return a list of missing required settings."""
        missing = []
        
        # Check required settings
        if not cls.SECRET_KEY:
            missing.append("SECRET_KEY")
        if not cls.OPENAI_API_KEY:
            missing.append("OPENAI_API_KEY")
        if not cls.FIREBASE_PROJECT_ID:
            missing.append("FIREBASE_PROJECT_ID")
        
        # Check optional but recommended settings
        if cls.AUTONOMOUS_MODE:
            if not cls.GOOGLE_ANALYTICS_PROPERTY_ID:
                missing.append("GOOGLE_ANALYTICS_PROPERTY_ID (required for autonomous mode)")
            if not cls.GOOGLE_ADS_CUSTOMER_ID:
                missing.append("GOOGLE_ADS_CUSTOMER_ID (required for autonomous mode)")
        
        return missing 
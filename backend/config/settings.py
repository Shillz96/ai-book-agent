import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """
    Configuration class for the AI Book Marketing Agent backend.
    Manages all environment variables and settings for autonomous operation.
    """
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4')
    
    # Firebase Configuration
    FIREBASE_CREDENTIALS_PATH = os.getenv('FIREBASE_CREDENTIALS_PATH', 'config/firebase-credentials.json')
    FIREBASE_PROJECT_ID = os.getenv('FIREBASE_PROJECT_ID')
    
    # Social Media API Keys
    TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
    TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
    TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
    TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
    
    FACEBOOK_ACCESS_TOKEN = os.getenv('FACEBOOK_ACCESS_TOKEN')
    FACEBOOK_PAGE_ID = os.getenv('FACEBOOK_PAGE_ID')
    
    INSTAGRAM_ACCESS_TOKEN = os.getenv('INSTAGRAM_ACCESS_TOKEN')
    INSTAGRAM_BUSINESS_ACCOUNT_ID = os.getenv('INSTAGRAM_BUSINESS_ACCOUNT_ID')
    
    PINTEREST_ACCESS_TOKEN = os.getenv('PINTEREST_ACCESS_TOKEN')
    PINTEREST_BOARD_ID = os.getenv('PINTEREST_BOARD_ID')
    
    # Google Analytics & Ads Configuration
    GOOGLE_ANALYTICS_PROPERTY_ID = os.getenv('GOOGLE_ANALYTICS_PROPERTY_ID')
    GOOGLE_ANALYTICS_CREDENTIALS_PATH = os.getenv('GOOGLE_ANALYTICS_CREDENTIALS_PATH')
    GOOGLE_ADS_CUSTOMER_ID = os.getenv('GOOGLE_ADS_CUSTOMER_ID')
    GOOGLE_ADS_DEVELOPER_TOKEN = os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN')
    GOOGLE_ADS_CREDENTIALS_PATH = os.getenv('GOOGLE_ADS_CREDENTIALS_PATH')
    
    # Budget Management Configuration
    MONTHLY_MARKETING_BUDGET = float(os.getenv('MONTHLY_MARKETING_BUDGET', 500.0))
    BUDGET_ALERT_THRESHOLD = float(os.getenv('BUDGET_ALERT_THRESHOLD', 0.8))
    EMERGENCY_STOP_THRESHOLD = float(os.getenv('EMERGENCY_STOP_THRESHOLD', 0.95))
    AUTO_BUDGET_REALLOCATION = os.getenv('AUTO_BUDGET_REALLOCATION', 'true').lower() == 'true'
    
    # Autonomous Operation Settings
    AUTONOMOUS_MODE = os.getenv('AUTONOMOUS_MODE', 'true').lower() == 'true'
    DAILY_POST_SCHEDULE = os.getenv('DAILY_POST_SCHEDULE', '9:00,14:00,19:00').split(',')
    WEEKLY_REPORT_DAY = os.getenv('WEEKLY_REPORT_DAY', 'monday').lower()
    WEEKLY_REPORT_TIME = os.getenv('WEEKLY_REPORT_TIME', '09:00')
    AUTO_OPTIMIZATION_ENABLED = os.getenv('AUTO_OPTIMIZATION_ENABLED', 'true').lower() == 'true'
    MIN_CONFIDENCE_THRESHOLD = float(os.getenv('MIN_CONFIDENCE_THRESHOLD', 0.7))
    
    # Book Information
    BOOK_TITLE = os.getenv('BOOK_TITLE', 'Unstoppable - the young athlete\'s guide to rock solid mental strength')
    BOOK_AMAZON_URL = os.getenv('BOOK_AMAZON_URL', 'https://amazon.com/dp/your-book-id')
    BOOK_AUDIBLE_URL = os.getenv('BOOK_AUDIBLE_URL', 'https://audible.com/pd/your-book-id')
    LANDING_PAGE_URL = os.getenv('LANDING_PAGE_URL', 'https://your-landing-page.com')
    
    # Target Audience Configuration
    PRIMARY_AUDIENCE = os.getenv('PRIMARY_AUDIENCE', 'youth athletes, parents, coaches')
    TARGET_AGE_RANGE = os.getenv('TARGET_AGE_RANGE', '13-25')
    GEOGRAPHIC_TARGETS = os.getenv('GEOGRAPHIC_TARGETS', 'US,CA,UK,AU').split(',')
    
    # Performance Thresholds
    MIN_ENGAGEMENT_RATE = float(os.getenv('MIN_ENGAGEMENT_RATE', 0.02))
    MIN_CTR = float(os.getenv('MIN_CTR', 0.01))
    TARGET_ROAS = float(os.getenv('TARGET_ROAS', 3.0))
    MIN_CONVERSION_RATE = float(os.getenv('MIN_CONVERSION_RATE', 0.005))
    
    # Redis Configuration (for task queue and caching)
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # App Configuration
    DEFAULT_APP_ID = os.getenv('DEFAULT_APP_ID', 'unstoppable-book-agent')
    
    @classmethod
    def validate_config(cls):
        """
        Validate that all required configuration variables are present.
        
        Returns:
            List of missing configuration variables
        """
        required_vars = [
            'OPENAI_API_KEY',
            'FIREBASE_PROJECT_ID'
        ]
        
        # Google Analytics/Ads required for autonomous operation
        if cls.AUTONOMOUS_MODE:
            required_vars.extend([
                'GOOGLE_ANALYTICS_PROPERTY_ID',
                'GOOGLE_ANALYTICS_CREDENTIALS_PATH',
                'GOOGLE_ADS_CUSTOMER_ID',
                'GOOGLE_ADS_DEVELOPER_TOKEN',
                'GOOGLE_ADS_CREDENTIALS_PATH'
            ])
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        return missing_vars
    
    @classmethod
    def get_social_media_config(cls):
        """
        Get social media API configuration.
        
        Returns:
            Dictionary of social media API configurations
        """
        return {
            'TWITTER_API_KEY': cls.TWITTER_API_KEY,
            'TWITTER_API_SECRET': cls.TWITTER_API_SECRET,
            'TWITTER_ACCESS_TOKEN': cls.TWITTER_ACCESS_TOKEN,
            'TWITTER_ACCESS_TOKEN_SECRET': cls.TWITTER_ACCESS_TOKEN_SECRET,
            'FACEBOOK_ACCESS_TOKEN': cls.FACEBOOK_ACCESS_TOKEN,
            'FACEBOOK_PAGE_ID': cls.FACEBOOK_PAGE_ID,
            'INSTAGRAM_ACCESS_TOKEN': cls.INSTAGRAM_ACCESS_TOKEN,
            'INSTAGRAM_BUSINESS_ACCOUNT_ID': cls.INSTAGRAM_BUSINESS_ACCOUNT_ID,
            'PINTEREST_ACCESS_TOKEN': cls.PINTEREST_ACCESS_TOKEN,
            'PINTEREST_BOARD_ID': cls.PINTEREST_BOARD_ID
        }
    
    @classmethod
    def get_google_services_config(cls):
        """
        Get Google services configuration.
        
        Returns:
            Dictionary of Google Analytics and Ads configurations
        """
        return {
            'analytics': {
                'property_id': cls.GOOGLE_ANALYTICS_PROPERTY_ID,
                'credentials_path': cls.GOOGLE_ANALYTICS_CREDENTIALS_PATH
            },
            'ads': {
                'customer_id': cls.GOOGLE_ADS_CUSTOMER_ID,
                'developer_token': cls.GOOGLE_ADS_DEVELOPER_TOKEN,
                'credentials_path': cls.GOOGLE_ADS_CREDENTIALS_PATH
            }
        }
    
    @classmethod
    def get_autonomous_config(cls):
        """
        Get autonomous operation configuration.
        
        Returns:
            Dictionary of autonomous operation settings
        """
        return {
            'enabled': cls.AUTONOMOUS_MODE,
            'post_schedule': cls.DAILY_POST_SCHEDULE,
            'weekly_report_day': cls.WEEKLY_REPORT_DAY,
            'weekly_report_time': cls.WEEKLY_REPORT_TIME,
            'auto_optimization': cls.AUTO_OPTIMIZATION_ENABLED,
            'min_confidence': cls.MIN_CONFIDENCE_THRESHOLD,
            'budget_management': {
                'monthly_budget': cls.MONTHLY_MARKETING_BUDGET,
                'alert_threshold': cls.BUDGET_ALERT_THRESHOLD,
                'emergency_threshold': cls.EMERGENCY_STOP_THRESHOLD,
                'auto_reallocation': cls.AUTO_BUDGET_REALLOCATION
            },
            'performance_thresholds': {
                'min_engagement_rate': cls.MIN_ENGAGEMENT_RATE,
                'min_ctr': cls.MIN_CTR,
                'target_roas': cls.TARGET_ROAS,
                'min_conversion_rate': cls.MIN_CONVERSION_RATE
            }
        }
    
    @classmethod
    def get_book_config(cls):
        """
        Get book-specific configuration.
        
        Returns:
            Dictionary of book information and targeting
        """
        return {
            'title': cls.BOOK_TITLE,
            'amazon_url': cls.BOOK_AMAZON_URL,
            'audible_url': cls.BOOK_AUDIBLE_URL,
            'landing_page_url': cls.LANDING_PAGE_URL,
            'target_audience': {
                'primary_audience': cls.PRIMARY_AUDIENCE,
                'age_range': cls.TARGET_AGE_RANGE,
                'geographic_targets': cls.GEOGRAPHIC_TARGETS
            }
        } 
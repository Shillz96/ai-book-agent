"""Services package for the AI Book Marketing Agent."""

import logging
import os
from typing import Dict, Any
from ..config import Config

# Configure logging
logger = logging.getLogger(__name__)

# Global service instances
firebase_service = None
content_generator = None
social_media_manager = None
revenue_growth_manager = None
performance_analytics = None
google_analytics_service = None
google_ads_service = None
autonomous_manager = None
budget_manager = None
scheduler_service = None
config_loader = None

def initialize_services():
    """Initialize all backend services."""
    global firebase_service, content_generator, social_media_manager
    global revenue_growth_manager, performance_analytics, google_analytics_service
    global google_ads_service, autonomous_manager, budget_manager, scheduler_service
    global config_loader
    
    try:
        # Import service classes
        from .firebase_service import FirebaseService
        from .content_generator import ContentGenerator
        from .social_media_manager import SocialMediaManager
        from .async_social_media_manager import AsyncSocialMediaManager
        from .revenue_growth_manager import RevenueGrowthManager
        from .performance_analytics import PerformanceAnalytics
        from .google_analytics_service import GoogleAnalyticsService
        from .google_ads_service import GoogleAdsService
        from .autonomous_manager import AutonomousMarketingManager
        from .budget_manager import BudgetManager
        from .scheduler_service import SchedulerService
        from .config_loader import initialize_config_loader, get_config_loader
        
        # Validate configuration
        missing_configs = Config.validate_config()
        if missing_configs:
            logger.warning(f"Missing configuration: {', '.join(missing_configs)}")
            # Continue initialization even with missing configs since we now have dynamic loading
        
        logger.info("Starting service initialization...")
        
        # Initialize Firebase service first (needed by config loader)
        if Config.FIREBASE_PROJECT_ID and os.path.exists(Config.FIREBASE_CREDENTIALS_PATH):
            firebase_service = FirebaseService(
                Config.FIREBASE_CREDENTIALS_PATH,
                Config.FIREBASE_PROJECT_ID
            )
            logger.info("Firebase service initialized successfully")
        else:
            logger.warning("Firebase configuration missing or credentials file not found")
        
        # Initialize Config Loader (depends on Firebase)
        initialize_config_loader(firebase_service)
        config_loader = get_config_loader()
        logger.info("Config loader initialized successfully")
        
        # Initialize Content Generator with dynamic config support
        # We still need a fallback OpenAI key for initial setup, but services will use user-specific keys
        if Config.OPENAI_API_KEY:
            content_generator = ContentGenerator(
                Config.OPENAI_API_KEY,
                Config.OPENAI_MODEL,
                config_loader=config_loader  # Pass config loader for dynamic loading
            )
            logger.info("Content generator initialized successfully")
        else:
            logger.warning("OpenAI API key not configured - content generation will require user configuration")
        
        logger.info("Service initialization completed")
        
    except Exception as e:
        logger.error(f"Error initializing services: {str(e)}")
        raise

def get_service_status() -> Dict[str, bool]:
    """Get the status of all services."""
    return {
        "firebase": firebase_service is not None,
        "content_generator": content_generator is not None,
        "social_media": social_media_manager is not None,
        "google_analytics": google_analytics_service is not None,
        "google_ads": google_ads_service is not None,
        "autonomous_manager": autonomous_manager is not None,
        "budget_manager": budget_manager is not None,
        "scheduler": scheduler_service is not None,
        "config_loader": config_loader is not None
    } 
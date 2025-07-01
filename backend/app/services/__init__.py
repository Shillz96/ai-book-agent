"""Production services package for the AI Book Marketing Agent."""

import logging
import os
from typing import Dict, Any
from ..config import Config

# Configure production logging
logger = logging.getLogger(__name__)

# Global service instances for production
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
    """
    Initialize all backend services for production deployment.
    Implements robust error handling and fallback mechanisms for production use.
    """
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
        
        # Validate production configuration
        missing_configs = Config.validate_config()
        if missing_configs:
            logger.warning(f"Production configuration incomplete: {', '.join(missing_configs)}")
            # In production, we continue with available services rather than failing completely
        
        logger.info("Starting production service initialization...")
        
        # Initialize Firebase service first (critical for production)
        try:
            # Ensure Firebase credentials are properly configured for production
            if Config.FIREBASE_CREDENTIALS_PATH and os.path.exists(Config.FIREBASE_CREDENTIALS_PATH):
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = Config.FIREBASE_CREDENTIALS_PATH
                firebase_service = FirebaseService()
                logger.info("Production Firebase service initialized successfully")
            else:
                logger.error("Firebase credentials not found - critical service unavailable")
                # In production, Firebase is critical, so we should fail if not available
                raise Exception("Firebase configuration required for production")
        except Exception as e:
            logger.error(f"Critical Firebase initialization failed: {str(e)}")
            # In production, we need Firebase, so re-raise the exception
            raise Exception(f"Production Firebase initialization failed: {str(e)}")
        
        # Initialize Config Loader (depends on Firebase)
        try:
            initialize_config_loader(firebase_service)
            config_loader = get_config_loader()
            logger.info("Production config loader initialized successfully")
        except Exception as e:
            logger.error(f"Config loader initialization failed: {str(e)}")
            raise Exception(f"Production config loader initialization failed: {str(e)}")
        
        # Initialize Content Generator with production OpenAI API
        try:
            if Config.OPENAI_API_KEY:
                content_generator = ContentGenerator(
                    Config.OPENAI_API_KEY,
                    Config.OPENAI_MODEL,
                    config_loader=config_loader
                )
                logger.info("Production content generator initialized successfully")
            else:
                logger.error("OpenAI API key not configured - content generation unavailable")
                raise Exception("OpenAI API key required for production")
        except Exception as e:
            logger.error(f"Content generator initialization failed: {str(e)}")
            raise Exception(f"Production content generator initialization failed: {str(e)}")
        
        # Initialize Social Media Manager with production API credentials
        try:
            # Build social media configuration from environment
            social_config = {
                'TWITTER_API_KEY': Config.TWITTER_API_KEY,
                'TWITTER_API_SECRET': Config.TWITTER_API_SECRET,
                'TWITTER_ACCESS_TOKEN': Config.TWITTER_ACCESS_TOKEN,
                'TWITTER_ACCESS_TOKEN_SECRET': Config.TWITTER_ACCESS_TOKEN_SECRET,
                'FACEBOOK_ACCESS_TOKEN': Config.FACEBOOK_ACCESS_TOKEN,
                'FACEBOOK_PAGE_ID': Config.FACEBOOK_PAGE_ID,
                'INSTAGRAM_ACCESS_TOKEN': Config.INSTAGRAM_ACCESS_TOKEN,
                'INSTAGRAM_BUSINESS_ACCOUNT_ID': Config.INSTAGRAM_BUSINESS_ACCOUNT_ID,
                'PINTEREST_ACCESS_TOKEN': Config.PINTEREST_ACCESS_TOKEN,
                'PINTEREST_BOARD_ID': Config.PINTEREST_BOARD_ID
            }
            
            social_media_manager = SocialMediaManager(social_config)
            enabled_platforms = Config.get_enabled_platforms()
            logger.info(f"Production social media manager initialized with platforms: {enabled_platforms}")
        except Exception as e:
            logger.warning(f"Social media manager initialization failed: {str(e)}")
            # Social media is not critical for basic operation, so we continue
        
        # Initialize Google Analytics Service (if configured)
        try:
            if Config.GOOGLE_ANALYTICS_PROPERTY_ID and GoogleAnalyticsService:
                google_analytics_service = GoogleAnalyticsService(
                    property_id=Config.GOOGLE_ANALYTICS_PROPERTY_ID,
                    credentials_path=Config.GOOGLE_ANALYTICS_CREDENTIALS_PATH
                )
                logger.info("Production Google Analytics service initialized")
            else:
                logger.warning("Google Analytics not configured - analytics features limited")
        except Exception as e:
            logger.warning(f"Google Analytics initialization failed: {str(e)}")
        
        # Initialize Google Ads Service (if configured)
        try:
            if (Config.GOOGLE_ADS_CUSTOMER_ID and Config.GOOGLE_ADS_DEVELOPER_TOKEN 
                and Config.GOOGLE_ADS_CREDENTIALS_PATH and GoogleAdsService):
                google_ads_service = GoogleAdsService(
                    customer_id=Config.GOOGLE_ADS_CUSTOMER_ID,
                    developer_token=Config.GOOGLE_ADS_DEVELOPER_TOKEN,
                    credentials_path=Config.GOOGLE_ADS_CREDENTIALS_PATH
                )
                logger.info("Production Google Ads service initialized")
            else:
                logger.warning("Google Ads not configured - advertising features unavailable")
        except Exception as e:
            logger.warning(f"Google Ads initialization failed: {str(e)}")
        
        # Initialize Revenue Growth Manager
        try:
            if RevenueGrowthManager:
                revenue_growth_manager = RevenueGrowthManager()
                logger.info("Production Revenue Growth Manager initialized")
        except Exception as e:
            logger.warning(f"Revenue Growth Manager initialization failed: {str(e)}")
        
        # Initialize Performance Analytics
        try:
            if PerformanceAnalytics:
                performance_analytics = PerformanceAnalytics()
                logger.info("Production Performance Analytics initialized")
        except Exception as e:
            logger.warning(f"Performance Analytics initialization failed: {str(e)}")
        
        # Initialize Budget Manager
        try:
            if BudgetManager:
                budget_manager = BudgetManager()
                logger.info("Production Budget Manager initialized")
        except Exception as e:
            logger.warning(f"Budget Manager initialization failed: {str(e)}")
        
        # Initialize Scheduler Service  
        try:
            if SchedulerService:
                scheduler_service = SchedulerService()
                logger.info("Production Scheduler Service initialized")
        except Exception as e:
            logger.warning(f"Scheduler Service initialization failed: {str(e)}")
        
        # Initialize Autonomous Manager (if enabled and all dependencies available)
        try:
            if (Config.AUTONOMOUS_MODE and AutonomousMarketingManager and 
                google_analytics_service and google_ads_service):
                autonomous_manager = AutonomousMarketingManager()
                logger.info("Production Autonomous Marketing Manager initialized")
            else:
                logger.info("Autonomous mode disabled or dependencies unavailable")
        except Exception as e:
            logger.warning(f"Autonomous Manager initialization failed: {str(e)}")
        
        logger.info("Production service initialization completed successfully")
        
        # Log production service status
        _log_production_service_status()
        
    except Exception as e:
        logger.error(f"Critical error initializing production services: {str(e)}")
        raise

def _log_production_service_status():
    """Log the status of all production services for monitoring."""
    service_status = get_service_status()
    
    logger.info("=" * 50)
    logger.info("PRODUCTION SERVICE STATUS")
    logger.info("=" * 50)
    
    critical_services = ["firebase", "content_generator", "config_loader"]
    optional_services = ["social_media", "google_analytics", "google_ads", 
                        "autonomous_manager", "budget_manager", "scheduler"]
    
    # Log critical services
    logger.info("Critical Services:")
    for service in critical_services:
        status = "✓ ONLINE" if service_status.get(service, False) else "✗ OFFLINE"
        logger.info(f"  {service}: {status}")
    
    # Log optional services
    logger.info("Optional Services:")
    for service in optional_services:
        status = "✓ ONLINE" if service_status.get(service, False) else "✗ OFFLINE"
        logger.info(f"  {service}: {status}")
    
    # Overall health check
    critical_online = all(service_status.get(service, False) for service in critical_services)
    logger.info(f"Production Health: {'HEALTHY' if critical_online else 'DEGRADED'}")
    logger.info("=" * 50)

def get_service_status() -> Dict[str, bool]:
    """Get the status of all production services."""
    return {
        "firebase": firebase_service is not None,
        "content_generator": content_generator is not None,
        "social_media": social_media_manager is not None,
        "google_analytics": google_analytics_service is not None,
        "google_ads": google_ads_service is not None,
        "autonomous_manager": autonomous_manager is not None,
        "budget_manager": budget_manager is not None,
        "scheduler": scheduler_service is not None,
        "config_loader": config_loader is not None,
        "revenue_growth": revenue_growth_manager is not None,
        "performance_analytics": performance_analytics is not None
    }

def get_production_health() -> Dict[str, Any]:
    """Get detailed production health information."""
    service_status = get_service_status()
    
    critical_services = ["firebase", "content_generator", "config_loader"]
    critical_online = all(service_status.get(service, False) for service in critical_services)
    
    enabled_platforms = Config.get_enabled_platforms() if Config else []
    
    return {
        "overall_health": "HEALTHY" if critical_online else "DEGRADED",
        "critical_services_online": critical_online,
        "service_status": service_status,
        "enabled_platforms": enabled_platforms,
        "autonomous_mode": Config.AUTONOMOUS_MODE if Config else False,
        "production_mode": Config.is_production() if Config else False
    } 
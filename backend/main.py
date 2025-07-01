from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os
import asyncio
import sys
import traceback
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
import threading
import atexit
import signal

# Configure logging for production - INFO level instead of DEBUG
logging.basicConfig(
    level=logging.INFO,  # Changed to INFO for production
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Thread pool for async operations
executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix='async_worker')

# Celery configuration for production task queue
celery_app = None
try:
    from celery import Celery
    from app.services.task_queue import make_celery
    celery_app = make_celery(app)
    logger.info("Production Celery task queue initialized successfully")
except ImportError:
    logger.warning("Celery not available - using thread pool for async operations")
except Exception as e:
    logger.warning(f"Celery initialization failed: {str(e)} - using thread pool fallback")

def async_route(timeout=30):
    """
    Decorator to handle async operations in Flask routes with timeout.
    Production-ready async handling with proper error management.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Submit the async function to thread pool
                future = executor.submit(f, *args, **kwargs)
                result = future.result(timeout=timeout)
                return result
            except TimeoutError:
                logger.error(f"Operation {f.__name__} timed out after {timeout}s")
                return jsonify({"error": f"Operation timed out after {timeout} seconds"}), 408
            except Exception as e:
                logger.error(f"Error in async route {f.__name__}: {str(e)}")
                return jsonify({"error": str(e)}), 500
        return decorated_function
    return decorator

def run_async_safe(coro, timeout=30):
    """
    Safely run async coroutines with proper error handling and timeout.
    Production-grade async execution management.
    """
    try:
        # Create new event loop for thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(asyncio.wait_for(coro, timeout=timeout))
        finally:
            loop.close()
    except asyncio.TimeoutError:
        raise TimeoutError(f"Async operation timed out after {timeout} seconds")
    except Exception as e:
        logger.error(f"Error in async operation: {str(e)}")
        raise

try:
    # Load production configuration
    from app.config import Config
    app.config.from_object(Config)
    logger.info("Production configuration loaded successfully")
    
    # Production CORS configuration - restrict origins based on environment
    if Config.is_production():
        # In production, specify allowed origins explicitly
        allowed_origins = [
            "https://your-production-domain.com",  # Replace with actual production domain
            "https://ai-book-agent.vercel.app",    # Example Vercel deployment
            "https://ai-book-agent.herokuapp.com"  # Example Heroku deployment
        ]
        CORS(app, origins=allowed_origins, 
             supports_credentials=True,
             allow_headers=['Content-Type', 'Authorization'])
        logger.info(f"Production CORS enabled for origins: {allowed_origins}")
    else:
        # Development CORS - more permissive
        CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])
        logger.info("Development CORS enabled")
    
    # Import production-ready services
    from app.services.firebase_service import FirebaseService
    from app.services.content_generator import ContentGenerator
    from app.services.social_media_manager import SocialMediaManager
    from app.services.async_social_media_manager import AsyncSocialMediaManager
    from app.services.revenue_growth_manager import RevenueGrowthManager
    from app.services.performance_analytics import PerformanceAnalytics
    from app.services.budget_manager import BudgetManager
    from app.services.scheduler_service import SchedulerService
    from app.services.config_loader import initialize_config_loader, get_config_loader
    
    # Import production route blueprints
    from app.routes.config import config_bp
    from app.routes import register_routes
    
    # Production Google services integration
    GoogleAnalyticsService = None
    GoogleAdsService = None
    AutonomousMarketingManager = None
    
    try:
        from app.services.google_analytics_service import GoogleAnalyticsService
        logger.info("Production Google Analytics service available")
    except ImportError as e:
        logger.warning(f"Google Analytics service not available: {e}")
        GoogleAnalyticsService = None
        
    try:
        from app.services.google_ads_service import GoogleAdsService
        logger.info("Production Google Ads service available")
    except ImportError as e:
        logger.warning(f"Google Ads service not available: {e}")
        GoogleAdsService = None
        
    try:
        from app.services.autonomous_manager import AutonomousMarketingManager
        logger.info("Production Autonomous Marketing Manager available")
    except ImportError as e:
        logger.warning(f"Autonomous Marketing Manager not available: {e}")
        AutonomousMarketingManager = None
    
    logger.info("All production modules imported successfully")
except Exception as e:
    logger.error(f"Production startup error: {str(e)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    sys.exit(1)

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

# Background task management
background_tasks = {}
task_lock = threading.Lock()

def ensure_services_initialized():
    """
    Ensure services are initialized within Flask application context.
    This is particularly important for Celery workers and other contexts
    where services might not be initialized yet.
    """
    global firebase_service, content_generator, social_media_manager
    global revenue_growth_manager, performance_analytics, google_analytics_service
    global google_ads_service, autonomous_manager, budget_manager, scheduler_service
    
    # Check if services are already initialized
    if firebase_service is not None or content_generator is not None:
        return  # Services already initialized
    
    logger.info("Services not initialized, initializing now...")
    
    # Ensure we're within Flask application context
    from flask import has_app_context
    if not has_app_context():
        logger.error("Cannot initialize services outside Flask application context")
        raise RuntimeError("Working outside of application context")
    
    try:
        initialize_services()
        logger.info("Services initialized successfully within Flask context")
    except Exception as e:
        logger.error(f"Failed to initialize services: {str(e)}")
        raise

def initialize_services():
    """Initialize all backend services with proper error handling and integration."""
    global firebase_service, content_generator, social_media_manager
    global revenue_growth_manager, performance_analytics, google_analytics_service
    global google_ads_service, autonomous_manager, budget_manager, scheduler_service
    
    try:
        # Validate configuration
        missing_configs = Config.validate_config()
        if missing_configs:
            logger.warning(f"Missing configuration: {', '.join(missing_configs)}")
            return
        
        logger.info("Starting service initialization...")
        
        # Initialize Firebase service
        if Config.FIREBASE_PROJECT_ID and os.path.exists(Config.FIREBASE_CREDENTIALS_PATH):
            try:
                # Set environment variable for Firebase credentials
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = Config.FIREBASE_CREDENTIALS_PATH
                firebase_service = FirebaseService()
                logger.info("Firebase service initialized successfully")
            except Exception as e:
                logger.warning(f"Firebase initialization failed: {str(e)}")
                firebase_service = None
        else:
            logger.warning("Firebase configuration missing or credentials file not found")
            firebase_service = None
        
        # Initialize config loader after Firebase service
        initialize_config_loader(firebase_service)
        config_loader = get_config_loader()
        logger.info("Config loader initialized successfully")
        
        # Initialize Content Generator
        if Config.OPENAI_API_KEY:
            content_generator = ContentGenerator(
                Config.OPENAI_API_KEY,
                Config.OPENAI_MODEL,
                config_loader
            )
            logger.info("Content generator initialized successfully")
        else:
            logger.warning("OpenAI API key not configured")
        
        # Initialize Social Media Manager (async-capable wrapper)
        social_config = Config.get_social_media_config()
        social_media_manager = AsyncSocialMediaManager(social_config)
        logger.info("Async social media manager initialized successfully")
        
        # Initialize Google Analytics Service
        google_services_config = Config.get_google_services_config()
        if (GoogleAnalyticsService and google_services_config['analytics']['property_id'] and 
            google_services_config['analytics']['credentials_path']):
            google_analytics_service = GoogleAnalyticsService(
                google_services_config['analytics']['credentials_path'],
                google_services_config['analytics']['property_id']
            )
            logger.info("Google Analytics service initialized successfully")
        else:
            logger.warning("Google Analytics not available or not configured - limited autonomous functionality")
        
        # Initialize Google Ads Service
        if (GoogleAdsService and google_services_config['ads']['customer_id'] and 
            google_services_config['ads']['developer_token'] and
            google_services_config['ads']['credentials_path']):
            google_ads_service = GoogleAdsService(
                google_services_config['ads']['customer_id'],
                google_services_config['ads']['developer_token'],
                google_services_config['ads']['credentials_path']
            )
            logger.info("Google Ads service initialized successfully")
        else:
            logger.warning("Google Ads not available or not configured - limited autonomous functionality")
        
        # Initialize Budget Manager
        if firebase_service:
            budget_manager = BudgetManager(
                firebase_service,
                google_analytics_service,
                google_ads_service
            )
            logger.info("Budget Manager initialized successfully")
        
        # Initialize Performance Analytics
        if Config.OPENAI_API_KEY and firebase_service:
            performance_analytics = PerformanceAnalytics(
                Config.OPENAI_API_KEY,
                firebase_service,
                config_loader
            )
            logger.info("Performance Analytics initialized successfully")
        
        # Initialize Revenue Growth Manager
        if Config.OPENAI_API_KEY and firebase_service:
            revenue_growth_manager = RevenueGrowthManager(
                Config.OPENAI_API_KEY,
                firebase_service,
                google_analytics_service,  # Google Analytics service for real website/marketing metrics
                google_ads_service,        # Google Ads service for campaign performance data
                performance_analytics      # Performance Analytics service for content analysis
            )
            logger.info("Revenue Growth Manager initialized successfully with comprehensive data integrations")
        else:
            logger.warning("Revenue Growth Manager not initialized - missing OpenAI API key or Firebase service")
        
        # Initialize Autonomous Marketing Manager
        if (AutonomousMarketingManager and Config.OPENAI_API_KEY and firebase_service and content_generator and 
            social_media_manager and google_analytics_service):
            autonomous_manager = AutonomousMarketingManager(
                firebase_service,
                content_generator,
                social_media_manager,
                google_analytics_service,
                google_ads_service,
                Config.OPENAI_API_KEY
            )
            logger.info("Autonomous Marketing Manager initialized successfully")
        else:
            logger.warning("Cannot initialize Autonomous Manager - missing dependencies or class not available")
        
        # Initialize Scheduler Service
        if autonomous_manager and Config.AUTONOMOUS_MODE:
            scheduler_service = SchedulerService(
                autonomous_manager,
                firebase_service,
                Config
            )
            logger.info("Scheduler Service initialized successfully")
            
            # Start autonomous operations if enabled (in background)
            try:
                def start_autonomous_background():
                    run_async_safe(scheduler_service.start_autonomous_operation())
                
                executor.submit(start_autonomous_background)
                logger.info("Autonomous operations started in background")
            except Exception as e:
                logger.error(f"Error starting autonomous operations: {str(e)}")
        
        logger.info("Service initialization completed")
        
    except Exception as e:
        logger.error(f"Error initializing services: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

# Celery tasks (if Celery is available)
if celery_app:
    @celery_app.task
    def execute_daily_operations_task():
        """Background task for daily operations."""
        try:
            # Ensure services are initialized within Flask context
            ensure_services_initialized()
            
            if autonomous_manager:
                result = run_async_safe(autonomous_manager.execute_daily_operations(), timeout=300)
                return {"success": True, "result": result}
            return {"error": "Autonomous manager not available"}
        except Exception as e:
            logger.error(f"Daily operations task failed: {str(e)}")
            return {"error": str(e)}
    
    @celery_app.task
    def generate_weekly_report_task():
        """Background task for weekly report generation."""
        try:
            # Ensure services are initialized within Flask context
            ensure_services_initialized()
            
            if autonomous_manager:
                result = run_async_safe(autonomous_manager.generate_weekly_report(), timeout=600)
                return {"success": True, "result": result}
            return {"error": "Autonomous manager not available"}
        except Exception as e:
            logger.error(f"Weekly report task failed: {str(e)}")
            return {"error": str(e)}
    
    @celery_app.task
    def content_generation_batch_task(platforms, user_settings, count_per_platform, user_id, app_id):
        """Background task for batch content generation."""
        try:
            # Ensure services are initialized within Flask context
            ensure_services_initialized()
            
            if content_generator and firebase_service:
                generated_posts = content_generator.generate_content_batch(
                    platforms, user_settings, count_per_platform
                )
                
                # Save generated posts to Firebase
                saved_posts = []
                for post_data in generated_posts:
                    doc_id = firebase_service.save_generated_post(app_id, user_id, post_data)
                    if doc_id:
                        post_data['id'] = doc_id
                        saved_posts.append(post_data)
                
                return {"success": True, "posts": saved_posts, "count": len(saved_posts)}
            return {"error": "Required services not available"}
        except Exception as e:
            logger.error(f"Batch content generation task failed: {str(e)}")
            return {"error": str(e)}

@app.route("/")
def hello_world():
    """Basic health check endpoint with comprehensive service status."""
    return jsonify({
        "message": "AI Book Marketing Agent Backend is running!",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "autonomous_mode": Config.AUTONOMOUS_MODE,
        "task_queue": "celery" if celery_app else "thread_pool",
        "services": {
            "firebase": firebase_service is not None,
            "content_generator": content_generator is not None,
            "social_media": social_media_manager is not None,
            "google_analytics": google_analytics_service is not None,
            "google_ads": google_ads_service is not None,
            "autonomous_manager": autonomous_manager is not None,
            "budget_manager": budget_manager is not None,
            "scheduler": scheduler_service is not None
        }
    })

@app.route("/api/health")
def health_check():
    """
    Detailed health check for all services including autonomous operation status.
    """
    try:
        scheduler_status = {}
        if scheduler_service:
            # Use thread pool for non-blocking status check
            future = executor.submit(lambda: run_async_safe(scheduler_service.get_scheduler_status(), timeout=10))
            try:
                scheduler_status = future.result(timeout=15)
            except Exception as e:
                scheduler_status = {'error': str(e)}
        
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "firebase": firebase_service is not None,
                "content_generator": content_generator is not None,
                "social_media": social_media_manager is not None,
                "revenue_growth_manager": revenue_growth_manager is not None,
                "performance_analytics": performance_analytics is not None,
                "google_analytics": google_analytics_service is not None,
                "google_ads": google_ads_service is not None,
                "autonomous_manager": autonomous_manager is not None,
                "budget_manager": budget_manager is not None,
                "scheduler": scheduler_service is not None,
                "platform_status": social_media_manager.get_platform_status() if social_media_manager else {}
            },
            "config": {
                "openai_configured": bool(Config.OPENAI_API_KEY),
                "firebase_configured": bool(Config.FIREBASE_PROJECT_ID),
                "autonomous_mode": Config.AUTONOMOUS_MODE,
                "google_analytics_configured": bool(Config.GOOGLE_ANALYTICS_PROPERTY_ID),
                "google_ads_configured": bool(Config.GOOGLE_ADS_CUSTOMER_ID)
            },
            "autonomous_status": scheduler_status,
            "task_queue_status": {
                "type": "celery" if celery_app else "thread_pool",
                "active_tasks": len(background_tasks)
            }
        })
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

# ==================== AUTONOMOUS OPERATION ENDPOINTS ====================

@app.route("/api/autonomous/start", methods=["POST"])
@async_route(timeout=60)
def start_autonomous_operation():
    """Start autonomous marketing operation (non-blocking)."""
    try:
        if not autonomous_manager or not scheduler_service:
            return jsonify({"error": "Autonomous services not available"}), 500
        
        # Start autonomous operation in background
        result = run_async_safe(scheduler_service.start_autonomous_operation(), timeout=30)
        
        return jsonify({
            "status": "autonomous_operation_started",
            "timestamp": datetime.now().isoformat(),
            "result": result
        })
        
    except Exception as e:
        logger.error(f"Error starting autonomous operation: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/autonomous/stop", methods=["POST"])
@async_route(timeout=30)
def stop_autonomous_operation():
    """Stop autonomous marketing operation (non-blocking)."""
    try:
        if not scheduler_service:
            return jsonify({"error": "Scheduler service not available"}), 500
        
        # Stop autonomous operation
        result = run_async_safe(scheduler_service.stop_autonomous_operation(), timeout=20)
        
        return jsonify({
            "status": "autonomous_operation_stopped",
            "timestamp": datetime.now().isoformat(),
            "result": result
        })
        
    except Exception as e:
        logger.error(f"Error stopping autonomous operation: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/autonomous/status")
@async_route(timeout=15)
def get_autonomous_status():
    """Get current autonomous operation status (non-blocking)."""
    try:
        if not scheduler_service:
            return jsonify({"error": "Scheduler service not available"}), 500
        
        status = run_async_safe(scheduler_service.get_scheduler_status(), timeout=10)
        
        return jsonify({
            "autonomous_status": status,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting autonomous status: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/autonomous/execute-daily", methods=["POST"])
def execute_daily_operations():
    """Manually trigger daily autonomous operations (background task)."""
    try:
        if not autonomous_manager:
            return jsonify({"error": "Autonomous manager not available"}), 500
        
        # Use Celery task if available, otherwise thread pool
        if celery_app:
            task = execute_daily_operations_task.delay()
            with task_lock:
                background_tasks[task.id] = {
                    "type": "daily_operations",
                    "started_at": datetime.now().isoformat(),
                    "task_id": task.id
                }
            
            return jsonify({
                "status": "daily_operations_queued",
                "task_id": task.id,
                "timestamp": datetime.now().isoformat(),
                "message": "Daily operations started in background. Check task status for results."
            })
        else:
            # Fallback to thread pool
            def execute_operations():
                return run_async_safe(autonomous_manager.execute_daily_operations(), timeout=300)
            
            future = executor.submit(execute_operations)
            task_id = str(id(future))
            
            with task_lock:
                background_tasks[task_id] = {
                    "type": "daily_operations",
                    "started_at": datetime.now().isoformat(),
                    "future": future
                }
            
            return jsonify({
                "status": "daily_operations_queued",
                "task_id": task_id,
                "timestamp": datetime.now().isoformat(),
                "message": "Daily operations started in background. Check task status for results."
            })
        
    except Exception as e:
        logger.error(f"Error executing daily operations: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/task-status/<task_id>")
def get_task_status(task_id):
    """Get status of background task."""
    try:
        with task_lock:
            if task_id not in background_tasks:
                return jsonify({"error": "Task not found"}), 404
            
            task_info = background_tasks[task_id]
        
        if celery_app and "task_id" in task_info:
            # Celery task
            from celery.result import AsyncResult
            result = AsyncResult(task_info["task_id"], app=celery_app)
            
            return jsonify({
                "task_id": task_id,
                "status": result.status,
                "result": result.result if result.ready() else None,
                "started_at": task_info["started_at"]
            })
        else:
            # Thread pool task
            future = task_info.get("future")
            if future:
                if future.done():
                    try:
                        result = future.result()
                        return jsonify({
                            "task_id": task_id,
                            "status": "SUCCESS",
                            "result": result,
                            "started_at": task_info["started_at"]
                        })
                    except Exception as e:
                        return jsonify({
                            "task_id": task_id,
                            "status": "FAILURE",
                            "error": str(e),
                            "started_at": task_info["started_at"]
                        })
                else:
                    return jsonify({
                        "task_id": task_id,
                        "status": "PENDING",
                        "started_at": task_info["started_at"]
                    })
        
        return jsonify({"error": "Unable to determine task status"}), 500
        
    except Exception as e:
        logger.error(f"Error getting task status: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ==================== BUDGET MANAGEMENT ENDPOINTS ====================

@app.route("/api/budget/status")
def get_budget_status():
    """Get current budget status and utilization."""
    try:
        if not budget_manager:
            return jsonify({"error": "Budget manager not available"}), 500
        
        budget_status = budget_manager.get_current_budget_status()
        
        return jsonify({
            "budget_status": budget_status,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting budget status: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/budget/optimize", methods=["POST"])
def optimize_budget_allocation():
    """Optimize budget allocation based on performance."""
    try:
        if not budget_manager:
            return jsonify({"error": "Budget manager not available"}), 500
        
        # Get performance data from request or use default
        performance_data = request.get_json() or {}
        
        optimization_result = budget_manager.optimize_budget_allocation(performance_data)
        
        return jsonify({
            "budget_optimization": optimization_result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error optimizing budget allocation: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/budget/forecast")
def get_budget_forecast():
    """Get monthly budget performance forecast."""
    try:
        if not budget_manager:
            return jsonify({"error": "Budget manager not available"}), 500
        
        forecast = budget_manager.forecast_monthly_performance()
        
        return jsonify({
            "budget_forecast": forecast,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting budget forecast: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ==================== GOOGLE ANALYTICS ENDPOINTS ====================

@app.route("/api/analytics/marketing-metrics", methods=["POST"])
def get_marketing_metrics():
    """Get comprehensive marketing metrics from Google Analytics."""
    try:
        if not google_analytics_service:
            return jsonify({"error": "Google Analytics service not available"}), 500
        
        data = request.get_json()
        start_date = data.get('start_date', '30daysAgo')
        end_date = data.get('end_date', 'today')
        
        metrics = google_analytics_service.get_book_marketing_metrics(start_date, end_date)
        
        return jsonify({
            "marketing_metrics": metrics,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting marketing metrics: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/analytics/social-attribution")
def get_social_media_attribution():
    """Get social media attribution analysis."""
    try:
        if not google_analytics_service:
            return jsonify({"error": "Google Analytics service not available"}), 500
        
        days_back = request.args.get('days_back', 30, type=int)
        
        attribution = google_analytics_service.get_social_media_attribution(days_back)
        
        return jsonify({
            "social_attribution": attribution,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting social media attribution: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ==================== GOOGLE ADS ENDPOINTS ====================

@app.route("/api/ads/create-campaign", methods=["POST"])
def create_ads_campaign():
    """Create new Google Ads campaign for book marketing."""
    try:
        if not google_ads_service:
            return jsonify({"error": "Google Ads service not available"}), 500
        
        campaign_config = request.get_json()
        
        campaign_result = google_ads_service.create_book_marketing_campaign(campaign_config)
        
        return jsonify({
            "campaign_creation": campaign_result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error creating ads campaign: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/ads/optimize-campaign", methods=["POST"])
def optimize_ads_campaign():
    """Optimize existing Google Ads campaign."""
    try:
        if not google_ads_service:
            return jsonify({"error": "Google Ads service not available"}), 500
        
        data = request.get_json()
        campaign_id = data.get('campaign_id')
        
        if not campaign_id:
            return jsonify({"error": "campaign_id is required"}), 400
        
        optimization_result = google_ads_service.optimize_campaign_performance(campaign_id)
        
        return jsonify({
            "campaign_optimization": optimization_result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error optimizing ads campaign: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ==================== WEEKLY REPORTING ENDPOINTS ====================

@app.route("/api/reports/weekly", methods=["POST"])
def generate_weekly_report():
    """Generate comprehensive weekly performance report (background task)."""
    try:
        if not autonomous_manager:
            return jsonify({"error": "Autonomous manager not available"}), 500
        
        # Use Celery task if available, otherwise thread pool
        if celery_app:
            task = generate_weekly_report_task.delay()
            with task_lock:
                background_tasks[task.id] = {
                    "type": "weekly_report",
                    "started_at": datetime.now().isoformat(),
                    "task_id": task.id
                }
            
            return jsonify({
                "status": "weekly_report_queued",
                "task_id": task.id,
                "timestamp": datetime.now().isoformat(),
                "message": "Weekly report generation started in background. Check task status for results."
            })
        else:
            # Fallback to thread pool
            def generate_report():
                return run_async_safe(autonomous_manager.generate_weekly_report(), timeout=600)
            
            future = executor.submit(generate_report)
            task_id = str(id(future))
            
            with task_lock:
                background_tasks[task_id] = {
                    "type": "weekly_report",
                    "started_at": datetime.now().isoformat(),
                    "future": future
                }
            
            return jsonify({
                "status": "weekly_report_queued",
                "task_id": task_id,
                "timestamp": datetime.now().isoformat(),
                "message": "Weekly report generation started in background. Check task status for results."
            })
        
    except Exception as e:
        logger.error(f"Error generating weekly report: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ==================== ENHANCED CONTENT GENERATION ENDPOINTS ====================

@app.route("/api/generate-posts", methods=["POST"])
def generate_posts():
    """
    Generate new social media posts for the user.
    
    Enhanced with autonomous optimization and budget-aware posting.
    Supports both synchronous and asynchronous generation.
    """
    try:
        # Validate services are available
        if not content_generator:
            return jsonify({"error": "Content generator not initialized"}), 500
        
        if not firebase_service:
            return jsonify({"error": "Firebase service not initialized"}), 500
        
        # Parse request data
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        user_id = data.get("user_id")
        app_id = data.get("app_id", Config.DEFAULT_APP_ID)
        platforms = data.get("platforms", ["twitter", "facebook"])
        count_per_platform = data.get("count_per_platform", 1)
        async_generation = data.get("async", False)  # Option for async generation
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        # Get user settings from Firebase
        user_settings = firebase_service.get_user_settings(app_id, user_id)
        if not user_settings:
            return jsonify({"error": "User settings not found"}), 404
        
        # Check budget status before generation
        if Config.AUTONOMOUS_MODE and budget_manager:
            budget_status = budget_manager.get_current_budget_status()
            if budget_status.get('overall_utilization', 0) > 0.95:
                return jsonify({
                    "error": "Budget limit exceeded - content generation blocked",
                    "budget_status": budget_status
                }), 429
        
        # Determine if we should use async generation
        total_posts = len(platforms) * count_per_platform
        should_use_async = async_generation or total_posts > 5
        
        if should_use_async:
            # Use background task for large batches
            if celery_app:
                task = content_generation_batch_task.delay(
                    platforms, user_settings, count_per_platform, user_id, app_id
                )
                with task_lock:
                    background_tasks[task.id] = {
                        "type": "content_generation",
                        "started_at": datetime.now().isoformat(),
                        "task_id": task.id,
                        "user_id": user_id
                    }
                
                return jsonify({
                    "status": "content_generation_queued",
                    "task_id": task.id,
                    "timestamp": datetime.now().isoformat(),
                    "message": f"Generating {total_posts} posts in background. Check task status for results."
                })
            else:
                # Fallback to thread pool
                def generate_content():
                    generated_posts = content_generator.generate_content_batch(
                        platforms, user_settings, count_per_platform
                    )
                    
                    # Save generated posts to Firebase
                    saved_posts = []
                    for post_data in generated_posts:
                        doc_id = firebase_service.save_generated_post(app_id, user_id, post_data)
                        if doc_id:
                            post_data['id'] = doc_id
                            saved_posts.append(post_data)
                    
                    return {"posts": saved_posts, "count": len(saved_posts)}
                
                future = executor.submit(generate_content)
                task_id = str(id(future))
                
                with task_lock:
                    background_tasks[task_id] = {
                        "type": "content_generation",
                        "started_at": datetime.now().isoformat(),
                        "future": future,
                        "user_id": user_id
                    }
                
                return jsonify({
                    "status": "content_generation_queued",
                    "task_id": task_id,
                    "timestamp": datetime.now().isoformat(),
                    "message": f"Generating {total_posts} posts in background. Check task status for results."
                })
        else:
            # Synchronous generation for small batches
            generated_posts = content_generator.generate_content_batch(
                platforms, user_settings, count_per_platform
            )
            
            # Save generated posts to Firebase
            saved_posts = []
            for post_data in generated_posts:
                doc_id = firebase_service.save_generated_post(app_id, user_id, post_data)
                if doc_id:
                    post_data['id'] = doc_id
                    saved_posts.append(post_data)
            
            logger.info(f"Generated and saved {len(saved_posts)} posts for user {user_id}")
            
            return jsonify({
                "posts_generated": len(saved_posts),
                "posts": saved_posts,
                "timestamp": datetime.now().isoformat(),
                "autonomous_mode": Config.AUTONOMOUS_MODE,
                "budget_status": budget_manager.get_current_budget_status() if budget_manager else None
            })
        
    except Exception as e:
        logger.error(f"Error generating posts: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/approve-post", methods=["POST"])
@async_route(timeout=30)
def approve_and_schedule_post():
    """
    Approve and schedule a post for publishing.
    Enhanced with budget awareness and autonomous optimization.
    """
    try:
        if not social_media_manager:
            return jsonify({"error": "Social media manager not initialized"}), 500
        
        if not firebase_service:
            return jsonify({"error": "Firebase service not initialized"}), 500
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        post_id = data.get("post_id")
        user_id = data.get("user_id")
        app_id = data.get("app_id", Config.DEFAULT_APP_ID)
        scheduled_time = data.get("scheduled_time")
        
        if not all([post_id, user_id]):
            return jsonify({"error": "post_id and user_id are required"}), 400
        
        # Check budget status before approving
        if budget_manager:
            budget_status = budget_manager.get_current_budget_status()
            if budget_status.get('overall_utilization', 0) > 0.95:
                return jsonify({
                    "error": "Budget limit exceeded - post approval blocked",
                    "budget_status": budget_status
                }), 429
        
        # Get post data
        post_data = firebase_service.get_generated_post(app_id, user_id, post_id)
        if not post_data:
            return jsonify({"error": "Post not found"}), 404
        
        # Update post status
        post_data['status'] = 'approved'
        post_data['approved_at'] = datetime.now().isoformat()
        post_data['scheduled_time'] = scheduled_time
        
        # Schedule the post (using run_async_safe for any async operations)
        if hasattr(social_media_manager, 'schedule_post_async'):
            scheduling_result = run_async_safe(
                social_media_manager.schedule_post_async(
                    post_data['platform'],
                    post_data['content'],
                    scheduled_time
                ),
                timeout=20
            )
        else:
            scheduling_result = social_media_manager.schedule_post(
                post_data['platform'],
                post_data['content'],
                scheduled_time
            )
        
        # Update post in Firebase
        firebase_service.update_generated_post(app_id, user_id, post_id, post_data)
        
        # Log approval for autonomous learning
        if autonomous_manager:
            try:
                # This would feed into the learning system
                # Could be implemented as a background task
                pass
            except Exception as e:
                logger.warning(f"Error logging approval for learning: {str(e)}")
        
        return jsonify({
            "status": "approved_and_scheduled",
            "post_id": post_id,
            "scheduling_result": scheduling_result,
            "scheduled_time": scheduled_time,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error approving and scheduling post: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/reject-post", methods=["POST"])
def reject_post():
    """
    Reject a pending post.
    
    Expected JSON payload:
    {
        "user_id": "user123",
        "app_id": "app123",
        "post_id": "post123",
        "reason": "Content needs revision"
    }
    """
    try:
        if not firebase_service:
            return jsonify({"error": "Firebase service not initialized"}), 500
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        user_id = data.get("user_id")
        app_id = data.get("app_id", Config.DEFAULT_APP_ID)
        post_id = data.get("post_id")
        reason = data.get("reason", "Rejected by user")
        
        if not user_id or not post_id:
            return jsonify({"error": "user_id and post_id are required"}), 400
        
        # Update post status to rejected
        update_data = {"rejection_reason": reason}
        success = firebase_service.update_post_status(
            app_id, user_id, post_id, "rejected", update_data
        )
        
        if success:
            logger.info(f"Post {post_id} rejected by user {user_id}")
            return jsonify({
                "success": True,
                "message": "Post rejected successfully",
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({"error": "Failed to update post status"}), 500
        
    except Exception as e:
        logger.error(f"Error rejecting post: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/pending-posts/<user_id>")
def get_pending_posts(user_id):
    """
    Get all pending posts for a user.
    """
    try:
        if not firebase_service:
            return jsonify({"error": "Firebase service not initialized"}), 500
        
        app_id = request.args.get("app_id", Config.DEFAULT_APP_ID)
        
        pending_posts = firebase_service.get_pending_posts(app_id, user_id)
        
        return jsonify({
            "success": True,
            "posts": pending_posts,
            "count": len(pending_posts),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error retrieving pending posts: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/platform-status")
def get_platform_status():
    """
    Get the status of all social media platforms.
    """
    try:
        if not social_media_manager:
            return jsonify({"error": "Social media manager not initialized"}), 500
        
        status = social_media_manager.get_platform_status()
        
        return jsonify({
            "success": True,
            "platform_status": status,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting platform status: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/test-platform/<platform>")
def test_platform(platform):
    """
    Test connection to a specific social media platform.
    """
    try:
        if not social_media_manager:
            return jsonify({"error": "Social media manager not initialized"}), 500
        
        test_result = social_media_manager.test_platform_connection(platform)
        
        return jsonify({
            "platform": platform,
            "test_result": test_result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error testing platform {platform}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/revenue-analysis", methods=["POST"])
def analyze_revenue_performance():
    """
    Comprehensive revenue performance analysis with growth optimization recommendations.
    
    Expected JSON payload:
    {
        "user_id": "user123",
        "app_id": "app123"
    }
    """
    try:
        # Validate services are available
        if not revenue_growth_manager:
            return jsonify({"error": "Revenue Growth Manager not initialized"}), 500
        
        # Parse request data
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        user_id = data.get("user_id")
        app_id = data.get("app_id", Config.DEFAULT_APP_ID)
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        # Perform comprehensive revenue analysis
        analysis_result = revenue_growth_manager.analyze_revenue_performance(app_id, user_id)
        
        if 'error' in analysis_result:
            return jsonify(analysis_result), 500
        
        logger.info(f"Revenue analysis completed for user {user_id}")
        
        return jsonify({
            "success": True,
            "analysis": analysis_result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in revenue analysis: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/optimize-pricing", methods=["POST"])
def optimize_pricing_strategy():
    """
    Optimize pricing strategy for maximum revenue growth.
    
    Expected JSON payload:
    {
        "user_id": "user123",
        "app_id": "app123",
        "current_metrics": {
            "monthly_sales": 5000.0,
            "growth_rate": 0.12,
            "conversion_rate": 0.025,
            "average_order_value": 24.99
        },
        "market_data": {}
    }
    """
    try:
        if not revenue_growth_manager:
            return jsonify({"error": "Revenue Growth Manager not initialized"}), 500
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        user_id = data.get("user_id")
        app_id = data.get("app_id", Config.DEFAULT_APP_ID)
        current_metrics_data = data.get("current_metrics", {})
        market_data = data.get("market_data", {})
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        # Create RevenueMetrics object
        from app.services.revenue_growth_manager import RevenueMetrics
        current_metrics = RevenueMetrics(
            monthly_sales=current_metrics_data.get("monthly_sales", 0.0),
            growth_rate=current_metrics_data.get("growth_rate", 0.0),
            customer_acquisition_cost=current_metrics_data.get("customer_acquisition_cost", 0.0),
            customer_lifetime_value=current_metrics_data.get("customer_lifetime_value", 0.0),
            churn_rate=current_metrics_data.get("churn_rate", 0.0),
            conversion_rate=current_metrics_data.get("conversion_rate", 0.0),
            average_order_value=current_metrics_data.get("average_order_value", 0.0)
        )
        
        # Optimize pricing strategy
        optimization_result = revenue_growth_manager.optimize_pricing_strategy(current_metrics, market_data)
        
        if 'error' in optimization_result:
            return jsonify(optimization_result), 500
        
        logger.info(f"Pricing optimization completed for user {user_id}")
        
        return jsonify({
            "success": True,
            "optimization": optimization_result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in pricing optimization: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/churn-prevention", methods=["POST"])
def predict_and_prevent_churn():
    """
    Predict customer churn risk and implement prevention strategies.
    
    Expected JSON payload:
    {
        "user_id": "user123",
        "app_id": "app123"
    }
    """
    try:
        if not revenue_growth_manager:
            return jsonify({"error": "Revenue Growth Manager not initialized"}), 500
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        user_id = data.get("user_id")
        app_id = data.get("app_id", Config.DEFAULT_APP_ID)
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        # Predict and prevent churn
        churn_result = revenue_growth_manager.predict_and_prevent_churn(app_id, user_id)
        
        if 'error' in churn_result:
            return jsonify(churn_result), 500
        
        logger.info(f"Churn prevention analysis completed for user {user_id}")
        
        return jsonify({
            "success": True,
            "churn_prevention": churn_result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in churn prevention: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/performance-analysis", methods=["POST"])
def analyze_content_performance():
    """
    Comprehensive content performance analysis with optimization recommendations.
    
    Expected JSON payload:
    {
        "user_id": "user123",
        "app_id": "app123",
        "time_range_days": 30
    }
    """
    try:
        if not performance_analytics:
            return jsonify({"error": "Performance Analytics not initialized"}), 500
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        user_id = data.get("user_id")
        app_id = data.get("app_id", Config.DEFAULT_APP_ID)
        time_range_days = data.get("time_range_days", 30)
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        # Analyze content performance
        performance_result = performance_analytics.analyze_content_performance(app_id, user_id, time_range_days)
        
        if 'error' in performance_result:
            return jsonify(performance_result), 500
        
        logger.info(f"Performance analysis completed for user {user_id}")
        
        return jsonify({
            "success": True,
            "performance_analysis": performance_result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in performance analysis: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/ab-test", methods=["POST"])
def run_ab_test():
    """
    Set up and run A/B test for content optimization.
    
    Expected JSON payload:
    {
        "user_id": "user123",
        "app_id": "app123",
        "test_config": {
            "content_base": "Mental toughness tips for young athletes",
            "test_dimension": "tone",
            "target_metric": "engagement_rate",
            "platforms": ["instagram", "facebook"]
        }
    }
    """
    try:
        if not performance_analytics:
            return jsonify({"error": "Performance Analytics not initialized"}), 500
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        user_id = data.get("user_id")
        app_id = data.get("app_id", Config.DEFAULT_APP_ID)
        test_config = data.get("test_config", {})
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        # Run A/B test
        test_result = performance_analytics.run_ab_test(app_id, user_id, test_config)
        
        if 'error' in test_result:
            return jsonify(test_result), 500
        
        logger.info(f"A/B test setup completed for user {user_id}")
        
        return jsonify({
            "success": True,
            "ab_test": test_result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error setting up A/B test: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/predict-performance", methods=["POST"])
def predict_content_performance():
    """
    Predict content performance before publishing.
    
    Expected JSON payload:
    {
        "user_id": "user123",
        "app_id": "app123",
        "content_data": {
            "content": "Mental toughness is a game changer for young athletes!",
            "content_type": "text",
            "scheduled_time": "2024-01-15T10:00:00Z"
        },
        "platform": "instagram"
    }
    """
    try:
        if not performance_analytics:
            return jsonify({"error": "Performance Analytics not initialized"}), 500
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        user_id = data.get("user_id")
        app_id = data.get("app_id", Config.DEFAULT_APP_ID)
        content_data = data.get("content_data", {})
        platform = data.get("platform", "instagram")
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        if not content_data.get("content"):
            return jsonify({"error": "content is required"}), 400
        
        # Predict content performance
        prediction_result = performance_analytics.predict_content_performance(
            content_data, platform, user_id, app_id
        )
        
        if 'error' in prediction_result:
            return jsonify(prediction_result), 500
        
        logger.info(f"Content performance prediction completed for {platform}")
        
        return jsonify({
            "success": True,
            "prediction": prediction_result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error predicting content performance: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/performance-report", methods=["POST"])
def generate_performance_report():
    """
    Generate comprehensive performance report.
    
    Expected JSON payload:
    {
        "user_id": "user123",
        "app_id": "app123",
        "report_period": "monthly"
    }
    """
    try:
        if not performance_analytics:
            return jsonify({"error": "Performance Analytics not initialized"}), 500
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        user_id = data.get("user_id")
        app_id = data.get("app_id", Config.DEFAULT_APP_ID)
        report_period = data.get("report_period", "monthly")
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        # Generate performance report
        report_result = performance_analytics.generate_performance_report(app_id, user_id, report_period)
        
        if 'error' in report_result:
            return jsonify(report_result), 500
        
        logger.info(f"Performance report generated for user {user_id}")
        
        return jsonify({
            "success": True,
            "report": report_result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error generating performance report: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ==================== TASK MANAGEMENT ENDPOINTS ====================

@app.route("/api/tasks/active")
def get_active_tasks():
    """Get list of all active background tasks."""
    try:
        active_tasks_list = []
        
        # Get Celery tasks if available
        if celery_app:
            from app.services.task_queue import get_active_tasks
            celery_tasks = get_active_tasks(celery_app)
            for task in celery_tasks:
                active_tasks_list.append({
                    "task_id": task.get("id"),
                    "name": task.get("name"),
                    "worker": task.get("worker"),
                    "args": task.get("args", []),
                    "kwargs": task.get("kwargs", {}),
                    "type": "celery"
                })
        
        # Get thread pool tasks
        with task_lock:
            for task_id, task_info in background_tasks.items():
                if "future" in task_info:
                    future = task_info["future"]
                    if not future.done():
                        active_tasks_list.append({
                            "task_id": task_id,
                            "type": "thread_pool",
                            "name": task_info.get("type", "unknown"),
                            "started_at": task_info.get("started_at"),
                            "user_id": task_info.get("user_id")
                        })
        
        return jsonify({
            "active_tasks": active_tasks_list,
            "count": len(active_tasks_list),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting active tasks: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/tasks/revoke/<task_id>", methods=["POST"])
def revoke_task(task_id):
    """Revoke/cancel a background task."""
    try:
        data = request.get_json() or {}
        terminate = data.get("terminate", False)
        
        revoke_result = {"task_id": task_id, "revoked": False}
        
        # Try to revoke Celery task first
        if celery_app:
            with task_lock:
                if task_id in background_tasks and "task_id" in background_tasks[task_id]:
                    from app.services.task_queue import revoke_task as revoke_celery_task
                    result = revoke_celery_task(task_id, celery_app, terminate)
                    revoke_result.update(result)
                    revoke_result["revoked"] = True
                    
                    # Remove from our tracking
                    del background_tasks[task_id]
        
        # Try to cancel thread pool task
        with task_lock:
            if task_id in background_tasks and "future" in background_tasks[task_id]:
                future = background_tasks[task_id]["future"]
                cancelled = future.cancel()
                revoke_result.update({
                    "revoked": cancelled,
                    "type": "thread_pool",
                    "cancelled": cancelled
                })
                
                # Remove from our tracking
                if cancelled:
                    del background_tasks[task_id]
        
        if not revoke_result["revoked"]:
            return jsonify({"error": "Task not found or could not be revoked"}), 404
        
        return jsonify({
            "result": revoke_result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error revoking task: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/tasks/stats")
def get_task_queue_stats():
    """Get comprehensive task queue statistics."""
    try:
        stats = {
            "timestamp": datetime.now().isoformat(),
            "thread_pool": {
                "max_workers": executor._max_workers,
                "active_tasks": len([t for t in background_tasks.values() if "future" in t and not t["future"].done()]),
                "total_tracked": len(background_tasks)
            }
        }
        
        # Add Celery stats if available
        if celery_app:
            from app.services.task_queue import get_worker_stats
            celery_stats = get_worker_stats(celery_app)
            stats["celery"] = celery_stats
        else:
            stats["celery"] = {"available": False}
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error getting task queue stats: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Production 404 error handler."""
    logger.warning(f"404 error: {request.url}")
    return jsonify({"error": "Endpoint not found", "status": 404}), 404

@app.errorhandler(500)  
def internal_error(error):
    """Production 500 error handler."""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({"error": "Internal server error", "status": 500}), 500

@app.errorhandler(408)
def timeout_error(error):
    """Production timeout error handler."""
    logger.error(f"Request timeout: {str(error)}")
    return jsonify({"error": "Request timeout", "status": 408}), 408

# Cleanup functions for graceful shutdown
def cleanup_resources():
    """
    Clean up resources on shutdown for production deployment.
    Ensures graceful shutdown of all services and connections.
    """
    logger.info("Starting production resource cleanup...")
    
    try:
        # Shutdown thread pool executor
        if executor:
            executor.shutdown(wait=True, timeout=30)
            logger.info("Thread pool executor shutdown completed")
    except Exception as e:
        logger.warning(f"Error shutting down executor: {str(e)}")

    try:
        # Cancel background tasks
        with task_lock:
            for task_id, task_info in background_tasks.items():
                if 'future' in task_info and not task_info['future'].done():
                    task_info['future'].cancel()
                    logger.info(f"Cancelled background task: {task_id}")
            background_tasks.clear()
    except Exception as e:
        logger.warning(f"Error cancelling background tasks: {str(e)}")

    try:
        # Shutdown Celery if available
        if celery_app:
            celery_app.control.shutdown()
            logger.info("Celery shutdown initiated")
    except Exception as e:
        logger.warning(f"Error shutting down Celery: {str(e)}")

    try:
        # Close Firebase connections
        if firebase_service and hasattr(firebase_service, 'db'):
            firebase_service.db._client.close()
            logger.info("Firebase connections closed")
    except Exception as e:
        logger.warning(f"Error closing Firebase connections: {str(e)}")

    logger.info("Production resource cleanup completed")

def signal_handler(signum, frame):
    """
    Production signal handler for graceful shutdown.
    Handles SIGTERM and SIGINT for proper production deployment.
    """
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    cleanup_resources()
    sys.exit(0)

# Register signal handlers for production
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)
atexit.register(cleanup_resources)

# Production startup information
logger.info("=" * 60)
logger.info("AI BOOK MARKETING AGENT - PRODUCTION MODE")
logger.info("=" * 60)
logger.info(f"Production mode: {Config.is_production()}")
logger.info(f"Debug mode: {Config.DEBUG}")
logger.info(f"Autonomous mode: {Config.AUTONOMOUS_MODE}")
logger.info(f"Enabled platforms: {Config.get_enabled_platforms()}")
logger.info(f"Server host: {Config.HOST}")
logger.info(f"Server port: {Config.PORT}")
logger.info("=" * 60)

# Production server startup
if __name__ == "__main__":
    try:
        # Initialize services before starting server
        ensure_services_initialized()
        
        # Register all production route blueprints
        register_routes(app)
        logger.info("All production routes registered successfully")
        
        # Start production server
        logger.info("Starting production server...")
        app.run(
            host=Config.HOST,
            port=Config.PORT,
            debug=Config.DEBUG,
            threaded=True,  # Enable threading for production
            use_reloader=False  # Disable reloader in production
        )
    except KeyboardInterrupt:
        logger.info("Server shutdown requested by user")
    except Exception as e:
        logger.error(f"Production server startup failed: {str(e)}")
        sys.exit(1)
    finally:
        cleanup_resources()

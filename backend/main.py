from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os
import asyncio
from datetime import datetime

# Import our custom services
from config.settings import Config
from app.firebase_service import FirebaseService
from app.content_generator import ContentGenerator
from app.social_media_manager import SocialMediaManager
from app.revenue_growth_manager import RevenueGrowthManager
from app.performance_analytics import PerformanceAnalytics
from app.google_analytics_service import GoogleAnalyticsService
from app.google_ads_service import GoogleAdsService
from app.autonomous_manager import AutonomousMarketingManager
from app.budget_manager import BudgetManager
from app.scheduler_service import SchedulerService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS for frontend communication
CORS(app, origins=["http://localhost:3000", "https://your-frontend-domain.com"])

# Global service instances (initialized on startup)
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

def initialize_services():
    """
    Initialize all backend services with proper error handling and integration.
    """
    global firebase_service, content_generator, social_media_manager
    global revenue_growth_manager, performance_analytics, google_analytics_service
    global google_ads_service, autonomous_manager, budget_manager, scheduler_service
    
    try:
        # Validate configuration
        missing_configs = Config.validate_config()
        if missing_configs:
            logger.warning(f"Missing configuration: {', '.join(missing_configs)}")
        
        # Initialize Firebase service
        if Config.FIREBASE_PROJECT_ID and os.path.exists(Config.FIREBASE_CREDENTIALS_PATH):
            firebase_service = FirebaseService(
                Config.FIREBASE_CREDENTIALS_PATH,
                Config.FIREBASE_PROJECT_ID
            )
            logger.info("Firebase service initialized successfully")
        else:
            logger.error("Firebase configuration missing or credentials file not found")
        
        # Initialize Content Generator
        if Config.OPENAI_API_KEY:
            content_generator = ContentGenerator(
                Config.OPENAI_API_KEY,
                Config.OPENAI_MODEL
            )
            logger.info("Content generator initialized successfully")
        else:
            logger.error("OpenAI API key not configured")
        
        # Initialize Social Media Manager
        social_config = Config.get_social_media_config()
        social_media_manager = SocialMediaManager(social_config)
        logger.info("Social media manager initialized successfully")
        
        # Initialize Google Analytics Service
        google_services_config = Config.get_google_services_config()
        if (google_services_config['analytics']['property_id'] and 
            google_services_config['analytics']['credentials_path']):
            google_analytics_service = GoogleAnalyticsService(
                google_services_config['analytics']['credentials_path'],
                google_services_config['analytics']['property_id']
            )
            logger.info("Google Analytics service initialized successfully")
        else:
            logger.warning("Google Analytics not configured - limited autonomous functionality")
        
        # Initialize Google Ads Service
        if (google_services_config['ads']['customer_id'] and 
            google_services_config['ads']['developer_token'] and
            google_services_config['ads']['credentials_path']):
            google_ads_service = GoogleAdsService(
                google_services_config['ads']['customer_id'],
                google_services_config['ads']['developer_token'],
                google_services_config['ads']['credentials_path']
            )
            logger.info("Google Ads service initialized successfully")
        else:
            logger.warning("Google Ads not configured - limited autonomous functionality")
        
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
                firebase_service
            )
            logger.info("Performance Analytics initialized successfully")
        
        # Initialize Revenue Growth Manager
        if Config.OPENAI_API_KEY and firebase_service:
            revenue_growth_manager = RevenueGrowthManager(
                Config.OPENAI_API_KEY,
                firebase_service,
                google_analytics_service
            )
            logger.info("Revenue Growth Manager initialized successfully")
        
        # Initialize Autonomous Marketing Manager
        if (Config.OPENAI_API_KEY and firebase_service and content_generator and 
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
            logger.error("Cannot initialize Autonomous Manager - missing dependencies")
        
        # Initialize Scheduler Service
        if autonomous_manager and Config.AUTONOMOUS_MODE:
            scheduler_service = SchedulerService(
                autonomous_manager,
                firebase_service,
                Config
            )
            logger.info("Scheduler Service initialized successfully")
            
            # Start autonomous operations if enabled
            try:
                asyncio.create_task(scheduler_service.start_autonomous_operation())
                logger.info("Autonomous operations started")
            except Exception as e:
                logger.error(f"Error starting autonomous operations: {str(e)}")
        
    except Exception as e:
        logger.error(f"Error initializing services: {str(e)}")

@app.route("/")
def hello_world():
    """
    Basic health check endpoint with comprehensive service status.
    """
    return jsonify({
        "message": "AI Book Marketing Agent Backend is running!",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "autonomous_mode": Config.AUTONOMOUS_MODE,
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
    scheduler_status = {}
    if scheduler_service:
        try:
            scheduler_status = asyncio.run(scheduler_service.get_scheduler_status())
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
        "autonomous_status": scheduler_status
    })

# ==================== AUTONOMOUS OPERATION ENDPOINTS ====================

@app.route("/api/autonomous/start", methods=["POST"])
def start_autonomous_operation():
    """Start autonomous marketing operation."""
    try:
        if not autonomous_manager or not scheduler_service:
            return jsonify({"error": "Autonomous services not available"}), 500
        
        # Start autonomous operation
        result = asyncio.run(scheduler_service.start_autonomous_operation())
        
        return jsonify({
            "status": "autonomous_operation_started",
            "timestamp": datetime.now().isoformat(),
            "result": result
        })
        
    except Exception as e:
        logger.error(f"Error starting autonomous operation: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/autonomous/stop", methods=["POST"])
def stop_autonomous_operation():
    """Stop autonomous marketing operation."""
    try:
        if not scheduler_service:
            return jsonify({"error": "Scheduler service not available"}), 500
        
        # Stop autonomous operation
        result = asyncio.run(scheduler_service.stop_autonomous_operation())
        
        return jsonify({
            "status": "autonomous_operation_stopped",
            "timestamp": datetime.now().isoformat(),
            "result": result
        })
        
    except Exception as e:
        logger.error(f"Error stopping autonomous operation: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/autonomous/status")
def get_autonomous_status():
    """Get current autonomous operation status."""
    try:
        if not scheduler_service:
            return jsonify({"error": "Scheduler service not available"}), 500
        
        status = asyncio.run(scheduler_service.get_scheduler_status())
        
        return jsonify({
            "autonomous_status": status,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting autonomous status: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/autonomous/execute-daily", methods=["POST"])
def execute_daily_operations():
    """Manually trigger daily autonomous operations."""
    try:
        if not autonomous_manager:
            return jsonify({"error": "Autonomous manager not available"}), 500
        
        result = asyncio.run(autonomous_manager.execute_daily_operations())
        
        return jsonify({
            "daily_operations": result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error executing daily operations: {str(e)}")
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
    """Generate comprehensive weekly performance report."""
    try:
        if not autonomous_manager:
            return jsonify({"error": "Autonomous manager not available"}), 500
        
        weekly_report = asyncio.run(autonomous_manager.generate_weekly_report())
        
        return jsonify({
            "weekly_report": weekly_report,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error generating weekly report: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ==================== EXISTING ENDPOINTS (Updated) ====================

@app.route("/api/generate-posts", methods=["POST"])
def generate_posts():
    """
    Generate new social media posts for the user.
    
    Enhanced with autonomous optimization and budget-aware posting.
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
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        # Get user settings from Firebase
        user_settings = firebase_service.get_user_settings(app_id, user_id)
        if not user_settings:
            return jsonify({"error": "User settings not found"}), 404
        
        # Generate posts with autonomous optimization
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
        
        # If autonomous mode is enabled, automatically optimize based on budget
        if Config.AUTONOMOUS_MODE and budget_manager:
            budget_status = budget_manager.get_current_budget_status()
            if budget_status.get('overall_utilization', 0) > 0.8:
                logger.warning("High budget utilization detected - optimizing post schedule")
        
        return jsonify({
            "posts_generated": len(saved_posts),
            "posts": saved_posts,
            "timestamp": datetime.now().isoformat(),
            "autonomous_mode": Config.AUTONOMOUS_MODE
        })
        
    except Exception as e:
        logger.error(f"Error generating posts: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/approve-post", methods=["POST"])
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
        
        # Schedule the post
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
        from app.revenue_growth_manager import RevenueMetrics
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
        
        content_data = data.get("content_data", {})
        platform = data.get("platform", "instagram")
        
        if not content_data.get("content"):
            return jsonify({"error": "content is required"}), 400
        
        # Predict content performance
        prediction_result = performance_analytics.predict_content_performance(content_data, platform)
        
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

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

# Initialize services when the app starts
with app.app_context():
    initialize_services()

if __name__ == '__main__':
    # Print startup information
    print("=" * 50)
    print("AI Book Marketing Agent Backend")
    print("=" * 50)
    print(f"OpenAI API configured: {bool(Config.OPENAI_API_KEY)}")
    print(f"Firebase configured: {bool(Config.FIREBASE_PROJECT_ID)}")
    print(f"Debug mode: {Config.DEBUG}")
    print("=" * 50)
    
    # Get port from environment (for deployment) or default to 5000 (for local dev)
    port = int(os.environ.get('PORT', 5000))
    
    # Run the Flask app
    app.run(
        debug=Config.DEBUG,
        host='0.0.0.0',
        port=port
    )

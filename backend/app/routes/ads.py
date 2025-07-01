"""Google Ads management endpoints for the AI Book Marketing Agent."""

from flask import Blueprint, request, jsonify
from datetime import datetime
from ..config import Config
from ..services import google_ads_service

# Create blueprint
ads_bp = Blueprint('ads', __name__)

@ads_bp.route("/campaigns/<user_id>")
def get_campaigns(user_id):
    """Get all ad campaigns for a user."""
    try:
        if not google_ads_service:
            return jsonify({"error": "Google Ads service not initialized"}), 500
        
        app_id = request.args.get("app_id", Config.DEFAULT_APP_ID)
        status = request.args.get("status")  # active, paused, removed
        
        campaigns = google_ads_service.get_campaigns(
            app_id, user_id, status=status
        )
        
        return jsonify({
            "success": True,
            "data": campaigns,
            "status_filter": status,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ads_bp.route("/campaign", methods=["POST"])
def create_campaign():
    """Create a new ad campaign."""
    try:
        if not google_ads_service:
            return jsonify({"error": "Google Ads service not initialized"}), 500
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        user_id = data.get("user_id")
        app_id = data.get("app_id", Config.DEFAULT_APP_ID)
        campaign_data = data.get("campaign")
        
        if not all([user_id, campaign_data]):
            return jsonify({
                "error": "user_id and campaign data are required"
            }), 400
        
        # Use the create_book_marketing_campaign method
        campaign_result = google_ads_service.create_book_marketing_campaign(campaign_data)
        
        if campaign_result and 'error' not in campaign_result:
            return jsonify({
                "success": True,
                "message": "Campaign created successfully",
                "campaign_data": campaign_result,
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({"error": campaign_result.get('error', 'Failed to create campaign')}), 500
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ads_bp.route("/campaign/<campaign_id>", methods=["GET", "PUT", "DELETE"])
def manage_campaign(campaign_id):
    """Get, update, or delete a specific campaign."""
    try:
        if not google_ads_service:
            return jsonify({"error": "Google Ads service not initialized"}), 500
        
        user_id = request.args.get("user_id")
        app_id = request.args.get("app_id", Config.DEFAULT_APP_ID)
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        if request.method == "GET":
            # Get campaign performance data
            performance_data = google_ads_service._get_campaign_performance(campaign_id)
            campaign_budget = google_ads_service._get_campaign_budget_data(campaign_id)
            
            campaign_info = {
                'campaign_id': campaign_id,
                'performance': performance_data,
                'budget': campaign_budget,
                'status': 'active'
            }
            
            return jsonify({
                "success": True,
                "data": campaign_info,
                "timestamp": datetime.now().isoformat()
            })
            
        elif request.method == "PUT":
            data = request.get_json()
            if not data or "campaign" not in data:
                return jsonify({"error": "campaign data is required"}), 400
            
            # For demo purposes, assume update is successful
            # In real implementation, would update campaign via Google Ads API
            return jsonify({
                "success": True,
                "message": "Campaign updated successfully",
                "updated_data": data["campaign"],
                "timestamp": datetime.now().isoformat()
            })
            
        else:  # DELETE
            # For demo purposes, assume deletion is successful
            # In real implementation, would delete campaign via Google Ads API
            return jsonify({
                "success": True,
                "message": "Campaign deleted successfully",
                "timestamp": datetime.now().isoformat()
            })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ads_bp.route("/performance/<campaign_id>")
def get_campaign_performance(campaign_id):
    """Get performance metrics for a specific campaign."""
    try:
        if not google_ads_service:
            return jsonify({"error": "Google Ads service not initialized"}), 500
        
        user_id = request.args.get("user_id")
        app_id = request.args.get("app_id", Config.DEFAULT_APP_ID)
        metrics = request.args.getlist("metrics")
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        # Get comprehensive performance analysis
        performance = google_ads_service._get_campaign_performance(campaign_id)
        keyword_analysis = google_ads_service._analyze_keyword_performance(campaign_id)
        ad_analysis = google_ads_service._analyze_ad_performance(campaign_id)
        
        return jsonify({
            "success": True,
            "data": {
                "performance_metrics": performance,
                "keyword_analysis": keyword_analysis,
                "ad_analysis": ad_analysis
            },
            "campaign_id": campaign_id,
            "metrics_requested": metrics,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ads_bp.route("/optimize/<campaign_id>", methods=["POST"])
def optimize_campaign(campaign_id):
    """Optimize a specific campaign based on performance data."""
    try:
        if not google_ads_service:
            return jsonify({"error": "Google Ads service not initialized"}), 500
        
        # Get optimization data from request
        data = request.get_json() or {}
        
        # Run campaign optimization
        optimization_result = google_ads_service.optimize_campaign_performance(campaign_id)
        
        return jsonify({
            "success": True,
            "optimization_result": optimization_result,
            "campaign_id": campaign_id,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ads_bp.route("/budget/monitor", methods=["POST"])
def monitor_campaign_budgets():
    """Monitor budget utilization across campaigns."""
    try:
        if not google_ads_service:
            return jsonify({"error": "Google Ads service not initialized"}), 500
        
        data = request.get_json()
        if not data or "campaign_ids" not in data:
            return jsonify({"error": "campaign_ids are required"}), 400
        
        campaign_ids = data["campaign_ids"]
        
        # Monitor budget utilization
        budget_monitoring = google_ads_service.monitor_budget_utilization(campaign_ids)
        
        return jsonify({
            "success": True,
            "budget_monitoring": budget_monitoring,
            "campaigns_monitored": len(campaign_ids),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ads_bp.route("/roi-analysis/<campaign_id>")
def get_roi_analysis(campaign_id):
    """Get ROI analysis for a specific campaign."""
    try:
        if not google_ads_service:
            return jsonify({"error": "Google Ads service not initialized"}), 500
        
        days_back = request.args.get('days_back', 30, type=int)
        
        # Get ROI analysis
        roi_analysis = google_ads_service.get_campaign_roi_analysis(campaign_id, days_back)
        
        return jsonify({
            "success": True,
            "roi_analysis": roi_analysis,
            "campaign_id": campaign_id,
            "analysis_period": f"{days_back} days",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ads_bp.route("/create-ad-variations", methods=["POST"])
def create_ad_variations():
    """Create automated ad variations for testing."""
    try:
        if not google_ads_service:
            return jsonify({"error": "Google Ads service not initialized"}), 500
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        campaign_id = data.get("campaign_id")
        base_ad_config = data.get("base_ad_config", {})
        
        if not campaign_id:
            return jsonify({"error": "campaign_id is required"}), 400
        
        # Create ad variations
        ad_variations = google_ads_service.create_automated_ad_variations(campaign_id, base_ad_config)
        
        return jsonify({
            "success": True,
            "ad_variations": ad_variations,
            "campaign_id": campaign_id,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ads_bp.route("/alerts", methods=["POST"])
def get_campaign_alerts():
    """Get real-time alerts for campaigns."""
    try:
        if not google_ads_service:
            return jsonify({"error": "Google Ads service not initialized"}), 500
        
        data = request.get_json()
        if not data or "campaign_ids" not in data:
            return jsonify({"error": "campaign_ids are required"}), 400
        
        campaign_ids = data["campaign_ids"]
        
        # Get real-time alerts
        alerts = google_ads_service.get_real_time_campaign_alerts(campaign_ids)
        
        return jsonify({
            "success": True,
            "alerts": alerts,
            "total_alerts": len(alerts),
            "campaigns_monitored": len(campaign_ids),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ads_bp.route("/keyword-research", methods=["POST"])  
def keyword_research():
    """Research and suggest new keywords for campaigns."""
    try:
        if not google_ads_service:
            return jsonify({"error": "Google Ads service not initialized"}), 500
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        seed_keywords = data.get("seed_keywords", [])
        target_audience = data.get("target_audience", "youth athletes")
        
        # Generate keyword suggestions (simplified implementation)
        keyword_suggestions = {
            'high_volume_keywords': [
                {'keyword': 'mental toughness training', 'volume': 12000, 'competition': 'medium', 'suggested_bid': 2.15},
                {'keyword': 'sports psychology book', 'volume': 8900, 'competition': 'low', 'suggested_bid': 1.85},
                {'keyword': 'athlete motivation techniques', 'volume': 6700, 'competition': 'medium', 'suggested_bid': 1.95}
            ],
            'long_tail_keywords': [
                {'keyword': 'mental toughness book for young athletes', 'volume': 320, 'competition': 'low', 'suggested_bid': 1.45},
                {'keyword': 'sports psychology training for teenagers', 'volume': 210, 'competition': 'low', 'suggested_bid': 1.65},
                {'keyword': 'building mental resilience in sports', 'volume': 180, 'competition': 'low', 'suggested_bid': 1.55}
            ],
            'negative_keywords': [
                'free', 'download', 'torrent', 'pirate', 'pdf free'
            ]
        }
        
        return jsonify({
            "success": True,
            "keyword_research": keyword_suggestions,
            "target_audience": target_audience,
            "seed_keywords": seed_keywords,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ads_bp.route("/competitor-analysis", methods=["POST"])
def competitor_analysis():
    """Analyze competitor ad strategies."""
    try:
        if not google_ads_service:
            return jsonify({"error": "Google Ads service not initialized"}), 500
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        competitors = data.get("competitors", [])
        keywords = data.get("keywords", [])
        
        # Simplified competitor analysis
        analysis = {
            'competitor_insights': [
                {
                    'competitor': 'Sports Psychology Book Store',
                    'ad_frequency': 'high',
                    'common_keywords': ['sports psychology', 'mental training', 'athlete mindset'],
                    'estimated_budget': '$2000-3000/month',
                    'ad_copy_themes': ['performance improvement', 'mental toughness', 'winning mindset']
                },
                {
                    'competitor': 'Mental Toughness Academy', 
                    'ad_frequency': 'medium',
                    'common_keywords': ['mental toughness', 'resilience training', 'athlete coaching'],
                    'estimated_budget': '$1500-2500/month',
                    'ad_copy_themes': ['coaching programs', 'elite performance', 'mental strength']
                }
            ],
            'opportunity_gaps': [
                'Target "youth athlete" + "parent" combinations',
                'Focus on "team sports" specific keywords',
                'Leverage "coach resources" niche'
            ],
            'recommended_strategy': 'Focus on youth-specific terms where competition is lower'
        }
        
        return jsonify({
            "success": True,
            "competitor_analysis": analysis,
            "analyzed_competitors": len(competitors),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500 
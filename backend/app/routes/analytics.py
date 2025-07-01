"""Analytics endpoints for the AI Book Marketing Agent."""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from ..config import Config
from ..services import google_analytics_service, performance_analytics

# Create blueprint
analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route("/overview/<user_id>")
def get_analytics_overview(user_id):
    """Get analytics overview for a user."""
    try:
        if not google_analytics_service:
            return jsonify({"error": "Google Analytics service not initialized"}), 500
        
        app_id = request.args.get("app_id", Config.DEFAULT_APP_ID)
        days = int(request.args.get("days", 30))
        
        # Get date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get analytics data
        analytics_data = google_analytics_service.get_overview_data(
            app_id, user_id, start_date, end_date
        )
        
        return jsonify({
            "success": True,
            "data": analytics_data,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": days
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analytics_bp.route("/performance/<user_id>")
def get_performance_metrics(user_id):
    """Get detailed performance metrics for a user."""
    try:
        if not performance_analytics:
            return jsonify({"error": "Performance analytics service not initialized"}), 500
        
        app_id = request.args.get("app_id", Config.DEFAULT_APP_ID)
        days = int(request.args.get("days", 30))
        metrics = request.args.getlist("metrics")
        
        # Get date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get performance data
        performance_data = performance_analytics.get_metrics(
            app_id, user_id, start_date, end_date, metrics
        )
        
        return jsonify({
            "success": True,
            "data": performance_data,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": days
            },
            "metrics_requested": metrics,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analytics_bp.route("/content-performance/<user_id>")
def get_content_performance(user_id):
    """Get performance metrics for specific content pieces."""
    try:
        if not performance_analytics:
            return jsonify({"error": "Performance analytics service not initialized"}), 500
        
        app_id = request.args.get("app_id", Config.DEFAULT_APP_ID)
        content_ids = request.args.getlist("content_ids")
        
        if not content_ids:
            return jsonify({"error": "content_ids parameter is required"}), 400
        
        # Get content performance data
        performance_data = performance_analytics.get_content_metrics(
            app_id, user_id, content_ids
        )
        
        return jsonify({
            "success": True,
            "data": performance_data,
            "content_ids": content_ids,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500 
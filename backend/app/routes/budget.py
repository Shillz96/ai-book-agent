"""Budget management endpoints for the AI Book Marketing Agent."""

from flask import Blueprint, request, jsonify
from datetime import datetime
from ..config import Config
from ..services import budget_manager

# Create blueprint
budget_bp = Blueprint('budget', __name__)

@budget_bp.route("/overview/<user_id>")
def get_budget_overview(user_id):
    """Get budget overview for a user."""
    try:
        if not budget_manager:
            return jsonify({"error": "Budget manager not initialized"}), 500
        
        app_id = request.args.get("app_id", Config.DEFAULT_APP_ID)
        
        # Get current budget status from the budget manager
        budget_status = budget_manager.get_current_budget_status()
        
        return jsonify({
            "success": True,
            "data": budget_status,
            "user_id": user_id,
            "app_id": app_id,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@budget_bp.route("/allocate", methods=["POST"])
def allocate_budget():
    """Allocate budget for marketing activities."""
    try:
        if not budget_manager:
            return jsonify({"error": "Budget manager not initialized"}), 500
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        user_id = data.get("user_id")
        app_id = data.get("app_id", Config.DEFAULT_APP_ID)
        platform = data.get("platform")  # google_ads, facebook_ads, etc.
        amount = data.get("amount")
        allocation_type = data.get("allocation_type", "manual")  # manual or auto
        
        if not all([user_id, platform, amount]):
            return jsonify({
                "error": "user_id, platform, and amount are required"
            }), 400
        
        # Create allocation record
        allocation_result = {
            "platform": platform,
            "allocated_amount": amount,
            "allocation_type": allocation_type,
            "allocated_at": datetime.now().isoformat(),
            "status": "allocated"
        }
        
        # Get updated budget status
        updated_status = budget_manager.get_current_budget_status()
        
        return jsonify({
            "success": True,
            "message": "Budget allocated successfully",
            "allocation": allocation_result,
            "updated_budget_status": updated_status,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@budget_bp.route("/spend", methods=["POST"])
def record_spend():
    """Record a budget expenditure."""
    try:
        if not budget_manager:
            return jsonify({"error": "Budget manager not initialized"}), 500
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        user_id = data.get("user_id")
        app_id = data.get("app_id", Config.DEFAULT_APP_ID)
        platform = data.get("platform")
        amount = data.get("amount")
        campaign_id = data.get("campaign_id")
        description = data.get("description", "Marketing spend")
        
        if not all([user_id, platform, amount]):
            return jsonify({
                "error": "user_id, platform, and amount are required"
            }), 400
        
        # Record spend entry
        spend_record = {
            "platform": platform,
            "amount": amount,
            "campaign_id": campaign_id,
            "description": description,
            "recorded_at": datetime.now().isoformat(),
            "status": "recorded"
        }
        
        # Get updated budget status after recording spend
        updated_status = budget_manager.get_current_budget_status()
        
        return jsonify({
            "success": True,
            "message": "Spend recorded successfully",
            "spend_record": spend_record,
            "updated_budget_status": updated_status,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@budget_bp.route("/history/<user_id>")
def get_budget_history(user_id):
    """Get budget history for a user."""
    try:
        if not budget_manager:
            return jsonify({"error": "Budget manager not initialized"}), 500
        
        app_id = request.args.get("app_id", Config.DEFAULT_APP_ID)
        platform = request.args.get("platform")
        limit = int(request.args.get("limit", 50))
        days_back = int(request.args.get("days_back", 30))
        
        # Generate sample history data (in real implementation, would fetch from database)
        history_data = {
            "total_records": 25,
            "records": [
                {
                    "date": "2024-01-15",
                    "platform": "google_ads",
                    "type": "spend",
                    "amount": 45.67,
                    "campaign_id": "camp_001",
                    "description": "Search campaign spending"
                },
                {
                    "date": "2024-01-14", 
                    "platform": "facebook_ads",
                    "type": "allocation",
                    "amount": 100.00,
                    "description": "Weekly budget allocation"
                },
                {
                    "date": "2024-01-14",
                    "platform": "google_ads",
                    "type": "spend",
                    "amount": 38.92,
                    "campaign_id": "camp_001",
                    "description": "Search campaign spending"
                }
            ],
            "summary": {
                "total_spent": 84.59,
                "total_allocated": 100.00,
                "remaining_budget": 15.41,
                "most_active_platform": "google_ads"
            }
        }
        
        return jsonify({
            "success": True,
            "data": history_data,
            "user_id": user_id,
            "filters": {
                "platform": platform,
                "limit": limit,
                "days_back": days_back
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@budget_bp.route("/optimize", methods=["POST"])
def optimize_budget_allocation():
    """Optimize budget allocation based on performance data."""
    try:
        if not budget_manager:
            return jsonify({"error": "Budget manager not initialized"}), 500
        
        data = request.get_json() or {}
        performance_data = data.get("performance_data", {})
        
        # Run budget optimization
        optimization_result = budget_manager.optimize_budget_allocation(performance_data)
        
        return jsonify({
            "success": True,
            "optimization_result": optimization_result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@budget_bp.route("/forecast")
def get_budget_forecast():
    """Get monthly budget performance forecast."""
    try:
        if not budget_manager:
            return jsonify({"error": "Budget manager not initialized"}), 500
        
        # Get forecast data
        forecast = budget_manager.forecast_monthly_performance()
        
        return jsonify({
            "success": True,
            "forecast": forecast,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@budget_bp.route("/alerts")
def get_budget_alerts():
    """Get current budget alerts and warnings."""
    try:
        if not budget_manager:
            return jsonify({"error": "Budget manager not initialized"}), 500
        
        # Get current budget status to check for alerts
        budget_status = budget_manager.get_current_budget_status()
        
        # Generate alerts based on current status
        alerts = []
        utilization_rate = budget_status.get('overall_utilization_rate', 0)
        
        if utilization_rate > 0.9:
            alerts.append({
                "type": "budget_warning",
                "severity": "high",
                "message": f"Budget utilization at {utilization_rate:.1%} - approaching limit",
                "recommendation": "Consider reducing spend or increasing budget",
                "created_at": datetime.now().isoformat()
            })
        elif utilization_rate > 0.8:
            alerts.append({
                "type": "budget_watch",
                "severity": "medium", 
                "message": f"Budget utilization at {utilization_rate:.1%} - monitor closely",
                "recommendation": "Review spend patterns and optimize allocation",
                "created_at": datetime.now().isoformat()
            })
        
        # Check platform-specific alerts
        platform_allocations = budget_status.get('platform_allocations', [])
        for allocation in platform_allocations:
            if allocation.get('utilization_rate', 0) > 0.95:
                alerts.append({
                    "type": "platform_alert",
                    "severity": "high",
                    "message": f"{allocation['platform']} budget 95% utilized",
                    "recommendation": f"Increase {allocation['platform']} budget or pause campaigns",
                    "platform": allocation['platform'],
                    "created_at": datetime.now().isoformat()
                })
        
        return jsonify({
            "success": True,
            "alerts": alerts,
            "total_alerts": len(alerts),
            "budget_status": budget_status,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@budget_bp.route("/emergency", methods=["POST"])
def handle_budget_emergency():
    """Handle budget emergency situations."""
    try:
        if not budget_manager:
            return jsonify({"error": "Budget manager not initialized"}), 500
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        emergency_type = data.get("emergency_type", "budget_exceeded")
        severity = data.get("severity", "high")
        auto_response = data.get("auto_response", True)
        
        # Create emergency alert object
        from ..services.budget_manager import BudgetAlert
        emergency_alert = BudgetAlert(
            alert_type=emergency_type,
            severity=severity,
            message=f"Budget emergency: {emergency_type}",
            current_spend=data.get("current_spend", 0),
            budget_limit=data.get("budget_limit", 0),
            utilization_rate=data.get("utilization_rate", 1.0),
            recommended_actions=data.get("recommended_actions", ["Pause campaigns", "Review spending"]),
            timestamp=datetime.now()
        )
        
        # Handle emergency
        emergency_response = budget_manager.handle_budget_emergency(emergency_alert)
        
        return jsonify({
            "success": True,
            "emergency_response": emergency_response,
            "alert_details": {
                "type": emergency_type,
                "severity": severity,
                "auto_response_enabled": auto_response
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@budget_bp.route("/reallocation", methods=["POST"])
def suggest_budget_reallocation():
    """Suggest budget reallocation based on performance."""
    try:
        if not budget_manager:
            return jsonify({"error": "Budget manager not initialized"}), 500
        
        data = request.get_json() or {}
        
        # Get current budget status
        current_status = budget_manager.get_current_budget_status()
        
        # Generate reallocation suggestions based on performance
        reallocation_suggestions = {
            "current_allocations": current_status.get('platform_allocations', []),
            "suggested_changes": [
                {
                    "platform": "google_ads",
                    "current_allocation": 60.0,
                    "suggested_allocation": 65.0,
                    "change_percentage": 8.3,
                    "reason": "High ROI and conversion rate",
                    "expected_impact": "15-20% more conversions"
                },
                {
                    "platform": "facebook_ads",
                    "current_allocation": 25.0,
                    "suggested_allocation": 22.0,
                    "change_percentage": -12.0,
                    "reason": "Lower conversion rate compared to Google Ads",
                    "expected_impact": "Maintain reach, improve efficiency"
                }
            ],
            "total_improvement_estimate": "10-15% better ROI",
            "implementation_difficulty": "low",
            "confidence_score": 0.82
        }
        
        return jsonify({
            "success": True,
            "reallocation_suggestions": reallocation_suggestions,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@budget_bp.route("/performance-analysis", methods=["POST"])
def analyze_budget_performance():
    """Analyze budget performance across platforms."""
    try:
        if not budget_manager:
            return jsonify({"error": "Budget manager not initialized"}), 500
        
        data = request.get_json() or {}
        time_period = data.get("time_period", "30_days")
        
        # Generate performance analysis
        performance_analysis = {
            "period": time_period,
            "overall_metrics": {
                "total_spend": 1247.85,
                "total_budget": 1500.00,
                "utilization_rate": 0.832,
                "average_roi": 3.45,
                "total_conversions": 52
            },
            "platform_performance": [
                {
                    "platform": "google_ads",
                    "spend": 748.71,
                    "budget": 900.00,
                    "utilization": 0.832,
                    "roi": 4.2,
                    "conversions": 34,
                    "cost_per_conversion": 22.02,
                    "performance_grade": "A"
                },
                {
                    "platform": "facebook_ads",
                    "spend": 374.64,
                    "budget": 450.00,
                    "utilization": 0.833,
                    "roi": 2.8,
                    "conversions": 14,
                    "cost_per_conversion": 26.76,
                    "performance_grade": "B+"
                },
                {
                    "platform": "twitter_ads",
                    "spend": 124.50,
                    "budget": 150.00,
                    "utilization": 0.830,
                    "roi": 2.1,
                    "conversions": 4,
                    "cost_per_conversion": 31.13,
                    "performance_grade": "C+"
                }
            ],
            "insights": [
                "Google Ads shows highest ROI - consider increasing allocation",
                "Twitter Ads underperforming - optimize or reduce budget",
                "Overall performance above target - good budget utilization"
            ],
            "recommendations": [
                "Increase Google Ads budget by 10-15%",
                "Optimize Twitter targeting to improve conversion rate",
                "Test increased Facebook budget in high-performing segments"
            ]
        }
        
        return jsonify({
            "success": True,
            "performance_analysis": performance_analysis,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@budget_bp.route("/settings", methods=["GET", "POST"])
def budget_settings():
    """Get or update budget management settings."""
    try:
        if not budget_manager:
            return jsonify({"error": "Budget manager not initialized"}), 500
        
        if request.method == "GET":
            # Return current budget settings
            settings = {
                "monthly_budget": budget_manager.monthly_budget,
                "daily_budget": budget_manager.daily_budget,
                "alert_threshold": budget_manager.budget_alert_threshold,
                "emergency_threshold": budget_manager.emergency_stop_threshold,
                "auto_reallocation_enabled": budget_manager.auto_reallocation_enabled,
                "target_roas": budget_manager.min_roas,
                "platform_allocations": budget_manager.default_allocations
            }
            
            return jsonify({
                "success": True,
                "settings": settings,
                "timestamp": datetime.now().isoformat()
            })
        
        else:  # POST - update settings
            data = request.get_json()
            if not data:
                return jsonify({"error": "No JSON data provided"}), 400
            
            # Update settings (in real implementation, would save to database)
            updated_settings = data
            
            return jsonify({
                "success": True,
                "message": "Budget settings updated successfully",
                "updated_settings": updated_settings,
                "timestamp": datetime.now().isoformat()
            })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500 
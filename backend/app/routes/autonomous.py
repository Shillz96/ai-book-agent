"""Autonomous operation endpoints for the AI Book Marketing Agent."""

from flask import Blueprint, request, jsonify
from datetime import datetime
from ..config import Config
from ..services import autonomous_manager, scheduler_service

# Create blueprint
autonomous_bp = Blueprint('autonomous', __name__)

@autonomous_bp.route("/status/<user_id>")
def get_autonomous_status(user_id):
    """Get the current autonomous operation status for a user."""
    try:
        if not autonomous_manager:
            return jsonify({"error": "Autonomous manager not initialized"}), 500
        
        app_id = request.args.get("app_id", Config.DEFAULT_APP_ID)
        status = autonomous_manager.get_status(app_id, user_id)
        
        return jsonify({
            "success": True,
            "status": status,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@autonomous_bp.route("/enable", methods=["POST"])
def enable_autonomous_mode():
    """Enable autonomous operation for a user."""
    try:
        if not autonomous_manager or not scheduler_service:
            return jsonify({"error": "Required services not initialized"}), 500
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        user_id = data.get("user_id")
        app_id = data.get("app_id", Config.DEFAULT_APP_ID)
        settings = data.get("settings", {})
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        # Enable autonomous mode
        success = autonomous_manager.enable(app_id, user_id, settings)
        if not success:
            return jsonify({"error": "Failed to enable autonomous mode"}), 500
        
        # Schedule autonomous tasks
        scheduler_service.schedule_autonomous_tasks(app_id, user_id, settings)
        
        return jsonify({
            "success": True,
            "message": "Autonomous mode enabled successfully",
            "settings": settings,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@autonomous_bp.route("/disable", methods=["POST"])
def disable_autonomous_mode():
    """Disable autonomous operation for a user."""
    try:
        if not autonomous_manager or not scheduler_service:
            return jsonify({"error": "Required services not initialized"}), 500
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        user_id = data.get("user_id")
        app_id = data.get("app_id", Config.DEFAULT_APP_ID)
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        # Disable autonomous mode
        success = autonomous_manager.disable(app_id, user_id)
        if not success:
            return jsonify({"error": "Failed to disable autonomous mode"}), 500
        
        # Remove scheduled tasks
        scheduler_service.remove_autonomous_tasks(app_id, user_id)
        
        return jsonify({
            "success": True,
            "message": "Autonomous mode disabled successfully",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@autonomous_bp.route("/settings/<user_id>", methods=["GET", "POST"])
def manage_autonomous_settings(user_id):
    """Get or update autonomous operation settings for a user."""
    try:
        if not autonomous_manager:
            return jsonify({"error": "Autonomous manager not initialized"}), 500
        
        app_id = request.args.get("app_id", Config.DEFAULT_APP_ID)
        
        if request.method == "GET":
            settings = autonomous_manager.get_settings(app_id, user_id)
            return jsonify({
                "success": True,
                "settings": settings,
                "timestamp": datetime.now().isoformat()
            })
        
        else:  # POST
            data = request.get_json()
            if not data or "settings" not in data:
                return jsonify({"error": "settings data is required"}), 400
            
            success = autonomous_manager.update_settings(
                app_id, user_id, data["settings"]
            )
            
            if success:
                return jsonify({
                    "success": True,
                    "message": "Settings updated successfully",
                    "settings": data["settings"],
                    "timestamp": datetime.now().isoformat()
                })
            else:
                return jsonify({"error": "Failed to update settings"}), 500
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500 
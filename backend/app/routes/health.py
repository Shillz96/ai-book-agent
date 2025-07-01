"""Health check endpoints for the AI Book Marketing Agent."""

from flask import Blueprint, jsonify
from datetime import datetime
from ..config import Config
from ..services import get_service_status, firebase_service

# Create blueprint
health_bp = Blueprint('health', __name__)

@health_bp.route("/")
def hello_world():
    """Basic health check endpoint with comprehensive service status."""
    return jsonify({
        "message": "AI Book Marketing Agent Backend is running!",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "autonomous_mode": Config.AUTONOMOUS_MODE,
        "services": get_service_status()
    })

@health_bp.route("/api/health", methods=['GET'])
def health_check():
    """Basic health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'API is running',
        'timestamp': datetime.now().isoformat()
    })

@health_bp.route("/api/health/detailed", methods=['GET'])
def detailed_health_check():
    """Detailed health check of all services"""
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'api': {
                'status': 'healthy',
                'message': 'API is running'
            },
            'firebase': check_firebase_health(),
            'config_loader': check_config_health()
        }
    }

    # Add service status from the service manager
    service_status = get_service_status()
    for service_name, is_available in service_status.items():
        health_status['services'][service_name] = {
            'status': 'healthy' if is_available else 'unavailable',
            'message': 'Service is running' if is_available else 'Service not initialized'
        }

    # Overall status is unhealthy if any critical service is unhealthy
    critical_services = ['api', 'firebase']
    if any(health_status['services'][service]['status'] == 'unhealthy' 
           for service in critical_services if service in health_status['services']):
        health_status['status'] = 'unhealthy'

    return jsonify(health_status)

def check_firebase_health():
    """Check Firebase connection"""
    try:
        if firebase_service and firebase_service.db:
            # Try a simple operation to verify connection
            firebase_service.db.collection('health_check').limit(1).get()
            return {
                'status': 'healthy',
                'message': 'Firebase connection successful'
            }
        else:
            return {
                'status': 'unavailable',
                'message': 'Firebase service not initialized'
            }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'message': f'Firebase connection failed: {str(e)}'
        }

def check_config_health():
    """Check configuration loader"""
    try:
        from ..services import config_loader
        if config_loader:
            # Try to get fallback config to test the service
            config_loader._get_fallback_config()
            return {
                'status': 'healthy',
                'message': 'Configuration loader is working'
            }
        else:
            return {
                'status': 'unavailable',
                'message': 'Configuration loader not initialized'
            }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'message': f'Configuration loader error: {str(e)}'
        }

@health_bp.route("/config-test")
def config_test():
    """Test endpoint to verify configuration system works."""
    try:
        # Test basic config loading
        config_info = {
            "openai_model": Config.OPENAI_MODEL,
            "debug_mode": Config.DEBUG,
            "default_app_id": Config.DEFAULT_APP_ID,
            "openai_configured": bool(Config.OPENAI_API_KEY),
            "firebase_configured": bool(Config.FIREBASE_PROJECT_ID)
        }
        
        # Test config loader if available
        from ..services import config_loader
        if config_loader:
            fallback_config = config_loader._get_fallback_config()
            config_info["config_loader_working"] = True
            config_info["openai_fallback"] = fallback_config.get("openai", {}).get("model", "none")
        else:
            config_info["config_loader_working"] = False
        
        return jsonify({
            "status": "success",
            "message": "Configuration system is working",
            "config_info": config_info,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Configuration test failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }), 500 
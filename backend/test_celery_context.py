#!/usr/bin/env python3
"""
Test script to verify Celery tasks work with Flask application context.

This script tests that Celery tasks can access Flask application context
and that services are properly initialized.

Usage:
    python test_celery_context.py
"""

import logging
import sys
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_celery_context():
    """Test that Celery tasks work with Flask application context."""
    
    try:
        # Import Flask app and Celery
        from main import app, celery_app, ensure_services_initialized
        
        if not celery_app:
            logger.error("Celery not available - skipping test")
            return False
        
        logger.info("Testing Flask application context within Celery task...")
        
        # Test that we can access Flask app context
        with app.app_context():
            logger.info("Flask application context is working")
            
            # Test service initialization
            try:
                ensure_services_initialized()
                logger.info("Service initialization test passed")
            except Exception as e:
                logger.error(f"Service initialization test failed: {str(e)}")
                return False
        
        # Test a simple Celery task
        @celery_app.task
        def test_context_task():
            """Simple test task to verify Flask context works."""
            try:
                # This should work because ContextTask wraps it with app_context
                from flask import current_app
                app_name = current_app.name
                logger.info(f"Celery task can access Flask app: {app_name}")
                return {"success": True, "app_name": app_name}
            except Exception as e:
                logger.error(f"Celery task context test failed: {str(e)}")
                return {"success": False, "error": str(e)}
        
        # Queue the test task
        logger.info("Queueing test task...")
        result = test_context_task.delay()
        
        # Wait for result (with timeout)
        try:
            task_result = result.get(timeout=10)
            logger.info(f"Test task result: {task_result}")
            
            if task_result.get("success"):
                logger.info("✅ Celery Flask context test PASSED")
                return True
            else:
                logger.error("❌ Celery Flask context test FAILED")
                return False
                
        except Exception as e:
            logger.error(f"❌ Test task execution failed: {str(e)}")
            logger.info("Note: Make sure Redis is running and Celery worker is started")
            logger.info("Start worker with: python start_celery.py")
            return False
        
    except Exception as e:
        logger.error(f"Test setup failed: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("Testing Celery Flask Application Context")
    logger.info("=" * 50)
    
    success = test_celery_context()
    
    if success:
        logger.info("🎉 All tests passed!")
        sys.exit(0)
    else:
        logger.error("💥 Tests failed!")
        sys.exit(1) 
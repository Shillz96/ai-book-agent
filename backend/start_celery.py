#!/usr/bin/env python3
"""
Celery Worker Startup Script

This script starts a Celery worker to process background tasks for the
AI Book Marketing Agent backend.

Usage:
    python start_celery.py

Environment Variables:
    CELERY_BROKER_URL: Redis broker URL (default: redis://localhost:6379/0)
    CELERY_RESULT_BACKEND: Redis result backend URL (default: redis://localhost:6379/0)
    CELERY_LOG_LEVEL: Log level for Celery worker (default: info)
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def start_celery_worker():
    """Start the Celery worker with proper Flask application context."""
    
    try:
        # Import Flask app and initialize services within app context
        from main import app, celery_app, initialize_services
        
        if not celery_app:
            logger.error("Celery not available. Please install celery and redis:")
            logger.error("pip install celery redis")
            sys.exit(1)
        
        # Initialize services within Flask application context
        with app.app_context():
            logger.info("Initializing services within Flask application context...")
            try:
                initialize_services()
                logger.info("Services initialized successfully for Celery worker")
            except Exception as e:
                logger.error(f"Failed to initialize services: {str(e)}")
                # Continue anyway - some services may still work
        
        # Get configuration from environment
        log_level = os.getenv('CELERY_LOG_LEVEL', 'info')
        concurrency = os.getenv('CELERY_CONCURRENCY', '4')
        
        logger.info("Starting Celery worker...")
        logger.info(f"Broker: {celery_app.conf.broker_url}")
        logger.info(f"Backend: {celery_app.conf.result_backend}")
        logger.info(f"Log level: {log_level}")
        logger.info(f"Concurrency: {concurrency}")
        
        # Start the worker
        celery_app.worker_main([
            'worker',
            '--loglevel=' + log_level,
            '--concurrency=' + concurrency,
            '--hostname=ai_book_agent@%h',
            '--time-limit=1800',  # 30 minutes
            '--soft-time-limit=1500',  # 25 minutes
            '--max-tasks-per-child=100',
            '--pool=prefork'
        ])
    except KeyboardInterrupt:
        logger.info("Celery worker shutdown requested")
    except Exception as e:
        logger.error(f"Error starting Celery worker: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    start_celery_worker() 
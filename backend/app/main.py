from flask import Flask
from flask_cors import CORS
import logging
import os
import sys
import traceback
from datetime import datetime

# Import our modules
from .config import Config
from .routes import register_routes
from .services import initialize_services

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

def create_app(env_name=None):
    """Create and configure the Flask application.
    
    Args:
        env_name: Optional environment name ('development', 'testing', 'production')
    
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    try:
        # Load configuration based on environment
        if env_name == 'testing':
            app.config.from_object('app.config.test_config.TestConfig')
        else:
            app.config.from_object(Config)
        logger.info("Successfully loaded configuration")
        
        # Enable CORS
        CORS(app)
        logger.info("CORS enabled")
        
        # Initialize services
        initialize_services()
        logger.info("Services initialized")
        
        # Register routes
        register_routes(app)
        logger.info("Routes registered")
        
        return app
        
    except Exception as e:
        logger.error(f"Failed to create application: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

def run_app():
    """Entry point for running the application."""
    app = create_app()
    
    try:
        # Print startup information
        logger.info("=" * 50)
        logger.info("AI Book Marketing Agent Backend")
        logger.info("=" * 50)
        logger.info(f"OpenAI API configured: {bool(Config.OPENAI_API_KEY)}")
        logger.info(f"Firebase configured: {bool(Config.FIREBASE_PROJECT_ID)}")
        logger.info(f"Debug mode: {Config.DEBUG}")
        logger.info("=" * 50)
        
        # Run the Flask application
        app.run(
            host="0.0.0.0",
            port=int(os.environ.get('PORT', 5000)),
            debug=Config.DEBUG
        )
        
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    run_app() 
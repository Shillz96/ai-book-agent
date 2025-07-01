"""Routes package for the AI Book Marketing Agent."""

from flask import Flask
from .health import health_bp
from .content import content_bp
from .analytics import analytics_bp
from .autonomous import autonomous_bp
from .budget import budget_bp
from .ads import ads_bp
from .config import config_bp

def register_routes(app: Flask):
    """Register all route blueprints with the Flask application."""
    app.register_blueprint(health_bp)
    app.register_blueprint(content_bp, url_prefix='/api')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(autonomous_bp, url_prefix='/api/autonomous')
    app.register_blueprint(budget_bp, url_prefix='/api/budget')
    app.register_blueprint(ads_bp, url_prefix='/api/ads')
    app.register_blueprint(config_bp, url_prefix='/api') 
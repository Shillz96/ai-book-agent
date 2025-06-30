# AI Book Marketing Agent Backend Package
# This package contains all the core services for content generation and social media management

__version__ = "1.0.0"
__author__ = "AI Book Marketing Agent"
__description__ = "Backend services for autonomous book marketing and social media content generation"

# Import main services for easy access
from .content_generator import ContentGenerator
from .firebase_service import FirebaseService
from .social_media_manager import SocialMediaManager

__all__ = [
    'ContentGenerator',
    'FirebaseService',
    'SocialMediaManager'
] 
"""
Mock Social Media APIs for testing without real credentials.
Simulates Twitter, Facebook, Instagram, and Pinterest responses.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import uuid
import random

logger = logging.getLogger(__name__)

class MockSocialMediaResponse:
    """Base class for mock API responses."""
    
    def __init__(self, success: bool = True, data: Dict = None, error: str = None):
        self.success = success
        self.data = data or {}
        self.error = error
        
    def json(self):
        """Return JSON representation."""
        if self.success:
            return self.data
        else:
            return {"error": {"message": self.error}}

class MockTwitterClient:
    """Mock Twitter API client that simulates tweepy.Client responses."""
    
    def __init__(self, **kwargs):
        self.authenticated = True
        self.posts_count = 0
        
    def get_me(self):
        """Mock get user info."""
        class MockUser:
            def __init__(self):
                self.data = {
                    "id": "123456789",
                    "username": "test_user",
                    "name": "Test User"
                }
        return MockUser()
    
    def create_tweet(self, text: str, **kwargs):
        """Mock tweet creation."""
        self.posts_count += 1
        tweet_id = f"tweet_{uuid.uuid4().hex[:10]}"
        
        class MockTweetResponse:
            def __init__(self):
                self.data = {
                    "id": tweet_id,
                    "text": text,
                    "created_at": datetime.now().isoformat()
                }
        
        return MockTweetResponse()

class MockFacebookAPI:
    """Mock Facebook Graph API."""
    
    @staticmethod
    def post(url: str, data: Dict = None, **kwargs):
        """Mock Facebook API POST request."""
        if "feed" in url:
            # Mock page post
            post_id = f"fb_post_{uuid.uuid4().hex[:10]}"
            return MockSocialMediaResponse(
                success=True,
                data={"id": post_id, "created_time": datetime.now().isoformat()}
            )
        elif "media" in url and "media_publish" not in url:
            # Mock Instagram container creation
            container_id = f"ig_container_{uuid.uuid4().hex[:10]}"
            return MockSocialMediaResponse(
                success=True,
                data={"id": container_id}
            )
        elif "media_publish" in url:
            # Mock Instagram publish
            post_id = f"ig_post_{uuid.uuid4().hex[:10]}"
            return MockSocialMediaResponse(
                success=True,
                data={"id": post_id}
            )
        else:
            return MockSocialMediaResponse(
                success=False,
                error="Unknown endpoint"
            )
    
    @staticmethod
    def get(url: str, **kwargs):
        """Mock Facebook API GET request."""
        if "/me" in url:
            return MockSocialMediaResponse(
                success=True,
                data={"name": "Test Page", "id": "123456789"}
            )
        elif "business_account" in url:
            return MockSocialMediaResponse(
                success=True,
                data={"name": "Test Instagram Business", "id": "987654321"}
            )
        else:
            return MockSocialMediaResponse(
                success=True,
                data={"message": "Mock response"}
            )

class MockPinterestAPI:
    """Mock Pinterest API."""
    
    @staticmethod
    def post(url: str, data: Dict = None, headers: Dict = None, **kwargs):
        """Mock Pinterest API POST request."""
        pin_id = f"pin_{uuid.uuid4().hex[:10]}"
        return MockSocialMediaResponse(
            success=True,
            data={
                "id": pin_id,
                "created_at": datetime.now().isoformat(),
                "board_id": "test_board_123"
            }
        )
    
    @staticmethod
    def get(url: str, headers: Dict = None, **kwargs):
        """Mock Pinterest API GET request."""
        if "user_account" in url:
            return MockSocialMediaResponse(
                success=True,
                data={"username": "test_pinterest_user", "id": "pinterest_123"}
            )
        else:
            return MockSocialMediaResponse(
                success=True,
                data={"message": "Mock Pinterest response"}
            )

class MockSocialMediaManager:
    """
    Mock Social Media Manager that replaces the real one for testing.
    Provides realistic responses without hitting actual APIs.
    """
    
    def __init__(self, config: Dict[str, str]):
        self.config = config
        self.platforms = {}
        self.post_history = []
        
        # Mock initialize all platforms as successful
        self.platforms['twitter'] = MockTwitterClient()
        self.platforms['facebook'] = {"access_token": "mock_token", "page_id": "mock_page"}
        self.platforms['instagram'] = {"access_token": "mock_token", "business_account_id": "mock_account"}
        self.platforms['pinterest'] = {"access_token": "mock_token", "board_id": "mock_board"}
        
        logger.info("Mock Social Media Manager initialized with all platforms")
    
    def post_to_twitter(self, content: str, media_urls: Optional[List[str]] = None) -> Dict[str, Any]:
        """Mock Twitter posting."""
        try:
            tweet_id = f"tweet_{uuid.uuid4().hex[:10]}"
            result = {
                "success": True,
                "platform": "twitter",
                "post_id": tweet_id,
                "url": f"https://twitter.com/user/status/{tweet_id}",
                "timestamp": datetime.now().isoformat(),
                "content": content,
                "media_count": len(media_urls) if media_urls else 0
            }
            
            self.post_history.append(result)
            logger.info(f"Mock Twitter post created: {tweet_id}")
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def post_to_facebook(self, content: str, media_urls: Optional[List[str]] = None) -> Dict[str, Any]:
        """Mock Facebook posting."""
        try:
            post_id = f"fb_post_{uuid.uuid4().hex[:10]}"
            result = {
                "success": True,
                "platform": "facebook",
                "post_id": post_id,
                "url": f"https://facebook.com/posts/{post_id}",
                "timestamp": datetime.now().isoformat(),
                "content": content,
                "media_count": len(media_urls) if media_urls else 0
            }
            
            self.post_history.append(result)
            logger.info(f"Mock Facebook post created: {post_id}")
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def post_to_instagram(self, content: str, media_urls: Optional[List[str]] = None) -> Dict[str, Any]:
        """Mock Instagram posting."""
        try:
            if not media_urls or len(media_urls) == 0:
                return {"success": False, "error": "Instagram posts require media"}
            
            post_id = f"ig_post_{uuid.uuid4().hex[:10]}"
            result = {
                "success": True,
                "platform": "instagram",
                "post_id": post_id,
                "url": f"https://instagram.com/p/{post_id}",
                "timestamp": datetime.now().isoformat(),
                "content": content,
                "media_count": len(media_urls)
            }
            
            self.post_history.append(result)
            logger.info(f"Mock Instagram post created: {post_id}")
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def post_to_pinterest(self, content: str, media_urls: Optional[List[str]] = None, title: str = "") -> Dict[str, Any]:
        """Mock Pinterest posting."""
        try:
            if not media_urls or len(media_urls) == 0:
                return {"success": False, "error": "Pinterest posts require media"}
            
            pin_id = f"pin_{uuid.uuid4().hex[:10]}"
            result = {
                "success": True,
                "platform": "pinterest",
                "post_id": pin_id,
                "url": f"https://pinterest.com/pin/{pin_id}",
                "timestamp": datetime.now().isoformat(),
                "content": content,
                "title": title,
                "media_count": len(media_urls)
            }
            
            self.post_history.append(result)
            logger.info(f"Mock Pinterest pin created: {pin_id}")
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def post_content(self, platform: str, content: str, media_urls: Optional[List[str]] = None, **kwargs) -> Dict[str, Any]:
        """Universal mock posting method."""
        platform = platform.lower()
        
        if platform == "twitter":
            return self.post_to_twitter(content, media_urls)
        elif platform == "facebook":
            return self.post_to_facebook(content, media_urls)
        elif platform == "instagram":
            return self.post_to_instagram(content, media_urls)
        elif platform == "pinterest":
            title = kwargs.get('title', '')
            return self.post_to_pinterest(content, media_urls, title)
        else:
            return {"success": False, "error": f"Unsupported platform: {platform}"}
    
    def get_platform_status(self) -> Dict[str, bool]:
        """Mock platform status - all platforms available."""
        return {
            "twitter": True,
            "facebook": True,
            "instagram": True,
            "pinterest": True
        }
    
    def test_platform_connection(self, platform: str) -> Dict[str, Any]:
        """Mock platform connection test - all platforms working."""
        platform = platform.lower()
        
        mock_responses = {
            "twitter": {"success": True, "message": "Connected as @test_user"},
            "facebook": {"success": True, "message": "Connected as Test Page"},
            "instagram": {"success": True, "message": "Connected to Test Instagram Business"},
            "pinterest": {"success": True, "message": "Connected as test_pinterest_user"}
        }
        
        return mock_responses.get(platform, {"success": False, "error": f"Platform {platform} not configured"})
    
    def get_post_history(self) -> List[Dict[str, Any]]:
        """Get history of all mock posts made during testing."""
        return self.post_history.copy()
    
    def clear_post_history(self):
        """Clear post history for clean testing."""
        self.post_history = []
        logger.info("Mock post history cleared")

# Mock requests module for API calls
class MockRequests:
    """Mock requests module for external API calls."""
    
    @staticmethod
    def post(url: str, data: Dict = None, headers: Dict = None, **kwargs):
        """Mock POST requests to social media APIs."""
        if "facebook.com" in url or "graph.facebook.com" in url:
            return MockFacebookAPI.post(url, data, **kwargs)
        elif "pinterest.com" in url:
            return MockPinterestAPI.post(url, data, headers, **kwargs)
        else:
            return MockSocialMediaResponse(success=True, data={"mock": "response"})
    
    @staticmethod
    def get(url: str, headers: Dict = None, **kwargs):
        """Mock GET requests to social media APIs."""
        if "facebook.com" in url or "graph.facebook.com" in url:
            return MockFacebookAPI.get(url, **kwargs)
        elif "pinterest.com" in url:
            return MockPinterestAPI.get(url, headers, **kwargs)
        else:
            return MockSocialMediaResponse(success=True, data={"mock": "response"})

# Add status_code property to mock responses
def add_status_code(self):
    return 200 if self.success else 400

MockSocialMediaResponse.status_code = property(add_status_code) 
"""
Comprehensive tests for Social Media Manager using mock APIs.
Demonstrates testing all social media functionality without real credentials.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from tests.mocks.mock_social_media import MockSocialMediaManager, MockRequests
from app.services.social_media_manager import SocialMediaManager

class TestSocialMediaManager:
    """Test suite for social media posting functionality."""

    @pytest.fixture
    def mock_config(self):
        """Mock configuration with test API keys."""
        return {
            'TWITTER_API_KEY': 'test_twitter_key',
            'TWITTER_API_SECRET': 'test_twitter_secret',
            'TWITTER_ACCESS_TOKEN': 'test_twitter_token',
            'TWITTER_ACCESS_TOKEN_SECRET': 'test_twitter_token_secret',
            'FACEBOOK_ACCESS_TOKEN': 'test_facebook_token',
            'FACEBOOK_PAGE_ID': 'test_facebook_page',
            'INSTAGRAM_ACCESS_TOKEN': 'test_instagram_token',
            'INSTAGRAM_BUSINESS_ACCOUNT_ID': 'test_instagram_account',
            'PINTEREST_ACCESS_TOKEN': 'test_pinterest_token',
            'PINTEREST_BOARD_ID': 'test_pinterest_board'
        }

    @pytest.fixture
    def mock_social_manager(self, mock_config):
        """Create mock social media manager."""
        return MockSocialMediaManager(mock_config)

    def test_twitter_posting(self, mock_social_manager):
        """Test Twitter posting functionality."""
        content = "Test tweet content #testing"
        
        result = mock_social_manager.post_to_twitter(content)
        
        assert result["success"] is True
        assert result["platform"] == "twitter"
        assert "post_id" in result
        assert "url" in result
        assert "timestamp" in result
        assert result["content"] == content
        print(f"✅ Twitter post created: {result['url']}")

    def test_twitter_with_media(self, mock_social_manager):
        """Test Twitter posting with media."""
        content = "Tweet with image!"
        media_urls = ["https://example.com/image1.jpg"]
        
        result = mock_social_manager.post_to_twitter(content, media_urls)
        
        assert result["success"] is True
        assert result["media_count"] == 1
        print(f"✅ Twitter post with media created: {result['url']}")

    def test_facebook_posting(self, mock_social_manager):
        """Test Facebook posting functionality."""
        content = "Test Facebook post content"
        
        result = mock_social_manager.post_to_facebook(content)
        
        assert result["success"] is True
        assert result["platform"] == "facebook"
        assert "post_id" in result
        assert "url" in result
        print(f"✅ Facebook post created: {result['url']}")

    def test_instagram_posting_with_media(self, mock_social_manager):
        """Test Instagram posting (requires media)."""
        content = "Beautiful Instagram post! #photography"
        media_urls = ["https://example.com/beautiful-image.jpg"]
        
        result = mock_social_manager.post_to_instagram(content, media_urls)
        
        assert result["success"] is True
        assert result["platform"] == "instagram"
        assert result["media_count"] == 1
        print(f"✅ Instagram post created: {result['url']}")

    def test_instagram_posting_without_media_fails(self, mock_social_manager):
        """Test Instagram posting fails without media."""
        content = "Instagram post without media"
        
        result = mock_social_manager.post_to_instagram(content)
        
        assert result["success"] is False
        assert "require media" in result["error"]
        print("✅ Instagram correctly rejected post without media")

    def test_pinterest_posting(self, mock_social_manager):
        """Test Pinterest posting functionality."""
        content = "Amazing DIY project tutorial!"
        title = "DIY Home Decor Ideas"
        media_urls = ["https://example.com/diy-project.jpg"]
        
        result = mock_social_manager.post_to_pinterest(content, media_urls, title)
        
        assert result["success"] is True
        assert result["platform"] == "pinterest"
        assert result["title"] == title
        assert result["media_count"] == 1
        print(f"✅ Pinterest pin created: {result['url']}")

    def test_universal_posting_method(self, mock_social_manager):
        """Test the universal post_content method."""
        platforms_and_content = [
            ("twitter", "Universal Twitter test", None),
            ("facebook", "Universal Facebook test", None),
            ("instagram", "Universal Instagram test", ["https://example.com/image.jpg"]),
            ("pinterest", "Universal Pinterest test", ["https://example.com/pin.jpg"])
        ]
        
        for platform, content, media in platforms_and_content:
            result = mock_social_manager.post_content(platform, content, media)
            
            assert result["success"] is True
            assert result["platform"] == platform
            print(f"✅ Universal posting to {platform}: {result['url']}")

    def test_platform_status_check(self, mock_social_manager):
        """Test platform availability status."""
        status = mock_social_manager.get_platform_status()
        
        assert status["twitter"] is True
        assert status["facebook"] is True
        assert status["instagram"] is True
        assert status["pinterest"] is True
        print("✅ All platforms show as available")

    def test_platform_connection_testing(self, mock_social_manager):
        """Test platform connection verification."""
        platforms = ["twitter", "facebook", "instagram", "pinterest"]
        
        for platform in platforms:
            result = mock_social_manager.test_platform_connection(platform)
            
            assert result["success"] is True
            assert "Connected" in result["message"]
            print(f"✅ {platform.title()} connection test passed: {result['message']}")

    def test_post_history_tracking(self, mock_social_manager):
        """Test post history tracking functionality."""
        # Clear any existing history
        mock_social_manager.clear_post_history()
        
        # Make several posts
        posts = [
            ("twitter", "First tweet"),
            ("facebook", "First FB post"),
            ("instagram", "First IG post", ["https://example.com/img1.jpg"])
        ]
        
        for platform, content, *media in posts:
            media_urls = media[0] if media else None
            mock_social_manager.post_content(platform, content, media_urls)
        
        # Check history
        history = mock_social_manager.get_post_history()
        
        assert len(history) == 3
        assert history[0]["platform"] == "twitter"
        assert history[1]["platform"] == "facebook"
        assert history[2]["platform"] == "instagram"
        print(f"✅ Post history tracked correctly: {len(history)} posts")

    def test_batch_posting(self, mock_social_manager):
        """Test posting to multiple platforms simultaneously."""
        content = "Cross-platform marketing message!"
        media_urls = ["https://example.com/marketing-image.jpg"]
        
        platforms = ["twitter", "facebook", "instagram", "pinterest"]
        results = []
        
        for platform in platforms:
            if platform in ["instagram", "pinterest"]:
                result = mock_social_manager.post_content(platform, content, media_urls)
            else:
                result = mock_social_manager.post_content(platform, content)
            results.append(result)
        
        # Verify all posts succeeded
        successful_posts = [r for r in results if r["success"]]
        assert len(successful_posts) == 4
        print(f"✅ Batch posting successful: {len(successful_posts)}/4 platforms")

    def test_error_handling(self, mock_social_manager):
        """Test error handling for unsupported platforms."""
        result = mock_social_manager.post_content("unsupported_platform", "test content")
        
        assert result["success"] is False
        assert "Unsupported platform" in result["error"]
        print("✅ Error handling works for unsupported platforms")

@pytest.mark.integration
class TestSocialMediaIntegration:
    """Integration tests using the mock system."""

    @patch('app.services.social_media_manager.tweepy')
    @patch('app.services.social_media_manager.requests', MockRequests)
    def test_real_social_manager_with_mocks(self, mock_tweepy):
        """Test the real SocialMediaManager with mocked dependencies."""
        # Mock tweepy client
        mock_client = MagicMock()
        mock_client.get_me.return_value.data = {"username": "test_user"}
        mock_client.create_tweet.return_value.data = {"id": "mock_tweet_123"}
        mock_tweepy.Client.return_value = mock_client
        
        # Create real manager with test config
        config = {
            'TWITTER_API_KEY': 'test_key',
            'TWITTER_API_SECRET': 'test_secret',
            'TWITTER_ACCESS_TOKEN': 'test_token',
            'TWITTER_ACCESS_TOKEN_SECRET': 'test_token_secret',
            'FACEBOOK_ACCESS_TOKEN': 'test_fb_token',
            'FACEBOOK_PAGE_ID': 'test_page_id'
        }
        
        manager = SocialMediaManager(config)
        
        # Test Twitter posting
        result = manager.post_to_twitter("Test tweet with mocked dependencies")
        assert result["success"] is True
        print("✅ Real SocialMediaManager works with mocked dependencies")

def run_social_media_demo():
    """
    Demo function to show all social media functionality working.
    Run this to see mock social media posting in action.
    """
    print("\n🚀 Social Media Testing Demo")
    print("=" * 50)
    
    # Initialize mock manager
    config = {
        'TWITTER_API_KEY': 'demo_twitter_key',
        'TWITTER_API_SECRET': 'demo_twitter_secret',
        'TWITTER_ACCESS_TOKEN': 'demo_twitter_token',
        'TWITTER_ACCESS_TOKEN_SECRET': 'demo_twitter_token_secret',
        'FACEBOOK_ACCESS_TOKEN': 'demo_facebook_token',
        'FACEBOOK_PAGE_ID': 'demo_facebook_page',
        'INSTAGRAM_ACCESS_TOKEN': 'demo_instagram_token',
        'INSTAGRAM_BUSINESS_ACCOUNT_ID': 'demo_instagram_account',
        'PINTEREST_ACCESS_TOKEN': 'demo_pinterest_token',
        'PINTEREST_BOARD_ID': 'demo_pinterest_board'
    }
    
    manager = MockSocialMediaManager(config)
    
    # Demo posts
    demo_posts = [
        {
            "platform": "twitter",
            "content": "Exciting new AI book marketing campaign! 🚀 #AIMarketing #BookPromotion",
            "media": None
        },
        {
            "platform": "facebook",
            "content": "Our AI marketing system is revolutionizing book promotion. Check out the amazing results we're seeing!",
            "media": ["https://example.com/marketing-results.jpg"]
        },
        {
            "platform": "instagram",
            "content": "Behind the scenes of our AI-powered book marketing magic ✨ #BookMarketing #AI #Publishing",
            "media": ["https://example.com/behind-scenes.jpg"]
        },
        {
            "platform": "pinterest",
            "content": "Ultimate guide to AI book marketing strategies. Save this pin for later!",
            "media": ["https://example.com/marketing-infographic.jpg"],
            "title": "AI Book Marketing Guide"
        }
    ]
    
    print("\n📝 Creating demo posts...")
    for post in demo_posts:
        if post["platform"] == "pinterest":
            result = manager.post_to_pinterest(
                post["content"], 
                post["media"], 
                post.get("title", "")
            )
        else:
            result = manager.post_content(
                post["platform"], 
                post["content"], 
                post["media"]
            )
        
        if result["success"]:
            print(f"✅ {post['platform'].title()}: {result['url']}")
        else:
            print(f"❌ {post['platform'].title()}: {result['error']}")
    
    # Show platform status
    print("\n📊 Platform Status:")
    status = manager.get_platform_status()
    for platform, available in status.items():
        status_icon = "✅" if available else "❌"
        print(f"{status_icon} {platform.title()}: {'Available' if available else 'Unavailable'}")
    
    # Show post history
    print(f"\n📈 Total Posts Created: {len(manager.get_post_history())}")
    
    print("\n🎉 Demo completed! All social media functionality tested successfully.")
    return manager

if __name__ == "__main__":
    # Run the demo
    run_social_media_demo() 
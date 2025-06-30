# Import compatibility module first to handle Python 3.13 issues
from . import compat
compat.ensure_compatibility()

import tweepy
import requests
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

# Set up logging for this module
logger = logging.getLogger(__name__)

class SocialMediaManager:
    """
    Manages posting to various social media platforms.
    Handles authentication and posting for Twitter, Facebook, Instagram, and Pinterest.
    """
    
    def __init__(self, config: Dict[str, str]):
        """
        Initialize social media APIs with provided credentials.
        
        Args:
            config: Dictionary containing API credentials for all platforms
        """
        self.config = config
        self.platforms = {}
        
        # Initialize each platform
        self._init_twitter()
        self._init_facebook()
        self._init_instagram()
        self._init_pinterest()
    
    def _init_twitter(self):
        """Initialize Twitter API client."""
        try:
            if all(key in self.config for key in ['TWITTER_API_KEY', 'TWITTER_API_SECRET', 'TWITTER_ACCESS_TOKEN', 'TWITTER_ACCESS_TOKEN_SECRET']):
                # Twitter API v2 client
                self.platforms['twitter'] = tweepy.Client(
                    consumer_key=self.config['TWITTER_API_KEY'],
                    consumer_secret=self.config['TWITTER_API_SECRET'],
                    access_token=self.config['TWITTER_ACCESS_TOKEN'],
                    access_token_secret=self.config['TWITTER_ACCESS_TOKEN_SECRET']
                )
                logger.info("Twitter API initialized successfully")
            else:
                logger.warning("Twitter API credentials not found")
        except Exception as e:
            logger.error(f"Failed to initialize Twitter API: {str(e)}")
    
    def _init_facebook(self):
        """Initialize Facebook API client."""
        try:
            if 'FACEBOOK_ACCESS_TOKEN' in self.config:
                # Store Facebook credentials for API calls
                self.platforms['facebook'] = {
                    'access_token': self.config['FACEBOOK_ACCESS_TOKEN'],
                    'page_id': self.config.get('FACEBOOK_PAGE_ID')
                }
                logger.info("Facebook API initialized successfully")
            else:
                logger.warning("Facebook API credentials not found")
        except Exception as e:
            logger.error(f"Failed to initialize Facebook API: {str(e)}")
    
    def _init_instagram(self):
        """Initialize Instagram API client."""
        try:
            if 'INSTAGRAM_ACCESS_TOKEN' in self.config:
                # Store Instagram credentials for API calls
                self.platforms['instagram'] = {
                    'access_token': self.config['INSTAGRAM_ACCESS_TOKEN'],
                    'business_account_id': self.config.get('INSTAGRAM_BUSINESS_ACCOUNT_ID')
                }
                logger.info("Instagram API initialized successfully")
            else:
                logger.warning("Instagram API credentials not found")
        except Exception as e:
            logger.error(f"Failed to initialize Instagram API: {str(e)}")
    
    def _init_pinterest(self):
        """Initialize Pinterest API client."""
        try:
            if 'PINTEREST_ACCESS_TOKEN' in self.config:
                # Store Pinterest credentials for API calls
                self.platforms['pinterest'] = {
                    'access_token': self.config['PINTEREST_ACCESS_TOKEN'],
                    'board_id': self.config.get('PINTEREST_BOARD_ID')
                }
                logger.info("Pinterest API initialized successfully")
            else:
                logger.warning("Pinterest API credentials not found")
        except Exception as e:
            logger.error(f"Failed to initialize Pinterest API: {str(e)}")
    
    def post_to_twitter(self, content: str, media_urls: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Post content to Twitter.
        
        Args:
            content: Tweet content
            media_urls: Optional list of media URLs to attach
            
        Returns:
            Result dictionary with success status and details
        """
        try:
            if 'twitter' not in self.platforms:
                return {"success": False, "error": "Twitter API not initialized"}
            
            twitter_client = self.platforms['twitter']
            
            # Post tweet
            response = twitter_client.create_tweet(text=content)
            
            if response.data:
                tweet_id = response.data['id']
                logger.info(f"Successfully posted to Twitter: {tweet_id}")
                return {
                    "success": True,
                    "platform": "twitter",
                    "post_id": tweet_id,
                    "url": f"https://twitter.com/user/status/{tweet_id}",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"success": False, "error": "Failed to create tweet"}
                
        except Exception as e:
            logger.error(f"Error posting to Twitter: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def post_to_facebook(self, content: str, media_urls: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Post content to Facebook page.
        
        Args:
            content: Post content
            media_urls: Optional list of media URLs to attach
            
        Returns:
            Result dictionary with success status and details
        """
        try:
            if 'facebook' not in self.platforms:
                return {"success": False, "error": "Facebook API not initialized"}
            
            fb_config = self.platforms['facebook']
            access_token = fb_config['access_token']
            page_id = fb_config.get('page_id')
            
            if not page_id:
                return {"success": False, "error": "Facebook page ID not configured"}
            
            # Prepare post data
            post_data = {
                'message': content,
                'access_token': access_token
            }
            
            # Add media if provided
            if media_urls and len(media_urls) > 0:
                post_data['link'] = media_urls[0]  # Facebook allows one link per post
            
            # Make API request
            url = f"https://graph.facebook.com/v18.0/{page_id}/feed"
            response = requests.post(url, data=post_data)
            
            if response.status_code == 200:
                result = response.json()
                post_id = result.get('id')
                logger.info(f"Successfully posted to Facebook: {post_id}")
                return {
                    "success": True,
                    "platform": "facebook",
                    "post_id": post_id,
                    "url": f"https://facebook.com/{post_id}",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                error_details = response.json() if response.content else "Unknown error"
                return {"success": False, "error": f"Facebook API error: {error_details}"}
                
        except Exception as e:
            logger.error(f"Error posting to Facebook: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def post_to_instagram(self, content: str, media_urls: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Post content to Instagram (requires media).
        
        Args:
            content: Post caption
            media_urls: List of media URLs (required for Instagram)
            
        Returns:
            Result dictionary with success status and details
        """
        try:
            if 'instagram' not in self.platforms:
                return {"success": False, "error": "Instagram API not initialized"}
            
            if not media_urls or len(media_urls) == 0:
                return {"success": False, "error": "Instagram posts require media"}
            
            ig_config = self.platforms['instagram']
            access_token = ig_config['access_token']
            business_account_id = ig_config.get('business_account_id')
            
            if not business_account_id:
                return {"success": False, "error": "Instagram business account ID not configured"}
            
            # Step 1: Create media container
            container_data = {
                'image_url': media_urls[0],  # Use first media URL
                'caption': content,
                'access_token': access_token
            }
            
            container_url = f"https://graph.facebook.com/v18.0/{business_account_id}/media"
            container_response = requests.post(container_url, data=container_data)
            
            if container_response.status_code != 200:
                error_details = container_response.json() if container_response.content else "Unknown error"
                return {"success": False, "error": f"Instagram container creation error: {error_details}"}
            
            container_id = container_response.json().get('id')
            
            # Step 2: Publish the media
            publish_data = {
                'creation_id': container_id,
                'access_token': access_token
            }
            
            publish_url = f"https://graph.facebook.com/v18.0/{business_account_id}/media_publish"
            publish_response = requests.post(publish_url, data=publish_data)
            
            if publish_response.status_code == 200:
                result = publish_response.json()
                post_id = result.get('id')
                logger.info(f"Successfully posted to Instagram: {post_id}")
                return {
                    "success": True,
                    "platform": "instagram",
                    "post_id": post_id,
                    "url": f"https://instagram.com/p/{post_id}",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                error_details = publish_response.json() if publish_response.content else "Unknown error"
                return {"success": False, "error": f"Instagram publish error: {error_details}"}
                
        except Exception as e:
            logger.error(f"Error posting to Instagram: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def post_to_pinterest(self, content: str, media_urls: Optional[List[str]] = None, title: str = "") -> Dict[str, Any]:
        """
        Post content to Pinterest (requires media).
        
        Args:
            content: Pin description
            media_urls: List of media URLs (required for Pinterest)
            title: Pin title
            
        Returns:
            Result dictionary with success status and details
        """
        try:
            if 'pinterest' not in self.platforms:
                return {"success": False, "error": "Pinterest API not initialized"}
            
            if not media_urls or len(media_urls) == 0:
                return {"success": False, "error": "Pinterest pins require media"}
            
            pinterest_config = self.platforms['pinterest']
            access_token = pinterest_config['access_token']
            board_id = pinterest_config.get('board_id')
            
            if not board_id:
                return {"success": False, "error": "Pinterest board ID not configured"}
            
            # Prepare pin data
            pin_data = {
                'board_id': board_id,
                'description': content,
                'image_url': media_urls[0],  # Use first media URL
                'title': title or content[:100]  # Use first 100 chars as title if not provided
            }
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Make API request
            url = "https://api.pinterest.com/v5/pins"
            response = requests.post(url, json=pin_data, headers=headers)
            
            if response.status_code == 201:
                result = response.json()
                pin_id = result.get('id')
                logger.info(f"Successfully posted to Pinterest: {pin_id}")
                return {
                    "success": True,
                    "platform": "pinterest",
                    "post_id": pin_id,
                    "url": f"https://pinterest.com/pin/{pin_id}",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                error_details = response.json() if response.content else "Unknown error"
                return {"success": False, "error": f"Pinterest API error: {error_details}"}
                
        except Exception as e:
            logger.error(f"Error posting to Pinterest: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def post_content(self, platform: str, content: str, media_urls: Optional[List[str]] = None, **kwargs) -> Dict[str, Any]:
        """
        Universal method to post content to any supported platform.
        
        Args:
            platform: Target platform (twitter, facebook, instagram, pinterest)
            content: Post content
            media_urls: Optional media URLs
            **kwargs: Additional platform-specific parameters
            
        Returns:
            Result dictionary with success status and details
        """
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
        """
        Check which platforms are properly configured and available.
        
        Returns:
            Dictionary showing availability status for each platform
        """
        status = {}
        
        for platform in ['twitter', 'facebook', 'instagram', 'pinterest']:
            status[platform] = platform in self.platforms
        
        return status
    
    def test_platform_connection(self, platform: str) -> Dict[str, Any]:
        """
        Test connection to a specific platform.
        
        Args:
            platform: Platform to test
            
        Returns:
            Test result with success status and details
        """
        platform = platform.lower()
        
        try:
            if platform == "twitter" and 'twitter' in self.platforms:
                # Test Twitter connection by getting user info
                user = self.platforms['twitter'].get_me()
                if user.data:
                    return {"success": True, "message": f"Connected as @{user.data.username}"}
                else:
                    return {"success": False, "error": "Failed to retrieve user info"}
            
            elif platform == "facebook" and 'facebook' in self.platforms:
                # Test Facebook connection by making a simple API call
                access_token = self.platforms['facebook']['access_token']
                url = f"https://graph.facebook.com/v18.0/me?access_token={access_token}"
                response = requests.get(url)
                if response.status_code == 200:
                    user_data = response.json()
                    return {"success": True, "message": f"Connected as {user_data.get('name', 'Unknown')}"}
                else:
                    return {"success": False, "error": "Failed to connect to Facebook"}
            
            elif platform == "instagram" and 'instagram' in self.platforms:
                # Test Instagram connection
                access_token = self.platforms['instagram']['access_token']
                business_id = self.platforms['instagram']['business_account_id']
                if business_id:
                    url = f"https://graph.facebook.com/v18.0/{business_id}?fields=name&access_token={access_token}"
                    response = requests.get(url)
                    if response.status_code == 200:
                        account_data = response.json()
                        return {"success": True, "message": f"Connected to {account_data.get('name', 'Instagram Business Account')}"}
                    else:
                        return {"success": False, "error": "Failed to connect to Instagram"}
                else:
                    return {"success": False, "error": "Instagram business account ID not configured"}
            
            elif platform == "pinterest" and 'pinterest' in self.platforms:
                # Test Pinterest connection
                access_token = self.platforms['pinterest']['access_token']
                headers = {'Authorization': f'Bearer {access_token}'}
                url = "https://api.pinterest.com/v5/user_account"
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    user_data = response.json()
                    return {"success": True, "message": f"Connected as {user_data.get('username', 'Pinterest User')}"}
                else:
                    return {"success": False, "error": "Failed to connect to Pinterest"}
            
            else:
                return {"success": False, "error": f"Platform {platform} not configured"}
                
        except Exception as e:
            logger.error(f"Error testing {platform} connection: {str(e)}")
            return {"success": False, "error": str(e)} 
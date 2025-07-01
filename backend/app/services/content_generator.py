import openai
import logging
import json
import random
from typing import Dict, List, Optional, Any
from datetime import datetime

# Set up logging for this module
logger = logging.getLogger(__name__)

class ContentGenerator:
    """
    AI-powered content generation service for book marketing.
    Uses OpenAI GPT models to create engaging social media posts.
    
    Now supports dynamic configuration loading per user instead of static API keys.
    """
    
    def __init__(self, api_key: str = None, model: str = "gpt-4", config_loader=None):
        """
        Initialize the content generator with optional OpenAI API.
        
        Args:
            api_key: Default OpenAI API key (fallback)
            model: Default OpenAI model to use
            config_loader: ConfigLoader instance for dynamic user configuration
        """
        self.default_api_key = api_key
        self.default_model = model
        self.config_loader = config_loader
        
        # Initialize default client if API key is provided
        if api_key:
            self.default_client = openai.OpenAI(api_key=api_key)
        else:
            self.default_client = None
        
        # Book-specific information for "Unstoppable"
        self.book_context = {
            "title": "Unstoppable - The Young Athlete's Guide to Rock Solid Mental Strength",
            "target_audience": ["youth athletes", "parents of young athletes", "coaches", "sports psychology enthusiasts"],
            "key_themes": [
                "mental strength", "resilience", "youth sports", "performance psychology",
                "confidence building", "overcoming adversity", "sports mindset", "peak performance"
            ],
            "benefits": [
                "Build unshakeable confidence",
                "Develop mental toughness",
                "Overcome performance anxiety",
                "Handle pressure situations",
                "Bounce back from setbacks",
                "Maintain focus during competition"
            ]
        }
        
        # Platform-specific content guidelines
        self.platform_guidelines = {
            "twitter": {
                "max_length": 280,
                "style": "concise, impactful, use relevant hashtags",
                "features": ["hashtags", "mentions", "threads"]
            },
            "facebook": {
                "max_length": 2000,
                "style": "engaging, storytelling, community-focused",
                "features": ["longer posts", "questions", "emotional connection"]
            },
            "instagram": {
                "max_length": 2200,
                "style": "visual-focused, inspirational, behind-the-scenes",
                "features": ["hashtags", "visual content", "stories"]
            },
            "pinterest": {
                "max_length": 500,
                "style": "inspirational, actionable, quote-focused",
                "features": ["quotes", "tips", "infographics"]
            }
        }
    
    def _get_openai_client_for_user(self, user_id: str, app_id: str = None) -> openai.OpenAI:
        """
        Get OpenAI client configured for a specific user.
        
        Args:
            user_id: User ID to get configuration for
            app_id: Application ID (optional)
            
        Returns:
            OpenAI client configured with user's API key
            
        Raises:
            ValueError: If no valid API key is found
        """
        # Try to get user-specific configuration first
        if self.config_loader:
            try:
                openai_config = self.config_loader.get_openai_config(user_id, app_id)
                user_api_key = openai_config.get("apiKey")
                
                if user_api_key and user_api_key.strip():
                    logger.debug(f"Using user-specific OpenAI API key for user {user_id}")
                    return openai.OpenAI(api_key=user_api_key)
                    
            except Exception as e:
                logger.warning(f"Error loading user OpenAI config: {str(e)}")
        
        # Fall back to default client
        if self.default_client:
            logger.debug(f"Using default OpenAI API key for user {user_id}")
            return self.default_client
        
        # No valid API key found
        raise ValueError(f"No OpenAI API key configured for user {user_id} and no default key available")
    
    def _get_model_for_user(self, user_id: str, app_id: str = None) -> str:
        """
        Get OpenAI model preference for a specific user.
        
        Args:
            user_id: User ID to get configuration for
            app_id: Application ID (optional)
            
        Returns:
            Model name to use
        """
        # Try to get user-specific configuration first
        if self.config_loader:
            try:
                openai_config = self.config_loader.get_openai_config(user_id, app_id)
                user_model = openai_config.get("model")
                
                if user_model and user_model.strip():
                    return user_model
                    
            except Exception as e:
                logger.warning(f"Error loading user model config: {str(e)}")
        
        # Fall back to default model
        return self.default_model
    
    def generate_post(self, platform: str, user_settings: Dict[str, Any], post_type: str = "general", user_id: str = None, app_id: str = None) -> Dict[str, Any]:
        """
        Generate a social media post for the specified platform.
        
        Args:
            platform: Target social media platform (twitter, facebook, instagram, pinterest)
            user_settings: User configuration and preferences
            post_type: Type of post (general, quote, tip, story, etc.)
            user_id: User ID for dynamic configuration loading
            app_id: Application ID (optional)
            
        Returns:
            Dictionary containing generated post data
        """
        try:
            # Get user-specific OpenAI client and model
            if user_id:
                client = self._get_openai_client_for_user(user_id, app_id)
                model = self._get_model_for_user(user_id, app_id)
            else:
                # Fallback for backwards compatibility
                if not self.default_client:
                    raise ValueError("No OpenAI client available and no user_id provided")
                client = self.default_client
                model = self.default_model
            
            # Get platform-specific guidelines
            guidelines = self.platform_guidelines.get(platform, self.platform_guidelines["twitter"])
            
            # Create the prompt for content generation
            prompt = self._create_prompt(platform, user_settings, post_type, guidelines, user_id, app_id)
            
            # Generate content using OpenAI
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt(user_id, app_id)
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.8,  # Higher creativity for marketing content
                max_tokens=500
            )
            
            # Parse the generated content
            generated_content = response.choices[0].message.content.strip()
            
            # Structure the post data
            post_data = {
                "platform": platform,
                "content": generated_content,
                "post_type": post_type,
                "status": "pending_approval",
                "generated_by": "ai",
                "book_title": self._get_book_title(user_id, app_id),
                "target_audience": self._determine_target_audience(generated_content),
                "estimated_engagement": self._estimate_engagement_score(generated_content, platform),
                "content_length": len(generated_content),
                "hashtags": self._extract_hashtags(generated_content),
                "calls_to_action": self._extract_cta(generated_content, user_settings),
                "generation_metadata": {
                    "model": model,
                    "timestamp": datetime.now().isoformat(),
                    "prompt_type": post_type,
                    "user_guidelines": user_settings.get("contentGuidelines", ""),
                    "user_id": user_id,
                    "app_id": app_id
                }
            }
            
            logger.info(f"Generated {platform} post of type {post_type} for user {user_id}")
            return post_data
            
        except Exception as e:
            logger.error(f"Error generating content for user {user_id}: {str(e)}")
            raise
    
    def _get_book_title(self, user_id: str = None, app_id: str = None) -> str:
        """Get book title from user configuration or default."""
        if user_id and self.config_loader:
            try:
                book_config = self.config_loader.get_book_config(user_id, app_id)
                return book_config.get("title", self.book_context["title"])
            except:
                pass
        return self.book_context["title"]
    
    def _get_system_prompt(self, user_id: str = None, app_id: str = None) -> str:
        """
        Get the system prompt that defines the AI's role and behavior.
        Can be customized per user in the future.
        """
        # Get user-specific book information if available
        book_title = self._get_book_title(user_id, app_id)
        
        return f"""You are an expert marketing AI specialized in promoting books, specifically "{book_title}". Your goal is to create compelling social media content that drives book sales by targeting youth athletes, their parents, and coaches.

Key Guidelines:
- Always keep the target audience in mind (youth athletes, parents, coaches)
- Focus on mental strength, resilience, and peak performance themes
- Create emotionally resonant content that motivates action
- Include clear calls-to-action when appropriate
- Stay authentic and avoid overly salesy language
- Use sports psychology concepts and real-world athletic scenarios
- Emphasize practical benefits and transformation outcomes

Remember: Every post should ultimately drive toward book sales while providing genuine value to the audience."""
    
    def _create_prompt(self, platform: str, user_settings: Dict[str, Any], post_type: str, guidelines: Dict[str, Any], user_id: str = None, app_id: str = None) -> str:
        """
        Create a detailed prompt for content generation.
        """
        # Get user-specific book and configuration data
        if user_id and self.config_loader:
            try:
                book_config = self.config_loader.get_book_config(user_id, app_id)
                book_title = book_config.get("title", self.book_context["title"])
                landing_page = book_config.get("landingPageUrl", "")
                primary_audience = book_config.get("primaryAudience", ", ".join(self.book_context["target_audience"]))
            except:
                book_title = self.book_context["title"]
                landing_page = ""
                primary_audience = ", ".join(self.book_context["target_audience"])
        else:
            book_title = user_settings.get("bookTitle", self.book_context["title"])
            landing_page = user_settings.get("landingPageUrl", "")
            primary_audience = ", ".join(self.book_context["target_audience"])
        
        author = user_settings.get("bookAuthor", "Author Name")
        content_guidelines = user_settings.get("contentGuidelines", "")
        
        prompt = f"""Create a {platform} post for the book "{book_title}" by {author}.

Platform: {platform}
Post Type: {post_type}
Max Length: {guidelines['max_length']} characters
Style: {guidelines['style']}

Book Context:
- Target Audience: {primary_audience}
- Key Themes: {', '.join(self.book_context['key_themes'])}
- Key Benefits: {', '.join(self.book_context['benefits'])}

User Guidelines: {content_guidelines}

Landing Page: {landing_page}

Requirements:
1. Create engaging content that resonates with young athletes, parents, or coaches
2. Include practical value or inspiration related to mental strength
3. Stay within character limits
4. Include relevant hashtags (3-5 for Twitter, 5-10 for Instagram)
5. Include a subtle call-to-action that encourages book purchase
6. Make it feel authentic, not overly promotional
7. Focus on transformation and results

Generate only the post content, no additional commentary."""
        
        return prompt
    
    def _determine_target_audience(self, content: str) -> str:
        """
        Analyze content to determine primary target audience.
        """
        content_lower = content.lower()
        
        if any(word in content_lower for word in ["parent", "parents", "mom", "dad"]):
            return "parents"
        elif any(word in content_lower for word in ["coach", "coaches", "coaching"]):
            return "coaches"
        elif any(word in content_lower for word in ["athlete", "player", "young", "teen"]):
            return "youth_athletes"
        else:
            return "general"
    
    def _estimate_engagement_score(self, content: str, platform: str) -> float:
        """
        Estimate engagement score based on content characteristics.
        """
        score = 5.0  # Base score
        
        # Check for engagement-boosting elements
        if "?" in content:  # Questions increase engagement
            score += 1.0
        
        if any(word in content.lower() for word in ["you", "your", "yourself"]):
            score += 0.5  # Personal pronouns increase engagement
        
        if "#" in content:  # Hashtags help discoverability
            hashtag_count = content.count("#")
            score += min(hashtag_count * 0.3, 2.0)
        
        if any(word in content.lower() for word in ["free", "tip", "secret", "proven"]):
            score += 0.5  # Value words increase engagement
        
        # Platform-specific adjustments
        if platform == "instagram" and len(content) > 300:
            score += 0.5  # Longer content performs well on Instagram
        elif platform == "twitter" and len(content) < 200:
            score += 0.5  # Concise content performs well on Twitter
        
        return min(score, 10.0)  # Cap at 10.0
    
    def _extract_hashtags(self, content: str) -> List[str]:
        """
        Extract hashtags from generated content.
        """
        import re
        hashtags = re.findall(r'#\w+', content)
        return hashtags
    
    def _extract_cta(self, content: str, user_settings: Dict[str, Any]) -> List[str]:
        """
        Identify calls-to-action in the content.
        """
        cta_phrases = []
        content_lower = content.lower()
        
        # Common CTA patterns
        cta_patterns = [
            "buy now", "get the book", "order today", "available now",
            "learn more", "read more", "check it out", "grab your copy",
            "click link", "visit", "download", "purchase"
        ]
        
        for pattern in cta_patterns:
            if pattern in content_lower:
                cta_phrases.append(pattern)
        
        return cta_phrases
    
    def generate_content_batch(self, platforms: List[str], user_settings: Dict[str, Any], count_per_platform: int = 1, user_id: str = None, app_id: str = None) -> List[Dict[str, Any]]:
        """
        Generate multiple posts across different platforms.
        
        Args:
            platforms: List of platforms to generate content for
            user_settings: User configuration and preferences
            count_per_platform: Number of posts to generate per platform
            user_id: User ID for dynamic configuration loading
            app_id: Application ID (optional)
            
        Returns:
            List of generated post data dictionaries
        """
        all_posts = []
        
        post_types = ["general", "quote", "tip", "story", "question"]
        
        for platform in platforms:
            for i in range(count_per_platform):
                try:
                    # Vary post types for diversity
                    post_type = random.choice(post_types)
                    
                    post_data = self.generate_post(
                        platform, user_settings, post_type, user_id, app_id
                    )
                    all_posts.append(post_data)
                    
                except Exception as e:
                    logger.error(f"Error generating {platform} post {i+1}: {str(e)}")
                    continue
        
        logger.info(f"Generated {len(all_posts)} posts across {len(platforms)} platforms for user {user_id}")
        return all_posts
    
    def validate_content(self, content: str, platform: str) -> Dict[str, Any]:
        """
        Validate generated content against platform requirements.
        
        Args:
            content: Generated content text
            platform: Target platform
            
        Returns:
            Validation results dictionary
        """
        guidelines = self.platform_guidelines.get(platform, self.platform_guidelines["twitter"])
        
        validation = {
            "valid": True,
            "warnings": [],
            "errors": []
        }
        
        # Check length constraints
        if len(content) > guidelines["max_length"]:
            validation["valid"] = False
            validation["errors"].append(f"Content exceeds {guidelines['max_length']} character limit for {platform}")
        
        # Check for required elements
        if platform in ["twitter", "instagram"] and "#" not in content:
            validation["warnings"].append(f"No hashtags found - recommended for {platform}")
        
        # Check for CTA
        if not any(cta in content.lower() for cta in ["buy", "get", "learn", "check", "visit", "read"]):
            validation["warnings"].append("No clear call-to-action found")
        
        return validation 
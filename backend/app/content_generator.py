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
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        """
        Initialize the content generator with OpenAI API.
        
        Args:
            api_key: OpenAI API key
            model: OpenAI model to use (default: gpt-4)
        """
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        
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
    
    def generate_post(self, platform: str, user_settings: Dict[str, Any], post_type: str = "general") -> Dict[str, Any]:
        """
        Generate a social media post for the specified platform.
        
        Args:
            platform: Target social media platform (twitter, facebook, instagram, pinterest)
            user_settings: User configuration and preferences
            post_type: Type of post (general, quote, tip, story, etc.)
            
        Returns:
            Dictionary containing generated post data
        """
        try:
            # Get platform-specific guidelines
            guidelines = self.platform_guidelines.get(platform, self.platform_guidelines["twitter"])
            
            # Create the prompt for content generation
            prompt = self._create_prompt(platform, user_settings, post_type, guidelines)
            
            # Generate content using OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
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
                "book_title": user_settings.get("bookTitle", self.book_context["title"]),
                "target_audience": self._determine_target_audience(generated_content),
                "estimated_engagement": self._estimate_engagement_score(generated_content, platform),
                "content_length": len(generated_content),
                "hashtags": self._extract_hashtags(generated_content),
                "calls_to_action": self._extract_cta(generated_content, user_settings),
                "generation_metadata": {
                    "model": self.model,
                    "timestamp": datetime.now().isoformat(),
                    "prompt_type": post_type,
                    "user_guidelines": user_settings.get("contentGuidelines", "")
                }
            }
            
            logger.info(f"Generated {platform} post of type {post_type}")
            return post_data
            
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            raise
    
    def _get_system_prompt(self) -> str:
        """
        Get the system prompt that defines the AI's role and behavior.
        """
        return """You are an expert marketing AI specialized in promoting books, specifically "Unstoppable - The Young Athlete's Guide to Rock Solid Mental Strength". Your goal is to create compelling social media content that drives book sales by targeting youth athletes, their parents, and coaches.

Key Guidelines:
- Always keep the target audience in mind (youth athletes, parents, coaches)
- Focus on mental strength, resilience, and peak performance themes
- Create emotionally resonant content that motivates action
- Include clear calls-to-action when appropriate
- Stay authentic and avoid overly salesy language
- Use sports psychology concepts and real-world athletic scenarios
- Emphasize practical benefits and transformation outcomes

Remember: Every post should ultimately drive toward book sales while providing genuine value to the audience."""
    
    def _create_prompt(self, platform: str, user_settings: Dict[str, Any], post_type: str, guidelines: Dict[str, Any]) -> str:
        """
        Create a detailed prompt for content generation.
        """
        book_title = user_settings.get("bookTitle", self.book_context["title"])
        author = user_settings.get("bookAuthor", "Author Name")
        landing_page = user_settings.get("landingPageUrl", "")
        content_guidelines = user_settings.get("contentGuidelines", "")
        
        prompt = f"""Create a {platform} post for the book "{book_title}" by {author}.

Platform: {platform}
Post Type: {post_type}
Max Length: {guidelines['max_length']} characters
Style: {guidelines['style']}

Book Context:
- Target Audience: {', '.join(self.book_context['target_audience'])}
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
        
        common_ctas = [
            "get the book", "buy now", "order today", "learn more",
            "check it out", "grab your copy", "available now",
            "link in bio", "visit", "click"
        ]
        
        for cta in common_ctas:
            if cta in content_lower:
                cta_phrases.append(cta)
        
        return cta_phrases
    
    def generate_content_batch(self, platforms: List[str], user_settings: Dict[str, Any], count_per_platform: int = 1) -> List[Dict[str, Any]]:
        """
        Generate multiple posts across different platforms.
        
        Args:
            platforms: List of platforms to generate content for
            user_settings: User configuration
            count_per_platform: Number of posts to generate per platform
            
        Returns:
            List of generated post data
        """
        all_posts = []
        
        post_types = ["general", "quote", "tip", "story", "motivation"]
        
        for platform in platforms:
            for i in range(count_per_platform):
                try:
                    # Vary post types for diversity
                    post_type = random.choice(post_types)
                    post_data = self.generate_post(platform, user_settings, post_type)
                    all_posts.append(post_data)
                    
                except Exception as e:
                    logger.error(f"Error generating post {i+1} for {platform}: {str(e)}")
                    continue
        
        logger.info(f"Generated {len(all_posts)} posts across {len(platforms)} platforms")
        return all_posts
    
    def validate_content(self, content: str, platform: str) -> Dict[str, Any]:
        """
        Validate generated content against platform guidelines and policies.
        
        Args:
            content: Generated content to validate
            platform: Target platform
            
        Returns:
            Validation results with issues and suggestions
        """
        issues = []
        suggestions = []
        
        guidelines = self.platform_guidelines.get(platform, self.platform_guidelines["twitter"])
        
        # Check length
        if len(content) > guidelines["max_length"]:
            issues.append(f"Content exceeds {platform} character limit ({len(content)}/{guidelines['max_length']})")
            suggestions.append("Consider shortening the content or splitting into multiple posts")
        
        # Check for required elements
        if platform in ["twitter", "instagram"] and "#" not in content:
            suggestions.append("Consider adding relevant hashtags for better discoverability")
        
        # Check for call-to-action
        if not any(word in content.lower() for word in ["book", "learn", "get", "check", "visit"]):
            suggestions.append("Consider adding a subtle call-to-action")
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions,
            "character_count": len(content),
            "estimated_engagement": self._estimate_engagement_score(content, platform)
        } 
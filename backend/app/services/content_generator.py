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
    Now supports image generation with DALL-E for Instagram posts.
    
    Supports dynamic configuration loading per user instead of static API keys.
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
        
        # Book context for content generation
        self.book_context = {
            "title": "Unstoppable: Mental Strength for Young Athletes",
            "genre": "Sports Psychology",
            "target_audience": "youth athletes, parents, coaches",
            "key_themes": ["mental strength", "resilience", "confidence", "peak performance"],
            "benefits": ["overcome pressure", "build confidence", "develop focus", "handle setbacks"],
            "tone": "motivational and practical"
        }
        
        # Platform-specific posting guidelines
        self.platform_guidelines = {
            "twitter": {
                "max_length": 280,
                "style": "concise and impactful",
                "hashtags": "3-5",
                "best_times": ["9am", "3pm", "7pm"],
                "content_types": ["tips", "quotes", "questions", "threads"]
            },
            "facebook": {
                "max_length": 2000,
                "style": "conversational and detailed",
                "hashtags": "2-3",
                "best_times": ["6am-9am", "7pm-9pm"],
                "content_types": ["stories", "tips", "discussions", "videos"]
            },
            "instagram": {
                "max_length": 2200,
                "style": "visual-first with engaging captions",
                "hashtags": "8-15",
                "best_times": ["11am-1pm", "5pm-7pm"],
                "content_types": ["quotes", "tips", "behind_scenes", "user_generated"],
                "requires_image": True
            },
            "pinterest": {
                "max_length": 500,
                "style": "descriptive and keyword-rich",
                "hashtags": "10-20",
                "best_times": ["8pm-11pm"],
                "content_types": ["infographics", "guides", "inspiration"]
            }
        }
        
        # Enhanced post types for more variety
        self.post_types = [
            "motivational_quote",
            "practical_tip", 
            "success_story",
            "challenge_question",
            "behind_scenes",
            "testimonial",
            "quick_tip",
            "myth_buster",
            "weekly_wisdom",
            "coach_corner",
            "parent_perspective",
            "athlete_spotlight"
        ]
    
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
        Now supports image generation for Instagram posts.
        
        Args:
            platform: Target social media platform (twitter, facebook, instagram, pinterest)
            user_settings: User configuration and preferences
            post_type: Type of post (general, quote, tip, story, etc.)
            user_id: User ID for dynamic configuration loading
            app_id: Application ID (optional)
            
        Returns:
            Dictionary containing generated post data with optional image for Instagram
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
            
            # If post_type is "general", randomly select a more specific type for variety
            if post_type == "general":
                post_type = random.choice(self.post_types)
            
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
            
            # Generate image for Instagram posts
            image_url = None
            if platform.lower() == "instagram":
                logger.info(f"Generating image for Instagram post for user {user_id}")
                image_url = self.generate_instagram_image(generated_content, user_id, app_id)
                if image_url:
                    logger.info(f"Successfully generated Instagram image for user {user_id}")
                else:
                    logger.warning(f"Failed to generate Instagram image for user {user_id}")
            
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
                "image_url": image_url,  # Include generated image URL for Instagram
                "generation_metadata": {
                    "model": model,
                    "timestamp": datetime.now().isoformat(),
                    "prompt_type": post_type,
                    "user_guidelines": user_settings.get("contentGuidelines", ""),
                    "user_id": user_id,
                    "app_id": app_id,
                    "image_generated": image_url is not None
                }
            }
            
            logger.info(f"Generated {platform} post of type {post_type} for user {user_id}" + 
                       (f" with image" if image_url else ""))
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
        Create a detailed prompt for content generation based on platform and post type.
        Enhanced to support diverse post types and engaging content creation.
        """
        # Get user-specific book information
        book_title = self._get_book_title(user_id, app_id)
        author = user_settings.get("bookAuthor", "Author")
        content_guidelines = user_settings.get("contentGuidelines", "Create engaging content")
        landing_page = user_settings.get("landingPageUrl", "")
        primary_audience = user_settings.get("targetAudience", "youth athletes, parents, and coaches")
        
        # Create post-type specific content guidelines
        post_type_prompts = {
            "motivational_quote": f"Create an inspiring quote about mental strength with a brief explanation of how it applies to young athletes.",
            "practical_tip": f"Share a specific, actionable tip that young athletes can implement immediately to improve their mental game.",
            "success_story": f"Tell a brief story about overcoming mental challenges in sports (can be fictional but realistic).",
            "challenge_question": f"Ask an engaging question that encourages reflection about mental strength and athletic performance.",
            "behind_scenes": f"Share insights into the mental preparation process that goes into athletic success.",
            "testimonial": f"Create content that highlights the transformation possible through mental strength training.",
            "quick_tip": f"Provide a rapid-fire tip that athletes can use in high-pressure moments.",
            "myth_buster": f"Address a common misconception about mental toughness in youth sports.",
            "weekly_wisdom": f"Share deeper insights about developing resilience and mental strength over time.",
            "coach_corner": f"Provide advice specifically for coaches on developing their athletes' mental game.",
            "parent_perspective": f"Offer guidance for parents on supporting their young athlete's mental development.",
            "athlete_spotlight": f"Highlight the mindset and mental strategies of successful young athletes."
        }
        
        # Get specific prompt for post type
        type_specific_prompt = post_type_prompts.get(post_type, "Create engaging content about mental strength for young athletes.")
        
        # Platform-specific formatting requirements
        platform_instructions = {
            "twitter": "Use a punchy, concise tone. Include 3-5 relevant hashtags. Make every word count.",
            "facebook": "Use a conversational, storytelling approach. Include 2-3 hashtags. Encourage engagement with questions.",
            "instagram": "Create visually-focused copy that complements an image. Use 8-15 hashtags strategically. Include engaging emojis.",
            "pinterest": "Write descriptive, keyword-rich content. Use 10-20 hashtags. Focus on search discoverability."
        }
        
        platform_instruction = platform_instructions.get(platform, "Create engaging social media content.")
        
        prompt = f"""Create a {platform} post for the book "{book_title}" by {author}.

POST TYPE: {post_type}
TASK: {type_specific_prompt}

PLATFORM: {platform}
MAX LENGTH: {guidelines['max_length']} characters
STYLE: {guidelines['style']}
PLATFORM INSTRUCTION: {platform_instruction}

BOOK CONTEXT:
- Target Audience: {primary_audience}
- Key Themes: {', '.join(self.book_context['key_themes'])}
- Key Benefits: {', '.join(self.book_context['benefits'])}
- Tone: {self.book_context['tone']}

USER GUIDELINES: {content_guidelines}
LANDING PAGE: {landing_page}

CONTENT REQUIREMENTS:
1. Create authentic, valuable content that resonates with your target audience
2. Include practical value or inspiration related to mental strength in sports
3. Stay within character limits for {platform}
4. Include appropriate hashtags ({guidelines.get('hashtags', '3-5')})
5. Include a natural call-to-action that encourages book interest
6. Make it feel genuine, not overly promotional
7. Focus on transformation, results, and practical application
8. Use an encouraging, expert tone that builds trust
9. Include relevant emojis where appropriate (especially for Instagram)
10. Create content that people will want to share with others

EXAMPLE THEMES TO EXPLORE:
- Overcoming game-day nerves and pressure
- Building confidence after mistakes or losses
- Developing focus and concentration skills
- Handling criticism and feedback positively
- Setting and achieving mental performance goals
- Building resilience through challenges
- Team communication and leadership

Generate ONLY the post content with hashtags included. No additional commentary or formatting."""
        
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
        Generate multiple posts across different platforms with enhanced variety.
        Ensures good distribution of post types for diverse content.
        
        Args:
            platforms: List of target platforms
            user_settings: User configuration
            count_per_platform: Number of posts per platform
            user_id: User ID for dynamic configuration
            app_id: Application ID (optional)
            
        Returns:
            List of generated post data dictionaries
        """
        all_posts = []
        
        # Create a balanced mix of post types for variety
        available_post_types = self.post_types.copy()
        
        # Ensure we have enough variety for the total number of posts
        total_posts_needed = len(platforms) * count_per_platform
        
        # Create a balanced distribution of post types
        if total_posts_needed > len(available_post_types):
            # If we need more posts than available types, cycle through them
            post_type_cycle = []
            cycles_needed = (total_posts_needed // len(available_post_types)) + 1
            for _ in range(cycles_needed):
                shuffled_types = available_post_types.copy()
                random.shuffle(shuffled_types)
                post_type_cycle.extend(shuffled_types)
            selected_post_types = post_type_cycle[:total_posts_needed]
        else:
            # If we need fewer posts than available types, randomly select
            selected_post_types = random.sample(available_post_types, total_posts_needed)
        
        # Shuffle the selected types for random distribution
        random.shuffle(selected_post_types)
        
        post_type_index = 0
        
        for platform in platforms:
            logger.info(f"Generating {count_per_platform} posts for {platform}")
            
            for i in range(count_per_platform):
                try:
                    # Use the pre-selected post type for better variety
                    post_type = selected_post_types[post_type_index]
                    post_type_index += 1
                    
                    logger.info(f"Generating {platform} post {i+1} of type '{post_type}' for user {user_id}")
                    
                    post_data = self.generate_post(
                        platform, user_settings, post_type, user_id, app_id
                    )
                    all_posts.append(post_data)
                    
                except Exception as e:
                    logger.error(f"Error generating {platform} post {i+1} of type '{post_type}': {str(e)}")
                    continue
        
        logger.info(f"Successfully generated {len(all_posts)} posts across {len(platforms)} platforms for user {user_id}")
        
        # Log the variety of post types generated for debugging
        post_types_generated = [post.get('post_type') for post in all_posts]
        logger.info(f"Post types generated: {', '.join(post_types_generated)}")
        
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
    
    def generate_instagram_image(self, content: str, user_id: str = None, app_id: str = None) -> Optional[str]:
        """
        Generate an image for Instagram post using OpenAI's DALL-E.
        
        Args:
            content: The post content to base the image on
            user_id: User ID for dynamic configuration loading
            app_id: Application ID (optional)
            
        Returns:
            URL of the generated image or None if generation fails
        """
        try:
            # Get user-specific OpenAI client
            if user_id:
                client = self._get_openai_client_for_user(user_id, app_id)
            else:
                if not self.default_client:
                    logger.warning("No OpenAI client available for image generation")
                    return None
                client = self.default_client
            
            # Create image prompt based on content and book theme
            image_prompt = self._create_image_prompt(content, user_id, app_id)
            
            # Generate image using DALL-E 3
            response = client.images.generate(
                model="dall-e-3",
                prompt=image_prompt,
                size="1024x1024",  # Instagram square format
                quality="standard",
                n=1
            )
            
            image_url = response.data[0].url
            logger.info(f"Generated Instagram image for user {user_id}")
            return image_url
            
        except Exception as e:
            logger.error(f"Error generating Instagram image: {str(e)}")
            return None
    
    def _create_image_prompt(self, content: str, user_id: str = None, app_id: str = None) -> str:
        """
        Create a DALL-E prompt for Instagram image generation based on post content.
        
        Args:
            content: The post content
            user_id: User ID for customization
            app_id: Application ID (optional)
            
        Returns:
            Image generation prompt
        """
        # Get book title for context
        book_title = self._get_book_title(user_id, app_id)
        
        # Extract key themes from content
        content_lower = content.lower()
        
        # Determine image style based on content themes
        if any(word in content_lower for word in ["confidence", "strength", "power"]):
            style = "powerful and motivational"
            elements = "young athlete in action, confident pose, stadium background"
        elif any(word in content_lower for word in ["focus", "concentration", "mental"]):
            style = "focused and serene"
            elements = "athlete in meditation or focused preparation, clean background"
        elif any(word in content_lower for word in ["team", "coach", "training"]):
            style = "collaborative and energetic"
            elements = "coach and young athletes training together, sports equipment"
        elif any(word in content_lower for word in ["victory", "success", "champion"]):
            style = "triumphant and inspiring"
            elements = "celebrating athlete, trophy or medal, bright lighting"
        else:
            style = "inspiring and motivational"
            elements = "young athlete in sports gear, determined expression"
        
        # Create comprehensive prompt
        prompt = f"""Create a {style} Instagram image for a sports psychology book promotion. 

Image should include: {elements}

Style requirements:
- Professional photography quality
- Bright, vibrant colors
- Clean, modern aesthetic
- Inspirational and motivational mood
- Suitable for sports psychology book marketing
- Age-appropriate for youth athletes (13-18 years)
- No text or words in the image
- High contrast and Instagram-optimized
- Focus on mental strength and athletic performance themes

Technical specs: Square format, high quality, social media ready"""
        
        return prompt 
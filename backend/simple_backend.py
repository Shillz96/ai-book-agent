#!/usr/bin/env python3
"""
Simplified AI Book Marketing Agent Backend
Focuses on core post generation functionality without complex dependencies
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import logging
import json
import random
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "*"])

# Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your-openai-api-key-here')

# Enhanced post types for variety
POST_TYPES = [
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

# Platform guidelines
PLATFORM_GUIDELINES = {
    "twitter": {
        "max_length": 280,
        "style": "concise and impactful",
        "hashtags": "3-5"
    },
    "facebook": {
        "max_length": 2000,
        "style": "conversational and detailed",
        "hashtags": "2-3"
    },
    "instagram": {
        "max_length": 2200,
        "style": "visual-first with engaging captions",
        "hashtags": "8-15",
        "requires_image": True
    }
}

def create_prompt(platform, post_type, user_settings):
    """Create a prompt for content generation"""
    book_title = user_settings.get("bookTitle", "Unstoppable: Mental Strength for Young Athletes")
    author = user_settings.get("bookAuthor", "Author Name")
    audience = user_settings.get("targetAudience", "youth athletes, parents, coaches")
    
    post_type_prompts = {
        "motivational_quote": "Create an inspiring quote about mental strength with a brief explanation.",
        "practical_tip": "Share a specific, actionable tip for young athletes to improve their mental game.",
        "success_story": "Tell a brief story about overcoming mental challenges in sports.",
        "challenge_question": "Ask an engaging question about mental strength and athletic performance.",
        "behind_scenes": "Share insights into the mental preparation process for athletic success.",
        "testimonial": "Create content highlighting transformation through mental strength training.",
        "quick_tip": "Provide a rapid-fire tip for high-pressure moments.",
        "myth_buster": "Address a common misconception about mental toughness in youth sports.",
        "weekly_wisdom": "Share deeper insights about developing resilience over time.",
        "coach_corner": "Provide advice for coaches on developing athletes' mental game.",
        "parent_perspective": "Offer guidance for parents supporting their young athlete.",
        "athlete_spotlight": "Highlight mindset strategies of successful young athletes."
    }
    
    guidelines = PLATFORM_GUIDELINES.get(platform, PLATFORM_GUIDELINES["twitter"])
    type_prompt = post_type_prompts.get(post_type, "Create engaging content about mental strength.")
    
    prompt = f"""Create a {platform} post for the book "{book_title}" by {author}.

POST TYPE: {post_type}
TASK: {type_prompt}

PLATFORM: {platform}
MAX LENGTH: {guidelines['max_length']} characters
STYLE: {guidelines['style']}
HASHTAGS: Include {guidelines['hashtags']} relevant hashtags

TARGET AUDIENCE: {audience}
THEMES: mental strength, resilience, confidence, peak performance

REQUIREMENTS:
1. Create authentic, valuable content that resonates with the audience
2. Include practical value or inspiration related to mental strength in sports
3. Stay within character limits
4. Include appropriate hashtags
5. Include a subtle call-to-action encouraging book interest
6. Use an encouraging, expert tone that builds trust
7. Focus on transformation and practical application

Generate ONLY the post content with hashtags included."""
    
    return prompt

def generate_instagram_image(content, openai_client):
    """Generate an image for Instagram posts using DALL-E"""
    try:
        # Create image prompt based on content
        image_prompt = f"""Create a motivational Instagram image for a sports psychology book promotion. 

Style requirements:
- Professional photography quality
- Bright, vibrant colors
- Clean, modern aesthetic
- Inspirational and motivational mood
- Young athlete (13-18 years) in sports setting
- Determined expression, athletic gear
- No text or words in the image
- Square format, Instagram-optimized
- Focus on mental strength and performance themes

Technical specs: 1024x1024, high quality, social media ready"""
        
        response = openai_client.images.generate(
            model="dall-e-3",
            prompt=image_prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        
        return response.data[0].url
    except Exception as e:
        logger.error(f"Error generating image: {str(e)}")
        return None

def generate_single_post(platform, user_settings, post_type, openai_client):
    """Generate a single social media post"""
    try:
        # Create prompt
        prompt = create_prompt(platform, post_type, user_settings)
        
        # Generate content
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert marketing AI specialized in promoting books about youth sports psychology. Create compelling social media content that drives book sales while providing genuine value."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.8,
            max_tokens=500
        )
        
        content = response.choices[0].message.content.strip()
        
        # Generate image for Instagram
        image_url = None
        if platform.lower() == "instagram":
            image_url = generate_instagram_image(content, openai_client)
        
        # Structure post data
        post_data = {
            "id": f"post_{platform}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}",
            "platform": platform,
            "content": content,
            "post_type": post_type,
            "status": "pending_approval",
            "generated_by": "ai",
            "image_url": image_url,
            "createdAt": datetime.now().isoformat(),
            "lastModified": datetime.now().isoformat(),
            "scheduledFor": None,
            "generation_metadata": {
                "model": "gpt-4",
                "timestamp": datetime.now().isoformat(),
                "prompt_type": post_type,
                "image_generated": image_url is not None
            }
        }
        
        logger.info(f"Generated {platform} post of type {post_type}" + 
                   (f" with image" if image_url else ""))
        return post_data
        
    except Exception as e:
        logger.error(f"Error generating {platform} post: {str(e)}")
        raise

@app.route("/")
def hello():
    return {"message": "AI Book Marketing Agent - Simplified Backend", "status": "running"}

@app.route("/api/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.route("/api/generate-posts", methods=["POST"])
def generate_posts():
    """Generate new social media posts with AI"""
    try:
        # Parse request
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        user_id = data.get("user_id")
        platforms = data.get("platforms", ["twitter", "facebook", "instagram"])
        count_per_platform = data.get("count_per_platform", 2)
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        # Check OpenAI API key
        if not OPENAI_API_KEY or OPENAI_API_KEY == "your-openai-api-key-here":
            return jsonify({
                "success": False,
                "error": "OpenAI API key not configured",
                "message": "Please configure your OpenAI API key in Settings → OpenAI Configuration",
                "requires_config": True
            }), 400
        
        # Initialize OpenAI client
        try:
            openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"Failed to initialize OpenAI client: {str(e)}"
            }), 400
        
        # Default user settings if none provided
        user_settings = {
            "bookTitle": "Unstoppable: Mental Strength for Young Athletes",
            "bookAuthor": "Author Name",
            "targetAudience": "youth athletes, parents, coaches",
            "contentGuidelines": "Focus on mental strength, resilience, and peak performance"
        }
        
        # Generate posts
        all_posts = []
        post_types_used = []
        image_count = 0
        
        # Create variety in post types
        available_types = POST_TYPES.copy()
        total_posts = len(platforms) * count_per_platform
        
        for platform in platforms:
            for i in range(count_per_platform):
                # Select post type for variety
                if available_types:
                    post_type = random.choice(available_types)
                    available_types.remove(post_type)
                else:
                    post_type = random.choice(POST_TYPES)
                
                try:
                    post_data = generate_single_post(platform, user_settings, post_type, openai_client)
                    all_posts.append(post_data)
                    post_types_used.append(post_type)
                    
                    if post_data.get("image_url"):
                        image_count += 1
                        
                except Exception as e:
                    logger.error(f"Failed to generate {platform} post: {str(e)}")
                    continue
        
        # Response
        response_data = {
            "success": True,
            "posts_generated": len(all_posts),
            "images_generated": image_count,
            "posts": all_posts,
            "user_id": user_id,
            "platforms": platforms,
            "post_types_generated": post_types_used,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Successfully generated {len(all_posts)} posts with {image_count} images")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in generate_posts: {str(e)}")
        return jsonify({
            "success": False,
            "error": "An unexpected error occurred",
            "details": str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("AI Book Marketing Agent - Simplified Backend")
    logger.info("=" * 50)
    logger.info(f"OpenAI API configured: {bool(OPENAI_API_KEY and OPENAI_API_KEY != 'your-openai-api-key-here')}")
    logger.info("=" * 50)
    
    app.run(host="0.0.0.0", port=5000, debug=True) 
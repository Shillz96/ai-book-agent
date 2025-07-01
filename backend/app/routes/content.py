"""Content management endpoints for the AI Book Marketing Agent."""

from flask import Blueprint, request, jsonify
from datetime import datetime
from ..config import Config
from ..services import content_generator, firebase_service
import logging

# Create blueprint
content_bp = Blueprint('content', __name__)

logger = logging.getLogger(__name__)

@content_bp.route("/generate-posts", methods=["POST"])
def generate_posts():
    """Generate new social media posts with enhanced AI content and Instagram images."""
    try:
        # Validate services
        if not content_generator:
            return jsonify({"error": "Content generator not initialized"}), 500
        if not firebase_service:
            return jsonify({"error": "Firebase service not initialized"}), 500
        
        # Parse request data
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        user_id = data.get("user_id")
        app_id = data.get("app_id", Config.DEFAULT_APP_ID)
        platforms = data.get("platforms", ["twitter", "facebook", "instagram"])
        count_per_platform = data.get("count_per_platform", 1)
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        # Validate platforms
        supported_platforms = ["twitter", "facebook", "instagram", "pinterest"]
        platforms = [p for p in platforms if p.lower() in supported_platforms]
        if not platforms:
            return jsonify({"error": "No valid platforms specified"}), 400
        
        # Get user settings from Firebase
        user_settings = firebase_service.get_user_settings(app_id, user_id)
        if not user_settings:
            # For new users, use minimal default settings to allow content generation
            user_settings = {
                "bookTitle": "Your Book Title",
                "bookAuthor": "Author Name",
                "contentGuidelines": "Create engaging content for book marketing",
                "landingPageUrl": "",
                "targetAudience": "youth athletes, parents, coaches"
            }
        
        # Generate posts with user-specific configuration
        logger.info(f"Generating {count_per_platform} posts per platform for {len(platforms)} platforms")
        generated_posts = content_generator.generate_content_batch(
            platforms, user_settings, count_per_platform, user_id, app_id
        )
        
        # Save posts to Firebase
        saved_posts = []
        image_count = 0
        
        for post_data in generated_posts:
            # Add creation timestamp and other metadata
            post_data.update({
                "createdAt": datetime.now().isoformat(),
                "scheduledFor": None,
                "lastModified": datetime.now().isoformat()
            })
            
            # Count images generated
            if post_data.get("image_url"):
                image_count += 1
            
            doc_id = firebase_service.save_generated_post(app_id, user_id, post_data)
            if doc_id:
                post_data['id'] = doc_id
                saved_posts.append(post_data)
        
        # Create detailed response
        response_data = {
            "success": True,
            "posts_generated": len(saved_posts),
            "images_generated": image_count,
            "posts": saved_posts,
            "user_id": user_id,
            "app_id": app_id,
            "platforms": platforms,
            "post_types_generated": [post.get('post_type') for post in saved_posts],
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Successfully generated and saved {len(saved_posts)} posts with {image_count} images for user {user_id}")
        return jsonify(response_data)
        
    except ValueError as e:
        # Handle configuration errors (like missing API keys)
        error_msg = str(e)
        if "OpenAI API key" in error_msg:
            return jsonify({
                "success": False,
                "error": "OpenAI API key not configured",
                "message": "Please configure your OpenAI API key in the Settings page before generating content.",
                "requires_config": True
            }), 400
        else:
            logger.error(f"Configuration error: {error_msg}")
            return jsonify({
                "success": False,
                "error": error_msg
            }), 400
        
    except Exception as e:
        logger.error(f"Unexpected error generating posts: {str(e)}")
        return jsonify({
            "success": False,
            "error": "An unexpected error occurred while generating content",
            "details": str(e)
        }), 500

@content_bp.route("/pending-posts/<user_id>")
def get_pending_posts(user_id):
    """Get all pending posts for a user."""
    try:
        if not firebase_service:
            return jsonify({"error": "Firebase service not initialized"}), 500
        
        app_id = request.args.get("app_id", Config.DEFAULT_APP_ID)
        pending_posts = firebase_service.get_pending_posts(app_id, user_id)
        
        return jsonify({
            "success": True,
            "posts": pending_posts,
            "count": len(pending_posts),
            "user_id": user_id,
            "app_id": app_id,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@content_bp.route("/approve-post", methods=["POST"])
def approve_post():
    """Approve a pending post."""
    try:
        if not firebase_service:
            return jsonify({"error": "Firebase service not initialized"}), 500
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        post_id = data.get("post_id")
        user_id = data.get("user_id")
        app_id = data.get("app_id", Config.DEFAULT_APP_ID)
        
        if not all([post_id, user_id]):
            return jsonify({"error": "post_id and user_id are required"}), 400
        
        success = firebase_service.update_post_status(
            app_id, user_id, post_id, "approved"
        )
        
        if success:
            return jsonify({
                "success": True,
                "message": "Post approved successfully",
                "post_id": post_id,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({"error": "Failed to update post status"}), 500
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@content_bp.route("/reject-post", methods=["POST"])
def reject_post():
    """Reject a pending post."""
    try:
        if not firebase_service:
            return jsonify({"error": "Firebase service not initialized"}), 500
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        post_id = data.get("post_id")
        user_id = data.get("user_id")
        app_id = data.get("app_id", Config.DEFAULT_APP_ID)
        reason = data.get("reason", "Rejected by user")
        
        if not all([post_id, user_id]):
            return jsonify({"error": "post_id and user_id are required"}), 400
        
        update_data = {"rejection_reason": reason}
        success = firebase_service.update_post_status(
            app_id, user_id, post_id, "rejected", update_data
        )
        
        if success:
            return jsonify({
                "success": True,
                "message": "Post rejected successfully",
                "post_id": post_id,
                "user_id": user_id,
                "reason": reason,
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({"error": "Failed to update post status"}), 500
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500 
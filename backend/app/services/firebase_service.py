# Import compatibility module first to handle Python 3.13 issues
from . import compat
compat.ensure_compatibility()

import os
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import logging
from typing import Dict, List, Optional, Any

# Set up logging for this module
logger = logging.getLogger(__name__)

class FirebaseService:
    """
    Production Firebase Firestore service for managing user data and settings.
    This service handles all Firebase operations with proper error handling
    and production-grade security.
    """
    
    _instance = None
    _initialized = False

    def __new__(cls):
        """Create a singleton instance of the Firebase service."""
        if cls._instance is None:
            cls._instance = super(FirebaseService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the Firebase service with production configurations."""
        if not self._initialized:
            self._initialize_firebase()
            FirebaseService._initialized = True

    def _initialize_firebase(self):
        """
        Initialize Firebase with production credentials.
        Uses service account credentials for secure production access.
        """
        try:
            # Get credentials path from environment variable
            credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            
            if not credentials_path:
                raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable not set")
            
            if not os.path.exists(credentials_path):
                raise FileNotFoundError(f"Firebase credentials file not found: {credentials_path}")
            
            # Initialize Firebase with production service account
            cred = credentials.Certificate(credentials_path)
            firebase_admin.initialize_app(cred)
            
            # Initialize Firestore client
            self.db = firestore.client()
            
            logger.info("Firebase initialized successfully with production credentials")
            
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {str(e)}")
            raise Exception(f"Firebase initialization failed: {str(e)}")

    @property
    def initialized(self):
        """Check if Firebase is properly initialized."""
        return self._initialized and hasattr(self, 'db') and self.db is not None

    def get_user_settings(self, app_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve user settings from Firestore.
        
        Args:
            app_id: Application ID
            user_id: User ID
            
        Returns:
            Dictionary containing user settings or None if not found
        """
        try:
            doc_ref = self.db.collection('artifacts').document(app_id).collection('users').document(user_id).collection('userSettings').document('settings')
            doc = doc_ref.get()
            
            if doc.exists:
                settings = doc.to_dict()
                logger.info(f"Retrieved user settings for user {user_id}")
                return settings
            else:
                logger.warning(f"No user settings found for user {user_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving user settings: {str(e)}")
            return None
    
    def save_generated_post(self, app_id: str, user_id: str, post_data: Dict[str, Any]) -> Optional[str]:
        """
        Save a generated post to the posts collection.
        
        Args:
            app_id: Application ID
            user_id: User ID
            post_data: Dictionary containing post data
            
        Returns:
            Document ID of the saved post or None if failed
        """
        try:
            # Add timestamp and default status if not provided
            post_data['createdAt'] = firestore.SERVER_TIMESTAMP
            post_data['updatedAt'] = firestore.SERVER_TIMESTAMP
            
            if 'status' not in post_data:
                post_data['status'] = 'pending_approval'
            
            # Save to posts collection
            posts_ref = self.db.collection('artifacts').document(app_id).collection('users').document(user_id).collection('posts')
            doc_ref = posts_ref.add(post_data)
            
            doc_id = doc_ref[1].id
            logger.info(f"Saved generated post with ID: {doc_id}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Error saving generated post: {str(e)}")
            return None
    
    def get_pending_posts(self, app_id: str, user_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve all pending posts for a user.
        
        Args:
            app_id: Application ID
            user_id: User ID
            
        Returns:
            List of pending posts
        """
        try:
            posts_ref = self.db.collection('artifacts').document(app_id).collection('users').document(user_id).collection('posts')
            
            # Query for pending posts
            query = posts_ref.where('status', 'in', ['pending_approval', 'draft'])
            docs = query.stream()
            
            posts = []
            for doc in docs:
                post_data = doc.to_dict()
                post_data['id'] = doc.id
                posts.append(post_data)
            
            logger.info(f"Retrieved {len(posts)} pending posts for user {user_id}")
            return posts
            
        except Exception as e:
            logger.error(f"Error retrieving pending posts: {str(e)}")
            return []
    
    def update_post_status(self, app_id: str, user_id: str, post_id: str, status: str, additional_data: Optional[Dict] = None) -> bool:
        """
        Update the status of a post.
        
        Args:
            app_id: Application ID
            user_id: User ID
            post_id: Post document ID
            status: New status (e.g., 'approved', 'published', 'rejected')
            additional_data: Optional additional data to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            doc_ref = self.db.collection('artifacts').document(app_id).collection('users').document(user_id).collection('posts').document(post_id)
            
            update_data = {
                'status': status,
                'updatedAt': firestore.SERVER_TIMESTAMP
            }
            
            if additional_data:
                update_data.update(additional_data)
            
            doc_ref.update(update_data)
            logger.info(f"Updated post {post_id} status to {status}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating post status: {str(e)}")
            return False
    
    def get_post_by_id(self, app_id: str, user_id: str, post_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific post by ID.
        
        Args:
            app_id: Application ID
            user_id: User ID
            post_id: Post document ID
            
        Returns:
            Post data dictionary or None if not found
        """
        try:
            doc_ref = self.db.collection('artifacts').document(app_id).collection('users').document(user_id).collection('posts').document(post_id)
            doc = doc_ref.get()
            
            if doc.exists:
                post_data = doc.to_dict()
                post_data['id'] = doc.id
                logger.info(f"Retrieved post {post_id}")
                return post_data
            else:
                logger.warning(f"Post {post_id} not found")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving post: {str(e)}")
            return None
    
    def save_performance_data(self, app_id: str, user_id: str, performance_data: Dict[str, Any]) -> Optional[str]:
        """
        Save performance analytics data.
        
        Args:
            app_id: Application ID
            user_id: User ID
            performance_data: Performance metrics and data
            
        Returns:
            Document ID of saved performance data or None if failed
        """
        try:
            performance_data['timestamp'] = firestore.SERVER_TIMESTAMP
            
            analytics_ref = self.db.collection('artifacts').document(app_id).collection('users').document(user_id).collection('analytics')
            doc_ref = analytics_ref.add(performance_data)
            
            doc_id = doc_ref[1].id
            logger.info(f"Saved performance data with ID: {doc_id}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Error saving performance data: {str(e)}")
            return None

    def save_ab_test(self, app_id: str, user_id: str, test_id: str, test_setup: Dict[str, Any]) -> Optional[str]:
        """
        Save A/B test configuration and setup data.
        
        Args:
            app_id: Application ID
            user_id: User ID
            test_id: Unique test identifier
            test_setup: A/B test configuration data
            
        Returns:
            Document ID of saved test data or None if failed
        """
        try:
            test_setup['timestamp'] = firestore.SERVER_TIMESTAMP
            test_setup['test_id'] = test_id
            
            # Save to ab_tests collection
            ab_tests_ref = self.db.collection('artifacts').document(app_id).collection('users').document(user_id).collection('ab_tests')
            doc_ref = ab_tests_ref.document(test_id)
            doc_ref.set(test_setup)
            
            logger.info(f"Saved A/B test {test_id} with ID: {test_id}")
            return test_id
            
        except Exception as e:
            logger.error(f"Error saving A/B test: {str(e)}")
            return None

    def get_ab_test_results(self, app_id: str, user_id: str, test_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve A/B test results and data.
        
        Args:
            app_id: Application ID
            user_id: User ID
            test_id: Test identifier
            
        Returns:
            A/B test data dictionary or None if not found
        """
        try:
            doc_ref = self.db.collection('artifacts').document(app_id).collection('users').document(user_id).collection('ab_tests').document(test_id)
            doc = doc_ref.get()
            
            if doc.exists:
                test_data = doc.to_dict()
                logger.info(f"Retrieved A/B test data for test {test_id}")
                return test_data
            else:
                logger.warning(f"A/B test {test_id} not found")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving A/B test: {str(e)}")
            return None 
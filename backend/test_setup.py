#!/usr/bin/env python3
"""
Simple test script to verify backend setup and module imports.
This can be run without API keys to check if the basic structure is working.
"""

import os
import sys
from datetime import datetime

def test_imports():
    """Test that all modules can be imported successfully."""
    print("Testing module imports...")
    
    try:
        from config.settings import Config
        print("✓ Config module imported successfully")
    except Exception as e:
        print(f"✗ Config import failed: {e}")
        return False
    
    try:
        from app.content_generator import ContentGenerator
        print("✓ ContentGenerator module imported successfully")
    except Exception as e:
        print(f"✗ ContentGenerator import failed: {e}")
        return False
    
    try:
        from app.firebase_service import FirebaseService
        print("✓ FirebaseService module imported successfully")
    except Exception as e:
        print(f"✗ FirebaseService import failed: {e}")
        return False
    
    try:
        from app.social_media_manager import SocialMediaManager
        print("✓ SocialMediaManager module imported successfully")
    except Exception as e:
        print(f"✗ SocialMediaManager import failed: {e}")
        return False
    
    return True

def test_configuration():
    """Test configuration validation."""
    print("\nTesting configuration...")
    
    try:
        from config.settings import Config
        missing_configs = Config.validate_config()
        
        print(f"Missing required configurations: {missing_configs}")
        
        # Check if we have the basic structure
        print(f"OpenAI API Key configured: {bool(Config.OPENAI_API_KEY)}")
        print(f"Firebase Project ID configured: {bool(Config.FIREBASE_PROJECT_ID)}")
        print(f"Default App ID: {Config.DEFAULT_APP_ID}")
        
        return True
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def test_flask_app():
    """Test that the Flask app can be created."""
    print("\nTesting Flask app creation...")
    
    try:
        # Set minimal env vars to avoid errors
        os.environ.setdefault('SECRET_KEY', 'test-secret-key')
        
        from main import app
        print("✓ Flask app created successfully")
        print(f"✓ App name: {app.name}")
        print(f"✓ Debug mode: {app.debug}")
        
        # Test that we can get the app context
        with app.app_context():
            print("✓ Flask app context working")
        
        return True
    except Exception as e:
        print(f"✗ Flask app test failed: {e}")
        return False

def test_content_generator_structure():
    """Test ContentGenerator class structure without API key."""
    print("\nTesting ContentGenerator structure...")
    
    try:
        from app.content_generator import ContentGenerator
        
        # Test class creation with dummy API key (won't make actual calls)
        generator = ContentGenerator("dummy-key", "gpt-4")
        
        # Test that the platform guidelines are properly defined
        platforms = list(generator.platform_guidelines.keys())
        print(f"✓ Supported platforms: {platforms}")
        
        # Test that book context is defined
        themes = generator.book_context.get("key_themes", [])
        print(f"✓ Book themes configured: {len(themes)} themes")
        
        return True
    except Exception as e:
        print(f"✗ ContentGenerator structure test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("AI Book Marketing Agent - Backend Setup Test")
    print("=" * 60)
    print(f"Test started at: {datetime.now().isoformat()}")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print()
    
    tests = [
        test_imports,
        test_configuration,
        test_flask_app,
        test_content_generator_structure
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
                print("✓ Test passed")
            else:
                print("✗ Test failed")
        except Exception as e:
            print(f"✗ Test error: {e}")
        print("-" * 40)
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Backend setup is working correctly.")
        print("\nNext steps:")
        print("1. Set up your .env file with API keys")
        print("2. Configure Firebase credentials")
        print("3. Run 'python main.py' to start the backend")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)
    
    print("=" * 60)

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Demo script for testing social media functionality without real API credentials.
This demonstrates how to use mock social media APIs for development and testing.
"""

import os
import sys
import logging
from datetime import datetime

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(__file__))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_mock_environment():
    """Set up environment variables for mock testing."""
    print("🔧 Setting up mock testing environment...")
    
    # Enable mock mode
    os.environ['MOCK_SOCIAL_MEDIA'] = 'true'
    os.environ['TESTING'] = 'true'
    
    # Set mock API credentials (these won't hit real APIs)
    mock_credentials = {
        'OPENAI_API_KEY': 'sk-mock-openai-key-for-testing',
        'TWITTER_API_KEY': 'mock_twitter_api_key',
        'TWITTER_API_SECRET': 'mock_twitter_api_secret',
        'TWITTER_ACCESS_TOKEN': 'mock_twitter_access_token',
        'TWITTER_ACCESS_TOKEN_SECRET': 'mock_twitter_access_token_secret',
        'FACEBOOK_ACCESS_TOKEN': 'mock_facebook_access_token',
        'FACEBOOK_PAGE_ID': 'mock_facebook_page_id',
        'INSTAGRAM_ACCESS_TOKEN': 'mock_instagram_access_token',
        'INSTAGRAM_BUSINESS_ACCOUNT_ID': 'mock_instagram_business_account',
        'PINTEREST_ACCESS_TOKEN': 'mock_pinterest_access_token',
        'PINTEREST_BOARD_ID': 'mock_pinterest_board_id'
    }
    
    for key, value in mock_credentials.items():
        os.environ[key] = value
    
    print("✅ Mock environment configured successfully!")
    return mock_credentials

def demonstrate_social_media_testing():
    """Main demonstration of social media testing capabilities."""
    print("\n" + "="*60)
    print("🚀 AI BOOK AGENT - Social Media Testing Demo")
    print("="*60)
    print("This demo shows how to test all social media functionality")
    print("without needing real API credentials or making actual posts.")
    print()
    
    # Set up mock environment
    mock_creds = setup_mock_environment()
    
    # Import after setting up environment
    try:
        from tests.mocks.mock_social_media import MockSocialMediaManager
        print("✅ Mock social media modules imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import mock modules: {e}")
        return False
    
    # Initialize mock social media manager
    print("\n📱 Initializing Social Media Manager...")
    manager = MockSocialMediaManager(mock_creds)
    
    # Test all platforms
    print("\n🔍 Testing Platform Connections...")
    platforms = ['twitter', 'facebook', 'instagram', 'pinterest']
    
    for platform in platforms:
        result = manager.test_platform_connection(platform)
        status = "✅" if result['success'] else "❌"
        print(f"{status} {platform.title()}: {result.get('message', result.get('error'))}")
    
    # Demonstrate posting to each platform
    print("\n📝 Creating Test Posts...")
    
    test_posts = [
        {
            'platform': 'twitter',
            'content': '🚀 Testing our AI book marketing system! The future of book promotion is here. #BookMarketing #AI #Innovation',
            'media': None
        },
        {
            'platform': 'facebook', 
            'content': 'Exciting update: Our AI-powered book marketing agent is showing incredible results! 📚✨ Authors are seeing 300% increase in engagement rates.',
            'media': ['https://example.com/book-marketing-stats.jpg']
        },
        {
            'platform': 'instagram',
            'content': 'Behind the scenes of our AI book marketing magic! ✨📖 From manuscript to bestseller, our system handles it all. #BookMarketing #AIMarketing #Publishing #BookPromotion',
            'media': ['https://example.com/ai-marketing-behind-scenes.jpg']
        },
        {
            'platform': 'pinterest',
            'content': '📌 Ultimate Book Marketing Checklist: 10 proven strategies that every author needs to know. Save this pin for your next book launch!',
            'media': ['https://example.com/book-marketing-checklist-infographic.jpg'],
            'title': 'Book Marketing Checklist for Authors'
        }
    ]
    
    successful_posts = 0
    
    for post in test_posts:
        platform = post['platform']
        content = post['content']
        media = post.get('media')
        
        print(f"\n📤 Posting to {platform.title()}...")
        print(f"   Content: {content[:60]}{'...' if len(content) > 60 else ''}")
        
        if platform == 'pinterest':
            result = manager.post_to_pinterest(content, media, post.get('title', ''))
        else:
            result = manager.post_content(platform, content, media)
        
        if result['success']:
            successful_posts += 1
            print(f"   ✅ Success! Post ID: {result['post_id']}")
            print(f"   🔗 URL: {result['url']}")
            if media:
                print(f"   🖼️  Media attached: {len(media)} item(s)")
        else:
            print(f"   ❌ Failed: {result['error']}")
    
    # Show posting statistics
    print(f"\n📊 Posting Results:")
    print(f"   Total Posts: {len(test_posts)}")
    print(f"   Successful: {successful_posts}")
    print(f"   Failed: {len(test_posts) - successful_posts}")
    
    # Show platform status
    print(f"\n🌐 Platform Status:")
    status = manager.get_platform_status()
    for platform, available in status.items():
        icon = "✅" if available else "❌"
        print(f"   {icon} {platform.title()}: {'Available' if available else 'Unavailable'}")
    
    # Show post history
    print(f"\n📈 Post History:")
    history = manager.get_post_history()
    print(f"   Total posts in session: {len(history)}")
    
    for i, post in enumerate(history[-3:], 1):  # Show last 3 posts
        print(f"   {i}. {post['platform'].title()} - {post['timestamp'][:19]}")
    
    # Test batch posting
    print(f"\n🔄 Testing Batch Cross-Platform Posting...")
    batch_content = "🎉 Big announcement! Our AI Book Marketing Agent just hit a major milestone. Thank you to all the authors who trust us with their book promotion!"
    batch_media = ["https://example.com/milestone-celebration.jpg"]
    
    batch_results = []
    for platform in platforms:
        if platform in ['instagram', 'pinterest']:
            result = manager.post_content(platform, batch_content, batch_media)
        else:
            result = manager.post_content(platform, batch_content)
        batch_results.append(result)
    
    successful_batch = sum(1 for r in batch_results if r['success'])
    print(f"   📤 Batch posting completed: {successful_batch}/{len(platforms)} platforms")
    
    # Final summary
    print(f"\n" + "="*60)
    print(f"🎉 Demo Completed Successfully!")
    print(f"="*60)
    print(f"✨ All social media functionality tested without real API calls")
    print(f"📱 Platforms tested: {', '.join([p.title() for p in platforms])}")
    print(f"📊 Total mock posts created: {len(manager.get_post_history())}")
    print(f"🕒 Demo completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print(f"\n💡 How to use this for development:")
    print(f"   1. Set MOCK_SOCIAL_MEDIA=true in your environment")
    print(f"   2. Use MockSocialMediaManager instead of SocialMediaManager")
    print(f"   3. All posts will be simulated - no real API calls made")
    print(f"   4. Perfect for testing, development, and demonstrations")
    
    return True

def run_social_media_api_tests():
    """Run the social media mock tests using pytest."""
    print(f"\n🧪 Running Social Media API Tests...")
    
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 
            'tests/test_social_media_manager.py', 
            '-v', '--tb=short'
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        print(f"Test output:")
        print(result.stdout)
        if result.stderr:
            print(f"Errors:")
            print(result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")
        return False

def main():
    """Main function to run the demo."""
    try:
        # Run the main demonstration
        demo_success = demonstrate_social_media_testing()
        
        if demo_success:
            print(f"\n" + "="*60)
            user_input = input("🧪 Would you like to run the full test suite? (y/n): ").lower().strip()
            
            if user_input in ['y', 'yes']:
                test_success = run_social_media_api_tests()
                if test_success:
                    print(f"✅ All tests passed!")
                else:
                    print(f"⚠️  Some tests may have failed. Check output above.")
            
            print(f"\n🎯 Next Steps:")
            print(f"   • Use this mock system for development without API keys")
            print(f"   • Add more test cases in tests/test_social_media_manager.py")
            print(f"   • Configure real API keys when ready for production")
            print(f"   • Check out backend/tests/mocks/ for implementation details")
        
    except KeyboardInterrupt:
        print(f"\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 
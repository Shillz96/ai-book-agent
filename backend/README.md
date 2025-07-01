# AI Book Marketing Agent - Backend

This is the backend service for the AI Book Marketing Agent, designed to generate and publish social media content for the book "Unstoppable - The Young Athlete's Guide to Rock Solid Mental Strength".

## Features

- **AI Content Generation**: Uses OpenAI GPT-4 to create engaging social media posts
- **Multi-Platform Support**: Twitter, Facebook, Instagram, and Pinterest
- **Firebase Integration**: Stores user settings and generated posts
- **Human-in-the-Loop**: Posts require approval before publishing
- **Real-time API**: RESTful endpoints for frontend integration

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configuration

Copy the example environment file and configure your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your actual API keys and configuration:

```bash
# Required - OpenAI API Key
OPENAI_API_KEY=sk-your-openai-api-key-here

# Required - Firebase Configuration
FIREBASE_PROJECT_ID=your-firebase-project-id

# Social Media API Keys (at least one required)
TWITTER_API_KEY=your-twitter-api-key
FACEBOOK_ACCESS_TOKEN=your-facebook-access-token
# ... etc
```

### 3. Firebase Setup

1. Download your Firebase service account credentials JSON file
2. Place it at `backend/config/firebase-credentials.json`
3. Make sure your Firebase project has Firestore enabled

### 4. Run the Backend

```bash
python main.py
```

The backend will start on `http://localhost:5000`

## Package Management

### Updated Requirements

The project now uses more flexible version constraints to ensure compatibility while allowing for security updates:

- **`requirements.txt`**: Full dependencies with flexible version ranges
- **`requirements_core.txt`**: Minimal core dependencies for lightweight deployments

### Dependency Update Tool

Use the included utility script to safely manage package updates:

```bash
# Check for outdated packages (dry run)
python update_packages.py

# Actually update packages
python update_packages.py --upgrade

# Check for security vulnerabilities
python update_packages.py --security
```

This tool provides:
- Safe dependency checking before updating
- Conflict detection and resolution
- Security vulnerability scanning
- Rollback support if updates fail

### Key Dependencies

- **Flask 3.0+**: Modern web framework with latest security features
- **Firebase Admin SDK**: Latest stable version for database operations
- **OpenAI Python SDK**: Flexible version to accommodate frequent API updates
- **Google Cloud Firestore**: Latest version with improved performance

## API Endpoints

### Health Check
```
GET /api/health
```
Returns the status of all services and configurations.

### Generate Posts
```
POST /api/generate-posts
```
Generate new social media posts for a user.

**Request Body:**
```json
{
  "user_id": "user123",
  "platforms": ["twitter", "facebook", "instagram"],
  "count_per_platform": 2
}
```

### Approve Post
```
POST /api/approve-post
```
Approve and publish a generated post.

**Request Body:**
```json
{
  "user_id": "user123",
  "post_id": "post123"
}
```

### Get Pending Posts
```
GET /api/pending-posts/{user_id}
```
Retrieve all posts awaiting approval for a user.

### Platform Status
```
GET /api/platform-status
```
Check which social media platforms are configured and available.

## Configuration Requirements

### Required
- **OpenAI API Key**: For content generation
- **Firebase Project**: For data storage and user management

### Optional (but recommended)
- **Twitter API**: Developer account and app credentials
- **Facebook API**: Page access token and page ID
- **Instagram API**: Business account and access token
- **Pinterest API**: Access token and board ID

## Architecture

The backend consists of several key services:

### ContentGenerator (`app/content_generator.py`)
- Uses OpenAI GPT-4 to generate platform-specific content
- Incorporates book context and marketing guidelines
- Analyzes and scores content for engagement potential

### SocialMediaManager (`app/social_media_manager.py`)
- Handles posting to all social media platforms
- Manages API authentication and error handling
- Provides unified interface for cross-platform posting

### FirebaseService (`app/firebase_service.py`)
- Manages all Firestore database operations
- Handles user settings and post storage
- Provides real-time data synchronization

### Configuration (`config/settings.py`)
- Centralized configuration management
- Environment variable handling
- Validation and error checking

## Development

### Adding New Platforms

To add support for a new social media platform:

1. Add platform credentials to `config/settings.py`
2. Implement platform methods in `SocialMediaManager`
3. Add platform-specific guidelines to `ContentGenerator`
4. Update the API endpoints as needed

### Content Customization

The content generation can be customized by:

- Modifying the system prompt in `ContentGenerator._get_system_prompt()`
- Adjusting platform guidelines in `ContentGenerator.platform_guidelines`
- Updating the book context in `ContentGenerator.book_context`

### Testing

Test individual components:

```bash
# Test platform connections
curl http://localhost:5000/api/test-platform/twitter

# Check service health
curl http://localhost:5000/api/health

# Generate test posts (requires user setup)
curl -X POST http://localhost:5000/api/generate-posts \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user", "platforms": ["twitter"]}'
```

## Error Handling

The backend includes comprehensive error handling:

- Configuration validation on startup
- API key verification for all services
- Graceful degradation when services are unavailable
- Detailed logging for debugging

## Security Considerations

- Store API keys in environment variables, never in code
- Use Firebase security rules to protect user data
- Implement rate limiting for API endpoints (future enhancement)
- Validate all user inputs and sanitize content

## Future Enhancements

- **Scheduling**: Add support for scheduled posting
- **Analytics**: Integrate Google Analytics and social media insights
- **A/B Testing**: Test different content variations
- **Budget Management**: Track ad spend and ROI
- **Learning Loop**: Implement feedback-based content improvement

## Troubleshooting

### Common Issues

1. **Firebase Connection Failed**
   - Check credentials file path and permissions
   - Verify Firebase project ID is correct

2. **OpenAI API Errors**
   - Verify API key is valid and has sufficient credits
   - Check for rate limiting or quota issues

3. **Social Media API Issues**
   - Ensure all required scopes/permissions are granted
   - Check for expired tokens or authentication failures

### Logs

Check application logs for detailed error information:
```bash
tail -f backend.log
```

## Contributing

1. Follow the existing code style and structure
2. Add comprehensive comments and documentation
3. Include error handling for all new features
4. Test with real API credentials before submitting
5. Update this README with any new functionality 
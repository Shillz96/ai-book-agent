#!/usr/bin/env node

/**
 * AI Book Marketing Agent - Automated Deployment Script
 * 
 * This script helps clients deploy their AI Book Marketing Agent
 * with minimal technical knowledge required.
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log(`
🚀 AI Book Marketing Agent - Deployment Assistant
==============================================

This script will help you deploy your AI Book Marketing Agent.
Please ensure you have the following ready:

✅ Git repository created (GitHub/GitLab)
✅ Vercel account (vercel.com)
✅ Railway account (railway.app)
✅ OpenAI API key
✅ Firebase project setup

Press Ctrl+C to exit or Enter to continue...
`);

// Wait for user input
process.stdin.setRawMode(true);
process.stdin.resume();
process.stdin.on('data', process.exit.bind(process, 0));

async function deployApp() {
  console.log('\n🔧 Starting deployment process...\n');

  try {
    // Check if we're in the right directory
    if (!fs.existsSync('frontend') || !fs.existsSync('backend')) {
      console.error('❌ Error: Please run this script from the project root directory.');
      process.exit(1);
    }

    // Step 1: Frontend Setup
    console.log('📦 Step 1: Setting up frontend...');
    
    // Check if node_modules exists in frontend
    if (!fs.existsSync('frontend/node_modules')) {
      console.log('Installing frontend dependencies...');
      execSync('npm install', { cwd: 'frontend', stdio: 'inherit' });
    }

    // Create .env file for frontend if it doesn't exist
    const frontendEnvPath = 'frontend/.env';
    if (!fs.existsSync(frontendEnvPath)) {
      const frontendEnvContent = `# AI Book Marketing Agent - Frontend Environment Variables
# Update REACT_APP_API_URL after deploying backend
REACT_APP_API_URL=http://localhost:5000/api
REACT_APP_FIREBASE_PROJECT_ID=ai-book-agent-dashboard
`;
      fs.writeFileSync(frontendEnvPath, frontendEnvContent);
      console.log('✅ Created frontend/.env file');
    }

    // Step 2: Backend Setup
    console.log('\n📦 Step 2: Setting up backend...');
    
    // Create .env file for backend if it doesn't exist
    const backendEnvPath = 'backend/.env';
    if (!fs.existsSync(backendEnvPath)) {
      const backendEnvContent = `# AI Book Marketing Agent - Backend Environment Variables
# Add your API keys after deployment

# OpenAI Configuration (REQUIRED)
OPENAI_API_KEY=your-openai-api-key-here

# Firebase Configuration
GOOGLE_APPLICATION_CREDENTIALS=./ai-book-agent-dashboard-firebase-adminsdk.json
FIREBASE_PROJECT_ID=ai-book-agent-dashboard

# Social Media APIs (Configure after deployment)
TWITTER_API_KEY=
TWITTER_API_SECRET=
TWITTER_ACCESS_TOKEN=
TWITTER_ACCESS_TOKEN_SECRET=

FACEBOOK_ACCESS_TOKEN=
FACEBOOK_PAGE_ID=

INSTAGRAM_ACCESS_TOKEN=
INSTAGRAM_BUSINESS_ACCOUNT_ID=

PINTEREST_ACCESS_TOKEN=
PINTEREST_BOARD_ID=

# Google Services
GOOGLE_ANALYTICS_PROPERTY_ID=
GOOGLE_ADS_CUSTOMER_ID=
GOOGLE_ADS_DEVELOPER_TOKEN=

# Application Settings
FLASK_ENV=production
PORT=5000
`;
      fs.writeFileSync(backendEnvPath, backendEnvContent);
      console.log('✅ Created backend/.env file');
    }

    // Step 3: Create deployment configuration files
    console.log('\n📦 Step 3: Creating deployment configurations...');

    // Vercel configuration for frontend
    const vercelConfig = {
      "name": "ai-book-marketing-agent",
      "version": 2,
      "builds": [
        {
          "src": "package.json",
          "use": "@vercel/static-build",
          "config": {
            "distDir": "build"
          }
        }
      ],
      "routes": [
        {
          "src": "/static/(.*)",
          "headers": { "cache-control": "s-maxage=31536000,immutable" },
          "dest": "/static/$1"
        },
        { "src": "/service-worker.js", "headers": { "cache-control": "s-maxage=0" }, "dest": "/service-worker.js" },
        { "src": "/sockjs-node/(.*)", "dest": "/sockjs-node/$1" },
        { "src": "/(.*)", "dest": "/index.html" }
      ]
    };

    fs.writeFileSync('frontend/vercel.json', JSON.stringify(vercelConfig, null, 2));
    console.log('✅ Created frontend/vercel.json');

    // Railway configuration for backend
    const railwayConfig = {
      "build": {
        "builder": "NIXPACKS"
      },
      "deploy": {
        "startCommand": "python main.py",
        "healthcheckPath": "/health"
      }
    };

    fs.writeFileSync('backend/railway.json', JSON.stringify(railwayConfig, null, 2));
    console.log('✅ Created backend/railway.json');

    // Procfile for Heroku (alternative)
    fs.writeFileSync('backend/Procfile', 'web: python main.py');
    console.log('✅ Created backend/Procfile');

    // Step 4: Create README for client
    const clientReadme = `# Your AI Book Marketing Agent

## 🎉 Congratulations!

Your AI Book Marketing Agent is ready for deployment. This system will autonomously market your book across multiple platforms.

## 📋 Next Steps

1. **Deploy to Cloud** (Recommended):
   - Frontend: Deploy \`frontend/\` folder to [Vercel](https://vercel.com)
   - Backend: Deploy \`backend/\` folder to [Railway](https://railway.app)

2. **Configure API Keys**:
   - Open your deployed dashboard
   - Complete the setup guide
   - Add all your API keys in Settings

3. **Start Marketing**:
   - Configure your book details
   - Set your budget
   - Enable autonomous mode

## 🔗 Important Links

- **Frontend Dashboard**: Will be available at your Vercel URL
- **Setup Guide**: Built into the dashboard
- **API Documentation**: See DEPLOYMENT_GUIDE.md

## 📞 Support

If you need help:
1. Check the built-in setup guide
2. Review DEPLOYMENT_GUIDE.md
3. Contact your developer

---

**Your AI marketing team is ready to work 24/7 for your book! 🚀**
`;

    fs.writeFileSync('CLIENT_README.md', clientReadme);
    console.log('✅ Created CLIENT_README.md');

    // Step 5: Final instructions
    console.log(`
🎉 Deployment preparation complete!

📋 Next Steps:

1. **Commit to Git**:
   git add .
   git commit -m "Ready for deployment"
   git push

2. **Deploy Frontend (Vercel)**:
   - Go to vercel.com
   - Import your repository
   - Select the 'frontend' folder
   - Deploy

3. **Deploy Backend (Railway)**:
   - Go to railway.app
   - Import your repository  
   - Select the 'backend' folder
   - Add environment variables
   - Deploy

4. **Update API URL**:
   - After backend deployment, update frontend/.env
   - Change REACT_APP_API_URL to your Railway URL
   - Redeploy frontend

5. **Configure APIs**:
   - Open your dashboard
   - Complete the onboarding guide
   - Add all API keys in Settings

🔗 Your dashboard will be available at: https://your-app.vercel.app

📖 See DEPLOYMENT_GUIDE.md for detailed instructions.

Happy marketing! 🚀
`);

  } catch (error) {
    console.error('\n❌ Error during deployment preparation:', error.message);
    console.log('\n📞 If you need help, contact your developer or check the documentation.');
  }
}

// Run if called directly
if (require.main === module) {
  deployApp();
}

module.exports = { deployApp }; 
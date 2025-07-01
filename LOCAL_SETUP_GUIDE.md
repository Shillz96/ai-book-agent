# AI Book Marketing Agent - Local Setup Guide

## 🚀 Quick Start Guide for Running Locally

This guide will help you get the AI Book Marketing Agent running on your local computer in just a few simple steps. **No .env file editing required** - all configuration is done through the web interface!

## 📋 Prerequisites

Before starting, make sure you have these installed on your computer:

1. **Python 3.8 or higher** - [Download from python.org](https://www.python.org/downloads/)
2. **Node.js and npm** - [Download from nodejs.org](https://nodejs.org/downloads/)
3. **Git** - [Download from git-scm.com](https://git-scm.com/downloads)

## 🔧 Step-by-Step Setup

### Step 1: Clone the Repository
```powershell
# Open PowerShell and navigate to where you want to store the project
# Clone the repository
git clone https://github.com/Shillz96/ai-book-agent.git

# Navigate into the project directory
cd ai-book-agent
```

### Step 2: Set Up the Backend (Python)
```powershell
# Go to backend folder
cd backend

# Create a virtual environment (isolates Python packages)
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\activate

# Install required Python packages
pip install -r requirements.txt

# Copy the example environment file (optional - for advanced users)
copy .env.example .env
```

**Note**: You can skip the `.env` file entirely! The app will work with the web-based configuration.

### Step 3: Start the Backend Server
```powershell
# Make sure you're in the backend folder with virtual environment active
python main.py
```

You should see something like: `Running on http://127.0.0.1:5000`

**Keep this PowerShell window open** - this is your backend server.

### Step 4: Set Up the Frontend (React)
Open a **NEW PowerShell window** and run:

```powershell
# Navigate to project directory
cd ai-book-agent

# Go to frontend folder
cd frontend

# Install Node.js packages
npm install

# Start the frontend development server
npm start
```

Your web browser should automatically open to `http://localhost:3000`

## ⚙️ Configuration Through Web Interface

**🎉 New Feature**: No more `.env` file editing! Configure everything through the Settings page.

1. When you first open the application, click the **⚙️ Settings** button
2. Configure your API keys and settings:
   - **OpenAI API Key** (Required for content generation)
   - **Firebase Project Settings** (If you have your own Firebase project)
   - **Social Media API Keys** (Optional - for posting to platforms)
   - **Google Analytics & Ads** (Optional - for analytics and advertising)
   - **Book Information** (Your book details and marketing settings)
   - **Budget & Performance Settings** (Marketing budget and thresholds)

3. Use the **"Test Configuration"** button to validate your API keys
4. Click **"Save Settings"** to store your configuration

All settings are securely stored in Firebase and automatically loaded when needed.

## ✅ First-Time Setup Checklist

- [ ] Backend server running on port 5000
- [ ] Frontend running on port 3000
- [ ] Web interface opens in browser
- [ ] Configure OpenAI API key in Settings (minimum requirement)
- [ ] Test configuration to verify API keys work
- [ ] Generate your first content to verify everything works

## 🔍 Health Checks

The application includes built-in health monitoring:

- Basic health check: `http://localhost:5000/api/health`
- Detailed health status: `http://localhost:5000/api/health/detailed`

Use these endpoints to verify all services are running correctly.

## ✅ Verification

If everything is working correctly:

1. **Backend**: PowerShell shows "Running on http://127.0.0.1:5000"
2. **Frontend**: Browser opens to `http://localhost:3000` showing the dashboard
3. **Settings**: You can access and update configuration through the web interface
4. **Content Generation**: After configuring OpenAI API key, you can generate posts
5. **Health Checks**: All services show as "healthy" in the detailed health check

## 🛠️ Troubleshooting

### Backend Issues:
- **"Module not found"**: Make sure virtual environment is activated (`.\venv\Scripts\activate`)
- **"Permission denied"**: Run PowerShell as Administrator
- **"Port already in use"**: Kill existing Python processes or use a different port

### Frontend Issues:
- **"npm not found"**: Make sure Node.js is installed correctly
- **"Cannot connect to backend"**: Make sure backend is running on port 5000
- **"Build failed"**: Try deleting `node_modules` folder and run `npm install` again

### Configuration Issues:
- **"OpenAI API key not configured"**: Add your API key in Settings and click "Test Configuration"
- **"Cannot save settings"**: Check that both frontend and backend are running
- **"Configuration test failed"**: Verify your API keys are correct and have proper permissions

### Quick Reset Commands:
```powershell
# If you need to restart everything fresh:

# Stop both servers (Ctrl+C in both PowerShell windows)

# Backend reset:
cd ai-book-agent/backend
.\venv\Scripts\activate
python main.py

# Frontend reset (in new PowerShell window):
cd ai-book-agent/frontend
npm start
```

## 🎯 Next Steps

Once the app is running locally:

1. **Configure Settings**: Use the Settings page to add your API keys
2. **Test Configuration**: Use the "Test Configuration" button to verify API keys
3. **Generate Content**: Try generating your first social media posts
4. **Monitor Health**: Check the health endpoints to ensure all services are running
5. **Explore Features**: Try the various marketing automation features

## 🔒 Important Notes

- **Keep both PowerShell windows open** while using the app
- **Virtual environment**: Always activate it before working on backend (`.\venv\Scripts\activate`)
- **API Keys**: All sensitive data is securely stored and encrypted in Firebase
- **Web Configuration**: All settings can be managed through the web interface - no file editing needed
- **Automatic Updates**: Configuration changes are immediately available to the backend

## 🔑 Required API Keys

To use all features, you'll need:

1. **OpenAI API Key** (Required) - Get from [OpenAI Platform](https://platform.openai.com/api-keys)
2. **Firebase Project** (Optional) - Use the default or create your own
3. **Social Media APIs** (Optional) - For posting to Twitter, Facebook, Instagram, Pinterest
4. **Google Analytics & Ads** (Optional) - For advanced analytics and advertising

You can start with just the OpenAI API key and add others as needed.

## 📞 Need Help?

If you run into issues:
1. Check the health endpoints for service status
2. Use "Test Configuration" to verify your API keys
3. Look for error messages in the PowerShell windows
4. Try restarting both servers
5. Check the browser console for frontend errors

Your AI Book Marketing Agent should now be running locally with web-based configuration! 🚀 
# 🚀 AI Book Marketing Agent - Production Deployment Guide

This guide covers deploying the AI Book Marketing Agent to production environments including cloud platforms, Docker, and VPS servers.

## 📋 Production Checklist

Before deploying to production, ensure you have:

### ✅ **Required Configuration**
- [ ] OpenAI API key with sufficient credits
- [ ] Firebase project setup with Firestore enabled
- [ ] Firebase service account credentials file
- [ ] Strong SECRET_KEY for Flask sessions
- [ ] Domain name and SSL certificate (recommended)

### ✅ **Optional Configuration** 
- [ ] Social media API keys (Twitter, Facebook, Instagram, Pinterest)
- [ ] Google Analytics property and credentials
- [ ] Google Ads account and credentials
- [ ] Redis instance for task queue (recommended for scaling)

### ✅ **Security Setup**
- [ ] Environment variables properly configured
- [ ] Credential files secured and not in version control
- [ ] CORS settings updated for production domain
- [ ] DEBUG mode disabled (`FLASK_DEBUG=false`)

## 🐳 Docker Deployment (Recommended)

### Quick Start with Docker Compose
```bash
# Clone the repository
git clone https://github.com/Shillz96/ai-book-agent.git
cd ai-book-agent

# Create production environment file
cp .env.example .env.production
# Edit .env.production with your actual values

# Deploy with Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# Check health
curl http://localhost:5000/api/health
```

### Production Environment Variables
Create a `.env.production` file:
```bash
# Core Configuration (Required)
SECRET_KEY=your-super-secure-secret-key-here
OPENAI_API_KEY=sk-your-openai-api-key
FIREBASE_PROJECT_ID=your-firebase-project-id

# Production Settings
FLASK_DEBUG=false
AUTONOMOUS_MODE=true

# Your Book Information
BOOK_TITLE=Your Book Title Here
BOOK_AMAZON_URL=https://amazon.com/dp/your-book-id
BOOK_AUDIBLE_URL=https://audible.com/pd/your-book-id
LANDING_PAGE_URL=https://your-landing-page.com

# Budget Management
MONTHLY_MARKETING_BUDGET=1000.0
BUDGET_ALERT_THRESHOLD=0.8
EMERGENCY_STOP_THRESHOLD=0.95

# Add your social media and Google service credentials as needed
```

## ☁️ Cloud Platform Deployment

### 1. Railway (Simple, Recommended)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

**Railway Configuration:**
- Automatically detects Python and Node.js
- Set environment variables in Railway dashboard
- Connects to Procfile automatically
- Built-in Redis available as addon

### 2. Render (Free Tier Available)
1. Connect your GitHub repository to Render
2. Create a new Web Service
3. Set build command: `cd backend && pip install -r requirements.txt`
4. Set start command: `cd backend && python main.py`
5. Add environment variables in Render dashboard

### 3. Heroku
```bash
# Install Heroku CLI and login
heroku create your-app-name

# Add environment variables
heroku config:set OPENAI_API_KEY=sk-your-key
heroku config:set FIREBASE_PROJECT_ID=your-project
# ... add all other required variables

# Deploy
git push heroku main
```

### 4. AWS Elastic Beanstalk
1. Install AWS CLI and EB CLI
2. Initialize: `eb init`
3. Create environment: `eb create production`
4. Set environment variables in AWS console
5. Deploy: `eb deploy`

### 5. Google Cloud Platform
```bash
# Deploy using Cloud Run
gcloud run deploy ai-book-agent \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## 🖥️ VPS/Server Deployment

### Ubuntu/Debian Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3 python3-pip python3-venv nodejs npm nginx -y

# Clone and setup application
git clone https://github.com/Shillz96/ai-book-agent.git
cd ai-book-agent

# Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install
npm run build

# Copy built frontend to backend static directory
cp -r build/* ../backend/static/

# Create systemd service
sudo nano /etc/systemd/system/ai-book-agent.service
```

**Systemd Service File** (`/etc/systemd/system/ai-book-agent.service`):
```ini
[Unit]
Description=AI Book Marketing Agent
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/home/your-user/ai-book-agent/backend
Environment=PATH=/home/your-user/ai-book-agent/backend/venv/bin
EnvironmentFile=/home/your-user/ai-book-agent/.env.production
ExecStart=/home/your-user/ai-book-agent/backend/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### Nginx Configuration
Create `/etc/nginx/sites-available/ai-book-agent`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Optional: serve static files directly through nginx
    location /static/ {
        alias /home/your-user/ai-book-agent/backend/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/ai-book-agent /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### SSL Certificate with Let's Encrypt
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

### Start the Service
```bash
sudo systemctl enable ai-book-agent
sudo systemctl start ai-book-agent
sudo systemctl status ai-book-agent
```

## 📊 Production Monitoring

### Health Check Endpoints
- Basic health: `https://your-domain.com/api/health`
- Detailed status: `https://your-domain.com/api/health/detailed`

### Log Monitoring
```bash
# View application logs
sudo journalctl -u ai-book-agent -f

# View nginx access logs
sudo tail -f /var/log/nginx/access.log

# View nginx error logs
sudo tail -f /var/log/nginx/error.log
```

### Performance Monitoring
Consider integrating:
- **Sentry** for error tracking
- **DataDog** or **New Relic** for application monitoring
- **Grafana** + **Prometheus** for metrics visualization

## 🔒 Production Security

### Environment Security
- Never commit `.env` files to version control
- Use secrets management (AWS Secrets Manager, etc.)
- Rotate API keys regularly
- Use HTTPS in production

### Firebase Security
- Configure Firestore security rules
- Enable audit logging
- Use least-privilege service account permissions

### Server Security
- Keep system updated
- Configure firewall (UFW)
- Use fail2ban for intrusion prevention
- Regular security audits

## 🔄 CI/CD Pipeline

The project includes GitHub Actions workflows:

### Automatic Deployment
1. Push to `main` branch triggers deployment
2. Runs tests automatically
3. Builds and deploys to your chosen platform

### Manual Deployment
```bash
# Trigger manual deployment
gh workflow run deploy.yml
```

## 📈 Scaling Considerations

### Horizontal Scaling
- Use load balancer (nginx, CloudFlare)
- Deploy multiple instances
- Implement Redis for session storage

### Database Scaling
- Firebase Firestore auto-scales
- Consider read replicas for high traffic
- Implement proper indexing

### Cost Optimization
- Monitor OpenAI API usage
- Implement request caching
- Use cheaper models for non-critical operations

## 🆘 Production Troubleshooting

### Common Issues
1. **Health check fails**: Check environment variables and credentials
2. **High OpenAI costs**: Monitor usage and implement rate limiting
3. **Firebase errors**: Verify credentials and project permissions
4. **Memory issues**: Increase instance size or optimize code

### Getting Help
- Check health endpoints for detailed error information
- Review application logs for stack traces
- Monitor resource usage (CPU, memory, disk)
- Test configuration with validation endpoints

## 🎯 Post-Deployment

### Initial Setup
1. Access the web interface at your domain
2. Complete the onboarding process
3. Configure your API keys through the settings page
4. Test content generation and posting
5. Enable autonomous mode when ready

### Ongoing Maintenance
- Monitor performance metrics weekly
- Review and optimize content performance
- Update API keys before expiration
- Scale resources based on usage patterns

**Your AI Book Marketing Agent is now running in production! 🚀**

For support, check the health endpoints and review the logs. The system includes comprehensive error handling and monitoring to help you identify and resolve any issues quickly. 
# AI Book Marketing Agent

An autonomous AI agent designed to market the book "Unstoppable - the young athlete's guide to rock solid mental strength" with the primary goal of generating sales on Amazon and Audible.

## 🎯 Project Goals

- **Primary Goal**: Drive consistent book sales through automated marketing
- **Autonomy**: Self-managing agent that executes full-scale marketing strategy
- **Channels**: Twitter, Facebook, Instagram, Pinterest (daily posts), Google Ads
- **Budget Management**: Operate within predefined monthly marketing budget
- **Optimization**: Continuous learning and strategy refinement

## 🚀 Tech Stack

- **Backend**: Python (Flask/FastAPI)
- **Frontend**: React with Tailwind CSS and shadcn/ui
- **Database**: Firestore
- **AI/ML**: Gemini API for content generation
- **Integrations**: Google Analytics, Google Ads, Social Media APIs

## 📁 Project Structure

```
AI-BOOK-AGENT/
├── docs/                    # Project documentation
├── backend/                 # Python backend application
│   ├── app/
│   ├── config/
│   ├── requirements.txt
│   └── main.py
├── frontend/               # React frontend application
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── tailwind.config.js
├── database/               # Database schemas and migrations
├── scripts/                # Utility scripts
└── README.md
```

## 🏗️ Development Phases

### Phase 1: MVP - Automated Posting & Basic Tracking
- Content generation (AI-assisted)
- Scheduled posting to social media
- Basic Google Analytics integration
- Human-in-the-loop approval system

### Phase 2: Ad Management & Enhanced Analytics
- Google Ads integration
- Advanced metric tracking
- Automated reporting
- Budget allocation rules

### Phase 3: Learning & Autonomous Optimization
- Performance analysis engine
- AI-driven strategy refinement
- A/B testing framework
- Reduced human oversight

### Phase 4: Scaling & Advanced Features
- Predictive analytics
- Advanced audience segmentation
- Email marketing integration
- Competitor analysis

## 🚦 Getting Started

1. **Setup Environment**
   ```bash
   # Backend setup
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   
   # Frontend setup
   cd frontend
   npm install
   ```

2. **Configure APIs**
   - Set up Firebase project
   - Configure Google Analytics
   - Set up Google Ads API
   - Configure social media API keys

3. **Run Development Servers**
   ```bash
   # Backend (in backend/ directory)
   python main.py
   
   # Frontend (in frontend/ directory)
   npm start
   ```

## 📋 Core Requirements

- Drive consistent book sales
- Manage and execute full-scale marketing strategy
- Continuously learn and adapt
- Track and analyze metrics
- Generate weekly performance reports
- Stay on-brand targeting youth athletes, parents, and coaches

## 🤝 Human-in-the-Loop

The system includes capabilities for human approvals and strategy tweaks, especially in early stages, with the long-term goal of becoming fully autonomous.

## 📈 Success Metrics

- Monthly sales growth
- ROAS (Return on Ad Spend)
- Cost per acquisition
- Engagement rates across platforms
- Traffic to book landing pages 
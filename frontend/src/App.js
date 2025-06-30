// Essential imports for React functionality
import React, { useState, useEffect, createContext } from 'react';

// Import the new CustomModal component
import CustomModal from './CustomModal';

// Import the new Settings component
import Settings from './Settings';

// Import the new OnboardingGuide component
import OnboardingGuide from './OnboardingGuide';

// Firebase App initialization
import { initializeApp } from 'firebase/app';

// Firebase Auth imports for authentication handling
import { 
  getAuth, 
  connectAuthEmulator, 
  signInWithCustomToken, 
  onAuthStateChanged,
  signInAnonymously
  // signOut - removed as it's not currently used
} from 'firebase/auth';

// Firebase Firestore imports for database operations
import { 
  getFirestore, 
  doc, 
  getDoc, 
  setDoc, 
  updateDoc,
  deleteDoc,
  collection, 
  onSnapshot, 
  query, 
  serverTimestamp,
  addDoc 
} from 'firebase/firestore';

// Firebase Context for providing Firebase services throughout the app
const FirebaseContext = createContext(null);

// Main App component
function App() {
  // State initialization for Firebase services and app data
  const [firebaseApp, setFirebaseApp] = useState(null);
  const [db, setDb] = useState(null);
  const [auth, setAuth] = useState(null);
  const [userId, setUserId] = useState(null);
  const [loading, setLoading] = useState(true); // Initial loading state
  const [bookSettings, setBookSettings] = useState(null);
  const [pendingPosts, setPendingPosts] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [modalMessage, setModalMessage] = useState('');
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingPost, setEditingPost] = useState(null);
  const [editContent, setEditContent] = useState('');
  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const [editingSettings, setEditingSettings] = useState({});

  // New Settings Modal State
  const [showConfigSettingsModal, setShowConfigSettingsModal] = useState(false);

  // Onboarding Guide State
  const [showOnboardingGuide, setShowOnboardingGuide] = useState(false);
  const [isFirstTimeUser, setIsFirstTimeUser] = useState(true);
  const [onboardingCompleted, setOnboardingCompleted] = useState(false);

  // New state variables for Revenue Growth Management features
  const [revenueAnalysis, setRevenueAnalysis] = useState(null);
  const [performanceData, setPerformanceData] = useState(null);
  const [abTestResults, setAbTestResults] = useState([]);
  const [churnAnalysis, setChurnAnalysis] = useState(null);
  const [pricingOptimization, setPricingOptimization] = useState(null);
  const [contentPrediction, setContentPrediction] = useState(null);
  const [showRevenueModal, setShowRevenueModal] = useState(false);
  const [showAnalyticsModal, setShowAnalyticsModal] = useState(false);
  const [showABTestModal, setShowABTestModal] = useState(false);
  const [showPricingModal, setShowPricingModal] = useState(false);
  const [loading_revenue, setLoadingRevenue] = useState(false);
  const [loading_analytics, setLoadingAnalytics] = useState(false);

  // New state variables for Budget Management
  const [budgetStatus, setBudgetStatus] = useState(null);
  const [budgetForecast, setBudgetForecast] = useState(null);
  const [showBudgetModal, setShowBudgetModal] = useState(false);
  const [loading_budget, setLoadingBudget] = useState(false);

  // New state variables for Autonomous Operations
  const [autonomousStatus, setAutonomousStatus] = useState(null);
  const [showAutonomousModal, setShowAutonomousModal] = useState(false);
  const [loading_autonomous, setLoadingAutonomous] = useState(false);

  // New state variables for Google Ads Management
  const [adsData, setAdsData] = useState(null);
  const [showAdsModal, setShowAdsModal] = useState(false);
  const [loading_ads, setLoadingAds] = useState(false);

  // New state variables for Platform Status
  const [platformStatus, setPlatformStatus] = useState(null);
  const [showPlatformModal, setShowPlatformModal] = useState(false);
  const [loading_platform, setLoadingPlatform] = useState(false);

  // New state variables for Weekly Reports
  const [weeklyReport, setWeeklyReport] = useState(null);
  const [showReportModal, setShowReportModal] = useState(false);
  const [loading_report, setLoadingReport] = useState(false);

  // API Base URL for backend calls
  const API_BASE_URL = 'http://localhost:5000/api';

  // Helper function to make API calls with error handling
  const makeAPICall = async (endpoint, data = null, method = 'POST') => {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: data ? JSON.stringify(data) : null
      });

      const result = await response.json();
      
      if (!response.ok) {
        throw new Error(result.error || `HTTP error! status: ${response.status}`);
      }
      
      return result;
    } catch (error) {
      console.error(`API call failed for ${endpoint}:`, error);
      throw error;
    }
  };

  // ====== ONBOARDING FUNCTIONS ======

  /**
   * Check if user is first-time and show onboarding if needed
   */
  const checkFirstTimeUser = async () => {
    if (!userId || !db) return;

    try {
      const { getDoc, doc } = await import('firebase/firestore');
      const userRef = doc(db, 'users', userId);
      const userSnap = await getDoc(userRef);
      
      if (!userSnap.exists()) {
        // New user - show onboarding
        setIsFirstTimeUser(true);
        setShowOnboardingGuide(true);
      } else {
        const userData = userSnap.data();
        const hasCompletedOnboarding = userData.onboardingCompleted || false;
        
        if (!hasCompletedOnboarding) {
          setShowOnboardingGuide(true);
        }
        
        setIsFirstTimeUser(false);
        setOnboardingCompleted(hasCompletedOnboarding);
      }
    } catch (error) {
      console.error('Error checking first-time user:', error);
    }
  };

  /**
   * Complete onboarding process
   */
  const completeOnboarding = async () => {
    if (!userId || !db) return;

    try {
      const { setDoc, doc, serverTimestamp } = await import('firebase/firestore');
      const userRef = doc(db, 'users', userId);
      
      await setDoc(userRef, {
        onboardingCompleted: true,
        onboardingCompletedAt: serverTimestamp(),
        firstLoginAt: serverTimestamp()
      }, { merge: true });
      
      setOnboardingCompleted(true);
      setShowOnboardingGuide(false);
      
      showCustomModal('🎉 Welcome! Your AI Book Marketing Agent is ready to start promoting your book. Go to Settings to configure your API keys.');
    } catch (error) {
      console.error('Error completing onboarding:', error);
      showCustomModal('❌ Error completing onboarding. Please try again.');
    }
  };

  /**
   * Show onboarding guide manually
   */
  const showOnboardingManually = () => {
    setShowOnboardingGuide(true);
  };

  // ====== BUDGET MANAGEMENT FUNCTIONS ======

  /**
   * Get current budget status and spending
   */
  const getBudgetStatus = async () => {
    if (!userId) {
      showCustomModal("User not authenticated.");
      return;
    }

    setLoadingBudget(true);
    try {
      const result = await makeAPICall('/budget/status', null, 'GET');
      setBudgetStatus(result);
      setShowBudgetModal(true);
    } catch (error) {
      showCustomModal(`❌ Error getting budget status: ${error.message}`);
    } finally {
      setLoadingBudget(false);
    }
  };

  /**
   * Optimize budget allocation across platforms
   */
  const optimizeBudgetAllocation = async () => {
    if (!userId) {
      showCustomModal("User not authenticated.");
      return;
    }

    try {
      const result = await makeAPICall('/budget/optimize', {
        user_id: userId,
        app_id: window.__app_id || 'default-app-id'
      });
      
      showCustomModal(`✅ Budget optimization complete!\n\nRecommended allocation:\n${JSON.stringify(result.optimization, null, 2)}`);
      
      // Refresh budget status
      getBudgetStatus();
    } catch (error) {
      showCustomModal(`❌ Error optimizing budget: ${error.message}`);
    }
  };

  /**
   * Get budget forecast for next period
   */
  const getBudgetForecast = async () => {
    if (!userId) {
      showCustomModal("User not authenticated.");
      return;
    }

    try {
      const result = await makeAPICall('/budget/forecast', null, 'GET');
      setBudgetForecast(result);
      showCustomModal(`📊 Budget Forecast:\n\nProjected spend: $${result.projected_spend}\nProjected ROI: ${result.projected_roi}x\nRecommended budget: $${result.recommended_budget}`);
    } catch (error) {
      showCustomModal(`❌ Error getting budget forecast: ${error.message}`);
    }
  };

  // ====== AUTONOMOUS OPERATIONS FUNCTIONS ======

  /**
   * Start autonomous marketing operations
   */
  const startAutonomousOperation = async () => {
    if (!userId) {
      showCustomModal("User not authenticated.");
      return;
    }

    setLoadingAutonomous(true);
    try {
      const result = await makeAPICall('/autonomous/start', {
        user_id: userId,
        app_id: window.__app_id || 'default-app-id'
      });
      
      showCustomModal(`🚀 Autonomous marketing started!\n\nStatus: ${result.status}\nScheduled tasks: ${result.scheduled_tasks || 0}`);
      
      // Refresh autonomous status
      getAutonomousStatus();
    } catch (error) {
      showCustomModal(`❌ Error starting autonomous operation: ${error.message}`);
    } finally {
      setLoadingAutonomous(false);
    }
  };

  /**
   * Stop autonomous marketing operations
   */
  const stopAutonomousOperation = async () => {
    if (!userId) {
      showCustomModal("User not authenticated.");
      return;
    }

    try {
      const result = await makeAPICall('/autonomous/stop', {
        user_id: userId,
        app_id: window.__app_id || 'default-app-id'
      });
      
      showCustomModal(`⏹️ Autonomous marketing stopped!\n\nStatus: ${result.status}`);
      
      // Refresh autonomous status
      getAutonomousStatus();
    } catch (error) {
      showCustomModal(`❌ Error stopping autonomous operation: ${error.message}`);
    }
  };

  /**
   * Get autonomous operation status
   */
  const getAutonomousStatus = async () => {
    if (!userId) {
      showCustomModal("User not authenticated.");
      return;
    }

    try {
      const result = await makeAPICall('/autonomous/status', null, 'GET');
      setAutonomousStatus(result);
      setShowAutonomousModal(true);
    } catch (error) {
      showCustomModal(`❌ Error getting autonomous status: ${error.message}`);
    }
  };

  /**
   * Execute daily autonomous operations manually
   */
  const executeDailyOperations = async () => {
    if (!userId) {
      showCustomModal("User not authenticated.");
      return;
    }

    try {
      const result = await makeAPICall('/autonomous/execute-daily', {
        user_id: userId,
        app_id: window.__app_id || 'default-app-id'
      });
      
      showCustomModal(`✅ Daily operations executed!\n\nTasks completed: ${result.tasks_completed || 0}\nPosts generated: ${result.posts_generated || 0}`);
    } catch (error) {
      showCustomModal(`❌ Error executing daily operations: ${error.message}`);
    }
  };

  // ====== GOOGLE ADS FUNCTIONS ======

  /**
   * Create a new Google Ads campaign
   */
  const createAdsCampaign = async () => {
    if (!userId) {
      showCustomModal("User not authenticated.");
      return;
    }

    setLoadingAds(true);
    try {
      const campaignData = {
        user_id: userId,
        app_id: window.__app_id || 'default-app-id',
        campaign_name: `Book Marketing Campaign - ${new Date().toLocaleDateString()}`,
        budget: bookSettings?.monthlyBudget || 500,
        target_audience: bookSettings?.targetAudience || 'youth athletes, parents, coaches',
        keywords: ['mental strength', 'youth sports', 'athlete development', 'sports psychology'],
        ad_copy: {
          headline: 'Unstoppable Mental Strength for Young Athletes',
          description: 'Transform your young athlete\'s mindset with proven strategies for peak performance and resilience.'
        }
      };

      const result = await makeAPICall('/ads/create-campaign', campaignData);
      setAdsData(result);
      setShowAdsModal(true);
      
      showCustomModal(`🎯 Google Ads campaign created!\n\nCampaign ID: ${result.campaign_id}\nStatus: ${result.status}`);
    } catch (error) {
      showCustomModal(`❌ Error creating ads campaign: ${error.message}`);
    } finally {
      setLoadingAds(false);
    }
  };

  /**
   * Optimize existing Google Ads campaign
   */
  const optimizeAdsCampaign = async () => {
    if (!userId) {
      showCustomModal("User not authenticated.");
      return;
    }

    try {
      const result = await makeAPICall('/ads/optimize-campaign', {
        user_id: userId,
        app_id: window.__app_id || 'default-app-id',
        campaign_id: adsData?.campaign_id
      });
      
      showCustomModal(`🔧 Campaign optimization complete!\n\nOptimizations applied: ${result.optimizations_applied || 0}\nExpected improvement: ${result.expected_improvement || 'TBD'}`);
    } catch (error) {
      showCustomModal(`❌ Error optimizing campaign: ${error.message}`);
    }
  };

  // ====== PLATFORM TESTING FUNCTIONS ======

  /**
   * Get status of all social media platforms
   */
  const getPlatformStatus = async () => {
    if (!userId) {
      showCustomModal("User not authenticated.");
      return;
    }

    setLoadingPlatform(true);
    try {
      const result = await makeAPICall('/platform-status', null, 'GET');
      setPlatformStatus(result);
      setShowPlatformModal(true);
    } catch (error) {
      showCustomModal(`❌ Error getting platform status: ${error.message}`);
    } finally {
      setLoadingPlatform(false);
    }
  };

  /**
   * Test a specific social media platform
   */
  const testPlatform = async (platform) => {
    if (!userId) {
      showCustomModal("User not authenticated.");
      return;
    }

    try {
      const result = await makeAPICall(`/test-platform/${platform}`, null, 'GET');
      
      showCustomModal(`🧪 Platform Test Results - ${platform.toUpperCase()}\n\nStatus: ${result.status}\nAPI Connection: ${result.api_connected ? '✅' : '❌'}\nLast Test: ${result.last_test_time}`);
    } catch (error) {
      showCustomModal(`❌ Error testing ${platform}: ${error.message}`);
    }
  };

  // ====== ANALYTICS FUNCTIONS ======

  /**
   * Get comprehensive marketing metrics
   */
  const getMarketingMetrics = async () => {
    if (!userId) {
      showCustomModal("User not authenticated.");
      return;
    }

    setLoadingAnalytics(true);
    try {
      const result = await makeAPICall('/analytics/marketing-metrics', {
        user_id: userId,
        app_id: window.__app_id || 'default-app-id',
        date_range: '30d'
      });
      
      setPerformanceData(result);
      setShowAnalyticsModal(true);
    } catch (error) {
      showCustomModal(`❌ Error getting marketing metrics: ${error.message}`);
    } finally {
      setLoadingAnalytics(false);
    }
  };

  /**
   * Get social media attribution data
   */
  const getSocialAttribution = async () => {
    if (!userId) {
      showCustomModal("User not authenticated.");
      return;
    }

    try {
      const result = await makeAPICall('/analytics/social-attribution', null, 'GET');
      
      showCustomModal(`📊 Social Media Attribution:\n\nTop performing platform: ${result.top_platform}\nTotal conversions: ${result.total_conversions}\nAttribution breakdown: ${JSON.stringify(result.attribution, null, 2)}`);
    } catch (error) {
      showCustomModal(`❌ Error getting social attribution: ${error.message}`);
    }
  };

  // ====== REPORTING FUNCTIONS ======

  /**
   * Generate weekly marketing report
   */
  const generateWeeklyReport = async () => {
    if (!userId) {
      showCustomModal("User not authenticated.");
      return;
    }

    setLoadingReport(true);
    try {
      const result = await makeAPICall('/reports/weekly', {
        user_id: userId,
        app_id: window.__app_id || 'default-app-id',
        include_recommendations: true
      });
      
      setWeeklyReport(result);
      setShowReportModal(true);
    } catch (error) {
      showCustomModal(`❌ Error generating weekly report: ${error.message}`);
    } finally {
      setLoadingReport(false);
    }
  };

  // ====== EXISTING FUNCTIONS (keeping existing functionality) ======

  // Function to analyze revenue performance
  const analyzeRevenuePerformance = async () => {
    if (!userId) {
      showCustomModal("User not authenticated.");
      return;
    }

    setLoadingRevenue(true);
    try {
      const result = await makeAPICall('/revenue-analysis', {
        user_id: userId,
        app_id: window.__app_id || 'default-app-id'
      });

      setRevenueAnalysis(result.analysis);
      setShowRevenueModal(true);
      
    } catch (error) {
      showCustomModal(`❌ Error analyzing revenue: ${error.message}`);
    } finally {
      setLoadingRevenue(false);
    }
  };

  // Function to optimize pricing strategy
  const optimizePricingStrategy = async () => {
    if (!userId) {
      showCustomModal("User not authenticated.");
      return;
    }

    try {
      // Get current metrics from bookSettings or use defaults
      const currentMetrics = {
        monthly_sales: bookSettings?.estimatedMonthlySales || 5000.0,
        growth_rate: 0.12,
        customer_acquisition_cost: 25.0,
        customer_lifetime_value: 150.0,
        churn_rate: 0.03,
        conversion_rate: 0.025,
        average_order_value: bookSettings?.bookPrice || 24.99
      };

      const result = await makeAPICall('/optimize-pricing', {
        user_id: userId,
        app_id: window.__app_id || 'default-app-id',
        current_metrics: currentMetrics,
        market_data: {}
      });

      setPricingOptimization(result.optimization);
      setShowPricingModal(true);
      
    } catch (error) {
      showCustomModal(`❌ Error optimizing pricing: ${error.message}`);
    }
  };

  // Function to predict and prevent churn
  const predictAndPreventChurn = async () => {
    if (!userId) {
      showCustomModal("User not authenticated.");
      return;
    }

    try {
      const result = await makeAPICall('/churn-prevention', {
        user_id: userId,
        app_id: window.__app_id || 'default-app-id'
      });

      setChurnAnalysis(result.churn_prevention);
      showCustomModal(`🛡️ Churn Prevention Analysis Complete!\n\nPrevention Score: ${(result.churn_prevention.prevention_score * 100).toFixed(1)}%\n\nAutomated retention strategies have been activated based on AI analysis.`);
      
    } catch (error) {
      showCustomModal(`❌ Error in churn prevention: ${error.message}`);
    }
  };

  // Function to analyze content performance
  const analyzeContentPerformance = async () => {
    if (!userId) {
      showCustomModal("User not authenticated.");
      return;
    }

    setLoadingAnalytics(true);
    try {
      const result = await makeAPICall('/performance-analysis', {
        user_id: userId,
        app_id: window.__app_id || 'default-app-id',
        time_range_days: 30
      });

      setPerformanceData(result.performance_analysis);
      setShowAnalyticsModal(true);
      
    } catch (error) {
      showCustomModal(`❌ Error analyzing performance: ${error.message}`);
    } finally {
      setLoadingAnalytics(false);
    }
  };

  // Function to predict content performance
  const predictContentPerformance = async (content, platform = 'instagram') => {
    if (!userId) {
      showCustomModal("User not authenticated.");
      return;
    }

    try {
      const result = await makeAPICall('/predict-performance', {
        content_data: {
          content: content,
          content_type: 'text',
          scheduled_time: new Date().toISOString()
        },
        platform: platform
      });

      setContentPrediction(result.prediction);
      
      const confidence = (result.prediction.confidence_score * 100).toFixed(1);
      showCustomModal(`🔮 Content Performance Prediction:\n\nConfidence Score: ${confidence}%\n\n${result.prediction.ai_predictions}\n\nOptimization suggestions available in detailed view.`);
      
    } catch (error) {
      showCustomModal(`❌ Error predicting performance: ${error.message}`);
    }
  };

  // Function to set up A/B test
  const setupABTest = async (contentBase, testDimension = 'tone', platforms = ['instagram', 'facebook']) => {
    if (!userId) {
      showCustomModal("User not authenticated.");
      return;
    }

    try {
      const result = await makeAPICall('/ab-test', {
        user_id: userId,
        app_id: window.__app_id || 'default-app-id',
        test_config: {
          content_base: contentBase,
          test_dimension: testDimension,
          target_metric: 'engagement_rate',
          platforms: platforms
        }
      });

      setAbTestResults(prev => [...prev, result.ab_test]);
      setShowABTestModal(true);
      
      showCustomModal(`🧪 A/B Test Created!\n\nTest ID: ${result.ab_test.test_id}\n\nVariants: ${result.ab_test.variants.length}\n\nExpected Duration: ${result.ab_test.expected_duration}\n\nTracking has been activated automatically.`);
      
    } catch (error) {
      showCustomModal(`❌ Error setting up A/B test: ${error.message}`);
    }
  };

  // Function to generate comprehensive performance report
  const generatePerformanceReport = async (period = 'monthly') => {
    if (!userId) {
      showCustomModal("User not authenticated.");
      return;
    }

    try {
      const result = await makeAPICall('/performance-report', {
        user_id: userId,
        app_id: window.__app_id || 'default-app-id',
        report_period: period
      });

      const report = result.report;
      const reportText = `📊 ${period.toUpperCase()} PERFORMANCE REPORT\n\n` +
        `${report.executive_summary}\n\n` +
        `📈 KEY METRICS:\n` +
        `• Revenue Growth: ${JSON.stringify(report.kpis)}\n\n` +
        `🎯 NEXT PERIOD RECOMMENDATIONS:\n` +
        `${JSON.stringify(report.next_period_recommendations)}`;

      showCustomModal(reportText);
      
    } catch (error) {
      showCustomModal(`❌ Error generating report: ${error.message}`);
    }
  };

  // Enhanced function to analyze performance with new AI features
  const analyzePerformanceEnhanced = async () => {
    if (!db || !userId) {
      showCustomModal("Database connection not available.");
      return;
    }

    try {
      // Show loading state
      showCustomModal("🤖 Running comprehensive AI performance analysis...");
      
      // Run multiple AI analyses in parallel
      await Promise.all([
        analyzeRevenuePerformance(),
        analyzeContentPerformance(),
        predictAndPreventChurn()
      ]);

      // Generate summary report
      await generatePerformanceReport('weekly');
      
    } catch (error) {
      console.error('Error in enhanced performance analysis:', error);
      showCustomModal(`❌ Error in enhanced analysis: ${error.message}`);
    }
  };

  // Original analyze performance function (maintained for backwards compatibility)
  const analyzePerformance = async () => {
    if (!db || !userId) {
      showCustomModal("Database connection not available.");
      return;
    }

    try {
      // Simulate performance analysis
      const metrics = {
        totalPosts: Math.floor(Math.random() * 50) + 20,
        avgEngagement: (Math.random() * 5 + 2).toFixed(1),
        reachIncrease: (Math.random() * 30 + 10).toFixed(1),
        conversionRate: (Math.random() * 3 + 1).toFixed(2)
      };

      const performanceReport = `📊 PERFORMANCE ANALYSIS\n\n` +
        `📈 Total Posts Published: ${metrics.totalPosts}\n` +
        `👥 Average Engagement Rate: ${metrics.avgEngagement}%\n` +
        `📢 Reach Increase: +${metrics.reachIncrease}%\n` +
        `💰 Conversion Rate: ${metrics.conversionRate}%\n\n` +
        `🎯 Key Insights:\n` +
        `• Morning posts perform 23% better\n` +
        `• Video content gets 2.3x more engagement\n` +
        `• Hashtag #MentalToughness drives highest reach\n\n` +
        `💡 Recommendations:\n` +
        `• Schedule more content for 8-10 AM\n` +
        `• Create video testimonials\n` +
        `• Focus on motivational content themes`;

      showCustomModal(performanceReport);
      
    } catch (error) {
      console.error('Error analyzing performance:', error);
      showCustomModal(`❌ Error analyzing performance: ${error.message}`);
    }
  };

  // Helper function to update book settings with Unstoppable book information
  const updateToUnstoppableSettings = async () => {
    // Open settings editor instead of hardcoded update
    if (bookSettings) {
      setEditingSettings({ ...bookSettings });
    } else {
      // Set default values if no settings exist
      setEditingSettings({
        bookTitle: 'Unstoppable: Young Athletes Mental Strength',
        bookAuthor: 'Author Name',
        amazonLink: 'https://www.amazon.com/Unstoppable-young-athletes-mental-strength/dp/B0BBJ56YYQ',
        audibleLink: 'https://audible.com/pd/B0BBJ56YYQ',
        landingPageUrl: 'https://your-book-website.com',
        monthlyBudget: 2500,
        contentGuidelines: 'Focus on mental strength, resilience, and peak performance for young athletes. Use motivational and inspiring tone. Target parents, coaches, and young athletes aged 12-18. Emphasize growth mindset, confidence building, and overcoming challenges in youth sports.',
        humanInLoopEnabled: true,
        targetAudience: 'Parents of young athletes, youth coaches, high school athletes, sports psychologists',
        bookGenre: 'Sports Psychology / Youth Development',
        keyThemes: 'Mental toughness, resilience, confidence, goal setting, pressure management, youth sports',
        marketingTone: 'Motivational, professional, inspiring, empowering'
      });
    }
    setShowSettingsModal(true);
  };

  // Helper function to show custom modal with message
  const showCustomModal = (message) => {
    setModalMessage(message);
    setShowModal(true);
  };

  // Function to generate new marketing posts
  const generateNewPosts = async () => {
    if (!db || !userId) {
      showCustomModal("Database connection not available. Please refresh the page.");
      return;
    }

    try {
      showCustomModal("🤖 Generating new marketing posts... This may take a moment.");
      
      const appId = window.__app_id || 'default-app-id';
      const postsColRef = collection(db, 'artifacts', appId, 'users', userId, 'posts');
      
      // Sample marketing posts based on book settings
      const samplePosts = [
        {
          platform: 'Twitter',
          content: `🏆 Unlock your young athlete's mental strength! ${bookSettings?.bookTitle || 'Unstoppable'} teaches resilience, confidence, and peak performance. Perfect for parents and coaches! 💪 #YouthSports #MentalToughness #ParentingTips`,
          status: 'pending_approval',
          createdAt: serverTimestamp(),
          scheduledFor: null,
          mediaUrl: null
        },
        {
          platform: 'Facebook',
          content: `Does your young athlete struggle with pressure during games? 🤔\n\n${bookSettings?.bookTitle || 'Unstoppable'} provides proven strategies to help young athletes:\n✅ Build unshakeable confidence\n✅ Handle pressure like a pro\n✅ Bounce back from setbacks\n✅ Develop a champion mindset\n\nGet your copy today and watch your athlete thrive! 🌟`,
          status: 'pending_approval',
          createdAt: serverTimestamp(),
          scheduledFor: null,
          mediaUrl: null
        },
        {
          platform: 'Instagram',
          content: `Mental toughness isn't just for pro athletes! 💯\n\nEvery young athlete can develop:\n🧠 Focus under pressure\n💪 Resilience after defeats\n🎯 Goal-setting skills\n🏆 Champion confidence\n\nStart their journey with ${bookSettings?.bookTitle || 'Unstoppable'} today!\n\n#YouthAthletes #MentalStrength #SportsParents #Coaching`,
          status: 'pending_approval',
          createdAt: serverTimestamp(),
          scheduledFor: null,
          mediaUrl: null
        }
      ];

      // Add posts to Firestore
      for (const post of samplePosts) {
        await addDoc(postsColRef, post);
      }
      
      showCustomModal("✅ Successfully generated 3 new marketing posts! Check the pending approvals section below.");
      
    } catch (error) {
      console.error('Error generating posts:', error);
      showCustomModal(`❌ Error generating posts: ${error.message}`);
    }
  };

  // Function to approve and schedule a post
  const approvePost = async (postId, postContent) => {
    if (!db || !userId) {
      showCustomModal("Database connection not available.");
      return;
    }

    try {
      const appId = window.__app_id || 'default-app-id';
      const postRef = doc(db, 'artifacts', appId, 'users', userId, 'posts', postId);
      
      // Calculate schedule time (e.g., within next 24 hours)
      const scheduleTime = new Date();
      scheduleTime.setHours(scheduleTime.getHours() + Math.floor(Math.random() * 24) + 1);
      
      await updateDoc(postRef, {
        status: 'approved',
        approvedAt: serverTimestamp(),
        scheduledFor: scheduleTime,
        lastModified: serverTimestamp()
      });
      
      showCustomModal(`✅ Post approved and scheduled for ${scheduleTime.toLocaleString()}!`);
      
    } catch (error) {
      console.error('Error approving post:', error);
      showCustomModal(`❌ Error approving post: ${error.message}`);
    }
  };

  // Function to discard a post
  const discardPost = async (postId, postContent) => {
    if (!db || !userId) {
      showCustomModal("Database connection not available.");
      return;
    }

    try {
      const appId = window.__app_id || 'default-app-id';
      const postRef = doc(db, 'artifacts', appId, 'users', userId, 'posts', postId);
      
      await deleteDoc(postRef);
      showCustomModal("🗑️ Post discarded successfully!");
      
    } catch (error) {
      console.error('Error discarding post:', error);
      showCustomModal(`❌ Error discarding post: ${error.message}`);
    }
  };

  // Function to start editing a post
  const startEditPost = (post) => {
    setEditingPost(post);
    setEditContent(post.content);
    setShowEditModal(true);
  };

  // Function to save edited post
  const saveEditedPost = async () => {
    if (!db || !userId || !editingPost) {
      showCustomModal("Unable to save changes.");
      return;
    }

    try {
      const appId = window.__app_id || 'default-app-id';
      const postRef = doc(db, 'artifacts', appId, 'users', userId, 'posts', editingPost.id);
      
      await updateDoc(postRef, {
        content: editContent,
        lastModified: serverTimestamp()
      });
      
      setShowEditModal(false);
      setEditingPost(null);
      setEditContent('');
      showCustomModal("✅ Post updated successfully!");
      
    } catch (error) {
      console.error('Error updating post:', error);
      showCustomModal(`❌ Error updating post: ${error.message}`);
    }
  };

  // Function to view detailed reports
  const viewDetailedReports = async () => {
    if (!db || !userId) {
      showCustomModal("Database connection not available.");
      return;
    }

    try {
      // Simulate detailed report generation
      const report = `📋 DETAILED MARKETING REPORT\n\n` +
        `📅 Report Period: Last 30 days\n` +
        `📖 Book: ${bookSettings?.bookTitle || 'Unstoppable'}\n\n` +
        `🎯 PLATFORM PERFORMANCE:\n` +
        `• Instagram: 847 likes, 156 comments, 23 shares\n` +
        `• Facebook: 523 reactions, 89 comments, 45 shares\n` +
        `• Twitter: 234 retweets, 167 likes, 12 replies\n\n` +
        `💰 BUDGET ANALYSIS:\n` +
        `• Monthly Budget: $${bookSettings?.monthlyBudget || 2500}\n` +
        `• Spent This Month: $${(bookSettings?.monthlyBudget * 0.73).toFixed(2) || 1825}\n` +
        `• Cost Per Engagement: $2.34\n` +
        `• ROI: 187%\n\n` +
        `🔥 TOP PERFORMING CONTENT:\n` +
        `1. "Mental toughness tips for game day" - 1.2K engagements\n` +
        `2. "Building confidence in young athletes" - 987 engagements\n` +
        `3. "Overcoming sports anxiety" - 745 engagements\n\n` +
        `📈 GROWTH METRICS:\n` +
        `• Follower Growth: +12.3%\n` +
        `• Website Traffic: +34.7%\n` +
        `• Book Sales Inquiries: +28.9%`;

      showCustomModal(report);
      
    } catch (error) {
      console.error('Error generating report:', error);
      showCustomModal(`❌ Error generating report: ${error.message}`);
    }
  };

  // Function to save edited settings
  const saveEditedSettings = async () => {
    if (!db || !userId) {
      showCustomModal("Database connection not available.");
      return;
    }

    try {
      const appId = window.__app_id || 'default-app-id';
      const userSettingsRef = doc(db, 'artifacts', appId, 'users', userId, 'userSettings', 'settings');
      
      const updatedSettings = {
        ...editingSettings,
        lastUpdated: serverTimestamp()
      };

      await setDoc(userSettingsRef, updatedSettings);
      setBookSettings(updatedSettings);
      setShowSettingsModal(false);
      setEditingSettings({});
      
      showCustomModal("✅ Book settings updated successfully!");
      
    } catch (error) {
      console.error('Error updating book settings:', error);
      showCustomModal(`❌ Error updating settings: ${error.message}`);
    }
  };

  // Function to handle settings input changes
  const handleSettingsChange = (field, value) => {
    setEditingSettings(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Firebase initialization effect - runs once on component mount
  useEffect(() => {
    // Async function to initialize Firebase services
    const initializeFirebase = async () => {
      try {
        // Parse Firebase config from global variable or use empty object
        let firebaseConfig = {};
        try {
          firebaseConfig = window.__firebase_config ? 
            JSON.parse(window.__firebase_config) : {};
        } catch (error) {
          console.error('Error parsing Firebase config:', error);
          firebaseConfig = {};
        }

        // Configuration check - ensure Firebase config is not empty
        if (!firebaseConfig || Object.keys(firebaseConfig).length === 0) {
          showCustomModal("Firebase configuration is missing. Please check your environment settings.");
          setLoading(false);
          return; // Prevent further execution
        }

        // Initialize Firebase services
        console.log('Initializing Firebase with config:', firebaseConfig);
        const app = initializeApp(firebaseConfig);
        const firestoreDb = getFirestore(app);
        const firebaseAuth = getAuth(app);

        // Update state with initialized instances
        setFirebaseApp(app);
        setDb(firestoreDb);
        setAuth(firebaseAuth);

        // Authentication logic with comprehensive error handling
        console.log('Starting authentication process...');
        
        try {
          // Check if custom auth token is available
          if (window.__initial_auth_token) {
            console.log('Using custom auth token for sign-in');
            await signInWithCustomToken(firebaseAuth, window.__initial_auth_token);
          } else {
            console.log('Using anonymous sign-in');
            await signInAnonymously(firebaseAuth);
          }
        } catch (authError) {
          console.error('Authentication error:', authError);
          showCustomModal(`Authentication failed: ${authError.message}`);
          setLoading(false);
          return;
        }

        // Set up authentication state listener
        const unsubscribe = onAuthStateChanged(firebaseAuth, (user) => {
          if (user) {
            // User is signed in
            setUserId(user.uid);
            console.log("User signed in:", user.uid);
          } else {
            // User is signed out
            setUserId(null);
            console.log("User signed out.");
          }
          
          // Authentication is ready, stop loading
          setLoading(false);
        });

        // Return cleanup function for the auth listener
        return unsubscribe;

      } catch (error) {
        // Error handling for Firebase initialization
        console.error('Firebase initialization error:', error);
        showCustomModal(`Firebase initialization failed: ${error.message}`);
        setLoading(false);
      }
    };

    // Initialize Firebase and store cleanup function
    let unsubscribe;
    initializeFirebase().then((cleanup) => {
      unsubscribe = cleanup;
    });

    // Cleanup function for useEffect
    return () => {
      if (unsubscribe) {
        unsubscribe();
      }
    };
  }, []); // Empty dependency array - run once on mount

  // Data fetching effect for user settings and pending posts
  // This useEffect depends on db and userId and only runs when both are available
  useEffect(() => {
    // Only proceed if both db and userId are available
    if (!db || !userId) {
      return;
    }

    console.log('Setting up data fetching for user settings and pending posts...');

    // Check if user is first-time and show onboarding if needed
    checkFirstTimeUser();

    // Get app ID from global variable or use default
    const appId = window.__app_id || 'default-app-id';

    // Define Firestore references
    // User settings reference pointing to artifacts/${__app_id}/users/${userId}/userSettings/settings
    const userSettingsRef = doc(db, 'artifacts', appId, 'users', userId, 'userSettings', 'settings');
    
    // Pending posts collection reference pointing to artifacts/${__app_id}/users/${userId}/posts
    const pendingPostsColRef = collection(db, 'artifacts', appId, 'users', userId, 'posts');

    // Create Firestore query for pending posts (without orderBy to avoid index issues)
    const q = query(pendingPostsColRef);

    // Async function to fetch user settings with enhanced error handling
    const fetchSettings = async () => {
      try {
        console.log('Fetching user settings...');
        
        // Get user settings document
        const docSnap = await getDoc(userSettingsRef);
        
        if (docSnap.exists()) {
          // User settings exist, load them
          console.log('User settings found, loading...');
          setBookSettings(docSnap.data());
        } else {
          // First-time user, create default settings
          console.log('No user settings found, creating default settings...');
          
          // Define default settings object with values specific to "Unstoppable" book
          const defaultSettings = {
            bookTitle: 'Unstoppable: Young Athletes Mental Strength',
            bookAuthor: 'Author Name', // Update this with your actual name
            amazonLink: 'https://www.amazon.com/Unstoppable-young-athletes-mental-strength/dp/B0BBJ56YYQ',
            audibleLink: 'https://audible.com/pd/B0BBJ56YYQ', // Update if you have an Audible version
            landingPageUrl: 'https://your-book-website.com', // Update with your actual landing page
            monthlyBudget: 2500,
            contentGuidelines: 'Focus on mental strength, resilience, and peak performance for young athletes. Use motivational and inspiring tone. Target parents, coaches, and young athletes aged 12-18. Emphasize growth mindset, confidence building, and overcoming challenges in youth sports.',
            humanInLoopEnabled: true,
            // Additional settings specific to sports psychology book
            targetAudience: 'Parents of young athletes, youth coaches, high school athletes, sports psychologists',
            bookGenre: 'Sports Psychology / Youth Development', 
            keyThemes: 'Mental toughness, resilience, confidence, goal setting, pressure management, youth sports',
            marketingTone: 'Motivational, professional, inspiring, empowering',
            lastUpdated: serverTimestamp()
          };

          // Save default settings to Firestore with error handling
          try {
            await setDoc(userSettingsRef, defaultSettings);
            setBookSettings(defaultSettings);
            
            // Display custom modal message for first-time user
            showCustomModal("Default book settings initialized. Please update them!");
          } catch (setDocError) {
            console.error('Error saving default settings:', setDocError);
            showCustomModal(`Error saving default settings: ${setDocError.message}`);
          }
        }
      } catch (error) {
        // Error handling for settings fetch
        console.error('Error fetching user settings:', error);
        showCustomModal(`Error fetching user settings: ${error.message}`);
      }
    };

    // Set up real-time listener for pending posts with enhanced error handling
    console.log('Setting up pending posts listener...');
    const unsubscribePosts = onSnapshot(
      q,
      (snapshot) => {
        try {
          console.log('Received pending posts update, processing...');
          
          // Map snapshot documents to objects with id and data
          const allPosts = snapshot.docs.map(doc => ({
            id: doc.id,
            ...doc.data()
          }));

          // Filter posts to include only pending_approval or draft status
          const filteredPosts = allPosts.filter(post => 
            post.status === 'pending_approval' || post.status === 'draft'
          );

          // Sort filtered posts by createdAt in ascending order
          // Ensure createdAt exists and convert to Date if necessary
          const sortedPosts = filteredPosts.sort((a, b) => {
            const dateA = a.createdAt?.toDate ? a.createdAt.toDate() : new Date(a.createdAt || 0);
            const dateB = b.createdAt?.toDate ? b.createdAt.toDate() : new Date(b.createdAt || 0);
            return dateA - dateB; // Ascending order (oldest first)
          });

          console.log(`Found ${sortedPosts.length} pending posts`);
          setPendingPosts(sortedPosts);
        } catch (error) {
          console.error('Error processing pending posts snapshot:', error);
          showCustomModal(`Error processing pending posts: ${error.message}`);
        }
      },
      (error) => {
        // Error callback for onSnapshot listener
        console.error('Error listening to pending posts:', error);
        showCustomModal(`Error listening to pending posts: ${error.message}`);
      }
    );

    // Execute fetchSettings function
    fetchSettings();

    // Return cleanup function to unsubscribe from pending posts listener
    return () => {
      console.log('Cleaning up data fetching listeners...');
      unsubscribePosts();
    };
  }, [db, userId]); // Dependencies: db and userId

  // Loading state UI - show while Firebase is initializing with responsive design
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-100 p-4">
        <div className="text-center max-w-md w-full">
          {/* Loading spinner with proper accessibility */}
          <div 
            className="animate-spin rounded-full h-16 w-16 sm:h-24 sm:w-24 lg:h-32 lg:w-32 border-b-2 border-blue-500 mx-auto"
            role="status"
            aria-label="Loading Firebase services"
          ></div>
          <p className="mt-4 text-base sm:text-lg text-gray-600">Initializing Firebase services...</p>
          <p className="text-sm text-gray-500">Please wait while we set up your connection</p>
        </div>
      </div>
    );
  }

  // Main App UI - renders after Firebase initialization with enhanced responsiveness
  return (
    <FirebaseContext.Provider value={{ firebaseApp, db, auth, userId }}>
      {/* Overall Layout wrapper with responsive padding */}
      <div className="min-h-screen bg-gray-50 font-inter text-gray-800 p-2 sm:p-4 lg:p-8 flex flex-col items-center">
        
        {/* Main content area wrapper with responsive design */}
        <div className="w-full max-w-6xl bg-white rounded-xl shadow-lg p-4 sm:p-6 lg:p-8 mb-4 sm:mb-8">
          
          {/* Header with responsive typography */}
          <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-6 space-y-3 sm:space-y-0">
            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-extrabold text-blue-700">
              AI Marketing Dashboard
            </h1>
            {userId && (
              <div className="text-xs sm:text-sm text-gray-600 bg-blue-50 px-3 py-1 rounded-full self-start sm:self-center">
                User ID: <span className="font-mono text-blue-800">{userId.substring(0, 8)}...</span>
              </div>
            )}
          </div>

          {/* Grid Layout for Cards with enhanced responsive breakpoints */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6 mb-6 sm:mb-8">
            
            {/* Book Details Card with responsive design */}
            <div className="bg-gradient-to-br from-blue-50 to-indigo-100 p-4 sm:p-6 rounded-lg shadow-md">
              <h2 className="text-lg sm:text-xl font-bold text-blue-800 mb-4 flex items-center">
                {/* Book icon SVG with accessibility label */}
                <svg 
                  className="w-5 h-5 sm:w-6 sm:h-6 mr-2" 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24" 
                  xmlns="http://www.w3.org/2000/svg"
                  aria-label="Book icon"
                  role="img"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
                Book Details
              </h2>
              
              {/* Conditionally render book settings with responsive spacing */}
              {bookSettings ? (
                <div className="space-y-2 sm:space-y-3">
                  <div className="text-sm sm:text-base">
                    <span className="font-semibold">Title:</span> {bookSettings.bookTitle}
                  </div>
                  <div className="text-sm sm:text-base">
                    <span className="font-semibold">Author:</span> {bookSettings.bookAuthor}
                  </div>
                  <div className="text-sm sm:text-base">
                    <span className="font-semibold">Genre:</span> {bookSettings.bookGenre || 'Not specified'}
                  </div>
                  <div className="text-sm sm:text-base">
                    <span className="font-semibold">Target Audience:</span> {bookSettings.targetAudience || 'General'}
                  </div>
                  <div className="text-sm sm:text-base">
                    <span className="font-semibold">Amazon Link:</span>{' '}
                    <a 
                      href={bookSettings.amazonLink} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-800 underline break-all focus-ring"
                      aria-label={`Visit Amazon page: ${bookSettings.amazonLink}`}
                    >
                      View on Amazon
                    </a>
                  </div>
                  <div className="text-sm sm:text-base">
                    <span className="font-semibold">Landing Page:</span>{' '}
                    <a 
                      href={bookSettings.landingPageUrl} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-800 underline break-all focus-ring"
                      aria-label={`Visit landing page: ${bookSettings.landingPageUrl}`}
                    >
                      {bookSettings.landingPageUrl}
                    </a>
                  </div>
                  <div className="text-sm sm:text-base">
                    <span className="font-semibold">Monthly Budget:</span> ${bookSettings.monthlyBudget?.toFixed(2)}
                  </div>
                  <div className="text-sm sm:text-base">
                    <span className="font-semibold">Marketing Tone:</span> {bookSettings.marketingTone || 'Professional'}
                  </div>
                  <div className="text-sm sm:text-base">
                    <span className="font-semibold">Human-in-Loop:</span> {bookSettings.humanInLoopEnabled ? 'Enabled' : 'Disabled'}
                  </div>
                </div>
              ) : (
                <p className="text-gray-600 text-sm sm:text-base">Loading book settings or none found. Initializing default settings...</p>
              )}
              
              {/* Edit Settings button with responsive design */}
              <button
                onClick={updateToUnstoppableSettings}
                className="mt-4 w-full sm:w-auto bg-blue-500 text-white py-2 px-4 rounded-md hover:bg-blue-600 transition duration-150 ease-in-out shadow-md focus-ring text-sm sm:text-base"
                aria-label="Edit book settings"
              >
                Edit Settings
              </button>
            </div>

            {/* AI Agent Status Card with responsive design */}
            <div className="bg-gradient-to-br from-purple-50 to-pink-100 p-4 sm:p-6 rounded-lg shadow-md">
              <h2 className="text-lg sm:text-xl font-bold text-purple-800 mb-4 flex items-center">
                {/* AI/Robot icon SVG with accessibility label */}
                <svg 
                  className="w-5 h-5 sm:w-6 sm:h-6 mr-2" 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24" 
                  xmlns="http://www.w3.org/2000/svg"
                  aria-label="AI robot icon"
                  role="img"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                AI Agent Status
              </h2>
              
              {/* Display current AI operating mode with responsive design */}
              <div className="mb-4">
                <span className="font-semibold text-sm sm:text-base">Current Mode:</span>{' '}
                <span className={`px-2 py-1 rounded text-xs sm:text-sm ${
                  bookSettings?.humanInLoopEnabled 
                    ? 'bg-yellow-100 text-yellow-800' 
                    : 'bg-green-100 text-green-800'
                }`}>
                  {bookSettings?.humanInLoopEnabled ? 'Human-in-the-Loop' : 'Autonomous'}
                </span>
              </div>
              
              {/* Action buttons with responsive spacing */}
              <div className="space-y-2 sm:space-y-3">
                <button
                  onClick={generateNewPosts}
                  className="w-full bg-purple-500 text-white py-2 px-4 rounded-md hover:bg-purple-600 transition duration-150 ease-in-out shadow-md focus-ring text-sm sm:text-base"
                  aria-label="Generate new marketing posts"
                >
                  Generate New Posts
                </button>
                <button
                  onClick={analyzePerformanceEnhanced}
                  className="w-full bg-green-500 text-white py-2 px-4 rounded-md hover:bg-green-600 transition duration-150 ease-in-out shadow-md focus-ring text-sm sm:text-base"
                  aria-label="Analyze marketing performance"
                >
                  Analyze Performance
                </button>
              </div>
            </div>
          </div>

          {/* Pending Approvals Section with enhanced responsive design */}
          <div className="bg-white p-4 sm:p-6 rounded-lg shadow-md mb-6 sm:mb-8 border border-yellow-200">
            <h2 className="text-xl sm:text-2xl font-bold text-yellow-700 mb-4 flex items-center">
              {/* Warning/Pending icon SVG with accessibility label */}
              <svg 
                className="w-5 h-5 sm:w-6 sm:h-6 mr-2" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24" 
                xmlns="http://www.w3.org/2000/svg"
                aria-label="Pending approval warning icon"
                role="img"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 18.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
              Pending Approvals ({pendingPosts.length})
            </h2>
            
            {/* Conditionally render pending posts with responsive design */}
            {pendingPosts.length > 0 ? (
              <div className="space-y-4">
                {pendingPosts.map((post) => (
                  <div key={post.id} className="border border-yellow-300 rounded-lg p-3 sm:p-4 bg-yellow-50 shadow-sm">
                    <div className="mb-2 text-sm sm:text-base">
                      <span className="font-semibold">Platform:</span> {post.platform || 'Not specified'}
                    </div>
                    <div className="mb-2 text-sm sm:text-base">
                      <span className="font-semibold">Status:</span>{' '}
                      <span className="px-2 py-1 bg-yellow-200 text-yellow-800 rounded text-xs sm:text-sm">
                        {post.status}
                      </span>
                    </div>
                    <div className="mb-3 text-sm sm:text-base">
                      <span className="font-semibold">Content:</span>
                      <p className="mt-1 text-gray-700 whitespace-pre-wrap break-words">{post.content}</p>
                    </div>
                    
                    {/* Conditionally display media with responsive sizing */}
                    {post.mediaUrl && (
                      <div className="mb-3">
                        <span className="font-semibold text-sm sm:text-base">Media:</span>
                        <img 
                          src={post.mediaUrl}
                          alt={`Marketing post media for ${post.platform || 'social platform'}`}
                          className="mt-1 w-full max-w-xs sm:max-w-sm rounded border"
                          onError={(e) => {
                            e.target.src = "https://placehold.co/150x100/CCCCCC/FFFFFF?text=Image+Error";
                            e.target.alt = "Image failed to load - placeholder displayed";
                          }}
                        />
                      </div>
                    )}
                    
                    {/* Action buttons for each post with responsive design */}
                    <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-2">
                      <button
                        onClick={() => approvePost(post.id, post.content)}
                        className="bg-green-600 text-white py-1 px-3 rounded text-sm hover:bg-green-700 transition duration-150 ease-in-out focus-ring"
                        aria-label={`Approve and schedule post: ${post.content.substring(0, 30)}...`}
                      >
                        Approve & Schedule
                      </button>
                      <button
                        onClick={() => startEditPost(post)}
                        className="bg-blue-600 text-white py-1 px-3 rounded text-sm hover:bg-blue-700 transition duration-150 ease-in-out focus-ring"
                        aria-label={`Edit post: ${post.content.substring(0, 30)}...`}
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => discardPost(post.id, post.content)}
                        className="bg-red-600 text-white py-1 px-3 rounded text-sm hover:bg-red-700 transition duration-150 ease-in-out focus-ring"
                        aria-label={`Discard post: ${post.content.substring(0, 30)}...`}
                      >
                        Discard
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-600 text-center py-6 sm:py-8 text-sm sm:text-base">
                No posts awaiting approval. The AI is working hard! 🤖
              </p>
            )}
          </div>

          {/* Performance Overview Placeholder with responsive design */}
          <div className="bg-white p-4 sm:p-6 rounded-lg shadow-md mb-6 sm:mb-8 border border-blue-200">
            <h2 className="text-xl sm:text-2xl font-bold text-blue-700 mb-4 flex items-center">
              {/* Charts/Performance icon SVG with accessibility label */}
              <svg 
                className="w-5 h-5 sm:w-6 sm:h-6 mr-2" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24" 
                xmlns="http://www.w3.org/2000/svg"
                aria-label="Performance analytics chart icon"
                role="img"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              Performance Overview
            </h2>
            
            <p className="text-gray-600 mb-4 text-sm sm:text-base leading-relaxed">
              This section will display comprehensive analytics about your book marketing performance, including engagement metrics, 
              conversion rates, campaign effectiveness, and ROI tracking. Data visualization charts and key performance indicators 
              will help you understand which marketing strategies are working best for your book.
            </p>
            
            <button
              onClick={viewDetailedReports}
              className="w-full sm:w-auto bg-blue-500 text-white py-2 px-4 rounded-md hover:bg-blue-600 transition duration-150 ease-in-out shadow-md focus-ring text-sm sm:text-base"
              aria-label="View detailed performance reports"
            >
              View Detailed Reports
            </button>
          </div>

          {/* Revenue Growth Management Section - NEW AI-DRIVEN OPTIMIZATION */}
          <div className="bg-gradient-to-br from-green-50 to-emerald-100 p-4 sm:p-6 rounded-lg shadow-md mb-6 sm:mb-8 border border-green-200">
            <h2 className="text-xl sm:text-2xl font-bold text-green-800 mb-4 flex items-center">
              {/* Revenue/Growth icon SVG with accessibility label */}
              <svg 
                className="w-5 h-5 sm:w-6 sm:h-6 mr-2" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24" 
                xmlns="http://www.w3.org/2000/svg"
                aria-label="Revenue growth chart icon"
                role="img"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
              🚀 Revenue Growth Management
            </h2>
            
            <p className="text-green-700 mb-6 text-sm sm:text-base leading-relaxed">
              <strong>AI-driven optimization for compounding monthly sales growth.</strong> This advanced system uses machine learning 
              to analyze performance patterns, optimize pricing strategies, prevent customer churn, and maximize revenue through 
              intelligent automation. Goal: <span className="font-bold">15%+ monthly growth with minimal manual input.</span>
            </p>

            {/* Grid Layout for RGM Features */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
              
              {/* Revenue Analysis Card */}
              <div className="bg-white p-4 rounded-lg shadow-sm border border-green-200">
                <h3 className="font-bold text-green-800 mb-2 flex items-center text-sm sm:text-base">
                  📊 Revenue Analysis
                </h3>
                <p className="text-xs sm:text-sm text-gray-600 mb-3">
                  AI analyzes performance metrics, identifies growth opportunities, and generates actionable recommendations.
                </p>
                <button
                  onClick={analyzeRevenuePerformance}
                  disabled={loading_revenue}
                  className="w-full bg-green-600 text-white py-2 px-3 rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition duration-150 ease-in-out text-xs sm:text-sm"
                  aria-label="Run AI revenue performance analysis"
                >
                  {loading_revenue ? 'Analyzing...' : 'Analyze Revenue'}
                </button>
              </div>

              {/* Pricing Optimization Card */}
              <div className="bg-white p-4 rounded-lg shadow-sm border border-green-200">
                <h3 className="font-bold text-green-800 mb-2 flex items-center text-sm sm:text-base">
                  💰 Smart Pricing
                </h3>
                <p className="text-xs sm:text-sm text-gray-600 mb-3">
                  Dynamic pricing strategies based on market data, demand patterns, and customer behavior analysis.
                </p>
                <button
                  onClick={optimizePricingStrategy}
                  className="w-full bg-amber-600 text-white py-2 px-3 rounded-md hover:bg-amber-700 transition duration-150 ease-in-out text-xs sm:text-sm"
                  aria-label="Optimize pricing strategy with AI"
                >
                  Optimize Pricing
                </button>
              </div>

              {/* Churn Prevention Card */}
              <div className="bg-white p-4 rounded-lg shadow-sm border border-green-200">
                <h3 className="font-bold text-green-800 mb-2 flex items-center text-sm sm:text-base">
                  🛡️ Churn Prevention
                </h3>
                <p className="text-xs sm:text-sm text-gray-600 mb-3">
                  Predict at-risk customers and automatically implement retention strategies to reduce churn.
                </p>
                <button
                  onClick={predictAndPreventChurn}
                  className="w-full bg-red-600 text-white py-2 px-3 rounded-md hover:bg-red-700 transition duration-150 ease-in-out text-xs sm:text-sm"
                  aria-label="Run churn prediction and prevention analysis"
                >
                  Prevent Churn
                </button>
              </div>

              {/* Performance Analytics Card */}
              <div className="bg-white p-4 rounded-lg shadow-sm border border-green-200">
                <h3 className="font-bold text-green-800 mb-2 flex items-center text-sm sm:text-base">
                  📈 Smart Analytics
                </h3>
                <p className="text-xs sm:text-sm text-gray-600 mb-3">
                  Advanced content performance analysis with predictive insights and optimization recommendations.
                </p>
                <button
                  onClick={analyzeContentPerformance}
                  disabled={loading_analytics}
                  className="w-full bg-purple-600 text-white py-2 px-3 rounded-md hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition duration-150 ease-in-out text-xs sm:text-sm"
                  aria-label="Analyze content performance with AI"
                >
                  {loading_analytics ? 'Analyzing...' : 'Analyze Content'}
                </button>
              </div>

              {/* A/B Testing Card */}
              <div className="bg-white p-4 rounded-lg shadow-sm border border-green-200">
                <h3 className="font-bold text-green-800 mb-2 flex items-center text-sm sm:text-base">
                  🧪 A/B Testing
                </h3>
                <p className="text-xs sm:text-sm text-gray-600 mb-3">
                  Automated A/B testing framework for continuous content and strategy optimization.
                </p>
                <button
                  onClick={() => setupABTest("Mental toughness for young athletes", "tone", ["instagram", "facebook"])}
                  className="w-full bg-indigo-600 text-white py-2 px-3 rounded-md hover:bg-indigo-700 transition duration-150 ease-in-out text-xs sm:text-sm"
                  aria-label="Set up A/B test for content optimization"
                >
                  Create A/B Test
                </button>
              </div>

              {/* Content Prediction Card */}
              <div className="bg-white p-4 rounded-lg shadow-sm border border-green-200">
                <h3 className="font-bold text-green-800 mb-2 flex items-center text-sm sm:text-base">
                  🔮 Content Prediction
                </h3>
                <p className="text-xs sm:text-sm text-gray-600 mb-3">
                  Predict content performance before publishing and get optimization suggestions.
                </p>
                <button
                  onClick={() => predictContentPerformance("Mental strength is the game-changer for young athletes! 💪 #YouthSports #MentalToughness", "instagram")}
                  className="w-full bg-pink-600 text-white py-2 px-3 rounded-md hover:bg-pink-700 transition duration-150 ease-in-out text-xs sm:text-sm"
                  aria-label="Predict content performance with AI"
                >
                  Predict Performance
                </button>
              </div>
            </div>

            {/* Quick Actions Row */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 pt-4 border-t border-green-200">
              <button
                onClick={() => generatePerformanceReport('weekly')}
                className="bg-green-700 text-white py-2 px-4 rounded-md hover:bg-green-800 transition duration-150 ease-in-out text-xs sm:text-sm"
                aria-label="Generate weekly performance report"
              >
                📊 Weekly Report
              </button>
              <button
                onClick={() => generatePerformanceReport('monthly')}
                className="bg-green-700 text-white py-2 px-4 rounded-md hover:bg-green-800 transition duration-150 ease-in-out text-xs sm:text-sm"
                aria-label="Generate monthly performance report"
              >
                📈 Monthly Report
              </button>
              <button
                onClick={analyzePerformanceEnhanced}
                className="bg-green-800 text-white py-2 px-4 rounded-md hover:bg-green-900 transition duration-150 ease-in-out text-xs sm:text-sm font-semibold"
                aria-label="Run comprehensive AI analysis of all metrics"
              >
                🤖 Full AI Analysis
              </button>
            </div>

            {/* Growth Status Indicator */}
            <div className="mt-4 p-3 bg-green-100 rounded-lg border border-green-300">
              <div className="flex items-center justify-between flex-wrap">
                <span className="text-sm font-semibold text-green-800">🎯 Growth Status:</span>
                <span className="text-sm text-green-700">Optimizing for 15%+ monthly compounding growth</span>
              </div>
              <div className="mt-2 text-xs text-green-600">
                Last optimization: {new Date().toLocaleDateString()} | Target: Autonomous growth with minimal manual input
              </div>
            </div>
          </div>

          {/* Budget Management Section - NEW */}
          <div className="bg-gradient-to-br from-yellow-50 to-orange-100 p-4 sm:p-6 rounded-lg shadow-md mb-6 sm:mb-8 border border-yellow-200">
            <h2 className="text-xl sm:text-2xl font-bold text-orange-800 mb-4 flex items-center">
              <svg className="w-5 h-5 sm:w-6 sm:h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
              </svg>
              💰 Budget Management
            </h2>
            
            <p className="text-orange-700 mb-6 text-sm sm:text-base leading-relaxed">
              <strong>Intelligent budget allocation and optimization.</strong> Track spending across platforms, get alerts when approaching limits, 
              and automatically optimize budget distribution based on performance data.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-white p-4 rounded-lg shadow-sm border border-orange-200">
                <h3 className="font-bold text-orange-800 mb-2 text-sm sm:text-base">📊 Budget Status</h3>
                <p className="text-xs sm:text-sm text-gray-600 mb-3">
                  Current spending, remaining budget, and performance metrics across all platforms.
                </p>
                <button
                  onClick={getBudgetStatus}
                  disabled={loading_budget}
                  className="w-full bg-orange-600 text-white py-2 px-3 rounded-md hover:bg-orange-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition duration-150 ease-in-out text-xs sm:text-sm"
                >
                  {loading_budget ? 'Loading...' : 'View Budget Status'}
                </button>
              </div>

              <div className="bg-white p-4 rounded-lg shadow-sm border border-orange-200">
                <h3 className="font-bold text-orange-800 mb-2 text-sm sm:text-base">🔧 Optimize Allocation</h3>
                <p className="text-xs sm:text-sm text-gray-600 mb-3">
                  AI-powered optimization of budget distribution across platforms for maximum ROI.
                </p>
                <button
                  onClick={optimizeBudgetAllocation}
                  className="w-full bg-blue-600 text-white py-2 px-3 rounded-md hover:bg-blue-700 transition duration-150 ease-in-out text-xs sm:text-sm"
                >
                  Optimize Budget
                </button>
              </div>

              <div className="bg-white p-4 rounded-lg shadow-sm border border-orange-200">
                <h3 className="font-bold text-orange-800 mb-2 text-sm sm:text-base">📈 Forecast</h3>
                <p className="text-xs sm:text-sm text-gray-600 mb-3">
                  Predict spending patterns and ROI for the next period with AI forecasting.
                </p>
                <button
                  onClick={getBudgetForecast}
                  className="w-full bg-purple-600 text-white py-2 px-3 rounded-md hover:bg-purple-700 transition duration-150 ease-in-out text-xs sm:text-sm"
                >
                  Get Forecast
                </button>
              </div>
            </div>
          </div>

          {/* Autonomous Operations Section - NEW */}
          <div className="bg-gradient-to-br from-purple-50 to-indigo-100 p-4 sm:p-6 rounded-lg shadow-md mb-6 sm:mb-8 border border-purple-200">
            <h2 className="text-xl sm:text-2xl font-bold text-purple-800 mb-4 flex items-center">
              <svg className="w-5 h-5 sm:w-6 sm:h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              ⚡ Autonomous Operations
            </h2>
            
            <p className="text-purple-700 mb-6 text-sm sm:text-base leading-relaxed">
              <strong>Fully automated marketing operations.</strong> Let AI handle content creation, posting schedules, 
              performance optimization, and campaign management while you focus on writing your next book.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-white p-4 rounded-lg shadow-sm border border-purple-200">
                <h3 className="font-bold text-purple-800 mb-2 text-sm sm:text-base">🚀 Start Auto</h3>
                <p className="text-xs sm:text-sm text-gray-600 mb-3">
                  Begin fully autonomous marketing operations with AI oversight.
                </p>
                <button
                  onClick={startAutonomousOperation}
                  disabled={loading_autonomous}
                  className="w-full bg-green-600 text-white py-2 px-3 rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition duration-150 ease-in-out text-xs sm:text-sm"
                >
                  {loading_autonomous ? 'Starting...' : 'Start Auto Mode'}
                </button>
              </div>

              <div className="bg-white p-4 rounded-lg shadow-sm border border-purple-200">
                <h3 className="font-bold text-purple-800 mb-2 text-sm sm:text-base">⏹️ Stop Auto</h3>
                <p className="text-xs sm:text-sm text-gray-600 mb-3">
                  Stop autonomous operations and return to manual control.
                </p>
                <button
                  onClick={stopAutonomousOperation}
                  className="w-full bg-red-600 text-white py-2 px-3 rounded-md hover:bg-red-700 transition duration-150 ease-in-out text-xs sm:text-sm"
                >
                  Stop Auto Mode
                </button>
              </div>

              <div className="bg-white p-4 rounded-lg shadow-sm border border-purple-200">
                <h3 className="font-bold text-purple-800 mb-2 text-sm sm:text-base">📊 Status</h3>
                <p className="text-xs sm:text-sm text-gray-600 mb-3">
                  Check current autonomous operation status and performance metrics.
                </p>
                <button
                  onClick={getAutonomousStatus}
                  className="w-full bg-blue-600 text-white py-2 px-3 rounded-md hover:bg-blue-700 transition duration-150 ease-in-out text-xs sm:text-sm"
                >
                  Check Status
                </button>
              </div>

              <div className="bg-white p-4 rounded-lg shadow-sm border border-purple-200">
                <h3 className="font-bold text-purple-800 mb-2 text-sm sm:text-base">⚡ Execute Daily</h3>
                <p className="text-xs sm:text-sm text-gray-600 mb-3">
                  Manually trigger today's autonomous operations and content generation.
                </p>
                <button
                  onClick={executeDailyOperations}
                  className="w-full bg-amber-600 text-white py-2 px-3 rounded-md hover:bg-amber-700 transition duration-150 ease-in-out text-xs sm:text-sm"
                >
                  Execute Daily
                </button>
              </div>
            </div>
          </div>

          {/* Google Ads Management Section - NEW */}
          <div className="bg-gradient-to-br from-cyan-50 to-blue-100 p-4 sm:p-6 rounded-lg shadow-md mb-6 sm:mb-8 border border-cyan-200">
            <h2 className="text-xl sm:text-2xl font-bold text-cyan-800 mb-4 flex items-center">
              <svg className="w-5 h-5 sm:w-6 sm:h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
              </svg>
              🎯 Google Ads Management
            </h2>
            
            <p className="text-cyan-700 mb-6 text-sm sm:text-base leading-relaxed">
              <strong>Intelligent Google Ads campaign management.</strong> Create, optimize, and manage high-converting 
              ad campaigns with AI-powered keyword research, bid optimization, and performance tracking.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-white p-4 rounded-lg shadow-sm border border-cyan-200">
                <h3 className="font-bold text-cyan-800 mb-2 text-sm sm:text-base">🎯 Create Campaign</h3>
                <p className="text-xs sm:text-sm text-gray-600 mb-3">
                  Launch new Google Ads campaigns with AI-optimized targeting and ad copy.
                </p>
                <button
                  onClick={createAdsCampaign}
                  disabled={loading_ads}
                  className="w-full bg-cyan-600 text-white py-2 px-3 rounded-md hover:bg-cyan-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition duration-150 ease-in-out text-xs sm:text-sm"
                >
                  {loading_ads ? 'Creating...' : 'Create Campaign'}
                </button>
              </div>

              <div className="bg-white p-4 rounded-lg shadow-sm border border-cyan-200">
                <h3 className="font-bold text-cyan-800 mb-2 text-sm sm:text-base">🔧 Optimize Campaign</h3>
                <p className="text-xs sm:text-sm text-gray-600 mb-3">
                  AI-powered optimization of existing campaigns for better performance and ROI.
                </p>
                <button
                  onClick={optimizeAdsCampaign}
                  className="w-full bg-emerald-600 text-white py-2 px-3 rounded-md hover:bg-emerald-700 transition duration-150 ease-in-out text-xs sm:text-sm"
                >
                  Optimize Existing
                </button>
              </div>
            </div>
          </div>

          {/* Platform Testing & Status Section - NEW */}
          <div className="bg-gradient-to-br from-pink-50 to-rose-100 p-4 sm:p-6 rounded-lg shadow-md mb-6 sm:mb-8 border border-pink-200">
            <h2 className="text-xl sm:text-2xl font-bold text-pink-800 mb-4 flex items-center">
              <svg className="w-5 h-5 sm:w-6 sm:h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              🧪 Platform Testing & Status
            </h2>
            
            <p className="text-pink-700 mb-6 text-sm sm:text-base leading-relaxed">
              <strong>Monitor and test all social media integrations.</strong> Check API connections, test posting capabilities, 
              and ensure all platforms are properly configured and functioning.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
              <div className="bg-white p-4 rounded-lg shadow-sm border border-pink-200">
                <h3 className="font-bold text-pink-800 mb-2 text-sm sm:text-base">📊 Platform Status</h3>
                <p className="text-xs sm:text-sm text-gray-600 mb-3">
                  Check the status and health of all connected social media platforms.
                </p>
                <button
                  onClick={getPlatformStatus}
                  disabled={loading_platform}
                  className="w-full bg-pink-600 text-white py-2 px-3 rounded-md hover:bg-pink-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition duration-150 ease-in-out text-xs sm:text-sm"
                >
                  {loading_platform ? 'Checking...' : 'Check Status'}
                </button>
              </div>

              <div className="bg-white p-4 rounded-lg shadow-sm border border-pink-200">
                <h3 className="font-bold text-pink-800 mb-2 text-sm sm:text-base">🐦 Test Twitter</h3>
                <p className="text-xs sm:text-sm text-gray-600 mb-3">
                  Test Twitter API connection and posting capabilities.
                </p>
                <button
                  onClick={() => testPlatform('twitter')}
                  className="w-full bg-blue-500 text-white py-2 px-3 rounded-md hover:bg-blue-600 transition duration-150 ease-in-out text-xs sm:text-sm"
                >
                  Test Twitter
                </button>
              </div>

              <div className="bg-white p-4 rounded-lg shadow-sm border border-pink-200">
                <h3 className="font-bold text-pink-800 mb-2 text-sm sm:text-base">📘 Test Facebook</h3>
                <p className="text-xs sm:text-sm text-gray-600 mb-3">
                  Test Facebook API connection and posting capabilities.
                </p>
                <button
                  onClick={() => testPlatform('facebook')}
                  className="w-full bg-blue-700 text-white py-2 px-3 rounded-md hover:bg-blue-800 transition duration-150 ease-in-out text-xs sm:text-sm"
                >
                  Test Facebook
                </button>
              </div>

              <div className="bg-white p-4 rounded-lg shadow-sm border border-pink-200">
                <h3 className="font-bold text-pink-800 mb-2 text-sm sm:text-base">📷 Test Instagram</h3>
                <p className="text-xs sm:text-sm text-gray-600 mb-3">
                  Test Instagram API connection and posting capabilities.
                </p>
                <button
                  onClick={() => testPlatform('instagram')}
                  className="w-full bg-gradient-to-r from-purple-500 to-pink-500 text-white py-2 px-3 rounded-md hover:from-purple-600 hover:to-pink-600 transition duration-150 ease-in-out text-xs sm:text-sm"
                >
                  Test Instagram
                </button>
              </div>

              <div className="bg-white p-4 rounded-lg shadow-sm border border-pink-200">
                <h3 className="font-bold text-pink-800 mb-2 text-sm sm:text-base">📌 Test Pinterest</h3>
                <p className="text-xs sm:text-sm text-gray-600 mb-3">
                  Test Pinterest API connection and posting capabilities.
                </p>
                <button
                  onClick={() => testPlatform('pinterest')}
                  className="w-full bg-red-600 text-white py-2 px-3 rounded-md hover:bg-red-700 transition duration-150 ease-in-out text-xs sm:text-sm"
                >
                  Test Pinterest
                </button>
              </div>

              <div className="bg-white p-4 rounded-lg shadow-sm border border-pink-200">
                <h3 className="font-bold text-pink-800 mb-2 text-sm sm:text-base">📊 Analytics</h3>
                <p className="text-xs sm:text-sm text-gray-600 mb-3">
                  Get comprehensive marketing metrics and social media attribution data.
                </p>
                <button
                  onClick={getMarketingMetrics}
                  className="w-full bg-emerald-600 text-white py-2 px-3 rounded-md hover:bg-emerald-700 transition duration-150 ease-in-out text-xs sm:text-sm mb-2"
                >
                  Marketing Metrics
                </button>
                <button
                  onClick={getSocialAttribution}
                  className="w-full bg-teal-600 text-white py-2 px-3 rounded-md hover:bg-teal-700 transition duration-150 ease-in-out text-xs sm:text-sm"
                >
                  Social Attribution
                </button>
              </div>
            </div>
          </div>

          {/* Settings and Reports Section - NEW */}
          <div className="bg-gradient-to-br from-gray-50 to-slate-100 p-4 sm:p-6 rounded-lg shadow-md mb-6 sm:mb-8 border border-gray-200">
            <h2 className="text-xl sm:text-2xl font-bold text-gray-800 mb-4 flex items-center">
              <svg className="w-5 h-5 sm:w-6 sm:h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              ⚙️ Settings & Reports
            </h2>
            
            <p className="text-gray-700 mb-6 text-sm sm:text-base leading-relaxed">
              <strong>Configure your system and generate reports.</strong> Set up API keys, adjust marketing settings, 
              and generate comprehensive performance reports.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
                <h3 className="font-bold text-gray-800 mb-2 text-sm sm:text-base">🚀 Setup Guide</h3>
                <p className="text-xs sm:text-sm text-gray-600 mb-3">
                  Complete step-by-step setup guide with API key instructions and links.
                </p>
                <button
                  onClick={showOnboardingManually}
                  className="w-full bg-purple-600 text-white py-2 px-3 rounded-md hover:bg-purple-700 transition duration-150 ease-in-out text-xs sm:text-sm"
                >
                  Open Setup Guide
                </button>
              </div>

              <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
                <h3 className="font-bold text-gray-800 mb-2 text-sm sm:text-base">⚙️ API Settings</h3>
                <p className="text-xs sm:text-sm text-gray-600 mb-3">
                  Configure API keys, credentials, and system settings for all platforms and services.
                </p>
                <button
                  onClick={() => setShowConfigSettingsModal(true)}
                  className="w-full bg-gray-600 text-white py-2 px-3 rounded-md hover:bg-gray-700 transition duration-150 ease-in-out text-xs sm:text-sm"
                >
                  Open Settings
                </button>
              </div>

              <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
                <h3 className="font-bold text-gray-800 mb-2 text-sm sm:text-base">📊 Weekly Report</h3>
                <p className="text-xs sm:text-sm text-gray-600 mb-3">
                  Generate comprehensive weekly performance reports with insights and recommendations.
                </p>
                <button
                  onClick={generateWeeklyReport}
                  disabled={loading_report}
                  className="w-full bg-indigo-600 text-white py-2 px-3 rounded-md hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition duration-150 ease-in-out text-xs sm:text-sm"
                >
                  {loading_report ? 'Generating...' : 'Generate Report'}
                </button>
              </div>

              <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
                <h3 className="font-bold text-gray-800 mb-2 text-sm sm:text-base">📚 Book Settings</h3>
                <p className="text-xs sm:text-sm text-gray-600 mb-3">
                  Edit book information, target audience, and marketing preferences.
                </p>
                <button
                  onClick={() => setShowSettingsModal(true)}
                  className="w-full bg-blue-600 text-white py-2 px-3 rounded-md hover:bg-blue-700 transition duration-150 ease-in-out text-xs sm:text-sm"
                >
                  Edit Book Settings
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Custom Modal - using the imported CustomModal component */}
        {showModal && <CustomModal message={modalMessage} onClose={() => setShowModal(false)} />}

        {/* Edit Modal - using the enhanced CustomModal component for post editing */}
        {showEditModal && (
          <CustomModal
            title="Edit Post Content"
            onClose={() => {
              setShowEditModal(false);
              setEditingPost(null);
              setEditContent('');
            }}
            showCloseButton={false}
          >
            {/* Edit form content */}
            <div>
              {/* Platform indicator */}
              <div className="mb-3">
                <span className="text-sm font-semibold text-gray-700">Platform: </span>
                <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">
                  {editingPost?.platform || 'Unknown'}
                </span>
              </div>
              
              {/* Content editing textarea */}
              <label htmlFor="edit-content" className="block text-sm font-semibold text-gray-700 mb-2">
                Post Content:
              </label>
              <textarea
                id="edit-content"
                value={editContent}
                onChange={(e) => setEditContent(e.target.value)}
                className="w-full h-32 p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-vertical"
                placeholder="Enter your post content here..."
                maxLength={2000}
              />
              
              {/* Character count */}
              <div className="text-right text-xs text-gray-500 mt-1">
                {editContent.length}/2000 characters
              </div>
              
              {/* Action buttons */}
              <div className="mt-6 flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-3">
                <button
                  onClick={saveEditedPost}
                  disabled={!editContent.trim()}
                  className="bg-blue-500 text-white py-2 px-4 rounded-md hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition duration-150 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  Save Changes
                </button>
                <button
                  onClick={() => {
                    setShowEditModal(false);
                    setEditingPost(null);
                    setEditContent('');
                  }}
                  className="bg-gray-500 text-white py-2 px-4 rounded-md hover:bg-gray-600 transition duration-150 ease-in-out focus:outline-none focus:ring-2 focus:ring-gray-500"
                >
                  Cancel
                </button>
              </div>
            </div>
          </CustomModal>
        )}

        {/* Settings Modal - using the enhanced CustomModal component for settings editing */}
        {showSettingsModal && (
          <CustomModal
            title="Book Settings"
            onClose={() => {
              setShowSettingsModal(false);
              setEditingSettings({});
            }}
            showCloseButton={false}
          >
            {/* Settings form content */}
            <div>
              {/* Form fields for editing settings */}
              <div className="mb-4">
                <label htmlFor="bookTitle" className="block text-sm font-semibold text-gray-700 mb-2">
                  Title:
                </label>
                <input
                  id="bookTitle"
                  value={editingSettings.bookTitle}
                  onChange={(e) => handleSettingsChange('bookTitle', e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div className="mb-4">
                <label htmlFor="bookAuthor" className="block text-sm font-semibold text-gray-700 mb-2">
                  Author:
                </label>
                <input
                  id="bookAuthor"
                  value={editingSettings.bookAuthor}
                  onChange={(e) => handleSettingsChange('bookAuthor', e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div className="mb-4">
                <label htmlFor="amazonLink" className="block text-sm font-semibold text-gray-700 mb-2">
                  Amazon Link:
                </label>
                <input
                  id="amazonLink"
                  value={editingSettings.amazonLink}
                  onChange={(e) => handleSettingsChange('amazonLink', e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div className="mb-4">
                <label htmlFor="audibleLink" className="block text-sm font-semibold text-gray-700 mb-2">
                  Audible Link:
                </label>
                <input
                  id="audibleLink"
                  value={editingSettings.audibleLink}
                  onChange={(e) => handleSettingsChange('audibleLink', e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div className="mb-4">
                <label htmlFor="landingPageUrl" className="block text-sm font-semibold text-gray-700 mb-2">
                  Landing Page:
                </label>
                <input
                  id="landingPageUrl"
                  value={editingSettings.landingPageUrl}
                  onChange={(e) => handleSettingsChange('landingPageUrl', e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div className="mb-4">
                <label htmlFor="monthlyBudget" className="block text-sm font-semibold text-gray-700 mb-2">
                  Monthly Budget:
                </label>
                <input
                  id="monthlyBudget"
                  type="number"
                  value={editingSettings.monthlyBudget}
                  onChange={(e) => handleSettingsChange('monthlyBudget', Number(e.target.value))}
                  className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div className="mb-4">
                <label htmlFor="contentGuidelines" className="block text-sm font-semibold text-gray-700 mb-2">
                  Content Guidelines:
                </label>
                <textarea
                  id="contentGuidelines"
                  value={editingSettings.contentGuidelines}
                  onChange={(e) => handleSettingsChange('contentGuidelines', e.target.value)}
                  className="w-full h-32 p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Enter content guidelines here..."
                />
              </div>
              <div className="mb-4">
                <label htmlFor="humanInLoopEnabled" className="block text-sm font-semibold text-gray-700 mb-2">
                  Human-in-Loop:
                </label>
                <input
                  id="humanInLoopEnabled"
                  type="checkbox"
                  checked={editingSettings.humanInLoopEnabled}
                  onChange={(e) => handleSettingsChange('humanInLoopEnabled', e.target.checked)}
                  className="form-checkbox h-5 w-5 text-blue-600"
                />
              </div>
              <div className="mb-4">
                <label htmlFor="targetAudience" className="block text-sm font-semibold text-gray-700 mb-2">
                  Target Audience:
                </label>
                <input
                  id="targetAudience"
                  value={editingSettings.targetAudience}
                  onChange={(e) => handleSettingsChange('targetAudience', e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div className="mb-4">
                <label htmlFor="bookGenre" className="block text-sm font-semibold text-gray-700 mb-2">
                  Genre:
                </label>
                <input
                  id="bookGenre"
                  value={editingSettings.bookGenre}
                  onChange={(e) => handleSettingsChange('bookGenre', e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div className="mb-4">
                <label htmlFor="keyThemes" className="block text-sm font-semibold text-gray-700 mb-2">
                  Key Themes:
                </label>
                <input
                  id="keyThemes"
                  value={editingSettings.keyThemes}
                  onChange={(e) => handleSettingsChange('keyThemes', e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div className="mb-4">
                <label htmlFor="marketingTone" className="block text-sm font-semibold text-gray-700 mb-2">
                  Marketing Tone:
                </label>
                <input
                  id="marketingTone"
                  value={editingSettings.marketingTone}
                  onChange={(e) => handleSettingsChange('marketingTone', e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              
              {/* Action buttons */}
              <div className="mt-6 flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-3">
                <button
                  onClick={saveEditedSettings}
                  className="bg-blue-500 text-white py-2 px-4 rounded-md hover:bg-blue-600 transition duration-150 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  Save Changes
                </button>
                <button
                  onClick={() => {
                    setShowSettingsModal(false);
                    setEditingSettings({});
                  }}
                  className="bg-gray-500 text-white py-2 px-4 rounded-md hover:bg-gray-600 transition duration-150 ease-in-out focus:outline-none focus:ring-2 focus:ring-gray-500"
                >
                  Cancel
                </button>
              </div>
            </div>
          </CustomModal>
        )}

        {/* Revenue Analysis Modal - displays detailed revenue performance analysis */}
        {showRevenueModal && revenueAnalysis && (
          <CustomModal
            title="📊 Revenue Performance Analysis"
            onClose={() => setShowRevenueModal(false)}
            showCloseButton={true}
          >
            <div className="space-y-4">
              {/* Current Metrics Section */}
              <div className="bg-blue-50 p-4 rounded-lg">
                <h3 className="font-bold text-blue-800 mb-2">📈 Current Metrics</h3>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div><span className="font-semibold">Monthly Sales:</span> ${revenueAnalysis.current_metrics?.monthly_sales?.toFixed(2) || 'N/A'}</div>
                  <div><span className="font-semibold">Growth Rate:</span> {(revenueAnalysis.current_metrics?.growth_rate * 100)?.toFixed(1) || 'N/A'}%</div>
                  <div><span className="font-semibold">Conversion Rate:</span> {(revenueAnalysis.current_metrics?.conversion_rate * 100)?.toFixed(2) || 'N/A'}%</div>
                  <div><span className="font-semibold">AOV:</span> ${revenueAnalysis.current_metrics?.average_order_value?.toFixed(2) || 'N/A'}</div>
                </div>
              </div>

              {/* Growth Opportunities Section */}
              <div className="bg-green-50 p-4 rounded-lg">
                <h3 className="font-bold text-green-800 mb-2">🚀 Growth Opportunities</h3>
                <div className="text-sm">
                  {revenueAnalysis.growth_opportunities ? (
                    <pre className="whitespace-pre-wrap text-gray-700">{JSON.stringify(revenueAnalysis.growth_opportunities, null, 2)}</pre>
                  ) : (
                    <p className="text-gray-600">AI is analyzing growth opportunities...</p>
                  )}
                </div>
              </div>

              {/* AI Recommendations Section */}
              <div className="bg-yellow-50 p-4 rounded-lg">
                <h3 className="font-bold text-yellow-800 mb-2">🤖 AI Recommendations</h3>
                <div className="text-sm">
                  {revenueAnalysis.ai_recommendations ? (
                    <pre className="whitespace-pre-wrap text-gray-700">{JSON.stringify(revenueAnalysis.ai_recommendations, null, 2)}</pre>
                  ) : (
                    <p className="text-gray-600">Generating AI recommendations...</p>
                  )}
                </div>
              </div>

              {/* Growth Projections Section */}
              <div className="bg-purple-50 p-4 rounded-lg">
                <h3 className="font-bold text-purple-800 mb-2">📊 Growth Projections</h3>
                <div className="text-sm">
                  {revenueAnalysis.growth_projections ? (
                    <pre className="whitespace-pre-wrap text-gray-700">{JSON.stringify(revenueAnalysis.growth_projections, null, 2)}</pre>
                  ) : (
                    <p className="text-gray-600">Calculating growth projections...</p>
                  )}
                </div>
              </div>
            </div>
          </CustomModal>
        )}

        {/* Performance Analytics Modal - displays detailed content performance analysis */}
        {showAnalyticsModal && performanceData && (
          <CustomModal
            title="📈 Performance Analytics"
            onClose={() => setShowAnalyticsModal(false)}
            showCloseButton={true}
          >
            <div className="space-y-4">
              {/* Performance Metrics Section */}
              <div className="bg-blue-50 p-4 rounded-lg">
                <h3 className="font-bold text-blue-800 mb-2">📊 Performance Metrics</h3>
                <div className="text-sm">
                  {performanceData.performance_metrics ? (
                    <pre className="whitespace-pre-wrap text-gray-700">{JSON.stringify(performanceData.performance_metrics, null, 2)}</pre>
                  ) : (
                    <p className="text-gray-600">Analyzing performance metrics...</p>
                  )}
                </div>
              </div>

              {/* Top Performing Patterns Section */}
              <div className="bg-green-50 p-4 rounded-lg">
                <h3 className="font-bold text-green-800 mb-2">🏆 Top Performing Patterns</h3>
                <div className="text-sm">
                  {performanceData.top_performing_patterns ? (
                    <pre className="whitespace-pre-wrap text-gray-700">{JSON.stringify(performanceData.top_performing_patterns, null, 2)}</pre>
                  ) : (
                    <p className="text-gray-600">Identifying successful patterns...</p>
                  )}
                </div>
              </div>

              {/* AI Insights Section */}
              <div className="bg-yellow-50 p-4 rounded-lg">
                <h3 className="font-bold text-yellow-800 mb-2">🤖 AI Insights</h3>
                <div className="text-sm">
                  {performanceData.ai_insights ? (
                    <p className="whitespace-pre-wrap text-gray-700">{performanceData.ai_insights}</p>
                  ) : (
                    <p className="text-gray-600">Generating AI insights...</p>
                  )}
                </div>
              </div>

              {/* Optimization Recommendations Section */}
              <div className="bg-purple-50 p-4 rounded-lg">
                <h3 className="font-bold text-purple-800 mb-2">⚡ Optimization Recommendations</h3>
                <div className="text-sm">
                  {performanceData.optimization_recommendations ? (
                    <pre className="whitespace-pre-wrap text-gray-700">{JSON.stringify(performanceData.optimization_recommendations, null, 2)}</pre>
                  ) : (
                    <p className="text-gray-600">Creating optimization strategies...</p>
                  )}
                </div>
              </div>
            </div>
          </CustomModal>
        )}

        {/* Pricing Optimization Modal - displays pricing strategy recommendations */}
        {showPricingModal && pricingOptimization && (
          <CustomModal
            title="💰 Pricing Optimization"
            onClose={() => setShowPricingModal(false)}
            showCloseButton={true}
          >
            <div className="space-y-4">
              {/* Pricing Analysis Section */}
              <div className="bg-amber-50 p-4 rounded-lg">
                <h3 className="font-bold text-amber-800 mb-2">📊 Pricing Analysis</h3>
                <div className="text-sm">
                  {pricingOptimization.pricing_analysis ? (
                    <pre className="whitespace-pre-wrap text-gray-700">{JSON.stringify(pricingOptimization.pricing_analysis, null, 2)}</pre>
                  ) : (
                    <p className="text-gray-600">Analyzing current pricing effectiveness...</p>
                  )}
                </div>
              </div>

              {/* AI Recommendations Section */}
              <div className="bg-green-50 p-4 rounded-lg">
                <h3 className="font-bold text-green-800 mb-2">🤖 AI Pricing Recommendations</h3>
                <div className="text-sm">
                  {pricingOptimization.ai_recommendations ? (
                    <pre className="whitespace-pre-wrap text-gray-700">{JSON.stringify(pricingOptimization.ai_recommendations, null, 2)}</pre>
                  ) : (
                    <p className="text-gray-600">Generating pricing strategies...</p>
                  )}
                </div>
              </div>

              {/* Implementation Priority Section */}
              <div className="bg-blue-50 p-4 rounded-lg">
                <h3 className="font-bold text-blue-800 mb-2">🎯 Implementation Priority</h3>
                <div className="text-sm">
                  {pricingOptimization.implementation_priority ? (
                    <pre className="whitespace-pre-wrap text-gray-700">{JSON.stringify(pricingOptimization.implementation_priority, null, 2)}</pre>
                  ) : (
                    <p className="text-gray-600">Prioritizing pricing actions...</p>
                  )}
                </div>
              </div>

              {/* Expected Impact Section */}
              <div className="bg-purple-50 p-4 rounded-lg">
                <h3 className="font-bold text-purple-800 mb-2">📈 Expected Impact</h3>
                <div className="text-sm">
                  <p><span className="font-semibold">Revenue Impact:</span> {pricingOptimization.expected_impact ? `${(pricingOptimization.expected_impact * 100).toFixed(1)}%` : 'Calculating...'}</p>
                </div>
              </div>
            </div>
          </CustomModal>
        )}

        {/* A/B Testing Modal - displays active and completed tests */}
        {showABTestModal && (
          <CustomModal
            title="🧪 A/B Testing Dashboard"
            onClose={() => setShowABTestModal(false)}
            showCloseButton={true}
          >
            <div className="space-y-4">
              <div className="bg-indigo-50 p-4 rounded-lg">
                <h3 className="font-bold text-indigo-800 mb-2">📊 Active Tests</h3>
                {abTestResults.length > 0 ? (
                  abTestResults.map((test, index) => (
                    <div key={index} className="mb-4 p-3 bg-white rounded border">
                      <div className="text-sm">
                        <div><span className="font-semibold">Test ID:</span> {test.test_id}</div>
                        <div><span className="font-semibold">Variants:</span> {test.variants?.length || 0}</div>
                        <div><span className="font-semibold">Expected Duration:</span> {test.expected_duration || 'N/A'}</div>
                        <div><span className="font-semibold">Status:</span> 
                          <span className="ml-1 px-2 py-1 bg-yellow-100 text-yellow-800 rounded text-xs">Running</span>
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-gray-600 text-sm">No active A/B tests. Create one to start optimizing!</p>
                )}
              </div>

              {/* Quick Test Setup */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-bold text-gray-800 mb-2">⚡ Quick Test Setup</h3>
                <div className="space-y-2">
                  <button
                    onClick={() => setupABTest("Mental toughness training for young athletes", "headline", ["instagram", "facebook"])}
                    className="w-full text-left p-2 bg-white rounded border hover:bg-blue-50 text-sm"
                  >
                    🏆 Test Headlines for Sports Content
                  </button>
                  <button
                    onClick={() => setupABTest("Overcome challenges and build confidence", "tone", ["instagram", "twitter"])}
                    className="w-full text-left p-2 bg-white rounded border hover:bg-blue-50 text-sm"
                  >
                    🎯 Test Content Tone Variations
                  </button>
                  <button
                    onClick={() => setupABTest("Get your copy today!", "call_to_action", ["facebook", "instagram"])}
                    className="w-full text-left p-2 bg-white rounded border hover:bg-blue-50 text-sm"
                  >
                    📢 Test Call-to-Action Phrases
                  </button>
                </div>
              </div>
            </div>
          </CustomModal>
        )}

        {/* Comprehensive Settings Modal - NEW */}
        <Settings
          isOpen={showConfigSettingsModal}
          onClose={() => setShowConfigSettingsModal(false)}
          firebaseServices={{ db, auth }}
          userId={userId}
          onSettingsUpdate={(newSettings) => {
            console.log('Settings updated:', newSettings);
            showCustomModal('✅ Settings saved successfully! Your configuration has been updated.');
          }}
        />

        {/* Onboarding Guide Modal - NEW */}
        <OnboardingGuide
          isOpen={showOnboardingGuide}
          onClose={() => setShowOnboardingGuide(false)}
          onComplete={completeOnboarding}
        />

      </div>
    </FirebaseContext.Provider>
  );
}

export default App; 

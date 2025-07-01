import React, { useState, useEffect } from 'react';

/**
 * Comprehensive Settings Page Component
 * Allows users to configure all API keys and settings that were previously in .env
 * Organized into logical sections with validation and helpful descriptions
 */
const Settings = ({ 
  isOpen, 
  onClose, 
  firebaseServices, 
  userId, 
  onSettingsUpdate 
}) => {
  // State for all configuration settings
  const [settings, setSettings] = useState({
    // OpenAI Configuration
    openai: {
      apiKey: '',
      model: 'gpt-4'
    },
    
    // Firebase Configuration  
    firebase: {
      projectId: 'ai-book-agent-dashboard',
      credentialsPath: ''
    },
    
    // Social Media API Keys
    twitter: {
      apiKey: '',
      apiSecret: '',
      accessToken: '',
      accessTokenSecret: ''
    },
    
    facebook: {
      accessToken: '',
      pageId: ''
    },
    
    instagram: {
      accessToken: '',
      businessAccountId: ''
    },
    
    pinterest: {
      accessToken: '',
      boardId: ''
    },
    
    // Google Services
    googleAnalytics: {
      propertyId: '',
      credentialsPath: ''
    },
    
    googleAds: {
      customerId: '',
      developerToken: '',
      credentialsPath: ''
    },
    
    // Budget Management
    budget: {
      monthlyBudget: 500.00,
      alertThreshold: 0.8,
      emergencyStopThreshold: 0.95,
      autoReallocation: true
    },
    
    // Autonomous Operation Settings
    autonomous: {
      enabled: false,
      dailyPostSchedule: '9:00,14:00,19:00',
      weeklyReportDay: 'monday',
      weeklyReportTime: '09:00',
      autoOptimization: true,
      minConfidenceThreshold: 0.7
    },
    
    // Book Information
    book: {
      title: '',
      amazonUrl: '',
      audibleUrl: '',
      landingPageUrl: '',
      primaryAudience: '',
      targetAgeRange: '',
      geographicTargets: 'US,CA,UK,AU'
    },
    
    // Performance Thresholds
    performance: {
      minEngagementRate: 0.02,
      minCTR: 0.01,
      targetROAS: 3.0,
      minConversionRate: 0.005
    }
  });

  const [activeTab, setActiveTab] = useState('openai');
  const [loading, setLoading] = useState(false);
  const [saveMessage, setSaveMessage] = useState('');

  // Load existing settings when component mounts
  useEffect(() => {
    if (isOpen && userId && firebaseServices?.db) {
      loadSettings();
    }
  }, [isOpen, userId, firebaseServices]);

  /**
   * Load settings from Firebase
   */
  const loadSettings = async () => {
    try {
      const { getDoc, doc } = await import('firebase/firestore');
      const settingsRef = doc(firebaseServices.db, 'settings', userId);
      const docSnap = await getDoc(settingsRef);
      
      if (docSnap.exists()) {
        const loadedSettings = docSnap.data();
        setSettings(prevSettings => ({
          ...prevSettings,
          ...loadedSettings
        }));
      }
    } catch (error) {
      console.error('Error loading settings:', error);
    }
  };

  /**
   * Test configuration by validating API connections
   */
  const testConfiguration = async () => {
    if (!userId) {
      setSaveMessage('❌ User not authenticated');
      return;
    }

    setLoading(true);
    setSaveMessage('🧪 Testing configuration...');

    try {
      const response = await fetch(`http://localhost:5000/api/config/${userId}/validate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          config: settings
        })
      });

      const result = await response.json();
      
      if (!response.ok) {
        throw new Error(result.error || 'Failed to validate configuration');
      }

      const validationResults = result.validation_results;
      
      // Format results for display
      let message = '📋 Configuration Test Results:\n\n';
      Object.entries(validationResults).forEach(([service, result]) => {
        const emoji = result.status === 'success' ? '✅' : 
                     result.status === 'error' ? '❌' : 
                     result.status === 'skipped' ? '⏭️' : '⚠️';
        message += `${emoji} ${service}: ${result.message}\n`;
      });

      setSaveMessage(message);
      
      // Clear message after 10 seconds (longer for test results)
      setTimeout(() => setSaveMessage(''), 10000);
      
    } catch (error) {
      console.error('Error testing configuration:', error);
      setSaveMessage('❌ Error testing configuration: ' + error.message);
      setTimeout(() => setSaveMessage(''), 5000);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Save settings to Firebase and update backend
   */
  const saveSettings = async () => {
    if (!userId || !firebaseServices?.db) {
      setSaveMessage('❌ User not authenticated');
      return;
    }

    setLoading(true);
    setSaveMessage('');

    try {
      // Save to Firebase (for immediate UI updates)
      const { setDoc, doc } = await import('firebase/firestore');
      const settingsRef = doc(firebaseServices.db, 'settings', userId);
      
      const settingsToSave = {
        ...settings,
        lastUpdated: new Date().toISOString()
      };

      await setDoc(settingsRef, settingsToSave);
      
      // Also save to backend config API for dynamic loading
      try {
        const response = await fetch(`http://localhost:5000/api/config/${userId}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            config: settings,
            app_id: window.__app_id || 'default-app-id'
          })
        });

        const result = await response.json();
        
        if (!response.ok) {
          throw new Error(result.error || 'Failed to save configuration to backend');
        }

        console.log('Configuration saved to backend:', result);
        
        // If we get here, both Firebase and backend saves succeeded
        setSaveMessage('✅ Settings saved successfully! All systems synchronized.');
        
      } catch (backendError) {
        console.error('Error saving to backend config API:', backendError);
        
        // Provide specific guidance based on the error
        let warningMessage = '⚠️ Settings saved to Firebase but backend sync failed.\n\n';
        
        if (backendError.message.includes('Firebase service not initialized')) {
          warningMessage += '📋 Solution: The backend needs Firebase configuration:\n';
          warningMessage += '1. Set GOOGLE_APPLICATION_CREDENTIALS environment variable\n';
          warningMessage += '2. Or configure Firebase in backend/.env file\n';
          warningMessage += '3. Restart the backend server\n\n';
          warningMessage += 'Your settings are saved and the app will work, but some backend features may be limited.';
        } else {
          warningMessage += '📋 Your settings are still saved and working!\n';
          warningMessage += 'This only affects backend configuration caching.\n\n';
          warningMessage += 'To fix: Restart the backend server or check backend logs.';
        }
        
        setSaveMessage(warningMessage);
      }
      
      // Call callback to notify parent component
      if (onSettingsUpdate) {
        onSettingsUpdate(settingsToSave);
      }
      
      // Clear message after 3 seconds
      setTimeout(() => setSaveMessage(''), 3000);
      
    } catch (error) {
      console.error('Error saving settings:', error);
      setSaveMessage('❌ Error saving settings: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Update a nested setting value
   */
  const updateSetting = (category, field, value) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [field]: value
      }
    }));
  };

  /**
   * Validate API key format (basic validation)
   */
  const validateAPIKey = (key, type) => {
    if (!key) return false;
    
    switch (type) {
      case 'openai':
        return key.startsWith('sk-');
      case 'twitter':
        return key.length > 20;
      case 'facebook':
      case 'instagram':
      case 'pinterest':
        return key.length > 10;
      default:
        return key.length > 5;
    }
  };

  // Tab configuration
  const tabs = [
    { id: 'openai', label: '🤖 OpenAI', description: 'Configure AI content generation' },
    { id: 'social', label: '📱 Social Media', description: 'API keys for social platforms' },
    { id: 'google', label: '📊 Google Services', description: 'Analytics and Ads configuration' },
    { id: 'budget', label: '💰 Budget', description: 'Marketing budget settings' },
    { id: 'autonomous', label: '⚡ Automation', description: 'Autonomous operation settings' },
    { id: 'book', label: '📚 Book Info', description: 'Your book details and targeting' },
    { id: 'performance', label: '📈 Performance', description: 'Success metrics and thresholds' }
  ];

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-2xl font-bold">⚙️ Settings & Configuration</h2>
              <p className="text-blue-100 mt-1">Configure your API keys and marketing settings</p>
            </div>
            <button
              onClick={onClose}
              className="text-white hover:text-gray-200 text-2xl"
            >
              ✕
            </button>
          </div>
        </div>

        <div className="flex h-[70vh]">
          {/* Sidebar Navigation */}
          <div className="w-1/4 bg-gray-50 border-r overflow-y-auto">
            <div className="p-4">
              {tabs.map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full text-left p-3 rounded-lg mb-2 transition-all ${
                    activeTab === tab.id
                      ? 'bg-blue-100 text-blue-700 border-l-4 border-blue-500'
                      : 'hover:bg-gray-100'
                  }`}
                >
                  <div className="font-medium">{tab.label}</div>
                  <div className="text-xs text-gray-500 mt-1">{tab.description}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Content Area */}
          <div className="flex-1 overflow-y-auto p-6">
            {/* OpenAI Settings */}
            {activeTab === 'openai' && (
              <div className="space-y-4">
                <h3 className="text-xl font-bold text-gray-800">🤖 OpenAI Configuration</h3>
                <p className="text-gray-600">Configure your OpenAI API for content generation</p>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    API Key *
                  </label>
                  <input
                    type="password"
                    value={settings.openai.apiKey}
                    onChange={(e) => updateSetting('openai', 'apiKey', e.target.value)}
                    placeholder="sk-your-openai-api-key-here"
                    className={`w-full p-3 border rounded-lg ${
                      validateAPIKey(settings.openai.apiKey, 'openai') 
                        ? 'border-green-300' 
                        : 'border-gray-300'
                    }`}
                  />
                  <p className="text-sm text-gray-500 mt-1">
                    Get your API key from <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener noreferrer" className="text-blue-500">OpenAI Platform</a>
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Model
                  </label>
                  <select
                    value={settings.openai.model}
                    onChange={(e) => updateSetting('openai', 'model', e.target.value)}
                    className="w-full p-3 border border-gray-300 rounded-lg"
                  >
                    <option value="gpt-4">GPT-4 (Recommended)</option>
                    <option value="gpt-4-turbo">GPT-4 Turbo</option>
                    <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                  </select>
                </div>
              </div>
            )}

            {/* Social Media Settings */}
            {activeTab === 'social' && (
              <div className="space-y-6">
                <h3 className="text-xl font-bold text-gray-800">📱 Social Media APIs</h3>
                
                {/* Twitter */}
                <div className="border rounded-lg p-4">
                  <h4 className="font-semibold text-gray-800 mb-3">🐦 Twitter / X</h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">API Key</label>
                      <input
                        type="password"
                        value={settings.twitter.apiKey}
                        onChange={(e) => updateSetting('twitter', 'apiKey', e.target.value)}
                        placeholder="your-twitter-api-key"
                        className="w-full p-2 border border-gray-300 rounded"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">API Secret</label>
                      <input
                        type="password"
                        value={settings.twitter.apiSecret}
                        onChange={(e) => updateSetting('twitter', 'apiSecret', e.target.value)}
                        placeholder="your-twitter-api-secret"
                        className="w-full p-2 border border-gray-300 rounded"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Access Token</label>
                      <input
                        type="password"
                        value={settings.twitter.accessToken}
                        onChange={(e) => updateSetting('twitter', 'accessToken', e.target.value)}
                        placeholder="your-twitter-access-token"
                        className="w-full p-2 border border-gray-300 rounded"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Access Token Secret</label>
                      <input
                        type="password"
                        value={settings.twitter.accessTokenSecret}
                        onChange={(e) => updateSetting('twitter', 'accessTokenSecret', e.target.value)}
                        placeholder="your-twitter-access-token-secret"
                        className="w-full p-2 border border-gray-300 rounded"
                      />
                    </div>
                  </div>
                </div>

                {/* Facebook */}
                <div className="border rounded-lg p-4">
                  <h4 className="font-semibold text-gray-800 mb-3">📘 Facebook</h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Access Token</label>
                      <input
                        type="password"
                        value={settings.facebook.accessToken}
                        onChange={(e) => updateSetting('facebook', 'accessToken', e.target.value)}
                        placeholder="your-facebook-access-token"
                        className="w-full p-2 border border-gray-300 rounded"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Page ID</label>
                      <input
                        type="text"
                        value={settings.facebook.pageId}
                        onChange={(e) => updateSetting('facebook', 'pageId', e.target.value)}
                        placeholder="your-facebook-page-id"
                        className="w-full p-2 border border-gray-300 rounded"
                      />
                    </div>
                  </div>
                </div>

                {/* Instagram */}
                <div className="border rounded-lg p-4">
                  <h4 className="font-semibold text-gray-800 mb-3">📷 Instagram</h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Access Token</label>
                      <input
                        type="password"
                        value={settings.instagram.accessToken}
                        onChange={(e) => updateSetting('instagram', 'accessToken', e.target.value)}
                        placeholder="your-instagram-access-token"
                        className="w-full p-2 border border-gray-300 rounded"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Business Account ID</label>
                      <input
                        type="text"
                        value={settings.instagram.businessAccountId}
                        onChange={(e) => updateSetting('instagram', 'businessAccountId', e.target.value)}
                        placeholder="your-instagram-business-account-id"
                        className="w-full p-2 border border-gray-300 rounded"
                      />
                    </div>
                  </div>
                </div>

                {/* Pinterest */}
                <div className="border rounded-lg p-4">
                  <h4 className="font-semibold text-gray-800 mb-3">📌 Pinterest</h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Access Token</label>
                      <input
                        type="password"
                        value={settings.pinterest.accessToken}
                        onChange={(e) => updateSetting('pinterest', 'accessToken', e.target.value)}
                        placeholder="your-pinterest-access-token"
                        className="w-full p-2 border border-gray-300 rounded"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Board ID</label>
                      <input
                        type="text"
                        value={settings.pinterest.boardId}
                        onChange={(e) => updateSetting('pinterest', 'boardId', e.target.value)}
                        placeholder="your-pinterest-board-id"
                        className="w-full p-2 border border-gray-300 rounded"
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Google Services Settings */}
            {activeTab === 'google' && (
              <div className="space-y-6">
                <h3 className="text-xl font-bold text-gray-800">📊 Google Services</h3>
                
                {/* Google Analytics */}
                <div className="border rounded-lg p-4">
                  <h4 className="font-semibold text-gray-800 mb-3">📈 Google Analytics</h4>
                  <div className="space-y-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Property ID</label>
                      <input
                        type="text"
                        value={settings.googleAnalytics.propertyId}
                        onChange={(e) => updateSetting('googleAnalytics', 'propertyId', e.target.value)}
                        placeholder="your-google-analytics-property-id"
                        className="w-full p-2 border border-gray-300 rounded"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Credentials File Path</label>
                      <input
                        type="text"
                        value={settings.googleAnalytics.credentialsPath}
                        onChange={(e) => updateSetting('googleAnalytics', 'credentialsPath', e.target.value)}
                        placeholder="path/to/google-analytics-credentials.json"
                        className="w-full p-2 border border-gray-300 rounded"
                      />
                    </div>
                  </div>
                </div>

                {/* Google Ads */}
                <div className="border rounded-lg p-4">
                  <h4 className="font-semibold text-gray-800 mb-3">🎯 Google Ads</h4>
                  <div className="space-y-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Customer ID</label>
                      <input
                        type="text"
                        value={settings.googleAds.customerId}
                        onChange={(e) => updateSetting('googleAds', 'customerId', e.target.value)}
                        placeholder="your-google-ads-customer-id"
                        className="w-full p-2 border border-gray-300 rounded"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Developer Token</label>
                      <input
                        type="password"
                        value={settings.googleAds.developerToken}
                        onChange={(e) => updateSetting('googleAds', 'developerToken', e.target.value)}
                        placeholder="your-google-ads-developer-token"
                        className="w-full p-2 border border-gray-300 rounded"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Credentials File Path</label>
                      <input
                        type="text"
                        value={settings.googleAds.credentialsPath}
                        onChange={(e) => updateSetting('googleAds', 'credentialsPath', e.target.value)}
                        placeholder="path/to/google-ads-credentials.json"
                        className="w-full p-2 border border-gray-300 rounded"
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Budget Settings */}
            {activeTab === 'budget' && (
              <div className="space-y-4">
                <h3 className="text-xl font-bold text-gray-800">💰 Budget Management</h3>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Monthly Marketing Budget ($)
                  </label>
                  <input
                    type="number"
                    value={settings.budget.monthlyBudget}
                    onChange={(e) => updateSetting('budget', 'monthlyBudget', parseFloat(e.target.value))}
                    className="w-full p-3 border border-gray-300 rounded-lg"
                    min="0"
                    step="10"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Alert Threshold ({(settings.budget.alertThreshold * 100).toFixed(0)}% of budget)
                  </label>
                  <input
                    type="range"
                    min="0.5"
                    max="1.0"
                    step="0.05"
                    value={settings.budget.alertThreshold}
                    onChange={(e) => updateSetting('budget', 'alertThreshold', parseFloat(e.target.value))}
                    className="w-full"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Emergency Stop Threshold ({(settings.budget.emergencyStopThreshold * 100).toFixed(0)}% of budget)
                  </label>
                  <input
                    type="range"
                    min="0.8"
                    max="1.0"
                    step="0.05"
                    value={settings.budget.emergencyStopThreshold}
                    onChange={(e) => updateSetting('budget', 'emergencyStopThreshold', parseFloat(e.target.value))}
                    className="w-full"
                  />
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="autoReallocation"
                    checked={settings.budget.autoReallocation}
                    onChange={(e) => updateSetting('budget', 'autoReallocation', e.target.checked)}
                    className="mr-2"
                  />
                  <label htmlFor="autoReallocation" className="text-sm font-medium text-gray-700">
                    Enable Automatic Budget Reallocation
                  </label>
                </div>
              </div>
            )}

            {/* Autonomous Settings */}
            {activeTab === 'autonomous' && (
              <div className="space-y-4">
                <h3 className="text-xl font-bold text-gray-800">⚡ Autonomous Operation</h3>
                
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="autonomousEnabled"
                    checked={settings.autonomous.enabled}
                    onChange={(e) => updateSetting('autonomous', 'enabled', e.target.checked)}
                    className="mr-2"
                  />
                  <label htmlFor="autonomousEnabled" className="text-sm font-medium text-gray-700">
                    Enable Autonomous Marketing
                  </label>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Daily Post Schedule (24h format, comma-separated)
                  </label>
                  <input
                    type="text"
                    value={settings.autonomous.dailyPostSchedule}
                    onChange={(e) => updateSetting('autonomous', 'dailyPostSchedule', e.target.value)}
                    placeholder="9:00,14:00,19:00"
                    className="w-full p-3 border border-gray-300 rounded-lg"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Weekly Report Day
                  </label>
                  <select
                    value={settings.autonomous.weeklyReportDay}
                    onChange={(e) => updateSetting('autonomous', 'weeklyReportDay', e.target.value)}
                    className="w-full p-3 border border-gray-300 rounded-lg"
                  >
                    <option value="monday">Monday</option>
                    <option value="tuesday">Tuesday</option>
                    <option value="wednesday">Wednesday</option>
                    <option value="thursday">Thursday</option>
                    <option value="friday">Friday</option>
                    <option value="saturday">Saturday</option>
                    <option value="sunday">Sunday</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Minimum Confidence Threshold ({(settings.autonomous.minConfidenceThreshold * 100).toFixed(0)}%)
                  </label>
                  <input
                    type="range"
                    min="0.5"
                    max="1.0"
                    step="0.05"
                    value={settings.autonomous.minConfidenceThreshold}
                    onChange={(e) => updateSetting('autonomous', 'minConfidenceThreshold', parseFloat(e.target.value))}
                    className="w-full"
                  />
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="autoOptimization"
                    checked={settings.autonomous.autoOptimization}
                    onChange={(e) => updateSetting('autonomous', 'autoOptimization', e.target.checked)}
                    className="mr-2"
                  />
                  <label htmlFor="autoOptimization" className="text-sm font-medium text-gray-700">
                    Enable Automatic Optimization
                  </label>
                </div>
              </div>
            )}

            {/* Book Information */}
            {activeTab === 'book' && (
              <div className="space-y-4">
                <h3 className="text-xl font-bold text-gray-800">📚 Book Information</h3>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Book Title</label>
                  <input
                    type="text"
                    value={settings.book.title}
                    onChange={(e) => updateSetting('book', 'title', e.target.value)}
                    placeholder="Your Book Title"
                    className="w-full p-3 border border-gray-300 rounded-lg"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Amazon URL</label>
                  <input
                    type="url"
                    value={settings.book.amazonUrl}
                    onChange={(e) => updateSetting('book', 'amazonUrl', e.target.value)}
                    placeholder="https://amazon.com/dp/your-book-id"
                    className="w-full p-3 border border-gray-300 rounded-lg"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Audible URL</label>
                  <input
                    type="url"
                    value={settings.book.audibleUrl}
                    onChange={(e) => updateSetting('book', 'audibleUrl', e.target.value)}
                    placeholder="https://audible.com/pd/your-book-id"
                    className="w-full p-3 border border-gray-300 rounded-lg"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Landing Page URL</label>
                  <input
                    type="url"
                    value={settings.book.landingPageUrl}
                    onChange={(e) => updateSetting('book', 'landingPageUrl', e.target.value)}
                    placeholder="https://your-landing-page.com"
                    className="w-full p-3 border border-gray-300 rounded-lg"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Primary Audience</label>
                  <input
                    type="text"
                    value={settings.book.primaryAudience}
                    onChange={(e) => updateSetting('book', 'primaryAudience', e.target.value)}
                    placeholder="youth athletes, parents, coaches"
                    className="w-full p-3 border border-gray-300 rounded-lg"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Target Age Range</label>
                  <input
                    type="text"
                    value={settings.book.targetAgeRange}
                    onChange={(e) => updateSetting('book', 'targetAgeRange', e.target.value)}
                    placeholder="13-25"
                    className="w-full p-3 border border-gray-300 rounded-lg"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Geographic Targets</label>
                  <input
                    type="text"
                    value={settings.book.geographicTargets}
                    onChange={(e) => updateSetting('book', 'geographicTargets', e.target.value)}
                    placeholder="US,CA,UK,AU"
                    className="w-full p-3 border border-gray-300 rounded-lg"
                  />
                </div>
              </div>
            )}

            {/* Performance Thresholds */}
            {activeTab === 'performance' && (
              <div className="space-y-4">
                <h3 className="text-xl font-bold text-gray-800">📈 Performance Thresholds</h3>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Minimum Engagement Rate ({(settings.performance.minEngagementRate * 100).toFixed(1)}%)
                  </label>
                  <input
                    type="range"
                    min="0.01"
                    max="0.1"
                    step="0.005"
                    value={settings.performance.minEngagementRate}
                    onChange={(e) => updateSetting('performance', 'minEngagementRate', parseFloat(e.target.value))}
                    className="w-full"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Minimum CTR ({(settings.performance.minCTR * 100).toFixed(1)}%)
                  </label>
                  <input
                    type="range"
                    min="0.005"
                    max="0.05"
                    step="0.005"
                    value={settings.performance.minCTR}
                    onChange={(e) => updateSetting('performance', 'minCTR', parseFloat(e.target.value))}
                    className="w-full"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Target ROAS ({settings.performance.targetROAS.toFixed(1)}x)
                  </label>
                  <input
                    type="range"
                    min="1.0"
                    max="10.0"
                    step="0.5"
                    value={settings.performance.targetROAS}
                    onChange={(e) => updateSetting('performance', 'targetROAS', parseFloat(e.target.value))}
                    className="w-full"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Minimum Conversion Rate ({(settings.performance.minConversionRate * 100).toFixed(2)}%)
                  </label>
                  <input
                    type="range"
                    min="0.001"
                    max="0.02"
                    step="0.001"
                    value={settings.performance.minConversionRate}
                    onChange={(e) => updateSetting('performance', 'minConversionRate', parseFloat(e.target.value))}
                    className="w-full"
                  />
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Footer with Test and Save Buttons */}
        <div className="bg-gray-50 px-6 py-4 flex justify-between items-center">
          <div className="text-sm text-gray-600 max-w-md">
            {saveMessage && (
              <div className={`whitespace-pre-line ${saveMessage.includes('✅') ? 'text-green-600' : saveMessage.includes('❌') ? 'text-red-600' : 'text-blue-600'}`}>
                {saveMessage}
              </div>
            )}
          </div>
          
          <div className="space-x-3">
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-600 hover:text-gray-800"
            >
              Cancel
            </button>
            <button
              onClick={testConfiguration}
              disabled={loading}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Testing...' : 'Test Configuration'}
            </button>
            <button
              onClick={saveSettings}
              disabled={loading}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Saving...' : 'Save Settings'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings; 
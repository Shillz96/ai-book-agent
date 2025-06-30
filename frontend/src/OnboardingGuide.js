import React, { useState } from 'react';

/**
 * Comprehensive Onboarding Guide Component
 * Provides step-by-step instructions for setting up the AI Book Marketing Agent
 * Includes detailed API key acquisition guides with direct links
 */
const OnboardingGuide = ({ isOpen, onClose, onComplete }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState(new Set());

  // Mark step as completed
  const markStepCompleted = (stepIndex) => {
    setCompletedSteps(prev => new Set([...prev, stepIndex]));
  };

  // Navigation functions
  const nextStep = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const goToStep = (stepIndex) => {
    setCurrentStep(stepIndex);
  };

  // Complete onboarding
  const completeOnboarding = () => {
    if (onComplete) {
      onComplete();
    }
    onClose();
  };

  // Detailed setup steps with instructions
  const steps = [
    {
      title: "Welcome to AI Book Marketing Agent",
      icon: "🚀",
      content: (
        <div className="space-y-4">
          <h3 className="text-xl font-bold text-gray-800">Welcome! 🎉</h3>
          <p className="text-gray-600">
            This AI agent will autonomously market your book across multiple platforms including:
          </p>
          <ul className="list-disc list-inside space-y-2 text-gray-700">
            <li>📱 Social Media (Twitter/X, Facebook, Instagram, Pinterest)</li>
            <li>🎯 Google Ads campaigns</li>
            <li>📊 Performance analytics and optimization</li>
            <li>💰 Budget management and ROI tracking</li>
            <li>⚡ Autonomous content generation and posting</li>
          </ul>
          <div className="bg-blue-50 p-4 rounded-lg">
            <p className="text-blue-800 font-medium">
              💡 This setup will take 15-30 minutes, but once completed, your AI agent will run autonomously 24/7!
            </p>
          </div>
        </div>
      )
    },
    {
      title: "OpenAI API Setup",
      icon: "🤖",
      content: (
        <div className="space-y-4">
          <h3 className="text-xl font-bold text-gray-800">🤖 OpenAI API Configuration</h3>
          <p className="text-gray-600">OpenAI powers your AI content generation. Here's how to get your API key:</p>
          
          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
            <h4 className="font-semibold text-yellow-800">Step-by-Step Instructions:</h4>
            <ol className="list-decimal list-inside space-y-2 mt-2 text-yellow-700">
              <li>Visit <a href="https://platform.openai.com" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">OpenAI Platform</a></li>
              <li>Create an account or log in</li>
              <li>Go to <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">API Keys section</a></li>
              <li>Click "Create new secret key"</li>
              <li>Name it "AI Book Agent" and copy the key immediately</li>
              <li>Add billing information (required for API access)</li>
            </ol>
          </div>

          <div className="bg-green-50 p-4 rounded-lg">
            <h4 className="font-semibold text-green-800">💰 Pricing Information:</h4>
            <p className="text-green-700">
              GPT-4: ~$0.03 per 1K tokens (approximately $1-3 per day for typical usage)
            </p>
          </div>

          <div className="bg-red-50 p-4 rounded-lg">
            <h4 className="font-semibold text-red-800">🔒 Security Note:</h4>
            <p className="text-red-700">
              Never share your API key. It starts with "sk-" and should be kept secret.
            </p>
          </div>
        </div>
      )
    },
    {
      title: "Firebase Setup",
      icon: "🔥",
      content: (
        <div className="space-y-4">
          <h3 className="text-xl font-bold text-gray-800">🔥 Firebase Database Setup</h3>
          <p className="text-gray-600">Firebase stores your settings and manages data. Follow these steps:</p>
          
          <div className="bg-blue-50 border-l-4 border-blue-400 p-4">
            <h4 className="font-semibold text-blue-800">Step-by-Step Instructions:</h4>
            <ol className="list-decimal list-inside space-y-2 mt-2 text-blue-700">
              <li>Go to <a href="https://console.firebase.google.com" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">Firebase Console</a></li>
              <li>Click "Create a project" or use existing project</li>
              <li>Enable Firestore Database (Cloud Firestore)</li>
              <li>Go to Project Settings → Service Accounts</li>
              <li>Click "Generate new private key"</li>
              <li>Download the JSON file and keep it secure</li>
            </ol>
          </div>

          <div className="bg-purple-50 p-4 rounded-lg">
            <h4 className="font-semibold text-purple-800">🎯 Our Project:</h4>
            <p className="text-purple-700">
              We've already set up Firebase for you! The project ID is: <code className="bg-gray-200 px-2 py-1 rounded">ai-book-agent-dashboard</code>
            </p>
          </div>
        </div>
      )
    },
    {
      title: "Twitter/X API Setup",
      icon: "🐦",
      content: (
        <div className="space-y-4">
          <h3 className="text-xl font-bold text-gray-800">🐦 Twitter/X API Configuration</h3>
          <p className="text-gray-600">Get your Twitter API credentials to post automatically:</p>
          
          <div className="bg-blue-50 border-l-4 border-blue-400 p-4">
            <h4 className="font-semibold text-blue-800">Step-by-Step Instructions:</h4>
            <ol className="list-decimal list-inside space-y-2 mt-2 text-blue-700">
              <li>Go to <a href="https://developer.twitter.com" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">Twitter Developer Portal</a></li>
              <li>Apply for a developer account (can take 1-3 days)</li>
              <li>Create a new app with name "AI Book Agent"</li>
              <li>Go to "Keys and Tokens" tab</li>
              <li>Generate Consumer Keys (API Key & Secret)</li>
              <li>Generate Access Token & Secret</li>
              <li>Enable "Read and Write" permissions</li>
            </ol>
          </div>

          <div className="bg-yellow-50 p-4 rounded-lg">
            <h4 className="font-semibold text-yellow-800">💰 Cost:</h4>
            <p className="text-yellow-700">
              Free tier: 300 posts/month. Pro ($100/month): Unlimited posting.
            </p>
          </div>

          <div className="bg-green-50 p-4 rounded-lg">
            <h4 className="font-semibold text-green-800">📝 Application Tips:</h4>
            <p className="text-green-700">
              Use case: "Automated book marketing and promotional content for published authors"
            </p>
          </div>
        </div>
      )
    },
    {
      title: "Facebook & Instagram Setup",
      icon: "📱",
      content: (
        <div className="space-y-4">
          <h3 className="text-xl font-bold text-gray-800">📱 Meta (Facebook & Instagram) Setup</h3>
          <p className="text-gray-600">Connect your Facebook page and Instagram business account:</p>
          
          <div className="bg-blue-50 border-l-4 border-blue-400 p-4">
            <h4 className="font-semibold text-blue-800">Facebook Page Setup:</h4>
            <ol className="list-decimal list-inside space-y-2 mt-2 text-blue-700">
              <li>Go to <a href="https://developers.facebook.com" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">Facebook Developers</a></li>
              <li>Create an app → "Business" type</li>
              <li>Add "Facebook Login" and "Instagram API" products</li>
              <li>Generate a Page Access Token for your book's Facebook page</li>
              <li>Get your Page ID from Facebook Page Settings</li>
            </ol>
          </div>

          <div className="bg-purple-50 border-l-4 border-purple-400 p-4">
            <h4 className="font-semibold text-purple-800">Instagram Business Setup:</h4>
            <ol className="list-decimal list-inside space-y-2 mt-2 text-purple-700">
              <li>Convert your Instagram to a Business Account</li>
              <li>Connect it to your Facebook Page</li>
              <li>Get Business Account ID from Meta Business Suite</li>
              <li>Use the same Access Token as Facebook</li>
            </ol>
          </div>

          <div className="bg-green-50 p-4 rounded-lg">
            <h4 className="font-semibold text-green-800">💰 Cost:</h4>
            <p className="text-green-700">
              Free for posting. Ads budget is separate and configurable in settings.
            </p>
          </div>
        </div>
      )
    },
    {
      title: "Pinterest API Setup",
      icon: "📌",
      content: (
        <div className="space-y-4">
          <h3 className="text-xl font-bold text-gray-800">📌 Pinterest Business Setup</h3>
          <p className="text-gray-600">Pinterest is excellent for book marketing, especially for visual content:</p>
          
          <div className="bg-red-50 border-l-4 border-red-400 p-4">
            <h4 className="font-semibold text-red-800">Step-by-Step Instructions:</h4>
            <ol className="list-decimal list-inside space-y-2 mt-2 text-red-700">
              <li>Convert to <a href="https://business.pinterest.com" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">Pinterest Business Account</a></li>
              <li>Go to <a href="https://developers.pinterest.com" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">Pinterest Developers</a></li>
              <li>Create an app for "Content Publishing"</li>
              <li>Generate Access Token with write permissions</li>
              <li>Create or identify a board for your book content</li>
              <li>Get Board ID from the board URL</li>
            </ol>
          </div>

          <div className="bg-green-50 p-4 rounded-lg">
            <h4 className="font-semibold text-green-800">📚 Why Pinterest for Books:</h4>
            <p className="text-green-700">
              Pinterest drives significant book sales through visual pins, quotes, and reading lists.
            </p>
          </div>
        </div>
      )
    },
    {
      title: "Google Analytics & Ads",
      icon: "📊",
      content: (
        <div className="space-y-4">
          <h3 className="text-xl font-bold text-gray-800">📊 Google Services Setup</h3>
          <p className="text-gray-600">Track performance and run targeted ads:</p>
          
          <div className="bg-blue-50 border-l-4 border-blue-400 p-4">
            <h4 className="font-semibold text-blue-800">Google Analytics 4:</h4>
            <ol className="list-decimal list-inside space-y-2 mt-2 text-blue-700">
              <li>Go to <a href="https://analytics.google.com" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">Google Analytics</a></li>
              <li>Create a new property for your book/website</li>
              <li>Copy the Property ID (format: 123456789)</li>
              <li>Set up Service Account for API access</li>
              <li>Download credentials JSON file</li>
            </ol>
          </div>

          <div className="bg-green-50 border-l-4 border-green-400 p-4">
            <h4 className="font-semibold text-green-800">Google Ads:</h4>
            <ol className="list-decimal list-inside space-y-2 mt-2 text-green-700">
              <li>Go to <a href="https://ads.google.com" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">Google Ads</a></li>
              <li>Create an account and get Customer ID</li>
              <li>Apply for <a href="https://developers.google.com/google-ads/api" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">Google Ads API</a> access</li>
              <li>Get Developer Token (can take 1-3 days)</li>
              <li>Set up OAuth2 credentials</li>
            </ol>
          </div>

          <div className="bg-yellow-50 p-4 rounded-lg">
            <h4 className="font-semibold text-yellow-800">🎯 Ad Budget:</h4>
            <p className="text-yellow-700">
              Start with $10-20/day. The AI will optimize spend based on performance.
            </p>
          </div>
        </div>
      )
    },
    {
      title: "Book Information Setup",
      icon: "📚",
      content: (
        <div className="space-y-4">
          <h3 className="text-xl font-bold text-gray-800">📚 Your Book Details</h3>
          <p className="text-gray-600">Configure your book information for targeted marketing:</p>
          
          <div className="bg-purple-50 border-l-4 border-purple-400 p-4">
            <h4 className="font-semibold text-purple-800">Required Information:</h4>
            <ul className="list-disc list-inside space-y-2 mt-2 text-purple-700">
              <li><strong>Book Title:</strong> The exact title of your book</li>
              <li><strong>Amazon URL:</strong> Direct link to your book on Amazon</li>
              <li><strong>Audible URL:</strong> Direct link to your audiobook (if available)</li>
              <li><strong>Landing Page:</strong> Your book's website or sales page</li>
              <li><strong>Target Audience:</strong> Who should read your book</li>
              <li><strong>Age Range:</strong> Primary age demographic</li>
              <li><strong>Geographic Targets:</strong> Countries to focus marketing</li>
            </ul>
          </div>

          <div className="bg-blue-50 p-4 rounded-lg">
            <h4 className="font-semibold text-blue-800">📖 Example for "Unstoppable":</h4>
            <ul className="list-disc list-inside space-y-1 mt-2 text-blue-700 text-sm">
              <li>Target Audience: Youth athletes, parents, coaches</li>
              <li>Age Range: 13-25 (primary), 35-50 (parents)</li>
              <li>Geographic: US, Canada, UK, Australia</li>
            </ul>
          </div>
        </div>
      )
    },
    {
      title: "Budget & Performance Settings",
      icon: "💰",
      content: (
        <div className="space-y-4">
          <h3 className="text-xl font-bold text-gray-800">💰 Budget & Performance Configuration</h3>
          <p className="text-gray-600">Set your marketing budget and performance thresholds:</p>
          
          <div className="bg-green-50 border-l-4 border-green-400 p-4">
            <h4 className="font-semibold text-green-800">Budget Settings:</h4>
            <ul className="list-disc list-inside space-y-2 mt-2 text-green-700">
              <li><strong>Monthly Budget:</strong> Total marketing spend (recommended: $500-2000)</li>
              <li><strong>Alert Threshold:</strong> Get notified at 80% of budget</li>
              <li><strong>Emergency Stop:</strong> Auto-pause at 95% of budget</li>
              <li><strong>Auto-Reallocation:</strong> Let AI move budget to best-performing platforms</li>
            </ul>
          </div>

          <div className="bg-blue-50 border-l-4 border-blue-400 p-4">
            <h4 className="font-semibold text-blue-800">Performance Targets:</h4>
            <ul className="list-disc list-inside space-y-2 mt-2 text-blue-700">
              <li><strong>Target ROAS:</strong> Return on Ad Spend (3x = $3 revenue per $1 spent)</li>
              <li><strong>Min Engagement Rate:</strong> Social media interaction threshold</li>
              <li><strong>Min CTR:</strong> Click-through rate for ads</li>
              <li><strong>Min Conversion Rate:</strong> Visitors who buy your book</li>
            </ul>
          </div>

          <div className="bg-yellow-50 p-4 rounded-lg">
            <h4 className="font-semibold text-yellow-800">💡 Recommended Starting Values:</h4>
            <p className="text-yellow-700">
              Budget: $500/month | ROAS: 3x | Engagement: 2% | CTR: 1% | Conversion: 0.5%
            </p>
          </div>
        </div>
      )
    },
    {
      title: "Autonomous Operation Setup",
      icon: "⚡",
      content: (
        <div className="space-y-4">
          <h3 className="text-xl font-bold text-gray-800">⚡ Autonomous AI Configuration</h3>
          <p className="text-gray-600">Configure how your AI agent operates automatically:</p>
          
          <div className="bg-purple-50 border-l-4 border-purple-400 p-4">
            <h4 className="font-semibold text-purple-800">Autonomous Features:</h4>
            <ul className="list-disc list-inside space-y-2 mt-2 text-purple-700">
              <li><strong>Daily Posting:</strong> AI generates and posts content automatically</li>
              <li><strong>Ad Optimization:</strong> Adjusts bids and targeting based on performance</li>
              <li><strong>Budget Management:</strong> Reallocates spend to best-performing platforms</li>
              <li><strong>Content A/B Testing:</strong> Tests different post types and styles</li>
              <li><strong>Weekly Reports:</strong> Automated performance summaries</li>
            </ul>
          </div>

          <div className="bg-green-50 border-l-4 border-green-400 p-4">
            <h4 className="font-semibold text-green-800">Safety Controls:</h4>
            <ul className="list-disc list-inside space-y-2 mt-2 text-green-700">
              <li><strong>Confidence Threshold:</strong> AI only acts when 70%+ confident</li>
              <li><strong>Human Approval:</strong> Option to review before posting</li>
              <li><strong>Budget Limits:</strong> Hard stops prevent overspending</li>
              <li><strong>Brand Guidelines:</strong> Maintains consistent messaging</li>
            </ul>
          </div>

          <div className="bg-blue-50 p-4 rounded-lg">
            <h4 className="font-semibold text-blue-800">🕒 Recommended Schedule:</h4>
            <p className="text-blue-700">
              Posts: 9:00 AM, 2:00 PM, 7:00 PM | Reports: Monday 9:00 AM
            </p>
          </div>
        </div>
      )
    },
    {
      title: "Ready to Launch!",
      icon: "🎯",
      content: (
        <div className="space-y-4">
          <h3 className="text-xl font-bold text-gray-800">🎯 You're Ready to Launch!</h3>
          <p className="text-gray-600">Your AI Book Marketing Agent is configured and ready to start promoting your book!</p>
          
          <div className="bg-green-50 border-l-4 border-green-400 p-4">
            <h4 className="font-semibold text-green-800">What Happens Next:</h4>
            <ol className="list-decimal list-inside space-y-2 mt-2 text-green-700">
              <li>Click "Complete Setup" to save all your settings</li>
              <li>Go to Settings to enter all your API keys</li>
              <li>Test each platform connection</li>
              <li>Enable autonomous operation when ready</li>
              <li>Monitor your dashboard for performance updates</li>
            </ol>
          </div>

          <div className="bg-blue-50 border-l-4 border-blue-400 p-4">
            <h4 className="font-semibold text-blue-800">🚀 First Week Recommendations:</h4>
            <ul className="list-disc list-inside space-y-2 mt-2 text-blue-700">
              <li>Start with manual post approval to review AI content</li>
              <li>Monitor daily for the first few days</li>
              <li>Adjust budget based on initial performance</li>
              <li>Enable full automation after you're comfortable</li>
            </ul>
          </div>

          <div className="bg-yellow-50 p-4 rounded-lg">
            <h4 className="font-semibold text-yellow-800">📞 Support:</h4>
            <p className="text-yellow-700">
              Need help? Check the documentation or contact support through the dashboard.
            </p>
          </div>

          <div className="bg-purple-50 p-4 rounded-lg">
            <h4 className="font-semibold text-purple-800">🎉 Congratulations!</h4>
            <p className="text-purple-700">
              You now have a 24/7 AI marketing team working to promote your book!
            </p>
          </div>
        </div>
      )
    }
  ];

  if (!isOpen) return null;

  const currentStepData = steps[currentStep];
  const progress = ((currentStep + 1) / steps.length) * 100;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white p-6">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-2xl font-bold">🚀 AI Book Marketing Agent Setup</h2>
              <p className="text-purple-100 mt-1">Step {currentStep + 1} of {steps.length}</p>
            </div>
            <button
              onClick={onClose}
              className="text-white hover:text-gray-200 text-2xl"
            >
              ✕
            </button>
          </div>
          
          {/* Progress Bar */}
          <div className="mt-4">
            <div className="bg-purple-200 rounded-full h-2">
              <div 
                className="bg-white rounded-full h-2 transition-all duration-300"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
          </div>
        </div>

        <div className="flex h-[70vh]">
          {/* Step Navigation Sidebar */}
          <div className="w-1/4 bg-gray-50 border-r overflow-y-auto">
            <div className="p-4">
              {steps.map((step, index) => (
                <button
                  key={index}
                  onClick={() => goToStep(index)}
                  className={`w-full text-left p-3 rounded-lg mb-2 transition-all ${
                    currentStep === index
                      ? 'bg-blue-100 text-blue-700 border-l-4 border-blue-500'
                      : completedSteps.has(index)
                      ? 'bg-green-50 text-green-700'
                      : 'hover:bg-gray-100'
                  }`}
                >
                  <div className="flex items-center">
                    <span className="text-lg mr-2">{step.icon}</span>
                    <div>
                      <div className="font-medium text-sm">{step.title}</div>
                      {completedSteps.has(index) && (
                        <div className="text-xs text-green-600">✓ Completed</div>
                      )}
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Content Area */}
          <div className="flex-1 overflow-y-auto p-6">
            <div className="flex items-center mb-4">
              <span className="text-3xl mr-3">{currentStepData.icon}</span>
              <h3 className="text-2xl font-bold text-gray-800">{currentStepData.title}</h3>
            </div>
            
            {currentStepData.content}

            {/* Step Completion Button */}
            <div className="mt-6">
              <button
                onClick={() => markStepCompleted(currentStep)}
                className={`px-4 py-2 rounded-lg ${
                  completedSteps.has(currentStep)
                    ? 'bg-green-100 text-green-700 border border-green-300'
                    : 'bg-blue-100 text-blue-700 border border-blue-300 hover:bg-blue-200'
                }`}
              >
                {completedSteps.has(currentStep) ? '✓ Step Completed' : 'Mark as Completed'}
              </button>
            </div>
          </div>
        </div>

        {/* Footer Navigation */}
        <div className="bg-gray-50 px-6 py-4 flex justify-between items-center">
          <button
            onClick={prevStep}
            disabled={currentStep === 0}
            className="px-4 py-2 text-gray-600 hover:text-gray-800 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            ← Previous
          </button>
          
          <div className="text-sm text-gray-600">
            Step {currentStep + 1} of {steps.length}
          </div>
          
          <div className="space-x-3">
            {currentStep < steps.length - 1 ? (
              <button
                onClick={nextStep}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Next →
              </button>
            ) : (
              <button
                onClick={completeOnboarding}
                className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                Complete Setup 🎉
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default OnboardingGuide; 
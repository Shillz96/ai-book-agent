import React, { useState, useEffect } from 'react';
import axios from 'axios';

const SetupWizard = ({ onComplete }) => {
  const [step, setStep] = useState(1);
  const [config, setConfig] = useState({
    openai_api_key: '',
    firebase_project_id: '',
    google_analytics_id: '',
    google_ads_id: '',
  });

  const [validation, setValidation] = useState({
    openai_api_key: { valid: true, message: '' },
    firebase_project_id: { valid: true, message: '' },
    google_analytics_id: { valid: true, message: '' },
    google_ads_id: { valid: true, message: '' },
  });

  const [status, setStatus] = useState({
    loading: false,
    error: null,
    success: false
  });

  // Validation functions
  const validateOpenAIKey = async (key) => {
    if (!key) return { valid: false, message: 'API key is required' };
    if (key.length < 20) return { valid: false, message: 'Invalid API key format' };
    try {
      setStatus({ ...status, loading: true });
      await axios.post('/api/validate/openai-key', { key });
      return { valid: true, message: 'API key is valid' };
    } catch (error) {
      return { valid: false, message: 'Invalid API key. Please check and try again.' };
    } finally {
      setStatus({ ...status, loading: false });
    }
  };

  const validateFirebaseId = (id) => {
    if (!id) return { valid: false, message: 'Project ID is required' };
    if (!/^[a-z0-9-]+$/.test(id)) {
      return { valid: false, message: 'Project ID can only contain lowercase letters, numbers, and hyphens' };
    }
    return { valid: true, message: 'Project ID format is valid' };
  };

  const handleInputChange = async (e) => {
    const { name, value } = e.target;
    setConfig({ ...config, [name]: value });
    
    // Real-time validation
    let validationResult;
    switch (name) {
      case 'openai_api_key':
        validationResult = await validateOpenAIKey(value);
        break;
      case 'firebase_project_id':
        validationResult = validateFirebaseId(value);
        break;
      default:
        validationResult = { valid: true, message: '' };
    }
    
    setValidation({
      ...validation,
      [name]: validationResult
    });
  };

  const isStepValid = () => {
    switch (step) {
      case 1:
        return validation.openai_api_key.valid && config.openai_api_key;
      case 2:
        return validation.firebase_project_id.valid && config.firebase_project_id;
      case 3:
        return true; // Optional analytics configuration
      default:
        return false;
    }
  };

  const handleNext = () => {
    if (isStepValid()) {
      setStep(step + 1);
    }
  };

  const handleBack = () => {
    setStep(step - 1);
  };

  const handleComplete = async () => {
    try {
      setStatus({ ...status, loading: true });
      await axios.post('/api/configuration', config);
      setStatus({ loading: false, error: null, success: true });
      onComplete(config);
    } catch (error) {
      setStatus({ 
        loading: false, 
        error: `Failed to save configuration: ${error.response?.data?.message || error.message}`,
        success: false 
      });
    }
  };

  const renderStep = () => {
    switch (step) {
      case 1:
        return (
          <div className="wizard-step">
            <h3>Step 1: API Configuration</h3>
            <p>Let's start by setting up your OpenAI API key for AI functionality.</p>
            <div className="form-group">
              <label>OpenAI API Key</label>
              <input
                type="password"
                name="openai_api_key"
                value={config.openai_api_key}
                onChange={handleInputChange}
                className={!validation.openai_api_key.valid ? 'invalid' : ''}
                placeholder="Enter your OpenAI API key"
              />
              {validation.openai_api_key.message && (
                <div className={`validation-message ${validation.openai_api_key.valid ? 'success' : 'error'}`}>
                  {validation.openai_api_key.message}
                </div>
              )}
            </div>
          </div>
        );
      
      case 2:
        return (
          <div className="wizard-step">
            <h3>Step 2: Firebase Configuration</h3>
            <p>Now, let's configure your Firebase project settings.</p>
            <div className="form-group">
              <label>Firebase Project ID</label>
              <input
                type="text"
                name="firebase_project_id"
                value={config.firebase_project_id}
                onChange={handleInputChange}
                className={!validation.firebase_project_id.valid ? 'invalid' : ''}
                placeholder="Enter your Firebase project ID"
              />
              {validation.firebase_project_id.message && (
                <div className={`validation-message ${validation.firebase_project_id.valid ? 'success' : 'error'}`}>
                  {validation.firebase_project_id.message}
                </div>
              )}
            </div>
          </div>
        );
      
      case 3:
        return (
          <div className="wizard-step">
            <h3>Step 3: Analytics Setup (Optional)</h3>
            <p>Configure analytics tracking (optional).</p>
            <div className="form-group">
              <label>Google Analytics ID</label>
              <input
                type="text"
                name="google_analytics_id"
                value={config.google_analytics_id}
                onChange={handleInputChange}
                placeholder="Enter Google Analytics ID (optional)"
              />
            </div>
            <div className="form-group">
              <label>Google Ads ID</label>
              <input
                type="text"
                name="google_ads_id"
                value={config.google_ads_id}
                onChange={handleInputChange}
                placeholder="Enter Google Ads ID (optional)"
              />
            </div>
          </div>
        );
      
      default:
        return null;
    }
  };

  return (
    <div className="setup-wizard">
      <div className="wizard-progress">
        <div className={`progress-step ${step >= 1 ? 'active' : ''}`}>1. API Setup</div>
        <div className={`progress-step ${step >= 2 ? 'active' : ''}`}>2. Firebase</div>
        <div className={`progress-step ${step >= 3 ? 'active' : ''}`}>3. Analytics</div>
      </div>

      {status.error && (
        <div className="error-message">
          {status.error}
        </div>
      )}

      {renderStep()}

      <div className="wizard-controls">
        {step > 1 && (
          <button onClick={handleBack} className="back-button">
            Back
          </button>
        )}
        
        {step < 3 ? (
          <button 
            onClick={handleNext}
            disabled={!isStepValid() || status.loading}
            className="next-button"
          >
            Next
          </button>
        ) : (
          <button 
            onClick={handleComplete}
            disabled={status.loading}
            className="complete-button"
          >
            Complete Setup
          </button>
        )}
      </div>

      {status.loading && (
        <div className="loading-overlay">
          <div className="spinner"></div>
          <p>Processing...</p>
        </div>
      )}
    </div>
  );
};

export default SetupWizard; 
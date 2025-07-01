import React, { useState, useEffect } from 'react';
import axios from 'axios';
import SetupWizard from './SetupWizard';
import './SetupWizard.css';

const ConfigurationManager = () => {
  const [config, setConfig] = useState({
    openai_api_key: '',
    firebase_project_id: '',
    google_analytics_id: '',
    google_ads_id: '',
    social_media_tokens: {},
  });

  const [status, setStatus] = useState({
    loading: true,
    error: null,
    success: false,
    isFirstTimeSetup: true
  });

  useEffect(() => {
    checkConfiguration();
  }, []);

  const checkConfiguration = async () => {
    try {
      setStatus({ ...status, loading: true });
      const response = await axios.get('/api/configuration/status');
      const isConfigured = response.data.isConfigured;
      
      if (isConfigured) {
        const configResponse = await axios.get('/api/configuration');
        setConfig(configResponse.data);
        setStatus({ 
          loading: false, 
          error: null, 
          success: true, 
          isFirstTimeSetup: false 
        });
      } else {
        setStatus({ 
          loading: false, 
          error: null, 
          success: false, 
          isFirstTimeSetup: true 
        });
      }
    } catch (error) {
      setStatus({ 
        loading: false, 
        error: `Error checking configuration: ${error.response?.data?.message || error.message}`,
        success: false,
        isFirstTimeSetup: true
      });
    }
  };

  const handleWizardComplete = async (wizardConfig) => {
    setConfig(wizardConfig);
    setStatus({ 
      loading: false, 
      error: null, 
      success: true, 
      isFirstTimeSetup: false 
    });
  };

  const handleInputChange = async (e) => {
    const { name, value } = e.target;
    
    // Real-time validation
    try {
      if (name === 'openai_api_key' && value) {
        setStatus({ ...status, loading: true });
        await axios.post('/api/validate/openai-key', { key: value });
      }
      
      setConfig({ ...config, [name]: value });
      setStatus({ 
        ...status, 
        loading: false, 
        error: null 
      });
    } catch (error) {
      setStatus({ 
        ...status, 
        loading: false, 
        error: `Invalid ${name.replace('_', ' ')}: ${error.response?.data?.message || error.message}`
      });
    }
  };

  const saveConfiguration = async () => {
    try {
      setStatus({ ...status, loading: true });
      await axios.post('/api/configuration', config);
      setStatus({ 
        ...status, 
        loading: false, 
        error: null, 
        success: true 
      });
    } catch (error) {
      setStatus({ 
        ...status, 
        loading: false, 
        error: `Failed to save configuration: ${error.response?.data?.message || error.message}`,
        success: false 
      });
    }
  };

  if (status.loading) {
    return (
      <div className="loading-overlay">
        <div className="spinner"></div>
        <p>Loading configuration...</p>
      </div>
    );
  }

  if (status.isFirstTimeSetup) {
    return <SetupWizard onComplete={handleWizardComplete} />;
  }

  return (
    <div className="configuration-manager">
      <h2>System Configuration</h2>
      
      {status.error && (
        <div className="error-message">
          {status.error}
        </div>
      )}
      
      {status.success && (
        <div className="success-message">
          Configuration saved successfully!
        </div>
      )}

      <form onSubmit={(e) => { e.preventDefault(); saveConfiguration(); }}>
        <div className="form-group">
          <label>OpenAI API Key</label>
          <div className="input-group">
            <input
              type="password"
              name="openai_api_key"
              value={config.openai_api_key}
              onChange={handleInputChange}
              placeholder="Enter OpenAI API Key"
            />
            <div className="input-help">
              Your OpenAI API key is required for AI functionality
            </div>
          </div>
        </div>

        <div className="form-group">
          <label>Firebase Project ID</label>
          <div className="input-group">
            <input
              type="text"
              name="firebase_project_id"
              value={config.firebase_project_id}
              onChange={handleInputChange}
              placeholder="Enter Firebase Project ID"
            />
            <div className="input-help">
              Found in your Firebase Console under Project Settings
            </div>
          </div>
        </div>

        <div className="form-group">
          <label>Google Analytics ID (Optional)</label>
          <div className="input-group">
            <input
              type="text"
              name="google_analytics_id"
              value={config.google_analytics_id}
              onChange={handleInputChange}
              placeholder="Enter Google Analytics ID"
            />
            <div className="input-help">
              Your Google Analytics measurement ID (format: G-XXXXXXXXXX)
            </div>
          </div>
        </div>

        <div className="form-group">
          <label>Google Ads ID (Optional)</label>
          <div className="input-group">
            <input
              type="text"
              name="google_ads_id"
              value={config.google_ads_id}
              onChange={handleInputChange}
              placeholder="Enter Google Ads ID"
            />
            <div className="input-help">
              Your Google Ads conversion tracking ID
            </div>
          </div>
        </div>

        <button type="submit" className="save-button" disabled={status.loading}>
          {status.loading ? 'Saving...' : 'Save Configuration'}
        </button>
      </form>
    </div>
  );
};

export default ConfigurationManager; 
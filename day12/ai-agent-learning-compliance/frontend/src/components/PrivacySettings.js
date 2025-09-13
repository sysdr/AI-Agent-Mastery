import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const PrivacySettings = () => {
  const [userId, setUserId] = useState('test_user_001');
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchSettings = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/privacy-settings/${userId}`);
      setSettings(response.data);
    } catch (error) {
      console.error('Failed to fetch privacy settings:', error);
    }
    setLoading(false);
  };

  const updateSettings = async () => {
    try {
      await axios.put(`${API_BASE_URL}/privacy-settings/${userId}`, settings);
      alert('Settings updated successfully!');
    } catch (error) {
      console.error('Failed to update settings:', error);
    }
  };

  useEffect(() => {
    if (userId) {
      fetchSettings();
    }
  }, [userId]);

  if (loading) return <div>Loading privacy settings...</div>;

  return (
    <div className="privacy-settings">
      <h2>Privacy Settings</h2>
      
      <div className="user-input">
        <input
          type="text"
          placeholder="User ID"
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
        />
      </div>

      {settings && (
        <div className="settings-form">
          <div className="setting-item">
            <label>
              <input
                type="checkbox"
                checked={settings.allow_personalization}
                onChange={(e) => setSettings({...settings, allow_personalization: e.target.checked})}
              />
              Allow Personalization
            </label>
          </div>

          <div className="setting-item">
            <label>
              <input
                type="checkbox"
                checked={settings.allow_bias_monitoring}
                onChange={(e) => setSettings({...settings, allow_bias_monitoring: e.target.checked})}
              />
              Allow Bias Monitoring
            </label>
          </div>

          <div className="setting-item">
            <label>
              <input
                type="checkbox"
                checked={settings.allow_ab_testing}
                onChange={(e) => setSettings({...settings, allow_ab_testing: e.target.checked})}
              />
              Allow A/B Testing
            </label>
          </div>

          <div className="setting-item">
            <label>
              Data Retention (days):
              <input
                type="number"
                value={settings.data_retention_days}
                onChange={(e) => setSettings({...settings, data_retention_days: parseInt(e.target.value)})}
              />
            </label>
          </div>

          <div className="setting-item">
            <label>
              Privacy Level:
              <select
                value={settings.privacy_level}
                onChange={(e) => setSettings({...settings, privacy_level: e.target.value})}
              >
                <option value="strict">Strict</option>
                <option value="standard">Standard</option>
                <option value="relaxed">Relaxed</option>
              </select>
            </label>
          </div>

          <button onClick={updateSettings} className="update-button">
            Update Settings
          </button>
        </div>
      )}
    </div>
  );
};

export default PrivacySettings;
